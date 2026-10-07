"""Run one Lua file (a fixture loader or a recovered result) in the bounded emulator.

    python3 dev/emulate_file.py samples/real/wearedevs/0122989.lua --wall 20
    python3 dev/emulate_file.py logs/fixture-sweep/output/destroyed_12.lua --chunks

Prints the run status, the error if any, and what the run captured -- the same
`Real` executor surface the recovery pipeline uses.  Comparing the input file
with the recovered one says whether a recovery kept the loader's own behaviour.
"""
from __future__ import annotations

import argparse
import logging
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.emulator import LuaEmulator, run_bounded  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("file")
    parser.add_argument("--wall", type=float, default=20.0)
    parser.add_argument("--show", type=int, default=300)
    parser.add_argument("--chunks", action="store_true", help="list captured chunks")
    parser.add_argument("--profile", default=None, help="executor profile key")
    args = parser.parse_args()

    logging.basicConfig(level=logging.ERROR, format="[%(levelname)s] %(message)s")
    source = Path(args.file).read_text(encoding="latin-1")
    emulator = LuaEmulator(profile=args.profile, timeout_seconds=args.wall)
    result = run_bounded(emulator, source, wall_seconds=args.wall)
    print("file    : %s (%d bytes)" % (args.file, len(source)))
    print("runtime : %s" % result.runtime)
    print("status  : %s" % result.status)
    if result.error:
        print("error   : %s" % result.error[: args.show].replace("\n", " | "))
    print("captures: %d  requests: %d  downloads: %d  files: %d"
          % (len(result.captures), len(result.request_calls),
             len(result.downloaded_payloads), len(result.written_captures)))
    for chunk in result.source_chunks():
        print("  chunk  %-10s %7d bytes  %s" % (chunk.kind, len(chunk.text),
                                                chunk.text[:60].replace("\n", " ")))
    if args.chunks:
        for capture in result.captures:
            print("  cap    %-10s %7d bytes" % (capture.kind, len(capture.text)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
