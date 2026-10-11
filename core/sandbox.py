"""Sandboxed execution of obfuscated Lua in an isolated environment.

The sandbox is deliberately *layered*:

1. **runtime ladder** — every available Lua runtime is asked to compile the
   input; runtimes that cannot (e.g. Lua 5.1 and the ``control structure too
   long`` parser limit on large WRD files) are reported and skipped.
2. **policy ladder** — the environment is rebuilt for each policy
   (``codex`` → ``strict`` → ``permissive``) because no single stub policy keeps
   every obfuscator alive.  Each attempt gets its own artifact directory.
3. **capture** — ``load``/``loadstring`` chunks, ``table.concat`` rebuilds,
   ``string.char`` fragments, global reads/writes and any URL/file access the
   script performs are written to disk and summarised in ``report.json``.

Everything the sandbox produces lands in ``logs/run_<timestamp>_<hash>/`` so that
attempts never overwrite each other and a failed run can still be inspected.
"""

from __future__ import annotations

import hashlib
import shutil
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, List, Optional, Sequence, Tuple

from . import paths
from .config import SandboxConfig
from .errors import SandboxError
from .runtime import LuaRuntime, RunOutcome, RuntimeSpec, runtime_ladder


@dataclass
class Attempt:
    """One (runtime, policy) execution."""

    policy: str
    runtime: RuntimeSpec
    outcome: RunOutcome
    workdir: Path
    dumps: List[Path] = field(default_factory=list)
    concats: List[Path] = field(default_factory=list)
    sandbox_files: List[Path] = field(default_factory=list)
    trace: Optional[Path] = None
    char_fragments: Optional[Path] = None

    @property
    def report(self) -> dict:
        return self.outcome.report

    @property
    def ran(self) -> bool:
        return self.outcome.ran

    @property
    def timed_out(self) -> bool:
        return self.outcome.timed_out

    @property
    def error(self) -> str:
        return self.outcome.run_error

    @property
    def progress(self) -> int:
        """Rough measure of how far the script got (used to pick the best run)."""
        stats = self.report.get("stats") or {}
        captures = self.report.get("captures") or []
        return (
            int(stats.get("loads") or 0) * 1000
            + int(stats.get("concats") or 0) * 10
            + int(stats.get("char_calls") or 0) // 100
            + len(captures)
            + int(self.report.get("instructions") or 0) // 1_000_000
        )

    def summary(self) -> str:
        stats = self.report.get("stats") or {}
        state = "timeout" if self.timed_out else ("ran" if self.ran else f"error: {self.error[:120]}")
        return (
            f"{self.runtime.name}/{self.policy}: {state}; "
            f"loads={stats.get('loads', 0)} concats={stats.get('concats', 0)} "
            f"chars={stats.get('char_calls', 0)}"
        )


@dataclass
class SandboxResult:
    """Aggregated outcome of a sandboxed deobfuscation attempt."""

    source_hash: str
    source_path: Path
    workdir: Path
    attempts: List[Attempt] = field(default_factory=list)
    rejected_runtimes: List[Tuple[RuntimeSpec, str]] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    @property
    def best(self) -> Optional[Attempt]:
        if not self.attempts:
            return None
        return max(self.attempts, key=lambda a: a.progress)

    @property
    def any_loads(self) -> bool:
        return any(a.report.get("loads") for a in self.attempts)

    def all_dumps(self) -> List[Path]:
        out: List[Path] = []
        for attempt in self.attempts:
            out.extend(attempt.dumps)
        return out

    def all_candidates(self) -> List[Path]:
        """Every file that could contain a payload (loads + concats + sandbox files)."""
        out: List[Path] = []
        for attempt in self.attempts:
            out.extend(attempt.dumps)
            out.extend(attempt.concats)
            out.extend(attempt.sandbox_files)
        return out

    def as_dict(self) -> dict:
        return {
            "source_hash": self.source_hash,
            "source_path": str(self.source_path),
            "workdir": str(self.workdir),
            "attempts": [
                {
                    "policy": a.policy,
                    "runtime": a.runtime.as_dict(),
                    "ran": a.ran,
                    "timed_out": a.timed_out,
                    "error": a.error,
                    "progress": a.progress,
                    "summary": a.summary(),
                    "dumps": [str(p) for p in a.dumps],
                    "concats": [str(p) for p in a.concats],
                    "workdir": str(a.workdir),
                    "stats": a.report.get("stats") or {},
                    "loads": a.report.get("loads") or [],
                    "captures": a.report.get("captures") or [],
                    "missed_globals": (a.report.get("missed_globals") or [])[:20],
                    "notes": a.report.get("notes") or [],
                    "run_error": a.error,
                }
                for a in self.attempts
            ],
            "rejected_runtimes": [
                {"name": spec.name, "detail": spec.detail, "error": err[:300]} for spec, err in self.rejected_runtimes
            ],
            "notes": self.notes,
        }


class Sandbox:
    """Runs obfuscated Lua under a chosen engine and collects artifacts."""

    def __init__(self, config: Optional[SandboxConfig] = None, runner_path: Optional[Path] = None):
        self.config = config or SandboxConfig()
        self.runner_path = runner_path or (paths.core_dir() / "lua" / "runner.lua")

    # ------------------------------------------------------------------ public
    def run(
        self,
        source: str,
        source_name: str = "obfuscated",
        *,
        stop_when: Optional[Callable[[Attempt], bool]] = None,
        max_attempts: Optional[int] = None,
        prefer_exe: bool = False,
        workdir: Optional[Path] = None,
        encoding: str = "utf-8",
    ) -> SandboxResult:
        """Run ``source`` through the runtime/policy ladder.

        ``stop_when`` lets the caller stop the ladder as soon as an attempt
        produced something useful (typically: a payload candidate that already
        passes validation), which keeps the common case fast.
        """
        source_hash = hashlib.sha1(source.encode("utf-8", "replace")).hexdigest()
        stamp = time.strftime("%Y%m%d-%H%M%S")
        root = Path(workdir) if workdir else self.config.resolved_workdir()
        run_dir = paths.ensure_dir(root / f"run_{stamp}_{source_hash[:8]}")
        input_path = run_dir / "input.lua"
        input_path.write_bytes(source.encode(encoding, "replace"))

        result = SandboxResult(source_hash=source_hash, source_path=input_path, workdir=run_dir)

        try:
            usable, rejected = runtime_ladder(self.config.runtimes, source, prefer_exe=prefer_exe)
        except Exception as exc:  # RuntimeUnavailable and friends
            raise SandboxError(str(exc)) from exc

        result.rejected_runtimes = rejected
        if not usable:
            details = "; ".join(f"{spec.name}: {err[:80]}" for spec, err in rejected) or "no runtime found"
            result.notes.append("no runtime could compile the input: " + details)
            (run_dir / "last_run.txt").write_text(str(run_dir), encoding="utf-8")
            return result

        policies = list(self.config.policies)[: max(1, self.config.sample_runs)]
        attempts_left = self.config.max_attempts if max_attempts is None else max_attempts
        stop = False

        for runtime_spec in usable:
            if stop or attempts_left <= 0:
                break
            for policy in policies:
                if attempts_left <= 0:
                    break
                attempts_left -= 1
                attempt = self._run_single(source, source_name, runtime_spec, policy, run_dir, encoding=encoding)
                result.attempts.append(attempt)
                if stop_when and stop_when(attempt):
                    stop = True
                    break
                # A policy that timed out or died immediately is a poor base for
                # further ladder steps on the same runtime, but the next runtime
                # may behave differently - so only stop when we made progress.
                if attempt.progress == 0 and policy == policies[-1]:
                    break

        last = run_dir / "last_run.txt"
        last.write_text(str(run_dir), encoding="utf-8")
        return result

    # ----------------------------------------------------------------- internal
    def _run_single(
        self,
        source: str,
        source_name: str,
        runtime_spec: RuntimeSpec,
        policy: str,
        run_dir: Path,
        *,
        source_override: Optional[str] = None,
        mode: str = "run",
        encoding: str = "utf-8",
    ) -> Attempt:
        attempt_dir = paths.ensure_dir(run_dir / f"{runtime_spec.name}_{policy}")
        source_path = attempt_dir / "input.lua"
        payload = source_override if source_override is not None else source
        source_path.write_bytes(payload.encode(encoding, "replace"))

        config = {
            "base_dir": str(paths.core_dir() / "lua"),
            "logs_dir": str(attempt_dir),
            "source_path": str(source_path),
            "policy": policy,
            "mode": mode,
            "timeout": str(self.config.timeout),
            "max_instructions": str(self.config.max_instructions),
            "allow_unsafe": "1" if self.config.allow_unsafe else "0",
            "deterministic_random": "1" if self.config.deterministic_random else "0",
            "random_seed": str(self.config.random_seed),
            "engine": runtime_spec.kind,
            "hostname": source_name,
        }

        runtime = LuaRuntime(runtime_spec, runner_path=self.runner_path)
        outcome = runtime.run_runner(config, self.config)

        attempt = Attempt(policy=policy, runtime=runtime_spec, outcome=outcome, workdir=attempt_dir)
        attempt.dumps = sorted(attempt_dir.glob("dump_*.lua"))
        attempt.concats = sorted(attempt_dir.glob("concat_*.lua"))
        attempt.sandbox_files = sorted(attempt_dir.glob("sandbox_*.lua"))
        trace = attempt_dir / "trace.txt"
        if trace.exists():
            attempt.trace = trace
        charfrag = attempt_dir / "char_fragments.txt"
        if charfrag.exists():
            attempt.char_fragments = charfrag

        if not self.config.keep_artifacts and not attempt.dumps:
            shutil.rmtree(attempt_dir, ignore_errors=True)

        return attempt

    def trace_run(
        self,
        source: str,
        instrumented: str,
        attempt: Attempt,
        source_name: str = "obfuscated",
        mode: str = "trace",
        encoding: str = "utf-8",
    ) -> Attempt:
        """Re-run an instrumented source with the runtime/policy of ``attempt``."""
        run_dir = attempt.workdir.parent / f"trace_{attempt.workdir.name}"
        paths.ensure_dir(run_dir)
        return self._run_single(
            source,
            source_name,
            attempt.runtime,
            attempt.policy,
            run_dir,
            source_override=instrumented,
            mode=mode,
            encoding=encoding,
        )


__all__ = ["Attempt", "Sandbox", "SandboxResult"]
