from __future__ import annotations

import hashlib
import json
import logging
import os
import secrets
import shutil
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Callable

from core.bytecode_decompiler import (
    BUNDLED_DECOMPILER_COMMIT,
    BUNDLED_DECOMPILER_REPOSITORY,
    BytecodeDecompilerError,
    LocalBytecodeDecompiler,
)
from core.deobfuscator import (
    DeobfuscationResult,
    count_remote_payload_loaders,
    deobfuscate_source,
    tokenize,
)
from core.formatter import format_luau
from core.luraph_static import (
    LuraphStaticError,
    LuraphStaticUnpackResult,
    unpack_luraph_static,
)
from core.luraph_devirtualizer import (
    LuraphDevirtualizationError,
    LuraphDevirtualizationResult,
    devirtualize_luraph_v15,
)
from core.moonsec_devirtualizer import (
    MoonSecDevirtualizationError,
    MoonSecV3Result,
    devirtualize_moonsec_v3,
)
from core.protection import ProtectionProfile, inspect_protection
from core.runtime_paths import LOGS_DIR, OUTPUT_DIR, TOOLS_DIR
from core.sandbox import Sandbox, SandboxError, SandboxResult
from core.tracer import TraceError, TraceResult, Tracer
from core.version import VERSION

DEFAULT_OUTPUT_DIR = OUTPUT_DIR
DEFAULT_TOOLS_DIR = TOOLS_DIR
MAX_PAYLOAD_LAYERS = 6
MAX_PAYLOAD_CANDIDATES = 20
MAX_PIPELINE_SECONDS = 90.0
MAX_DYNAMIC_CAPTURE_ARTIFACT_BYTES = 16 * 1024 * 1024


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
    status: str = "complete"
    notice: str | None = None
    preview_path: Path | None = None
    trace_files: tuple[Path, ...] = ()
    trace_event_count: int = 0


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

    def run(self, source: str | bytes, *, source_name: str = "input") -> PipelineResult:
        if isinstance(source, bytes):
            return self._run_bytecode(source, source_name=source_name)
        if not isinstance(source, str):
            raise TypeError("source must be text or compiled Luau bytecode")

        started = time.monotonic()
        deadline = started + self.max_pipeline_seconds
        source_analysis = deobfuscate_source(source)
        protection = inspect_protection(source)
        if protection is not None:
            self._log_transformations("Input", source_analysis)
            family_lifter_error: str | None = None
            if protection.family == "MoonSec":
                remaining = deadline - time.monotonic()
                moonsec_result: MoonSecV3Result | None = None
                if remaining > 0:
                    self._progress(14, "DEVIRT")
                    try:
                        moonsec_result = devirtualize_moonsec_v3(
                            source,
                            tools_dir=self.tools_dir,
                            timeout_seconds=remaining,
                        )
                    except MoonSecDevirtualizationError as exc:
                        family_lifter_error = str(exc)
                    except Exception as exc:
                        family_lifter_error = f"unexpected {type(exc).__name__}: {exc}"
                        self.logger.exception("Unexpected error in the MoonSec V3 lifter")
                else:
                    family_lifter_error = "the total pipeline time limit was reached before VM lifting started"
                return self._write_moonsec_result(
                    source=source,
                    source_name=source_name,
                    profile=protection,
                    source_analysis=source_analysis,
                    devirtualized=moonsec_result,
                    error=family_lifter_error,
                    compiler=_LuauCompiler(
                        tools_dir=self.tools_dir,
                        timeout_seconds=self.compiler_timeout_seconds,
                        logger=self.logger,
                    ),
                    started=started,
                    deadline=deadline,
                )
            if (
                protection.family == "Luraph Obfuscator"
                and protection.version is not None
                and protection.version.split(".", maxsplit=1)[0] == "15"
            ):
                remaining = deadline - time.monotonic()
                if remaining > 0:
                    self._progress(14, "DEVIRT")
                    try:
                        devirtualized = devirtualize_luraph_v15(
                            source,
                            source_name=source_name,
                            tools_dir=self.tools_dir,
                            logs_dir=LOGS_DIR,
                            timeout_seconds=max(15.0, self.sandbox_timeout_seconds),
                            total_budget_seconds=remaining,
                            logger=self.logger,
                        )
                        return self._write_luraph_devirtualized_result(
                            source=source,
                            source_name=source_name,
                            profile=protection,
                            source_analysis=source_analysis,
                            devirtualized=devirtualized,
                            compiler=_LuauCompiler(
                                tools_dir=self.tools_dir,
                                timeout_seconds=self.compiler_timeout_seconds,
                                logger=self.logger,
                            ),
                            started=started,
                            deadline=deadline,
                        )
                    except LuraphDevirtualizationError as exc:
                        family_lifter_error = str(exc)
                        self.logger.warning("Luraph v15 VM lifting did not finish: %s", exc)
                    except Exception as exc:
                        family_lifter_error = f"unexpected {type(exc).__name__}: {exc}"
                        self.logger.exception("Unexpected error in the Luraph v15 lifter")
                else:
                    family_lifter_error = "the total pipeline time limit was reached before VM lifting started"
            notice = (
                f"{protection.display_name} detected; Protez will try family-specific VM lifting "
                "and isolated analysis. If lifting fails, the report will show the exact boundary."
            )
            self.logger.warning(notice)
            self._progress(8, "ANALYZE")
            return self._write_protection_analysis(
                source=source,
                source_name=source_name,
                profile=protection,
                source_analysis=source_analysis,
                duration_seconds=time.monotonic() - started,
                notice=notice,
                deadline=deadline,
                family_lifter_error=family_lifter_error,
            )

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
        trace_results: list[TraceResult] = []
        trace_error: str | None = None
        dynamic_attempted = False
        pending: list[tuple[str, int, str]] = []
        remaining = deadline - time.monotonic()
        if remaining > 0:
            sandbox.timeout_seconds = min(self.sandbox_timeout_seconds, remaining)
            try:
                dynamic_attempted = True
                initial_trace = self._trace_source(
                    sandbox,
                    runtime_source,
                    source_name=source_name,
                    label="input",
                    timeout_seconds=min(self.sandbox_timeout_seconds, remaining),
                )
                trace_results.append(initial_trace)
                initial_result = initial_trace.sandbox_result
            except (SandboxError, TraceError) as exc:
                trace_error = str(exc)
                self.logger.error("Initial sandbox attempt failed: %s", exc)
            except Exception as exc:
                trace_error = f"unexpected {type(exc).__name__}: {exc}"
                self.logger.exception("Initial sandbox attempt failed unexpectedly")
        else:
            self.logger.warning("Skipped initial sandbox after reaching the total runtime limit")
            trace_error = "the total runtime limit was reached before dynamic analysis started"

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
                nested_trace = self._trace_source(
                    sandbox,
                    runtime_candidate,
                    source_name=f"{source_name} [{candidate_name}]",
                    label=candidate_name,
                    timeout_seconds=min(self.sandbox_timeout_seconds, remaining),
                )
                trace_results.append(nested_trace)
                nested_result = nested_trace.sandbox_result
            except (SandboxError, TraceError) as exc:
                layer_report[-1]["dynamic_trace_error"] = str(exc)
                self.logger.warning("Sandbox could not inspect %s: %s", candidate_name, exc)
                continue
            except Exception:
                layer_report[-1]["dynamic_trace_error"] = "unexpected tracing error"
                self.logger.exception("Nested sandbox failed for %s", candidate_name)
                continue
            self._log_sandbox_status(nested_result, candidate_name)
            nested_payloads = self._captured_texts(nested_result)
            for index, payload in enumerate(nested_payloads, start=1):
                pending.append((payload, depth + 1, f"{candidate_name}.{index}"))

        if best_source is None:
            return self._trace_unresolved(
                source,
                source_name,
                layer_report,
                trace_results=trace_results,
                trace_error=trace_error,
                dynamic_attempted=dynamic_attempted,
            )

        if initial_result is not None and initial_result.timed_out:
            self.logger.warning("Keeping the valid source fallback after the sandbox time limit")
        if initial_result is not None and initial_result.output_limited:
            self.logger.warning("Keeping the valid source fallback after the sandbox output limit")

        best_source, formatting_applied = self._format_verified_candidate(
            best_source,
            compiler,
            label="formatted recovered source",
            deadline=deadline,
        )
        decoded_layers = max(0, best_depth)
        selected_transformations = best_transformations + (
            ("compile-verified whitespace formatting",) if formatting_applied else ()
        )
        return self._write_result(
            source=best_source,
            formatting_applied=formatting_applied,
            original_source=source,
            source_name=source_name,
            route=best_route,
            decoded_layers=decoded_layers,
            transformations=selected_transformations,
            source_analysis=source_analysis,
            candidate_count=candidate_count,
            layer_report=layer_report,
            sandbox_result=initial_result,
            duration_seconds=time.monotonic() - started,
            trace_results=trace_results,
            trace_error=trace_error,
            dynamic_attempted=dynamic_attempted,
        )

    def _run_bytecode(self, bytecode: bytes, *, source_name: str) -> PipelineResult:
        started = time.monotonic()
        deadline = started + self.max_pipeline_seconds
        self.logger.info("Offline Luau bytecode decompilation started (%s bytes)", f"{len(bytecode):,}")
        self._progress(8, "BYTECODE")
        decompiler = LocalBytecodeDecompiler(
            tools_dir=self.tools_dir,
            timeout_seconds=min(30.0, self.max_pipeline_seconds),
            logger=self.logger,
        )
        try:
            source, binary = decompiler.decompile(bytecode, source_name=source_name)
        except BytecodeDecompilerError as exc:
            raise PipelineError(str(exc)) from exc

        elapsed = time.monotonic() - started
        if elapsed >= self.max_pipeline_seconds:
            raise PipelineError("The total pipeline time limit was reached during bytecode decompilation")
        self._progress(78, "VERIFY")
        compiler = _LuauCompiler(
            tools_dir=self.tools_dir,
            timeout_seconds=min(self.compiler_timeout_seconds, self.max_pipeline_seconds - elapsed),
            logger=self.logger,
        )
        try:
            compiler.verify_text(source, label="decompiled bytecode output")
        except InvalidLuauPayload as exc:
            raise PipelineError(f"The local decompiler did not produce valid Luau: {exc}") from exc
        source, formatting_applied = self._format_verified_candidate(
            source,
            compiler,
            label="formatted decompiled bytecode",
            deadline=deadline,
        )
        bundled_binary = decompiler.is_bundled_binary(binary)
        transformations = ("offline Luau bytecode decompilation",) + (
            ("compile-verified whitespace formatting",) if formatting_applied else ()
        )

        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = self.output_dir / f"decompiled_{timestamp}.luau"
        report_path = self.output_dir / f"decompiled_{timestamp}.report.json"
        output_temp = output_path.with_name(output_path.name + ".tmp")
        report_temp = report_path.with_name(report_path.name + ".tmp")
        report = {
            "app_version": VERSION,
            "status": "complete",
            "route": "local-luau-bytecode-decompiler",
            "source_name": source_name,
            "decompiler": binary.name,
            "decompiler_provenance": (
                "verified-frozen-bundle" if bundled_binary else "local-binary-unverified"
            ),
            "decompiler_repository": BUNDLED_DECOMPILER_REPOSITORY if bundled_binary else None,
            "decompiler_source_commit": BUNDLED_DECOMPILER_COMMIT if bundled_binary else None,
            "formatting_applied": formatting_applied,
            "formatting_validation": "compile-only" if formatting_applied else None,
            "transformations": list(transformations),
            "bytecode_size": len(bytecode),
            "bytecode_sha256": hashlib.sha256(bytecode).hexdigest(),
            "output_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "bytecode_executed": False,
            "source_compiled_for_syntax_check_only": True,
            "original_source_recovered": False,
            "known_loss": [
                "Compilation discards comments and may omit original variable names without debug metadata.",
                "Recovered source is a semantic approximation, not a byte-for-byte copy of the original script.",
                "Opcode-shuffled or unsupported custom bytecode may produce partial or incorrect output.",
                "The pinned upstream README documents standard Luau bytecode v3-v9; support for other versions is not claimed.",
            ],
            "outputs": {"source": str(output_path)},
        }
        try:
            output_temp.write_text(source, encoding="utf-8", newline="")
            os.replace(output_temp, output_path)
            report_temp.write_text(
                json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8"
            )
            os.replace(report_temp, report_path)
        except OSError as exc:
            output_temp.unlink(missing_ok=True)
            report_temp.unlink(missing_ok=True)
            raise PipelineError(f"Could not write bytecode decompilation output: {exc}") from exc

        duration = time.monotonic() - started
        self.logger.info("Luau bytecode decompilation passed compile-only syntax verification")
        if formatting_applied:
            self.logger.info("Conservative whitespace formatting passed compile-only verification")
        self.logger.info("Decompiled Luau written to %s", output_path)
        self.logger.info("Bytecode decompilation report written to %s", report_path)
        self._progress(100, "DONE")
        return PipelineResult(
            output_path=output_path,
            report_path=report_path,
            route="local-luau-bytecode-decompiler",
            decoded_layers=0,
            transformations=transformations,
            sandbox_result=None,
            status="complete",
            notice=(
                "Bytecode was statically decompiled and not executed. Original comments and some names "
                "cannot be recovered from compiled bytecode."
            ),
        )

    def _write_moonsec_result(
        self,
        *,
        source: str,
        source_name: str,
        profile: ProtectionProfile,
        source_analysis: DeobfuscationResult,
        devirtualized: MoonSecV3Result | None,
        error: str | None,
        compiler: _LuauCompiler,
        started: float,
        deadline: float,
    ) -> PipelineResult:
        """Persist MoonSec output as source only after syntax validation; retain real partial artifacts."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        stem = f"moonsec_{timestamp}"
        preview_path = self.output_dir / f"{stem}.static-preview.luau"
        output_path = self.output_dir / f"{stem}.lua"
        candidate_path = self.output_dir / f"{stem}.candidate.lua"
        bytecode_path = self.output_dir / f"{stem}.lua51.luac"
        disassembly_path = self.output_dir / f"{stem}.disassembly.txt"
        report_path = self.output_dir / f"{stem}.report.json"

        source_candidate = devirtualized.source if devirtualized is not None else None
        source_valid = False
        if source_candidate is not None:
            remaining = deadline - time.monotonic()
            if remaining > 0:
                compiler.timeout_seconds = min(self.compiler_timeout_seconds, remaining)
                try:
                    compiler.verify_text(source_candidate, label="MoonSec V3 lifted source")
                    source_valid = True
                except PipelineError as exc:
                    error = f"Lua 5.1 decompiler output did not pass Luau syntax validation: {exc}"

        diagnostic_markers = tuple(
            sorted(
                {
                    "unluac_error_placeholder"
                    for token in tokenize(source_candidate or "")
                    if token.kind == "comment" and "[unluac error]" in token.text.lower()
                }
            )
        )
        remote_payload_loader_count = count_remote_payload_loaders(source_candidate or "")
        partial_reasons: list[str] = []
        if source_candidate is None:
            partial_reasons.append("lua51_source_not_lifted")
        elif not source_valid:
            partial_reasons.append("lua51_source_failed_luau_validation")
        if diagnostic_markers:
            partial_reasons.extend(diagnostic_markers)
        if remote_payload_loader_count:
            partial_reasons.append("remote_payload_loader_not_embedded")
        if devirtualized is None:
            partial_reasons.append("moonsec_v3_bytecode_not_recovered")
        elif devirtualized.error:
            partial_reasons.append("moonsec_v3_lifter_reported_error")

        source_recovered = source_valid and not partial_reasons

        artifacts: list[tuple[Path, bytes]] = []
        if source_recovered and source_candidate is not None:
            artifacts.append((output_path, source_candidate.encode("utf-8")))
            primary_path = output_path
        else:
            if source_candidate is not None:
                artifacts.append((candidate_path, source_candidate.encode("utf-8")))
            preview = (
                "-- Protez static preview only; this is not recovered source.\n"
                f"-- Detected: {profile.display_name}.\n"
                "-- Do not treat the obfuscated wrapper as devirtualized Luau.\n\n"
                + source_analysis.source
            )
            artifacts.append((preview_path, preview.encode("utf-8")))
            primary_path = preview_path
        if devirtualized is not None and devirtualized.bytecode is not None:
            artifacts.append((bytecode_path, devirtualized.bytecode))
        if devirtualized is not None and devirtualized.disassembly:
            artifacts.append((disassembly_path, devirtualized.disassembly.encode("utf-8")))

        status = "complete" if source_recovered else "partial"
        duration = time.monotonic() - started
        diagnostic_error = error or (devirtualized.error if devirtualized else None)
        report = {
            "app_version": VERSION,
            "status": status,
            "source_name": source_name,
            "route": "moonsec-v3-vm-lifter" if devirtualized else "moonsec-v3-analysis",
            "duration_seconds": round(duration, 3),
            "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "protection": {"family": profile.family, "version": profile.version},
            "family_specific_analysis": {
                "engine": devirtualized.devirtualizer_version if devirtualized else "MoonsecDeobfuscator V3 adapter",
                "decompiler": devirtualized.decompiler_version if devirtualized else "unluac-rs 1.4.4",
                "attempted": True,
                "lua51_bytecode_recovered": bool(devirtualized and devirtualized.bytecode),
                "source_recovered": source_recovered,
                "source_parsed_as_luau": source_valid,
                "source_recovery_complete": source_recovered,
                "unresolved_placeholder_count": len(diagnostic_markers),
                "remote_payload_loader_count": remote_payload_loader_count,
                "partial_reasons": partial_reasons,
                "semantic_equivalence_verified": False,
                "elapsed_seconds": round(devirtualized.elapsed_seconds, 3) if devirtualized else None,
                "lua51_bytecode_bytes": len(devirtualized.bytecode) if devirtualized and devirtualized.bytecode else None,
                "lua51_bytecode_sha256": hashlib.sha256(devirtualized.bytecode).hexdigest() if devirtualized and devirtualized.bytecode else None,
                "source_bytes": len(source_candidate.encode("utf-8")) if source_candidate is not None else None,
                "error": diagnostic_error,
            },
            "bytecode_executed": False,
            "input_transformations": list(source_analysis.transformations),
            "outputs": {
                "source": str(output_path) if source_recovered else None,
                "partial_source_candidate": str(candidate_path) if source_candidate is not None and not source_recovered else None,
                "static_preview": str(preview_path) if not source_recovered else None,
                "lua51_bytecode": str(bytecode_path) if devirtualized and devirtualized.bytecode else None,
                "disassembly": str(disassembly_path) if devirtualized and devirtualized.disassembly else None,
                "report": str(report_path),
            },
            "limitations": [
                "Support is limited to MoonSec V3 wrappers matching the vendored handler and serializer patterns.",
                "Recovered Lua source is approximate; original comments, local names, and exact formatting are unavailable.",
                "Luau syntax validation does not prove semantic equivalence to the protected program.",
                "The wrapper and recovered bytecode are parsed statically and are not executed by this route.",
            ],
        }
        artifacts.append((report_path, (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")))
        temporaries: list[Path] = []
        try:
            for path, payload in artifacts:
                tmp = path.with_name(path.name + ".tmp")
                tmp.write_bytes(payload)
                os.replace(tmp, path)
                temporaries.append(tmp)
        except OSError as exc:
            for path in (preview_path, output_path, candidate_path, bytecode_path, disassembly_path, report_path):
                path.unlink(missing_ok=True)
            raise PipelineError(f"Could not write MoonSec analysis output: {exc}") from exc
        notice = (
            "MoonSec V3 bytecode was lifted to readable Lua and passed Luau syntax validation; "
            "semantic equivalence is not verified."
            if source_recovered
            else "MoonSec V3 analysis is partial: "
            + ", ".join(partial_reasons)
            + (f". {diagnostic_error}" if diagnostic_error else ".")
        )
        self.logger.info("MoonSec analysis report written to %s", report_path)
        self._progress(100, "DONE" if source_recovered else "PARTIAL")
        return PipelineResult(
            output_path=primary_path,
            report_path=report_path,
            route=str(report["route"]),
            decoded_layers=0,
            transformations=("MoonSec V3 VM to Lua 5.1 bytecode", "Lua 5.1 bytecode source lifting") if source_recovered else (),
            sandbox_result=None,
            status=status,
            notice=notice,
            preview_path=preview_path if not source_recovered else None,
        )

    def _format_verified_candidate(
        self,
        source: str,
        compiler: _LuauCompiler,
        *,
        label: str,
        deadline: float,
    ) -> tuple[str, bool]:
        """Format only syntax-checked source, retaining the original on any failure."""
        try:
            formatted = format_luau(source)
        except Exception as exc:
            self.logger.warning("Could not prepare conservative formatting; preserving original: %s", exc)
            return source, False
        if formatted == source:
            return source, False

        remaining = deadline - time.monotonic()
        if remaining <= 0:
            self.logger.warning("Skipped optional formatting after reaching the pipeline time limit")
            return source, False
        compiler.timeout_seconds = min(compiler.timeout_seconds, max(0.001, remaining))
        try:
            compiler.verify_text(formatted, label=label)
        except PipelineError as exc:
            self.logger.warning("Formatted candidate did not pass compile-only validation; preserving original: %s", exc)
            return source, False

        self.logger.info("Conservative token-preserving formatting passed compile-only validation")
        return formatted, True

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

    def _best_luraph_runtime_payload(
        self,
        devirtualized: LuraphDevirtualizationResult,
        *,
        compiler: _LuauCompiler,
        deadline: float,
    ) -> tuple[str | None, dict[str, object] | None]:
        """Find a substantial, syntax-valid loadstring body captured by the isolated Luraph run."""
        minimum_bytes = max(512, len(devirtualized.source.encode("utf-8")) * 2)
        candidates: list[tuple[int, int, int, str, dict[str, object]]] = []
        inspected = 0
        for run_index, run in enumerate(devirtualized.run_results, start=1):
            paths = run.captured_paths or ((run.captured_path,) if run.captured_path else ())
            for capture_index, capture in enumerate(run.captures, start=1):
                if capture.kind.lower() not in {"loadstring", "load"}:
                    continue
                if inspected >= MAX_PAYLOAD_CANDIDATES or time.monotonic() >= deadline:
                    break
                if capture_index > len(paths) or paths[capture_index - 1] is None:
                    continue
                path = paths[capture_index - 1]
                inspected += 1
                try:
                    if path.stat().st_size > MAX_DYNAMIC_CAPTURE_ARTIFACT_BYTES:
                        continue
                    captured = path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError):
                    continue
                try:
                    decoded = deobfuscate_source(captured)
                except Exception as exc:
                    self.logger.info("Skipped captured Luraph payload %s.%s during static decoding: %s", run_index, capture.index, str(exc)[:400])
                    continue
                candidate = decoded.source
                candidate_bytes = candidate.encode("utf-8")
                if len(candidate_bytes) < minimum_bytes or inspect_protection(candidate) is not None:
                    continue
                if count_remote_payload_loaders(candidate):
                    continue
                remaining = deadline - time.monotonic()
                if remaining <= 0:
                    return None, None
                compiler.timeout_seconds = min(self.compiler_timeout_seconds, remaining)
                try:
                    compiler.verify_text(candidate, label=f"captured Luraph payload {run_index}.{capture.index}")
                except PipelineError as exc:
                    self.logger.info("Skipped captured Luraph payload %s.%s: %s", run_index, capture.index, str(exc)[:400])
                    continue
                metadata: dict[str, object] = {
                    "run": run_index,
                    "index": capture.index,
                    "kind": capture.kind,
                    "source_bytes": len(candidate_bytes),
                    "source_sha256": hashlib.sha256(candidate_bytes).hexdigest(),
                    "static_transformations": list(decoded.transformations),
                }
                candidates.append((len(candidate_bytes), run_index, capture.index, candidate, metadata))
        if not candidates:
            return None, None
        _size, _run, _capture, source, metadata = max(candidates, key=lambda item: item[:3])
        metadata["valid_candidate_count"] = len(candidates)
        return source, metadata

    @staticmethod
    def _sandbox_outcome(result: SandboxResult | None) -> str:
        if result is None:
            return "not-started"
        if result.timed_out:
            return "timed-out"
        if result.output_limited:
            return "output-limit"
        if result.returncode == 0:
            return "completed"
        if result.returncode == 1:
            return "runtime-error"
        if result.returncode == 65:
            return "compile-error"
        if result.returncode == 66:
            return "source-read-error"
        if result.returncode in {70, 71}:
            return "host-error"
        return f"worker-error-{result.returncode}"

    @staticmethod
    def _capture_report_entries(
        result: SandboxResult | None,
    ) -> list[dict[str, object]]:
        if result is None:
            return []
        paths = result.captured_paths or ((result.captured_path,) if result.captured_path else ())
        entries: list[dict[str, object]] = []
        for index, capture in enumerate(result.captures):
            path = paths[index] if index < len(paths) else None
            entry: dict[str, object] = {
                "index": capture.index,
                "kind": capture.kind,
                "size_bytes": capture.size_bytes,
            }
            if path is not None and path.is_file():
                entry["path"] = str(path)
                try:
                    digest = hashlib.sha256()
                    with path.open("rb") as stream:
                        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
                            digest.update(chunk)
                    entry["sha256"] = digest.hexdigest()
                except OSError:
                    pass
            entries.append(entry)
        return entries

    @classmethod
    def _dynamic_run_report(cls, result: TraceResult) -> dict[str, object]:
        sandbox_result = result.sandbox_result
        return {
            "source_name": result.source_name,
            "execution_outcome": cls._sandbox_outcome(sandbox_result),
            "isolation_backend": sandbox_result.isolation_backend,
            "trace_files": [str(path) for path in result.trace_files],
            "trace_event_count": result.event_count,
            "native_instruction_tracing": result.native_hooks_available,
            "captured_chunks": cls._capture_report_entries(sandbox_result),
        }

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

    def _trace_source(
        self,
        sandbox: Sandbox,
        source: str,
        *,
        source_name: str,
        label: str,
        timeout_seconds: float,
    ) -> TraceResult:
        trace_path = LOGS_DIR / (
            f"trace_{label}_{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}_"
            f"{secrets.token_hex(4)}.jsonl"
        )
        tracer = Tracer(
            logger=self.logger,
            progress_callback=self.progress_callback,
            tools_dir=self.tools_dir,
            timeout_seconds=timeout_seconds,
            trace_path=trace_path,
            sandbox=sandbox,
        )
        try:
            return tracer.trace(source, source_name=source_name)
        except Exception as exc:
            partial_paths = [trace_path, *trace_path.parent.glob(f"{trace_path.stem}.*{trace_path.suffix}")]
            existing = []
            for path in partial_paths:
                try:
                    if path.is_file() and path.stat().st_size:
                        existing.append(path)
                    else:
                        path.unlink(missing_ok=True)
                except OSError:
                    continue
            if existing:
                detail = ", ".join(str(path) for path in existing)
                raise TraceError(f"{exc}; partial trace was saved to {detail}") from exc
            raise

    def _trace_unresolved(
        self,
        source: str,
        source_name: str,
        layer_report: list[dict[str, object]],
        *,
        trace_results: list[TraceResult],
        trace_error: str | None,
        dynamic_attempted: bool,
    ) -> PipelineResult:
        self.logger.warning("No valid source layer was recovered after bounded dynamic analysis")
        self._progress(82, "TRACE")
        trace_files = tuple(path for result in trace_results for path in result.trace_files)
        report_path = self._write_failure_report(
            source,
            source_name,
            layer_report,
            trace_results=trace_results,
            trace_error=trace_error,
            dynamic_attempted=dynamic_attempted,
        )
        detail = (
            "VM instruction traces were saved, but VM lifting and source reconstruction are not implemented."
            if trace_results and any(result.native_hooks_available for result in trace_results)
            else f"Dynamic analysis did not recover valid source. {trace_error or 'No VM instruction trace was produced.'}"
        )
        trace_summary = f" Trace: {trace_files[0]}." if trace_files else ""
        raise PipelineError(
            f"No valid Luau source was recovered.{trace_summary} Report: {report_path}. {detail}"
        )

    def _write_luraph_devirtualized_result(
        self,
        *,
        source: str,
        source_name: str,
        profile: ProtectionProfile,
        source_analysis: DeobfuscationResult,
        devirtualized: LuraphDevirtualizationResult,
        compiler: _LuauCompiler,
        started: float,
        deadline: float,
    ) -> PipelineResult:
        captured_source, captured_source_info = self._best_luraph_runtime_payload(
            devirtualized,
            compiler=compiler,
            deadline=deadline,
        )
        source_candidate = captured_source or devirtualized.source
        source_origin = "runtime-loadstring-capture" if captured_source is not None else "vm-lifter"
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise LuraphDevirtualizationError(
                "the pipeline time limit was reached before validating the lifted source"
            )
        compiler.timeout_seconds = min(self.compiler_timeout_seconds, remaining)
        try:
            compiler.verify_text(source_candidate, label=f"Luraph v15 {source_origin} source")
        except PipelineError as exc:
            raise LuraphDevirtualizationError(
                f"the Luraph v15 {source_origin} output failed Luau syntax validation: {exc}"
            ) from exc

        formatted_source, formatting_applied = self._format_verified_candidate(
            source_candidate,
            compiler,
            label=f"formatted Luraph v15 {source_origin} source",
            deadline=deadline,
        )
        output_partial_reasons = list(devirtualized.incomplete_reasons)
        if captured_source is not None:
            output_partial_reasons = [
                reason for reason in output_partial_reasons
                if "remotely fetched Lua payloads are not embedded" not in reason
            ]
            if int((captured_source_info or {}).get("valid_candidate_count", 0)) > 1:
                output_partial_reasons.append("multiple captured Lua payloads were not merged")
        recovery_complete = not output_partial_reasons
        status = "complete" if recovery_complete else "partial"
        elapsed = time.monotonic() - started
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        source_name_suffix = "" if recovery_complete else ".candidate"
        output_path = self.output_dir / f"devirtualized_{timestamp}{source_name_suffix}.luau"
        report_path = self.output_dir / f"devirtualized_{timestamp}.report.json"
        trace_path = (
            self.output_dir / f"devirtualized_{timestamp}.behavior-trace.luau"
            if devirtualized.trace_source
            else None
        )
        last_run = devirtualized.run_results[-1] if devirtualized.run_results else None
        dynamic_runs = [
            {
                "run": index,
                "execution_outcome": self._sandbox_outcome(run),
                "duration_seconds": round(run.duration_seconds, 3),
                "output_bytes": run.output_bytes,
                "captures": self._capture_report_entries(run),
                "isolation_backend": run.isolation_backend,
                "run_log": str(run.run_log_path),
            }
            for index, run in enumerate(devirtualized.run_results, start=1)
        ]
        capture_artifacts: list[dict[str, object]] = []
        capture_writes: list[tuple[Path, bytes]] = []
        for run_index, run in enumerate(devirtualized.run_results, start=1):
            paths = run.captured_paths or ((run.captured_path,) if run.captured_path else ())
            for capture_index, capture in enumerate(run.captures, start=1):
                path = paths[capture_index - 1] if capture_index <= len(paths) else None
                entry: dict[str, object] = {
                    "run": run_index,
                    "index": capture.index,
                    "kind": capture.kind,
                    "size_bytes": capture.size_bytes,
                }
                if (
                    captured_source_info is not None
                    and captured_source_info.get("run") == run_index
                    and captured_source_info.get("index") == capture.index
                ):
                    entry["selected_as_recovered_source"] = True
                if path is not None and path.is_file():
                    try:
                        if path.stat().st_size > MAX_DYNAMIC_CAPTURE_ARTIFACT_BYTES:
                            entry["omitted_reason"] = "capture exceeds Protez's 16 MiB artifact limit"
                            capture_artifacts.append(entry)
                            continue
                        payload = path.read_bytes()
                        suffix = ".luau"
                        try:
                            payload.decode("utf-8")
                        except UnicodeDecodeError:
                            suffix = ".bin"
                        output_capture_path = self.output_dir / (
                            f"devirtualized_{timestamp}.runtime-{run_index:02d}-{capture_index:02d}{suffix}"
                        )
                        entry["output"] = str(output_capture_path)
                        entry["sha256"] = hashlib.sha256(payload).hexdigest()
                        capture_artifacts.append(entry)
                        capture_writes.append((output_capture_path, payload))
                    except OSError as exc:
                        entry["error"] = str(exc)
                        capture_artifacts.append(entry)
                else:
                    capture_artifacts.append(entry)
        if captured_source_info is not None:
            selected_capture_artifact = next(
                (
                    entry.get("output")
                    for entry in capture_artifacts
                    if entry.get("selected_as_recovered_source") is True
                ),
                None,
            )
            captured_source_info["artifact"] = selected_capture_artifact
        transformations = (
            "Luraph v15 VM proto/opcode lifting",
            "offline Roblox API model used during constant recovery",
        ) + (("sandbox-captured loadstring payload",) if captured_source is not None else ()) + (
            "Luau compile-only syntax verification",
        ) + (("compile-verified whitespace formatting",) if formatting_applied else ())
        report = {
            "app_version": VERSION,
            "status": status,
            "source_name": source_name,
            "route": devirtualized.route + ("+captured-loadstring" if captured_source is not None else ""),
            "duration_seconds": round(elapsed, 3),
            "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "output_sha256": hashlib.sha256(formatted_source.encode("utf-8")).hexdigest(),
            "protection": {
                "family": profile.family,
                "version": profile.version,
                "container_layout": profile.container_layout,
                "raw_payload_streams": profile.raw_payload_streams,
                "valid_payload_streams": profile.valid_payload_streams,
            },
            "source_reconstructed": devirtualized.lift_stats.get("functions", 0) > 0,
            "original_source_recovered": False,
            "semantic_equivalence_verified": False,
            "family_specific_analysis": {
                "engine": "MIT-licensed Luraph v15 devirtualizer",
                "provenance": "imnotherfav/deobfuscator-luraph-v15",
                "source_commit": "5a1ac583b69451f56dd735d2a1de6ab7a513432b",
                "source_bytes": devirtualized.source_bytes,
                "recovered_source_bytes": len(formatted_source.encode("utf-8")),
                "source_origin": source_origin,
                "runtime_capture_recovery": captured_source_info,
                "elapsed_seconds": round(devirtualized.elapsed_seconds, 3),
                "vm_prototypes_lifted": devirtualized.lift_stats.get("functions", 0) > 0,
                "lift_stats": devirtualized.lift_stats,
                "unresolved_lazy_constant_count": devirtualized.unresolved_constant_count,
                "unresolved_lazy_constant_samples": list(devirtualized.unresolved_constant_samples),
                "constant_misses": devirtualized.constant_misses,
                "unresolved_runtime_functions": list(devirtualized.unresolved_runtime_functions),
                "placeholder_counts": devirtualized.placeholder_counts,
                "remote_payload_loader_count": count_remote_payload_loaders(source_candidate),
                "partial_reasons": output_partial_reasons,
                "vm_lift_partial_reasons": list(devirtualized.incomplete_reasons),
                "readability_status": status,
                "version_scope": "Luraph v15 wrappers matching the supported VM structure",
            },
            "formatting_applied": formatting_applied,
            "formatting_validation": "compile-only" if formatting_applied else None,
            "selected_transformations": list(transformations),
            "dynamic_analysis": {
                "attempted": bool(devirtualized.run_results),
                "execution_outcome": self._sandbox_outcome(last_run),
                "runs": dynamic_runs,
                "isolation_backend": last_run.isolation_backend if last_run else None,
                "trace_event_count": 0,
                "native_instruction_tracing": False,
                "error": None,
            },
            "outputs": {
                "source": str(output_path) if recovery_complete else None,
                "partial_source_candidate": str(output_path) if not recovery_complete else None,
                "runtime_captured_source": str(output_path) if captured_source is not None else None,
                "behavior_trace": str(trace_path) if trace_path else None,
                "runtime_capture_payloads": capture_artifacts,
                "report": str(report_path),
            },
            "known_losses": [
                "Comments and original local names are not recoverable from the VM representation.",
                "Some control-flow edges and API values may remain approximate when the wrapper structure is unsupported.",
                "Syntax validation does not prove semantic equivalence to the protected program.",
            ] + (list(output_partial_reasons) if not recovery_complete else []) + (
                ["Runtime loadstring capture was not independently executed or checked for semantic equivalence."]
                if captured_source is not None
                else []
            ),
        }
        if recovery_complete:
            notice = (
                "Luraph v15 source was recovered from an isolated loadstring capture and passed a compile-only syntax check. "
                "Original comments/names and semantic equivalence are not recovered or verified."
                if captured_source is not None
                else "Luraph v15 VM code was lifted into readable Luau and passed a compile-only syntax check. "
                "Original comments/names and semantic equivalence are not recovered or verified."
            )
        else:
            reasons = "; ".join(output_partial_reasons)
            notice = (
                "Luraph v15 produced a partial Luau candidate. It is syntax-valid, but the report lists "
                f"unresolved source content: {reasons}. Protez did not mark it as fully recovered source."
            )
        writes: list[tuple[Path, bytes]] = [
            (output_path, formatted_source.encode("utf-8")),
            (report_path, (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8")),
        ] + capture_writes
        if trace_path and devirtualized.trace_source is not None:
            writes.append((trace_path, devirtualized.trace_source.encode("utf-8")))
        temporary_paths = [path.with_name(path.name + ".tmp") for path, _ in writes]
        try:
            for (path, payload), temporary_path in zip(writes, temporary_paths):
                temporary_path.write_bytes(payload)
                os.replace(temporary_path, path)
        except OSError as exc:
            for temporary_path in temporary_paths:
                temporary_path.unlink(missing_ok=True)
            for path, _ in writes:
                path.unlink(missing_ok=True)
            raise PipelineError(f"Could not write Luraph v15 output: {exc}") from exc

        self.logger.info("Luraph v15 VM source written to %s", output_path)
        self.logger.info("Luraph v15 analysis report written to %s", report_path)
        self._progress(100, "DONE" if recovery_complete else "PARTIAL")
        return PipelineResult(
            output_path=output_path,
            report_path=report_path,
            route=str(report["route"]),
            decoded_layers=0,
            transformations=transformations,
            sandbox_result=last_run,
            status=status,
            notice=notice,
            preview_path=output_path if not recovery_complete else None,
            trace_files=(trace_path,) if trace_path else (),
            trace_event_count=0,
        )

    def _write_protection_analysis(
        self,
        *,
        source: str,
        source_name: str,
        profile: ProtectionProfile,
        source_analysis: DeobfuscationResult,
        duration_seconds: float,
        notice: str,
        deadline: float,
        family_lifter_error: str | None = None,
    ) -> PipelineResult:
        """Write static triage, bounded container artifacts, and isolated runtime evidence."""
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        preview_path = self.output_dir / f"analysis_{timestamp}.static-preview.luau"
        report_path = self.output_dir / f"analysis_{timestamp}.report.json"
        summary_path = self.output_dir / f"analysis_{timestamp}.report.txt"

        unpack_started = time.monotonic()
        unpack_result: LuraphStaticUnpackResult | None = None
        unpack_error: str | None = None
        try:
            unpack_result = unpack_luraph_static(source)
        except LuraphStaticError as exc:
            unpack_error = str(exc)
        except Exception as exc:
            self.logger.exception("Unexpected error during static Luraph container extraction")
            unpack_error = f"unexpected static unpack error: {type(exc).__name__}: {exc}"

        sandbox = Sandbox(
            tools_dir=self.tools_dir,
            timeout_seconds=self.sandbox_timeout_seconds,
            logger=self.logger,
        )
        dynamic_trace: TraceResult | None = None
        dynamic_error: str | None = None
        remaining = deadline - time.monotonic()
        if remaining > 0:
            self._progress(28, "SANDBOX")
            sandbox.timeout_seconds = min(self.sandbox_timeout_seconds, remaining)
            try:
                dynamic_trace = self._trace_source(
                    sandbox,
                    source,
                    source_name=source_name,
                    label="luraph",
                    timeout_seconds=min(self.sandbox_timeout_seconds, remaining),
                )
            except (SandboxError, TraceError) as exc:
                dynamic_error = str(exc)
                self.logger.warning("Isolated Luraph runtime analysis could not start: %s", exc)
            except Exception as exc:
                dynamic_error = f"unexpected {type(exc).__name__}: {exc}"
                self.logger.exception("Unexpected isolated Luraph runtime-analysis error")
        else:
            dynamic_error = "the total runtime limit was reached before dynamic analysis started"
        dynamic_result = dynamic_trace.sandbox_result if dynamic_trace is not None else None
        if dynamic_result is not None:
            self._log_sandbox_status(dynamic_result, "Luraph wrapper")
        elapsed_seconds = duration_seconds + (time.monotonic() - unpack_started)
        trace_files = dynamic_trace.trace_files if dynamic_trace is not None else ()
        dynamic_runs = [self._dynamic_run_report(dynamic_trace)] if dynamic_trace is not None else []
        captured_chunks = dynamic_runs[0]["captured_chunks"] if dynamic_runs else []
        dynamic_outcome = self._sandbox_outcome(dynamic_result)
        dynamic_analysis: dict[str, object] = {
            "attempted": remaining > 0,
            "worker_started": dynamic_result is not None,
            "execution_outcome": dynamic_outcome,
            "runs": dynamic_runs,
            "isolation_backend": (
                dynamic_result.isolation_backend if dynamic_result is not None else None
            ),
            "trace_files": [str(path) for path in trace_files],
            "trace_event_count": dynamic_trace.event_count if dynamic_trace is not None else 0,
            "native_instruction_tracing": (
                dynamic_trace.native_hooks_available if dynamic_trace is not None else False
            ),
            "captured_chunks": captured_chunks,
            "error": dynamic_error,
        }
        vm_source_path: Path | None = None
        bytecode_path: Path | None = None
        vm_source_details: dict[str, object] | None = None
        bytecode_details: dict[str, object] | None = None

        if unpack_result is not None:
            if unpack_result.vm_source is not None:
                vm_source_path = self.output_dir / (
                    f"analysis_{timestamp}.luraph-vm-interpreter.luau"
                )
                vm_source_details = {
                    "path": str(vm_source_path),
                    "bytes": len(unpack_result.vm_source),
                    "sha256": hashlib.sha256(unpack_result.vm_source).hexdigest(),
                }
            bytecode_path = self.output_dir / f"analysis_{timestamp}.luraph-custom-bytecode.bin"
            bytecode_details = {
                "path": str(bytecode_path),
                "bytes": len(unpack_result.custom_bytecode),
                "sha256": hashlib.sha256(unpack_result.custom_bytecode).hexdigest(),
            }
            self.logger.info(
                "Statically unpacked Luraph %s container",
                unpack_result.layout,
            )
            if vm_source_details is not None:
                self.logger.info("Luraph VM-interpreter artifact written to %s", vm_source_path)
            self.logger.info("Luraph custom-bytecode artifact written to %s", bytecode_path)
            notice = (
                f"{profile.display_name} container streams were statically unpacked "
                f"({unpack_result.layout}); isolated execution/tracing outcome: "
                f"{dynamic_outcome}. Original source was not reconstructed."
            )
        else:
            unpack_error = unpack_error or "no supported Luraph container layout was found"
            self.logger.warning(
                "Luraph static stream extraction did not complete: %s",
                unpack_error,
            )
            notice = (
                f"{profile.display_name} detected; Protez produced a static wrapper preview only. "
                f"Stream extraction did not complete: {unpack_error}. Isolated execution/tracing "
                f"outcome: {dynamic_outcome}."
            )

        preview = (
            "-- Protez static preview only; this is not reconstructed source.\n"
            f"-- Detected: {profile.display_name}. Runtime outcome: {dynamic_outcome}.\n"
            "-- Do not treat this file as deobfuscated Luau.\n\n"
            + source_analysis.source
        )
        static_unpack_report: dict[str, object] = {
            "attempted": True,
            "success": unpack_result is not None,
            "container_layout": (
                unpack_result.layout if unpack_result is not None else profile.container_layout
            ),
            "source_reconstructed": False,
            "custom_vm_devirtualized": False,
            "compressed_stream_bytes": (
                list(unpack_result.compressed_stream_sizes) if unpack_result is not None else []
            ),
            "decoded_stream_bytes": (
                list(unpack_result.decoded_stream_sizes) if unpack_result is not None else []
            ),
            "vm_interpreter": vm_source_details,
            "custom_bytecode": bytecode_details,
            "error": None if unpack_result is not None else unpack_error,
        }
        execution_note = (
            "The wrapper was submitted to the isolated Luau worker without Roblox Engine APIs. "
            "A runtime error or timeout can stop it before a payload is reached."
            if dynamic_result is not None
            else "The wrapper did not run because isolated dynamic analysis could not start: "
            + (dynamic_error or "no worker result was produced.")
        )
        if family_lifter_error:
            family_lifter_limitation = (
                "Luraph v15 family-specific lifting was attempted but did not recover source: "
                + family_lifter_error
            )
        elif profile.version and profile.version.split(".", maxsplit=1)[0] == "15":
            family_lifter_limitation = "Luraph v15 VM source was not recovered by the family-specific lifter."
        else:
            family_lifter_limitation = (
                "This Protez release has a family-specific source lifter for Luraph v15 only; "
                "other Luraph versions receive static and isolated runtime analysis."
            )
        limitations = [
            (
                "The readable Luraph wrapper is not the original program; container decoding "
                "does not recover source-level control flow."
            ),
            (
                "The extracted custom VM bytecode is not standard Luau bytecode and is not "
                "passed to the ordinary Luau bytecode decompiler."
            ),
            family_lifter_limitation,
            execution_note,
            (
                "The Luau VM trace describes wrapper/interpreter instructions. It does not identify or "
                "lift the semantics of Luraph's custom bytecode."
            ),
        ]
        if unpack_result is None:
            limitations.insert(
                0,
                "Static Luraph stream extraction was attempted but did not complete: "
                + (unpack_error or "unknown error"),
            )
        report = {
            "app_version": VERSION,
            "status": "partial",
            "source_name": source_name,
            "route": "static-protection-report",
            "duration_seconds": round(elapsed_seconds, 3),
            "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "protection": {
                "family": profile.family,
                "version": profile.version,
                "embedded_payload_characters": profile.embedded_payload_chars,
                "raw_payload_streams": profile.raw_payload_streams,
                "valid_payload_streams": profile.valid_payload_streams,
                "container_layout": profile.container_layout,
            },
            "recovered": False,
            "source_reconstructed": False,
            "dynamic_analysis": dynamic_analysis,
            "wrapper_execution_outcome": dynamic_outcome,
            "input_transformations": list(source_analysis.transformations),
            "visible_wrapper_literals": list(profile.visible_literals),
            "static_unpack": static_unpack_report,
            "family_specific_analysis": {
                "engine": "luraph-v15-vm-lifter",
                "attempted": family_lifter_error is not None or (
                    profile.version is not None
                    and profile.version.split(".", maxsplit=1)[0] == "15"
                ),
                "source_recovered": False,
                "error": family_lifter_error,
            },
            "outputs": {
                "human_report": str(summary_path),
                "machine_report": str(report_path),
                "static_preview": str(preview_path),
                "luraph_vm_interpreter": str(vm_source_path) if vm_source_path else None,
                "luraph_custom_bytecode": str(bytecode_path) if bytecode_path else None,
                "trace_files": [str(path) for path in trace_files],
                "captured_chunks": [
                    item["path"] for item in captured_chunks if "path" in item
                ],
            },
            "limitations": limitations,
        }
        transformations = (
            "\n".join(f"  - {item}" for item in source_analysis.transformations)
            if source_analysis.transformations
            else "  - No supported static decoder pattern matched."
        )
        literals = (
            "\n".join(
                f"  - {json.dumps(item, ensure_ascii=False)}"
                for item in profile.visible_literals
            )
            if profile.visible_literals
            else "  - No short, readable wrapper literals were found."
        )
        payload_size = (
            f"approximately {profile.embedded_payload_chars:,} characters"
            if profile.embedded_payload_chars
            else "not identified by the static signature check"
        )
        if unpack_result is not None:
            unpack_lines = [
                f"  - Static container extraction: SUCCEEDED ({unpack_result.layout})",
            ]
            if vm_source_details is not None:
                unpack_lines.append(
                    "  - VM interpreter (intermediate, not original source): "
                    f"{vm_source_path} ({vm_source_details['bytes']:,} bytes, "
                    f"SHA-256 {vm_source_details['sha256']})"
                )
            else:
                unpack_lines.append(
                    "  - Separate VM-interpreter stream: "
                    "not present in this container layout"
                )
            unpack_lines.append(
                "  - Custom VM bytecode (not Luau bytecode): "
                f"{bytecode_path} ({bytecode_details['bytes']:,} bytes, "
                f"SHA-256 {bytecode_details['sha256']})"
            )
        else:
            unpack_lines = [
                "  - Static container extraction: NOT COMPLETED",
                f"  - Detail: {unpack_error}",
            ]
        captured_lines = []
        for item in captured_chunks:
            entry = f"  - {item['kind']}: {item['size_bytes']:,} bytes"
            if item.get("sha256"):
                entry += f", SHA-256 {item['sha256']}"
            if item.get("path"):
                entry += f" — {item['path']}"
            captured_lines.append(entry)
        summary = (
            "PROTEZ // STATIC PROTECTION ANALYSIS\n"
            "=====================================\n"
            "STATUS: PARTIAL — ORIGINAL SOURCE NOT RECONSTRUCTED\n\n"
            f"Protection: {profile.display_name}\n"
            f"Container layout: {profile.container_layout or 'not classified'}\n"
            f"Embedded payload: {payload_size}\n"
            f"Input: {source_name} ({source_analysis.input_bytes:,} bytes)\n"
            f"Elapsed: {elapsed_seconds:.2f} seconds\n"
            f"Isolated wrapper execution: {dynamic_outcome}\n"
            f"Luau VM trace events: {dynamic_analysis['trace_event_count']}\n"
            + (f"Trace file: {trace_files[0]}\n" if trace_files else "")
            + (f"Runtime-analysis detail: {dynamic_error}\n" if dynamic_error else "")
            + (
                "Captured loadstring/load chunks:\n"
                + "\n".join(captured_lines)
                + "\n"
                if captured_lines
                else ""
            )
            + "\nStatic Luraph extraction:\n"
            f"{chr(10).join(unpack_lines)}\n\n"
            "Static wrapper transforms:\n"
            f"{transformations}\n\n"
            "Visible wrapper strings (not necessarily program behavior):\n"
            f"{literals}\n\n"
            "What this result means:\n"
            "The Luraph container may now be unpacked into its VM-interpreter stream "
            "and/or custom virtual bytecode. "
            "The wrapper was also attempted in an isolated Luau worker; see the runtime outcome below. "
            "This is an intermediate analysis result, not the unobfuscated "
            "program. This report was written because the v15 source lifter did not "
            "complete or this version is outside its supported family.\n\n"
            "Safety:\n"
            f"{execution_note} The worker has no network access. Treat "
            "intermediate artifacts as "
            "untrusted code/data and review them before sharing.\n\n"
            "Files:\n"
            f"  Human report: {summary_path}\n"
            f"  Machine report: {report_path}\n"
            f"  Static preview: {preview_path}\n"
            + (f"  VM interpreter: {vm_source_path}\n" if vm_source_path else "")
            + (f"  Custom VM bytecode: {bytecode_path}\n" if bytecode_path else "")
        )

        writes: list[tuple[Path, bytes]] = [
            (preview_path, preview.encode("utf-8")),
            (
                report_path,
                (json.dumps(report, indent=2, ensure_ascii=False) + "\n").encode("utf-8"),
            ),
            (summary_path, summary.encode("utf-8")),
        ]
        if unpack_result is not None:
            if vm_source_path is not None and unpack_result.vm_source is not None:
                writes.append((vm_source_path, unpack_result.vm_source))
            if bytecode_path is not None:
                writes.append((bytecode_path, unpack_result.custom_bytecode))
        temporary_paths = [path.with_name(path.name + ".tmp") for path, _ in writes]
        try:
            for (path, payload), temporary_path in zip(writes, temporary_paths):
                temporary_path.write_bytes(payload)
                os.replace(temporary_path, path)
        except OSError as exc:
            for temporary_path in temporary_paths:
                temporary_path.unlink(missing_ok=True)
            for path, _ in writes:
                path.unlink(missing_ok=True)
            raise PipelineError(f"Could not write static protection analysis: {exc}") from exc

        self.logger.info("Static analysis report written to %s", summary_path)
        self.logger.info("Machine-readable report written to %s", report_path)
        self.logger.info("Static preview written to %s", preview_path)
        self._progress(100, "PARTIAL")
        return PipelineResult(
            output_path=summary_path,
            report_path=report_path,
            route="static-protection-report",
            decoded_layers=0,
            transformations=source_analysis.transformations,
            sandbox_result=dynamic_result,
            status="partial",
            notice=notice,
            preview_path=preview_path,
            trace_files=tuple(trace_files),
            trace_event_count=dynamic_trace.event_count if dynamic_trace is not None else 0,
        )

    def _write_result(
        self,
        *,
        source: str,
        formatting_applied: bool,
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
        trace_results: list[TraceResult],
        trace_error: str | None,
        dynamic_attempted: bool,
    ) -> PipelineResult:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        output_path = self.output_dir / f"deobfuscated_{timestamp}.luau"
        report_path = self.output_dir / f"deobfuscated_{timestamp}.report.json"
        output_temp = output_path.with_name(output_path.name + ".tmp")
        report_temp = report_path.with_name(report_path.name + ".tmp")
        trace_files = tuple(path for result in trace_results for path in result.trace_files)
        trace_event_count = sum(result.event_count for result in trace_results)
        dynamic_runs = [self._dynamic_run_report(result) for result in trace_results]
        captured_chunks = [
            item for run in dynamic_runs for item in run["captured_chunks"]
        ]
        dynamic_analysis = {
            "attempted": dynamic_attempted,
            "execution_outcome": self._sandbox_outcome(sandbox_result),
            "runs": dynamic_runs,
            "isolation_backend": (
                sandbox_result.isolation_backend if sandbox_result is not None else None
            ),
            "trace_files": [str(path) for path in trace_files],
            "trace_event_count": trace_event_count,
            "native_instruction_tracing": any(
                result.native_hooks_available for result in trace_results
            ),
            "captured_chunks": captured_chunks,
            "error": trace_error,
        }
        safety_notes = [
            "Dynamic runs use an OS sandbox with no network access and bounded process and VM memory.",
            "Roblox Engine APIs are not fabricated; scripts that require them stop at the first missing API.",
            "Filesystem, process, and remote module loading functions are unavailable inside the Luau worker.",
            "A syntactically valid output is not a guarantee of full deobfuscation.",
        ]
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
            "formatting_applied": formatting_applied,
            "formatting_validation": "compile-only" if formatting_applied else None,
            "layers": layer_report,
            "dynamic_analysis": dynamic_analysis,
            "safety_notes": safety_notes,
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
        if formatting_applied:
            self.logger.info("Whitespace formatting was compile-only verified")
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
            trace_files=trace_files,
            trace_event_count=trace_event_count,
        )

    def _write_failure_report(
        self,
        source: str,
        source_name: str,
        layer_report: list[dict[str, object]],
        *,
        trace_results: list[TraceResult],
        trace_error: str | None,
        dynamic_attempted: bool,
    ) -> Path:
        self.output_dir.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        report_path = self.output_dir / f"analysis_{timestamp}.report.json"
        trace_files = tuple(path for result in trace_results for path in result.trace_files)
        sandbox_result = trace_results[0].sandbox_result if trace_results else None
        dynamic_runs = [self._dynamic_run_report(result) for result in trace_results]
        report = {
            "app_version": VERSION,
            "source_name": source_name,
            "input_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
            "recovered": False,
            "dynamic_analysis": {
                "attempted": dynamic_attempted,
                "execution_outcome": self._sandbox_outcome(sandbox_result),
                "runs": dynamic_runs,
                "isolation_backend": (
                    sandbox_result.isolation_backend if sandbox_result is not None else None
                ),
                "trace_files": [str(path) for path in trace_files],
                "trace_event_count": sum(result.event_count for result in trace_results),
                "native_instruction_tracing": any(
                    result.native_hooks_available for result in trace_results
                ),
                "captured_chunks": [
                    item for run in dynamic_runs for item in run["captured_chunks"]
                ],
                "error": trace_error,
            },
            "layers": layer_report,
            "limitations": [
                "No syntactically valid source layer was recovered.",
                "Roblox Engine APIs are not supplied; code depending on them may stop at runtime.",
                "VM handler lifting and source reconstruction are not implemented.",
            ],
        }
        try:
            report_path.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        except OSError as exc:
            self.logger.error("Could not write analysis report: %s", exc)
        return report_path

    def _progress(self, percent: float, stage: str) -> None:
        if self.progress_callback is not None:
            self.progress_callback(percent, stage)
