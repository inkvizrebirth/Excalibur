from __future__ import annotations

import importlib
import logging
import os
import re
import sys
import tempfile
import threading
import time
from dataclasses import dataclass
from pathlib import Path
from types import SimpleNamespace

from core.runtime_paths import RESOURCE_ROOT
from core.sandbox import Sandbox, SandboxResult

VENDOR_ROOT = RESOURCE_ROOT / "third_party" / "protez_luraph_v15"
VENDOR_CORE = VENDOR_ROOT / "core"
MAX_LURAPH_V15_SOURCE_BYTES = 2 * 1024 * 1024
MAX_TRACE_TEXT_BYTES = 32 * 1024 * 1024
MAX_DEVIRT_ROUNDS = 8
MAX_TRAP_RUNS = 3
_ENVLOG_BEGIN = "\x00ENVLOG-BEGIN\n"
_ENVLOG_END = "\x00ENVLOG-END"


class LuraphDevirtualizationError(RuntimeError):
    pass


@dataclass(frozen=True)
class LuraphDevirtualizationResult:
    source: str
    route: str
    run_results: tuple[SandboxResult, ...]
    trace_source: str | None
    source_bytes: int
    elapsed_seconds: float


class _Job:
    def __init__(self, source_path: Path, source: str, trace_path: Path, args):
        self.input = str(source_path)
        self.source = source
        self.source_path = str(source_path)
        self.trace_path = str(trace_path)
        self.debug = False
        self.obfuscator = "Luraph v15"
        self.args = args

    @property
    def base(self) -> str:
        value = self.trace_path
        for suffix in (".deobf.luau", ".luau"):
            if value.endswith(suffix):
                return value[: -len(suffix)]
        return value

    @property
    def outdir(self) -> str:
        return str(Path(self.trace_path).parent)

    def path(self, suffix: str) -> str:
        return self.base + suffix

    def write(self, path: str, text: str, encoding: str = "utf-8") -> str:
        with open(path, "w", encoding=encoding, newline="\n" if encoding == "utf-8" else "") as output:
            output.write(text)
        return path

    def credit_header(self) -> str:
        return ""


class _ProtezRunner:
    def __init__(self, job: _Job, *, sandbox: Sandbox, timeout_seconds: float,
                 deadline: float, run_results: list[SandboxResult]):
        self.job = job
        self.bridge = None
        self.luau = None
        self.hpath = job.trace_path + ".harness.luau"
        self.sandbox = sandbox
        self.timeout_seconds = timeout_seconds
        self.deadline = deadline
        self.run_results = run_results

    def run(self, source, cfg, chunks=None):
        harness = importlib.import_module("harness")
        remaining = self.deadline - time.monotonic()
        if remaining <= 0:
            return None, "Luraph devirtualization reached Protez's total analysis time limit"
        self.sandbox.timeout_seconds = min(self.timeout_seconds, remaining)
        try:
            program = _build_sandbox_harness(harness, source, cfg, chunks)
            result = self.sandbox.run(
                program,
                source_name=Path(self.job.input).name,
                trace=False,
            )
        except Exception as exc:
            return None, f"isolated Luau harness failed: {type(exc).__name__}: {exc}"
        self.run_results.append(result)
        try:
            output = result.run_log_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return None, f"could not read isolated Luau harness output: {exc}"
        if result.timed_out:
            return None, f"timed out after {result.duration_seconds:.1f} seconds"
        if result.output_limited:
            return None, "isolated Luau harness exceeded the output limit"
        if len(output.encode("utf-8", errors="replace")) > MAX_TRACE_TEXT_BYTES:
            return None, "isolated Luau harness output exceeded the devirtualizer limit"
        output = re.sub(r"\x00HB\r?\n {16384}\r?\n", "", output).replace("\r\n", "\n")
        harness.LAST_RAW[0] = output
        start = output.find(_ENVLOG_BEGIN)
        if start < 0:
            return None, output[-3000:]
        start += len(_ENVLOG_BEGIN)
        end = output.find(_ENVLOG_END, start)
        if end < 0:
            return None, output[-3000:]
        body = output[start:end]
        for path in {self.hpath, self.hpath.replace("\\", "/")}:
            if path + ":" in body:
                body = re.sub(re.escape(path) + r":\d+: ", "", body)
        return body, None

    def finish(self):
        return None


def _build_sandbox_harness(harness, source: str, cfg, chunks) -> str:
    """Translate the vendor's byte-preserving internal strings back to UTF-8."""
    def from_latin1(value: str) -> str:
        return value.encode("latin-1").decode("utf-8")

    decoded_chunks = {
        key: from_latin1(value)
        for key, value in (chunks or {}).items()
    }
    return harness.build_harness(from_latin1(source), cfg, decoded_chunks)


def _import_vendor():
    if not VENDOR_CORE.is_dir():
        raise LuraphDevirtualizationError("the Luraph v15 lifter files are missing from this Protez build")
    core_path = str(VENDOR_CORE)
    if core_path not in sys.path:
        sys.path.insert(0, core_path)
    try:
        harness = importlib.import_module("harness")
        driver = importlib.import_module("obfuscators.luraph_v15.driver")
        backend = importlib.import_module("backend")
    except Exception as exc:
        raise LuraphDevirtualizationError(
            f"could not load the Luraph v15 analysis engine: {type(exc).__name__}: {exc}"
        ) from exc
    return harness, driver, backend


def _install_analysis_deadline(backend, deadline: float) -> None:
    """Interrupt the lifter's large-stack worker at the pipeline deadline."""
    def run_big_stack(fn, *args):
        sys.setrecursionlimit(200_000)
        threading.stack_size(256 * 1024 * 1024 - 4096)
        result = {}

        def deadline_trace(frame, event, arg):
            if event == "line" and time.monotonic() >= deadline:
                raise TimeoutError("Luraph VM lifting exceeded Protez's analysis time limit")
            return deadline_trace

        def target():
            sys.settrace(deadline_trace)
            try:
                result["value"] = fn(*args)
            except BaseException as exc:
                result["error"] = exc
            finally:
                sys.settrace(None)

        worker = threading.Thread(target=target, name="protez-luraph-lifter")
        worker.start()
        worker.join(max(0.0, deadline - time.monotonic()) + 1.0)
        if worker.is_alive():
            raise TimeoutError("Luraph VM lifting exceeded Protez's analysis time limit")
        if "error" in result:
            raise result["error"]
        return result.get("value")

    backend.run_big_stack = run_big_stack


def devirtualize_luraph_v15(
    source: str,
    *,
    source_name: str,
    tools_dir: Path,
    logs_dir: Path,
    timeout_seconds: float,
    total_budget_seconds: float,
    logger: logging.Logger,
) -> LuraphDevirtualizationResult:
    source_bytes = source.encode("utf-8")
    if len(source_bytes) > MAX_LURAPH_V15_SOURCE_BYTES:
        raise LuraphDevirtualizationError(
            f"Luraph v15 VM lifting is limited to {MAX_LURAPH_V15_SOURCE_BYTES // (1024 * 1024)} MiB; "
            "the bounded static and runtime report is still available"
        )

    ast_tool = tools_dir / ("luau-ast.exe" if os.name == "nt" else "luau-ast")
    if not ast_tool.is_file():
        raise LuraphDevirtualizationError(
            "the pinned Luau AST parser is missing; repair Protez's native runtime before lifting Luraph v15"
        )

    started = time.monotonic()
    deadline = started + total_budget_seconds
    vendor_source = source_bytes.decode("latin-1")
    harness, driver, backend = _import_vendor()
    _install_analysis_deadline(backend, deadline)

    run_results: list[SandboxResult] = []
    sandbox = Sandbox(
        tools_dir=tools_dir,
        logs_dir=logs_dir,
        timeout_seconds=min(timeout_seconds, total_budget_seconds),
        max_input_bytes=32 * 1024 * 1024,
        max_output_bytes=32 * 1024 * 1024,
        logger=logger,
    )

    previous_runner = harness.Runner
    previous_ast = os.environ.get("PROTEZ_LUAU_AST")
    previous_deadline = os.environ.get("PROTEZ_ANALYSIS_DEADLINE")
    previous_no_serve = os.environ.get("DEOB_NO_SERVE")
    harness.Runner = lambda job: _ProtezRunner(
        job,
        sandbox=sandbox,
        timeout_seconds=timeout_seconds,
        deadline=deadline,
        run_results=run_results,
    )
    os.environ["PROTEZ_LUAU_AST"] = str(ast_tool)
    os.environ["PROTEZ_ANALYSIS_DEADLINE"] = str(deadline)
    os.environ["DEOB_NO_SERVE"] = "1"

    try:
        with tempfile.TemporaryDirectory(prefix="protez-luraph-") as work_dir:
            work = Path(work_dir)
            source_path = work / Path(source_name).name
            if source_path.suffix.lower() not in {".lua", ".luau", ".txt"}:
                source_path = source_path.with_suffix(".luau")
            source_path.write_bytes(source_bytes)
            trace_path = work / (source_path.stem + ".deobf.luau")
            args = SimpleNamespace(
                no_devirt=False,
                no_hooks=False,
                no_tidy=False,
                keep_preamble=False,
                max_runs=MAX_TRAP_RUNS,
                devirt_rounds=MAX_DEVIRT_ROUNDS,
                no_fold=False,
                raw=None,
                timeout=max(1, int(min(timeout_seconds, total_budget_seconds))),
                keep_harness=False,
                studio=False,
                port=0,
                studio_wait=0,
                budget=max(1, min(8, int(timeout_seconds))),
                executor="Protez Offline",
                input_text=None,
                cfg=[],
                strings=False,
            )
            job = _Job(source_path, vendor_source, trace_path, args)
            try:
                returned_path = driver.run(job)
            except SystemExit as exc:
                detail = str(exc).strip() or "the family lifter rejected this wrapper shape"
                raise LuraphDevirtualizationError(detail) from exc
            except TimeoutError as exc:
                raise LuraphDevirtualizationError(str(exc)) from exc
            except Exception as exc:
                raise LuraphDevirtualizationError(
                    f"family lifter failed: {type(exc).__name__}: {exc}"
                ) from exc

            if not returned_path:
                raise LuraphDevirtualizationError("the family lifter produced no output")
            output_path = Path(returned_path)
            if output_path.name.endswith(".devirt.luau") and output_path.is_file():
                try:
                    lifted = output_path.read_text(encoding="utf-8")
                except (OSError, UnicodeDecodeError) as exc:
                    raise LuraphDevirtualizationError(f"could not read lifted Luau source: {exc}") from exc
                trace_source = None
                if trace_path.is_file():
                    try:
                        trace_source = trace_path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass
                return LuraphDevirtualizationResult(
                    source=lifted,
                    route="luraph-v15-vm-lifter",
                    run_results=tuple(run_results),
                    trace_source=trace_source,
                    source_bytes=len(source_bytes),
                    elapsed_seconds=time.monotonic() - started,
                )
            raise LuraphDevirtualizationError(
                "the wrapper ran, but the family lifter recovered only a behavior trace, not VM source"
            )
    finally:
        harness.Runner = previous_runner
        for key, previous in (
            ("PROTEZ_LUAU_AST", previous_ast),
            ("PROTEZ_ANALYSIS_DEADLINE", previous_deadline),
            ("DEOB_NO_SERVE", previous_no_serve),
        ):
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous
