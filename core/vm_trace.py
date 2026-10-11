"""Fallback stage: instrument the obfuscator's dispatch loop and trace it.

WRD v1.0.0 compiles the original script into a **control flow flattened state
machine**::

    while i do
      if i < 8182939 then
        if i < 3950221 then ... else ... end
      else ...
      end
    end

Neither a ``loadstring`` hook nor a ``table.concat`` hook can see the original
text, because it never exists as text: it is *interpreted*.  What can be observed
is the sequence of states the machine visits, which is exactly what this module
captures:

1. :func:`instrument_dispatch` inserts ``__sandbox_trace_state(<state>)`` calls at
   the head of the dispatch loop(s).  The call is cheap, bounded and writes only
   to ``logs/.../trace.txt``.
2. The instrumented source is executed by :class:`core.sandbox.Sandbox` in
   ``trace`` mode.
3. :func:`summarize_trace` turns the raw state list into a readable summary
   (distinct states, transition list, detected cycles, hottest states) that a
   human - or a future devirtualiser - can work from.

This is a *diagnostic* fallback by design; the report never claims that the
trace alone reconstructs the original source.
"""

from __future__ import annotations

import re
from collections import Counter
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Sequence, Tuple

from .wrd_detect import mask_lua

WHILE_RE = re.compile(r"while\s+([A-Za-z_]\w*)\s+do")
TRACE_CALL = "__sandbox_trace_state"


@dataclass
class TracePlan:
    """Result of instrumenting a source for tracing."""

    instrumented: str
    loops: int = 0
    injections: int = 0
    variables: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "loops": self.loops,
            "injections": self.injections,
            "variables": self.variables,
            "notes": self.notes,
        }


def _loop_score(mask: str, body_start: int) -> int:
    """Heuristic: the dispatch loop is the one full of ``if`` statements."""
    window = mask[body_start : body_start + 20000]
    return window.count("if ") + window.count("elseif") * 2


def instrument_dispatch(source: str, *, max_loops: int = 3, window: int = 40) -> TracePlan:
    """Insert state tracing calls into the most dispatch-like ``while`` loops."""
    # Prefer the loop the lift will analyse (the one whose body is the state
    # dispatch tree); fall back to the "most if statements" heuristic.
    try:
        from .lift import find_dispatcher

        found = find_dispatcher(source)
    except Exception:  # pragma: no cover - lift is optional
        found = None
    if found is not None:
        position = found["body_char_span"][0]
        return TracePlan(
            instrumented=source[:position] + f" {TRACE_CALL}({found['variable']}) " + source[position:],
            loops=1,
            injections=1,
            variables=[found["variable"]],
            notes=[f"instrumented the state dispatch loop on '{found['variable']}' "
                   f"({found['pivots']} state pivots) at offset {position}"],
        )

    mask = mask_lua(source)
    candidates: List[Tuple[int, int, str]] = []
    for match in WHILE_RE.finditer(mask):
        do_end = match.end()
        score = _loop_score(mask, do_end)
        if score < 4:
            continue
        candidates.append((score, do_end, match.group(1)))

    candidates.sort(reverse=True)
    selected = candidates[:max_loops]
    if not selected:
        return TracePlan(instrumented=source, notes=["no dispatch-like while loop found"])

    edits: List[Tuple[int, str]] = []
    variables: List[str] = []
    for _score, position, variable in selected:
        edits.append((position, f" {TRACE_CALL}({variable}) "))
        variables.append(variable)

    edits.sort()
    parts: List[str] = []
    cursor = 0
    for position, text in edits:
        parts.append(source[cursor:position])
        parts.append(text)
        cursor = position
    parts.append(source[cursor:])
    instrumented = "".join(parts)

    return TracePlan(
        instrumented=instrumented,
        loops=len(selected),
        injections=len(edits),
        variables=variables,
        notes=[f"instrumented {len(edits)} dispatch loop(s) on " + ", ".join(sorted(set(variables)))],
    )


def read_trace(path: str | Path) -> List[str]:
    """Read a trace file produced by the runner."""
    file_path = Path(path)
    if not file_path.exists():
        return []
    return [line.strip() for line in file_path.read_text(encoding="utf-8", errors="replace").splitlines() if line.strip()]


def summarize_trace(states: Sequence[str], *, top: int = 12, sequence: int = 60) -> Dict[str, object]:
    """Turn a raw state list into statistics and a readable transition list."""
    summary: Dict[str, object] = {
        "states": len(states),
        "distinct": len(set(states)),
    }
    if not states:
        return summary

    counts = Counter(states)
    summary["top_states"] = [{"state": s, "count": c} for s, c in counts.most_common(top)]
    summary["sequence_head"] = list(states[:sequence])
    summary["sequence_tail"] = list(states[-sequence:]) if len(states) > sequence else []

    transitions: List[Tuple[str, str]] = []
    for previous, current in zip(states, states[1:]):
        if previous != current:
            transitions.append((previous, current))
    summary["transitions"] = len(transitions)

    pair_counts = Counter(transitions)
    summary["top_transitions"] = [{"from": a, "to": b, "count": c} for (a, b), c in pair_counts.most_common(top)]

    # cycle detection: repeated short cycles in the visited state sequence
    cycles: List[Dict[str, object]] = []
    max_period = 8
    for period in range(2, max_period + 1):
        repeats = 0
        limit = min(len(states) - period * 2, 4000)
        index = 0
        while index < limit:
            if states[index] == states[index + period] == states[index + 2 * period]:
                repeats += 1
                index += period
            index += 1
        if repeats >= 3:
            cycles.append({"period": period, "occurrences": repeats})
    summary["cycles"] = cycles
    return summary


def render_summary(summary: Dict[str, object], *, title: str = "Excalibur trace summary") -> str:
    """Human readable trace summary written next to the dumps."""
    lines: List[str] = [title, "=" * len(title), ""]
    lines.append(f"recorded states   : {summary.get('states', 0)}")
    lines.append(f"distinct states   : {summary.get('distinct', 0)}")
    lines.append(f"transitions       : {summary.get('transitions', 0)}")
    top_states = summary.get("top_states") or []
    if top_states:
        lines.append("")
        lines.append("hottest states:")
        for row in top_states:
            lines.append(f"  {row['state']:>22}  x{row['count']}")
    transitions = summary.get("top_transitions") or []
    if transitions:
        lines.append("")
        lines.append("most frequent transitions:")
        for row in transitions:
            lines.append(f"  {row['from']:>22} -> {row['to']:<22} x{row['count']}")
    cycles = summary.get("cycles") or []
    if cycles:
        lines.append("")
        lines.append("detected cycles:")
        for row in cycles:
            lines.append(f"  period {row['period']} seen {row['occurrences']}x")
    head = summary.get("sequence_head") or []
    if head:
        lines.append("")
        lines.append("state sequence (head):")
        lines.append("  " + " ".join(str(s) for s in head))
    tail = summary.get("sequence_tail") or []
    if tail:
        lines.append("")
        lines.append("state sequence (tail):")
        lines.append("  " + " ".join(str(s) for s in tail))
    lines.append("")
    lines.append(
        "NOTE: WRD v1.0.0 executes the payload inside this state machine, so a trace "
        "does not contain the original source text.  The summary above is the input "
        "for devirtualisation (see docs/ROADMAP.md)."
    )
    return "\n".join(lines) + "\n"


__all__ = [
    "TRACE_CALL",
    "TracePlan",
    "instrument_dispatch",
    "read_trace",
    "render_summary",
    "summarize_trace",
]
