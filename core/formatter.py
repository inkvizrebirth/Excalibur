from __future__ import annotations

from core.deobfuscator import Token, _is_statement_if, tokenize

MAX_FORMAT_SOURCE_CHARS = 1 * 1024 * 1024

_OPERATOR_TOKENS = {
    "=", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=", "..=",
    "+", "-", "*", "/", "//", "%", "^", "==", "~=", "<", ">", "<=", ">=",
    "|", "&", "<<", ">>", "..", "->", "and", "or", "in",
}
_UNARY_TOKENS = {"+", "-", "~", "#", "not"}
_STATEMENT_STARTS = {"local", "return", "break", "continue", "type", "export", "for", "while", "repeat"}
def _previous_code_index(tokens: list[Token], index: int) -> int:
    index -= 1
    while index >= 0 and tokens[index].kind == "comment":
        index -= 1
    return index


def _next_code_index(tokens: list[Token], index: int) -> int:
    index += 1
    while index < len(tokens) and tokens[index].kind == "comment":
        index += 1
    return index


def _is_unary(tokens: list[Token], index: int) -> bool:
    token = tokens[index]
    if token.text not in _UNARY_TOKENS:
        return False
    if token.text == "not":
        return True
    previous = _previous_code_index(tokens, index)
    if previous < 0:
        return True
    before = tokens[previous]
    return (
        before.kind == "symbol" and before.text in _OPERATOR_TOKENS | {"(", "[", "{", ",", ";", "::"}
    ) or (
        before.kind == "identifier"
        and before.text in {"return", "then", "do", "else", "elseif", "until", "in", "and", "or", "not"}
    )


def _needs_space(previous: Token | None, current: Token, current_index: int, tokens: list[Token]) -> bool:
    if previous is None:
        return False
    prev_text = previous.text
    text = current.text
    if text in {",", ";", ")", "]", "}", ".", ":", "::"}:
        return False
    if prev_text in {"(", "[", ".", ":", "::"}:
        return False
    if text in _OPERATOR_TOKENS or prev_text in _OPERATOR_TOKENS:
        if text in _UNARY_TOKENS and _is_unary(tokens, current_index):
            return prev_text not in {"(", "[", ".", ":", "::"}
        if prev_text in _UNARY_TOKENS and _is_unary(tokens, current_index - 1):
            return text == "not"
        return True
    if text == "(":
        return prev_text in {"if", "for", "while"}
    if prev_text in {",", ";"}:
        return True
    if prev_text in {
        "local", "return", "if", "for", "while", "function", "then", "else", "elseif",
        "do", "repeat", "until", "type", "export", "in", "and", "or", "not",
    }:
        return True
    if previous.kind in {"identifier", "number", "string"} and current.kind in {
        "identifier", "number", "string",
    }:
        return True
    if prev_text in {")", "]", "}"} and current.kind in {"identifier", "number", "string"}:
        return True
    if text == "{" and previous.kind in {"identifier", "number", "string"}:
        return True
    return False


_LINE_BREAK_JOINERS = _OPERATOR_TOKENS | {
    "(", "[", "{", "=", ",", ";", "then", "do", "else", "and", "or", "not", "#",
    "return", "in", "::",
}
_LINE_BREAK_CLOSERS = {")", "]", "}", ",", ";", ".", ":", "::", "(", "[", "{",
                        "then", "do", "end", "else", "elseif", "until"}


def _line_break_between(source: str, previous: Token | None, current: Token) -> bool:
    """True when the input had a line break between two code tokens."""
    if previous is None or current.start <= previous.end:
        return False
    return "\n" in source[previous.end:current.start]


def _joins_across_lines(previous: Token | None, current: Token) -> bool:
    """True when the pair is a continuation that reads better on one line."""
    if previous is None:
        return True
    return previous.text in _LINE_BREAK_JOINERS or current.text in _LINE_BREAK_CLOSERS


def _function_parameter_closers(tokens: list[Token]) -> dict[int, int]:
    closers: dict[int, int] = {}
    for index, token in enumerate(tokens):
        if token.kind != "identifier" or token.text != "function":
            continue
        cursor = index + 1
        while cursor < len(tokens) and tokens[cursor].text != "(":
            if tokens[cursor].text in {"then", "do", "end", ";"}:
                break
            cursor += 1
        if cursor >= len(tokens) or tokens[cursor].text != "(":
            continue
        depth = 1
        cursor += 1
        while cursor < len(tokens) and depth:
            if tokens[cursor].text == "(":
                depth += 1
            elif tokens[cursor].text == ")":
                depth -= 1
                if depth == 0:
                    closers[cursor] = index
                    break
            cursor += 1
    return closers


def _has_typed_function_return(tokens: list[Token], closers: dict[int, int]) -> bool:
    return any(
        _next_code_index(tokens, close_index) < len(tokens)
        and tokens[_next_code_index(tokens, close_index)].text == ":"
        for close_index in closers
    )


def format_luau(source: str) -> str:
    """Apply a conservative, token-preserving formatter for ordinary Luau source.

    It changes only trivia (whitespace/comments). Interpolated strings, Luau
    if-expressions, and typed function return annotations are left untouched;
    the caller can then validate formatted candidates with the real Luau CLI.
    """
    if not source or len(source) > MAX_FORMAT_SOURCE_CHARS or "`" in source:
        return source
    tokens = tokenize(source)
    if not tokens:
        return source
    if any(
        token.kind == "identifier" and token.text == "if" and not _is_statement_if(source, tokens, index)
        for index, token in enumerate(tokens)
    ):
        return source

    function_closers = _function_parameter_closers(tokens)
    if _has_typed_function_return(tokens, function_closers):
        return source

    output: list[str] = []
    indent = 0
    line_open = False
    previous: Token | None = None
    blocks: list[dict[str, object]] = []

    def ensure_line() -> None:
        nonlocal line_open
        if not line_open:
            output.append("    " * max(0, indent))
            line_open = True

    def newline() -> None:
        nonlocal line_open
        while output and not output[-1].strip(" \t"):
            output.pop()
        if output and not output[-1].endswith("\n"):
            output.append("\n")
        line_open = False

    def emit(text: str, *, needs_space: bool = False) -> None:
        was_line_open = line_open
        ensure_line()
        if (
            needs_space
            and was_line_open
            and output
            and not output[-1].endswith((" ", "\t", "\n"))
        ):
            output.append(" ")
        output.append(text)

    bracket_depth = 0
    for index, token in enumerate(tokens):
        if token.kind == "comment":
            if line_open:
                if output and not output[-1].endswith((" ", "\n")):
                    output.append(" ")
            else:
                ensure_line()
            output.append(token.text)
            newline()
            previous = None
            continue

        text = token.text
        if text in {"(", "[", "{"}:
            bracket_depth += 1
        elif text in {")", "]", "}"}:
            bracket_depth = max(0, bracket_depth - 1)
        next_index = _next_code_index(tokens, index)
        next_text = tokens[next_index].text if next_index < len(tokens) else ""

        if text in {"end", "else", "elseif", "until"}:
            if blocks:
                frame = blocks[-1]
                if text in {"else", "elseif"} and frame["kind"] == "if":
                    if frame.get("body"):
                        indent = max(0, indent - 1)
                    frame["body"] = False
                    frame["awaiting_then"] = text == "elseif"
                elif text == "until" and frame["kind"] == "repeat":
                    if frame.get("body"):
                        indent = max(0, indent - 1)
                    blocks.pop()
                elif text == "end":
                    blocks.pop()
                    if frame.get("body"):
                        indent = max(0, indent - 1)
            newline()
            emit(text)
            if text == "else":
                newline()
                indent += 1
                if blocks and blocks[-1]["kind"] == "if":
                    blocks[-1]["body"] = True
            elif text == "elseif":
                if blocks and blocks[-1]["kind"] == "if":
                    blocks[-1]["awaiting_then"] = True
            elif text == "until":
                previous = token
                continue
            elif text == "end":
                if next_text not in {")", "]", ",", ";", ".", ":", "("}:
                    newline()
            previous = token
            continue

        if text in _STATEMENT_STARTS:
            if text != "type" or previous is None or previous.text != "export":
                if line_open:
                    newline()

        if text == "if" and token.kind == "identifier":
            if line_open:
                newline()
            emit(text)
            blocks.append({"kind": "if", "body": False, "awaiting_then": True})
            previous = token
            continue

        if text in {"for", "while"}:
            if line_open:
                newline()
            emit(text)
            blocks.append({"kind": "loop", "body": False, "pending_do": True})
            previous = token
            continue

        if text == "function" and token.kind == "identifier":
            expression_prefixes = {
                "=", ",", "(", "{", "return", "and", "or", "not", "then", "else",
            }
            previous_index = _previous_code_index(tokens, index)
            expression_context = previous_index >= 0 and (
                tokens[previous_index].text in expression_prefixes
                or tokens[previous_index].text in _OPERATOR_TOKENS
            )
            if line_open and not expression_context and previous is not None and previous.text != "local":
                newline()
            emit(text, needs_space=_needs_space(previous, token, index, tokens))
            blocks.append({"kind": "function", "body": False, "awaiting_params": True})
            previous = token
            continue

        if text == "repeat":
            if line_open:
                newline()
            emit(text)
            blocks.append({"kind": "repeat", "body": True})
            newline()
            indent += 1
            previous = token
            continue

        if text == "then" and blocks and blocks[-1]["kind"] == "if" and blocks[-1].get("awaiting_then"):
            emit(text, needs_space=True)
            blocks[-1]["awaiting_then"] = False
            blocks[-1]["body"] = True
            newline()
            indent += 1
            previous = token
            continue

        if text == "do":
            emit(text, needs_space=True)
            if blocks and blocks[-1]["kind"] == "loop" and blocks[-1].get("pending_do"):
                blocks[-1]["pending_do"] = False
                blocks[-1]["body"] = True
            else:
                blocks.append({"kind": "do", "body": True})
            newline()
            indent += 1
            previous = token
            continue

        if index in function_closers:
            emit(text, needs_space=_needs_space(previous, token, index, tokens))
            newline()
            indent += 1
            if blocks and blocks[-1]["kind"] == "function" and blocks[-1].get("awaiting_params"):
                blocks[-1]["body"] = True
                blocks[-1]["awaiting_params"] = False
            previous = token
            continue

        if text == ";":
            emit(text)
            newline()
            previous = token
            continue

        if (
            line_open
            and bracket_depth == 0
            and _line_break_between(source, previous, token)
            and not _joins_across_lines(previous, token)
        ):
            # Newlines are trivia in Lua, so keeping the author's line breaks
            # never changes behaviour — it only stops two statements from
            # being glued into one unreadable line.
            newline()

        unary = _is_unary(tokens, index)
        needs_space = _needs_space(previous, token, index, tokens)
        if text in {"+", "-", "~", "#"} and unary:
            previous_index = _previous_code_index(tokens, index)
            needs_space = previous_index >= 0 and tokens[previous_index].text not in {"(", "[", ".", ":", "::"}
        emit(text, needs_space=needs_space)
        if text == ",":
            output.append(" ")
        previous = token

    newline()
    result = "".join(output).rstrip()
    if source.endswith(("\n", "\r")) and result:
        result += "\n"
    return result


__all__ = ["MAX_FORMAT_SOURCE_CHARS", "format_luau"]
