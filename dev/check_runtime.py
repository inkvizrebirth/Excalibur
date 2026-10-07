"""Run every recovered script and report what happens at run time.

Readability is not the whole bar: a result can be formatted, syntax-valid and
still die on its first line because a placeholder took the place of a value the
lifter could not recover, or because the payload expects a handshake the
executor surface does not answer.  This checker runs each recovered file in the
bounded emulator (the same `Real` executor surface the recovery itself uses) and
prints the outcome, so per-family runtime fidelity is measurable instead of
anecdotal.

    python3 dev/check_runtime.py                        # newest result per fixture
    python3 dev/check_runtime.py --file output/destroyed_1.lua
    python3 dev/check_runtime.py --wall 30 --show 400
"""
from __future__ import annotations

import argparse
import json
import logging
import re
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.emulator import LuaEmulator, run_bounded  # noqa: E402

DEFAULT_DIRS = (REPO_ROOT / "logs" / "fixture-sweep" / "reports",)


def _newest_results(dirs: tuple[Path, ...]) -> list[tuple[str, str, Path]]:
    """(source label, route, result file) one per fixture, newest run first.

    The report names its own output, which is the file the application would
    hand a user (a single ``destroyed_N.lua``), so the checker runs exactly what
    the pipeline produced instead of guessing file names.
    """
    newest: dict[str, tuple[float, str, str, Path, dict]] = {}
    for directory in dirs:
        for report in directory.glob("report_*.json"):
            try:
                data = json.loads(report.read_text(encoding="utf-8"))
            except (OSError, ValueError):
                continue
            output = data.get("output_path")
            if not output:
                continue
            path = Path(output)
            if not path.is_file():
                continue
            key = str(data.get("source_name") or path.name)
            stamp = report.stat().st_mtime
            if key not in newest or stamp > newest[key][0]:
                newest[key] = (stamp, key, str(data.get("route") or ""), path, data)
    return [(key, route, path, data) for _, key, route, path, data in
            sorted(newest.values(), key=lambda item: item[1])]


def _signature(error: object) -> str:
    """First line of an error, whitespace collapsed: its identity, not a traceback."""
    text = re.sub(r"\s+", " ", str(error or "")).strip()
    return text.split(" stack traceback:")[0][:120]


def _verdict(baseline_status: str, baseline_error: object,
             status: str, error: object) -> str:
    """How the result behaves next to its own input.

    ``limit`` is not a failure: several loaders do not finish inside a bounded
    emulator on their own either.  What matters is that the result is not worse
    than the file it came from.
    """
    rank = {"completed": 0, "ok": 0, "success": 0, "limit": 1, "timeout": 1,
            "error": 2, "unavailable": 2, "checker-error": 3}
    left = rank.get(baseline_status, 2)
    right = rank.get(status, 2)
    if right > left:
        return "WORSE"
    if right < left:
        return "better"
    if left >= 1 and _signature(error) != _signature(baseline_error):
        return "differs"
    return "same"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--dir", action="append", default=[], help="directory with results")
    parser.add_argument("--file", action="append", default=[], help="one result file")
    parser.add_argument("--wall", type=float, default=20.0, help="seconds per run")
    parser.add_argument("--show", type=int, default=200, help="characters of the error to print")
    parser.add_argument("--quiet", action="store_true", help="only failures")
    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR, format="[%(levelname)s] %(message)s")
    directories = tuple(Path(d) for d in args.dir) or DEFAULT_DIRS
    entries = ([(f, "", Path(f), {}) for f in args.file]
               or _newest_results(directories))
    if not entries:
        print("no recovered results found in %s" % ", ".join(str(d) for d in directories))
        return 2

    failures = 0
    for label, route, path, report in entries:
        source = path.read_text(encoding="utf-8", errors="replace")
        emulator = LuaEmulator(profile=None, timeout_seconds=args.wall)
        started = time.monotonic()
        try:
            result = run_bounded(emulator, source, wall_seconds=args.wall)
            status, error = result.status, result.error
            chunks = len(result.source_chunks())
        except Exception as exc:  # noqa: BLE001 - a checker reports, never crashes
            status, error, chunks = "checker-error", f"{type(exc).__name__}: {exc}", 0
        elapsed = time.monotonic() - started
        baseline = report.get("emulator") if isinstance(report, dict) else None
        baseline = baseline if isinstance(baseline, dict) else {}
        base_status = str(baseline.get("status") or "unknown")
        verdict = _verdict(base_status, baseline.get("error"), status, error)
        bad = verdict == "WORSE"
        failures += 1 if bad else 0
        if args.quiet and not bad:
            continue
        head = re.sub(r"\s+", " ", (error or "")).strip()[: args.show]
        print("%-26s %-24s input=%-9s result=%-9s %-7s %5.1fs chunks=%d %s%s"
              % (label[:26], route[:24], base_status, status, verdict, elapsed, chunks,
                 "error=" if head else "", head))
    print("%d fixture(s): %d worse than its input" % (len(entries), failures))
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
