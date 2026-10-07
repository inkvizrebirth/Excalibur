"""Check that every pipeline result is a readable, intact script.

The readability pass must never edit program text: it re-flows the recovered
source onto its own lines and nothing else.  This script proves that per result
by re-running the statement breaker over the body and comparing token streams
(comment-free text), which catches any accidental edit inside a string or
number.  It also flags results that are still a single wall of text.

Usage::

    python3 dev/check_readability.py                       # logs/fixture-sweep/output
    python3 dev/check_readability.py --output-dir output    # the app's own output dir
    python3 dev/check_readability.py --min-lines 20
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.formatter import break_statements, tokenize  # noqa: E402

#: Anything shorter than this is still a minified wall, not a readable script.
DEFAULT_MIN_LINES = 20
#: A single line longer than this is unreadable in any editor.
MAX_LINE_LENGTH = 2000


def _body(text: str) -> str:
    """Return the script part: drop Protez's comment header and any report block.

    Static-protection results carry their report in front of the wrapper preview;
    the report is written as Lua comments, and the ``WRAPPER SOURCE BELOW`` banner
    marks where the actual script starts.
    """
    banner = "-- WRAPPER SOURCE BELOW"
    if banner in text:
        text = text.split(banner, 1)[1].split("\n", 2)[-1]
        return text
    marker = "\n" + "=" * 72 + "\n"
    if marker in text:
        return text.split(marker, 1)[1]
    return text


def _tokens(text: str) -> str:
    return "".join(token.text for token in tokenize(text) if token.kind != "comment")


def _compiles(text: str) -> bool | str:
    """Parse with Lua 5.1, lowering Luau-only syntax first (Roblox scripts need it)."""
    try:
        from lupa import lua51
    except Exception:  # pragma: no cover - optional dependency
        return "skipped"

    def attempt(payload: str) -> bool:
        try:
            runtime = lua51.LuaRuntime(unpack_returned_tuples=True, encoding="latin-1")
            outcome = runtime.eval("loadstring")(payload)
        except Exception:
            return False
        if isinstance(outcome, tuple):
            return outcome[0] is not None
        return outcome is not None

    if attempt(text):
        return True
    try:
        from core.devirt.luau_normalize import normalize_luau

        return attempt(normalize_luau(text).source)
    except Exception:
        return False


def _code_lengths(text: str) -> list[int]:
    """Per-line length ignoring string literals: data blobs are not unreadable code."""
    strings = sorted(
        (token.start, token.end) for token in tokenize(text) if token.kind == "string"
    )
    lines = text.split("\n")
    lengths = [0] * len(lines)
    offset = 0
    for index, line in enumerate(lines):
        start, end = offset, offset + len(line)
        covered = 0
        for token_start, token_end in strings:
            if token_end <= start or token_start >= end:
                continue
            covered += min(token_end, end) - max(token_start, start)
        lengths[index] = max(0, len(line) - covered)
        offset = end + 1
    return lengths


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir",
        default=str(REPO_ROOT / "logs" / "fixture-sweep" / "output"),
        help="directory holding destroyed_N.lua results",
    )
    parser.add_argument("--min-lines", type=int, default=DEFAULT_MIN_LINES)
    parser.add_argument("--max-line", type=int, default=MAX_LINE_LENGTH)
    args = parser.parse_args()

    directory = Path(args.output_dir)
    paths = sorted(
        (path for path in directory.glob("destroyed_*.lua") if path.is_file()),
        key=lambda path: int("".join(c for c in path.stem.split("_")[1] if c.isdigit()) or 0),
    )
    if not paths:
        print(f"no destroyed_*.lua results in {directory}")
        return 1

    failures = 0
    print(f"{'result':30s} {'lines':>7s} {'code':>7s} {'blob':>8s} {'intact':>7s} {'lua51':>6s}")
    for path in paths:
        text = path.read_text(encoding="utf-8", errors="replace")
        body = _body(text)
        lines = body.count("\n") + 1
        code_lengths = _code_lengths(body)
        longest_code = max(code_lengths, default=0)
        longest_line = max((len(line) for line in body.splitlines()), default=0)
        try:
            again = break_statements(body)
            intact = _tokens(again) == _tokens(body)
        except Exception as exc:  # noqa: BLE001 - report, do not crash
            again, intact = "", f"error: {exc}"[:40]
        compiles = _compiles(body)
        problems = []
        if lines < args.min_lines:
            problems.append(f"only {lines} lines")
        if longest_code > args.max_line:
            problems.append(f"{longest_code} chars of code on one line")
        if intact is not True:
            problems.append(f"text changed ({intact})")
        if compiles is False:
            problems.append("does not parse as Lua/Luau")
        failures += bool(problems)
        print(
            "%-30s %7d %7d %8d %7s %6s %s"
            % (
                path.name,
                lines,
                longest_code,
                longest_line,
                "yes" if intact is True else "NO",
                {True: "ok", False: "fail", "skipped": "-"}[compiles],
                "; ".join(problems),
            )
        )
    print()
    print(f"{len(paths) - failures}/{len(paths)} readable, intact and parsable")
    return 1 if failures else 0


if __name__ == "__main__":
    raise SystemExit(main())
