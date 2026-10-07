#!/usr/bin/env python3
"""Run the local obfuscator fixtures through the portable backend and pipeline.

Every fixture runs in its own process with a hard timeout: obfuscated loaders
contain anti-tamper loops that ignore the instruction budget because they never
leave one Lua call, and one stuck fixture must not hide the others.

Usage::

    python3 dev/fixture_sweep.py --mode emulator --limit 25
    python3 dev/fixture_sweep.py --mode pipeline --limit 100
    python3 dev/fixture_sweep.py --mode both --only luraph,v15

The child process is this same file with ``--one``.
"""

from __future__ import annotations

import argparse
import logging
import subprocess
import sys
import time
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SAMPLES = REPO_ROOT / "samples" / "real"
sys.path.insert(0, str(REPO_ROOT))


def _fixtures(pattern: str | None) -> list[Path]:
    paths = sorted(SAMPLES.glob("*/*.lua"))
    if pattern:
        wanted = [piece.strip().lower() for piece in pattern.split(",") if piece.strip()]
        paths = [path for path in paths if any(piece in str(path).lower() for piece in wanted)]
    return paths


def _emulator(path: Path, limit: float) -> str:
    from core.emulator import LuaEmulator

    source = path.read_bytes().decode("latin-1")
    started = time.time()
    result = LuaEmulator(timeout_seconds=limit).run(source)
    kinds: dict[str, int] = {}
    for capture in result.captures:
        kinds[capture.kind] = kinds.get(capture.kind, 0) + len(capture.text)
    lines = [
        "status=%s %.1fs captures=%s vm_tables=%d" % (
            result.status, time.time() - started, kinds, len(result.vm_tables or ()))
    ]
    if result.error:
        lines.append("error: " + result.error.splitlines()[0][:150])
    for capture in result.captures[:2]:
        lines.append("capture %s %d %r" % (capture.kind, len(capture.text), capture.text[:80]))
    return "\n".join(lines)


def _pipeline(path: Path, limit: float) -> str:
    from core.pipeline import DeobfuscationPipeline

    out_dir = REPO_ROOT / "logs" / "fixture-sweep"
    pipeline = DeobfuscationPipeline(
        output_dir=out_dir / "output",
        logs_dir=out_dir / "reports",
        tools_dir=REPO_ROOT / "tools",
        allow_network=False,
        max_pipeline_seconds=limit,
    )
    started = time.time()
    source = path.read_bytes().decode("latin-1")
    result = pipeline.run(source, source_name=path.parent.name + "-" + path.stem[:12])
    text = ""
    if result.output_path.is_file():
        text = result.output_path.read_text(encoding="utf-8", errors="replace")
    lines = [
        "route=%s status=%s layers=%d %.1fs bytes=%d lines=%d" % (
            result.route, result.status, result.decoded_layers, time.time() - started,
            len(text), text.count("\n") + 1),
        "markers: game=%d GetService=%d function=%d" % (
            text.count("game"), text.count("GetService"), text.count("function")),
    ]
    if result.notice:
        lines.append("notice: " + str(result.notice)[:150])
    lines.append("head: " + repr(text[:160]))
    return "\n".join(lines)


def _run_one(path: Path, mode: str, limit: float) -> int:
    if mode == "emulator":
        print(_emulator(path, limit))
    else:
        print(_pipeline(path, limit))
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=("emulator", "pipeline", "both"), default="both")
    parser.add_argument("--limit", type=float, default=60.0, help="seconds per fixture")
    parser.add_argument("--only", default=None, help="comma-separated substring filter")
    parser.add_argument("--one", default=None, help=argparse.SUPPRESS)
    parser.add_argument("--one-mode", default="emulator", help=argparse.SUPPRESS)
    args = parser.parse_args()

    logging.basicConfig(level=logging.WARNING)
    if args.one:
        return _run_one(Path(args.one), args.one_mode, args.limit)

    modes = ("emulator", "pipeline") if args.mode == "both" else (args.mode,)
    for mode in modes:
        print("=== %s ===" % mode)
        for path in _fixtures(args.only):
            name = path.relative_to(SAMPLES)
            print("%-46s " % name, end="", flush=True)
            command = [sys.executable, __file__, "--one", str(path),
                       "--one-mode", mode, "--limit", str(args.limit)]
            try:
                completed = subprocess.run(
                    command, capture_output=True, text=True, timeout=args.limit * 1.5
                )
            except subprocess.TimeoutExpired:
                print("KILLED after %.0fs" % (args.limit * 1.5), flush=True)
                continue
            body = (completed.stdout or "").strip()
            if completed.returncode != 0 and not body:
                body = "no output (exit %d): %s" % (
                    completed.returncode, (completed.stderr or "").strip()[-200:])
            print(flush=True)
            for line in body.splitlines():
                print("    " + line, flush=True)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
