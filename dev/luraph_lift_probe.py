"""Lift one Luraph fixture on its own, for fast iteration on the lifter.

    /home/user/pyenv/bin/python dev/luraph_lift_probe.py <sample> [budget] [out]

Runs just ``devirtualize_luraph`` (no pipeline), writes the lifted Luau and
prints the statistics.  The pipeline path (routes, reports, output policy) is
``dev/fixture_sweep.py --one <sample> --one-mode pipeline``.
"""
from __future__ import annotations

import logging
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO))

from core.luraph_devirtualizer import LuraphDevirtualizationError, devirtualize_luraph  # noqa: E402


def main() -> int:
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    sample = Path(sys.argv[1])
    budget = float(sys.argv[2]) if len(sys.argv) > 2 else 120.0
    out = Path(sys.argv[3]) if len(sys.argv) > 3 else Path("/tmp/lift_out.lua")
    logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s", stream=sys.stderr)
    source = sample.read_bytes().decode("latin-1")
    started = time.monotonic()
    try:
        result = devirtualize_luraph(
            source,
            source_name=sample.name,
            tools_dir=REPO / "tools",
            logs_dir=REPO / "logs",
            timeout_seconds=budget,
            total_budget_seconds=budget,
            logger=logging.getLogger("probe"),
        )
    except LuraphDevirtualizationError as exc:
        print("FAILED: %s: %s" % (type(exc).__name__, exc))
        print("elapsed %.1fs" % (time.monotonic() - started))
        return 1
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(result.source, encoding="utf-8", newline="")
    print("route: %s" % result.route)
    print("lift_stats: %s" % (result.lift_stats,))
    print("partial_reasons: %s" % (list(result.incomplete_reasons) or None,))
    print("placeholders: %s" % (result.placeholder_counts,))
    print("constant_misses: %s" % (result.constant_misses,))
    print("source_bytes: %d" % len(result.source.encode("utf-8")))
    print("elapsed %.1fs" % (time.monotonic() - started))
    print("wrote %s %d lines" % (out, result.source.count("\n") + 1))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
