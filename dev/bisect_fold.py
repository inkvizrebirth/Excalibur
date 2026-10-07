"""Find the single constant fold that breaks a loader at run time.

    python3 dev/bisect_fold.py samples/real/wearedevs/0122989.lua

Applies the static pass' edits one at a time and runs the result in the bounded
emulator after each prefix, so the edit that first changes behaviour is
reported with the source context that surrounds it.  Needed because a fold can
be numerically right and still wrong for Lua's value semantics (`m and A or B`).
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

import core.deobfuscator as D  # noqa: E402

CHILD = """
import sys
sys.path.insert(0, {repo!r})
from pathlib import Path
import core.deobfuscator as D
src = Path({sample!r}).read_text(encoding="latin-1")
cur, *_ = D._rewrite_once(src)
Path({out!r}).write_text(cur, encoding="utf-8")
"""


def edits_for(source: str) -> list[tuple[int, int, str, str]]:
    """The edits `_rewrite_once` would apply, in source order."""
    tokens = D.tokenize(source)
    bindings, paths = D._collect_local_constants(source, tokens)
    if paths is None:
        paths = [()] * len(tokens)
    bindings.sort(key=lambda b: b.available_from)
    active_bindings: dict = {}
    active_environment: dict = {}
    next_binding = 0
    edits: list[tuple[int, int, str, str]] = []
    index = 0
    while index < len(tokens):
        scope = paths[index]
        for name, binding in tuple(active_bindings.items()):
            if scope[: len(binding.scope_path)] != binding.scope_path:
                del active_bindings[name]
                active_environment.pop(name, None)
        while next_binding < len(bindings) and bindings[next_binding].available_from <= index:
            binding = bindings[next_binding]
            if scope[: len(binding.scope_path)] == binding.scope_path:
                active_bindings[binding.name] = binding
                active_environment[binding.name] = binding.value
            next_binding += 1
        token = tokens[index]
        if token.kind == "comment":
            index += 1
            continue
        if token.text in {"+", "-", "~", "#"} and not D._unary_operator_allowed(tokens, index):
            index += 1
            continue
        if token.kind == "identifier" and D._is_property_or_table_key(tokens, index):
            index += 1
            continue
        if token.text == "(":
            previous = D._previous_code_index(tokens, index)
            if previous >= 0 and (tokens[previous].kind in {"identifier", "number", "string"}
                                  or tokens[previous].text in {")", "]", "}"}):
                index += 1
                continue
        parser = D._ExpressionParser(tokens, index, active_environment)
        value, end = parser.parse()
        if (value is not D._UNKNOWN and end > index
                and D._span_is_complete_expression(tokens, index, end)
                and D._fold_fits_context(tokens, index, end)):
            rendered = D._render_value(value)
            if rendered is not None:
                first, last = tokens[index], tokens[end - 1]
                old = source[first.start:last.end]
                literal = token.kind == "string" and end == index + 1
                local_ref = token.kind == "identifier" and token.text in active_environment
                if (end > index + 1 or literal or local_ref) and old != rendered:
                    edits.append((first.start, last.end, old, rendered))
                    index = end
                    continue
        index += 1
    return edits


def apply_prefix(source: str, edits: list[tuple[int, int, str, str]], count: int) -> str:
    """Apply the first `count` edits the way the pass does, glue repair included."""
    out = source
    for start, end, _old, rendered in reversed(edits[:count]):
        replacement = D._prepare_replacement(source, start, end, rendered)
        out = out[:start] + replacement + out[end:]
    return out


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("sample")
    parser.add_argument("--wall", type=float, default=8.0)
    parser.add_argument("--out", default="/tmp/bisect_fold.lua")
    args = parser.parse_args()

    sample = Path(args.sample)
    source = sample.read_text(encoding="latin-1")
    edits = edits_for(source)
    print("%d edits" % len(edits))

    def fails(count: int) -> bool:
        Path(args.out).write_text(apply_prefix(source, edits, count), encoding="utf-8")
        run = subprocess.run([sys.executable, "dev/emulate_file.py", args.out, "--wall", str(args.wall)],
                             cwd=str(REPO_ROOT), capture_output=True, text=True)
        return "status  : error" in run.stdout

    if not fails(len(edits)):
        print("no edit breaks this file")
        return 0
    low, high = 0, len(edits)
    while low + 1 < high:
        mid = (low + high) // 2
        if fails(mid):
            high = mid
        else:
            low = mid
    start, end, old, rendered = edits[high - 1]
    print("first breaking edit is #%d of %d" % (high, len(edits)))
    print("  old: %r" % old[:200])
    print("  new: %r" % rendered[:200])
    print("  context: %r" % source[max(0, start - 80):end + 80])
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
