"""Prometheus devirtualizer: control-flow flattening removal.

Prometheus (and the flattening pass several other packers copied from it) walks
a function through a state machine::

    local v = 1
    while true do
        if v == 1 then
            print("real work")
            v = 2
        elseif v == 2 then
            print("more work")
            v = 3
        else
            break
        end
    end

Every statement is still there -- only the order is hidden behind comparisons
and ``state = n`` assignments.  This module reads the dispatcher, follows the
state graph from its entry value and writes the blocks back out as ordinary
straight-line code (wrapped in ``repeat ... until true`` when the original used
``break`` to leave the dispatcher, so the emitted code stays valid).

The transformation is deliberately conservative: a flattened function is
rewritten only when the state graph is *complete* -- every branch is reachable
by following literal ``state = n`` transitions, and no branch computes its next
state at runtime.  Anything less returns ``None``, because a half-linearised
function would be wrong rather than merely partial.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Sequence

from core.deobfuscator import Token, tokenize

__all__ = ["devirtualize", "deflatten", "lua_blocks_balanced"]

_MAX_BRANCHES = 400
_TERMINAL = re.compile(r"(?:^|[\s;(])(?:break|return|error|goto)(?:[\s;(]|$)")


@dataclass(frozen=True)
class _Branch:
    state: int
    body_start: int
    body_end: int
    target: int | None
    has_assignment: bool
    dynamic: bool


def _match_block(tokens: Sequence[Token], start: int) -> int:
    """Index of the ``end``/``until`` closing the block opened at ``start``."""
    depth = 0
    skip_do = False
    index = start
    while index < len(tokens):
        text = tokens[index].text
        if text in ("while", "for"):
            depth += 1
            skip_do = True
        elif text == "do":
            if skip_do:
                skip_do = False
            else:
                depth += 1
        elif text in ("if", "function", "repeat"):
            depth += 1
        elif text in ("end", "until"):
            depth -= 1
            if depth <= 0:
                return index
        index += 1
    return len(tokens) - 1


def _comparisons(tokens: Sequence[Token], name: str) -> int:
    count = 0
    for index in range(len(tokens) - 2):
        if tokens[index].kind == "identifier" and tokens[index].text == name:
            if tokens[index + 1].text in ("==", "~=") and tokens[index + 2].kind == "number":
                count += 1
        elif (
            tokens[index].kind == "number"
            and tokens[index + 1].text in ("==", "~=")
            and tokens[index + 2].kind == "identifier"
            and tokens[index + 2].text == name
        ):
            count += 1
    return count


def _state_candidates(tokens: Sequence[Token]) -> list[str]:
    """Variable names compared against numbers at least twice."""
    names: list[str] = []
    for token in tokens:
        if token.kind != "identifier" or token.text in names:
            continue
        if _comparisons(tokens, token.text) >= 2:
            names.append(token.text)
    return names


def _loop_for(tokens: Sequence[Token], name: str) -> tuple[int, int] | None:
    """The ``while`` loop whose body compares ``name`` the most."""
    best: tuple[int, int, int] | None = None
    for index, token in enumerate(tokens):
        if token.text != "while":
            continue
        end = _match_block(tokens, index)
        inside = _comparisons(tokens[index : end + 1], name)
        if inside < 2:
            continue
        span = end - index
        if best is None or (inside, -span) > (best[0], -best[1]):
            best = (inside, span, index)
    if best is None:
        return None
    index = best[2]
    return index, _match_block(tokens, index)


def _head_state(tokens: Sequence[Token], index: int, name: str) -> int | None:
    probe = index + 1
    if probe + 2 < len(tokens) and tokens[probe].text == name and tokens[probe + 1].text in ("==", "~="):
        number = tokens[probe + 2]
        if number.kind == "number":
            try:
                return int(float(number.text))
            except ValueError:
                return None
    return None


def _clauses(
    tokens: Sequence[Token],
    chain_start: int,
    chain_end: int,
    name: str,
) -> list[tuple[int | None, int, int, bool]]:
    """Split an if/elseif/else chain into ``(state, body_start, body_end, is_else)``."""
    clauses: list[tuple[int | None, int, int, bool]] = []
    depth = 0
    skip_do = False
    first = True
    head: int | None = None
    body_start = chain_start
    index = chain_start
    while index < chain_end:
        text = tokens[index].text
        if text in ("if", "elseif") and depth == (0 if first else 1):
            if not first:
                clauses.append((head, body_start, index, head is None))
            head = _head_state(tokens, index, name)
            probe = index + 1
            while probe < chain_end and tokens[probe].text != "then":
                probe += 1
            body_start = probe + 1
            first = False
        elif text == "else" and depth == 1:
            clauses.append((head, body_start, index, head is None))
            head = None
            body_start = index + 1
        if text in ("while", "for"):
            depth += 1
            skip_do = True
        elif text == "do":
            if skip_do:
                skip_do = False
            else:
                depth += 1
        elif text in ("if", "function", "repeat"):
            depth += 1
        elif text in ("end", "until"):
            depth -= 1
        index += 1
    clauses.append((head, body_start, chain_end, head is None))
    return clauses


def _branch_assignment(
    tokens: Sequence[Token], start: int, end: int, name: str
) -> tuple[int | None, bool, bool]:
    """``(literal target, saw an assignment, the assignment was not literal)``.

    Only assignments at the branch's own level count: one hidden inside a
    nested ``if``/loop only runs sometimes, so the next state is
    runtime-dependent and the branch is flagged as dynamic.
    """
    target: int | None = None
    seen = False
    dynamic = False
    depth = 0
    skip_do = False
    index = start
    while index < max(start, end - 2):
        text = tokens[index].text
        if text in ("while", "for"):
            depth += 1
            skip_do = True
        elif text == "do":
            if skip_do:
                skip_do = False
            else:
                depth += 1
        elif text in ("if", "function", "repeat"):
            depth += 1
        elif text in ("end", "until"):
            depth -= 1
        elif (
            text == name
            and tokens[index].kind == "identifier"
            and tokens[index + 1].text == "="
        ):
            number = tokens[index + 2]
            literal = False
            if number.kind == "number":
                try:
                    value = int(float(number.text))
                    literal = True
                except ValueError:
                    literal = False
            if depth > 0:
                # Conditional assignment: the branch can end somewhere else.
                dynamic = True
            elif literal:
                seen = True
                target = value
            else:
                seen = True
                dynamic = True
        index += 1
    return target, seen, dynamic


def _entry_state(
    source: str, tokens: Sequence[Token], name: str, loop_start: int
) -> tuple[int | None, int, int]:
    """``(entry_state, cut_start, cut_end)`` for the ``local state = n`` before the loop."""
    assignment = re.compile(
        rf"(?m)^[ \t]*(?:local[ \t]+)?{re.escape(name)}[ \t]*=[ \t]*(\d+)[ \t]*;?[ \t]*\n?"
    )
    best: tuple[int, int, int] | None = None
    offset = tokens[loop_start].start
    for match in assignment.finditer(source[:offset]):
        best = (int(match.group(1)), match.start(), match.end())
    if best is None:
        return None, offset, offset
    return best[0], best[1], offset


def _reindent(raw: str, base_indent: str) -> str:
    """Trim the block to its own indentation and re-indent it like the loop."""
    lines = raw.splitlines()
    while lines and not lines[0].strip():
        lines.pop(0)
    while lines and not lines[-1].strip():
        lines.pop()
    if not lines:
        return ""
    indents = [len(line) - len(line.lstrip()) for line in lines if line.strip()]
    common = min(indents) if indents else 0
    rendered: list[str] = []
    for line in lines:
        rendered.append(base_indent + line[common:].rstrip() if line.strip() else "")
    return "\n".join(rendered)


def _strip_transitions(body: str, name: str) -> str:
    """Remove the dispatcher assignments from an emitted block."""
    lines = []
    pattern = re.compile(rf"^[ \t]*(?:{re.escape(name)}[ \t]*=[ \t]*[^=\n]+)[ \t]*;?[ \t]*$")
    inline = re.compile(
        rf"(?m)^(?P<head>[ \t]*(?:local[ \t]+)?[^\n]*?)[ \t]*;[ \t]*{re.escape(name)}[ \t]*=[^=\n]+$"
    )
    for line in body.splitlines():
        if pattern.match(line):
            continue
        lines.append(inline.sub(lambda match: match.group("head"), line))
    return "\n".join(lines)


def lua_blocks_balanced(text: str) -> bool:
    """Cheap structural check: every ``if/while/for/function/do`` block is closed."""
    depth = 0
    skip_do = False
    for token in tokenize(text):
        name = token.text
        if name in ("while", "for"):
            depth += 1
            skip_do = True
        elif name == "do":
            if skip_do:
                skip_do = False
            else:
                depth += 1
        elif name in ("if", "function", "repeat"):
            depth += 1
        elif name in ("end", "until"):
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def deflatten(source: str) -> dict[str, object] | None:
    """Remove a Prometheus-style dispatcher, or return ``None``."""
    tokens = tokenize(source)
    if not tokens:
        return None
    for name in _state_candidates(tokens):
        loop = _loop_for(tokens, name)
        if loop is None:
            continue
        loop_start, loop_end = loop
        body_start = loop_start + 1
        while body_start < loop_end and tokens[body_start].text != "do":
            body_start += 1
        chain_start = None
        depth = 0
        skip_do = False
        index = body_start + 1
        while index < loop_end:
            text = tokens[index].text
            if depth == 0 and text == "if" and _head_state(tokens, index, name) is not None:
                chain_start = index
                break
            if text in ("while", "for"):
                depth += 1
                skip_do = True
            elif text == "do":
                if skip_do:
                    skip_do = False
                else:
                    depth += 1
            elif text in ("if", "function", "repeat"):
                depth += 1
            elif text in ("end", "until"):
                depth -= 1
            index += 1
        if chain_start is None:
            continue
        chain_end = _match_block(tokens, chain_start)
        branches: dict[int, _Branch] = {}
        else_blocks = 0
        for state, start, end, is_else in _clauses(tokens, chain_start, chain_end, name):
            if is_else or state is None:
                if is_else and start < end:
                    else_blocks += 1
                continue
            if start >= end:
                continue
            target, _seen, dynamic = _branch_assignment(tokens, start, end, name)
            branches[state] = _Branch(
                state=state,
                body_start=tokens[start].start,
                body_end=tokens[end - 1].end,
                target=target,
                has_assignment=_seen,
                dynamic=dynamic,
            )
            if len(branches) >= _MAX_BRANCHES:
                break
        if len(branches) < 2:
            continue

        entry, cut_start, cut_end = _entry_state(source, tokens, name, loop_start)
        entry_guessed = entry is None or entry not in branches
        if entry is None or entry not in branches:
            entry = next(iter(sorted(branches)))
        order: list[_Branch] = []
        seen: set[int] = set()
        state: int | None = entry
        cycle = False
        while state is not None and state in branches:
            if state in seen:
                cycle = True
                break
            branch = branches[state]
            seen.add(state)
            order.append(branch)
            state = branch.target

        # Only a complete, statically-followable state graph may be rewritten:
        # a partially emitted function -- or one that loops back through the
        # dispatcher -- would silently change behaviour.
        if cycle or len(order) != len(branches):
            continue
        safe = True
        for position, branch in enumerate(order):
            if position != len(order) - 1:
                if branch.dynamic:
                    # A branch that computes its next state may jump anywhere:
                    # the order we would emit is a guess.
                    safe = False
                    break
                continue
            raw_tail = source[branch.body_start : branch.body_end]
            terminal = bool(_TERMINAL.search(raw_tail))
            if terminal:
                continue
            if branch.has_assignment and not branch.dynamic:
                # The last block hands over to a state outside the chain: that
                # value is what the loop condition (or the fallback branch)
                # exits on, so the dispatcher can go.
                if branch.target in branches:
                    safe = False
                break
            # No terminal statement and no exit value: the original could run
            # more than once, so its order is not known.
            safe = False
            break
        if not safe:
            continue

        base_indent = re.match(
            r"[ \t]*", source[source.rfind("\n", 0, tokens[loop_start].start) + 1 :]
        ).group(0)
        blocks: list[str] = []
        used_repeat = False
        for branch in order:
            line_start = source.rfind("\n", 0, branch.body_start) + 1
            raw = source[line_start : branch.body_end]
            prefix = branch.body_start - line_start
            if prefix and raw[:prefix].strip():
                # The clause opened mid-line: keep only the statement itself.
                raw = raw[prefix:]
            block = _reindent(_strip_transitions(raw, name), base_indent)
            if not block.strip():
                continue
            if _TERMINAL.search(block):
                used_repeat = True
            blocks.append(block)
        if not blocks:
            continue

        total = len(branches) + else_blocks
        header = (
            f"{base_indent}-- Prometheus-style control-flow flattening removed by Protez: "
            f"traced {len(order)} of {total} state block(s)"
        )
        header += (
            f", entry state inferred as {entry}"
            if entry_guessed
            else f" from entry state {entry}"
        )
        if else_blocks:
            header += f"; {else_blocks} fallback branch(es) are exit-only"
        emitted = [header, ""]
        if used_repeat:
            emitted.append(f"{base_indent}repeat")
            emitted.extend(blocks)
            emitted.append(f"{base_indent}until true")
        else:
            emitted.extend(blocks)
        replacement = "\n".join(emitted) + "\n"
        rebuilt = source[:cut_start] + replacement + source[tokens[loop_end].end :]
        if not lua_blocks_balanced(rebuilt):
            continue
        return {
            "source": rebuilt,
            "blocks": len(order),
            "total": total,
            "entry": entry,
            "entry_guessed": entry_guessed,
            "used_repeat": used_repeat,
        }
    return None


def devirtualize(
    source: str,
    *,
    vm_tables: Sequence[object] | None = None,
    vm_analysis: object | None = None,
    family: str = "prometheus",
) -> dict[str, object] | None:
    """De-flatten Prometheus-style control flow; fall back to the table VM."""
    result = deflatten(source)
    if result is not None:
        notes = [
            f"removed a state-machine dispatcher: {int(result['blocks'])} block(s) re-ordered "
            f"into straight-line code"
        ]
        if result["entry_guessed"]:
            notes.append(
                f"the entry state was inferred as {result['entry']} (the script never assigned "
                "it in a plain statement before the loop)"
            )
        if result["used_repeat"]:
            notes.append(
                "the sequence is kept inside `repeat ... until true` because the original "
                "dispatcher used `break`"
            )
        return {
            "source": str(result["source"]),
            "bytecode": None,
            "method": "control-flow flattening removal",
            "notes": tuple(notes),
            "confidence": 0.7,
            "partial": False,
        }
    from core.devirt import table_vm

    return table_vm.devirtualize(
        source, vm_tables=vm_tables, vm_analysis=vm_analysis, family=family
    )
