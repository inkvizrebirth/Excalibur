"""Partial lift: turn a flattened WRD payload into readable pseudo-source.

After the constant layer is rewritten, a WRD v1.0.0 file looks like this:

.. code-block:: lua

    return(function(u, e, S, c, q, l, M, W, g, f, U, n, z, s, K, H, F, Z, Y, D, o, b)
      W, H, D, f, n, b, K, U, g, z, o, F, Y, Z, s = {}, function(H, S, c, q)
        while H do
          if H < 8372406 then
            if H < 4902010 then
              ...
              if H < 206733 then
                x = "setmetatable"  t = nil  y = "__metatable"  J = b()  j = {}  z[J] = j
                H = u["FZwOKLq0r7v3"]            -- next state read from the environment
              else
                H = 1220793                       -- constant jump
              end
            else
              H = W and 13087885 or 7757212       -- conditional jump
            end
          end
        end
      end, ...
    end)(...)

The payload is *not* missing: it is right there, as ordinary Lua statements, but
the control flow is a binary search over state numbers (``while H do if H < ...``)
and the variables are single letters.  This module recovers:

* the dispatcher (the ``while`` whose body is the pivot chain) and its state
  variable,
* every state: the code that belongs to it, plus its successors,
* the **state graph** (constant jumps are resolved to the state that owns the
  target value, conditional jumps keep their condition, dynamic jumps say which
  register they read),
* an inventory of every closure (``function``) found in the states,
* a rename table that turns the frame's variables into ``v1, v2, v3, ...`` while
  keeping the original names in the legend.

The result is deliberately *pseudo*-source: jumps are rendered as comments next
to the real assignment, so the text stays close to the original and can be read,
diffed and searched.  :mod:`core.registry` never claims it is runnable code.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from .wrd_detect import mask_lua

#: Files larger than this are not lifted (the scan is O(n), but the output would
#: be unreadable and the report would balloon).
MAX_LIFT_CHARS = 4_000_000

LUA_KEYWORDS = frozenset(
    """and break do else elseif end false for function goto if in local nil not or
    repeat return then true until while""".split()
)

NAME_START = re.compile(r"[A-Za-z_]")
NAME_CHARS = re.compile(r"[A-Za-z0-9_]")
NUMBER_CHARS = re.compile(r"[0-9A-Za-z_.]")
PIVOT_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*<\s*([0-9]+)\s*$")
STATE_ASSIGN_RE = re.compile(r"^\s*[A-Za-z_]\w*\s*=")
COND_JUMP_RE = re.compile(
    r"^\s*([A-Za-z_]\w*)\s*and\s*(\d+)\s*or\s*(\d+)\s*$"
)
CONST_JUMP_RE = re.compile(r"^\s*(\d+)\s*$")
REG_COND_JUMP_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s+and\s+([A-Za-z_]\w*)\s+or\s+([A-Za-z_]\w*)\s*$")
REG_OR_JUMP_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s+or\s+([A-Za-z_]\w*)\s*$")
ENV_JUMP_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*([\.\[])\s*")
REG_JUMP_RE = re.compile(r"^\s*([A-Za-z_]\w*)\s*$")


# ---------------------------------------------------------------------- tokens
@dataclass(frozen=True)
class Token:
    """One lexical unit of a Lua file (strings/comments are single tokens)."""

    kind: str  # "name" | "number" | "string" | "punct" | "keyword" | "comment"
    text: str
    start: int
    end: int

    @property
    def is_code(self) -> bool:
        return self.kind not in ("string", "comment")


def _comment_mask(source: str) -> str:
    """Blank *comments* only (strings stay visible as text)."""
    out = list(source)
    length = len(source)
    index = 0
    while index < length:
        if source.startswith("--", index):
            cursor = index + 2
            long_open = re.match(r"\[(=*)\[", source[cursor:])
            if long_open:
                close = "]" + long_open.group(1) + "]"
                end = source.find(close, cursor + long_open.end())
                end = length if end < 0 else end + len(close)
            else:
                end = source.find("\n", cursor)
                end = length if end < 0 else end
            for position in range(index, end):
                if source[position] != "\n":
                    out[position] = " "
            index = end
            continue
        index += 1
    return "".join(out)


def tokenize(source: str, mask: str) -> List[Token]:
    """Tokenise ``source``.

    ``mask`` (strings and comments blanked) is used for *structure*, while the
    source text is read back for the token bodies.  String and comment spans are
    detected on the source so that quotes inside comments cannot start a string.
    """
    comments = _comment_mask(source)
    tokens: List[Token] = []
    index = 0
    length = len(source)
    while index < length:
        if comments[index] == " " and source[index].isspace() is False and not source[index].isalnum():
            # inside a comment
            end = index
            while end < length and comments[end] == " " and source[end] != "\n":
                end += 1
            if end > index:
                tokens.append(Token("comment", source[index:end], index, end))
                index = end
                continue
        char = source[index]
        if char.isspace():
            index += 1
            continue
        if char in "\"'":
            quote = char
            cursor = index + 1
            while cursor < length:
                current = source[cursor]
                if current == "\\":
                    cursor += 2
                    continue
                if current == quote or current == "\n":
                    cursor += 1
                    break
                cursor += 1
            tokens.append(Token("string", source[index:cursor], index, cursor))
            index = cursor
            continue
        if char == "[" and source.startswith("[[", index) or (char == "[" and re.match(r"\[=+\[", source[index:])):
            long_open = re.match(r"\[(=*)\[", source[index:])
            close = "]" + long_open.group(1) + "]"
            end = source.find(close, index + long_open.end())
            end = length if end < 0 else end + len(close)
            tokens.append(Token("string", source[index:end], index, end))
            index = end
            continue
        if NAME_START.match(char):
            cursor = index + 1
            while cursor < length and NAME_CHARS.match(source[cursor]):
                cursor += 1
            text = source[index:cursor]
            kind = "keyword" if text in LUA_KEYWORDS else "name"
            tokens.append(Token(kind, text, index, cursor))
            index = cursor
            continue
        if char.isdigit() or (char == "." and index + 1 < length and source[index + 1].isdigit()):
            cursor = index + 1
            while cursor < length:
                candidate = source[cursor]
                if NUMBER_CHARS.match(candidate) or (candidate in "+-" and source[cursor - 1] in "eE"):
                    cursor += 1
                    continue
                break
            tokens.append(Token("number", source[index:cursor], index, cursor))
            index = cursor
            continue
        if source.startswith("...", index):
            tokens.append(Token("punct", "...", index, index + 3))
            index += 3
            continue
        if source.startswith("..", index):
            tokens.append(Token("punct", "..", index, index + 2))
            index += 2
            continue
        if source.startswith("==", index) or source.startswith("~=", index) or source.startswith("<=", index) \
                or source.startswith(">=", index) or source.startswith("::", index):
            tokens.append(Token("punct", source[index:index + 2], index, index + 2))
            index += 2
            continue
        tokens.append(Token("punct", char, index, index + 1))
        index += 1
    return tokens


# ---------------------------------------------------------------------- blocks
OPENERS = frozenset({"if", "for", "while", "do", "function", "repeat"})
CLOSERS = frozenset({"end", "until"})


def match_block(tokens: Sequence[Token], start: int, end: int) -> int:
    """Index one past the token that closes the block entered at ``start``.

    ``start`` is the first token *inside* the block.  ``while``/``for`` headers are
    skipped up to their ``do`` so the header's ``do`` is not mistaken for a
    standalone ``do``-block, and ``end``/``until`` close the innermost opener.
    """
    depth = 0
    index = start
    while index < end:
        token = tokens[index]
        if token.kind == "keyword":
            text = token.text
            if text in ("while", "for"):
                depth += 1
                cursor = index + 1
                while cursor < end and not (tokens[cursor].kind == "keyword" and tokens[cursor].text == "do"):
                    cursor += 1
                index = cursor + 1
                continue
            if text in ("if", "function", "do", "repeat"):
                depth += 1
            elif text in ("end", "until"):
                if depth == 0:
                    return index + 1
                depth -= 1
        index += 1
    return end


def block_span(tokens: Sequence[Token], opener_index: int) -> Tuple[int, int]:
    """Span (inside the opener's body) of the block belonging to ``opener_index``."""
    # skip forward to the body marker: then / do
    index = opener_index + 1
    length = len(tokens)
    while index < length:
        token = tokens[index]
        if token.kind == "keyword" and token.text in ("then", "do"):
            return index + 1, match_block(tokens, index + 1, length) - 1
        if token.kind == "punct" and token.text == ")" and index + 1 < length:
            # `function(...)` -> the body starts right after the parameter list
            if tokens[opener_index].text == "function":
                return index + 1, match_block(tokens, index + 1, length) - 1
            index += 1
            continue
        index += 1
    return length, length


# ----------------------------------------------------------------- statements
def split_statements(tokens: Sequence[Token], start: int, end: int) -> List[Tuple[int, int]]:
    """Split ``tokens[start:end]`` into statement spans (token index ranges).

    The scanner understands enough of Lua's grammar to find where a statement
    ends: block statements are matched with :func:`match_block`, and simple
    statements are split after a complete expression list.  The generated code
    WRD emits has no separators (``x="a"t=nil``), so expression scanning is the
    only reliable way to find the boundaries.
    """
    spans: List[Tuple[int, int]] = []
    index = start
    while index < end:
        token = tokens[index]
        if token.kind == "punct" and token.text == ";":
            index += 1
            continue
        statement_start = index
        if token.kind == "keyword" and token.text in ("if", "while", "for", "do", "function", "repeat"):
            index = match_block(tokens, index + 1, end)
            spans.append((statement_start, min(index, end)))
            continue
        if token.kind == "keyword" and token.text == "return":
            index = _scan_expression_list(tokens, index + 1, end)
            spans.append((statement_start, index))
            continue
        if token.kind == "keyword" and token.text in ("break", "goto"):
            index += 1
            spans.append((statement_start, index))
            continue
        if token.kind == "punct" and token.text == ":" and index + 1 < end and tokens[index + 1].text == ":":
            index += 3  # ::label::
            spans.append((statement_start, min(index, end)))
            continue
        # `local` / plain assignment / call
        index = _scan_simple_statement(tokens, index, end)
        if index <= statement_start:
            index = statement_start + 1
        spans.append((statement_start, min(index, end)))
    return spans


def _scan_expression_list(tokens: Sequence[Token], index: int, end: int) -> int:
    """Scan ``exp {,exp}`` and return the index after it."""
    index = _scan_expression(tokens, index, end)
    while index < end:
        token = tokens[index]
        if token.kind == "punct" and token.text == ",":
            index = _scan_expression(tokens, index + 1, end)
            continue
        break
    return index


def _scan_simple_statement(tokens: Sequence[Token], index: int, end: int) -> int:
    """Scan a local/assignment/call statement, return the index after it."""
    if tokens[index].kind == "keyword" and tokens[index].text == "local":
        index += 1
        if index < end and tokens[index].kind == "keyword" and tokens[index].text == "function":
            return match_block(tokens, index + 1, end)
        index = _scan_name_list(tokens, index, end)
        if index < end and tokens[index].kind == "punct" and tokens[index].text == "=":
            return _scan_expression_list(tokens, index + 1, end)
        return index

    index = _scan_suffixed_expression(tokens, index, end)
    if index < end and tokens[index].kind == "punct" and tokens[index].text in (",", "="):
        index = _scan_name_list(tokens, index, end)
        if index < end and tokens[index].kind == "punct" and tokens[index].text == "=":
            return _scan_expression_list(tokens, index + 1, end)
        return index
    return index


def _scan_name_list(tokens: Sequence[Token], index: int, end: int) -> int:
    while index < end:
        token = tokens[index]
        if token.kind == "name":
            index += 1
        elif token.kind == "punct" and token.text == ",":
            index += 1
            continue
        else:
            break
    return index


BINARY_OPS = {
    "or": 1, "and": 2,
    "<": 3, ">": 3, "<=": 3, ">=": 3, "~=": 3, "==": 3,
    "..": 4,
    "+": 5, "-": 5,
    "*": 6, "/": 6, "%": 6,
    "unary": 7,
    "^": 8,
}
UNARY_KEYWORDS = frozenset({"not"})


def _scan_expression(tokens: Sequence[Token], index: int, end: int, minimum: int = 1) -> int:
    """Precedence climbing over the token stream; returns the index past the term."""
    index = _scan_unary(tokens, index, end)
    while index < end:
        token = tokens[index]
        operator = token.text if token.kind in ("punct", "keyword") else None
        if operator is None or operator not in BINARY_OPS:
            break
        precedence = BINARY_OPS[operator]
        if precedence < minimum:
            break
        # right associative operators
        next_minimum = precedence if operator in ("..", "^") else precedence + 1
        index = _scan_expression(tokens, index + 1, end, next_minimum)
    return index


def _scan_unary(tokens: Sequence[Token], index: int, end: int) -> int:
    if index >= end:
        return index
    token = tokens[index]
    if (token.kind == "punct" and token.text in ("-", "#")) or (
        token.kind == "keyword" and token.text in UNARY_KEYWORDS
    ):
        return _scan_unary(tokens, index + 1, end)
    return _scan_suffixed_expression(tokens, index, end)


def _scan_suffixed_expression(tokens: Sequence[Token], index: int, end: int) -> int:
    index = _scan_primary_expression(tokens, index, end)
    while index < end:
        token = tokens[index]
        if token.kind == "punct" and token.text in (".", ":"):
            index += 2 if index + 1 < end else 1
            continue
        if token.kind == "punct" and token.text == "[":
            index = match_balanced(tokens, index, end)
            continue
        if token.kind == "punct" and token.text in ("(", "{"):
            index = match_balanced(tokens, index, end)
            continue
        if token.kind == "string":
            index += 1
            continue
        break
    return index


def _scan_primary_expression(tokens: Sequence[Token], index: int, end: int) -> int:
    if index >= end:
        return index
    token = tokens[index]
    if token.kind in ("name", "number", "string"):
        return index + 1
    if token.kind == "keyword" and token.text in ("nil", "true", "false", "function"):
        if token.text == "function":
            return match_block(tokens, index + 1, end)
        return index + 1
    if token.kind == "punct" and token.text == "...":
        return index + 1
    if token.kind == "punct" and token.text == "(":
        return match_balanced(tokens, index, end)
    if token.kind == "punct" and token.text == "{":
        return match_balanced(tokens, index, end)
    return index + 1


def match_balanced(tokens: Sequence[Token], index: int, end: int) -> int:
    """Match ``()``/``[]``/``{}`` starting at ``index`` (index past the closer)."""
    pairs = {"(": ")", "[": "]", "{": "}"}
    if index >= end or tokens[index].text not in pairs:
        return min(index + 1, end)
    stack: List[str] = [pairs[tokens[index].text]]
    cursor = index + 1
    while cursor < end and stack:
        token = tokens[cursor]
        if token.kind == "punct":
            if token.text in pairs:
                stack.append(pairs[token.text])
            elif token.text == stack[-1]:
                stack.pop()
            elif token.text in pairs.values():
                return cursor + 1  # mismatched closer: recover here
        cursor += 1
    return cursor


# ------------------------------------------------------------------- dispatcher
@dataclass
class Condition:
    """One pivot of the dispatch tree."""

    variable: str
    bound: int
    below: bool  # True: `variable < bound`, False: `variable >= bound`

    def render(self) -> str:
        return f"{self.variable} < {self.bound}" if self.below else f"{self.variable} >= {self.bound}"


@dataclass
class Successor:
    kind: str  # "constant" | "conditional" | "dynamic" | "literal" | "unknown"
    target: str = ""
    condition: str = ""
    raw: str = ""
    resolved: str = ""
    """Target inferred from the trace (which state actually ran next)."""

    confidence: float = 0.0
    visits: int = 0

    def render(self) -> str:
        if self.kind == "constant":
            return f"goto {self.target}"
        if self.kind == "conditional":
            return f"if {self.condition} then goto {self.target} else goto {self.raw} end"
        if self.kind == "dynamic":
            if self.resolved:
                evidence = f"{self.visits} visit(s)"
                if self.visits >= 3:
                    evidence += f", {self.confidence:.0%} consistent"
                return f"goto {self.target}  (dynamic; trace: {self.resolved} in {evidence})"
            return f"goto {self.target}  (dynamic: target read from a register)"
        if self.kind == "register-jump":
            return f"if {self.condition} then goto {self.target} else goto {self.raw} end  (registers)"
        if self.kind == "literal":
            return f"state = {self.target}  (loop keeps running while state is truthy)"
        return f"goto {self.raw or self.target}  (computed target)"


@dataclass
class StateBlock:
    """One state of the flattened machine."""

    index: int
    label: str
    conditions: List[Condition]
    lo: Optional[int]
    hi: Optional[int]
    value: Optional[int]
    body: str = ""
    span: Tuple[int, int] = (0, 0)
    token_span: Tuple[int, int] = (0, 0)
    successors: List[Successor] = field(default_factory=list)
    closures: List[str] = field(default_factory=list)
    reachable_from: List[str] = field(default_factory=list)
    observed: int = 0
    observed_sample: List[str] = field(default_factory=list)
    observed_transitions: List[dict] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "index": self.index,
            "guard_value": self.value,
            "label": self.label,
            "value": self.value,
            "range": [self.lo, self.hi],
            "conditions": [c.render() for c in self.conditions],
            "successors": [
                {
                    "kind": s.kind,
                    "target": s.target,
                    "condition": s.condition,
                    "render": s.render(),
                    "resolved": s.resolved,
                    "confidence": round(s.confidence, 3),
                    "visits": s.visits,
                }
                for s in self.successors
            ],
            "closures": self.closures,
            "reachable_from": self.reachable_from,
            "observed_values": self.observed,
            "observed_sample": self.observed_sample,
            "observed_transitions": self.observed_transitions,
            "statements": self.body.count("\n"),
        }


@dataclass
class LiftResult:
    ok: bool = False
    reason: str = ""
    dispatcher: dict = field(default_factory=dict)
    registers: Dict[str, str] = field(default_factory=dict)  # vN -> original
    states: List[StateBlock] = field(default_factory=list)
    helpers: List[dict] = field(default_factory=list)
    pseudocode: str = ""
    notes: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def stats(self) -> dict:
        dynamic = sum(1 for s in self.states for x in s.successors if x.kind == "dynamic")
        resolved = sum(1 for s in self.states for x in s.successors if x.resolved)
        literals = sum(1 for s in self.states for x in s.successors if x.kind == "literal")
        conditional = sum(1 for s in self.states for x in s.successors if x.kind == "conditional")
        closures = sum(len(s.closures) for s in self.states)
        return {
            "states": len(self.states),
            "registers": len(self.registers),
            "closures": closures,
            "dynamic_jumps": dynamic,
            "dynamic_jumps_resolved_by_trace": resolved,
            "literal_jumps": literals,
            "conditional_jumps": conditional,
            "helpers": len(self.helpers),
            "pseudocode_chars": len(self.pseudocode),
        }

    def as_dict(self, max_states: int = 200) -> dict:
        return {
            "ok": self.ok,
            "reason": self.reason,
            "dispatcher": self.dispatcher,
            "stats": self.stats(),
            "registers": self.registers,
            "states": [state.as_dict() for state in self.states[:max_states]],
            "states_truncated": max(0, len(self.states) - max_states),
            "helpers": [
                {k: v for k, v in helper.items() if k != "body"} | {"body_chars": len(helper.get("body", ""))}
                for helper in self.helpers
            ],
            "notes": self.notes,
            "warnings": self.warnings,
        }


# ------------------------------------------------------------------- scanning
def _find_whiles(tokens: Sequence[Token]) -> List[int]:
    return [i for i, t in enumerate(tokens) if t.kind == "keyword" and t.text == "while"]


def _pivot_of(tokens: Sequence[Token], if_index: int) -> Optional[Tuple[str, int]]:
    """Parse ``if <variable> < <number> then`` starting at ``if_index``."""
    parts: List[Token] = []
    index = if_index + 1
    while index < len(tokens) and len(parts) <= 4:
        token = tokens[index]
        if token.kind == "keyword" and token.text == "then":
            break
        parts.append(token)
        index += 1
    if len(parts) != 3:
        return None
    first, operator, second = parts
    if first.kind != "name" or operator.kind != "punct" or operator.text != "<" or second.kind != "number":
        return None
    try:
        bound = int(second.text, 0)
    except ValueError:
        try:
            bound = int(float(second.text))
        except ValueError:
            return None
    return first.text, bound


def _count_pivots(tokens: Sequence[Token], start: int, end: int, variable: str) -> int:
    count = 0
    for index in range(start, end):
        token = tokens[index]
        if token.kind == "keyword" and token.text in ("if", "elseif"):
            parsed = _pivot_of(tokens, index)
            if parsed and parsed[0] == variable:
                count += 1
    return count


def _slice(tokens: Sequence[Token], start: int, end: int) -> str:
    if start >= end:
        return ""
    return " ".join(t.text for t in tokens[start:end])


def find_dispatcher(source: str) -> Optional[dict]:
    """Locate the dispatch loop of a flattened script (public entry point).

    Returns ``{"variable", "start", "body_char_span", "pivots"}`` or ``None``.
    Used by :mod:`core.vm_trace` so that the trace instruments *the same* loop
    this module analyses.
    """
    mask = mask_lua(source)
    tokens = tokenize(source, mask)
    found = _find_dispatcher(tokens)
    if found is None:
        return None
    variable, index, body_start, body_end = found
    pivots = _count_pivots(tokens, body_start, body_end, variable)
    return {
        "variable": variable,
        "start": tokens[index].start,
        "body_char_span": (
            tokens[body_start].start if body_start < len(tokens) else 0,
            tokens[body_end - 1].end if body_end > body_start else 0,
        ),
        "pivots": pivots,
        "token_span": (body_start, body_end),
    }


def _find_dispatcher(tokens: Sequence[Token]) -> Optional[Tuple[str, int, int, int]]:
    """Return ``(variable, while_index, body_start, body_end)`` for the dispatcher."""
    best: Optional[Tuple[int, str, int, int, int]] = None
    for index in _find_whiles(tokens):
        if index + 1 >= len(tokens) or tokens[index + 1].kind != "name":
            continue
        variable = tokens[index + 1].text
        body_start, body_end = block_span(tokens, index)
        if body_end <= body_start:
            continue
        pivots = _count_pivots(tokens, body_start, body_end, variable)
        if pivots < 3:
            continue
        if best is None or pivots > best[0]:
            best = (pivots, variable, index, body_start, body_end)
    if best is None:
        return None
    _count, variable, index, body_start, body_end = best
    return variable, index, body_start, body_end


def _split_if(tokens: Sequence[Token], if_index: int, end: int) -> Optional[Tuple[int, int, int, int]]:
    """Split an ``if``/``elseif`` into ``(then_start, then_end, else_start, else_end)``.

    ``else_start == else_end`` when there is no ``else`` branch.  Nested blocks are
    skipped with :func:`match_block`, so only the branches of *this* statement are
    returned.
    """
    then_marker: Optional[int] = None
    depth = 0
    index = if_index + 1
    while index < end:
        token = tokens[index]
        if token.kind == "punct":
            if token.text in ("(", "[", "{"):
                depth += 1
            elif token.text in (")", "]", "}"):
                depth -= 1
        elif depth == 0 and token.kind == "keyword":
            if token.text == "then":
                if then_marker is None:
                    then_marker = index + 1
                index += 1
                continue
            if token.text in ("if", "for", "while", "do", "repeat", "function"):
                index = match_block(tokens, index + 1, end)
                continue
            if token.text in ("end", "else") and then_marker is not None:
                if token.text == "end":
                    return then_marker, index, index, index
                # `else` -> everything up to the closing `end` is the else branch
                cursor = index + 1
                while cursor < end:
                    candidate = tokens[cursor]
                    if candidate.kind == "keyword":
                        if candidate.text in ("if", "for", "while", "do", "repeat", "function"):
                            cursor = match_block(tokens, cursor + 1, end)
                            continue
                        if candidate.text == "end":
                            return then_marker, index, index + 1, cursor
                    cursor += 1
                return then_marker, index, index + 1, end
            if token.text == "elseif" and then_marker is not None:
                # keep the `elseif` in the else branch so recursion treats it as a pivot
                return then_marker, index, index, end
        index += 1
    if then_marker is None:
        return None
    return then_marker, end, end, end


def _walk_dispatch(
    tokens: Sequence[Token],
    start: int,
    end: int,
    variable: str,
    conditions: List[Condition],
    leaves: List[Tuple[List[Condition], int, int]],
    guard: int = 0,
) -> None:
    """Recursively split the pivot chain into leaves."""
    if guard > 4096:
        return
    if start < end and tokens[start].kind == "keyword" and tokens[start].text in ("if", "elseif"):
        parsed = _pivot_of(tokens, start)
        split = _split_if(tokens, start, end)
        if parsed and split and parsed[0] == variable:
            then_start, then_end, else_start, else_end = split
            _bound = parsed[1]
            _walk_dispatch(tokens, then_start, then_end, variable,
                           conditions + [Condition(variable, _bound, True)], leaves, guard + 1)
            if else_start < else_end:
                _walk_dispatch(tokens, else_start, else_end, variable,
                               conditions + [Condition(variable, _bound, False)], leaves, guard + 1)
            return
    leaves.append((conditions, start, end))


# -------------------------------------------------------------------- renaming
def _collect_names(tokens: Sequence[Token], spans: Iterable[Tuple[int, int]]) -> List[str]:
    """Identifier names in the given spans, in first-appearance order."""
    seen: List[str] = []
    known = set()
    for start, end in spans:
        for token in tokens[start:end]:
            if token.kind == "name" and token.text not in known:
                known.add(token.text)
                seen.append(token.text)
    return seen


def _rewrite_text(source: str, mask: str, start: int, end: int, mapping: Dict[str, str]) -> str:
    """Render ``source[start:end]`` with identifiers renamed (strings untouched)."""
    text = source[start:end]
    if not mapping:
        return text
    out: List[str] = []
    index = start
    while index < end:
        char = mask[index]
        if char.isspace():
            out.append(source[index])
            index += 1
            continue
        match = NAME_START.match(source[index]) if char != " " else None
        if match:
            cursor = index + 1
            while cursor < end and NAME_CHARS.match(mask[cursor]):
                cursor += 1
            word = source[index:cursor]
            out.append(mapping.get(word, word))
            index = cursor
            continue
        if char == " " and source[index] in "\"'":
            # a string literal: copy it verbatim (respecting escapes)
            quote = source[index]
            cursor = index + 1
            while cursor < end:
                current = source[cursor]
                if current == "\\":
                    cursor += 2
                    continue
                if current == quote or current == "\n":
                    cursor += 1
                    break
                cursor += 1
            out.append(source[index:cursor])
            index = cursor
            continue
        out.append(source[index])
        index += 1
    return "".join(out)


# ------------------------------------------------------------------- lift core
def _parse_successor(tokens: Sequence[Token], start: int, end: int, variable: str) -> List[Successor]:
    """Find ``<variable> = <expr>`` statements and describe them."""
    successors: List[Successor] = []
    for span_start, span_end in split_statements(tokens, start, end):
        statement = tokens[span_start:span_end]
        if not statement:
            continue
        text = " ".join(t.text for t in statement)
        match = re.match(r"^([A-Za-z_]\w*)\s*=\s*(.*)$", text, re.S)
        if not match or match.group(1) != variable:
            continue
        expression_tokens = statement[2:]
        expression = " ".join(t.text for t in expression_tokens)
        constant = CONST_JUMP_RE.match(expression)
        if constant:
            successors.append(Successor("constant", target=constant.group(1), raw=expression))
            continue
        conditional = COND_JUMP_RE.match(expression)
        if conditional:
            successors.append(
                Successor(
                    "conditional",
                    target=conditional.group(2),
                    condition=conditional.group(1),
                    raw=conditional.group(3),
                )
            )
            continue
        env = ENV_JUMP_RE.match(expression)
        if env:
            successors.append(Successor("dynamic", target=expression, raw=expression))
            continue
        register_conditional = REG_COND_JUMP_RE.match(expression)
        if register_conditional:
            successors.append(
                Successor(
                    "register-jump",
                    target=register_conditional.group(2),
                    condition=register_conditional.group(1),
                    raw=register_conditional.group(3),
                )
            )
            continue
        register_or = REG_OR_JUMP_RE.match(expression)
        if register_or:
            successors.append(
                Successor(
                    "register-jump",
                    target=register_or.group(1),
                    condition=register_or.group(1),
                    raw=register_or.group(2),
                )
            )
            continue
        if expression.strip() in ("true", "false", "nil"):
            successors.append(Successor("literal", target=expression.strip(), raw=expression.strip()))
            continue
        register = REG_JUMP_RE.match(expression)
        if register:
            successors.append(Successor("dynamic", target=expression, raw=expression))
            continue
        successors.append(Successor("unknown", target=expression, raw=expression))
    return successors


def _simplify_successors(successors: List[Successor], variable: str) -> List[Successor]:
    """Collapse ``state=<literal>`` followed by ``state=state and A or B``.

    WRD sets the loop variable to a constant and then immediately turns it into a
    two-way jump; with the constant known the jump collapses to its taken branch.
    """
    simplified: List[Successor] = []
    index = 0
    while index < len(successors):
        current = successors[index]
        if current.kind == "literal" and index + 1 < len(successors):
            following = successors[index + 1]
            if following.kind == "conditional" and following.condition in (variable, "state"):
                truthy = current.target == "true"
                chosen = following.target if truthy else following.raw
                simplified.append(
                    Successor("constant", target=chosen, raw=f"{current.target} -> {chosen}")
                )
                index += 2
                continue
        simplified.append(current)
        index += 1
    return simplified


def _closures(tokens: Sequence[Token], start: int, end: int) -> List[str]:
    """Render every ``function`` header found in a span."""
    found: List[str] = []
    index = start
    while index < end:
        token = tokens[index]
        if token.kind == "keyword" and token.text == "function":
            cursor = index + 1
            parameters = "?"
            if cursor < end and tokens[cursor].kind == "punct" and tokens[cursor].text == "(":
                close = match_balanced(tokens, cursor, end)
                parameters = " ".join(t.text for t in tokens[cursor:close])
                cursor = close
            body_end = match_block(tokens, cursor, end)
            length = body_end - index
            found.append(f"function {parameters}  -- {length} tokens")
            index = body_end
            continue
        index += 1
    return found


def lift(
    source: str,
    *,
    observed: Sequence[str] = (),
    max_chars: int = MAX_LIFT_CHARS,
) -> LiftResult:
    """Lift a flattened WRD payload into readable pseudo-source.

    ``observed`` may contain the raw state values recorded by
    :func:`core.vm_trace.read_trace`; every numeric value is bucketed into the
    guard interval that contains it, which turns "which code does this state run"
    into something grounded in a real execution.
    """
    result = LiftResult()
    if not source or not source.strip():
        result.reason = "empty source"
        return result
    if len(source) > max_chars:
        result.reason = f"source larger than {max_chars} characters; lift skipped"
        return result

    mask = mask_lua(source)
    tokens = tokenize(source, mask)
    dispatcher = _find_dispatcher(tokens)
    if dispatcher is None:
        result.reason = "no dispatch loop (while <state> do if <state> < ... ) found"
        return result

    variable, while_index, body_start, body_end = dispatcher
    result.dispatcher = {
        "variable": variable,
        "while_token": while_index,
        "start": tokens[while_index].start,
        "body_tokens": [body_start, body_end],
    }

    leaves: List[Tuple[List[Condition], int, int]] = []
    _walk_dispatch(tokens, body_start, body_end, variable, [], leaves)
    leaves = [(c, s, e) for c, s, e in leaves if e > s]
    if not leaves:
        result.reason = "dispatch loop found but no state blocks could be split"
        return result

    # ---- state ranges -----------------------------------------------------
    pivots = sorted({c.bound for conditions, _s, _e in leaves for c in conditions})
    values = set(pivots)
    constant_targets = set()
    for _conditions, start, end in leaves:
        for successor in _simplify_successors(_parse_successor(tokens, start, end, variable), variable):
            if successor.kind == "constant":
                constant_targets.add(int(successor.target))
            elif successor.kind == "conditional":
                constant_targets.add(int(successor.target))
                constant_targets.add(int(successor.raw))
    values |= constant_targets
    ordered = sorted(values)

    def label_for(lo: Optional[int], hi: Optional[int]) -> str:
        if lo is not None and hi is not None:
            if hi - lo == 1:
                return f"S{lo}"
            return f"S_{lo}_{hi}"
        if hi is not None:
            return f"S_below{hi}"
        if lo is not None:
            return f"S_from{lo}"
        return "S_entry"

    blocks: List[StateBlock] = []
    for index, (conditions, start, end) in enumerate(leaves):
        lo = max((c.bound for c in conditions if not c.below), default=None)
        hi = min((c.bound for c in conditions if c.below), default=None)
        value = lo if (lo is not None and hi is not None and hi - lo == 1) else None
        label = label_for(lo, hi)
        block = StateBlock(
            index=index,
            label=label,
            conditions=conditions,
            lo=lo,
            hi=hi,
            value=value,
            token_span=(start, end),
            span=(tokens[start].start if start < len(tokens) else 0,
                  tokens[end - 1].end if end > start else 0),
            successors=_simplify_successors(_parse_successor(tokens, start, end, variable), variable),
            closures=_closures(tokens, start, end),
        )
        blocks.append(block)

    # ---- registers --------------------------------------------------------
    # The whole file is one closure scope (helpers and the dispatcher share their
    # upvalues), so the rename map is built from the dispatcher first and then
    # extended with whatever the helper bodies use.
    body_spans = [(s_, e_) for _c, s_, e_ in leaves]
    names = [n for n in _collect_names(tokens, body_spans) if n != variable]
    known = set(names)
    for helper in _function_spans(tokens):
        for name in _collect_names(tokens, [helper["token_span"]]):
            if name == variable or name in known:
                continue
            known.add(name)
            names.append(name)
    mapping: Dict[str, str] = {}
    for position, name in enumerate(names, start=1):
        mapping[name] = f"v{position}"
    legend = {f"v{position}": name for position, name in enumerate(names, start=1)}

    # the state variable keeps a speaking name
    rename = dict(mapping)
    state_alias = "state"
    rename[variable] = state_alias
    legend[state_alias] = variable
    result.registers = legend
    result.dispatcher["renamed"] = rename.get(variable, variable)

    # ---- resolve successors to labels ------------------------------------
    def state_for(value: int) -> str:
        """Label of the state whose guard interval contains ``value``."""
        for block in blocks:
            if block.lo is not None and value < block.lo:
                continue
            if block.hi is not None and value >= block.hi:
                continue
            return block.label
        return f"S?{value}"

    for block in blocks:
        for successor in block.successors:
            if successor.condition:
                successor.condition = rename.get(successor.condition, successor.condition)
            if successor.kind == "register-jump":
                successor.target = rename.get(successor.target, successor.target)
                successor.raw = rename.get(successor.raw, successor.raw)
            if successor.kind == "dynamic" and successor.target:
                target = re.sub(r"\s*\[\s*", "[", successor.target)
                target = re.sub(r"\s*\]\s*", "]", target)
                target = re.sub(r"\s*\.\s*", ".", target)
                target = re.sub(
                    r"\b[A-Za-z_]\w*\b",
                    lambda m: rename.get(m.group(0), m.group(0)) if m.group(0) in rename else m.group(0),
                    target,
                )
                successor.target = target
            if successor.kind == "constant":
                target_value = int(successor.target)
                successor.raw = str(target_value)
                successor.target = state_for(target_value)
            elif successor.kind == "conditional":
                successor.target = state_for(int(successor.target))
                successor.raw = state_for(int(successor.raw))

    # reachability (successor labels -> blocks)
    label_index = {block.label: block for block in blocks}
    for block in blocks:
        for successor in block.successors:
            targets = [successor.target]
            if successor.kind == "conditional":
                targets.append(successor.raw)
            for target in targets:
                candidate = label_index.get(target)
                if candidate is not None and block.label not in candidate.reachable_from:
                    candidate.reachable_from.append(block.label)

    for block in blocks:
        block.body = "\n".join(_render_block(tokens, source, mask, block, rename))

    observed_values: List[int] = []
    for raw in observed:
        try:
            observed_values.append(int(str(raw).strip(), 0))
        except (TypeError, ValueError):
            continue
    if observed_values:
        def block_of(value: int) -> Optional[StateBlock]:
            for candidate in blocks:
                if candidate.lo is not None and value < candidate.lo:
                    continue
                if candidate.hi is not None and value >= candidate.hi:
                    continue
                return candidate
            return None

        for block in blocks:
            inside = [
                value for value in observed_values
                if (block.lo is None or value >= block.lo) and (block.hi is None or value < block.hi)
            ]
            if inside:
                block.observed = len(inside)
                block.observed_sample = [str(v) for v in sorted(set(inside))[:4]]

        # transition counts: which state actually ran next
        sequence = [block_of(value) for value in observed_values]
        transitions: Dict[Tuple[int, int], int] = {}
        for previous, following in zip(sequence, sequence[1:]):
            if previous is None or following is None or previous is following:
                continue
            key = (previous.index, following.index)
            transitions[key] = transitions.get(key, 0) + 1
        for block in blocks:
            outgoing = {target: count for (source, target), count in transitions.items() if source == block.index}
            if not outgoing:
                continue
            total = sum(outgoing.values())
            best_target, best_count = max(outgoing.items(), key=lambda item: item[1])
            block.observed_transitions = [
                {"to": blocks[target].label, "count": count}
                for target, count in sorted(outgoing.items(), key=lambda item: -item[1])[:4]
            ]
            for successor in block.successors:
                if successor.kind != "dynamic":
                    continue
                successor.visits = total
                successor.resolved = blocks[best_target].label
                successor.confidence = best_count / total if total else 0.0
        result.notes.append(
            f"{len(observed_values)} observed state value(s) mapped onto {len(blocks)} state range(s), "
            f"{len(transitions)} observed transition(s)"
        )

    result.states = blocks

    # ---- helpers (the VM's own functions) --------------------------------
    result.helpers = _helper_inventory(tokens, source, mask, rename)
    if len(blocks) and all(b.body == "" for b in blocks):
        result.warnings.append("state bodies are empty")
    if not result.warnings:
        dynamic = sum(1 for b in blocks for s in b.successors if s.kind == "dynamic")
        if dynamic:
            result.warnings.append(
                f"{dynamic} jump(s) read their target from a register/environment entry"
            )
    result.pseudocode = _render(source, mask, tokens, blocks, legend, variable, mapping,
                                result.dispatcher, result.helpers)
    result.ok = True
    result.reason = "ok"
    return result


def _function_spans(tokens: Sequence[Token]) -> List[dict]:
    """Every ``function`` definition with its name/parameter list and body span."""
    found: List[dict] = []
    length = len(tokens)
    for index, token in enumerate(tokens):
        if token.kind != "keyword" or token.text != "function":
            continue
        name = ""
        cursor = index + 1
        if cursor < length and tokens[cursor].kind == "name":
            name = tokens[cursor].text
            cursor += 1
            while cursor + 1 < length and tokens[cursor].text in (".", ":"):
                name += tokens[cursor].text + tokens[cursor + 1].text
                cursor += 2
        while cursor < length and not (tokens[cursor].kind == "punct" and tokens[cursor].text == "("):
            cursor += 1
        if cursor >= length:
            continue
        parameters_end = match_balanced(tokens, cursor, length)
        body_end = match_block(tokens, parameters_end - 1, length)
        parameters = " ".join(t.text for t in tokens[cursor:parameters_end])
        found.append({
            "at": tokens[index].start,
            "name": name,
            "parameters": parameters,
            "parameter_span": (cursor, parameters_end),
            "token_span": (parameters_end, body_end),
            "body_tokens": max(0, body_end - parameters_end),
        })
    return found


def _helper_inventory(
    tokens: Sequence[Token],
    source: str,
    mask: str,
    rename: Dict[str, str],
    *,
    max_body: int = 6000,
) -> List[dict]:
    """The VM's own functions (the instruction table) with rendered bodies."""
    helpers: List[dict] = []
    for index, function in enumerate(_function_spans(tokens), start=1):
        start, end = function["token_span"]
        rendered: List[str] = []
        for statement_start, statement_end in split_statements(tokens, start, end):
            first, last = tokens[statement_start], tokens[statement_end - 1]
            text = _rewrite_text(source, mask, first.start, last.end, rename).strip()
            if text:
                rendered.append(text)
            if sum(len(line) for line in rendered) > max_body:
                rendered.append("-- ... (truncated in this listing)")
                break
        helpers.append({
            "index": index,
            "name": function["name"] or f"anonymous#{index}",
            "parameters": _render_parameters(function["parameters"], rename),
            "at": function["at"],
            "body_tokens": function["body_tokens"],
            "body": "\n".join(rendered),
        })
    return helpers


def _render_parameters(parameters: str, rename: Dict[str, str]) -> str:
    """Rename the parameter list of a helper (``(a,b)`` -> ``(v1,v2)``)."""
    if not parameters:
        return parameters
    out = []
    for chunk in re.split(r"([A-Za-z_]\w*)", parameters):
        out.append(rename.get(chunk, chunk) if re.fullmatch(r"[A-Za-z_]\w*", chunk or "") else chunk)
    return "".join(out)


# ------------------------------------------------------------------- rendering
def _render_block(
    tokens: Sequence[Token],
    source: str,
    mask: str,
    block: StateBlock,
    rename: Dict[str, str],
) -> List[str]:
    """Render one state's statements with the register names rewritten."""
    start, end = block.token_span
    if start >= end:
        return []
    out: List[str] = []
    for statement_start, statement_end in split_statements(tokens, start, end):
        first, last = tokens[statement_start], tokens[statement_end - 1]
        text = source[first.start:last.end].strip()
        if not text:
            continue
        out.append(_rewrite_text(source, mask, first.start, last.end, rename).strip())
    return out


def _render(
    source: str,
    mask: str,
    tokens: Sequence[Token],
    blocks: Sequence[StateBlock],
    legend: Dict[str, str],
    variable: str,
    mapping: Dict[str, str],
    dispatcher: dict,
    helpers: Sequence[dict],
) -> str:
    """Render the pseudo-source listing."""
    lines: List[str] = []
    lines.append("--[[")
    lines.append("    Excalibur partial lift")
    lines.append("")
    lines.append("    The blocks below are the states of the obfuscator's state machine: the payload")
    lines.append("    is present, but its control flow is a binary search over state numbers and the")
    lines.append("    variables are single letters.  Registers are renamed to v1, v2, v3, ... (see the")
    lines.append("    legend) and every jump keeps its original form:")
    lines.append("")
    lines.append("      goto S12345                 -- constant jump, resolved to the owning state")
    lines.append("      if v3 then ... else ... end -- conditional jump (condition kept)")
    lines.append('      goto v7["name"]             -- target read from a register/environment')
    lines.append("")
    # the header shows the state variable under its new name as well
    state_name = dispatcher.get("renamed") or mapping.get(variable, variable)
    lines.append(f"    dispatcher: while {state_name} do ... end  -  {len(blocks)} states")
    lines.append("]]")
    lines.append("")
    lines.append("-- register legend (original names, before renaming)")
    ordered = sorted(
        ((name, alias) for alias, name in legend.items()),
        key=lambda pair: (len(pair[1]), pair[1]),
    )
    for name, alias in ordered:
        lines.append(f"-- {alias:<6} = {name}")
    lines.append("")

    for block in blocks:
        lines.append(f"-- ==== state {block.label} (#{block.index}) ====")
        if block.conditions:
            lines.append("-- guard: " + " & ".join(c.render() for c in block.conditions))
        if block.reachable_from:
            unique = list(dict.fromkeys(block.reachable_from))
            lines.append("-- reached from: " + ", ".join(unique[:8]))
        if block.observed:
            lines.append(f"-- observed in the trace: {block.observed} visit(s) {block.observed_sample}")
        if block.observed_transitions:
            rendered = ", ".join(f"{row['to']} x{row['count']}" for row in block.observed_transitions)
            lines.append(f"-- observed transitions: {rendered}")
        if block.body:
            lines.extend(block.body.split("\n"))
        else:
            lines.append("-- (empty state)")
        for closure in block.closures:
            lines.append(f"-- contains closure: {closure}")
        if block.successors:
            for successor in block.successors:
                lines.append("-- " + successor.render())
        else:
            lines.append("-- (no jump: falls through)")
        lines.append("")

    if helpers:
        lines.append("--[[")
        lines.append("    Appendix: the VM's own functions (the instruction table).")
        lines.append("    Registers keep the same vN names as above.")
        lines.append("]]")
        lines.append("")
        for helper in helpers:
            lines.append(f"-- ==== helper #{helper['index']}: {helper['name']} {helper['parameters']} "
                         f"({helper['body_tokens']} tokens) ====")
            if helper["body"]:
                lines.extend(helper["body"].split("\n"))
            else:
                lines.append("-- (empty body)")
            lines.append("")
    return "\n".join(lines) + "\n"


__all__ = [
    "Condition",
    "LiftResult",
    "MAX_LIFT_CHARS",
    "StateBlock",
    "Successor",
    "lift",
    "match_balanced",
    "match_block",
    "tokenize",
    "split_statements",
    "tokenize",
]
