r"""Luau to Lua source normalisation.

Luau (Roblox's Lua dialect) accepts a syntax superset of the Lua releases that
the vendored sandbox can execute: numeric separators, the ``continue`` control
statement, type annotations and a handful of aliases.  Every obfuscator in the
Luraph family emits Luau flavoured wrappers, so the devirtualiser needs a
faithful lowering step before a wrapper may be loaded into a Lua state.

The implementation works on the token stream produced by
:func:`core.deobfuscator.tokenize` instead of regular expressions, so string
literals, comments and long brackets can never be rewritten by accident.  All
edits are pure source spans: untouched text keeps its original formatting.

Supported transformations
-------------------------

``numerals``
    ``0b101_010`` / ``0X14_`` / ``1_000`` are rewritten to spellings the
    reference implementation accepts: binaries become exact decimals (or, past
    2^53, floats), separators are removed.  Unparseable numerals are reported
    instead of being touched.
``string_escapes``
    Short strings whose escapes only Luau accepts (``'\!'``) are decoded and
    re-emitted with portable numeric escapes; the bytes are preserved exactly.
``not_equal_alias``
    ``!=`` (accepted by Luau) becomes ``~=``.
``compound_assignment``
    ``x += 1`` / ``t[k] ..= s`` / ``a[f()] -= 1`` become plain assignments.
    Targets are repeated in the lowered form, so index expressions that could
    be evaluated twice with side effects are hoisted into temporaries first.
``continue``
    Luau's ``continue`` is lowered per enclosing loop without changing
    semantics, including loops whose bodies also contain ``break``::

        repeat BODY until COND  ->  repeat
                                      for C = 1, 1 do BODY' end   -- continue: break
                                      if B then break end          -- break: B=true break
                                    until COND

        while COND do BODY end  ->  local B = false
                                    while COND do
                                      repeat BODY' until true
                                      if B then break end
                                    end

    In the ``repeat`` form ``continue`` becomes ``do break end``, which leaves
    the one-shot wrapper and falls into the ``until`` test exactly like Luau.
    The ``for``/``while`` form uses the same trick around the whole body.
``type_annotations``
    Declaration types (``local x: T``), parameter types (``function f(a: T)``),
    return types (``function f(): T``) and ``expr :: T`` casts are removed.
    The scanner understands generics, table/function/union types and string
    literal types; anything it cannot prove harmless raises
    :class:`UnsupportedLuauSyntax` instead of producing silently broken output.
``type_declarations``
    ``type X = ...`` / ``export type X = ...`` statements are dropped.

Constructs that are *not* supported raise :class:`UnsupportedLuauSyntax` with a
``line:column`` location, so callers never receive corrupted source.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Callable, Iterable

from ..deobfuscator import (
    MAX_SOURCE_BYTES,
    Token,
    interpolated_string_end,
    tokenize,
)

__all__ = ["Normalization", "UnsupportedLuauSyntax", "normalize_luau", "luau_only_features"]

#: token indexes of loops are tracked with this many candidates at most; a
#: pathological nesting depth beyond it is treated as unsupported input.
_MAX_NESTING = 512

_LOOP_KEYWORDS = frozenset({"for", "while", "repeat"})
_BLOCK_OPENERS = frozenset({"function", "if", "do", "for", "while", "repeat"})
_TYPE_ATOMS = frozenset(
    {
        "nil", "true", "false", "typeof", "keyof", "string", "number", "boolean",
        "any", "unknown", "never", "void", "thread", "buffer", "vector", "userdata",
        "function", "table", "self",
    }
)
_TYPE_EXPR_TOKENS = frozenset(
    {"|", "&", "?", ".", "->", "::", "*", "=>", "..."}
)
_STATEMENT_KEYWORDS = frozenset(
    {
        "do", "end", "then", "else", "elseif", "return", "local", "for", "while",
        "repeat", "until", "break", "continue", "if", "function", "for",
    }
)
_VALID_NUMERAL = re.compile(
    r"^(?:"
    r"0[xX][0-9a-fA-F]+(?:\.[0-9a-fA-F]*)?(?:[pP][+-]?\d+)?|"
    r"0[bB][01]+|"
    r"\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|"
    r"\.\d+(?:[eE][+-]?\d+)?"
    r")$"
)


class UnsupportedLuauSyntax(ValueError):
    """Raised when a Luau construct cannot be lowered faithfully."""

    def __init__(self, message: str, *, source: str, offset: int) -> None:
        line = source.count("\n", 0, offset) + 1
        column = offset - (source.rfind("\n", 0, offset) + 1) + 1
        super().__init__(f"{message} (line {line}, column {column})")
        self.offset = offset
        self.line = line
        self.column = column


@dataclass(frozen=True)
class Normalization:
    """Result of :func:`normalize_luau`."""

    source: str
    applied: tuple[str, ...]
    notes: tuple[str, ...]

    @property
    def changed(self) -> bool:
        return bool(self.applied)


@dataclass
class _Edit:
    start: int
    end: int
    text: str
    order: int = 0

    def key(self) -> tuple[int, int, int]:
        return (self.start, self.order, self.end)


@dataclass
class _Loop:
    kind: str
    keyword: int
    body_start: int = -1
    closer: int = -1
    func_depth: int = 0
    continues: list[int] = None  # type: ignore[assignment]
    breaks: list[int] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        if self.continues is None:
            self.continues = []
        if self.breaks is None:
            self.breaks = []


def _apply_edits(source: str, edits: Iterable[_Edit]) -> str:
    ordered = sorted(edits, key=_Edit.key)
    pieces: list[str] = []
    cursor = 0
    for edit in ordered:
        if edit.start < cursor:
            # Overlapping edits would corrupt the source; the passes below are
            # written so that this cannot happen, so treat it as a bug guard.
            raise AssertionError(f"overlapping normalisation edits at offset {edit.start}")
        pieces.append(source[cursor : edit.start])
        pieces.append(edit.text)
        cursor = edit.end
    pieces.append(source[cursor:])
    return "".join(pieces)


def _line_column(source: str, offset: int) -> str:
    line = source.count("\n", 0, offset) + 1
    column = offset - (source.rfind("\n", 0, offset) + 1) + 1
    return f"line {line}, column {column}"


# ---------------------------------------------------------------------------
# pass: numeric separators
# ---------------------------------------------------------------------------


def _convert_numeral(text: str) -> str | None:
    """Return a Lua-compatible spelling of a Luau numeral, or ``None``.

    Luau accepts binary literals (``0b1010``) and digit separators (``1_000``);
    no release of the reference implementation does, so binaries are converted
    to an exact decimal (or float) spelling and separators are removed.
    """
    lowered = text.lower()
    if lowered.startswith("0b"):
        digits = lowered[2:].replace("_", "")
        if not digits or any(char not in "01" for char in digits):
            return None
        value = int(digits, 2)
        if value <= 2**53:
            return str(value)
        return repr(float(value))
    if "_" not in text:
        return None
    cleaned = text.replace("_", "")
    if not _VALID_NUMERAL.match(cleaned):
        return None
    return cleaned


def _normalise_numerals(source: str, tokens: list[Token], edits: list[_Edit], notes: list[str]) -> None:
    for token in tokens:
        if token.kind != "number":
            continue
        replacement = _convert_numeral(token.text)
        if replacement is None:
            if "_" in token.text or token.text[:2].lower() == "0b":
                notes.append(
                    f"kept malformed numeral {token.text!r} at {_line_column(source, token.start)}"
                )
            continue
        if replacement != token.text:
            # ``0b1..x`` becomes ``1..x`` which the Lua lexer reads as a
            # malformed numeral; keep a separator when the shortened spelling
            # would touch the following token.
            following = source[token.end : token.end + 1]
            if following.isalnum() or following == "_" or following == ".":
                replacement += " "
            edits.append(_Edit(token.start, token.end, replacement))


# ---------------------------------------------------------------------------
# pass: ``!=`` alias
# ---------------------------------------------------------------------------


def _normalise_not_equal(source: str, tokens: list[Token], edits: list[_Edit]) -> None:
    for index, token in enumerate(tokens[:-1]):
        if token.text != "!" or token.kind != "symbol":
            continue
        following = tokens[index + 1]
        if following.text != "=" or following.start != token.end:
            continue
        edits.append(_Edit(token.start, following.end, "~="))


# ---------------------------------------------------------------------------
# pass: string escapes
# ---------------------------------------------------------------------------

_SIMPLE_ESCAPES = {
    "a": 7,
    "b": 8,
    "f": 12,
    "n": 10,
    "r": 13,
    "t": 9,
    "v": 11,
    "\\": 92,
    '"': 34,
    "'": 39,
}


def _decode_short_string(inner: str, *, strict: bool) -> bytes:
    """Decode the body of a short Lua string literal into bytes.

    ``strict=True`` implements the Lua 5.2+ escape set and raises on anything it
    does not recognise.  ``strict=False`` implements the permissive Luau /
    Lua 5.1 behaviour where an unknown escape simply yields the escaped byte.
    """
    out = bytearray()
    index = 0
    length = len(inner)
    while index < length:
        character = inner[index]
        if character != "\\":
            out.extend(character.encode("latin-1", "replace"))
            index += 1
            continue
        index += 1
        if index >= length:
            raise ValueError("trailing backslash in string literal")
        escape = inner[index]
        if escape in _SIMPLE_ESCAPES:
            out.append(_SIMPLE_ESCAPES[escape])
            index += 1
        elif escape == "\n":
            out.append(10)
            index += 1
        elif escape == "\r":
            out.append(10)
            index += 1
            if index < length and inner[index] == "\n":
                index += 1
        elif escape.isdigit():
            digits = escape
            index += 1
            while len(digits) < 3 and index < length and inner[index].isdigit():
                digits += inner[index]
                index += 1
            value = int(digits)
            if value > 255:
                if strict:
                    raise ValueError("decimal escape too large")
                value &= 0xFF
            out.append(value)
        elif escape == "x":
            if not strict:
                pass
            hex_digits = inner[index + 1 : index + 3]
            if len(hex_digits) < 2 or any(char not in "0123456789abcdefABCDEF" for char in hex_digits):
                if strict:
                    raise ValueError("hexadecimal escape requires two digits")
                out.append(ord("x"))
                index += 1
                continue
            out.append(int(hex_digits, 16))
            index += 3
        elif escape == "z":
            index += 1
            while index < length and inner[index].isspace():
                index += 1
        elif escape == "u":
            if index + 1 >= length or inner[index + 1] != "{":
                if strict:
                    raise ValueError("unicode escape requires braces")
                out.append(ord("u"))
                index += 1
                continue
            closing = inner.find("}", index + 2)
            if closing < 0:
                if strict:
                    raise ValueError("unterminated unicode escape")
                out.append(ord("u"))
                index += 1
                continue
            codepoint = int(inner[index + 2 : closing], 16)
            out.extend(chr(codepoint).encode("utf-8"))
            index = closing + 1
        else:
            if strict:
                raise ValueError(f"invalid escape sequence '\\{escape}'")
            out.extend(escape.encode("latin-1", "replace"))
            index += 1
    return bytes(out)


def _encode_short_string(data: bytes, quote: str) -> str:
    pieces = [quote]
    for byte in data:
        if byte == ord(quote) or byte == 0x5C:
            pieces.append("\\" + chr(byte))
        elif 32 <= byte < 127:
            pieces.append(chr(byte))
        else:
            pieces.append(f"\\{byte:03d}")
    pieces.append(quote)
    return "".join(pieces)


def _normalise_string_escapes(
    source: str, tokens: list[Token], edits: list[_Edit], notes: list[str]
) -> None:
    for token in tokens:
        if token.kind != "string":
            continue
        text = token.text
        if not text[:1] in ('"', "'") or text[-1:] != text[:1] or len(text) < 2:
            continue  # long strings have no escapes
        inner = text[1:-1]
        try:
            _decode_short_string(inner, strict=True)
            continue
        except ValueError:
            pass
        try:
            data = _decode_short_string(inner, strict=False)
        except ValueError:
            notes.append(
                f"kept string with undecodable escapes at {_line_column(source, token.start)}"
            )
            continue
        edits.append(_Edit(token.start, token.end, _encode_short_string(data, text[0])))


# ---------------------------------------------------------------------------
# pass: compound assignments
# ---------------------------------------------------------------------------

_COMPOUND_OPERATORS = {
    "+=": "+",
    "-=": "-",
    "*=": "*",
    "/=": "/",
    "//=": "//",
    "%=": "%",
    "^=": "^",
    "..=": "..",
}

#: Tokens that cannot appear inside a statement's right-hand side expression at
#: nesting depth zero.  ``,``/``)``/``]``/``}`` only show up for malformed input
#: and are treated as terminators as well.
_RHS_TERMINATORS = frozenset(
    {
        ";", ",", ")", "]", "}", "end", "else", "elseif", "until", "do", "then",
        "local", "if", "for", "while", "repeat", "return", "break", "continue",
    }
)


def _assignment_target_start(source: str, tokens: list[Token], end_index: int) -> int:
    """Token index of the first token of a Luau assignment target."""
    index = end_index
    while index >= 0:
        token = tokens[index]
        if token.text == "]":
            depth = 0
            while index >= 0:
                if tokens[index].text == "]":
                    depth += 1
                elif tokens[index].text == "[":
                    depth -= 1
                    if depth == 0:
                        break
                index -= 1
            if depth != 0 or index < 0:
                raise UnsupportedLuauSyntax(
                    "unbalanced index in assignment target", source=source, offset=token.start
                )
            index -= 1
            continue
        if token.kind == "identifier":
            if index - 1 >= 0 and tokens[index - 1].text == ".":
                index -= 2
                continue
            return index
        raise UnsupportedLuauSyntax(
            f"unsupported assignment target near {token.text!r}", source=source, offset=token.start
        )
    raise UnsupportedLuauSyntax(
        "assignment target not found", source=source, offset=tokens[end_index].start
    )


def _assignment_rhs_end(source: str, tokens: list[Token], start_index: int) -> int:
    """Token index just past the right-hand side of an assignment."""
    depth = 0
    index = start_index
    while index < len(tokens):
        text = tokens[index].text
        if depth == 0 and text in _RHS_TERMINATORS:
            break
        if text in ("(", "[", "{"):
            depth += 1
        elif text in (")", "]", "}"):
            depth -= 1
        index += 1
    if index == start_index:
        raise UnsupportedLuauSyntax(
            "missing right-hand side", source=source, offset=tokens[start_index - 1].start
        )
    if depth != 0:
        raise UnsupportedLuauSyntax(
            "unbalanced expression in assignment", source=source, offset=tokens[start_index].start
        )
    if tokens[start_index].text == "function":
        raise UnsupportedLuauSyntax(
            "function expression is not a valid right-hand side", source=source, offset=tokens[start_index].start
        )
    return index


def _index_spans(source: str, tokens: list[Token], start: int, end: int) -> list[tuple[int, int]]:
    """Bracket spans (``[...]``) inside the assignment target's token range."""
    spans: list[tuple[int, int]] = []
    index = start
    while index < end:
        if tokens[index].text == "[":
            depth = 0
            open_index = index
            while index < end:
                if tokens[index].text == "[":
                    depth += 1
                elif tokens[index].text == "]":
                    depth -= 1
                    if depth == 0:
                        break
                index += 1
            spans.append((open_index, index))
        index += 1
    return spans


_UNARY_PREFIXES = frozenset({"-", "not", "#"})
_BRACKET_PAIRS = {"(": ")", "[": "]", "{": "}"}
_CLOSING_BRACKETS = frozenset(_BRACKET_PAIRS.values())


def _balanced_end(tokens: list[Token], index: int) -> int | None:
    """Index just past the bracket that matches the opener at ``index``."""
    closer = _BRACKET_PAIRS.get(tokens[index].text)
    if closer is None:
        return None
    closers = _CLOSING_BRACKETS
    depth = 0
    while index < len(tokens):
        text = tokens[index].text
        if text in _BRACKET_PAIRS:
            depth += 1
        elif text in closers:
            depth -= 1
            if depth == 0:
                return index + 1
        index += 1
    return None


def _balanced_start(tokens: list[Token], index: int) -> int | None:
    """Index of the opener that matches the closer at ``index``."""
    opener_for = {value: key for key, value in _BRACKET_PAIRS.items()}
    opener = opener_for.get(tokens[index].text)
    if opener is None:
        return None
    depth = 0
    while index >= 0:
        text = tokens[index].text
        if text in _CLOSING_BRACKETS:
            depth += 1
        elif text in _BRACKET_PAIRS:
            depth -= 1
            if depth == 0:
                return index
        index -= 1
    return None


def _primary_end(tokens: list[Token], index: int) -> int | None:
    """Index just past the primary expression starting at ``index``."""
    while index < len(tokens) and tokens[index].text in _UNARY_PREFIXES:
        index += 1
    if index >= len(tokens):
        return None
    token = tokens[index]
    if token.text in _BRACKET_PAIRS:
        following = _balanced_end(tokens, index)
        if following is None:
            return None
        index = following
    elif token.kind in {"identifier", "number", "string"} or token.text in {
        "nil",
        "true",
        "false",
        "...",
    }:
        index += 1
    else:
        return None
    return _suffixes_end(tokens, index)


def _suffixes_end(tokens: list[Token], index: int) -> int | None:
    """Consume ``.name``, ``[expr]``, ``(args)``, ``:name(args)`` and ``f "s"``."""
    while index < len(tokens):
        text = tokens[index].text
        if text == "." and index + 1 < len(tokens) and tokens[index + 1].kind == "identifier":
            index += 2
        elif text in _BRACKET_PAIRS:
            following = _balanced_end(tokens, index)
            if following is None:
                return None
            index = following
        elif text == ":" and index + 1 < len(tokens) and tokens[index + 1].kind == "identifier":
            index += 2
        elif tokens[index].kind == "string":
            index += 1
        else:
            break
    return index


def _primary_start(tokens: list[Token], index: int) -> int | None:
    """Index of the first token of the primary expression ending at ``index``."""
    if index < 0:
        return None
    while True:
        text = tokens[index].text
        if text in _CLOSING_BRACKETS:
            opening = _balanced_start(tokens, index)
            if opening is None:
                return None
            index = opening
            if index == 0:
                break
            previous = tokens[index - 1]
            # ``f(...)`` / ``t[k]``: the bracket is a suffix, keep walking back.
            if previous.kind in {"identifier", "string"} or previous.text in _CLOSING_BRACKETS:
                index -= 1
                continue
            break
        if tokens[index].kind == "string" and index > 0:
            previous = tokens[index - 1]
            if previous.kind == "identifier" or previous.text in _CLOSING_BRACKETS:
                index -= 1
                continue
        if tokens[index].kind == "identifier" or tokens[index].kind == "number":
            if index >= 2 and tokens[index - 1].text == ".":
                index -= 2
                continue
            break
        if text in {"nil", "true", "false", "..."}:
            break
        # Anonymous functions and anything else are left alone: a wrong span
        # would silently change the program.
        return None
    while index > 0 and tokens[index - 1].text in _UNARY_PREFIXES:
        index -= 1
    return index


def _first_floor_division(tokens: list[Token]) -> tuple[int, int, int] | None:
    """Offsets of ``left // right`` for the first floor division, or ``None``.

    Returns ``(left_start, right_end, operator_offset)`` in character offsets.
    """
    for index, token in enumerate(tokens):
        if token.text != "//" or token.kind != "symbol":
            continue
        left = _primary_start(tokens, index - 1)
        right = _primary_end(tokens, index + 1)
        if left is None or right is None:
            continue
        return tokens[left].start, tokens[right - 1].end, token.start
    return None


def _lower_floor_division(
    source: str, notes: list[str], *, limit: int = 512
) -> tuple[str, int]:
    """Rewrite Luau's ``a // b`` as ``math.floor(a / b)``.

    Lua 5.1 has no floor division, and Luraph's Luau output leans on it hard
    (``N[j[J]] // x[J]``).  One occurrence is rewritten per round so that a
    chain (``a // b // c``) nests correctly instead of producing overlapping
    edits; the ``//`` operator and ``*`` share precedence, and wrapping the
    whole product as the call argument keeps that intact.
    """
    text = source
    count = 0
    for _ in range(limit):
        tokens = tokenize(text)
        found = _first_floor_division(tokens)
        if found is None:
            break
        left_start, right_end, operator_offset = found
        inner = text[left_start:right_end].replace("//", "/", 1)
        try:
            text = text[:left_start] + f"math.floor({inner})" + text[right_end:]
        except Exception as exc:  # noqa: BLE001 - never corrupt the source
            notes.append(f"floor division at offset {operator_offset} was left as is ({exc})")
            break
        count += 1
    if count:
        notes.append(f"{count} floor division(s) rewritten as math.floor(a / b)")
    return text, count


def _lower_one_interpolated(source: str, start: int, end: int) -> str:
    """Rewrite one Luau interpolated string as a Lua concatenation.

    `` `hp: {x}/100` `` becomes ``("hp: " .. tostring(x) .. "/100")``.  The
    literal segments are decoded with the permissive escape rules and re-emitted
    with portable numeric escapes, so the bytes survive exactly.
    """
    parts: list[tuple[str, str]] = []
    index = start + 1
    literal_start = index
    while index < end - 1:
        character = source[index]
        if character == "\\":
            index += 2
            continue
        if character == "{":
            parts.append(("text", source[literal_start:index]))
            depth = 1
            cursor = index + 1
            while cursor < end - 1 and depth:
                current = source[cursor]
                if current == "\\":
                    cursor += 2
                    continue
                if current == "{":
                    depth += 1
                elif current == "}":
                    depth -= 1
                    if depth == 0:
                        break
                elif current == "`":
                    cursor = interpolated_string_end(source, cursor) - 1
                cursor += 1
            if depth:
                raise ValueError("unterminated interpolation")
            parts.append(("expr", source[index + 1:cursor]))
            index = cursor + 1
            literal_start = index
            continue
        index += 1
    parts.append(("text", source[literal_start:end - 1]))

    pieces: list[str] = []
    for kind, text in parts:
        if kind == "text":
            if not text:
                continue
            data = _decode_short_string(text, strict=False)
            pieces.append(_encode_short_string(data, '"'))
        else:
            pieces.append(f"tostring({text})")
    if not pieces:
        return '""'
    if len(pieces) == 1:
        return pieces[0]
    return "(" + " .. ".join(pieces) + ")"


def _lower_interpolated_strings(
    source: str, tokens: list[Token], edits: list[_Edit], notes: list[str]
) -> None:
    """Lower every Luau interpolated string in one pass."""
    for token in tokens:
        if token.kind != "string" or not token.text.startswith("`"):
            continue
        try:
            replacement = _lower_one_interpolated(source, token.start, token.end)
        except Exception as exc:  # noqa: BLE001 - reported as unsupported
            raise UnsupportedLuauSyntax(
                f"string interpolation could not be lowered: {exc}",
                source=source,
                offset=token.start,
            ) from exc
        edits.append(_Edit(token.start, token.end, replacement))
    if edits:
        notes.append(f"{len(edits)} interpolated string(s) lowered to concatenations")


#: Keywords that cannot continue an expression: seeing one at the current
#: depth means the expression before it has ended.
_EXPRESSION_STOP_WORDS = frozenset({
    "then", "else", "elseif", "end", "do", "until", "repeat", "local", "return",
    "for", "while", "break", "continue", "in",
})
_BLOCK_OPENERS = frozenset({"function", "if", "for", "while", "do", "repeat"})


def _is_if_expression(tokens: list[Token], index: int, if_expression_depths: list[int],
                      bracket_depth: int) -> bool:
    """True when the ``if`` at ``index`` opens Luau's if-*expression*."""
    previous = tokens[index - 1].text if index else ""
    if previous in _EXPRESSION_PRECEDERS:
        return True
    return (
        previous in ("then", "else")
        and bool(if_expression_depths)
        and if_expression_depths[-1] == bracket_depth
    )


def _if_expression_span(
    tokens: list[Token], index: int, bracket_depth: int
) -> tuple[int, int, int] | None:
    """``(then_index, else_index, end_index)`` for the if-expression at ``index``.

    ``end_index`` is one past the whole expression.  ``else_index`` is the index
    of the ``else``/``elseif`` token; for ``elseif`` the branch is itself an
    if-expression and its span is what ends this one.
    """
    depths: list[int] = [bracket_depth]
    depth = bracket_depth
    cursor = index + 1
    then_index: int | None = None
    while cursor < len(tokens):
        token = tokens[cursor]
        text = token.text
        kind = token.kind
        if kind == "symbol":
            if text in ("(", "[", "{"):
                depth += 1
            elif text in (")", "]", "}"):
                if depth == bracket_depth:
                    return None
                depth -= 1
        elif kind == "identifier":
            if text == "if":
                if _is_if_expression(tokens, cursor, depths, depth):
                    span = _if_expression_span(tokens, cursor, depth)
                    if span is None:
                        return None
                    cursor = span[2]
                    continue
            elif text == "then" and depth == bracket_depth:
                then_index = cursor
                break
            elif text == "function":
                end = _block_end(tokens, cursor, depth)
                if end is None:
                    return None
                cursor = end
                continue
        cursor += 1
    if then_index is None:
        return None

    # Branch A runs from after ``then`` to the matching ``else``/``elseif``.
    depth = bracket_depth
    cursor = then_index + 1
    while cursor < len(tokens):
        token = tokens[cursor]
        text = token.text
        kind = token.kind
        if kind == "symbol":
            if text in ("(", "[", "{"):
                depth += 1
            elif text in (")", "]", "}"):
                if depth == bracket_depth:
                    return None
                depth -= 1
        elif kind == "identifier":
            if text == "if":
                if _is_if_expression(tokens, cursor, depths, depth):
                    span = _if_expression_span(tokens, cursor, depth)
                    if span is None:
                        return None
                    cursor = span[2]
                    continue
            elif text in ("else", "elseif") and depth == bracket_depth:
                if text == "elseif":
                    # ``elseif c then a else b`` is a nested if-expression.
                    span = _if_expression_span(tokens, cursor - 1, bracket_depth)
                    if span is None:
                        return None
                    return then_index, cursor, span[2]
                end = _expression_end(tokens, cursor + 1, bracket_depth, depths)
                if end is None:
                    return None
                return then_index, cursor, end
            elif text == "function":
                end = _block_end(tokens, cursor, depth)
                if end is None:
                    return None
                cursor = end
                continue
        cursor += 1
    return None


#: Symbols that may follow an operand and continue an expression.
_CONTINUATION_SYMBOLS = frozenset({
    "+", "-", "*", "/", "//", "%", "^", "..", "==", "~=", "<", ">", "<=", ">=",
})
#: Words that may follow an operand and continue an expression.
_CONTINUATION_WORDS = frozenset({"and", "or"})


def _expression_end(tokens: list[Token], start: int, bracket_depth: int,
                    if_expression_depths: list[int]) -> int | None:
    """Index just past the expression starting at ``start``.

    The scan tracks whether the previous token was an *operand*: only a
    continuation (a suffix like ``(``/``[``/``.``/``:`` or a string call, an
    operator, ``and``/``or``) may follow one.  Without that check the scan ran
    straight through a statement boundary -- in ``local step = if c then 10 else
    20`` it swallowed the next statement and produced code that did not compile.
    """
    depth = bracket_depth
    cursor = start
    operand = False
    while cursor < len(tokens):
        token = tokens[cursor]
        kind = token.kind
        text = token.text
        if kind == "symbol":
            if text in ("(", "[", "{"):
                if text == "{":
                    if operand:
                        operand = False  # ``f{...}``: a call with a table
                    cursor += 1
                    depth += 1
                    continue
                operand = False
                depth += 1
                cursor += 1
                continue
            if text in (")", "]", "}"):
                if depth == bracket_depth:
                    return cursor
                depth -= 1
                operand = True
                cursor += 1
                continue
            if text in _CONTINUATION_SYMBOLS:
                operand = False
                cursor += 1
                continue
            if text in (".", ":", "::"):
                operand = True  # ``a.b`` and ``a:b`` keep the operand open
                cursor += 1
                continue
            # ``;``, ``,``, ``=`` and anything else cannot continue an operand.
            return cursor
        if kind == "number":
            if operand:
                return cursor
            operand = True
            cursor += 1
            continue
        if kind == "string":
            # A string after an operand is a call (``f "text"``); elsewhere it is
            # the operand itself.
            operand = True
            cursor += 1
            continue
        if kind == "identifier":
            if operand:
                if text in _CONTINUATION_WORDS:
                    operand = False
                    cursor += 1
                    continue
                return cursor
            if text == "if":
                span = _if_expression_span(tokens, cursor, depth)
                if span is None:
                    return None
                cursor = span[2]
                operand = True
                continue
            if text == "function":
                block_end = _block_end(tokens, cursor, depth)
                if block_end is None:
                    return None
                cursor = block_end
                operand = True
                continue
            if text in _EXPRESSION_STOP_WORDS:
                return cursor
            operand = True
            cursor += 1
            continue
        cursor += 1
    return cursor if cursor > start else None


def _block_end(tokens: list[Token], index: int, bracket_depth: int) -> int | None:
    """Index just past the ``end`` matching the block opener at ``index``."""
    depth = bracket_depth
    stack: list[str] = []
    cursor = index
    while cursor < len(tokens):
        token = tokens[cursor]
        text = token.text
        kind = token.kind
        if kind == "symbol":
            if text in ("(", "[", "{"):
                depth += 1
            elif text in (")", "]", "}"):
                depth -= 1
            cursor += 1
            continue
        if kind == "identifier":
            if text == "if":
                if stack and stack[-1] == "loop-pending" and False:  # pragma: no cover
                    pass
                span = _if_expression_span(tokens, cursor, depth)
                if span is not None:
                    cursor = span[2]
                    continue
                stack.append("if")
            elif text in ("for", "while"):
                stack.append("loop-pending")
            elif text == "do":
                if stack and stack[-1] == "loop-pending":
                    stack[-1] = "loop"
                else:
                    stack.append("do")
            elif text == "repeat":
                stack.append("repeat")
            elif text == "function":
                stack.append("function")
            elif text == "end":
                if not stack:
                    return cursor + 1
                stack.pop()
            elif text == "until":
                if stack and stack[-1] == "repeat":
                    stack.pop()
        cursor += 1
    return None


def _lower_one_if_expression(
    source: str, tokens: list[Token], index: int, bracket_depth: int
) -> tuple[int, int, str] | None:
    """``(start, end, replacement)`` for the if-expression at ``index``.

    ``elseif`` chains are collected so the whole expression becomes a single
    closure with a normal ``if``/``elseif``/``else`` chain inside -- valid Lua
    5.1, and exactly the same value semantics.
    """
    segments: list[tuple[str, str]] = []
    depths = [bracket_depth]
    cursor = index
    while True:
        opener = tokens[cursor]  # 'if' or 'elseif'

        then_index = None
        probe = cursor + 1
        depth = bracket_depth
        while probe < len(tokens):
            token = tokens[probe]
            text = token.text
            kind = token.kind
            if kind == "symbol":
                if text in ("(", "[", "{"):
                    depth += 1
                elif text in (")", "]", "}"):
                    if depth == bracket_depth:
                        return None
                    depth -= 1
            elif kind == "identifier":
                if text == "if" and _is_if_expression(tokens, probe, depths, depth):
                    span = _if_expression_span(tokens, probe, depth)
                    if span is None:
                        return None
                    probe = span[2]
                    continue
                if text == "then" and depth == bracket_depth:
                    then_index = probe
                    break
                if text == "function":
                    end = _block_end(tokens, probe, depth)
                    if end is None:
                        return None
                    probe = end
                    continue
            probe += 1
        if then_index is None:
            return None
        condition = source[opener.end:tokens[then_index].start].strip()

        else_index = None
        probe = then_index + 1
        depth = bracket_depth
        while probe < len(tokens):
            token = tokens[probe]
            text = token.text
            kind = token.kind
            if kind == "symbol":
                if text in ("(", "[", "{"):
                    depth += 1
                elif text in (")", "]", "}"):
                    if depth == bracket_depth:
                        return None
                    depth -= 1
            elif kind == "identifier":
                if text == "if" and _is_if_expression(tokens, probe, depths, depth):
                    span = _if_expression_span(tokens, probe, depth)
                    if span is None:
                        return None
                    probe = span[2]
                    continue
                if text in ("else", "elseif") and depth == bracket_depth:
                    else_index = probe
                    break
                if text == "function":
                    end = _block_end(tokens, probe, depth)
                    if end is None:
                        return None
                    probe = end
                    continue
            probe += 1
        if else_index is None:
            return None
        segments.append(
            (condition, source[tokens[then_index].end:tokens[else_index].start].strip())
        )
        if tokens[else_index].text == "elseif":
            cursor = else_index
            continue

        end_index = _expression_end(tokens, else_index + 1, bracket_depth, depths)
        if end_index is None:
            return None
        final = source[tokens[else_index].end:tokens[end_index - 1].end].strip()
        chain = ""
        for position, (branch_condition, branch) in enumerate(segments):
            keyword = "if" if position == 0 else "elseif"
            chain += f"{keyword} {branch_condition} then return {branch} "
        chain += f"else return {final} end"
        return tokens[index].start, tokens[end_index - 1].end, f"(function() {chain} end)()"


def _lower_if_expressions(source: str, notes: list[str], *, limit: int = 256) -> tuple[str, int]:
    """Lower every Luau if-expression in ``source``, innermost chains included.

    One occurrence is rewritten per round, left to right; a nested expression
    inside a branch is left for the next round, which keeps every offset valid
    without a second parser.
    """
    text = source
    count = 0
    for _ in range(limit):
        tokens = tokenize(text)
        if_expression_depths: list[int] = []
        bracket_depth = 0
        found: tuple[int, int, str] | None = None
        for index, token in enumerate(tokens):
            kind = token.kind
            if kind == "symbol":
                text_token = token.text
                if text_token in ("(", "[", "{"):
                    bracket_depth += 1
                elif text_token in (")", "]", "}"):
                    bracket_depth = max(0, bracket_depth - 1)
                    while if_expression_depths and if_expression_depths[-1] > bracket_depth:
                        if_expression_depths.pop()
                elif text_token in _IF_EXPRESSION_ENDERS:
                    while if_expression_depths and if_expression_depths[-1] >= bracket_depth:
                        if_expression_depths.pop()
                continue
            if kind != "identifier":
                continue
            if token.text in _IF_EXPRESSION_ENDERS or token.text == "end":
                while if_expression_depths and if_expression_depths[-1] >= bracket_depth:
                    if_expression_depths.pop()
                continue
            if token.text != "if":
                continue
            if not _is_if_expression(tokens, index, if_expression_depths, bracket_depth):
                continue
            found = _lower_one_if_expression(text, tokens, index, bracket_depth)
            if found is None:
                raise UnsupportedLuauSyntax(
                    "if-expression without a matching 'else'",
                    source=text,
                    offset=token.start,
                )
            break
        if found is None:
            break
        start, end, replacement = found
        text = text[:start] + replacement + text[end:]
        count += 1
    if count:
        notes.append(f"{count} if-expression(s) lowered to closures")
    return text, count




def _lower_compound_assignments(
    source: str, tokens: list[Token], edits: list[_Edit], notes: list[str]
) -> None:
    counter = 0
    for index, token in enumerate(tokens):
        base = _COMPOUND_OPERATORS.get(token.text)
        if base is None or token.kind != "symbol":
            continue
        start = _assignment_target_start(source, tokens, index - 1)
        rhs_end = _assignment_rhs_end(source, tokens, index + 1)
        rhs_text = source[tokens[index + 1].start : tokens[rhs_end - 1].end]

        # The target is repeated in the lowered statement, so index expressions
        # that could be re-evaluated with side effects (or through a metamethod)
        # are hoisted into temporaries exactly like Luau evaluates them once.
        rewrites: list[tuple[int, int, str]] = []
        prefix = ""
        for open_index, close_index in _index_spans(source, tokens, start, index):
            inner = tokens[open_index + 1 : close_index]
            if not inner:
                raise UnsupportedLuauSyntax(
                    "empty index expression", source=source, offset=tokens[open_index].start
                )
            if len(inner) == 1 and inner[0].kind in ("identifier", "number", "string"):
                continue
            name = f"__dv_key_{counter}"
            counter += 1
            expression = source[inner[0].start : inner[-1].end]
            prefix += f"local {name} = {expression}; "
            rewrites.append((inner[0].start, inner[-1].end, name))

        target_text = source[tokens[start].start : tokens[index].start]
        for span_start, span_end, text in rewrites:
            target_text = target_text.replace(
                source[span_start:span_end], text
            )
        replacement = f"{target_text} = {target_text} {base} {rhs_text}"
        if prefix:
            edits.append(_Edit(tokens[start].start, tokens[start].start, prefix, order=0))
        edits.append(_Edit(tokens[start].start, tokens[rhs_end - 1].end, replacement))


# ---------------------------------------------------------------------------
# pass: ``continue`` lowering
# ---------------------------------------------------------------------------


#: Tokens after which an ``if`` must be Luau's if-*expression*
#: (``z = if c then a else b``), which has no ``end``.
_EXPRESSION_PRECEDERS = frozenset({
    "=", ",", "(", "[", "{", "return", "..", "+", "-", "*", "/", "//", "%", "^",
    "and", "or", "not", "#", "<", ">", "<=", ">=", "==", "~=",
    "+=", "-=", "*=", "/=", "//=", "%=", "^=", "..=",
})
#: Tokens that close an if-expression started at the current bracket depth.
_IF_EXPRESSION_ENDERS = frozenset({";", ","})


def _rewrite_continue(source: str, tokens: list[Token], edits: list[_Edit], notes: list[str]) -> None:
    stack: list[tuple[str, _Loop | None]] = []
    open_loops: list[_Loop] = []
    loops: list[_Loop] = []
    func_depth = 0
    # Luau's if-expression (``local x = if c then a else b``) is not a block and
    # has no ``end``: counting it as a statement used to steal an ``end`` from
    # the enclosing loop or function, so the pass reported "unterminated 'if'
    # block" on perfectly valid Luau.  Entries are the bracket depth at which
    # the expression started; a nested ``if`` after its ``then``/``else`` is an
    # expression too.
    if_expression_depths: list[int] = []
    bracket_depth = 0

    for index, token in enumerate(tokens):
        text = token.text
        kind = token.kind

        if kind == "symbol":
            if text in ("(", "[", "{"):
                bracket_depth += 1
            elif text in (")", "]", "}"):
                bracket_depth = max(0, bracket_depth - 1)
                while if_expression_depths and if_expression_depths[-1] > bracket_depth:
                    if_expression_depths.pop()
            elif text in _IF_EXPRESSION_ENDERS:
                while if_expression_depths and if_expression_depths[-1] >= bracket_depth:
                    if_expression_depths.pop()
            continue
        if kind != "identifier":
            continue
        if text in _IF_EXPRESSION_ENDERS or text == "end":
            while if_expression_depths and if_expression_depths[-1] >= bracket_depth:
                if_expression_depths.pop()

        if text == "function":
            stack.append(("function", None))
            func_depth += 1
            continue
        if text == "if":
            previous = tokens[index - 1].text if index else ""
            expression = (
                previous in _EXPRESSION_PRECEDERS
                or (previous in ("then", "else")
                    and if_expression_depths
                    and if_expression_depths[-1] == bracket_depth)
            )
            if expression:
                if_expression_depths.append(bracket_depth)
            else:
                stack.append(("if", None))
            continue
        if text == "do":
            # ``do`` closes the header of a ``for``/``while`` loop; any other
            # ``do`` introduces a plain block.
            if stack and stack[-1][0] == "loop-pending":
                loop = stack[-1][1]
                assert loop is not None
                stack[-1] = (loop.kind, loop)
                loop.body_start = index + 1
            else:
                stack.append(("do", None))
            continue
        if text in ("for", "while"):
            loop = _Loop(kind=text, keyword=index, func_depth=func_depth)
            loops.append(loop)
            open_loops.append(loop)
            stack.append(("loop-pending", loop))
            continue
        if text == "repeat":
            loop = _Loop(kind=text, keyword=index, body_start=index + 1, func_depth=func_depth)
            loops.append(loop)
            open_loops.append(loop)
            stack.append(("repeat", loop))
            continue
        if text == "until":
            if not stack or stack[-1][0] != "repeat":
                raise UnsupportedLuauSyntax("'until' without matching 'repeat'", source=source, offset=token.start)
            loop = stack.pop()[1]
            assert loop is not None
            loop.closer = index
            _close_loop(source, open_loops, loop, token)
            continue
        if text == "end":
            if not stack:
                raise UnsupportedLuauSyntax("unbalanced 'end'", source=source, offset=token.start)
            opener, loop = stack.pop()
            if opener == "loop-pending":
                keyword = tokens[loop.keyword].start if loop is not None else token.start
                raise UnsupportedLuauSyntax("'for'/'while' without 'do'", source=source, offset=keyword)
            if opener == "repeat":
                raise UnsupportedLuauSyntax("'repeat' closed by 'end'", source=source, offset=token.start)
            if opener == "function":
                func_depth -= 1
            if loop is not None:
                loop.closer = index
                _close_loop(source, open_loops, loop, token)
            continue
        if text in ("continue", "break"):
            if not open_loops:
                # Luau rejects this as well; report instead of guessing.
                raise UnsupportedLuauSyntax(f"'{text}' outside of a loop", source=source, offset=token.start)
            loop = open_loops[-1]
            if loop.func_depth != func_depth:
                # Inside a nested function: Luau also rejects this ("continue
                # must be inside a loop in the same function").
                raise UnsupportedLuauSyntax(
                    f"'{text}' inside a nested function", source=source, offset=token.start
                )
            if loop.body_start < 0:
                raise UnsupportedLuauSyntax(
                    f"'{text}' before the loop body", source=source, offset=token.start
                )
            (loop.continues if text == "continue" else loop.breaks).append(index)
            continue

    if stack:
        opener, loop = stack[-1]
        offset = tokens[loop.keyword].start if loop is not None else tokens[-1].start
        raise UnsupportedLuauSyntax(f"unterminated '{opener}' block", source=source, offset=offset)

    for counter, loop in enumerate(loops):
        if not loop.continues:
            continue
        continue_flag = f"__dv_cont_{counter}"
        break_flag = f"__dv_brk_{counter}"
        if loop.kind == "repeat":
            # ``continue`` in a ``repeat`` loop jumps to the until-test, which is
            # the end of the body.  Wrapping the body in a one-shot ``for`` gives
            # ``do break end`` exactly that jump: it leaves the wrapper and falls
            # through the rest of the body into ``until``.  ``break`` has to be
            # redirected through a flag because it would otherwise leave only the
            # wrapper.
            keyword = tokens[loop.keyword]
            closer = tokens[loop.closer]
            edits.append(_Edit(keyword.start, keyword.start, f"local {break_flag} = false; ", order=1))
            edits.append(_Edit(keyword.end, keyword.end, f" for {continue_flag} = 1, 1 do", order=1))
            edits.append(
                _Edit(closer.start, closer.start, f" end; if {break_flag} then break end; ", order=2)
            )
            for token_index in loop.continues:
                span = tokens[token_index]
                edits.append(_Edit(span.start, span.end, "do break end"))
            for token_index in loop.breaks:
                span = tokens[token_index]
                edits.append(_Edit(span.start, span.end, f"{break_flag} = true do break end"))
        else:
            # ``continue`` in a ``for``/``while`` loop starts the next iteration,
            # tests included: wrapping the body in ``repeat ... until true`` and
            # lowering ``continue`` to ``do break end`` lands right after the
            # wrapper, which is the end of the iteration.
            keyword = tokens[loop.keyword]
            body = tokens[loop.body_start - 1]  # the ``do`` token
            closer = tokens[loop.closer]
            edits.append(_Edit(keyword.start, keyword.start, f"local {break_flag} = false; ", order=1))
            edits.append(_Edit(body.end, body.end, " repeat", order=1))
            edits.append(
                _Edit(
                    closer.start,
                    closer.start,
                    f" until true; if {break_flag} then break end; ",
                    order=2,
                )
            )
            for token_index in loop.continues:
                span = tokens[token_index]
                edits.append(_Edit(span.start, span.end, "do break end"))
            for token_index in loop.breaks:
                span = tokens[token_index]
                edits.append(_Edit(span.start, span.end, f"{break_flag} = true do break end"))


def _close_loop(source: str, open_loops: list[_Loop], loop: _Loop, token: Token) -> None:
    if not open_loops or open_loops[-1] is not loop:
        raise UnsupportedLuauSyntax("mismatched loop nesting", source=source, offset=token.start)
    open_loops.pop()


# ---------------------------------------------------------------------------
# pass: type annotations
# ---------------------------------------------------------------------------


def _skip_type(source: str, tokens: list[Token], index: int, stop: frozenset[str]) -> int:
    """Return the token index just past a Luau type expression.

    ``stop`` lists the tokens that terminate the type at nesting depth zero.
    The scanner rejects anything it cannot classify, so a malformed guess can
    never truncate real code.
    """
    depth = 0
    start = index
    while index < len(tokens):
        token = tokens[index]
        text = token.text
        if depth == 0 and text in stop:
            break
        if text in ("{", "(", "[", "<"):
            depth += 1
            index += 1
            continue
        if text in ("}", ")", "]", ">"):
            if depth == 0:
                break
            depth -= 1
            index += 1
            continue
        if text in _TYPE_EXPR_TOKENS:
            if text == "..." and depth == 0 and index > start:
                # ``...`` only appears as a type tail inside an argument list.
                pass
            index += 1
            continue
        if token.kind == "identifier" or text in _TYPE_ATOMS:
            index += 1
            continue
        if token.kind == "string":
            index += 1
            continue
        if token.kind == "number":
            index += 1
            continue
        if depth == 0:
            break
        index += 1
    if index == start:
        offset = tokens[start].start if start < len(tokens) else len(source)
        raise UnsupportedLuauSyntax("expected a type expression", source=source, offset=offset)
    return index


def _strip_types(source: str, tokens: list[Token], edits: list[_Edit], notes: list[str] | None = None) -> None:
    index = 0
    total = len(tokens)
    # ``signature_depth`` is the parenthesis depth of the current function
    # signature parameter list, or ``None`` outside of a signature.
    signature_paren: int | None = None
    paren_depth = 0
    pending_signature = False
    while index < total:
        token = tokens[index]
        text = token.text
        if text == "function":
            pending_signature = True
            index += 1
            continue
        if pending_signature and text == "(":
            paren_depth += 1
            signature_paren = paren_depth
            pending_signature = False
            index += 1
            continue
        if text == "(":
            paren_depth += 1
            index += 1
            continue
        if text == ")":
            if signature_paren == paren_depth:
                signature_paren = None
                index += 1
                if index < total and tokens[index].text == ":":
                    end = _skip_type(source, tokens, index + 1, _STATEMENT_KEYWORDS)
                    edits.append(_Edit(tokens[index].start, tokens[end - 1].end, " "))
                    index = end
                continue
            paren_depth = max(0, paren_depth - 1)
            index += 1
            continue
        if signature_paren is not None and paren_depth == signature_paren and text == ":":
            # ``function f(a: T, ...: U)`` - the annotation runs to ``,`` or ``)``.
            end = _skip_type(source, tokens, index + 1, frozenset({",", ")"}))
            edits.append(_Edit(token.start, tokens[end - 1].end, ""))
            index = end
            continue
        if text == "local":
            index = _strip_local_declaration(source, tokens, index, edits)
            continue
        if text == "::":
            end = _skip_type(source, tokens, index + 1, _STATEMENT_KEYWORDS | frozenset({",", ")", "]", "}", ";", "="}))
            edits.append(_Edit(token.start, tokens[end - 1].end, ""))
            index = end
            continue
        if text in ("type", "export") and token.kind == "identifier":
            next_index = index + 1
            if text == "export" and next_index < total and tokens[next_index].text == "type":
                next_index += 1
            if (
                next_index < total
                and tokens[next_index].kind == "identifier"
                and tokens[next_index].text not in _STATEMENT_KEYWORDS
                and _looks_like_type_declaration(tokens, next_index + 1)
            ):
                end = _skip_type(source, tokens, next_index + 1, _STATEMENT_KEYWORDS)
                edits.append(_Edit(token.start, tokens[end - 1].end, " "))
                index = end
                continue
        index += 1


def _looks_like_type_declaration(tokens: list[Token], index: int) -> bool:
    """``type X = ...`` / ``type X<T> = ...`` look-ahead."""
    depth = 0
    while index < len(tokens):
        text = tokens[index].text
        if text == "<":
            depth += 1
        elif text == ">":
            depth = max(0, depth - 1)
        elif text == "=" and depth == 0:
            return True
        elif text in _STATEMENT_KEYWORDS and depth == 0:
            return False
        index += 1
    return False


def _strip_local_declaration(source: str, tokens: list[Token], index: int, edits: list[_Edit]) -> int:
    """Handle ``local x: T`` (and friend) starting at the ``local`` token."""
    index += 1
    if index < len(tokens) and tokens[index].text == "function":
        # ``local function f(): T`` - the signature pass handles the rest.
        return index
    while index < len(tokens):
        token = tokens[index]
        if token.kind != "identifier":
            return index
        if token.text in _STATEMENT_KEYWORDS:
            return index
        index += 1
        # optional attribute: ``local x <const>``
        if index < len(tokens) and tokens[index].text == "<":
            depth = 1
            index += 1
            while index < len(tokens) and depth:
                depth += {"<": 1, ">": -1}.get(tokens[index].text, 0)
                index += 1
        if index < len(tokens) and tokens[index].text == ":":
            end = _skip_type(source, tokens, index + 1, frozenset({",", "=", ";"}) | _STATEMENT_KEYWORDS)
            edits.append(_Edit(tokens[index].start, tokens[end - 1].end, ""))
            index = end
        if index < len(tokens) and tokens[index].text == ",":
            index += 1
            continue
        return index
    return index


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------


def luau_only_features(source: str) -> tuple[str, ...]:
    """Cheaply list the Luau-only constructs present in ``source``."""
    if len(source) > MAX_SOURCE_BYTES:
        raise ValueError("source is too large to normalise")
    found: list[str] = []
    tokens = tokenize(source)
    for token in tokens:
        if token.kind == "identifier":
            if token.text == "continue":
                found.append("continue")
            elif token.text == "type":
                found.append("type")
        elif token.kind == "number" and "_" in token.text:
            found.append("numeric_separators")
        elif token.text == "::":
            found.append("casts")
    return tuple(dict.fromkeys(found))


def normalize_luau(source: str) -> Normalization:
    """Lower Luau-only syntax in ``source`` to plain Lua.

    Raises :class:`UnsupportedLuauSyntax` when a construct cannot be converted
    without changing semantics.
    """
    if len(source) > MAX_SOURCE_BYTES:
        raise ValueError("source is too large to normalise")
    if "\x00" in source:
        source = source.replace("\x00", " ")
    text = source
    notes: list[str] = []
    applied: list[str] = []
    # Each pass works on the output of the previous one: edits from different
    # passes would otherwise overlap (a numeral inside a compound assignment
    # span, for instance).
    passes: tuple[tuple[str, "Callable[[str, list[Token], list[_Edit], list[str]], None]"], ...] = (
        ("string_interpolation", _lower_interpolated_strings),
        ("numerals", _normalise_numerals),
        ("string_escapes", _normalise_string_escapes),
        ("not_equal_alias", _normalise_not_equal),
        ("compound_assignment", _lower_compound_assignments),
        ("continue", _rewrite_continue),
        ("type_annotations", _strip_types),
    )
    for name, function in passes:
        tokens = tokenize(text)
        edits: list[_Edit] = []
        if name == "not_equal_alias":
            function(text, tokens, edits)  # type: ignore[call-arg]
        else:
            function(text, tokens, edits, notes)
        if edits:
            text = _apply_edits(text, edits)
            applied.append(name)
    # If-expressions come before floor division: their branches may contain
    # ``//``, and lowering them first means the division pass sees plain text.
    text, if_expression_count = _lower_if_expressions(text, notes)
    if if_expression_count:
        applied.append("if_expression")
    # Floor division runs last: the compound-assignment pass turns ``x //= 2``
    # into ``x = x // 2``, and only then is it a plain ``//`` to rewrite.
    lowered, floor_count = _lower_floor_division(text, notes)
    if floor_count:
        text = lowered
        applied.append("floor_division")
    return Normalization(source=text, applied=tuple(applied), notes=tuple(notes))
