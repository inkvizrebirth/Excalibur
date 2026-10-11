"""The deobfuscation pipeline.

Stages, in order:

1. **route** - detect the obfuscator and pick a :class:`core.registry.Deobfuscator`.
2. **static** - decode the WRD constant layer (string pool, resolver inlining,
   constant folding) and produce ``decoded.lua``.  Fast, deterministic and, for
   scripts whose payload is interpreted rather than rebuilt as text, the only
   stage that yields anything readable.
3. **dynamic** - run the script in the sandbox with hooks, following the
   runtime/policy ladder, and capture everything the script compiles or
   reassembles.  This is what recovers the *original script text* whenever the
   obfuscator rebuilds it with ``loadstring``.
4. **trace** - when neither stage produced a validated payload, instrument the
   dispatch loop and record the visited states (diagnostics, see
   :mod:`core.vm_trace`).

The pipeline always writes a machine readable ``report.json`` plus a human
readable ``summary.txt`` next to the artefacts, so a failed run is still
actionable ("Lua 5.1 could not compile the file: control structure too long;
Lua 5.4 did compile but the script exited after reading TheGlobalX, ...").
"""

from __future__ import annotations

import hashlib
import json
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional

from . import paths
from .config import PipelineConfig
from .errors import ExcaliburError
from .pick_payload import PayloadPick, pick_payload, rank_payloads, score_text
from .registry import detect_and_route
from .sandbox import Attempt, Sandbox, SandboxResult
from .sourceio import write_source
from .validate import MODE_DYNAMIC, MODE_STATIC, ValidationResult, validate_payload
from .vm_trace import instrument_dispatch, read_trace, render_summary, summarize_trace
from .wrd_static import StaticLayerResult, analyze

ProgressCallback = Callable[[str, str], None]


@dataclass
class StageResult:
    name: str
    ok: bool
    detail: str = ""
    duration_ms: int = 0
    data: dict = field(default_factory=dict)

    def as_dict(self) -> dict:
        return {"name": self.name, "ok": self.ok, "detail": self.detail, "duration_ms": self.duration_ms, "data": self.data}


@dataclass
class DeobfuscationResult:
    """Everything the caller (GUI/CLI/tests) needs to know about a run."""

    source_hash: str
    success: bool = False
    partial: bool = False
    """True when only the constant layer was removed (the flattened payload
    remains) - reported as "partial" instead of a full deobfuscation."""

    method: str = "none"
    output: Optional[str] = None
    output_path: Optional[Path] = None
    decoded_path: Optional[Path] = None
    report_path: Optional[Path] = None
    summary_path: Optional[Path] = None
    workdir: Optional[Path] = None
    route: str = ""
    detection: dict = field(default_factory=dict)
    stages: List[StageResult] = field(default_factory=list)
    picks: List[dict] = field(default_factory=list)
    validation: Optional[dict] = None
    chosen: Optional[dict] = None
    static: Optional[dict] = None
    sandbox: Optional[dict] = None
    trace: Optional[dict] = None
    runtime_used: Optional[str] = None
    notes: List[str] = field(default_factory=list)
    elapsed_ms: int = 0

    def as_dict(self) -> dict:
        return {
            "source_hash": self.source_hash,
            "success": self.success,
            "partial": self.partial,
            "method": self.method,
            "route": self.route,
            "detection": self.detection,
            "stages": [s.as_dict() for s in self.stages],
            "picks": self.picks,
            "validation": self.validation,
            "chosen": self.chosen,
            "static": self.static,
            "sandbox": self.sandbox,
            "trace": self.trace,
            "runtime_used": self.runtime_used,
            "notes": self.notes,
            "elapsed_ms": self.elapsed_ms,
            "output_path": str(self.output_path) if self.output_path else None,
            "decoded_path": str(self.decoded_path) if self.decoded_path else None,
            "workdir": str(self.workdir) if self.workdir else None,
        }

    # ------------------------------------------------------------------ report
    def summary_text(self) -> str:
        lines: List[str] = []
        lines.append("Excalibur deobfuscation summary")
        lines.append("=" * 30)
        lines.append(f"source sha1     : {self.source_hash}")
        lines.append(f"route           : {self.route or 'unknown'}")
        if self.success and self.partial:
            verdict = "PARTIAL (constant layer removed, payload still virtualised)"
        elif self.success:
            verdict = f"SUCCESS ({self.method})"
        else:
            verdict = "no validated payload"
        lines.append(f"result          : {verdict}")
        lines.append(f"runtime used    : {self.runtime_used or '-'}")
        lines.append(f"elapsed         : {self.elapsed_ms} ms")
        if self.output_path:
            lines.append(f"output          : {self.output_path}")
        if self.decoded_path:
            lines.append(f"decoded layer   : {self.decoded_path}")
        lines.append("")
        lines.append("stages:")
        for stage in self.stages:
            status = "ok" if stage.ok else "failed"
            lines.append(f"  - {stage.name:<8} {status:<7} {stage.duration_ms:>6} ms  {stage.detail}")
        if self.static:
            stats = self.static.get("stats") or {}
            lines.append("")
            lines.append(
                "static layer    : "
                f"{stats.get('decoded_entries', 0)}/{stats.get('pool_entries', 0)} constants decoded, "
                f"{stats.get('inlined_calls', 0)} resolver calls inlined, "
                f"{stats.get('folded_expressions', 0)} expressions folded"
            )
        if self.sandbox:
            lines.append("")
            lines.append("sandbox attempts:")
            for attempt in self.sandbox.get("attempts", []):
                lines.append(f"  - {attempt.get('summary')}")
            for rejection in self.sandbox.get("rejected_runtimes", []):
                lines.append(f"  - rejected {rejection['name']}: {rejection['error'][:100]}")
        if self.chosen:
            lines.append("")
            lines.append(f"chosen candidate: {self.chosen.get('source')} score={self.chosen.get('score')} "
                         f"({self.chosen.get('length')} chars)")
        if self.validation:
            lines.append(f"validation      : {'valid' if self.validation.get('valid') else 'invalid'} - "
                         f"{self.validation.get('reason', '')[:160]}")
        if self.trace:
            lines.append("")
            lines.append(f"trace fallback  : {self.trace.get('states', 0)} states, "
                         f"{self.trace.get('distinct', 0)} distinct")
        if self.notes:
            lines.append("")
            lines.append("notes:")
            for note in self.notes:
                lines.append(f"  - {note}")
        return "\n".join(lines) + "\n"


def _log(progress: Optional[ProgressCallback], stage: str, message: str) -> None:
    if progress:
        try:
            progress(stage, message)
        except Exception:  # pragma: no cover - a UI callback must never break a run
            pass


def deobfuscate(
    source: str,
    *,
    config: Optional[PipelineConfig] = None,
    source_name: str = "input.lua",
    encoding: str = "utf-8",
    progress: Optional[ProgressCallback] = None,
    workdir: Optional[Path] = None,
) -> DeobfuscationResult:
    """Run the full pipeline on ``source`` and return a result object."""
    config = config or PipelineConfig()
    started = time.time()
    source_hash = hashlib.sha1(source.encode(encoding, "replace")).hexdigest()
    result = DeobfuscationResult(source_hash=source_hash, workdir=workdir)
    _log(progress, "start", f"{len(source)} chars, sha1 {source_hash[:12]}")

    # ---------------------------------------------------------------- routing
    route = detect_and_route(source)
    result.route = route.message
    result.detection = route.detection.as_dict()
    _log(progress, "detect", route.message)
    if route.detection.warnings:
        result.notes.extend(route.detection.warnings)

    if not route.detection.is_obfuscated:
        result.notes.append(
            "the input carries no known obfuscator signature; running the generic stages anyway "
            "(detection may miss a modified build)."
        )

    if route.detection.is_obfuscated and not route.supported and route.deobfuscator is not None:
        result.notes.append(
            f"{route.deobfuscator.label} is recognised but not supported yet; "
            "running the generic stages anyway (they are format agnostic)."
        )

    # ----------------------------------------------------------------- static
    static_result: Optional[StaticLayerResult] = None
    if config.prefer_static:
        stage_started = time.time()
        _log(progress, "static", "decoding string layer")
        try:
            static_result = analyze(source, inline=True, fold=True)
        except Exception as exc:  # defensive: a malformed input must not crash the GUI
            static_result = StaticLayerResult(ok=False, reason=f"{type(exc).__name__}: {exc}")
        duration = int((time.time() - stage_started) * 1000)
        if static_result.ok:
            stats = static_result.stats()
            detail = (f"{stats['decoded_entries']}/{stats['pool_entries']} constants, "
                      f"{stats['inlined_calls']} inlined, {stats['folded_expressions']} folded")
            result.static = static_result.as_dict()
            result.stages.append(StageResult("static", True, detail, duration, result.static))
            _log(progress, "static", detail)
        else:
            result.static = static_result.as_dict()
            result.stages.append(StageResult("static", False, static_result.reason, duration, result.static))
            _log(progress, "static", f"skipped: {static_result.reason}")

    candidates: List[PayloadPick] = []
    if static_result is not None and static_result.ok and static_result.output:
        static_score, static_reasons = score_text(static_result.output)
        candidates.append(
            PayloadPick(path=None, text=static_result.output, score=static_score,
                        reasons=["static constant layer removal"] + static_reasons, source="static")
        )

    # ---------------------------------------------------------------- dynamic
    sandbox_result: Optional[SandboxResult] = None
    if config.run_dynamic:
        stage_started = time.time()
        _log(progress, "dynamic", "running the script in the sandbox")
        sandbox = Sandbox(config.sandbox)

        def stop_when(attempt: Attempt) -> bool:
            """Stop the ladder as soon as an attempt yields a compilable payload."""
            captured = list(attempt.dumps) + list(attempt.concats) + list(attempt.sandbox_files)
            if not captured:
                return False
            pick = pick_payload(captured, source, min_chars=config.min_payload_chars, source_hash=source_hash)
            if pick is None:
                return False
            validation = validate_payload(pick.text, source=source)
            if validation.valid:
                _log(progress, "dynamic", f"captured payload via {pick.source} ({pick.length} chars)")
            return validation.valid

        try:
            sandbox_result = sandbox.run(
                source,
                source_name=source_name,
                stop_when=stop_when,
                max_attempts=config.sandbox.max_attempts,
                workdir=workdir,
                encoding=encoding,
            )
        except ExcaliburError as exc:
            result.notes.append(f"sandbox error: {exc}")
            sandbox_result = None

        duration = int((time.time() - stage_started) * 1000)
        if sandbox_result is not None:
            result.sandbox = sandbox_result.as_dict()
            attempts = len(sandbox_result.attempts)
            captured = len(sandbox_result.all_dumps())
            detail = f"{attempts} attempt(s), {captured} chunk(s) captured"
            if sandbox_result.rejected_runtimes:
                detail += f", {len(sandbox_result.rejected_runtimes)} runtime(s) rejected"
            result.stages.append(StageResult("dynamic", captured > 0, detail, duration, result.sandbox))
            _log(progress, "dynamic", detail)
            if sandbox_result.best:
                result.runtime_used = sandbox_result.best.runtime.name
            result.notes.extend(sandbox_result.notes)
            for rejection in sandbox_result.rejected_runtimes:
                result.notes.append(f"{rejection[0].name} rejected the input: {rejection[1][:120]}")

            for attempt in sandbox_result.attempts:
                for row in attempt.report.get("captures", []):
                    if row.get("kind") == "file" and row.get("value"):
                        result.notes.append(f"script tried to access file: {str(row['value'])[:120]}")
            dynamic_pick = pick_payload(
                sandbox_result.all_candidates(),
                source,
                min_chars=config.min_payload_chars,
                source_hash=source_hash,
            )
            if dynamic_pick is not None:
                dynamic_pick.reasons.append("captured at runtime")
                candidates.append(dynamic_pick)
        else:
            result.stages.append(StageResult("dynamic", False, "sandbox did not run", duration))

    # ------------------------------------------------------- rank and validate
    ranked = rank_payloads(candidates)
    result.picks = [c.as_dict() for c in ranked[:10]]
    chosen: Optional[PayloadPick] = None
    validation: Optional[ValidationResult] = None

    # 1) a runtime-captured payload must be *clean* source to be accepted;
    dynamic_ranked = [c for c in ranked if c.source in {"load", "concat", "writefile"}]
    for candidate in dynamic_ranked[:8]:
        check = validate_payload(candidate.text, source=source, mode=MODE_DYNAMIC)
        if check.valid:
            chosen, validation = candidate, check
            break
        if validation is None:
            validation = check
            result.notes.append(f"captured payload rejected: {check.reason[:200]}")

    # 2) otherwise the rewritten constant layer is still a useful (partial) result
    if chosen is None:
        for candidate in [c for c in ranked if c.source == "static"][:2]:
            check = validate_payload(candidate.text, source=source, mode=MODE_STATIC)
            if check.valid:
                chosen, validation = candidate, check
                break
            if validation is None:
                validation = check
                result.notes.append(f"constant layer rejected: {check.reason[:200]}")
    if chosen is not None:
        result.success = True
        dynamic_source = chosen.source in {"load", "concat", "writefile"}
        result.method = "dynamic" if dynamic_source else "static"
        result.partial = not dynamic_source
        if result.partial:
            result.notes.append(
                "the chosen candidate is the constant-layer rewrite, not the original source: the "
                "payload is still virtualised. See report.json -> trace and docs/REAL_WORLD_NOTES.md."
            )
        result.output = chosen.text
        result.chosen = chosen.as_dict()
        result.validation = validation.as_dict() if validation else None
    elif validation is not None:
        result.validation = validation.as_dict()

    # ----------------------------------------------------------------- trace
    if not result.success and config.trace_on_failure and sandbox_result is not None and sandbox_result.best:
        stage_started = time.time()
        _log(progress, "trace", "instrumenting dispatch loop")
        plan = instrument_dispatch(source)
        if plan.injections:
            trace_attempt = Sandbox(config.sandbox).trace_run(
                source, plan.instrumented, sandbox_result.best, source_name=source_name, encoding=encoding
            )
            trace_path = trace_attempt.trace
            states = read_trace(trace_path) if trace_path else []
            summary = summarize_trace(states)
            result.trace = {**plan.as_dict(), **summary}
            if states:
                summary_path = (sandbox_result.workdir if sandbox_result else paths.logs_dir()) / "trace_summary.txt"
                write_source(summary_path, render_summary(summary))
                result.trace["summary_path"] = str(summary_path)
            result.stages.append(
                StageResult("trace", bool(states), f"{summary.get('states', 0)} states recorded",
                            int((time.time() - stage_started) * 1000), plan.as_dict())
            )
            _log(progress, "trace", f"{summary.get('states', 0)} states, {summary.get('distinct', 0)} distinct")
        else:
            result.stages.append(
                StageResult("trace", False, "; ".join(plan.notes) or "nothing to instrument",
                            int((time.time() - stage_started) * 1000))
            )

    # --------------------------------------------------------------- artefacts
    run_dir = Path(workdir) if workdir else (sandbox_result.workdir if sandbox_result else config.resolved_workdir())
    paths.ensure_dir(run_dir)
    result.workdir = run_dir

    if static_result is not None and static_result.ok and static_result.output:
        decoded_path = run_dir / "decoded.lua"
        write_source(decoded_path, static_result.output, encoding=encoding)
        result.decoded_path = decoded_path

    if result.success and result.output:
        output_path = run_dir / "output.lua"
        write_source(output_path, result.output, encoding=encoding)
        result.output_path = output_path

    result.elapsed_ms = int((time.time() - started) * 1000)
    report_path = run_dir / "report.json"
    report_path.write_text(json.dumps(result.as_dict(), indent=2, ensure_ascii=False), encoding="utf-8")
    result.report_path = report_path

    summary_path = run_dir / "summary.txt"
    summary_path.write_text(result.summary_text(), encoding="utf-8")
    result.summary_path = summary_path

    if not result.success:
        hint = "no validated payload was produced"
        if not candidates:
            hint += "; the sandbox captured nothing - see report.json for the per-attempt diagnostics"
        elif validation is not None:
            hint += f"; last validation failure: {validation.reason[:200]}"
        result.notes.append(hint)
    _log(progress, "done", "success" if result.success else "no payload")
    return result


def deobfuscate_file(
    path: str | Path,
    *,
    config: Optional[PipelineConfig] = None,
    progress: Optional[ProgressCallback] = None,
) -> DeobfuscationResult:
    """Convenience wrapper: read a file byte faithfully and run the pipeline."""
    from .sourceio import read_source

    source = read_source(path)
    return deobfuscate(
        source.text,
        config=config,
        source_name=Path(path).name,
        encoding=source.encoding,
        progress=progress,
    )


__all__ = ["DeobfuscationResult", "StageResult", "deobfuscate", "deobfuscate_file"]
