from __future__ import annotations

import hashlib
import json
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

from core.deobfuscator import DeobfuscationResult, deobfuscate_source
from core.runtime_paths import LOGS_DIR, OUTPUT_DIR, TOOLS_DIR
from core.sandbox import Sandbox, SandboxError, SandboxResult
from core.tracer import Tracer
from core.version import VERSION

DEFAULT_OUTPUT_DIR = OUTPUT_DIR
DEFAULT_TOOLS_DIR = TOOLS_DIR
MAX_PAYLOAD_LAYERS = 6
MAX_PAYLOAD_CANDIDATES = 20
MAX_PIPELINE_SECONDS = 90.0


class PipelineError(RuntimeError):
    pass


class InvalidLuauPayload(PipelineError):
    pass


@dataclass(frozen=True)
class PipelineResult:
    output_path: Path
    report_path: Path
    route: str
    decoded_layers: int
    transformations: tuple[str, ...]
    sandbox_result: SandboxResult | None


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
        native_host = compiler.name.lower().startswith("protez-native-host")
        started = time.monotonic()
        backend = "bundled Luau compiler" if native_host else "luau-compile"
        self.logger.info("Verifying source with %s: %s", backend, source_path.name)

        try:
            with tempfile.TemporaryFile(mode="w+b") as diagnostics:
                process = self._start_compiler(
                    compiler,
                    source_path,
                    diagnostics,
                    compile_only=native_host,
                )
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
            raise PipelineError(f"Could not run the Luau compiler: {exc}") from exc

        if returncode != 0:
            message = detail or f"compiler exited with code {returncode}"
            raise InvalidLuauPayload(f"Source is not valid Luau: {message}")
        self.logger.info("Luau syntax check passed in %.2f seconds", time.monotonic() - started)

    def verify_text(self, source: str, *, label: str = "candidate") -> None:
        temporary_path: Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                errors="strict",
                suffix=".luau",
                prefix="protez-check-",
                delete=False,
            ) as temporary:
                temporary.write(source)
                temporary_path = Path(temporary.name)
            self.verify(temporary_path)
        except UnicodeEncodeError as exc:
            raise InvalidLuauPayload(f"{label} is not valid UTF-8 text: {exc}") from exc
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)

    def _resolve_binary(self) -> Path:
        if os.name == "nt":
            host_names = ("protez-native-host.exe", "protez-native-host")
            compiler_names = ("luau-compile.exe", "luau-compile")
        else:
            host_names = ("protez-native-host", "protez-native-host.exe")
            compiler_names = ("luau-compile", "luau-compile.exe")
        candidates = [self.tools_dir / name for name in (*host_names, *compiler_names)]
        for command_name in ("protez-native-host", "luau-compile"):
            path_from_env = shutil.which(command_name)
            if path_from_env:
                candidates.append(Path(path_from_env))
        for candidate in candidates:
            try:
                if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
                    return candidate.resolve()
            except OSError:
                continue
        expected = self.tools_dir / host_names[0]
        raise PipelineError(
            f"Luau compiler not found at {expected}. The installer will repair the bundled runtime."
        )

    def _start_compiler(
        self,
        compiler: Path,
        source_path: Path,
        diagnostics,
        *,
        compile_only: bool = False,
    ) -> subprocess.Popen:
        creationflags = 0
        options: dict[str, object] = {}
        if os.name == "nt":
            creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        else:
            options["start_new_session"] = True

        try:
            command = [str(compiler)]
            if compile_only:
                command.extend(["--source", str(source_path), "--compile-only"])
            else:
                command.append(str(source_path))
            return subprocess.Popen(
                command,
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
    """Static Luau cleanup plus bounded, iterative extraction of local loader layers."""

    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
        output_dir: Path | str = DEFAULT_OUTPUT_DIR,
        tools_dir: Path | str = DEFAULT_TOOLS_DIR,
        compiler_timeout_seconds: float = 10.0,
        sandbox_timeout_seconds: float = 5.0,
        max_payload_layers: int = MAX_PAYLOAD_LAYERS,
        max_payload_candidates: int = MAX_PAYLOAD_CANDIDATES,
        max_pipeline_seconds: float = MAX_PIPELINE_SECONDS,
    ):
        if (
            compiler_timeout_seconds <= 0
            or sandbox_timeout_seconds <= 0
            or max_payload_layers < 0
            or max_payload_candidates <= 0
            or max_pipeline_seconds <= 0
        ):
            raise ValueError("timeouts must be positive; layer/candidate limits cannot be negative")
        self.logger = logger or logging.getLogger("protez")
        self.progress_callback = progress_callback
        self.output_dir = Path(output_dir).expanduser().resolve()
        self.tools_dir = Path(tools_dir).expanduser().resolve()
        self.compiler_timeout_seconds = compiler_timeout_seconds
        self.sandbox_timeout_seconds = sandbox_timeout_seconds
        self.max_payload_layers = max_payload_layers
        self.max_payload_candidates = max_payload_candidates
        self.max_pipeline_seconds = max_pipeline_seconds

    def run(self, source: str, *, source_name: str = "input") -> PipelineResult:
        if not isinstance(source, str):
            raise TypeError("source must be text")
        if self._running_elevated():
            raise PipelineError(
                "For safety, Protez will not execute input while running as Administrator. "
                "Close it and launch Protez normally; only the installer needs elevation."
            )

        started = time.monotonic()
        deadline = started + self.max_pipeline_seconds
        source_analysis = deobfuscate_source(source)
        self.logger.info("Static Luau analysis started (%s bytes)", f"{source_analysis.input_bytes:,}")
        self._log_transformations("Input", source_analysis)
        self._progress(8, "ANALYZE")

        compiler = _LuauCompiler(
            tools_dir=self.tools_dir,
            timeout_seconds=self.compiler_timeout_seconds,
            logger=self.logger,
        )
        original_is_valid = self._is_valid_source(compiler, source, "original input", deadline)
        if source_analysis.changed:
            decoded_is_valid = self._is_valid_source(
                compiler,
                source_analysis.source,
                "statically decoded input",
                deadline,
            )
        else:
            decoded_is_valid = original_is_valid
        if decoded_is_valid:
            self.logger.info("A valid source layer is available as a fallback")
        else:
            self.logger.warning("Input did not pass the Luau syntax check after static decoding")
        runtime_source = source if original_is_valid else source_analysis.source

        sandbox = Sandbox(
            tools_dir=self.tools_dir,
            timeout_seconds=self.sandbox_timeout_seconds,
            logger=self.logger,
        )
        self._progress(18, "SANDBOX")
        initial_result: SandboxResult | None = None
        pending: list[tuple[str, int, str]] = []
        remaining = deadline - time.monotonic()
        if remaining > 0:
            sandbox.timeout_seconds = min(self.sandbox_timeout_seconds, remaining)
            try:
                initial_result = sandbox.run(runtime_source, source_name=source_name)
            except SandboxError as exc:
                self.logger.error("Initial sandbox attempt failed: %s", exc)
            except Exception:
                self.logger.exception("Initial sandbox attempt failed unexpectedly")
        else:
            self.logger.warning("Skipped initial sandbox after reaching the total runtime limit")

        if initial_result is not None:
            self._log_sandbox_status(initial_result, "Input")
            pending.extend(
                (payload, 1, f"layer-{index}")
                for index, payload in enumerate(self._captured_texts(initial_result), start=1)
            )

        best_source: str | None = (
            source_analysis.source if decoded_is_valid else source if original_is_valid else None
        )
        best_depth = 0 if best_source is not None else -1
        best_transformations = (
            source_analysis.transformations if decoded_is_valid else ()
        )
        best_route = "static-source" if decoded_is_valid and source_analysis.changed else "direct-source"
        candidate_count = 0
        seen: set[str] = set()
        layer_report: list[dict[str, object]] = []
        self._progress(30, "DECODE")

        while pending and candidate_count < self.max_payload_candidates:
            if time.monotonic() >= deadline:
                self.logger.warning("Stopped payload exploration at the total runtime limit")
                break
            candidate, depth, candidate_name = pending.pop(0)
            fingerprint = hashlib.sha256(candidate.encode("utf-8", errors="replace")).hexdigest()
            if fingerprint in seen:
                self.logger.info("Ignoring an already-seen payload candidate (%s)", candidate_name)
                continue
            seen.add(fingerprint)
            candidate_count += 1

            try:
                analysis = deobfuscate_source(candidate)
            except (TypeError, ValueError) as exc:
                self.logger.warning("Could not statically decode %s: %s", candidate_name, exc)
                continue
            self._log_transformations(candidate_name, analysis)
            try:
                original_valid = self._is_valid_source(
                    compiler,
                    candidate,
                    f"{candidate_name} original",
                    deadline,
                )
                decoded_valid = (
                    self._is_valid_source(compiler, analysis.source, candidate_name, deadline)
                    if analysis.changed
                    else original_valid
                )
            except PipelineError:
                if time.monotonic() >= deadline:
                    self.logger.warning("Stopped syntax validation at the total runtime limit")
                    break
                raise
            valid = original_valid or decoded_valid
            output_candidate = analysis.source if decoded_valid else candidate
            runtime_candidate = candidate if original_valid else analysis.source if decoded_valid else None
            layer_report.append(
                {
                    "depth": depth,
                    "name": candidate_name,
                    "sha256": hashlib.sha256(output_candidate.encode("utf-8")).hexdigest(),
                    "valid_luau": valid,
                    "original_valid_luau": original_valid,
                    "decoded_valid_luau": decoded_valid,
                    "transformations": list(analysis.transformations),
                }
            )
            if valid and depth >= best_depth:
                best_source = output_candidate
                best_depth = depth
                best_transformations = analysis.transformations if decoded_valid else ()
                best_route = "decoded-payload"

            if (
                runtime_candidate is None
                or depth >= self.max_payload_layers
                or not self._looks_like_loader(runtime_candidate)
            ):
                continue
            if time.monotonic() >= deadline:
                self.logger.warning("Payload recursion reached the total runtime limit")
                break

            self.logger.info("Inspecting captured layer %s in the bounded sandbox", depth)
            self._progress(min(75, 30 + depth * 7), "DECODE")
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                self.logger.warning("Stopped nested sandbox work at the total runtime limit")
                break
            sandbox.timeout_seconds = min(self.sandbox_timeout_seconds, remaining)
            try:
                nested_result = sandbox.run(
                    runtime_candidate,
                    source_name=f"{source_name} [{candidate_name}]",
                )
            except SandboxError as exc:
                self.logger.warning("Sandbox could not inspect %s: %s", candidate_name, exc)
                continue
            except Exception:
                self.logger.exception("Nested sandbox failed for %s", candidate_name)
                continue
            self._log_sandbox_status(nested_result, candidate_name)
            nested_payloads = self._captured_texts(nested_result)
            for index, payload in enumerate(nested_payloads, start=1):
                pending.append((payload, depth + 1, f"{candidate_name}.{index}"))

        if best_source is None:
            return self._trace_unresolved(
                runtime_source,
                source_name,
                layer_report,
                deadline=deadline,
            )

        if initial_result is not None and initial_result.timed_out:
            self.logger.warning("Keeping the valid source fallback after the sandbox time limit")
        if initial_result is not None and initial_result.output_limited:
            self.logger.warning("Keeping the valid source fallback after the sandbox output limit")

        decoded_layers = max(0, best_depth)
        return self._write_result(
            source=best_source,
            original_source=source,
            source_name=source_name,
            route=best_route,
            decoded_layers=decoded_layers,
            transformations=best_transformations,
            source_analysis=source_analysis,
            candidate_count=candidate_count,
            layer_report=layer_report,
            sandbox_result=initial_result,
            duration_seconds=time.monotonic() - started,
        )

    def _is_valid_source(
        self,
        compiler: _LuauCompiler,
        source: str,
        label: str,
        deadline: float,
    ) -> bool:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise PipelineError("The total pipeline time limit was reached during syntax validation")
        compiler.timeout_seconds = min(compiler.timeout_seconds, max(0.001, remaining))
        try:
            compiler.verify_text(source, label=label)
            return True
        except InvalidLuauPayload as exc:
            self.logger.info("%s is not yet valid Luau: %s", label, str(exc)[:1200])
            return False

    @staticmethod
    def _captured_texts(result: SandboxResult) -> tuple[str, ...]:
        paths = result.captured_paths or ((result.captured_path,) if result.captured_path else ())
        payloads: list[str] = []
        for path in paths:
            if path is None:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if text.strip():
                payloads.append(text)
        return tuple(payloads)

    def _log_transformations(self, label: str, result: DeobfuscationResult) -> None:
        if not result.transformations:
            self.logger.info("%s: no static decoder patterns matched", label)
            return
        for transformation in result.transformations:
            self.logger.info("%s: applied %s", label, transformation)

    def _log_sandbox_status(self, result: SandboxResult, label: str) -> None:
        if result.timed_out:
            self.logger.warning("%s sandbox stage timed out", label)
        if result.output_limited:
            self.logger.warning("%s sandbox stage hit the output limit", label)
        if result.returncode not in (0, None) and not result.timed_out:
            self.logger.warning("%s sandbox stage exited with code %s", label, result.returncode)
        if result.captures:
            kinds = ", ".join(item.kind for item in result.captures)
            self.logger.info("%s captured %s payload layer(s): %s", label, len(result.captures), kinds)
        else:
            self.logger.info("%s produced no additional local payloads", label)

    @staticmethod
    def _looks_like_loader(source: str) -> bool:
        lowered = source.lower()
        return any(
            marker in lowered
            for marker in (
                "loadstring",
                "load(",
                "require(",
                "base64decode",
                "base64.decode",
                "httpget",
                "http_request",
                "crypt.base64",
            )
        )

    def _trace_unresolved(
        self,
        source: str,
        source_name: str,
        layer_report: list[dict[str, object]],
        *,
        deadline: float,
    ) -> PipelineResult:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            trace_path = LOGS_DIR / "trace.jsonl"
            report_path = self._write_failure_report(source, source_name, trace_path, layer_report)
            raise PipelineError(
                f"No valid Luau source was recovered before the total time limit. "
                f"Report: {report_path}. Tracing was skipped."
            )
        self.logger.warning("No valid source layer was recovered; starting an instruction/API trace")
        self._progress(82, "TRACE")
        try:
            trace_result = Tracer(
                logger=self.logger,
                progress_callback=self.progress_callback,
                tools_dir=self.tools_dir,
                timeout_seconds=remaining,
            ).trace(source, source_name=source_name)
        except Exception as trace_error:
            raise PipelineError(f"No valid Luau source was recovered; tracing failed: {trace_error}") from trace_error
        trace_path = trace_result.trace_files[0] if trace_result.trace_files else LOGS_DIR / "trace.jsonl"
        detail = (
            "Instruction trace saved; CFG lifting, register recovery and source reconstruction are not implemented."
            if trace_result.native_hooks_available
            else "Only mock/API events are available without the native host; no VM register trace was produced."
        )
        self.logger.error("Analysis incomplete: %s", detail)
        report_path = self._write_failure_report(source, source_name, trace_path, layer_report)
        raise PipelineError(f"No valid Luau source was recovered. Trace: {trace_path}. Report: {report_path}. {detail}")

    def _write_result(
        self,
        *,
        source: str,
        original_source: str,
        source_name: str,
        route: str,
        decoded_layers: int,
        transformations: tuple[str, ...],
        source_analysis: DeobfuscationResult,
        candidate_count: int,
        layer_report: list[dict[str, object]],
        sandbox_result: SandboxResult | None,
        duration_seconds: float,
    ) -> PipelineResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = self.output_dir / f"deobfuscated_{timestamp}.luau"
        report_path = self.output_dir / f"deobfuscated_{timestamp}.report.json"
        output_temp = output_path.with_name(output_path.name + ".tmp")
        report_temp = report_path.with_name(report_path.name + ".tmp")
        report = {
            "app_version": VERSION,
            "source_name": source_name,
            "route": route,
            "decoded_layers": decoded_layers,
            "candidate_count": candidate_count,
            "duration_seconds": round(duration_seconds, 3),
            "input_sha256": hashlib.sha256(original_source.encode("utf-8")).hexdigest(),
            "output_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "input_transformations": list(source_analysis.transformations),
            "selected_transformations": list(transformations),
            "layers": layer_report,
            "safety_notes": [
                "HTTP and remote module requests remain disabled in the mock runtime.",
                "Dynamic inspection is process-limited and is not an OS security boundary.",
                "A syntactically valid output is not a guarantee of full deobfuscation.",
            ],
        }
        try:
            output_temp.write_text(source, encoding="utf-8", newline="")
            os.replace(output_temp, output_path)
            report_temp.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
            os.replace(report_temp, report_path)
        except OSError as exc:
            output_temp.unlink(missing_ok=True)
            report_temp.unlink(missing_ok=True)
            raise PipelineError(f"Could not write output/report: {exc}") from exc

        self.logger.info("Recovered source through route: %s", route)
        self.logger.info("Output written to %s", output_path)
        self.logger.info("Analysis report written to %s", report_path)
        self._progress(100, "DONE")
        return PipelineResult(
            output_path=output_path,
            report_path=report_path,
            route=route,
            decoded_layers=decoded_layers,
            transformations=transformations,
            sandbox_result=sandbox_result,
        )

    def _write_failure_report(
        self,
        source: str,
        source_name: str,
        trace_path: Path,
        layer_report: list[dict[str, object]],
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        report_path = self.output_dir / f"analysis_{timestamp}.report.json"
        report = {
            "app_version": VERSION,
            "source_name": source_name,
            "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "recovered": False,
            "trace_path": str(trace_path),
            "layers": layer_report,
            "limitations": [
                "No syntactically valid source layer was recovered.",
                "Remote HTTP and require requests are disabled.",
                "VM handler lifting and source reconstruction are not implemented.",
            ],
        }
        try:
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except OSError as exc:
            self.logger.error("Could not write analysis report: %s", exc)
        return report_path

    @staticmethod
    def _running_elevated() -> bool:
        if os.name != "nt":
            return False
        try:
            import ctypes

            return bool(ctypes.windll.shell32.IsUserAnAdmin())
        except (AttributeError, OSError):
            return False

    def _progress(self, percent: float, stage: str) -> None:
        if self.progress_callback is not None:
            self.progress_callback(percent, stage)
