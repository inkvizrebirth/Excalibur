"""Static decoding of the WRD v1.0.0 string/constant layer.

What this module does (all of it verified against real WRD samples, see
``docs/REAL_WORLD_NOTES.md``):

1. **String pool** - WRD stores its constants as *escaped decimal* literals
   (``"\\051\\048..."``) that are base64 text.  Each entry is decoded with a
   **custom 64 character alphabet** that the script builds at runtime.
2. **Shuffle passes** - three ``while`` loops swap pool entries around
   (``j[a], j[b], ... = j[b], j[a], a+1, b-1``) before the resolver index space
   is meaningful.  The passes are replayed exactly.
3. **Resolver inlining** - ``local function g(i) return j[i - OFFSET] end`` is
   located, and every call ``g(<constant expression>)`` is replaced by the
   decoded Lua string literal.  This turns
   ``local a = h(-460905-(-523958))`` into ``local a = "print"``.
4. **Constant folding** - WRD hides every integer behind arithmetic
   (``8220092-37153``).  Pure numeric expressions are folded, which is what
   makes the flattened VM code readable again.

Together 3+4 produce the ``*.decoded.lua`` artefact: the same program with its
constant layer removed.  It is *not* the original script when the obfuscator
used a bytecode VM (the payload does not exist as text in that case) - it is the
best statically reachable representation, and it is what the dynamic stage and a
human analyst then work from.
"""

from __future__ import annotations

import ast
import base64
import math
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Sequence, Tuple

from .wrd_detect import ESCAPED_DECIMAL_STRING_RE, RESOLVER_DEF_RE, mask_lua

# ------------------------------------------------------------------ constants

MAX_EXPR_LEN = 400
MAX_FOLD_RESULT = 1e15
IDENTIFIER_RE = re.compile(r"^[A-Za-z_]\w*$")
TABLE_START_RE = re.compile(r"local\s+([A-Za-z_]\w*)\s*=\s*\{")
STRING_ITEM_RE = re.compile(r'^"((?:[^"\\]|\\.)*)"$', re.S)
LUA_ESCAPE_MAP = {"\\": "\\\\", '"': '\\"', "\n": "\\n", "\r": "\\r", "\t": "\\t"}

_ALLOWED_BINOPS = (ast.Add, ast.Sub, ast.Mult, ast.Div, ast.Mod, ast.Pow, ast.FloorDiv)
_ALLOWED_UNARY = (ast.UAdd, ast.USub)


# ------------------------------------------------------------------ helpers


def unescape_lua_string(text: str) -> str:
    """Decode a Lua short-string body (``\\051`` and ``\\n`` style escapes)."""
    out: List[str] = []
    i = 0
    n = len(text)
    while i < n:
        ch = text[i]
        if ch != "\\":
            out.append(ch)
            i += 1
            continue
        m = re.match(r"\\(\d{1,3})", text[i:])
        if m:
            value = int(m.group(1))
            out.append(chr(value & 0xFF))
            i += m.end()
            continue
        nxt = text[i + 1 : i + 2]
        simple = {"n": "\n", "t": "\t", "r": "\r", "a": "\a", "b": "\b", "f": "\f", "v": "\v", "\\": "\\", '"': '"', "'": "'"}
        if nxt in simple:
            out.append(simple[nxt])
            i += 2
            continue
        if nxt == "x":
            m2 = re.match(r"\\x([0-9a-fA-F]{1,2})", text[i:])
            if m2:
                out.append(chr(int(m2.group(1), 16)))
                i += m2.end()
                continue
        if nxt == "\n":
            out.append("\n")
            i += 2
            continue
        out.append(nxt)
        i += 2
    return "".join(out)


def escape_lua_string(value: str, quote: str = '"') -> str:
    """Escape ``value`` so it can be embedded in a Lua short string.

    ``value`` holds bytes mapped 1:1 onto code points (latin-1).  Every byte
    outside printable ASCII is written as a decimal escape, so the result is
    pure ASCII: the generated file is byte exact no matter which encoding the
    surrounding tooling uses, and Lua turns ``\\196`` back into byte 196.
    """
    parts: List[str] = []
    for ch in value:
        code = ord(ch)
        if ch in LUA_ESCAPE_MAP:
            parts.append(LUA_ESCAPE_MAP[ch])
        elif ch == "'" and quote == "'":
            parts.append("\\'")
        elif code < 32 or code >= 127:
            parts.append(f"\\{code:03d}")
        else:
            parts.append(ch)
    return "".join(parts)


def lua_string_literal(value: str, prefer_long: bool = True) -> str:
    """Render ``value`` as a Lua literal, using a long string when it helps."""
    if prefer_long and all(ord(c) < 127 for c in value) and ("\n" in value or value.count('"') > 3) \
            and "]]" not in value and not value.endswith("]"):
        # [[ ]] cannot represent a leading newline faithfully, and Lua skips a
        # first newline inside long strings - prepend one to preserve content.
        body = value
        if body.startswith("\n"):
            body = "\n" + body
        if "\r" not in value:
            return f"[[{body}]]"
    encoded = escape_lua_string(value, '"')
    if "\n" in value:
        encoded = encoded.replace("\n", "\\n")
    return f'"{encoded}"'


def cheap_candidate_ok(expr: str) -> bool:
    """Fast reject for spans that cannot be a complete arithmetic expression.

    Runs in O(len) without parsing, which keeps the folding pass fast on
    multi-megabyte inputs where most candidates are unbalanced.
    """
    if not expr or len(expr) > MAX_EXPR_LEN:
        return False
    last = expr[-1]
    if not (last.isdigit() or last == ")"):
        return False
    depth = 0
    for ch in expr:
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth -= 1
            if depth < 0:
                return False
    return depth == 0


def evaluate_constant(expr: str) -> Optional[float]:
    """Evaluate a pure numeric Lua expression; returns None when not constant.

    Uses :mod:`ast` with a strict node whitelist - never :func:`eval`.
    """
    expr = expr.strip()
    if not expr or len(expr) > MAX_EXPR_LEN:
        return None
    # Lua 5.1 accepts hexadecimal literals; rewrite them for the parser below.
    if "0X" in expr.upper():
        expr = re.sub(r"\b0[xX]([0-9a-fA-F]+)\b", lambda m: str(int(m.group(1), 16)), expr)
    if not cheap_candidate_ok(expr):
        return None
    if not re.fullmatch(r"[-+*/%^()\d\s.eE]+", expr):
        return None
    py_expr = expr.replace("^", "**")
    try:
        tree = ast.parse(py_expr, mode="eval")
    except SyntaxError:
        return None

    def visit(node: ast.AST) -> float:
        if isinstance(node, ast.Expression):
            return visit(node.body)
        if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
            return float(node.value)
        if isinstance(node, ast.UnaryOp) and isinstance(node.op, _ALLOWED_UNARY):
            value = visit(node.operand)
            return -value if isinstance(node.op, ast.USub) else value
        if isinstance(node, ast.BinOp) and isinstance(node.op, _ALLOWED_BINOPS):
            left = visit(node.left)
            right = visit(node.right)
            if isinstance(node.op, ast.Add):
                return left + right
            if isinstance(node.op, ast.Sub):
                return left - right
            if isinstance(node.op, ast.Mult):
                return left * right
            if isinstance(node.op, ast.Div):
                return left / right
            if isinstance(node.op, ast.FloorDiv):
                return float(left // right)
            if isinstance(node.op, ast.Mod):
                # Lua's `%` is floor-modulo (Lua 5.1 manual 2.5.1), exactly like
                # Python's float `%`; math.fmod would be wrong for negatives.
                return left % right
            return left**right
        raise ValueError("non-constant node")

    try:
        value = visit(tree)
    except (ValueError, ZeroDivisionError, OverflowError, TypeError):
        return None
    if not math.isfinite(value):
        return None
    if abs(value) > MAX_FOLD_RESULT:
        return None
    return value


def format_number(value: float) -> str:
    """Render a folded number the way Lua 5.1 would print it."""
    if value == int(value) and abs(value) < 1e15:
        return str(int(value))
    text = f"{value:.14g}"
    if "e" in text:
        text = text.replace("e+", "e")
    return text


def split_top_level(text: str, *, seps: str = ",;", keep_blank: bool = False) -> List[Tuple[int, int]]:
    """Split ``text`` on top-level separators, returning ``(start, end)`` spans.

    Strings inside ``text`` are expected to be blanked already (see
    :func:`core.wrd_detect.mask_lua`), so only bracket depth matters.
    """
    spans: List[Tuple[int, int]] = []
    depth = 0
    start = 0
    for i, ch in enumerate(text):
        if ch in "([{":
            depth += 1
        elif ch in ")]}":
            depth -= 1
        elif ch in seps and depth == 0:
            if keep_blank or text[start:i].strip():
                spans.append((start, i))
            start = i + 1
    if keep_blank or text[start:].strip():
        spans.append((start, len(text)))
    return spans


def balanced_span(mask: str, open_index: int, opening: str = "{", closing: str = "}") -> Optional[Tuple[int, int]]:
    """Return the ``(start, end)`` of a balanced bracket group in ``mask``."""
    depth = 0
    for i in range(open_index, len(mask)):
        ch = mask[i]
        if ch == opening:
            depth += 1
        elif ch == closing:
            depth -= 1
            if depth == 0:
                return open_index, i + 1
    return None


# ------------------------------------------------------------------ result


@dataclass
class PoolInfo:
    name: str
    start: int
    end: int
    entries: int
    alphabets: Dict[str, Dict[str, int]] = field(default_factory=dict)
    shuffles: List[Tuple[int, int]] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "entries": self.entries,
            "alphabet_size": max((len(a) for a in self.alphabets.values()), default=0),
            "shuffles": [list(s) for s in self.shuffles],
        }


@dataclass
class StaticLayerResult:
    ok: bool
    reason: str = ""
    version: Optional[str] = None
    pool: Optional[PoolInfo] = None
    decoded: List[Optional[str]] = field(default_factory=list)
    resolver: Optional[dict] = None
    inlined_calls: int = 0
    folded_expressions: int = 0
    output: Optional[str] = None
    warnings: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)

    # -------------------------------------------------------------- reporting
    def constant_table(self, limit: int = 400) -> List[dict]:
        rows: List[dict] = []
        for index, value in enumerate(self.decoded):
            if value is None:
                continue
            kind = "binary"
            preview = ""
            if IDENTIFIER_RE.match(value):
                kind = "identifier"
                preview = value
            elif all(32 <= ord(c) < 127 or c in "\n\r\t" for c in value):
                kind = "text"
                preview = value if len(value) <= 120 else value[:117] + "..."
            else:
                preview = repr(value[:40])
            rows.append({"index": index + 1, "kind": kind, "preview": preview, "length": len(value)})
            if len(rows) >= limit:
                break
        return rows

    def stats(self) -> dict:
        decoded = [d for d in self.decoded if d is not None]
        identifiers = sum(1 for d in decoded if IDENTIFIER_RE.match(d))
        text = sum(
            1 for d in decoded if not IDENTIFIER_RE.match(d) and all(32 <= ord(c) < 127 or c in "\n\r\t" for c in d)
        )
        return {
            "pool_entries": len(self.decoded),
            "decoded_entries": len(decoded),
            "identifiers": identifiers,
            "text_constants": text,
            "binary_constants": len(decoded) - identifiers - text,
            "total_decoded_bytes": sum(len(d) for d in decoded),
            "inlined_calls": self.inlined_calls,
            "folded_expressions": self.folded_expressions,
        }

    def as_dict(self, *, include_output: bool = False) -> dict:
        data = {
            "ok": self.ok,
            "reason": self.reason,
            "version": self.version,
            "pool": self.pool.as_dict() if self.pool else None,
            "resolver": self.resolver,
            "stats": self.stats(),
            "warnings": self.warnings,
            "notes": self.notes,
            "constants": self.constant_table(60),
        }
        if include_output and self.output is not None:
            data["output_chars"] = len(self.output)
        return data


# ------------------------------------------------------------------ pool parsing


def _find_pool_tables(mask: str) -> List[Tuple[str, int, int]]:
    """Locate ``local <name> = { ... }`` tables and return their spans."""
    found: List[Tuple[str, int, int]] = []
    for match in TABLE_START_RE.finditer(mask):
        span = balanced_span(mask, match.end() - 1)
        if span:
            found.append((match.group(1), span[0], span[1]))
    return found


def _pool_items(mask: str, source: str, start: int, end: int) -> List[Tuple[int, int]]:
    """Top level item spans of a pool table.

    Strings inside the mask are blanked to whitespace, so items are located via
    the mask and classified using the original source text.  Spans of blank
    (trailing separators) items are dropped.
    """
    body = mask[start + 1 : end - 1]
    spans: List[Tuple[int, int]] = []
    for rel_start, rel_end in split_top_level(body, keep_blank=True):
        absolute = (start + 1 + rel_start, start + 1 + rel_end)
        if source[absolute[0] : absolute[1]].strip():
            spans.append(absolute)
    return spans


def _pool_entries(mask: str, source: str, start: int, end: int) -> List[Tuple[int, int]]:
    """Spans of the *string* items of a pool table."""
    items: List[Tuple[int, int]] = []
    for span in _pool_items(mask, source, start, end):
        item_text = source[span[0] : span[1]].strip()
        if item_text.startswith('"') and item_text.endswith('"') and STRING_ITEM_RE.match(item_text):
            items.append(span)
    return items


def _parse_alphabet(mask: str, source: str, start: int, end: int) -> Dict[str, int]:
    """Parse a ``{char = value, ...}`` table used as a custom alphabet."""
    body = mask[start + 1 : end - 1]
    mapping: Dict[str, int] = {}
    for rel_start, rel_end in split_top_level(body, seps=",;"):
        item = source[start + 1 + rel_start : start + 1 + rel_end].strip()
        if "=" not in item:
            continue
        key_text, _, value_text = item.partition("=")
        key_text = key_text.strip()
        if key_text.startswith("["):
            key_text = key_text[1:-1].strip()
            if key_text.startswith('"') and key_text.endswith('"'):
                key_text = unescape_lua_string(key_text[1:-1])
            else:
                continue
        elif not re.fullmatch(r"[A-Za-z_]\w*", key_text):
            continue
        value = evaluate_constant(value_text)
        if value is None or value < 0 or value > 200:
            continue
        mapping[key_text] = int(value)
    return mapping


def _parse_shuffles(mask: str) -> List[Tuple[int, int]]:
    """Extract the ``ipairs({{a,b},{c,d}...})`` swap ranges."""
    specs: List[Tuple[int, int]] = []
    for match in re.finditer(r"for\s+\w+\s*,\s*\w+\s+in\s+ipairs\s*\(\s*\{", mask):
        span = balanced_span(mask, match.end() - 1)
        if not span:
            continue
        tail = mask[span[1] : span[1] + 800]
        if "while" not in tail:
            continue
        outer = mask[span[0] + 1 : span[1] - 1]
        for group_start, group_end in split_top_level(outer):
            group_text = outer[group_start:group_end].strip()
            if not group_text.startswith("{"):
                continue
            inner = group_text[1:-1] if group_text.endswith("}") else group_text[1:]
            numbers: List[int] = []
            for part_start, part_end in split_top_level(inner):
                value = evaluate_constant(inner[part_start:part_end])
                if value is not None and value == int(value):
                    numbers.append(int(value))
            if len(numbers) == 2:
                specs.append((numbers[0], numbers[1]))
    return specs


# ------------------------------------------------------------------ decoding


def decode_custom_base64(text: str, alphabet: Dict[str, int]) -> bytes:
    """Decode base64 whose alphabet is a ``{char = value}`` mapping."""
    values: List[int] = []
    for ch in text:
        if ch == "=":
            continue
        value = alphabet.get(ch)
        if value is None:
            continue
        values.append(value)
    out = bytearray()
    accumulator = 0
    count = 0
    for value in values:
        accumulator = (accumulator << 6) | (value & 0x3F)
        count += 1
        if count == 4:
            out += accumulator.to_bytes(3, "big")
            accumulator = 0
            count = 0
    if count == 3:
        out += ((accumulator >> 2) & 0xFFFF).to_bytes(2, "big")
    elif count == 2:
        out += bytes([(accumulator >> 4) & 0xFF])
    return bytes(out)


def _apply_shuffles(items: List[str], shuffles: Sequence[Tuple[int, int]]) -> None:
    for start, end in shuffles:
        i, j = start, end
        while i < j:
            if 1 <= i <= len(items) and 1 <= j <= len(items):
                items[i - 1], items[j - 1] = items[j - 1], items[i - 1]
            i += 1
            j -= 1


# ------------------------------------------------------------------ transform


class _Editor:
    """Collects non overlapping replacements and applies them in one pass."""

    def __init__(self, text: str):
        self.text = text
        self.edits: List[Tuple[int, int, str]] = []

    def replace(self, start: int, end: int, replacement: str) -> None:
        self.edits.append((start, end, replacement))

    def render(self) -> str:
        if not self.edits:
            return self.text
        self.edits.sort(key=lambda e: e[0])
        parts: List[str] = []
        cursor = 0
        for start, end, replacement in self.edits:
            if start < cursor:
                continue
            parts.append(self.text[cursor:start])
            parts.append(replacement)
            cursor = end
        parts.append(self.text[cursor:])
        return "".join(parts)


#: Lua 5.1 keywords.  An operator directly after one of these is unary, not
#: binary the way it is after an identifier: `H and-459339+1691705` parses as
#: `(H and (-459339 + 1691705))`, so folding `459339+1691705` would be wrong.
LUA_KEYWORDS = frozenset(
    {
        "and", "break", "do", "else", "elseif", "end", "false", "for", "function", "if", "in",
        "local", "nil", "not", "or", "repeat", "return", "then", "true", "until", "while",
    }
)

#: Punctuation after which an expression may start.
_EXPR_START_PUNCT = frozenset("(,{;=[<>~.")
#: Operators with precedence *higher* than the arithmetic we fold.  A span that
#: follows one of these is bound by it (`a*1+2` parses as `(a*1)+2`), so folding
#: the span on its own would change the value.
_UNSAFE_LEFT_OPS = frozenset("*/%^#")
#: Operators that bind *tighter* on the right of a folded span and would change
#: the value as well (`1+2*3` must not become `3*3`).
_UNSAFE_RIGHT_OPS = frozenset("*/%^")
_WORD_RE = re.compile(r"[A-Za-z0-9_]")
_VALUE_END_RE = re.compile(r"[A-Za-z0-9_)\]'\"]")


def _word_ending_at(text: str, index: int) -> str:
    """Identifier ending at ``index`` (inclusive)."""
    start = index
    while start >= 0 and _WORD_RE.match(text[start]):
        start -= 1
    return text[start + 1 : index + 1]


#: Lua 5.1 operator precedence (manual 2.5.6).  Higher binds tighter.
LUA_PRECEDENCE = {"..": 4, "+": 5, "-": 5, "*": 6, "/": 6, "%": 6, "^": 8}
_ATOMIC = 99


def _top_level_min_precedence(expr: str) -> int:
    """Lowest precedence of the operators that bind ``expr`` as a whole."""
    depth = 0
    best = _ATOMIC
    i = 0
    while i < len(expr):
        ch = expr[i]
        if ch == "(":
            depth += 1
        elif ch == ")":
            depth = max(0, depth - 1)
        elif depth == 0:
            if ch == "." and expr.startswith("..", i):
                best = min(best, LUA_PRECEDENCE[".."])
                i += 1
            elif ch in LUA_PRECEDENCE:
                prev = expr[i - 1] if i > 0 else ""
                unary = ch in "+-" and (i == 0 or prev in "(,*+/%^<>=~-")
                if not unary:
                    best = min(best, LUA_PRECEDENCE[ch])
        i += 1
    return best


def _is_complete_paren_group(source: str, start: int, end: int) -> bool:
    if start >= end or source[start] != "(":
        return False
    depth = 0
    for i in range(start, end):
        if source[i] == "(":
            depth += 1
        elif source[i] == ")":
            depth -= 1
            if depth == 0:
                return i == end - 1
    return False


def _left_context(source: str, start: int, end: int) -> Tuple[Optional[int], int]:
    """Resolve the left boundary of a span.

    Returns ``(new_start, binding_precedence)``.  ``new_start`` is ``None`` when
    folding would be unsafe; ``binding_precedence`` is the precedence of the
    operator on the left that would bind the span (``0`` when the span starts an
    expression, in which case it cannot be re-bound).
    """
    complete_group = _is_complete_paren_group(source, start, end)
    i = start - 1
    while i >= 0 and source[i] in " \t\r\n":
        i -= 1
    if i < 0:
        return start, 0

    ch = source[i]
    if ch in "+-":
        # Signed run: absorb it when the first sign is unary.
        run_start = i
        j = i
        while j >= 0 and source[j] in "+- \t\r\n":
            j -= 1
        if j < 0:
            return run_start, 0
        before = source[j]
        if _WORD_RE.match(before):
            if _word_ending_at(source, j) in LUA_KEYWORDS:
                return run_start, 0
            return None, 0
        if before in "+-":
            return None, 0
        if before in _UNSAFE_LEFT_OPS or before in "/%*^":
            # `a*-1+2`: the sign is unary but the enclosing operator binds the
            # span, so it may only cover operators that bind tighter.
            if complete_group:
                return start, 0
            return run_start, LUA_PRECEDENCE.get(before, 0)
        if before in _EXPR_START_PUNCT or before in "<>=~":
            if before == "." and not source.startswith("..", j):
                return None, 0
            return run_start, 0
        return None, 0

    if _WORD_RE.match(ch):
        if _word_ending_at(source, i) in LUA_KEYWORDS:
            return start, 0
        # `f(...)` is a call: replacing the argument list with a bare number
        # would change the syntax even though the value is the same.
        return None, 0

    if ch in _UNSAFE_LEFT_OPS or ch in "/%*^":
        if complete_group:
            return start, 0
        return None, 0
    if ch in _EXPR_START_PUNCT:
        if ch == "." and not source.startswith("..", i):
            return None, 0
        return start, 0
    return None, 0


def _fold_one(source: str, editor: _Editor, start: int, end: int) -> bool:
    """Try to fold ``source[start:end]``; returns True when it was replaced."""
    while end > start and source[end - 1] in " \t\r\n":
        end -= 1
    if end - start < 3:
        return False
    new_start, binding = _left_context(source, start, end)
    if new_start is None:
        return False
    start = new_start
    # A fully parenthesised span is an atomic expression: no neighbouring
    # operator can rebind it, which is why `a*(1+2)` may fold but `a*1+2` may not.
    atomic = _is_complete_paren_group(source, start, end)

    candidate = source[start:end]
    if len(candidate) < 3:
        return False

    if not atomic:
        k = end
        while k < len(source) and source[k] in " \t\r\n":
            k += 1
        if k < len(source):
            nxt = source[k]
            if nxt in _UNSAFE_RIGHT_OPS:
                return False
            if nxt == "." and not source.startswith("..", k):
                return False

    value = evaluate_constant(candidate)
    if value is None:
        return False
    if not atomic:
        precedence = _top_level_min_precedence(candidate)
        if binding > 0 and precedence <= binding:
            return False

    replacement = format_number(value)
    if replacement == candidate:
        return False
    if start > 0 and _WORD_RE.match(source[start - 1]) and replacement[0].isalnum():
        replacement = " " + replacement
    if end < len(source) and _WORD_RE.match(source[end]) and replacement[-1:].isalnum():
        replacement = replacement + " "
    editor.replace(start, end, replacement)
    return True


def _fold_constants(source: str, mask: Optional[str] = None) -> Tuple[int, str]:
    """Fold pure numeric expressions such as ``-9378+9379`` or ``(2+3)*7``.

    Conservative on purpose: everything that cannot be proven to be a complete
    sub-expression is left untouched.  This turns

        H=H and-459339+1691705 or-1039381+14652065 end
        for u=-9378+9379,#z,-673266-(-673267)do

    into

        H=H and 1232366 or 13612684 end
        for u=1,#z,1 do

    while ``x-1+2`` (left associative subtraction), ``a*1+2`` (the span is bound
    by ``*``) and ``2^3^x`` are preserved verbatim.

    Returns ``(number_of_folds, new_source)``.  Each pass runs on the text it
    produced, so the offsets recorded by :class:`_Editor` are always valid.
    """
    text = source
    folded = 0
    # One pass exposes nested constants that sat inside a bigger span, so the
    # pass repeats until it stops changing the source (bounded).
    for _ in range(4):
        current_mask = mask if (mask is not None and text == source) else mask_lua(text)
        editor = _Editor(text)
        changed = 0
        for match in re.finditer(r"[()\d][-+*/%^()\d\s]*", current_mask):
            end = match.end()
            while end > match.start() and text[end - 1] in " \t\r\n":
                end -= 1
            if end <= match.start():
                continue
            ends = [end]
            for i in range(end - 1, match.start(), -1):
                ch = text[i]
                if ch == ")":
                    ends.append(i + 1)
                    ends.append(i)
                elif ch in "-+*/%^":
                    ends.append(i)
                if len(ends) >= 16:
                    break
            starts = [match.start()]
            for i in range(match.start() + 1, end):
                if len(starts) >= 4:
                    break
                ch = text[i]
                if ch != "(" and not ch.isdigit():
                    continue
                if _WORD_RE.match(text[i - 1]):
                    continue  # would start in the middle of a number/identifier
                starts.append(i)
            done = False
            budget = 16
            for candidate_start in starts:
                for candidate_end in ends:
                    if budget <= 0:
                        break
                    if candidate_end - candidate_start < 3:
                        continue
                    first = text[candidate_start]
                    if not (first == "(" or first == ")" or first.isdigit()):
                        continue
                    candidate = text[candidate_start:candidate_end]
                    if not cheap_candidate_ok(candidate):
                        budget -= 1
                        continue
                    budget -= 1
                    if _fold_one(text, editor, candidate_start, candidate_end):
                        changed += 1
                        done = True
                        break
                if done:
                    break
        folded += changed
        text = editor.render()
        if not changed:
            break
    return folded, text


def index_from_arg(resolver: Dict[str, Any]):
    """Return the ``arg -> pool index`` mapping of a resolver description.

    ``analyze()`` attaches a ready-made closure, but the helper is also called
    directly (tests, tools), so derive it from ``op``/``offset`` when missing.
    """
    function = resolver.get("index_from_arg")
    if callable(function):
        return function
    offset = int(resolver.get("offset", 0))
    op = resolver.get("op", "-")
    if op == "+":
        return lambda arg, off=offset: arg + off
    return lambda arg, off=offset: arg - off


def inline_resolver_calls(
    source: str,
    mask: str,
    resolver: dict,
    pool_values: Sequence[Optional[str]],
) -> Tuple[int, str]:
    """Replace every ``resolver(<const>)`` call with the decoded literal.

    Returns ``(number_of_calls_inlined, new_source)``.
    """
    editor = _Editor(source)
    name = resolver["name"]
    inlined = 0
    pattern = re.compile(rf"(?<![\w.:]){re.escape(name)}\s*\(")
    for match in pattern.finditer(mask):
        open_index = match.end() - 1
        span = balanced_span(mask, open_index, "(", ")")
        if not span:
            continue
        _, close = span
        arg_text = source[open_index + 1 : close - 1]
        value = evaluate_constant(arg_text)
        if value is None or value != int(value):
            continue
        index = index_from_arg(resolver)(int(value))
        if index is None or not (1 <= index <= len(pool_values)):
            continue
        decoded = pool_values[index - 1]
        if decoded is None:
            continue
        if not decoded:
            editor.replace(match.start(), close, '""')
            inlined += 1
            continue
        editor.replace(match.start(), close, lua_string_literal(decoded))
        inlined += 1
    return inlined, editor.render()


# ------------------------------------------------------------------ public API


def analyze(
    source: str,
    *,
    decode: bool = True,
    inline: bool = True,
    fold: bool = True,
    max_pool_bytes: int = 256 * 1024 * 1024,
) -> StaticLayerResult:
    """Decode the WRD constant layer and (optionally) rewrite the source.

    ``decode=True``  build the decoded constant table
    ``inline=True``  replace ``resolver(<const>)`` calls with literals
    ``fold=True``    fold constant arithmetic expressions
    """
    result = StaticLayerResult(ok=False)
    if not source:
        result.reason = "empty source"
        return result

    mask = mask_lua(source)
    if len(source) > max_pool_bytes:
        result.warnings.append("source very large; static pass still O(n)")

    # ---- locate the pool ----
    best: Optional[Tuple[int, str, int, int]] = None
    for name, start, end in _find_pool_tables(mask):
        slice_mask = mask[start:end]
        count = len(ESCAPED_DECIMAL_STRING_RE.findall(source[start:end]))
        if count or slice_mask.count(",") > 8:
            if best is None or count > best[0]:
                best = (count, name, start, end)
    if best is None or best[0] == 0:
        result.reason = "no escaped-decimal string pool found"
        return result

    count, pool_name, pool_start, pool_end = best
    items = _pool_entries(mask, source, pool_start, pool_end)
    if not items:
        result.reason = "string pool is empty"
        return result

    # Resolver indices address *every* top level item of the pool, so a pool
    # containing nested tables would shift the index space.  Detect that and
    # refuse to inline (decoding stays valid, inlining would be wrong).
    all_items = _pool_items(mask, source, pool_start, pool_end)
    index_safe = len(all_items) == len(items)
    if not index_safe:
        result.warnings.append(
            f"pool contains non-string items ({len(all_items) - len(items)}); resolver inlining disabled"
        )
        inline = False

    pool_text = [unescape_lua_string(source[s + 1 : e - 1]) for s, e in items]
    result.pool = PoolInfo(name=pool_name, start=pool_start, end=pool_end, entries=len(pool_text))
    result.notes.append(f"pool '{pool_name}' with {len(pool_text)} entries")

    if not decode:
        result.ok = True
        result.reason = "pool located (decode disabled)"
        return result

    # ---- alphabet(s) and shuffles ----
    alphabets: Dict[str, Dict[str, int]] = {}
    for name, start, end in _find_pool_tables(mask):
        mapping = _parse_alphabet(mask, source, start, end)
        if len(mapping) >= 40:
            alphabets[name] = mapping
    if not alphabets:
        result.reason = "custom base64 alphabet not found"
        return result
    result.pool.alphabets = alphabets
    # the most plausible alphabet: the one with most distinct values <= 85
    alphabet = max(alphabets.values(), key=lambda m: (len(m), len(set(m.values()))))
    result.notes.append(f"alphabet of {len(alphabet)} characters")

    shuffles = _parse_shuffles(mask)
    result.pool.shuffles = shuffles
    if shuffles:
        result.notes.append("shuffles: " + ", ".join(f"{a}-{b}" for a, b in shuffles))

    _apply_shuffles(pool_text, shuffles)

    decoded: List[Optional[str]] = []
    failures = 0
    for text in pool_text:
        if not text:
            decoded.append("")
            continue
        try:
            raw = decode_custom_base64(text, alphabet)
        except Exception:
            raw = b""
        if raw:
            decoded.append(raw.decode("latin-1"))
        elif text and all(32 <= ord(c) < 127 for c in text) and "=" in text:
            decoded.append(None)
            failures += 1
        else:
            decoded.append(None)
    result.decoded = decoded
    if failures:
        result.warnings.append(f"{failures} pool entries could not be decoded")

    # ---- resolver ----
    resolver: Optional[dict] = None
    for match in RESOLVER_DEF_RE.finditer(mask):
        name, param, pool_var, indexed, op, offset_text = (
            match.group(1) or match.group(3), match.group(2) or match.group(4),
            match.group(5), match.group(6), match.group(7), match.group(8),
        )
        if param != indexed:
            continue
        offset = evaluate_constant(offset_text)
        if offset is None:
            continue
        offset_int = int(offset)
        if op == "-":
            index_from_arg = lambda arg, off=offset_int: arg - off  # noqa: E731
        else:
            index_from_arg = lambda arg, off=offset_int: arg + off  # noqa: E731
        resolver = {
            "name": name,
            "param": param,
            "pool": pool_var,
            "offset": offset_int,
            "op": op,
            "index_from_arg_repr": f"arg {op} {offset_int}",
        }
        break
    if resolver is None:
        # some builds omit the wrapper; fall back to a direct pool index
        resolver = {
            "name": pool_name,
            "param": "i",
            "pool": pool_name,
            "offset": 0,
            "op": "-",
            "index_from_arg_repr": "arg",
            "synthetic": True,
        }
        result.warnings.append("resolver function not found; assuming direct pool indexing")
    resolver["index_from_arg"] = (lambda arg, off=resolver["offset"], op=resolver["op"]: arg - off if op == "-" else arg + off)
    result.resolver = {k: v for k, v in resolver.items() if k != "index_from_arg"}

    # ---- rewrite ----
    if inline or fold:
        text = source
        inlined = 0
        if inline:
            inlined, text = inline_resolver_calls(text, mask, resolver, decoded)
        folded = 0
        if fold:
            folded, text = _fold_constants(text)
        result.inlined_calls = inlined
        result.folded_expressions = folded
        result.output = text
        result.notes.append(f"inlined {inlined} resolver call(s), folded {folded} constant expression(s)")

    result.ok = True
    result.reason = "ok"
    return result


__all__ = [
    "PoolInfo",
    "StaticLayerResult",
    "analyze",
    "decode_custom_base64",
    "escape_lua_string",
    "evaluate_constant",
    "format_number",
    "inline_resolver_calls",
    "lua_string_literal",
    "mask_lua",
    "unescape_lua_string",
]
