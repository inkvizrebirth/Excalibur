from __future__ import annotations

import base64
import binascii
import json
import math
import re
from dataclasses import dataclass
from typing import Any

MAX_SOURCE_BYTES = 16 * 1024 * 1024
MAX_FOLDED_STRING_BYTES = 32 * 1024
MAX_EXPRESSION_TOKENS = 512
MAX_TRANSFORM_PASSES = 6

_IDENTIFIER = re.compile(r"[A-Za-z_][A-Za-z0-9_]*")
_NUMBER = re.compile(
    r"(?:0[xX][0-9a-fA-F]+(?:\.(?!\.)[0-9a-fA-F]*)?(?:[pP][+-]?\d+)?|"
    r"0[bB][01]+|(?:\d+(?:\.(?!\.)\d*)?|\.\d+)(?:[eE][+-]?\d+)?)"
)
_LONG_BRACKET = re.compile(r"\[(=*)\[")
_OPERATORS = (
    "...", "..=", "//", "<<", ">>", "==", "~=", "<=", ">=", "..", "::", "->",
    "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=",
)
_PRECEDENCE = {
    "or": 1,
    "and": 2,
    "==": 3,
    "~=": 3,
    "<": 3,
    "<=": 3,
    ">": 3,
    ">=": 3,
    "|": 4,
    "~": 5,
    "&": 6,
    "<<": 7,
    ">>": 7,
    "..": 8,
    "+": 9,
    "-": 9,
    "*": 10,
    "/": 10,
    "//": 10,
    "%": 10,
    "^": 12,
}
_RIGHT_ASSOCIATIVE = {"..", "^"}
_UNKNOWN = object()


@dataclass(frozen=True)
class Token:
    kind: str
    text: str
    start: int
    end: int


@dataclass(frozen=True)
class DeobfuscationResult:
    source: str
    passes: int
    folded_expressions: int
    decoded_strings: int
    transformations: tuple[str, ...]
    input_bytes: int
    output_bytes: int

    @property
    def changed(self) -> bool:
        return bool(self.transformations)


@dataclass(frozen=True)
class _Namespace:
    name: str


@dataclass(frozen=True)
class _Path:
    name: str


@dataclass(frozen=True)
class _Function:
    name: str


@dataclass(frozen=True)
class _Receiver:
    name: str


@dataclass(frozen=True)
class _Game:
    pass


@dataclass(frozen=True)
class _Table:
    values: tuple[Any, ...]
    fields: tuple[tuple[Any, Any], ...] = ()


@dataclass(frozen=True)
class _MultiReturn:
    values: tuple[Any, ...]


def _long_bracket_end(source: str, start: int) -> tuple[int, int] | None:
    match = _LONG_BRACKET.match(source, start)
    if not match:
        return None
    closing = "]" + match.group(1) + "]"
    content_start = match.end()
    content_end = source.find(closing, content_start)
    if content_end < 0:
        return len(source), content_start
    return content_end + len(closing), content_start


def tokenize(source: str) -> list[Token]:
    """Lex enough Lua/Luau syntax to safely find constant literal expressions."""
    tokens: list[Token] = []
    index = 0
    length = len(source)
    while index < length:
        character = source[index]
        if character.isspace():
            index += 1
            continue

        start = index
        if source.startswith("--", index):
            long_comment = _long_bracket_end(source, index + 2)
            if long_comment:
                index = long_comment[0]
            else:
                newline = source.find("\n", index + 2)
                index = length if newline < 0 else newline
            tokens.append(Token("comment", source[start:index], start, index))
            continue

        if character in "\"'":
            quote = character
            index += 1
            while index < length:
                current = source[index]
                if current == "\\":
                    index += 2
                    continue
                index += 1
                if current == quote:
                    break
            tokens.append(Token("string", source[start:index], start, index))
            continue

        long_string = _long_bracket_end(source, index)
        if long_string:
            index = long_string[0]
            tokens.append(Token("string", source[start:index], start, index))
            continue

        identifier = _IDENTIFIER.match(source, index)
        if identifier:
            index = identifier.end()
            tokens.append(Token("identifier", identifier.group(0), start, index))
            continue

        number = _NUMBER.match(source, index)
        if number:
            index = number.end()
            tokens.append(Token("number", number.group(0), start, index))
            continue

        operator = next((item for item in _OPERATORS if source.startswith(item, index)), None)
        if operator:
            index += len(operator)
        else:
            index += 1
        tokens.append(Token("symbol", source[start:index], start, index))
    return tokens


def count_remote_payload_loaders(source: str) -> int:
    """Count dynamic code loaders whose argument contains a recognizable HTTP fetch."""
    tokens = tokenize(source)
    remote_fetch_names = {
        "httpget",
        "httppost",
        "getasync",
        "postasync",
        "request",
        "http_request",
        "httprequest",
        "httprequestasync",
    }
    loader_names = {"load", "loadstring"}
    for index in range(len(tokens) - 3):
        if (
            tokens[index].kind == "identifier"
            and tokens[index].text == "local"
            and tokens[index + 1].kind == "identifier"
            and tokens[index + 2].text == "="
            and tokens[index + 3].kind == "identifier"
            and tokens[index + 3].text.lower() in loader_names
        ):
            loader_names.add(tokens[index + 1].text.lower())

    count = 0
    for index, token in enumerate(tokens[:-1]):
        if (
            token.kind != "identifier"
            or token.text.lower() not in loader_names
            or tokens[index + 1].text != "("
        ):
            continue

        depth = 0
        contains_fetch = False
        for argument_token in tokens[index + 1 :]:
            if argument_token.text == "(":
                depth += 1
            elif argument_token.text == ")":
                depth -= 1
                if depth == 0:
                    break
            elif (
                depth > 0
                and argument_token.kind == "identifier"
                and argument_token.text.lower() in remote_fetch_names
            ):
                contains_fetch = True
        if contains_fetch:
            count += 1
    return count


def _decode_string(token: Token) -> bytes | None:
    text = token.text
    if not text:
        return None
    if text[0] not in "\"'":
        opening = _LONG_BRACKET.match(text)
        if not opening:
            return None
        closing = "]" + opening.group(1) + "]"
        if not text.endswith(closing):
            return None
        content = text[opening.end() : -len(closing)]
        if content.startswith("\r\n"):
            content = content[2:]
        elif content.startswith(("\n", "\r")):
            content = content[1:]
        return content.encode("utf-8")

    quote = text[0]
    if len(text) < 2 or text[-1] != quote:
        return None
    output = bytearray()
    index = 1
    end = len(text) - 1
    simple_escapes = {
        "a": 7,
        "b": 8,
        "f": 12,
        "n": 10,
        "r": 13,
        "t": 9,
        "v": 11,
        "\\": 92,
        "\"": 34,
        "'": 39,
    }
    while index < end:
        character = text[index]
        if character != "\\":
            output.extend(character.encode("utf-8"))
            index += 1
            continue
        index += 1
        if index >= end:
            return None
        escaped = text[index]
        index += 1
        if escaped in simple_escapes:
            output.append(simple_escapes[escaped])
        elif escaped == "z":
            while index < end and text[index].isspace():
                index += 1
        elif escaped == "x":
            digits = text[index : index + 2]
            if len(digits) != 2 or not all(char in "0123456789abcdefABCDEF" for char in digits):
                return None
            output.append(int(digits, 16))
            index += 2
        elif escaped == "u" and index < end and text[index] == "{":
            close = text.find("}", index + 1, end)
            if close < 0:
                return None
            try:
                codepoint = int(text[index + 1 : close], 16)
                if codepoint > 0x10FFFF or 0xD800 <= codepoint <= 0xDFFF:
                    return None
                output.extend(chr(codepoint).encode("utf-8"))
            except (ValueError, UnicodeEncodeError):
                return None
            index = close + 1
        elif escaped in "\r\n":
            if escaped == "\r" and index < end and text[index] == "\n":
                index += 1
            output.append(10)
        elif escaped.isdigit():
            digits = escaped
            while index < end and len(digits) < 3 and text[index].isdigit():
                digits += text[index]
                index += 1
            value = int(digits, 10)
            if value > 255:
                return None
            output.append(value)
        else:
            # Luau rejects unknown escapes; leaving them untouched is safer.
            return None
    return bytes(output)


def _quote_bytes(value: bytes) -> str:
    try:
        text = value.decode("utf-8")
    except UnicodeDecodeError:
        pieces: list[str] = []
        for byte in value:
            if byte == 34:
                pieces.append("\\\"")
            elif byte == 92:
                pieces.append("\\\\")
            elif byte == 10:
                pieces.append("\\n")
            elif byte == 13:
                pieces.append("\\r")
            elif byte == 9:
                pieces.append("\\t")
            elif 32 <= byte < 127:
                pieces.append(chr(byte))
            else:
                pieces.append(f"\\{byte:03d}")
        return '"' + "".join(pieces) + '"'

    pieces = ['"']
    for character in text:
        codepoint = ord(character)
        if character == '"':
            pieces.append("\\\"")
        elif character == "\\":
            pieces.append("\\\\")
        elif character == "\n":
            pieces.append("\\n")
        elif character == "\r":
            pieces.append("\\r")
        elif character == "\t":
            pieces.append("\\t")
        elif codepoint < 32 or codepoint == 127:
            pieces.append(f"\\{codepoint:03d}")
        else:
            pieces.append(character)
    pieces.append('"')
    return "".join(pieces)


def _parse_number(text: str) -> int | float | object:
    lowered = text.lower()
    try:
        if lowered.startswith("0x"):
            if "p" in lowered or "." in lowered:
                return float.fromhex(text)
            return int(text, 16)
        if lowered.startswith("0b"):
            return int(text, 2)
        if any(marker in lowered for marker in (".", "e")):
            value = float(text)
            return value if math.isfinite(value) else _UNKNOWN
        return int(text, 10)
    except (ValueError, OverflowError):
        return _UNKNOWN


def _lua_truthy(value: Any) -> bool:
    return value is not _UNKNOWN and value is not None and value is not False


def _to_bytes(value: Any) -> bytes | object:
    if isinstance(value, bytes):
        return value
    if isinstance(value, bool):
        return ("true" if value else "false").encode("ascii")
    if isinstance(value, (int, float)):
        if isinstance(value, float) and not math.isfinite(value):
            return _UNKNOWN
        return format(value, ".15g").encode("ascii")
    return _UNKNOWN


def _integer(value: Any) -> int | object:
    if isinstance(value, bool):
        return _UNKNOWN
    if isinstance(value, int):
        return value
    if isinstance(value, float) and math.isfinite(value) and value.is_integer():
        return int(value)
    return _UNKNOWN


def _number(value: Any) -> int | float | object:
    if isinstance(value, (int, float)) and not isinstance(value, bool):
        return value
    return _UNKNOWN


def _decode_base64(value: bytes) -> bytes | object:
    compact = b"".join(value.split())
    if len(compact) > MAX_FOLDED_STRING_BYTES * 2:
        return _UNKNOWN
    if b"-" in compact or b"_" in compact:
        compact = compact.translate(bytes.maketrans(b"-_", b"+/"))
    compact += b"=" * ((-len(compact)) % 4)
    return base64.b64decode(compact, validate=True)


def _json_value(value: Any, budget: list[int], depth: int = 0) -> Any:
    budget[0] -= 1
    if budget[0] < 0 or depth > 24:
        raise ValueError("JSON value limit exceeded")
    if value is None or isinstance(value, bool):
        return value
    if isinstance(value, int):
        return value if abs(value) <= 2**53 else _UNKNOWN
    if isinstance(value, float):
        return value if math.isfinite(value) else _UNKNOWN
    if isinstance(value, str):
        encoded = value.encode("utf-8")
        if len(encoded) > MAX_FOLDED_STRING_BYTES:
            raise ValueError("JSON string limit exceeded")
        return encoded
    if isinstance(value, list):
        if len(value) > 4096:
            raise ValueError("JSON array limit exceeded")
        return _Table(tuple(_json_value(item, budget, depth + 1) for item in value))
    if isinstance(value, dict):
        if len(value) > 4096:
            raise ValueError("JSON object limit exceeded")
        fields = tuple(
            (key.encode("utf-8"), _json_value(item, budget, depth + 1))
            for key, item in value.items()
        )
        return _Table((), fields)
    raise ValueError("unsupported JSON value")


def _format_string(arguments: list[Any]) -> bytes | object:
    if not arguments or not isinstance(arguments[0], bytes):
        return _UNKNOWN
    template = arguments[0]
    if len(template) > MAX_FOLDED_STRING_BYTES:
        return _UNKNOWN
    values = arguments[1:]
    output = bytearray()
    cursor = 0
    value_index = 0
    while cursor < len(template):
        if template[cursor] != 37:
            output.append(template[cursor])
            cursor += 1
            continue
        if cursor + 1 < len(template) and template[cursor + 1] == 37:
            output.append(37)
            cursor += 2
            continue
        match = re.match(rb"%([-+#0 ]*)([0-9]{0,3})(?:\.([0-9]{0,3}))?([cdiuoxXfeEgGqs])", template[cursor:])
        if not match or value_index >= len(values):
            return _UNKNOWN
        flags = match.group(1).decode("ascii")
        width = int(match.group(2) or b"0")
        precision = int(match.group(3)) if match.group(3) is not None else None
        conversion = chr(match.group(4)[0])
        value = values[value_index]
        value_index += 1
        cursor += match.end()
        try:
            if conversion == "q":
                if not isinstance(value, bytes):
                    return _UNKNOWN
                rendered = _quote_bytes(value).encode("utf-8")
            elif conversion == "s":
                rendered_value = _to_bytes(value)
                if rendered_value is _UNKNOWN:
                    return _UNKNOWN
                if precision is not None:
                    rendered_value = rendered_value[:precision]
                padding = max(0, width - len(rendered_value))
                rendered = rendered_value + b" " * padding if "-" in flags else b" " * padding + rendered_value
            elif conversion == "c":
                integer = _integer(value)
                if integer is _UNKNOWN or not 0 <= integer <= 255:
                    return _UNKNOWN
                rendered = bytes((integer,))
            elif conversion in "diuoxX":
                integer = _integer(value)
                if integer is _UNKNOWN:
                    return _UNKNOWN
                if conversion == "u":
                    integer &= 0xFFFFFFFF
                spec_type = "d" if conversion in "diu" else conversion
                spec = ("<" if "-" in flags else ">")
                if "+" in flags:
                    spec += "+"
                elif " " in flags:
                    spec += " "
                if "#" in flags:
                    spec += "#"
                if "0" in flags and "-" not in flags:
                    spec += "0"
                if width:
                    spec += str(width)
                if precision is not None:
                    spec += "." + str(precision)
                spec += spec_type
                rendered = format(integer, spec).encode("ascii")
            else:
                number = _number(value)
                if number is _UNKNOWN or not math.isfinite(number):
                    return _UNKNOWN
                spec = "<" if "-" in flags else ">"
                if "+" in flags:
                    spec += "+"
                elif " " in flags:
                    spec += " "
                if "#" in flags:
                    spec += "#"
                if "0" in flags and "-" not in flags:
                    spec += "0"
                if width:
                    spec += str(width)
                if precision is not None:
                    spec += "." + str(precision)
                spec += conversion
                rendered = format(number, spec).encode("ascii")
        except (OverflowError, TypeError, ValueError):
            return _UNKNOWN
        output.extend(rendered)
        if len(output) > MAX_FOLDED_STRING_BYTES:
            return _UNKNOWN
    return bytes(output)


def _evaluate_call(name: str, arguments: list[Any]) -> Any:
    if any(value is _UNKNOWN for value in arguments):
        return _UNKNOWN
    try:
        if name == "string.char":
            integers = [_integer(value) for value in arguments]
            if any(value is _UNKNOWN or not 0 <= value <= 255 for value in integers):
                return _UNKNOWN
            result = bytes(integers)
            return result if len(result) <= MAX_FOLDED_STRING_BYTES else _UNKNOWN
        if name == "utf8.char":
            integers = [_integer(value) for value in arguments]
            if any(value is _UNKNOWN or not 0 <= value <= 0x10FFFF for value in integers):
                return _UNKNOWN
            if any(0xD800 <= value <= 0xDFFF for value in integers):
                return _UNKNOWN
            result = "".join(chr(value) for value in integers).encode("utf-8")
            return result if len(result) <= MAX_FOLDED_STRING_BYTES else _UNKNOWN
        if name == "string.reverse" and len(arguments) == 1 and isinstance(arguments[0], bytes):
            return arguments[0][::-1]
        if name in {"string.lower", "string.upper"} and len(arguments) == 1 and isinstance(arguments[0], bytes):
            return arguments[0].lower() if name.endswith("lower") else arguments[0].upper()
        if name == "string.rep" and 2 <= len(arguments) <= 3 and isinstance(arguments[0], bytes):
            count = _integer(arguments[1])
            separator = arguments[2] if len(arguments) == 3 else b""
            if count is _UNKNOWN or not isinstance(separator, bytes) or count < 0:
                return _UNKNOWN
            size = len(arguments[0]) * count + len(separator) * max(0, count - 1)
            if size > MAX_FOLDED_STRING_BYTES:
                return _UNKNOWN
            return separator.join([arguments[0]] * count)
        if name == "string.sub" and 2 <= len(arguments) <= 3 and isinstance(arguments[0], bytes):
            value = arguments[0]
            start = _integer(arguments[1])
            stop = _integer(arguments[2]) if len(arguments) == 3 else len(value)
            if start is _UNKNOWN or stop is _UNKNOWN:
                return _UNKNOWN
            first = max(0, start - 1 if start > 0 else len(value) + start if start < 0 else 0)
            last = max(0, stop if stop >= 0 else len(value) + stop + 1)
            return value[first:last]
        if name == "string.byte" and 1 <= len(arguments) <= 3 and isinstance(arguments[0], bytes):
            value = arguments[0]
            start = _integer(arguments[1]) if len(arguments) >= 2 else 1
            stop = _integer(arguments[2]) if len(arguments) >= 3 else start
            if start is _UNKNOWN or stop is _UNKNOWN:
                return _UNKNOWN
            first = start if start > 0 else len(value) + start + 1
            last = stop if stop > 0 else len(value) + stop + 1
            result = tuple(value[position - 1] for position in range(first, last + 1) if 1 <= position <= len(value))
            if len(arguments) == 3:
                return _MultiReturn(result)
            return result[0] if result else None
        if name in {"bit32.bxor", "bit.bxor", "bit32.band", "bit.band", "bit32.bor", "bit.bor", "bit32.btest"}:
            values = [_integer(value) for value in arguments]
            if any(value is _UNKNOWN for value in values):
                return _UNKNOWN
            if "xor" in name:
                result = 0
                for value in values:
                    result ^= value
            elif "band" in name or name.endswith("btest"):
                result = 0xFFFFFFFF
                for value in values:
                    result &= value
            else:
                result = 0
                for value in values:
                    result |= value
            result &= 0xFFFFFFFF
            return result != 0 if name.endswith("btest") else result
        if name in {"bit32.bnot", "bit.bnot"} and len(arguments) == 1:
            value = _integer(arguments[0])
            return (~value) & 0xFFFFFFFF if value is not _UNKNOWN else _UNKNOWN
        if name in {"bit32.lshift", "bit.lshift", "bit32.rshift", "bit.rshift", "bit32.arshift"} and len(arguments) == 2:
            value = _integer(arguments[0])
            shift = _integer(arguments[1])
            if value is _UNKNOWN or shift is _UNKNOWN:
                return _UNKNOWN
            unsigned = value & 0xFFFFFFFF
            direction = "left" if name.endswith("lshift") else "right"
            arithmetic = name.endswith("arshift")
            if shift < 0:
                shift = -shift
                direction = "left" if direction == "right" else "right"
                arithmetic = False
            if shift >= 32:
                if direction == "right" and arithmetic and unsigned & 0x80000000:
                    return 0xFFFFFFFF
                return 0
            if direction == "left":
                return (unsigned << shift) & 0xFFFFFFFF
            if arithmetic:
                signed = unsigned - 0x100000000 if unsigned & 0x80000000 else unsigned
                return (signed >> shift) & 0xFFFFFFFF
            return unsigned >> shift
        if name in {"bit32.lrotate", "bit32.rrotate", "bit.rol", "bit.ror"} and len(arguments) == 2:
            value = _integer(arguments[0])
            shift = _integer(arguments[1])
            if value is _UNKNOWN or shift is _UNKNOWN:
                return _UNKNOWN
            shift %= 32
            unsigned = value & 0xFFFFFFFF
            if name.endswith("rrotate") or name.endswith("ror"):
                shift = (-shift) % 32
            if shift == 0:
                return unsigned
            return ((unsigned << shift) | (unsigned >> (32 - shift))) & 0xFFFFFFFF
        if name == "bit32.extract" and 2 <= len(arguments) <= 3:
            value = _integer(arguments[0])
            field = _integer(arguments[1])
            width = _integer(arguments[2]) if len(arguments) == 3 else 1
            if value is _UNKNOWN or field is _UNKNOWN or width is _UNKNOWN:
                return _UNKNOWN
            if not 0 <= field <= 31 or not 0 <= width <= 32 or field + width > 32:
                return _UNKNOWN
            mask = 0xFFFFFFFF if width == 32 else (1 << width) - 1
            return ((value & 0xFFFFFFFF) >> field) & mask
        if name == "bit32.replace" and 3 <= len(arguments) <= 4:
            value = _integer(arguments[0])
            replacement = _integer(arguments[1])
            field = _integer(arguments[2])
            width = _integer(arguments[3]) if len(arguments) == 4 else 1
            if value is _UNKNOWN or replacement is _UNKNOWN or field is _UNKNOWN or width is _UNKNOWN:
                return _UNKNOWN
            if not 0 <= field <= 31 or not 0 <= width <= 32 or field + width > 32:
                return _UNKNOWN
            mask = 0xFFFFFFFF if width == 32 else (1 << width) - 1
            shifted_mask = (mask << field) & 0xFFFFFFFF
            return ((value & 0xFFFFFFFF) & ~shifted_mask | (replacement & mask) << field) & 0xFFFFFFFF
        if name in {"bit32.countlz", "bit32.countrz"} and len(arguments) == 1:
            value = _integer(arguments[0])
            if value is _UNKNOWN:
                return _UNKNOWN
            unsigned = value & 0xFFFFFFFF
            if name.endswith("countlz"):
                return 32 - unsigned.bit_length()
            return 32 if unsigned == 0 else (unsigned & -unsigned).bit_length() - 1
        base64_decode_names = {
            "base64.decode", "base64_decode", "base64decode", "base64Decode",
            "crypt.base64decode", "crypt.base64.decode", "syn.crypt.base64.decode",
            "syn.crypt.base64decode", "HttpService:Base64Decode", "HttpService.Base64Decode",
        }
        if name in base64_decode_names and len(arguments) == 1 and isinstance(arguments[0], bytes):
            return _decode_base64(arguments[0])
        if name in {"HttpService:Base64Encode", "HttpService.Base64Encode"} and len(arguments) == 1 and isinstance(arguments[0], bytes):
            return base64.b64encode(arguments[0])
        if name in {"HttpService:JSONDecode", "HttpService.JSONDecode"} and len(arguments) == 1 and isinstance(arguments[0], bytes):
            if len(arguments[0]) > MAX_FOLDED_STRING_BYTES:
                return _UNKNOWN
            decoded = json.loads(arguments[0].decode("utf-8"))
            return _json_value(decoded, [4096])
        if name == "table.concat" and 1 <= len(arguments) <= 4 and isinstance(arguments[0], _Table):
            separator = arguments[1] if len(arguments) >= 2 else b""
            first = _integer(arguments[2]) if len(arguments) >= 3 else 1
            last = _integer(arguments[3]) if len(arguments) >= 4 else len(arguments[0].values)
            if not isinstance(separator, bytes) or first is _UNKNOWN or last is _UNKNOWN:
                return _UNKNOWN
            if first < 1 or last < 0 or last > len(arguments[0].values):
                return _UNKNOWN
            values = arguments[0].values[first - 1 : last]
            parts = [_to_bytes(value) for value in values]
            if any(part is _UNKNOWN for part in parts):
                return _UNKNOWN
            result = separator.join(parts)
            return result if len(result) <= MAX_FOLDED_STRING_BYTES else _UNKNOWN
        if name in {"table.unpack", "unpack"} and 1 <= len(arguments) <= 3 and isinstance(arguments[0], _Table):
            first = _integer(arguments[1]) if len(arguments) >= 2 else 1
            last = _integer(arguments[2]) if len(arguments) >= 3 else len(arguments[0].values)
            if first is _UNKNOWN or last is _UNKNOWN or first < 1 or last > len(arguments[0].values):
                return _UNKNOWN
            if last < first:
                return _MultiReturn(())
            if last - first > 4096:
                return _UNKNOWN
            return _MultiReturn(arguments[0].values[first - 1 : last])
        if name == "string.format":
            return _format_string(arguments)
        if name == "tonumber" and 1 <= len(arguments) <= 2:
            value = arguments[0]
            base = _integer(arguments[1]) if len(arguments) == 2 else 10
            if base is _UNKNOWN or not 2 <= base <= 36:
                return _UNKNOWN
            if isinstance(value, bytes):
                text = value.decode("ascii").strip()
                if base == 10 and any(char in text.lower() for char in (".", "e")):
                    number = float(text)
                    return number if math.isfinite(number) else _UNKNOWN
                return int(text, base)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return value
        if name == "tostring" and len(arguments) == 1:
            value = arguments[0]
            if isinstance(value, bytes):
                return value
            if isinstance(value, bool):
                return b"true" if value else b"false"
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return _to_bytes(value)
        if name.startswith("math."):
            values = [_number(value) for value in arguments]
            if any(value is _UNKNOWN for value in values):
                return _UNKNOWN
            if name in {"math.floor", "math.ceil", "math.abs", "math.sqrt", "math.exp", "math.log", "math.sin", "math.cos", "math.tan", "math.asin", "math.acos", "math.deg", "math.rad", "math.sign"} and len(values) in {1, 2}:
                value = values[0]
                if not math.isfinite(value):
                    return _UNKNOWN
                if name == "math.floor":
                    return math.floor(value)
                if name == "math.ceil":
                    return math.ceil(value)
                if name == "math.abs":
                    return abs(value)
                if name == "math.sqrt":
                    return math.sqrt(value)
                if name == "math.exp":
                    return math.exp(value)
                if name == "math.log":
                    return math.log(value) if len(values) == 1 else math.log(value, values[1])
                if name == "math.sin":
                    return math.sin(value)
                if name == "math.cos":
                    return math.cos(value)
                if name == "math.tan":
                    return math.tan(value)
                if name == "math.asin":
                    return math.asin(value)
                if name == "math.acos":
                    return math.acos(value)
                if name == "math.deg":
                    return math.degrees(value)
                if name == "math.rad":
                    return math.radians(value)
                if name == "math.sign":
                    return (value > 0) - (value < 0)
            if name in {"math.min", "math.max"} and values:
                return min(values) if name == "math.min" else max(values)
            if name in {"math.fmod", "math.atan2", "math.pow"} and len(values) == 2:
                if name == "math.fmod":
                    return math.fmod(values[0], values[1])
                if name == "math.atan2":
                    return math.atan2(values[0], values[1])
                return values[0] ** values[1]
            if name == "math.clamp" and len(values) == 3 and values[1] <= values[2]:
                return min(max(values[0], values[1]), values[2])
            if name == "math.round" and len(values) == 1:
                value = values[0]
                return math.floor(value + 0.5) if value >= 0 else math.ceil(value - 0.5)
            if name == "math.modf" and len(values) == 1:
                value = values[0]
                integral = math.trunc(value)
                return _MultiReturn((integral, value - integral))
    except (ArithmeticError, OverflowError, ValueError, TypeError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError):
        return _UNKNOWN
    return _UNKNOWN


def _apply_binary(operator: str, left: Any, right: Any) -> Any:
    if operator == "and":
        if left is _UNKNOWN:
            return _UNKNOWN
        return right if _lua_truthy(left) else left
    if operator == "or":
        if left is _UNKNOWN:
            return _UNKNOWN
        return left if _lua_truthy(left) else right
    if left is _UNKNOWN or right is _UNKNOWN:
        return _UNKNOWN
    try:
        if operator == "..":
            first, second = _to_bytes(left), _to_bytes(right)
            if first is _UNKNOWN or second is _UNKNOWN or len(first) + len(second) > MAX_FOLDED_STRING_BYTES:
                return _UNKNOWN
            return first + second
        if operator in {"==", "~=", "<", "<=", ">", ">="}:
            if isinstance(left, _Table) or isinstance(right, _Table):
                return _UNKNOWN
            if type(left) is not type(right) and not (
                isinstance(left, (int, float)) and not isinstance(left, bool)
                and isinstance(right, (int, float)) and not isinstance(right, bool)
            ):
                if operator == "==":
                    return False
                if operator == "~=":
                    return True
                return _UNKNOWN
            return {
                "==": lambda: left == right,
                "~=": lambda: left != right,
                "<": lambda: left < right,
                "<=": lambda: left <= right,
                ">": lambda: left > right,
                ">=": lambda: left >= right,
            }[operator]()
        if operator in {"|", "&", "~", "<<", ">>"}:
            first, second = _integer(left), _integer(right)
            if first is _UNKNOWN or second is _UNKNOWN:
                return _UNKNOWN
            if operator == "|":
                return first | second
            if operator == "&":
                return first & second
            if operator == "~":
                return first ^ second
            shift = max(-63, min(63, second))
            if operator == "<<":
                return first << shift if shift >= 0 else first >> -shift
            return first >> shift if shift >= 0 else first << -shift
        if operator == "+":
            value = left + right
        elif operator == "-":
            value = left - right
        elif operator == "*":
            value = left * right
        elif operator == "/":
            value = left / right
        elif operator == "//":
            value = left // right
        elif operator == "%":
            value = left % right
        elif operator == "^":
            if abs(right) > 32 or abs(left) > 1_000_000:
                return _UNKNOWN
            value = left**right
        else:
            return _UNKNOWN
        if isinstance(value, (int, float)) and math.isfinite(value) and abs(value) <= 1e100:
            return value
    except (ArithmeticError, OverflowError, TypeError, ValueError):
        return _UNKNOWN
    return _UNKNOWN


def _table_get(value: _Table, key: Any) -> Any:
    if isinstance(key, bytes):
        for field_key, field_value in reversed(value.fields):
            if field_key == key:
                return field_value
        return None
    index = _integer(key)
    if index is _UNKNOWN:
        return _UNKNOWN
    if 1 <= index <= len(value.values):
        return value.values[index - 1]
    for field_key, field_value in reversed(value.fields):
        if field_key == index:
            return field_value
    return None


def _expand_multi_returns(arguments: list[Any]) -> list[Any]:
    expanded: list[Any] = []
    for index, value in enumerate(arguments):
        if not isinstance(value, _MultiReturn):
            expanded.append(value)
        elif index == len(arguments) - 1:
            expanded.extend(value.values)
        else:
            expanded.append(value.values[0] if value.values else None)
        if len(expanded) > 1024:
            return [_UNKNOWN]
    return expanded


class _ExpressionParser:
    def __init__(self, tokens: list[Token], start: int, environment: dict[str, Any] | None = None):
        self.tokens = tokens
        self.start = start
        self.environment = environment or {}
        self.operations: list[str] = []
        self.raw_value: Any = _UNKNOWN

    def _text(self, index: int) -> str:
        if index >= len(self.tokens) or self.tokens[index].kind == "comment":
            return ""
        return self.tokens[index].text

    def parse(self) -> tuple[Any, int]:
        if self.start >= len(self.tokens):
            return _UNKNOWN, self.start
        value, end = self._expression(self.start, 0)
        self.raw_value = value
        if isinstance(value, (_Namespace, _Path, _Function, _Receiver, _Game)):
            return _UNKNOWN, end
        return value, end

    def _expression(self, index: int, minimum: int) -> tuple[Any, int]:
        left, cursor = self._prefix(index)
        if cursor <= index:
            return _UNKNOWN, index
        while cursor < len(self.tokens):
            operator = self._text(cursor)
            precedence = _PRECEDENCE.get(operator)
            if precedence is None or precedence < minimum:
                break
            right_minimum = precedence if operator in _RIGHT_ASSOCIATIVE else precedence + 1
            right, next_cursor = self._expression(cursor + 1, right_minimum)
            if next_cursor <= cursor + 1:
                break
            if isinstance(left, (_Namespace, _Path, _Function, _Receiver, _Game)):
                left = _UNKNOWN
            if isinstance(right, (_Namespace, _Path, _Function, _Receiver, _Game)):
                right = _UNKNOWN
            if operator in {"and", "or"}:
                left = _apply_binary(operator, left, right)
            elif left is not _UNKNOWN and right is not _UNKNOWN:
                left = _apply_binary(operator, left, right)
            else:
                left = _UNKNOWN
            self.operations.append(operator)
            cursor = next_cursor
        return left, cursor

    def _prefix(self, index: int) -> tuple[Any, int]:
        if index >= len(self.tokens) or self.tokens[index].kind == "comment":
            return _UNKNOWN, index
        token = self.tokens[index]
        text = token.text
        if text in {"-", "+", "not", "~", "#"}:
            value, end = self._expression(index + 1, 3 if text == "not" else 11)
            if value is _UNKNOWN:
                return _UNKNOWN, end
            try:
                if text == "-" and isinstance(value, (int, float)) and not isinstance(value, bool):
                    result = -value
                elif text == "+" and isinstance(value, (int, float)) and not isinstance(value, bool):
                    result = +value
                elif text == "not":
                    result = not _lua_truthy(value)
                elif text == "~" and _integer(value) is not _UNKNOWN:
                    result = ~value
                elif text == "#" and isinstance(value, bytes):
                    result = len(value)
                elif text == "#" and isinstance(value, _Table) and all(
                    item is not None for item in value.values
                ):
                    result = len(value.values)
                else:
                    return _UNKNOWN, end
                self.operations.append("unary " + text)
                return result, end
            except (ArithmeticError, TypeError, ValueError):
                return _UNKNOWN, end
        if token.kind == "number":
            return _parse_number(text), index + 1
        if token.kind == "string":
            value = _decode_string(token)
            return (value if value is not None else _UNKNOWN), index + 1
        if text == "(":
            value, end = self._expression(index + 1, 0)
            if self._text(end) == ")":
                return value, end + 1
            return _UNKNOWN, end
        if text == "{":
            return self._table(index)
        if token.kind == "identifier":
            if text == "true":
                value: Any = True
            elif text == "false":
                value = False
            elif text == "nil":
                value = None
            elif text == "game":
                value = _Game()
            elif text == "HttpService":
                value = _Receiver("HttpService")
            elif text in self.environment:
                value = self.environment[text]
            elif text in {"string", "utf8", "bit32", "bit", "math", "table", "base64", "crypt", "syn"}:
                value = _Namespace(text)
            else:
                value = _Path(text)
            return self._postfix(value, index + 1)
        return _UNKNOWN, index + 1

    def _postfix(self, value: Any, cursor: int) -> tuple[Any, int]:
        while cursor < len(self.tokens):
            punctuation = self._text(cursor)
            if punctuation == "[":
                key, key_end = self._expression(cursor + 1, 0)
                if self._text(key_end) != "]":
                    return _UNKNOWN, self._skip_bracket(cursor)
                if isinstance(value, _Table):
                    value = _table_get(value, key)
                else:
                    value = _UNKNOWN
                cursor = key_end + 1
                continue
            if punctuation in {".", ":"} and self.tokens[cursor].kind == "symbol":
                member_index = cursor + 1
                if member_index >= len(self.tokens) or self.tokens[member_index].kind != "identifier":
                    break
                member = self.tokens[member_index].text
                if punctuation == ":" and isinstance(value, _Game) and member == "GetService":
                    if self._text(member_index + 1) != "(":
                        return _UNKNOWN, member_index + 1
                    arguments, end = self._arguments(member_index + 1)
                    value = _Receiver("HttpService") if arguments == [b"HttpService"] else _UNKNOWN
                    cursor = end
                    continue
                if punctuation == "." and isinstance(value, _Namespace) and value.name == "math":
                    if member == "pi":
                        value = math.pi
                    elif member == "huge":
                        value = math.inf
                    else:
                        value = _Function(value.name + "." + member)
                elif punctuation == "." and isinstance(value, _Table):
                    value = _table_get(value, member.encode("utf-8"))
                elif punctuation == ":" and isinstance(value, _Receiver):
                    value = _Function(value.name + ":" + member)
                elif punctuation == "." and isinstance(value, _Receiver):
                    value = _Function(value.name + "." + member)
                elif isinstance(value, (_Namespace, _Path, _Function)):
                    value = _Function(value.name + "." + member)
                else:
                    value = _UNKNOWN
                cursor = member_index + 1
                continue
            if punctuation == "(" and isinstance(value, _Function):
                arguments, end = self._arguments(cursor)
                value = _evaluate_call(value.name, arguments)
                self.operations.append(value.__class__.__name__ if value is not _UNKNOWN else "call")
                cursor = end
                continue
            if punctuation == "(":
                _, end = self._arguments(cursor)
                value = _UNKNOWN
                cursor = end
                continue
            break
        return value, cursor

    def _skip_bracket(self, opening: int) -> int:
        depth = 1
        cursor = opening + 1
        while cursor < len(self.tokens):
            text = self._text(cursor)
            if text == "[":
                depth += 1
            elif text == "]":
                depth -= 1
                if depth == 0:
                    return cursor + 1
            cursor += 1
        return cursor

    def _arguments(self, opening: int) -> tuple[list[Any], int]:
        arguments: list[Any] = []
        cursor = opening + 1
        if self._text(cursor) == ")":
            return arguments, cursor + 1
        while cursor < len(self.tokens):
            value, end = self._expression(cursor, 0)
            if end <= cursor:
                return [_UNKNOWN], cursor + 1
            arguments.append(value)
            if len(arguments) > 1024:
                return [_UNKNOWN], end
            cursor = end
            if self._text(cursor) == ",":
                cursor += 1
                continue
            if self._text(cursor) == ")":
                return _expand_multi_returns(arguments), cursor + 1
            return [_UNKNOWN], cursor
        return [_UNKNOWN], cursor

    def _table(self, opening: int) -> tuple[Any, int]:
        indexed_values: dict[int, Any] = {}
        fields: list[tuple[Any, Any]] = []
        next_array_index = 1
        cursor = opening + 1
        if self._text(cursor) == "}":
            return _Table(()), cursor + 1

        while cursor < len(self.tokens):
            cursor = self._skip_comments(cursor)
            if self._text(cursor) == "}":
                values = tuple(indexed_values.get(index) for index in range(1, max(indexed_values, default=0) + 1))
                return _Table(values, tuple(fields)), cursor + 1

            if self.tokens[cursor].kind == "identifier" and self._text(cursor + 1) == "=":
                key: Any = self.tokens[cursor].text.encode("utf-8")
                value, end = self._expression(cursor + 2, 0)
                if end <= cursor + 2:
                    return _UNKNOWN, self._skip_table(cursor)
                fields.append((key, value))
                cursor = end
            elif self._text(cursor) == "[":
                key, key_end = self._expression(cursor + 1, 0)
                if self._text(key_end) != "]" or self._text(key_end + 1) != "=":
                    return _UNKNOWN, self._skip_table(cursor)
                value, end = self._expression(key_end + 2, 0)
                if end <= key_end + 2:
                    return _UNKNOWN, self._skip_table(cursor)
                integer_key = _integer(key)
                if integer_key is not _UNKNOWN and 1 <= integer_key <= 4096:
                    indexed_values[integer_key] = value
                elif isinstance(key, bytes) or integer_key is not _UNKNOWN:
                    fields.append((key, value))
                else:
                    return _UNKNOWN, self._skip_table(cursor)
                cursor = end
            else:
                value, end = self._expression(cursor, 0)
                if end <= cursor:
                    return _UNKNOWN, self._skip_table(cursor)
                indexed_values[next_array_index] = value
                next_array_index += 1
                cursor = end

            cursor = self._skip_comments(cursor)
            if self._text(cursor) in {",", ";"}:
                cursor += 1
                continue
            if self._text(cursor) == "}":
                values = tuple(indexed_values.get(index) for index in range(1, max(indexed_values, default=0) + 1))
                return _Table(values, tuple(fields)), cursor + 1
            return _UNKNOWN, self._skip_table(cursor)
        return _UNKNOWN, cursor

    def _skip_comments(self, cursor: int) -> int:
        while cursor < len(self.tokens) and self.tokens[cursor].kind == "comment":
            cursor += 1
        return cursor

    def _skip_table(self, cursor: int) -> int:
        depth = 1
        while cursor < len(self.tokens):
            text = self._text(cursor)
            if text == "{":
                depth += 1
            elif text == "}":
                depth -= 1
                if depth == 0:
                    return cursor + 1
            cursor += 1
        return cursor


def _render_value(value: Any) -> str | None:
    if isinstance(value, bytes):
        return _quote_bytes(value) if len(value) <= MAX_FOLDED_STRING_BYTES else None
    if value is None:
        return "nil"
    if isinstance(value, bool):
        return "true" if value else "false"
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float) and math.isfinite(value):
        return format(value, ".15g")
    return None


def _unary_operator_allowed(tokens: list[Token], index: int) -> bool:
    previous_index = index - 1
    while previous_index >= 0 and tokens[previous_index].kind == "comment":
        previous_index -= 1
    if previous_index < 0:
        return True
    previous = tokens[previous_index]
    if previous.kind == "symbol":
        return previous.text in {
            "(", "[", "{", ",", ";", "=", "+", "-", "*", "/", "//", "%", "^",
            "..", "==", "~=", "<", "<=", ">", ">=", "|", "&", "~", "<<", ">>",
            "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=",
        }
    return previous.kind == "identifier" and previous.text in {
        "return", "then", "do", "else", "elseif", "until", "in", "and", "or", "not",
    }


@dataclass(frozen=True)
class _LocalBinding:
    name: str
    value: Any
    declaration_index: int
    available_from: int
    scope_path: tuple[int, ...]


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


def _is_statement_if(source: str, tokens: list[Token], index: int) -> bool:
    previous_index = _previous_code_index(tokens, index)
    if previous_index < 0:
        return True
    previous = tokens[previous_index]
    if previous.text in {"then", "else", "elseif", "do", "repeat", ";"}:
        return True
    if previous.text in {
        "return", "=", ",", "(", "[", "{", "+", "-", "*", "/", "//", "%", "^",
        "..", "==", "~=", "<", "<=", ">", ">=", "|", "&", "~", "<<", ">>",
        "and", "or", "not", "::",
    }:
        return False
    gap = source[previous.end : tokens[index].start]
    return "\n" in gap or "\r" in gap


def _scope_paths(source: str, tokens: list[Token]) -> list[tuple[int, ...]] | None:
    # A Luau if-expression has no `end`; leave local propagation disabled for
    # such a file rather than risk treating its `then` as a statement block.
    if any(
        token.kind == "identifier" and token.text == "if" and not _is_statement_if(source, tokens, index)
        for index, token in enumerate(tokens)
    ):
        return None

    paths: list[tuple[int, ...]] = []
    stack: list[dict[str, Any]] = []
    next_scope = 1

    def push(kind: str, *, scope: bool = True) -> None:
        nonlocal next_scope
        stack.append({"kind": kind, "scope": next_scope if scope else None, "awaiting_then": False})
        if scope:
            next_scope += 1

    def current_path() -> tuple[int, ...]:
        return tuple(frame["scope"] for frame in stack if frame["scope"] is not None)

    for index, token in enumerate(tokens):
        paths.append(current_path())
        if token.kind != "identifier":
            continue
        text = token.text
        if text == "if":
            push("if", scope=False)
            stack[-1]["awaiting_then"] = True
        elif text == "then":
            for frame in reversed(stack):
                if frame["kind"] == "if" and frame["awaiting_then"]:
                    frame["awaiting_then"] = False
                    push("if-branch")
                    break
        elif text in {"else", "elseif"}:
            if stack and stack[-1]["kind"] == "if-branch":
                stack.pop()
            if stack and stack[-1]["kind"] == "if":
                if text == "elseif":
                    stack[-1]["awaiting_then"] = True
                else:
                    push("if-branch")
        elif text == "function":
            push("function")
        elif text in {"for", "while"}:
            push("loop-pending", scope=False)
        elif text == "do":
            if stack and stack[-1]["kind"] == "loop-pending":
                stack[-1]["kind"] = "loop"
                stack[-1]["scope"] = next_scope
                next_scope += 1
            else:
                push("do")
        elif text == "repeat":
            push("repeat")
        elif text == "until":
            if stack and stack[-1]["kind"] == "repeat":
                stack.pop()
        elif text == "end":
            if stack and stack[-1]["kind"] == "if-branch":
                stack.pop()
                if stack and stack[-1]["kind"] == "if":
                    stack.pop()
            elif stack:
                stack.pop()
    return paths


def _local_declaration_counts(tokens: list[Token]) -> dict[str, int]:
    counts: dict[str, int] = {}
    for index, token in enumerate(tokens):
        if token.kind != "identifier" or token.text != "local":
            continue
        cursor = _next_code_index(tokens, index)
        if cursor >= len(tokens):
            continue
        if tokens[cursor].text == "function":
            cursor = _next_code_index(tokens, cursor)
            if cursor < len(tokens) and tokens[cursor].kind == "identifier":
                name = tokens[cursor].text
                counts[name] = counts.get(name, 0) + 1
            continue
        while cursor < len(tokens) and tokens[cursor].kind == "identifier":
            name = tokens[cursor].text
            counts[name] = counts.get(name, 0) + 1
            cursor = _next_code_index(tokens, cursor)
            if cursor < len(tokens) and tokens[cursor].text == ":":
                cursor += 1
                while cursor < len(tokens) and tokens[cursor].text not in {",", "="}:
                    cursor += 1
            if cursor < len(tokens) and tokens[cursor].text == ",":
                cursor = _next_code_index(tokens, cursor)
                continue
            break
    return counts


def _function_has_parameter(tokens: list[Token], name: str) -> bool:
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
            text = tokens[cursor].text
            if text == "(":
                depth += 1
            elif text == ")":
                depth -= 1
            elif depth and tokens[cursor].kind == "identifier" and text == name:
                return True
            cursor += 1
    return False


def _for_declares_name(tokens: list[Token], name: str) -> bool:
    for index, token in enumerate(tokens):
        if token.kind != "identifier" or token.text != "for":
            continue
        cursor = index + 1
        while cursor < len(tokens) and tokens[cursor].text not in {"in", "=", "do"}:
            if tokens[cursor].kind == "identifier" and tokens[cursor].text == name:
                return True
            cursor += 1
    return False


def _is_property_or_table_key(tokens: list[Token], index: int) -> bool:
    previous = _previous_code_index(tokens, index)
    following = _next_code_index(tokens, index)
    if previous >= 0 and tokens[previous].text in {".", ":", "::"}:
        return True
    if following < len(tokens) and tokens[following].text == "::":
        return True
    if following < len(tokens) and tokens[following].text == "=" and previous >= 0:
        if tokens[previous].text in {"{", ","}:
            depth = 0
            for cursor in range(index - 1, -1, -1):
                text = tokens[cursor].text
                if tokens[cursor].kind == "comment":
                    continue
                if text == "}":
                    depth += 1
                elif text == "{":
                    if depth:
                        depth -= 1
                    else:
                        return True
                elif depth == 0 and text in {";", "then", "do", "end", "return"}:
                    break
    return False


def _multi_assignment_target(tokens: list[Token], index: int) -> bool:
    following = _next_code_index(tokens, index)
    if following >= len(tokens) or tokens[following].text != ",":
        return False
    depths = {"(": 0, "[": 0, "{": 0}
    closing = {")": "(", "]": "[", "}": "{"}
    cursor = following + 1
    while cursor < len(tokens):
        token = tokens[cursor]
        if token.kind == "comment":
            cursor += 1
            continue
        text = token.text
        if text in depths:
            depths[text] += 1
        elif text in closing:
            opener = closing[text]
            if depths[opener] > 0:
                depths[opener] -= 1
        elif not any(depths.values()):
            if text == "=":
                return True
            if text in {";", "then", "do", "end", "else", "elseif", "return"}:
                return False
        cursor += 1
    return False


def _qualified_name_before(tokens: list[Token], opening: int) -> str:
    cursor = _previous_code_index(tokens, opening)
    if cursor < 0 or tokens[cursor].kind != "identifier":
        return ""
    parts = [tokens[cursor].text]
    cursor = _previous_code_index(tokens, cursor)
    while cursor >= 0 and tokens[cursor].text in {".", ":"}:
        member = _previous_code_index(tokens, cursor)
        if member < 0 or tokens[member].kind != "identifier":
            break
        parts.append(tokens[member].text)
        cursor = _previous_code_index(tokens, member)
    return ".".join(reversed(parts))


def _enclosing_call_name(tokens: list[Token], index: int) -> str:
    depths = {")": 0, "]": 0, "}": 0}
    matching = {"(": ")", "[": "]", "{": "}"}
    for cursor in range(index - 1, -1, -1):
        token = tokens[cursor]
        if token.kind == "comment":
            continue
        text = token.text
        if text in depths:
            depths[text] += 1
        elif text in matching:
            expected_closer = matching[text]
            if depths[expected_closer] > 0:
                depths[expected_closer] -= 1
            elif text == "(" and not any(depths.values()):
                return _qualified_name_before(tokens, cursor)
    return ""


def _table_binding_is_read_only(tokens: list[Token], name: str, declaration_index: int) -> bool:
    for index, token in enumerate(tokens):
        if token.kind != "identifier" or token.text != name or index == declaration_index:
            continue
        if _is_property_or_table_key(tokens, index):
            continue
        previous = _previous_code_index(tokens, index)
        following = _next_code_index(tokens, index)
        if following >= len(tokens):
            return False
        next_text = tokens[following].text
        if next_text == "[":
            depth = 1
            cursor = following + 1
            while cursor < len(tokens) and depth:
                if tokens[cursor].text == "[":
                    depth += 1
                elif tokens[cursor].text == "]":
                    depth -= 1
                cursor += 1
            after_index = _next_code_index(tokens, cursor - 1)
            if after_index < len(tokens) and tokens[after_index].text in {"=", "+=", "-=", "*=", "/=", "%="}:
                return False
            continue
        if next_text == ".":
            member = _next_code_index(tokens, following)
            after_member = _next_code_index(tokens, member)
            if after_member < len(tokens) and tokens[after_member].text in {"=", "+=", "-=", "*=", "/=", "%="}:
                return False
            continue
        if previous >= 0 and tokens[previous].text == "#":
            continue
        if previous >= 0 and tokens[previous].text in {"(", ","}:
            call_name = _enclosing_call_name(tokens, index)
            if call_name in {"table.concat", "table.unpack", "unpack"}:
                continue
        return False
    return True


def _binding_value(value: Any) -> Any:
    if isinstance(value, _MultiReturn):
        value = value.values[0] if value.values else None
    if value is _UNKNOWN or isinstance(value, (_Path,)):
        return _UNKNOWN
    if isinstance(value, bytes):
        return value if len(value) <= MAX_FOLDED_STRING_BYTES else _UNKNOWN
    if isinstance(value, float) and math.isnan(value):
        return _UNKNOWN
    if isinstance(value, _Table):
        if len(value.values) > 4096 or len(value.fields) > 4096:
            return _UNKNOWN
        members = (*value.values, *(item for _, item in value.fields))
        if any(_binding_value(item) is _UNKNOWN for item in members):
            return _UNKNOWN
        return value
    if isinstance(value, (_Namespace, _Function, _Receiver, _Game)):
        return value
    if value is None or isinstance(value, (bool, int, float)):
        return value
    return _UNKNOWN


def _function_parameter_names(tokens: list[Token]) -> set[str]:
    names: set[str] = set()
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
        expect_name = True
        cursor += 1
        while cursor < len(tokens) and depth:
            text = tokens[cursor].text
            if text == "(":
                depth += 1
            elif text == ")":
                depth -= 1
            elif depth == 1 and text == ",":
                expect_name = True
            elif depth == 1 and expect_name and tokens[cursor].kind == "identifier":
                names.add(text)
                expect_name = False
            elif depth == 1 and text == "...":
                expect_name = False
            cursor += 1
    return names


def _loop_variable_names(tokens: list[Token]) -> set[str]:
    names: set[str] = set()
    for index, token in enumerate(tokens):
        if token.kind != "identifier" or token.text != "for":
            continue
        cursor = index + 1
        while cursor < len(tokens) and tokens[cursor].text not in {"in", "=", "do"}:
            if tokens[cursor].kind == "identifier":
                names.add(tokens[cursor].text)
            cursor += 1
    return names


def _written_names(tokens: list[Token]) -> set[str]:
    names: set[str] = set()
    assignment_ops = {"=", "+=", "-=", "*=", "/=", "%=", "^=", "&=", "|=", "..="}
    for index, token in enumerate(tokens):
        if token.kind != "identifier":
            continue
        previous = _previous_code_index(tokens, index)
        if previous >= 0 and tokens[previous].text in {"local", "for"}:
            continue
        if previous >= 0 and tokens[previous].text == "function":
            names.add(token.text)
            continue
        if _is_property_or_table_key(tokens, index):
            continue
        following = _next_code_index(tokens, index)
        if following < len(tokens) and tokens[following].text in assignment_ops:
            names.add(token.text)
        elif _multi_assignment_target(tokens, index):
            names.add(token.text)
    return names


def _stable_local_name(
    name: str,
    declaration_counts: dict[str, int],
    parameter_names: set[str],
    loop_names: set[str],
    written_names: set[str],
) -> bool:
    return (
        declaration_counts.get(name, 0) == 1
        and name not in parameter_names
        and name not in loop_names
        and name not in written_names
    )


def _collect_local_constants(
    source: str, tokens: list[Token]
) -> tuple[list[_LocalBinding], list[tuple[int, ...]] | None]:
    paths = _scope_paths(source, tokens)
    if paths is None:
        return [], None
    declaration_counts = _local_declaration_counts(tokens)
    parameter_names = _function_parameter_names(tokens)
    loop_names = _loop_variable_names(tokens)
    written_names = _written_names(tokens)
    bindings: list[_LocalBinding] = []
    active: dict[str, _LocalBinding] = {}
    scheduled: dict[int, list[_LocalBinding]] = {}

    for index, token in enumerate(tokens):
        scope = paths[index]
        for name, binding in tuple(active.items()):
            if scope[: len(binding.scope_path)] != binding.scope_path:
                del active[name]
        for binding in scheduled.pop(index, ()):
            if scope[: len(binding.scope_path)] == binding.scope_path:
                active[binding.name] = binding
                bindings.append(binding)

        if token.kind != "identifier" or token.text != "local":
            continue
        name_index = _next_code_index(tokens, index)
        equal_index = _next_code_index(tokens, name_index)
        if (
            name_index >= len(tokens)
            or tokens[name_index].kind != "identifier"
            or equal_index >= len(tokens)
            or tokens[equal_index].text != "="
        ):
            continue
        name = tokens[name_index].text
        if not _stable_local_name(
            name, declaration_counts, parameter_names, loop_names, written_names
        ):
            continue
        value_index = _next_code_index(tokens, equal_index)
        parser = _ExpressionParser(tokens, value_index, {key: item.value for key, item in active.items()})
        _, end = parser.parse()
        value = _binding_value(parser.raw_value)
        if value is _UNKNOWN or end <= value_index:
            continue
        if isinstance(value, _Table) and not _table_binding_is_read_only(tokens, name, name_index):
            continue
        binding = _LocalBinding(name, value, index, end, scope)
        scheduled.setdefault(end, []).append(binding)

    return bindings, paths


def _rewrite_once(source: str) -> tuple[str, int, int, dict[str, int]]:
    tokens = tokenize(source)
    bindings, paths = _collect_local_constants(source, tokens)
    if paths is None:
        paths = [()] * len(tokens)
    bindings.sort(key=lambda binding: binding.available_from)
    active_bindings: dict[str, _LocalBinding] = {}
    active_environment: dict[str, Any] = {}
    next_binding = 0
    edits: list[tuple[int, int, str]] = []
    expression_count = 0
    string_count = 0
    transformations: dict[str, int] = {}
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
        if token.text in {"+", "-", "~", "#"} and not _unary_operator_allowed(tokens, index):
            index += 1
            continue
        if token.kind == "identifier" and _is_property_or_table_key(tokens, index):
            index += 1
            continue
        if token.text == "(":
            previous = _previous_code_index(tokens, index)
            if previous >= 0 and (
                tokens[previous].kind in {"identifier", "number", "string"}
                or tokens[previous].text in {")", "]", "}",
            }):
                index += 1
                continue
        parser = _ExpressionParser(tokens, index, active_environment)
        value, end = parser.parse()
        if value is not _UNKNOWN and end > index:
            rendered = _render_value(value)
            if rendered is not None:
                first = tokens[index]
                last = tokens[end - 1]
                old = source[first.start : last.end]
                is_literal_string = token.kind == "string" and end == index + 1
                is_local_reference = token.kind == "identifier" and token.text in active_environment
                should_replace = end > index + 1 or is_literal_string or is_local_reference
                if should_replace and old != rendered:
                    edits.append((first.start, last.end, rendered))
                    if isinstance(value, bytes):
                        string_count += 1
                        transformations["decoded string expression"] = (
                            transformations.get("decoded string expression", 0) + 1
                        )
                        if is_local_reference:
                            transformations["immutable local/API propagation"] = (
                                transformations.get("immutable local/API propagation", 0) + 1
                            )
                    else:
                        expression_count += 1
                        transformations["constant expression"] = (
                            transformations.get("constant expression", 0) + 1
                        )
                        if is_local_reference:
                            transformations["immutable local/API propagation"] = (
                                transformations.get("immutable local/API propagation", 0) + 1
                            )
                    index = end
                    continue
        index += 1

    if not edits:
        return source, 0, 0, {}
    for start, end, replacement in reversed(edits):
        source = source[:start] + replacement + source[end:]
    return source, expression_count, string_count, transformations


def deobfuscate_source(source: str) -> DeobfuscationResult:
    if not isinstance(source, str):
        raise TypeError("source must be text")
    input_bytes = len(source.encode("utf-8"))
    if input_bytes > MAX_SOURCE_BYTES:
        raise ValueError(f"Input exceeds the {MAX_SOURCE_BYTES // (1024 * 1024)} MiB analysis limit")

    current = source
    total_expressions = 0
    total_strings = 0
    pass_count = 0
    totals: dict[str, int] = {}
    for _ in range(MAX_TRANSFORM_PASSES):
        updated, expressions, strings, transformations = _rewrite_once(current)
        if updated == current:
            break
        if len(updated.encode("utf-8")) > MAX_SOURCE_BYTES:
            break
        current = updated
        pass_count += 1
        total_expressions += expressions
        total_strings += strings
        for name, count in transformations.items():
            totals[name] = totals.get(name, 0) + count

    messages = tuple(f"{name}: {count}" for name, count in sorted(totals.items()))
    return DeobfuscationResult(
        source=current,
        passes=pass_count,
        folded_expressions=total_expressions,
        decoded_strings=total_strings,
        transformations=messages,
        input_bytes=input_bytes,
        output_bytes=len(current.encode("utf-8")),
    )


__all__ = ["DeobfuscationResult", "deobfuscate_source", "tokenize"]
