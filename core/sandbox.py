from __future__ import annotations

import base64
import binascii
import logging
import math
import os
import secrets
import shlex
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO, Callable

from core.runtime_paths import LOGS_DIR, TOOLS_DIR

DEFAULT_TOOLS_DIR = TOOLS_DIR
DEFAULT_LOGS_DIR = LOGS_DIR
CAPTURE_PATH = DEFAULT_LOGS_DIR / "captured_payload.luau"


class SandboxError(RuntimeError):
    pass


@dataclass(frozen=True)
class CapturedPayload:
    index: int
    kind: str
    size_bytes: int


@dataclass(frozen=True)
class SandboxResult:
    returncode: int
    timed_out: bool
    output_limited: bool
    output_bytes: int
    duration_seconds: float
    captures: tuple[CapturedPayload, ...]
    captured_path: Path | None
    captured_paths: tuple[Path, ...]
    run_log_path: Path
    trace_token: str | None
    isolation_backend: str
    stalled: bool = False


class _PipeDrainer(threading.Thread):
    MAX_CALLBACK_LINE_BYTES = 16 * 1024

    def __init__(
        self,
        stream: BinaryIO,
        destination: Path,
        byte_limit: int,
        line_callback: Callable[[bytes], None] | None = None,
    ):
        super().__init__(name="protez-luau-output", daemon=True)
        self._stream = stream
        self._destination = destination
        self._byte_limit = byte_limit
        self._line_callback = line_callback
        self._line_buffer = bytearray()
        self._discarding_line = False
        self.limit_hit = threading.Event()
        self.total_bytes = 0
        self.saved_bytes = 0
        self.error: OSError | None = None
        self.callback_error: Exception | None = None
        # A run that stops producing output is not doing visible work: the
        # heartbeat the harness prints is how a spinner is told from a worker.
        self.last_output_at = time.monotonic()

    def run(self) -> None:
        try:
            reader = getattr(self._stream, "read1", self._stream.read)
            with self._destination.open("wb") as output:
                while True:
                    chunk = reader(64 * 1024)
                    if not chunk:
                        break
                    self.last_output_at = time.monotonic()
                    self.total_bytes += len(chunk)
                    remaining = self._byte_limit - self.saved_bytes
                    if remaining > 0:
                        saved = chunk[:remaining]
                        output.write(saved)
                        self.saved_bytes += len(saved)
                        self._consume_lines(saved)
                    if self.total_bytes > self._byte_limit:
                        self.limit_hit.set()
            if self._line_buffer and not self._discarding_line:
                self._call_line_callback(bytes(self._line_buffer))
        except (OSError, ValueError) as exc:
            self.error = OSError(str(exc))

    def _consume_lines(self, chunk: bytes) -> None:
        if self._line_callback is None:
            return
        if self._discarding_line:
            newline = chunk.find(b"\n")
            if newline < 0:
                return
            chunk = chunk[newline + 1 :]
            self._discarding_line = False
        if chunk:
            self._line_buffer.extend(chunk)

        while True:
            newline = self._line_buffer.find(b"\n")
            if newline < 0:
                if len(self._line_buffer) > self.MAX_CALLBACK_LINE_BYTES:
                    self._line_buffer.clear()
                    self._discarding_line = True
                return
            line = bytes(self._line_buffer[: newline + 1])
            del self._line_buffer[: newline + 1]
            if len(line) <= self.MAX_CALLBACK_LINE_BYTES:
                self._call_line_callback(line)

    def _call_line_callback(self, line: bytes) -> None:
        if self._line_callback is None:
            return
        try:
            self._line_callback(line)
        except Exception as exc:
            self.callback_error = exc
            self._line_callback = None


class _CaptureParser:
    MAX_MARKER_LINE_BYTES = 16 * 1024
    MAX_CAPTURE_COUNT = 100

    def __init__(
        self,
        *,
        token: str,
        capture_path: Path,
        logger: logging.Logger,
        max_payload_bytes: int,
    ):
        self._prefix = f"__PROTEZ_CAPTURE_{token}|".encode("ascii")
        self._capture_path = capture_path
        self._logger = logger
        self._max_payload_bytes = max_payload_bytes
        self._captures: list[CapturedPayload] = []
        self._current_index: int | None = None
        self._current_kind = ""
        self._current_size = 0
        self._current_path: Path | None = None
        self._current_file: BinaryIO | None = None
        self._work_dir: Path | None = None
        self._latest_path: Path | None = None
        self._paths: list[Path] = []

    def parse(
        self, log_path: Path
    ) -> tuple[tuple[CapturedPayload, ...], Path | None, tuple[Path, ...]]:
        with tempfile.TemporaryDirectory(
            prefix="protez-captures-", dir=self._capture_path.parent
        ) as temp_dir:
            self._work_dir = Path(temp_dir)
            try:
                with log_path.open("rb") as log_file:
                    while True:
                        line = log_file.readline(self.MAX_MARKER_LINE_BYTES)
                        if not line:
                            break
                        if len(line) >= self.MAX_MARKER_LINE_BYTES and not line.endswith(b"\n"):
                            continue
                        self._consume(line.rstrip(b"\r\n"))
                if self._current_index is not None:
                    self._rollback_current()
            finally:
                if self._current_file is not None:
                    self._rollback_current()

        if self._captures and self._latest_path is not None:
            latest_temp = self._capture_path.with_name(self._capture_path.name + ".tmp")
            shutil.copyfile(self._latest_path, latest_temp)
            os.replace(latest_temp, self._capture_path)
            return tuple(self._captures), self._capture_path, tuple(self._paths)
        self._capture_path.unlink(missing_ok=True)
        return (), None, ()

    def _consume(self, line: bytes) -> None:
        if line.startswith(self._prefix):
            fields = line[len(self._prefix) :].split(b"|", maxsplit=2)
            if not fields:
                return
            marker = fields[0]
            try:
                if marker == b"B" and len(fields) == 3:
                    self._begin(int(fields[1]), fields[2].decode("ascii"))
                elif marker == b"C" and len(fields) == 3:
                    self._chunk(int(fields[1]), fields[2])
                elif marker == b"E" and len(fields) == 3:
                    self._end(int(fields[1]), int(fields[2]))
            except (ValueError, UnicodeDecodeError, binascii.Error) as exc:
                self._logger.warning("Ignoring malformed sandbox capture record: %s", exc)
                if self._current_index is not None:
                    self._rollback_current()
            return

        if line.startswith(b"[PROTEZ:"):
            closing = line.find(b"]")
            if closing < 0:
                return
            level_name = line[len(b"[PROTEZ:") : closing].decode("ascii", errors="replace")
            message = line[closing + 1 :].lstrip().decode("utf-8", errors="replace")
            levels = {
                "DEBUG": logging.DEBUG,
                "INFO": logging.INFO,
                "WARN": logging.WARNING,
                "ERROR": logging.ERROR,
            }
            level = levels.get(level_name.upper())
            if level is not None:
                self._logger.log(level, "Sandbox: %s", message[:2000])

    def _begin(self, index: int, kind: str) -> None:
        if self._current_index is not None:
            self._rollback_current()
        if (
            index < 1
            or index > self.MAX_CAPTURE_COUNT
            or not kind.isascii()
            or not kind.replace("_", "").isalnum()
            or self._work_dir is None
        ):
            return
        self._current_path = self._work_dir / f"payload_{index:03d}.part"
        self._current_file = self._current_path.open("wb")
        self._current_index = index
        self._current_kind = kind
        self._current_size = 0

    def _chunk(self, index: int, encoded: bytes) -> None:
        if index != self._current_index or self._current_file is None:
            return
        decoded = base64.b64decode(encoded, validate=True)
        self._current_size += len(decoded)
        if self._current_size > self._max_payload_bytes:
            self._logger.warning("Captured payload exceeded the configured size limit")
            self._rollback_current()
            return
        self._current_file.write(decoded)

    def _end(self, index: int, expected_size: int) -> None:
        if index != self._current_index or self._current_file is None or self._current_path is None:
            return
        if expected_size != self._current_size:
            self._logger.warning(
                "Discarding incomplete payload %s (%s of %s bytes)",
                index,
                self._current_size,
                expected_size,
            )
            self._rollback_current()
            return

        self._current_file.flush()
        self._current_file.close()
        destination = self._capture_path.with_name(
            f"{self._capture_path.stem}_{index:03d}.luau"
        )
        os.replace(self._current_path, destination)
        self._latest_path = destination
        self._paths.append(destination)
        self._captures.append(
            CapturedPayload(
                index=index,
                kind=self._current_kind,
                size_bytes=self._current_size,
            )
        )
        self._current_file = None
        self._current_path = None
        self._current_index = None
        self._current_kind = ""
        self._current_size = 0

    def _rollback_current(self) -> None:
        if self._current_file is not None:
            self._current_file.close()
        if self._current_path is not None:
            self._current_path.unlink(missing_ok=True)
        self._current_file = None
        self._current_path = None
        self._current_index = None
        self._current_kind = ""
        self._current_size = 0


class Sandbox:
    """Execute Luau in a networkless OS sandbox with bounded VM and process use."""

    # Cached answer to "can a plain user build namespaces on this host?".
    _UNSHARE_PROBE: bool | None = None

    def __init__(
        self,
        *,
        tools_dir: Path | str = DEFAULT_TOOLS_DIR,
        logs_dir: Path | str = DEFAULT_LOGS_DIR,
        timeout_seconds: float = 5.0,
        max_input_bytes: int = 16 * 1024 * 1024,
        max_output_bytes: int = 32 * 1024 * 1024,
        max_trace_events: int = 25_000,
        logger: logging.Logger | None = None,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_input_bytes <= 0 or max_output_bytes <= 0 or max_trace_events <= 0:
            raise ValueError("input, output and trace-event limits must be positive")
        self.tools_dir = Path(tools_dir).expanduser().resolve()
        self.logs_dir = Path(logs_dir).expanduser().resolve()
        self.capture_path = self.logs_dir / CAPTURE_PATH.name
        self.timeout_seconds = float(timeout_seconds)
        self.max_input_bytes = int(max_input_bytes)
        self.max_output_bytes = int(max_output_bytes)
        self.max_trace_events = int(max_trace_events)
        self.logger = logger or logging.getLogger("protez")
        self._run_lock = threading.Lock()

    def run(
        self,
        source: str,
        *,
        source_name: str = "input",
        trace: bool = False,
        trace_token: str | None = None,
        output_line_callback: Callable[[bytes], None] | None = None,
        prelude: str | None = None,
        stall_timeout_seconds: float | None = None,
    ) -> SandboxResult:
        if not isinstance(source, str):
            raise TypeError("source must be text")
        if stall_timeout_seconds is not None and stall_timeout_seconds <= 0:
            raise ValueError("stall_timeout_seconds must be positive")
        worker_source = f"{prelude}\n{source}" if prelude else source
        source_bytes = worker_source.encode("utf-8")
        if len(source_bytes) > self.max_input_bytes:
            raise SandboxError(
                f"Input is {len(source_bytes):,} bytes; limit is {self.max_input_bytes:,} bytes"
            )
        if not source.strip():
            raise SandboxError("Input is empty")
        if not trace and (trace_token is not None or output_line_callback is not None):
            raise ValueError("trace_token and output_line_callback require trace=True")

        with self._run_lock:
            return self._run_once(
                worker_source,
                source_name,
                len(source_bytes),
                trace=trace,
                prelude=prelude,
                trace_token=trace_token,
                output_line_callback=output_line_callback,
                stall_timeout_seconds=stall_timeout_seconds,
            )

    def _run_once(
        self,
        source: str,
        source_name: str,
        source_size: int,
        *,
        prelude: str | None = None,
        trace: bool,
        trace_token: str | None,
        output_line_callback: Callable[[bytes], None] | None,
        stall_timeout_seconds: float | None = None,
    ) -> SandboxResult:
        native_host = self._resolve_native_host()
        if native_host is None:
            raise SandboxError(
                "The isolated Luau worker is unavailable. Repair the bundled native host; "
                "the ordinary Luau CLI is not used to execute untrusted source."
            )
        if trace:
            if trace_token is None:
                trace_token = secrets.token_hex(16)
            elif len(trace_token) != 32 or any(
                character not in "0123456789abcdef" for character in trace_token
            ):
                raise SandboxError("Trace token must be 32 lowercase hexadecimal characters")

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.capture_path.parent.mkdir(parents=True, exist_ok=True)
        token = secrets.token_hex(16)
        capture_path = self.logs_dir / f"captured_payload_{token}.luau"
        run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_log_path = self.logs_dir / f"sandbox_{run_stamp}_{token[:8]}.log"
        timeout = self.timeout_seconds
        started = time.monotonic()

        self.logger.info("Deobfuscation input: %s (%s bytes)", source_name, f"{source_size:,}")
        if prelude:
            self.logger.info(
                "Executor environment prelude attached (%s bytes): %s",
                f"{len(prelude.encode('utf-8')):,}",
                (prelude.splitlines()[0] if prelude.splitlines() else "").strip()[:120],
            )
        self.logger.info("Starting Luau in a networkless operating-system sandbox")

        with tempfile.TemporaryDirectory(prefix="protez-sandbox-", dir=self.logs_dir) as temp_dir:
            runner_path = Path(temp_dir) / "input.luau"
            if os.name != "nt":
                try:
                    runner_path.write_text(source, encoding="utf-8", newline="")
                except OSError as exc:
                    raise SandboxError(f"Could not stage Luau source: {exc}") from exc

            creationflags = 0
            popen_options: dict[str, object] = {}
            if os.name == "nt":
                creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
            else:
                popen_options["start_new_session"] = True

            worker_args = [
                "--capture-token",
                token,
                "--max-captures",
                "100",
                "--max-capture-bytes",
                str(min(8 * 1024 * 1024, max(1, self.max_output_bytes // 3))),
            ]
            if trace and trace_token is not None:
                worker_args.extend(
                    ["--trace-token", trace_token, "--max-trace-events", str(self.max_trace_events)]
                )
            if os.name == "nt":
                command = [str(native_host), "--appcontainer", *worker_args]
                stdin_mode = subprocess.PIPE
                sandbox_backend = "Windows AppContainer"
            elif os.name == "posix":
                command = self._linux_isolated_command(native_host, runner_path, worker_args, timeout)
                stdin_mode = subprocess.DEVNULL
                names = {Path(part).name for part in command}
                sandbox_backend = (
                    "unshare namespaces" if "unshare" in names else "bubblewrap namespaces"
                )
            else:
                raise SandboxError(f"No isolated Luau worker is available on {os.name}")

            try:
                process = subprocess.Popen(
                    command,
                    cwd=temp_dir,
                    env=self._minimal_environment(),
                    stdin=stdin_mode,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                    creationflags=creationflags,
                    **popen_options,
                )
            except OSError as exc:
                raise SandboxError(f"Could not start isolated Luau worker {native_host}: {exc}") from exc

            if process.stdout is None:
                self._kill_process(process)
                raise SandboxError("Luau process did not expose an output stream")

            self.logger.info("Isolated worker started (%s)", sandbox_backend)
            self.logger.info("Real loadstring/load compilation and execution capture enabled")
            if trace:
                self.logger.info(
                    "Native Luau instruction tracing enabled (limit: %s events)",
                    f"{self.max_trace_events:,}",
                )
            drainer = _PipeDrainer(
                process.stdout,
                run_log_path,
                self.max_output_bytes,
                line_callback=output_line_callback,
            )
            drainer.start()
            input_writer: threading.Thread | None = None
            if process.stdin is not None:
                def write_worker_source() -> None:
                    try:
                        process.stdin.write(source.encode("utf-8"))
                        process.stdin.flush()
                    except (BrokenPipeError, OSError) as exc:
                        self.logger.debug("Worker stopped reading source input: %s", exc)
                    finally:
                        try:
                            process.stdin.close()
                        except OSError:
                            pass

                input_writer = threading.Thread(
                    target=write_worker_source,
                    name="protez-worker-input",
                    daemon=True,
                )
                input_writer.start()
            timed_out = False
            output_limited = False
            stalled = False
            deadline = started + timeout

            while process.poll() is None:
                if drainer.limit_hit.is_set():
                    output_limited = True
                    self._kill_process(process)
                    break
                if time.monotonic() >= deadline:
                    timed_out = True
                    self._kill_process(process)
                    break
                if (
                    stall_timeout_seconds is not None
                    and time.monotonic() - drainer.last_output_at >= stall_timeout_seconds
                ):
                    stalled = True
                    self._kill_process(process)
                    break
                time.sleep(0.025)

            try:
                returncode = process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self._kill_process(process)
                returncode = process.wait()

            if input_writer is not None:
                input_writer.join(timeout=2.0)
                if input_writer.is_alive():
                    self._kill_process(process)
                    input_writer.join(timeout=1.0)

            drainer.join(timeout=2.0)
            if drainer.is_alive():
                self._kill_process(process)
                try:
                    process.stdout.close()
                except OSError:
                    pass
                drainer.join(timeout=1.0)
            if drainer.error:
                raise SandboxError(f"Could not save Luau process output: {drainer.error}")
            if drainer.callback_error:
                self.logger.error("Trace line callback stopped: %s", drainer.callback_error)
            if drainer.limit_hit.is_set():
                output_limited = True

        try:
            parser = _CaptureParser(
                token=token,
                capture_path=capture_path,
                logger=self.logger,
                max_payload_bytes=self.max_output_bytes,
            )
            captures, captured_path, captured_paths = parser.parse(run_log_path)
        except OSError as exc:
            raise SandboxError(f"Could not parse captured payload output: {exc}") from exc

        duration = time.monotonic() - started
        if timed_out:
            self.logger.warning("Sandbox timed out after %.1f seconds; process terminated", timeout)
        if output_limited:
            self.logger.warning(
                "Sandbox output exceeded %s bytes; process terminated",
                f"{self.max_output_bytes:,}",
            )
        if stalled:
            self.logger.warning(
                "Sandbox produced no output for %.0f seconds; process terminated "
                "(the payload is spinning where it cannot be seen)",
                stall_timeout_seconds,
            )
        if returncode != 0 and not timed_out and not output_limited and not stalled:
            self.logger.error(
                "Luau process exited with code %s (see %s)",
                returncode,
                run_log_path.name,
            )
        if captures:
            total_bytes = sum(item.size_bytes for item in captures)
            self.logger.info(
                "Captured payload: %s bytes in %s item(s)",
                f"{total_bytes:,}",
                len(captures),
            )
            self.logger.info("Payload written to %s", captured_path)
        else:
            self.logger.info("No loadstring payload captured")
        self.logger.info("Sandbox finished in %.2f seconds", duration)

        return SandboxResult(
            returncode=returncode,
            timed_out=timed_out,
            output_limited=output_limited,
            output_bytes=drainer.saved_bytes,
            duration_seconds=duration,
            captures=captures,
            captured_path=captured_path,
            captured_paths=captured_paths,
            run_log_path=run_log_path,
            trace_token=trace_token,
            isolation_backend=sandbox_backend,
            stalled=stalled,
        )

    def _resolve_native_host(self) -> Path | None:
        names = (
            ("protez-native-host.exe", "protez-native-host")
            if os.name == "nt"
            else ("protez-native-host", "protez-native-host.exe")
        )
        candidates = [self.tools_dir / name for name in names]
        path_from_env = shutil.which("protez-native-host")
        if path_from_env:
            candidates.append(Path(path_from_env))
        for candidate in candidates:
            try:
                if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
                    return candidate.resolve()
            except OSError:
                continue
        return None

    def _linux_isolated_command(
        self,
        native_host: Path,
        source_path: Path,
        worker_args: list[str],
        timeout_seconds: float,
    ) -> list[str]:
        bwrap = shutil.which("bwrap")
        prlimit = shutil.which("prlimit")
        if prlimit is None:
            raise SandboxError(
                "Linux dynamic analysis needs prlimit; install it to enable isolated execution."
            )
        limits = [
            prlimit,
            f"--as={1024 * 1024 * 1024}",
            f"--cpu={max(1, math.ceil(timeout_seconds) + 1)}",
            "--fsize=1048576",
            "--nofile=64",
            "--core=0",
            "--",
        ]
        if bwrap is None:
            unshare = self._linux_unshare_command(native_host, source_path, worker_args)
            if unshare is not None:
                return [*limits, *unshare]
            raise SandboxError(
                "Linux dynamic analysis needs bubblewrap, or unshare with unprivileged user "
                "namespaces; install one of them to enable isolated execution."
            )

        command = [
            *limits,
            bwrap,
            "--unshare-all",
            "--die-with-parent",
            "--new-session",
            "--ro-bind",
            "/usr",
            "/usr",
        ]
        for runtime_dir in (Path("/lib"), Path("/lib64")):
            try:
                resolved_dir = runtime_dir.resolve(strict=True)
                if resolved_dir.is_dir():
                    # The ELF interpreter commonly lives under /lib64 even when
                    # that path is a symlink to /usr/lib64 on the host.
                    command.extend(["--ro-bind", str(resolved_dir), str(runtime_dir)])
            except OSError:
                continue
        command.extend(["--dir", "/etc"])
        loader_cache = Path("/etc/ld.so.cache")
        if loader_cache.is_file():
            command.extend(["--ro-bind", str(loader_cache), "/etc/ld.so.cache"])
        command.extend(
            [
                "--dev",
                "/dev",
                "--tmpfs",
                "/tmp",
                "--ro-bind",
                str(native_host),
                "/protez-native-host",
                "--ro-bind",
                str(source_path),
                "/input.luau",
                "--clearenv",
                "--setenv",
                "HOME",
                "/tmp",
                "--setenv",
                "PATH",
                "/usr/bin:/bin",
                "--setenv",
                "LANG",
                "C",
                "--setenv",
                "LC_ALL",
                "C",
                "--chdir",
                "/tmp",
                "--",
                "/protez-native-host",
                "--source",
                "/input.luau",
                *worker_args,
            ]
        )
        return command

    @staticmethod
    def _unprivileged_namespaces_available() -> bool:
        """Whether this host lets a plain user build user/mount/pid/net namespaces.

        bubblewrap is the first choice, but it is a package that is not installed
        everywhere; Linux has answered the same question in userspace since 3.8
        with ``unshare``.  The probe is cached because it costs a process.
        """

        cached = Sandbox._UNSHARE_PROBE
        if cached is not None:
            return cached
        available = False
        unshare = shutil.which("unshare")
        if unshare is not None:
            try:
                probe = subprocess.run(
                    [
                        unshare,
                        "--user",
                        "--map-root-user",
                        "--mount",
                        "--pid",
                        "--fork",
                        "--net",
                        "--",
                        "true",
                    ],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    timeout=10,
                    check=False,
                )
                available = probe.returncode == 0
            except (OSError, subprocess.SubprocessError):
                available = False
        Sandbox._UNSHARE_PROBE = available
        return available

    def _linux_unshare_command(
        self,
        native_host: Path,
        source_path: Path,
        worker_args: list[str],
    ) -> list[str] | None:
        """The bubblewrap recipe rebuilt on ``unshare`` from util-linux.

        Same guarantees: a private network namespace (no sockets), a private
        mount namespace whose root holds nothing but read-only copies of the
        interpreter's own runtime, the worker and the staged source, a private
        PID namespace, and no privileges.
        """

        unshare = shutil.which("unshare")
        if unshare is None or not self._unprivileged_namespaces_available():
            return None
        root = source_path.parent / "protez-root"
        script_lines = [
            "set -eu",
            "mount --make-rprivate /",
            f"mkdir -p {shlex.quote(str(root))}",
            f"mount -t tmpfs -o mode=0755 tmpfs {shlex.quote(str(root))}",
        ]
        for name in ("usr", "lib", "lib64"):
            script_lines.extend(
                [
                    f"mkdir -p {shlex.quote(str(root / name))}",
                    f"if [ -d /{name} ]; then "
                    f"mount --bind /{name} {shlex.quote(str(root / name))} && "
                    f"mount -o remount,ro,bind {shlex.quote(str(root / name))}; fi",
                ]
            )
        script_lines.append(f"mkdir -p {shlex.quote(str(root / 'etc'))}")
        script_lines.append(
            "if [ -f /etc/ld.so.cache ]; then "
            f": > {shlex.quote(str(root / 'etc' / 'ld.so.cache'))} && "
            f"mount --bind /etc/ld.so.cache {shlex.quote(str(root / 'etc' / 'ld.so.cache'))} && "
            f"mount -o remount,ro,bind {shlex.quote(str(root / 'etc' / 'ld.so.cache'))}; fi"
        )
        for name, mode in (("dev", "0755"), ("tmp", "1777")):
            script_lines.extend(
                [
                    f"mkdir -p {shlex.quote(str(root / name))}",
                    f"mount -t tmpfs -o mode={mode} tmpfs {shlex.quote(str(root / name))}",
                ]
            )
        script_lines.append(f"mkdir -p {shlex.quote(str(root / 'proc'))}")
        script_lines.append(
            f"mount -t proc none {shlex.quote(str(root / 'proc'))} 2>/dev/null || true"
        )
        for staged, target in ((native_host, "protez-native-host"), (source_path, "input.luau")):
            destination = root / target
            script_lines.extend(
                [
                    f": > {shlex.quote(str(destination))} && "
                    f"mount --bind {shlex.quote(str(staged))} {shlex.quote(str(destination))} && "
                    f"mount -o remount,ro,bind {shlex.quote(str(destination))}",
                ]
            )
        worker = " ".join(
            shlex.quote(part) for part in ("--source", "/input.luau", *worker_args)
        )
        chroot = shutil.which("chroot") or "/usr/sbin/chroot"
        script_lines.append(
            f"exec {shlex.quote(chroot)} {shlex.quote(str(root))} /usr/bin/env -i HOME=/tmp "
            f"PATH=/usr/bin:/bin LANG=C LC_ALL=C /protez-native-host {worker}"
        )
        return [
            unshare,
            "--user",
            "--map-root-user",
            "--mount",
            "--pid",
            "--fork",
            "--net",
            "--",
            "/bin/sh",
            "-c",
            "\n".join(script_lines),
        ]

    @staticmethod
    def _minimal_environment() -> dict[str, str]:
        if os.name == "nt":
            environment: dict[str, str] = {}
            for name in ("SystemRoot", "WINDIR", "TEMP", "TMP", "PATHEXT"):
                value = os.environ.get(name)
                if value:
                    environment[name] = value
            system_root = environment.get("SystemRoot") or environment.get("WINDIR")
            if system_root:
                environment["PATH"] = str(Path(system_root) / "System32")
            return environment
        return {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}

    @staticmethod
    def _kill_process(process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            try:
                process.kill()
            except OSError:
                pass
        try:
            process.wait(timeout=2.0)
        except subprocess.TimeoutExpired:
            try:
                process.kill()
            except OSError:
                pass


__all__ = [
    "CapturedPayload",
    "Sandbox",
    "SandboxError",
    "SandboxResult",
]
