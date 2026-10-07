from __future__ import annotations

import hashlib
import importlib
import json
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

from core.deobfuscator import count_remote_payload_loaders, tokenize
from core.runtime_paths import RESOURCE_ROOT
from core.sandbox import Sandbox, SandboxResult

VENDOR_ROOT = RESOURCE_ROOT / "third_party" / "protez_luraph_v15"
VENDOR_CORE = VENDOR_ROOT / "core"
MAX_LURAPH_V15_SOURCE_BYTES = 2 * 1024 * 1024
HARNESS_STALL_SECONDS = 20.0

MAX_TRACE_TEXT_BYTES = 32 * 1024 * 1024
MAX_DEVIRT_ROUNDS = 8
MAX_TRAP_RUNS = 3
_ENVLOG_BEGIN = "\x00ENVLOG-BEGIN\n"
_ENVLOG_END = "\x00ENVLOG-END"
_LURAPH_V14_BANNER = re.compile(r"luraph\s+obfuscator\s+v?14[.\d]*", re.IGNORECASE)
_LURAPH_V15_BANNER = re.compile(r"luraph\s+obfuscator\s+v?15[.\d]*", re.IGNORECASE)
# `local S=(...)[[LPH]]...` wrappers end with `end}):t()(...)`: a method fetch
# on the table the wrapper returned, which is v14's entry shape.
_V14_ENTRY_TAIL = re.compile(r"\}\s*\)\s*:\s*[A-Za-z_][A-Za-z0-9_]*\s*\(\s*\)\s*\(\s*\.\.\.\s*\)\s*;?\s*$")
_V15_ENTRY_MARKERS = re.compile(r"LPH_(?:ENCSTR|ENCFUNC|CRASH|NO_VIRTUALIZE)")


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
    lift_stats: dict[str, int]
    unresolved_constant_count: int
    unresolved_constant_samples: tuple[str, ...]
    constant_misses: dict[str, int]
    unresolved_runtime_functions: tuple[str, ...]
    placeholder_counts: dict[str, int]
    incomplete_reasons: tuple[str, ...]


_SHARED_STUB = re.compile(
    r'(?m)^local function (?P<name>luraph_runtime\d+)\(\.\.\.\)\r?\n'
    r'[ \t]*error\("Luraph runtime function, not devirtualized"\)\r?\n'
    r'end(?:\r?\n)?'
)


def _prepare_lifted_source(source: str) -> tuple[str, tuple[str, ...], dict[str, int]]:
    """Remove generated error stubs and report actual unresolved lifter markers."""
    tokens = tokenize(source)
    stub_matches = list(_SHARED_STUB.finditer(source))
    unresolved_runtime: list[str] = []
    replacements: list[tuple[int, int, str]] = []
    for match in stub_matches:
        name = match.group("name")
        used_outside_stub = any(
            token.kind == "identifier"
            and token.text == name
            and not (match.start() <= token.start < match.end())
            for token in tokens
        )
        if used_outside_stub:
            unresolved_runtime.append(name)
            replacement = f"-- Unresolved Luraph runtime function {name} was omitted."
        else:
            replacement = ""
        replacements.append((match.start(), match.end(), replacement))

    for start, end, replacement in reversed(replacements):
        source = source[:start] + replacement + source[end:]

    output_tokens = tokenize(source)
    comments = [token.text.lower() for token in output_tokens if token.kind == "comment"]
    opaque_nil_values = 0
    generic_iterator_markers = 0
    unlifted_closure_markers = 0
    unresolved_tail_markers = 0
    for index, token in enumerate(output_tokens):
        following = output_tokens[index + 1] if index + 1 < len(output_tokens) else None
        if (
            token.kind == "identifier"
            and token.text == "nil"
            and following is not None
            and following.kind == "comment"
            and following.text.startswith("--[[")
            and "constant not decoded" not in following.text.lower()
            and "the caller's registers" not in following.text.lower()
        ):
            opaque_nil_values += 1
        if token.kind == "identifier" and token.text == "geniter" and following is not None:
            generic_iterator_markers += following.kind == "symbol" and following.text == "("
        if token.kind == "comment" and "tail?" in token.text.lower():
            unresolved_tail_markers += 1
        if (
            token.kind == "identifier"
            and token.text == "function"
            and index + 4 < len(output_tokens)
            and [item.text for item in output_tokens[index + 1 : index + 4]] == ["(", "...", ")"]
            and output_tokens[index + 4].kind == "comment"
            and "closure" in output_tokens[index + 4].text.lower()
        ):
            unlifted_closure_markers += 1
    placeholder_counts = {
        "undecoded_constants": sum("constant not decoded" in comment for comment in comments),
        "missing_caller_registers": sum("the caller's registers" in comment for comment in comments),
        "opaque_expression_markers": sum(bool(re.search(r"--\[\[\?[^]]+\]\]", comment)) for comment in comments),
        "opaque_nil_values": opaque_nil_values,
        "unlifted_closures": unlifted_closure_markers,
        "generic_iterator_markers": generic_iterator_markers,
        "unresolved_tail_markers": unresolved_tail_markers,
    }
    return source, tuple(sorted(set(unresolved_runtime))), placeholder_counts


def _lift_incomplete_reasons(
    *,
    source: str,
    stats: dict[str, int],
    unresolved_constant_count: int,
    unresolved_runtime_functions: tuple[str, ...],
    placeholder_counts: dict[str, int],
    remote_payload_loader_count: int = 0,
) -> tuple[str, ...]:
    reasons: list[str] = []
    if stats.get("functions", 0) <= 0:
        reasons.append("no payload VM functions were lifted")
    if stats.get("errors", 0) > 0:
        reasons.append(f"{stats['errors']} VM blocks could not be lifted")
    if unresolved_constant_count:
        reasons.append(f"{unresolved_constant_count} lazy constants remain unresolved")
    if unresolved_runtime_functions:
        reasons.append(
            "unresolved Luraph runtime functions: " + ", ".join(unresolved_runtime_functions[:8])
        )
    for key, count in placeholder_counts.items():
        if count:
            label = key.replace("_", " ")
            reasons.append(f"{count} {label} remain in the lifted source")
    if remote_payload_loader_count:
        reasons.append(
            f"{remote_payload_loader_count} remotely fetched Lua payloads are not embedded in the lifted source"
        )
    if not source.strip():
        reasons.append("the lifter emitted no source statements")
    return tuple(reasons)


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
            # Development aid: keep the exact harness a run used so it can be
            # replayed by hand (the vendored runtime heartbeats on stdout).
            dump = os.environ.get("PROTEZ_DUMP_HARNESS")
            if dump:
                Path(dump).write_text(program, encoding="utf-8")
            result = self.sandbox.run(
                program,
                source_name=Path(self.job.input).name,
                trace=False,
                # The vendored runtime heartbeats while it works, so a payload
                # whose VM spins without touching the environment stops
                # reporting and can be given up on long before the wall
                # timeout: its run carries no evidence either way.
                stall_timeout_seconds=HARNESS_STALL_SECONDS,
            )
        except Exception as exc:
            return None, f"isolated Luau harness failed: {type(exc).__name__}: {exc}"
        self.run_results.append(result)
        try:
            output = result.run_log_path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            return None, f"could not read isolated Luau harness output: {exc}"
        if result.stalled:
            return None, (
                f"timed out after {result.duration_seconds:.1f} seconds (no harness output for "
                f"{HARNESS_STALL_SECONDS:.0f}s: the script is stuck in a loop the tracer cannot see)"
            )
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
    """Translate the vendor's byte-preserving internal strings back to UTF-8.

    The batch of runtime options is what the vendor's own ``run_once`` would
    pass: in particular the heartbeat, which is the only thing that tells a
    script working quietly in its own code apart from one spinning where
    nothing can see it.
    """
    def from_latin1(value: str) -> str:
        return value.encode("latin-1").decode("utf-8")

    decoded_chunks = {
        key: from_latin1(value)
        for key, value in (chunks or {}).items()
    }
    options = dict(cfg)
    options.setdefault("heartbeat", getattr(harness, "HEARTBEAT", 2))
    return harness.build_harness(from_latin1(source), options, decoded_chunks)


def luraph_family(source: str) -> str:
    """Which shipped Luraph front end owns this wrapper.

    v14.7/14.8/14.9 (Luraph's method-based state-machine VM, protos as closure
    factories) and v15 (flat dispatch loops) share one analysis engine, but the
    mapper, the runtime capture and the lift differ, so the family is decided
    before anything runs.  The banner is authoritative when it is present; a
    stripped banner is recognised by the v14 entry call the wrapper ends with
    (`...}):t()(...)`, a method lookup on the returned table) or by the
    interpreter's initializer shape.
    """
    head = source[:8192]
    if _LURAPH_V14_BANNER.search(head):
        return "luraph_v14"
    if _LURAPH_V15_BANNER.search(head):
        return "luraph_v15"
    stripped = source.rstrip()
    if _V14_ENTRY_TAIL.search(stripped[-4096:]):
        return "luraph_v14"
    if _V15_ENTRY_MARKERS.search(stripped[-4096:]):
        return "luraph_v15"
    return "luraph_v15"


def _import_vendor(family: str = "luraph_v15"):
    if not VENDOR_CORE.is_dir():
        raise LuraphDevirtualizationError("the Luraph lifter files are missing from this Protez build")
    core_path = str(VENDOR_CORE)
    if core_path not in sys.path:
        sys.path.insert(0, core_path)
    try:
        harness = importlib.import_module("harness")
        driver = importlib.import_module("obfuscators.luraph_v15.driver")
        backend = importlib.import_module("backend")
        if family == "luraph_v14":
            devirt = importlib.import_module("obfuscators.luraph_v14.devirt")
            vmmap = importlib.import_module("obfuscators.luraph_v14.vmmap")
            plugin = importlib.import_module("obfuscators.luraph_v14.driver")
        else:
            devirt = importlib.import_module("obfuscators.luraph_v15.devirt")
            vmmap = None
            plugin = None
    except Exception as exc:
        raise LuraphDevirtualizationError(
            f"could not load the Luraph {family} analysis engine: {type(exc).__name__}: {exc}"
        ) from exc
    return harness, driver, devirt, backend, vmmap, plugin


# Both knobs exist because a Luraph VM does most of its work in the script's
# own code, where nothing touches the environment: the spin watchdog exists to
# stop such a run early, and these decide how early.  The defaults are the
# vendored ones; raising them costs wall time and buys a fuller capture.
LURAPH_SPIN_CHECKS = int(os.environ.get("PROTEZ_LURAPH_SPIN_CHECKS", "24"))
LURAPH_TIME_BUDGET = int(os.environ.get("PROTEZ_LURAPH_TIME_BUDGET", "8"))

# The counter the vendored runtime's spin watchdog reads: it lives inside the
# script's own VM loops, so a payload that spins without ever touching the
# environment still reports (the watchdog keeps the heartbeat alive and stops
# the run with the trace it has).  Same statement the vendor's `patch_spin`
# inserts; only the way the loops are found differs.
_V14_SPIN_COUNTER = "__SPIN.n=__SPIN.n+1;if __SPIN.n>=__SPIN.step then __SPIN.f()end;"

_V14_LOOP_TYPES = ("AstStatWhile", "AstStatRepeat")


def _v14_loop_inserts(vmmap, source: str, scratch_dir: Path) -> list[tuple[int, int]]:
    """Heads of every loop body in `source`, from the pinned Luau parser.

    The vendor's ``patch_spin`` recognises a single textual loop shape with a
    regex (``while true do x = t[i];``).  A Luraph v14 wrapper dispatches
    through several others -- ``while true do if s == ... then``,
    ``while true do a, b = vm:step(...)``, ``repeat ... until false`` -- and a
    regex cannot tell a loop from the same words inside a string literal, so
    the positions come from the AST instead.  Any error returns no positions:
    the runtime's own watchdog is still there as a backstop.
    """

    try:
        scratch_dir.mkdir(parents=True, exist_ok=True)
        path = scratch_dir / ("spin_%s.luau" % hashlib.sha256(source.encode("latin-1")).hexdigest()[:16])
        path.write_bytes(source.encode("latin-1"))
        root = vmmap.load_ast(str(path))
    except Exception:
        return []
    positions: list[tuple[int, int]] = []

    def visit(node) -> None:
        if node.get("type") not in _V14_LOOP_TYPES:
            return
        body = node.get("body") or {}
        location = body.get("location")
        if not location:
            return
        try:
            line, column = (int(part) for part in location.split(" - ")[0].split(","))
        except ValueError:
            return
        positions.append((line, column))

    vmmap.walk(root, visit)
    return positions


def _v14_spin_patch(vmmap, scratch_dir: Path):
    """A drop-in replacement for the vendor's `patch_spin`, for the v14 route."""

    def patch(source: str) -> str:
        positions = _v14_loop_inserts(vmmap, source, scratch_dir)
        if not positions:
            return source
        lines = source.split("\n")
        for line, column in sorted(set(positions), reverse=True):
            if line >= len(lines) or column > len(lines[line]):
                continue
            # The leading space matters: a loop head ends in a keyword
            # (`do`, `repeat`) and gluing the counter to it turns both into one
            # identifier, which deletes the loop and orphans every `break`.
            lines[line] = (
                lines[line][:column] + " " + _V14_SPIN_COUNTER + lines[line][column:]
            )
        return "\n".join(lines)

    return patch


class _V14Route:
    """Point the shared engine at the v14 mapper and lifter for one lift.

    ``patch_entries`` (the runtime instrumentation) and ``patch_entries``'s
    helper lookups resolve the v15 mapper through
    ``obfuscators.luraph_v15.vmmap``, and the shared driver's ``lift`` is a
    module global: both are swapped for the v14 plugin here and restored
    afterwards, so the process can lift either family, in any order.
    """

    def __init__(self, driver, vmmap, plugin, devirt, scratch_dir: Path | None = None,
                 lift_wrapper=None):
        self.driver = driver
        self.vmmap = vmmap
        self.plugin = plugin
        self.devirt = devirt
        self.scratch_dir = Path(scratch_dir) if scratch_dir is not None else Path(tempfile.gettempdir())
        # Applied to the lift this route installs, so the caller's recorder (the
        # one that collects lift statistics for the report) still sees the
        # v14 lift: the route swaps the engine's entry point, and a recorder
        # installed on the module before the route ran would silently never be
        # called -- the report then claimed a wrapper nothing had been lifted
        # from while its 27 prototypes sat in the output.
        self.lift_wrapper = lift_wrapper
        self._saved = []

    def __enter__(self):
        package = importlib.import_module("obfuscators.luraph_v15")
        self._saved.append((package, "vmmap", getattr(package, "vmmap", None)))
        package.vmmap = self.vmmap
        v15_lift = self.driver.lift

        def lift(job, runner, patched, cfg, chunks, run_text, ppath, dpath, chunk_paths):
            return v15_lift(job, runner, patched, cfg, chunks, run_text, ppath, dpath,
                            chunk_paths, self.devirt)

        self._saved.append((self.driver, "lift", v15_lift))
        self.driver.lift = lift
        # The vendor's spin watchdog only recognises the v15 loop shape; the
        # v14 wrappers need the AST-driven one or a spinning payload is
        # indistinguishable from a payload that is merely slow.
        self._saved.append((self.driver, "patch_spin", self.driver.patch_spin))
        self.driver.patch_spin = _v14_spin_patch(self.vmmap, self.scratch_dir)
        self._saved.append((self.driver, "SPIN_CHECKS", self.driver.SPIN_CHECKS))
        self.driver.SPIN_CHECKS = LURAPH_SPIN_CHECKS
        # The v14 dump predates the harness' root ranking: Protez ranks the
        # payload root itself, because the dump's rootCallee is the anti-tamper
        # proto. Engines without the hook (older/newer vendor code) keep theirs.
        if hasattr(self.devirt, "_lift_candidates"):
            self._saved.append((self.devirt, "_lift_candidates", self.devirt._lift_candidates))
            self.devirt._lift_candidates = _v14_root_candidates
        # A v14 container is one flat prototype namespace per VM, so lifting
        # only the ranked root would emit the bootstrap and drop the script's
        # own protos: every proto is lifted instead.
        if hasattr(self.devirt, "lift_program_all"):
            self._saved.append((self.devirt, "lift_program", self.devirt.lift_program))
            installed = self.devirt.lift_program_all
            if self.lift_wrapper is not None:
                installed = self.lift_wrapper(installed)
            self.devirt.lift_program = installed
        return self

    def __exit__(self, *_exc):
        for owner, name, previous in reversed(self._saved):
            setattr(owner, name, previous)
        self._saved.clear()
        return False


def _v14_root_candidates(protos_path: str) -> list[int]:
    """Payload-root candidates for a captured v14 prototype graph.

    The runtime capture reports `root_callee` as the first proto the entry
    method calls, which in the v14 layout is Luraph's anti-tamper proto
    (thousands of opcodes, a deep stack) rather than the program.  Luraph
    numbers the program root first, so the plausible protos are ranked by
    prototype number, skipping the anti-tamper-shaped ones, and the dump's own
    root is pointed at the best candidate: the lifter still tries each
    candidate and keeps the cleanest result, so a wrong ranking costs time,
    never output quality.  A dump that already carries the harness' ranked
    roots (`root_candidates`, v15 captures) keeps that order.
    """
    try:
        data = json.loads(Path(protos_path).read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return []
    harness_ranked = [int(pid) for pid in (data.get("root_candidates") or []) if str(pid).isdigit()]
    protos = data.get("protos") or {}
    tables = data.get("tables") or {}
    ranked: list[tuple[int, int]] = []
    for key, proto in protos.items():
        if not key.isdigit() or not isinstance(proto, dict):
            continue
        ops = proto.get("H")
        if not isinstance(ops, dict) or "t" not in ops:
            continue
        table = tables.get(str(ops["t"]))
        if not table:
            continue
        count = len(table.get("arr") or [])
        maxstack = proto.get("K")
        if not isinstance(maxstack, (int, float)):
            maxstack = 0
        if count < 64 or maxstack >= 80:
            continue
        ranked.append((int(key), count))
    ranked.sort()
    candidates = [pid for pid, _count in ranked]
    if harness_ranked:
        return harness_ranked + [pid for pid in candidates if pid not in harness_ranked]
    if candidates and data.get("root_callee") not in candidates:
        # the capture's own root is anti-tamper shaped: make the best candidate
        # the default so the lifter's first walk is the program, not the trap
        data["root_callee"] = candidates[0]
        try:
            Path(protos_path).write_text(json.dumps(data, separators=(",", ":")), encoding="utf-8")
        except OSError:
            pass
    return candidates


def _install_analysis_deadline(backend, deadline: float) -> None:
    """Interrupt the lifter's large-stack worker at the pipeline deadline."""
    def run_big_stack(fn, *args):
        previous_recursion_limit = sys.getrecursionlimit()
        previous_stack_size = threading.stack_size()
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
        try:
            try:
                worker.start()
            finally:
                threading.stack_size(previous_stack_size)
            worker.join(max(0.0, deadline - time.monotonic()) + 1.0)
        finally:
            sys.setrecursionlimit(previous_recursion_limit)
        if worker.is_alive():
            raise TimeoutError("Luraph VM lifting exceeded Protez's analysis time limit")
        if "error" in result:
            raise result["error"]
        return result.get("value")

    backend.run_big_stack = run_big_stack


def devirtualize_luraph(
    source: str,
    *,
    source_name: str,
    tools_dir: Path,
    logs_dir: Path,
    timeout_seconds: float,
    total_budget_seconds: float,
    logger: logging.Logger,
    family: str = "auto",
) -> LuraphDevirtualizationResult:
    if family == "auto":
        family = luraph_family(source)
    label = "Luraph v14" if family == "luraph_v14" else "Luraph v15"
    source_bytes = source.encode("utf-8")
    if len(source_bytes) > MAX_LURAPH_V15_SOURCE_BYTES:
        raise LuraphDevirtualizationError(
            f"{label} VM lifting is limited to {MAX_LURAPH_V15_SOURCE_BYTES // (1024 * 1024)} MiB; "
            "the bounded static and runtime report is still available"
        )

    ast_tool = tools_dir / ("luau-ast.exe" if os.name == "nt" else "luau-ast")
    if not ast_tool.is_file():
        raise LuraphDevirtualizationError(
            f"the pinned Luau AST parser is missing; repair Protez's native runtime before lifting {label}"
        )

    started = time.monotonic()
    deadline = started + total_budget_seconds
    vendor_source = source_bytes.decode("latin-1")
    harness, driver, devirt, backend, vmmap, plugin = _import_vendor(family)
    previous_backend_big_stack = backend.run_big_stack
    previous_big_stack = devirt.run_big_stack
    previous_lift_program = devirt.lift_program
    lift_observations: list[dict[str, object]] = []

    _install_analysis_deadline(backend, deadline)

    def make_record_lift(lift):
        def record_lift(*args, **kwargs):
            return _record(lift, *args, **kwargs)
        return record_lift

    def _record(lift, *args, **kwargs):
        result = lift(*args, **kwargs)
        if isinstance(result, tuple) and len(result) == 4:
            _text, stats, requests, _buffer_patches = result
            dump = devirt.LAST_DUMP[-1] if devirt.LAST_DUMP else None
            lift_observations.append(
                {
                    "stats": {str(key): int(value) for key, value in stats.items()},
                    "request_count": len(requests),
                    "request_samples": tuple(sorted(str(item) for item in requests)[:32]),
                    "misses": {
                        str(key): int(value)
                        for key, value in (dump.misses.items() if dump is not None else ())
                    },
                }
            )
        return result

    # devirt cached backend.run_big_stack at import time, so patch its alias as
    # well as backend's implementation to enforce Protez's per-input deadline.
    devirt.run_big_stack = backend.run_big_stack
    devirt.lift_program = make_record_lift(previous_lift_program)

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
                budget=max(1, min(LURAPH_TIME_BUDGET, int(timeout_seconds))),
                executor="Protez Offline",
                input_text=None,
                cfg=[],
                strings=False,
            )
            job = _Job(source_path, vendor_source, trace_path, args)

            def lift_once():
                if family == "luraph_v14":
                    with _V14Route(driver, vmmap, plugin, devirt, scratch_dir=work,
                                   lift_wrapper=make_record_lift):
                        return driver.run(job)
                return driver.run(job)

            try:
                returned_path = lift_once()
            except SystemExit as exc:
                detail = str(exc).strip() or "the family lifter rejected this wrapper shape"
                # A capture is a snapshot of a running script: which tables the
                # runtime recorded (and how far it got) varies a little from run
                # to run, and a v14 walk can come up empty on one snapshot and
                # map the whole program on the next.  One retry, and only while
                # there is budget left for it, is what keeps a fixture from
                # reporting "cannot read" for a wrapper it just read.
                retryable = "no closure makers" in detail or "dispatchers found" in detail
                if retryable and deadline - time.monotonic() > 25.0:
                    logger.info("Luraph %s lift found no program in this capture; retrying", label)
                    for stale in (job.path(".protos.json"), job.path(".devirt.luau")):
                        try:
                            Path(stale).unlink()
                        except OSError:
                            pass
                    try:
                        returned_path = lift_once()
                    except SystemExit as second:
                        raise LuraphDevirtualizationError(
                            str(second).strip() or detail
                        ) from second
                else:
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
                    raise LuraphDevirtualizationError(
                        f"could not read lifted Luau source: {exc}"
                    ) from exc
                lifted, unresolved_runtime, placeholder_counts = _prepare_lifted_source(lifted)
                observation = lift_observations[-1] if lift_observations else {}
                lift_stats = dict(observation.get("stats", {}))
                unresolved_constant_count = int(observation.get("request_count", 0))
                unresolved_constant_samples = tuple(observation.get("request_samples", ()))
                incomplete_reasons = _lift_incomplete_reasons(
                    source=lifted,
                    stats=lift_stats,
                    unresolved_constant_count=unresolved_constant_count,
                    unresolved_runtime_functions=unresolved_runtime,
                    placeholder_counts=placeholder_counts,
                    remote_payload_loader_count=count_remote_payload_loaders(lifted),
                )
                output_path.write_text(lifted, encoding="utf-8", newline="")
                trace_source = None
                if trace_path.is_file():
                    try:
                        trace_source = trace_path.read_text(encoding="utf-8", errors="replace")
                    except OSError:
                        pass
                return LuraphDevirtualizationResult(
                    source=lifted,
                    route=("luraph-v14-vm-lifter" if family == "luraph_v14" else "luraph-v15-vm-lifter"),
                    run_results=tuple(run_results),
                    trace_source=trace_source,
                    source_bytes=len(source_bytes),
                    elapsed_seconds=time.monotonic() - started,
                    lift_stats=lift_stats,
                    unresolved_constant_count=unresolved_constant_count,
                    unresolved_constant_samples=unresolved_constant_samples,
                    constant_misses=dict(observation.get("misses", {})),
                    unresolved_runtime_functions=unresolved_runtime,
                    placeholder_counts=placeholder_counts,
                    incomplete_reasons=incomplete_reasons,
                )
            raise LuraphDevirtualizationError(
                "the wrapper ran, but the family lifter recovered only a behavior trace, not VM source"
            )
    finally:
        harness.Runner = previous_runner
        devirt.lift_program = previous_lift_program
        devirt.run_big_stack = previous_big_stack
        backend.run_big_stack = previous_backend_big_stack
        for key, previous in (
            ("PROTEZ_LUAU_AST", previous_ast),
            ("PROTEZ_ANALYSIS_DEADLINE", previous_deadline),
            ("DEOB_NO_SERVE", previous_no_serve),
        ):
            if previous is None:
                os.environ.pop(key, None)
            else:
                os.environ[key] = previous


def devirtualize_luraph_v15(source: str, **kwargs) -> LuraphDevirtualizationResult:
    """Lift a v15 wrapper (kept as the stable entry point for older callers)."""
    kwargs.pop("family", None)
    return devirtualize_luraph(source, family="luraph_v15", **kwargs)
