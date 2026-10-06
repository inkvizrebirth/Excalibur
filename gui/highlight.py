"""Lua/Luau token scanner used by the result viewer.

The scanner is deliberately small and dependency-free: it produces per-line
``(start, end, tag)`` spans that a Tk text widget turns into tags.  Keeping it
pure Python means the highlighting rules can be unit-tested without a display.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable

TAG_KEYWORD = "keyword"
TAG_CONSTANT = "constant"
TAG_BUILTIN = "builtin"
TAG_STANDARD = "standard"
TAG_EXECUTOR = "executor"
TAG_STRING = "string"
TAG_NUMBER = "number"
TAG_COMMENT = "comment"
TAG_OPERATOR = "operator"
TAG_FUNCTION = "function"
TAG_PROPERTY = "property"
TAG_LABEL = "label"

TAG_ORDER: tuple[str, ...] = (
    TAG_KEYWORD,
    TAG_CONSTANT,
    TAG_BUILTIN,
    TAG_STANDARD,
    TAG_EXECUTOR,
    TAG_STRING,
    TAG_NUMBER,
    TAG_COMMENT,
    TAG_OPERATOR,
    TAG_FUNCTION,
    TAG_PROPERTY,
    TAG_LABEL,
)

KEYWORDS = frozenset(
    {
        "and",
        "break",
        "continue",
        "do",
        "else",
        "elseif",
        "end",
        "export",
        "for",
        "function",
        "goto",
        "if",
        "in",
        "local",
        "not",
        "or",
        "repeat",
        "return",
        "then",
        "type",
        "until",
        "while",
    }
)

CONSTANTS = frozenset({"true", "false", "nil"})

BUILTINS = frozenset(
    {
        "assert",
        "collectgarbage",
        "dofile",
        "error",
        "getfenv",
        "getmetatable",
        "ipairs",
        "load",
        "loadfile",
        "loadstring",
        "module",
        "next",
        "pairs",
        "pcall",
        "print",
        "rawequal",
        "rawget",
        "rawlen",
        "rawset",
        "require",
        "select",
        "setfenv",
        "setmetatable",
        "tonumber",
        "tostring",
        "type",
        "typeof",
        "unpack",
        "xpcall",
        "_G",
        "_VERSION",
        "game",
        "workspace",
        "script",
        "shared",
        "settings",
        "Instance",
        "Enum",
        "task",
        "wait",
        "spawn",
        "delay",
        "tick",
        "time",
        "warn",
        "newproxy",
        "coroutine",
        "bit32",
        "utf8",
        "buffer",
        "vector",
    }
)

STANDARD_LIBRARIES = frozenset({"math", "string", "table", "os", "io", "debug", "package"})

# Executor globals worth colouring distinctly; kept in sync with the injector
# profiles so a recovered script shows which executor surface it touches.
EXECUTOR_GLOBALS = frozenset(
    {
        "identifyexecutor",
        "getexecutorname",
        "getexecutor",
        "getgenv",
        "getrenv",
        "getgc",
        "getreg",
        "getinstances",
        "getnilinstances",
        "getloadedmodules",
        "getscripts",
        "getcallingscript",
        "getscriptbytecode",
        "getscripthash",
        "decompile",
        "checkcaller",
        "cloneref",
        "compareinstances",
        "islclosure",
        "iscclosure",
        "isfunction",
        "newcclosure",
        "hookfunction",
        "hookmetamethod",
        "replaceclosure",
        "getrawmetatable",
        "setreadonly",
        "isreadonly",
        "getupvalue",
        "getupvalues",
        "setupvalue",
        "getconstants",
        "getprotos",
        "getconnections",
        "getnamecallmethod",
        "setnamecallmethod",
        "getthreadidentity",
        "getidentity",
        "setthreadidentity",
        "queue_on_teleport",
        "setclipboard",
        "writefile",
        "readfile",
        "appendfile",
        "listfiles",
        "isfile",
        "isfolder",
        "delfile",
        "makefolder",
        "delfolder",
        "getcustomasset",
        "cache_replace",
        "fireclickdetector",
        "firetouchinterest",
        "fireproximityprompt",
        "sethiddenproperty",
        "gethiddenproperty",
        "request",
        "http_request",
        "base64_encode",
        "base64_decode",
        "base64encode",
        "base64decode",
        "syn",
        "krnl",
        "fluxus",
        "solara",
        "xeno",
        "hydrogen",
        "protect_gui",
        "unprotect_gui",
        "KRNL_LOADED",
        "FLUXUS_LOADED",
        "getsenv",
        "getmenv",
        "getcustomasset",
        "getcallingscript",
    }
)

_OPERATORS = frozenset("+-*/%^#=<>~;:,.(){}[]&|!")


@dataclass(frozen=True)
class Span:
    start: int
    end: int
    tag: str


@dataclass
class ScanState:
    """Carry-over state between lines (long comments and long strings)."""

    long_comment_level: int | None = None
    long_string_level: int | None = None

    def busy(self) -> bool:
        return self.long_comment_level is not None or self.long_string_level is not None


def _long_bracket(text: str, index: int) -> tuple[int, int] | None:
    """Detect ``[=*[`` at ``index``; returns (level, opener_length)."""
    if index >= len(text) or text[index] != "[":
        return None
    cursor = index + 1
    level = 0
    while cursor < len(text) and text[cursor] == "=":
        level += 1
        cursor += 1
    if cursor < len(text) and text[cursor] == "[":
        return level, cursor - index + 1
    return None


def _long_close(text: str, index: int, level: int) -> int | None:
    """Index just past a ``]=*]`` close at ``index``, or None."""
    if index >= len(text) or text[index] != "]":
        return None
    cursor = index + 1
    seen = 0
    while cursor < len(text) and text[cursor] == "=":
        seen += 1
        cursor += 1
    if seen == level and cursor < len(text) and text[cursor] == "]":
        return cursor + 1
    return None


def _scan_line(line: str, state: ScanState) -> tuple[list[Span], ScanState]:
    spans: list[Span] = []
    length = len(line)
    index = 0

    if state.long_comment_level is not None:
        level = state.long_comment_level
        while index < length:
            closed = _long_close(line, index, level)
            if closed is not None:
                spans.append(Span(0, closed, TAG_COMMENT))
                state.long_comment_level = None
                index = closed
                break
            index += 1
        else:
            spans.append(Span(0, length, TAG_COMMENT))
            return spans, state
    elif state.long_string_level is not None:
        level = state.long_string_level
        closed_index = 0
        while index < length:
            closed = _long_close(line, index, level)
            if closed is not None:
                spans.append(Span(0, closed, TAG_STRING))
                state.long_string_level = None
                index = closed
                break
            index += 1
        else:
            spans.append(Span(0, length, TAG_STRING))
            return spans, state

    previous_significant = ""

    while index < length:
        char = line[index]

        if char == "-" and line.startswith("--", index):
            opener = _long_bracket(line, index + 2)
            if opener is not None:
                level, opener_length = opener
                opening_end = index + 2 + opener_length
                cursor = opening_end
                while cursor < length:
                    closed = _long_close(line, cursor, level)
                    if closed is not None:
                        spans.append(Span(index, closed, TAG_COMMENT))
                        cursor = closed
                        break
                    cursor += 1
                else:
                    spans.append(Span(index, length, TAG_COMMENT))
                    state.long_comment_level = level
                    return spans, state
                index = cursor
                previous_significant = ""
                continue
            spans.append(Span(index, length, TAG_COMMENT))
            return spans, state

        if char in "\"'":
            quote = char
            cursor = index + 1
            while cursor < length:
                current = line[cursor]
                if current == "\\":
                    cursor += 2
                    continue
                if current == quote:
                    cursor += 1
                    break
                cursor += 1
            else:
                cursor = length
            spans.append(Span(index, min(cursor, length), TAG_STRING))
            index = min(cursor, length)
            previous_significant = "string"
            continue

        if char == "[":
            opener = _long_bracket(line, index)
            if opener is not None:
                level, opener_length = opener
                cursor = index + opener_length
                while cursor < length:
                    closed = _long_close(line, cursor, level)
                    if closed is not None:
                        spans.append(Span(index, closed, TAG_STRING))
                        cursor = closed
                        break
                    cursor += 1
                else:
                    spans.append(Span(index, length, TAG_STRING))
                    state.long_string_level = level
                    return spans, state
                index = cursor
                previous_significant = "string"
                continue

        if char.isdigit() or (char == "." and index + 1 < length and line[index + 1].isdigit()):
            cursor = index
            if line.startswith(("0x", "0X"), cursor):
                cursor += 2
                while cursor < length and (line[cursor].isalnum() or line[cursor] in "._"):
                    cursor += 1
            else:
                while cursor < length and (line[cursor].isdigit() or line[cursor] in "._"):
                    cursor += 1
                if cursor < length and line[cursor] in "eE":
                    cursor += 1
                    if cursor < length and line[cursor] in "+-":
                        cursor += 1
                    while cursor < length and line[cursor].isdigit():
                        cursor += 1
            spans.append(Span(index, cursor, TAG_NUMBER))
            index = cursor
            previous_significant = "number"
            continue

        if char.isalpha() or char == "_":
            cursor = index
            while cursor < length and (line[cursor].isalnum() or line[cursor] == "_"):
                cursor += 1
            word = line[index:cursor]
            lookahead = cursor
            while lookahead < length and line[lookahead] in " \t":
                lookahead += 1
            tag = TAG_LABEL
            if word in KEYWORDS:
                tag = TAG_KEYWORD
            elif word in CONSTANTS:
                tag = TAG_CONSTANT
            elif word in EXECUTOR_GLOBALS:
                tag = TAG_EXECUTOR
            elif word in BUILTINS:
                tag = TAG_BUILTIN
            elif word in STANDARD_LIBRARIES:
                tag = TAG_STANDARD
            elif previous_significant in {".", ":"}:
                tag = TAG_PROPERTY
            elif lookahead < length and line[lookahead] == "(":
                tag = TAG_FUNCTION
            elif lookahead < length and line[lookahead] == "=" and not line.startswith("==", lookahead):
                tag = TAG_LABEL
            spans.append(Span(index, cursor, tag))
            index = cursor
            previous_significant = word
            continue

        if char in _OPERATORS:
            spans.append(Span(index, index + 1, TAG_OPERATOR))
            previous_significant = char

        index += 1

    return spans, state


def highlight_lines(text: str) -> list[list[Span]]:
    """Return one span list per line of ``text``."""
    state = ScanState()
    result: list[list[Span]] = []
    for line in text.split("\n"):
        spans, state = _scan_line(line, state)
        result.append(spans)
    return result


def tags_used(spans: Iterable[Iterable[Span]]) -> set[str]:
    return {span.tag for line in spans for span in line}


def summarize(text: str, *, limit: int = 400) -> dict[str, int]:
    """Count tokens per tag; used by tests and the status strip."""
    counts: dict[str, int] = {}
    for line in highlight_lines(text)[:limit]:
        for span in line:
            counts[span.tag] = counts.get(span.tag, 0) + 1
    return counts
