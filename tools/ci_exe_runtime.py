"""CI helper: run the acceptance fixture through a standalone interpreter.

The exe runtime path (``lua/lua51.exe`` / a native twin) is a different code
path from lupa: the interpreter is a separate process, values are printed
instead of returned and the watchdog has to abort from inside Lua.  CI therefore
runs the acceptance fixture through it - and because Actions logs are awkward to
read from a script, any failure is also emitted as a ``::error`` annotation with
the pipeline summary, the sandbox attempts and the notes.

    python tools/ci_exe_runtime.py --runtime exe --out native_out.lua
    python tools/ci_exe_runtime.py --runtime exe --native lua/lua51 --json
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import PipelineConfig, SandboxConfig  # noqa: E402
from core.deobfuscate import deobfuscate_file  # noqa: E402

FIXTURE = ROOT / "tests" / "wrd_v1_0_0.lua"
CLEAN = ROOT / "tests" / "wrd_v1_0_0_clean.lua"


def _annotation(message: str) -> None:
    """Emit a workflow command so the reason shows up in the check annotations."""
    escaped = message.replace("%", "%25").replace("\r", "").replace("\n", "%0A")
    print(f"::error title=exe runtime::{escaped[:4000]}")


def summarise(result) -> str:
    lines: List[str] = []
    if result is None:
        return "the pipeline did not return a result"
    lines.append(f"success={result.success} partial={result.partial} method={result.method}")
    for stage in result.stages:
        lines.append(f"  [{stage.name}] ok={stage.ok} {stage.duration_ms}ms {stage.detail[:120]}")
    attempts = (result.sandbox or {}).get("attempts") or []
    for attempt in attempts:
        runtime = (attempt.get("runtime") or {}).get("name", "?")
        stats = attempt.get("stats") or {}
        lines.append(
            f"  attempt {runtime}/{attempt.get('policy')}: {attempt.get('summary') or 'no summary'}"
            f" loads={stats.get('loads')} concats={stats.get('concats')}"
            f" error={str(attempt.get('error'))[:80]}"
        )
    if not attempts:
        lines.append("  no sandbox attempt was made")
    for note in result.notes[:6]:
        lines.append(f"  note: {note[:160]}")
    return "\n".join(lines)


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--runtime", choices=("auto", "exe", "lupa"), default="exe")
    parser.add_argument("--out", metavar="PATH", help="write the recovered source here")
    parser.add_argument("--native", metavar="PATH",
                        help="build a native interpreter first (tools/build_lua.py --native)")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    if args.native:
        code = os.spawnv(os.P_WAIT, sys.executable,
                         [sys.executable, str(ROOT / "tools" / "build_lua.py"), "--native", args.native])
        if code != 0:
            _annotation(f"python tools/build_lua.py --native {args.native} failed with {code}")
            return 1

    prefer_exe = {"auto": None, "exe": True, "lupa": False}[args.runtime]
    config = PipelineConfig(
        sandbox=SandboxConfig(timeout=30, sample_runs=2, max_attempts=4, prefer_exe=prefer_exe),
    )

    result = None
    try:
        result = deobfuscate_file(FIXTURE, config=config)
    except Exception as exc:  # the CLI must never crash - report and fail cleanly
        _annotation(f"the pipeline raised {type(exc).__name__}: {exc}")
        return 1

    summary = summarise(result)
    print(summary)
    if args.out:
        Path(args.out).write_text(result.output or "", encoding="utf-8")

    expected = CLEAN.read_text(encoding="utf-8")
    identical = (result.output or "") == expected
    if args.out:
        identical = identical and Path(args.out).read_text(encoding="utf-8") == expected

    payload = {
        "runtime": args.runtime,
        "identical": identical,
        "success": bool(result.success),
        "partial": bool(result.partial),
        "method": result.method,
        "attempts": len((result.sandbox or {}).get("attempts") or []),
    }
    if args.json:
        print(json.dumps(payload, indent=2))

    if not identical:
        _annotation(f"the recovered source is not the clean fixture\n{summary}")
        return 1
    if args.runtime == "exe":
        attempts = (result.sandbox or {}).get("attempts") or []
        kinds = {(a.get("runtime") or {}).get("kind") for a in attempts}
        if "exe" not in kinds:
            _annotation(f"the exe runtime was requested but lupa ran instead: {sorted(kinds)}\n{summary}")
            return 1
    print(f"exe runtime ({args.runtime}): byte identical = True")
    return 0


if __name__ == "__main__":
    sys.exit(main())
