from __future__ import annotations

import logging
import os
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from core.sandbox import Sandbox, SandboxResult
from core.tracer import Tracer

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_OUTPUT_DIR = ROOT / "output"
DEFAULT_TOOLS_DIR = ROOT / "tools"


class PipelineError(RuntimeError):
    pass


class InvalidLuauPayload(PipelineError):
    pass


@dataclass(frozen=True)
class PipelineResult:
    output_path: Path
    payload_path: Path
    route: str
    sandbox_result: SandboxResult


class _LuauCompiler:
    def __init__(
        self,
        *,
        tools_dir: Path,
        timeout_seconds: float,
        logger: logging.Logger,
    ):
        self.tools_dir = tools_dir
        self.timeout_seconds = timeout_seconds
        self.logger = logger

    def verify(self, source_path: Path) -> None:
        compiler = self._resolve_binary()
        started = time.monotonic()
        self.logger.info("Verifying captured payload with luau-compile")

        try:
            with tempfile.TemporaryFile(mode="w+b") as diagnostics:
                process = self._start_compiler(compiler, source_path, diagnostics)
                try:
                    returncode = process.wait(timeout=self.timeout_seconds)
                except subprocess.TimeoutExpired as exc:
                    self._kill(process)
                    process.wait()
                    raise PipelineError(
                        f"Luau syntax verification exceeded {self.timeout_seconds:.1f} seconds"
                    ) from exc

                diagnostics.seek(0, os.SEEK_END)
                output_size = diagnostics.tell()
                diagnostics.seek(max(0, output_size - 8192))
                detail = diagnostics.read().decode("utf-8", errors="replace").strip()
        except OSError as exc:
            raise PipelineError(f"Could not run luau-compile: {exc}") from exc

        if returncode != 0:
            message = detail or f"compiler exited with code {returncode}"
            raise InvalidLuauPayload(f"Captured payload is not valid Luau: {message}")
        self.logger.info("Luau syntax verification passed in %.2f seconds", time.monotonic() - started)

    def _resolve_binary(self) -> Path:
        names = ("luau-compile.exe", "luau-compile") if os.name == "nt" else (
            "luau-compile",
            "luau-compile.exe",
        )
        candidates = [self.tools_dir / name for name in names]
        path_from_env = shutil.which("luau-compile")
        if path_from_env:
            candidates.append(Path(path_from_env))
        for candidate in candidates:
            try:
                if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
                    return candidate.resolve()
            except OSError:
                continue
        expected = self.tools_dir / ("luau-compile.exe" if os.name == "nt" else "luau-compile")
        raise PipelineError(
            f"Luau compiler not found at {expected}. Run installer.py or add the official compiler."
        )

    def _start_compiler(
        self,
        compiler: Path,
        source_path: Path,
        diagnostics,
    ) -> subprocess.Popen:
        creationflags = 0
        options: dict[str, object] = {}
        if os.name == "nt":
            creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        else:
            options["start_new_session"] = True

        try:
            return subprocess.Popen(
                [str(compiler), str(source_path)],
                cwd=source_path.parent,
                env=self._minimal_environment(),
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=diagnostics,
                close_fds=True,
                creationflags=creationflags,
                **options,
            )
        except OSError as exc:
            raise PipelineError(f"Could not start Luau compiler {compiler}: {exc}") from exc

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
    def _kill(process: subprocess.Popen) -> None:
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


class DeobfuscationPipeline:
    """MVP pipeline: sandbox, validate a captured source payload, and pass it through."""

    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
        output_dir: Path | str = DEFAULT_OUTPUT_DIR,
        tools_dir: Path | str = DEFAULT_TOOLS_DIR,
        compiler_timeout_seconds: float = 10.0,
    ):
        self.logger = logger or logging.getLogger("protez")
        self.progress_callback = progress_callback
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.tools_dir = Path(tools_dir).expanduser().resolve()
        self.compiler_timeout_seconds = compiler_timeout_seconds

    def run(self, source: str, *, source_name: str = "input") -> PipelineResult:
        self._progress(0, "SANDBOX")
        sandbox_result = Sandbox(logger=self.logger).run(source, source_name=source_name)
        self._progress(20, "SANDBOX")

        if sandbox_result.timed_out:
            raise PipelineError("Sandbox timed out before a stable payload was captured")
        if sandbox_result.output_limited:
            raise PipelineError("Sandbox output limit was reached; capture may be incomplete")
        if sandbox_result.captured_path is None:
            raise PipelineError(
                "No payload was captured. Remote HTTP requests are disabled in this build; "
                "only payloads produced locally by the input script can be recovered."
            )

        payload_path = sandbox_result.captured_path
        self.logger.info("Captured source found; checking for valid Luau")
        compiler = _LuauCompiler(
            tools_dir=self.tools_dir,
            timeout_seconds=self.compiler_timeout_seconds,
            logger=self.logger,
        )
        try:
            compiler.verify(payload_path)
        except InvalidLuauPayload as invalid_payload:
            self.logger.warning("Captured payload is not source Luau; starting trace fallback")
            self._progress(20, "TRACE")
            try:
                trace_result = Tracer(
                    logger=self.logger,
                    progress_callback=self.progress_callback,
                ).trace(source, source_name=source_name)
            except Exception as trace_error:
                raise PipelineError(
                    f"Payload validation failed ({invalid_payload}); tracing failed: {trace_error}"
                ) from trace_error
            if trace_result.native_hooks_available:
                raise PipelineError(
                    f"Trace saved to {trace_result.trace_files[0] if trace_result.trace_files else 'logs/trace.jsonl'}; "
                    "VM lifting is not implemented yet"
                )
            trace_path = trace_result.trace_files[0] if trace_result.trace_files else "logs/trace.jsonl"
            raise PipelineError(
                f"Trace was recorded at {trace_path}, but stock Luau exposes no debug.sethook; "
                "only mock/API events are available and VM register tracing is unavailable"
            )
        self.logger.info("Valid Luau payload detected; trace and lifting stages skipped")
        self._progress(90, "CODEGEN")

        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = self.output_dir / f"deobfuscated_{timestamp}.luau"
        temporary_path = output_path.with_name(f".{output_path.name}.tmp")
        try:
            shutil.copyfile(payload_path, temporary_path)
            os.replace(temporary_path, output_path)
        except OSError as exc:
            temporary_path.unlink(missing_ok=True)
            raise PipelineError(f"Could not write deobfuscated output: {exc}") from exc

        self.logger.info("Fast path used: captured Luau payload passed through unchanged")
        self.logger.info("Output written to %s", output_path)
        self._progress(100, "DONE")
        return PipelineResult(
            output_path=output_path,
            payload_path=payload_path,
            route="valid-luau-payload",
            sandbox_result=sandbox_result,
        )

    def _progress(self, percent: float, stage: str) -> None:
        if self.progress_callback is not None:
            self.progress_callback(percent, stage)
