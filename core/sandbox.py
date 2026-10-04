from __future__ import annotations

import base64
import binascii
import logging
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
import threading
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import BinaryIO

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_TOOLS_DIR = ROOT / "tools"
DEFAULT_LOGS_DIR = ROOT / "logs"
ENVLOG_PATH = ROOT / "sandbox" / "envlog.luau"
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
    run_log_path: Path


class _PipeDrainer(threading.Thread):
    def __init__(self, stream: BinaryIO, destination: Path, byte_limit: int):
        super().__init__(name="protez-luau-output", daemon=True)
        self._stream = stream
        self._destination = destination
        self._byte_limit = byte_limit
        self.limit_hit = threading.Event()
        self.total_bytes = 0
        self.saved_bytes = 0
        self.error: OSError | None = None

    def run(self) -> None:
        try:
            with self._destination.open("wb") as output:
                while True:
                    chunk = self._stream.read(64 * 1024)
                    if not chunk:
                        break
                    self.total_bytes += len(chunk)
                    remaining = self._byte_limit - self.saved_bytes
                    if remaining > 0:
                        saved = chunk[:remaining]
                        output.write(saved)
                        self.saved_bytes += len(saved)
                    if self.total_bytes > self._byte_limit:
                        self.limit_hit.set()
        except (OSError, ValueError) as exc:
            self.error = OSError(str(exc))


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

    def parse(self, log_path: Path) -> tuple[tuple[CapturedPayload, ...], Path | None]:
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
            return tuple(self._captures), self._capture_path
        self._capture_path.unlink(missing_ok=True)
        return (), None

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
        destination = self._capture_path.with_name(f"captured_payload_{index:03d}.luau")
        os.replace(self._current_path, destination)
        self._latest_path = destination
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
    """Run a Luau file in a separate process with a hard timeout.

    The mock runtime is not an OS-level security boundary. Use a disposable
    operating-system account or VM when testing untrusted input.
    """

    def __init__(
        self,
        *,
        tools_dir: Path | str = DEFAULT_TOOLS_DIR,
        logs_dir: Path | str = DEFAULT_LOGS_DIR,
        envlog_path: Path | str = ENVLOG_PATH,
        luau_path: Path | str | None = None,
        timeout_seconds: float = 5.0,
        max_input_bytes: int = 16 * 1024 * 1024,
        max_output_bytes: int = 32 * 1024 * 1024,
        logger: logging.Logger | None = None,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        if max_input_bytes <= 0 or max_output_bytes <= 0:
            raise ValueError("input and output limits must be positive")
        self.tools_dir = Path(tools_dir).expanduser().resolve()
        self.logs_dir = Path(logs_dir).expanduser().resolve()
        self.envlog_path = Path(envlog_path).expanduser().resolve()
        self.capture_path = self.logs_dir / CAPTURE_PATH.name
        self.luau_path = (
            Path(luau_path).expanduser().resolve() if luau_path is not None else None
        )
        self.timeout_seconds = float(timeout_seconds)
        self.max_input_bytes = int(max_input_bytes)
        self.max_output_bytes = int(max_output_bytes)
        self.logger = logger or logging.getLogger("protez")
        self._run_lock = threading.Lock()

    def run(self, source: str, *, source_name: str = "input") -> SandboxResult:
        if not isinstance(source, str):
            raise TypeError("source must be text")
        source_bytes = source.encode("utf-8")
        if len(source_bytes) > self.max_input_bytes:
            raise SandboxError(
                f"Input is {len(source_bytes):,} bytes; limit is {self.max_input_bytes:,} bytes"
            )
        if not source.strip():
            raise SandboxError("Input is empty")

        with self._run_lock:
            return self._run_once(source, source_name, len(source_bytes))

    def _run_once(self, source: str, source_name: str, source_size: int) -> SandboxResult:
        binary = self._resolve_luau_binary()
        try:
            envlog = self.envlog_path.read_text(encoding="utf-8")
        except OSError as exc:
            raise SandboxError(f"Could not read sandbox environment {self.envlog_path}: {exc}") from exc
        if "__PROTEZ_CAPTURE_TOKEN__" not in envlog:
            raise SandboxError("Sandbox environment is missing its capture-token placeholder")

        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.capture_path.parent.mkdir(parents=True, exist_ok=True)
        self.capture_path.unlink(missing_ok=True)
        for previous_capture in self.logs_dir.glob("captured_payload_[0-9]*.luau"):
            previous_capture.unlink(missing_ok=True)
        token = secrets.token_hex(16)
        runner_text = self._build_runner(envlog, token, source)
        run_stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        run_log_path = self.logs_dir / f"sandbox_{run_stamp}_{token[:8]}.log"
        timeout = self.timeout_seconds
        started = time.monotonic()

        self.logger.info("Deobfuscation input: %s (%s bytes)", source_name, f"{source_size:,}")
        self.logger.warning(
            "Process timeout is enabled; this mock is not an OS-level security boundary"
        )

        with tempfile.TemporaryDirectory(prefix="protez-sandbox-", dir=self.logs_dir) as temp_dir:
            runner_path = Path(temp_dir) / "runner.luau"
            try:
                runner_path.write_text(runner_text, encoding="utf-8")
            except OSError as exc:
                raise SandboxError(f"Could not prepare Luau runner: {exc}") from exc

            creationflags = 0
            popen_options: dict[str, object] = {}
            if os.name == "nt":
                creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
                creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
            else:
                popen_options["start_new_session"] = True

            try:
                process = subprocess.Popen(
                    [str(binary), str(runner_path)],
                    cwd=temp_dir,
                    env=self._minimal_environment(),
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                    creationflags=creationflags,
                    **popen_options,
                )
            except OSError as exc:
                raise SandboxError(f"Could not start Luau interpreter {binary}: {exc}") from exc

            if process.stdout is None:
                self._kill_process(process)
                raise SandboxError("Luau process did not expose an output stream")

            self.logger.info("Sandbox spawned (Luau CLI process)")
            self.logger.info("Hooking loadstring, load, require, game, Instance")
            drainer = _PipeDrainer(process.stdout, run_log_path, self.max_output_bytes)
            drainer.start()
            timed_out = False
            output_limited = False
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
                time.sleep(0.025)

            try:
                returncode = process.wait(timeout=2.0)
            except subprocess.TimeoutExpired:
                self._kill_process(process)
                returncode = process.wait()

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
            if drainer.limit_hit.is_set():
                output_limited = True

        try:
            parser = _CaptureParser(
                token=token,
                capture_path=self.capture_path,
                logger=self.logger,
                max_payload_bytes=self.max_output_bytes,
            )
            captures, captured_path = parser.parse(run_log_path)
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
        if returncode != 0 and not timed_out and not output_limited:
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
            run_log_path=run_log_path,
        )

    def _resolve_luau_binary(self) -> Path:
        if self.luau_path is not None:
            candidates = [self.luau_path]
        else:
            names = ("luau.exe", "luau") if os.name == "nt" else ("luau", "luau.exe")
            candidates = [self.tools_dir / name for name in names]
            path_from_env = shutil.which("luau")
            if path_from_env:
                candidates.append(Path(path_from_env))

        for candidate in candidates:
            try:
                if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
                    return candidate.resolve()
            except OSError:
                continue
        expected = self.tools_dir / ("luau.exe" if os.name == "nt" else "luau")
        raise SandboxError(
            f"Luau CLI not found at {expected}. Run installer.py or place the official binary there."
        )

    @staticmethod
    def _build_runner(envlog: str, token: str, source: str) -> str:
        prelude = envlog.replace("__PROTEZ_CAPTURE_TOKEN__", token)
        if prelude == envlog:
            raise SandboxError("Could not set the sandbox capture token")
        return (
            prelude
            + "\nlocal function __PROTEZ_INPUT(...)\n"
            + source
            + "\nend\n"
            + "local __protez_run_ok, __protez_run_error = "
            + "__protez_raw_pcall(__PROTEZ_INPUT)\n"
            + "if not __protez_run_ok then\n"
            + "    __protez_log('ERROR', __protez_run_error)\n"
            + "end\n"
        )

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
