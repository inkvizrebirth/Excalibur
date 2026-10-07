"""Luau standard-library gaps for the portable backend.

Roblox runs Luau, so a Roblox loader may probe for functions Lua 5.1 does not
have.  ``core.injector_env`` fills the gaps it can express in Lua (``bit32``,
``table.pack``/``unpack``, ``utf8``, the task scheduler); what is left is
``string.pack``/``unpack``/``packsize``, whose format handling is fiddly enough
that implementing it in Lua would be a source of wrong answers.

Reloading an IronBrew3 wrapper shows why this matters: its loader starts with

    if not (string.pack and string.unpack) then
        -- "Your Lua version is missing functions required by Ironbrew!"
        error(...)
    end

so a Luau environment without ``string.pack`` stops the loader before it
decodes a single byte.  These functions implement the Lua 5.3/Luau format
strings on top of Python's :mod:`struct`, which is the same code path the
native Luau build uses:

* integers ``b/B h/H l/L j/J i[n]/I[n]``, ``f``, ``d``, ``n``, ``T``;
* strings ``c[n]`` (fixed), ``s[n]`` (length-prefixed), ``z`` (zero-terminated);
* padding ``x`` and ``Xop``, alignment ``!n``, endianness ``< > =``.

Anything else raises a Lua error instead of returning silently wrong bytes.
"""

from __future__ import annotations

import struct as _struct
from typing import Any, Iterable

__all__ = ["install_string_pack", "MISSING_IN_LUA51"]

#: What Lua 5.1 lacks and the portable backend provides from Python.
MISSING_IN_LUA51 = ("string.pack", "string.unpack", "string.packsize")

_INT_OPTIONS = {"b": (1, True), "B": (1, False), "h": (2, True), "H": (2, False),
                "l": (8, True), "L": (8, False), "j": (8, True), "J": (8, False)}
_FLOAT_OPTIONS = {"f": 4, "d": 8, "n": 8, "T": 8}
_MAX_ALIGNMENT = 8


class FormatError(ValueError):
    """A pack/unpack format this implementation does not support."""


class _Option:
    __slots__ = ("kind", "size", "signed", "little", "align")

    def __init__(self, kind: str, size: int = 0, signed: bool = False,
                 little: bool = True, align: int = 1):
        self.kind = kind
        self.size = size
        self.signed = signed
        self.little = little
        self.align = align


def _digits(text: str, index: int) -> tuple[int | None, int]:
    start = index
    while index < len(text) and text[index].isdigit():
        index += 1
    if index == start:
        return None, start
    return int(text[start:index]), index


def _options(format: str) -> Iterable[_Option]:
    little = True
    max_align = 1
    index = 0
    while index < len(format):
        option = format[index]
        index += 1
        if option in "<>=":
            little = option != ">"
            continue
        if option == "!":
            size, index = _digits(format, index)
            max_align = size if size is not None else _MAX_ALIGNMENT
            continue
        if option == "x":
            yield _Option("x", size=1, align=max_align)
            continue
        if option == "X":
            if index >= len(format):
                raise FormatError("'X' needs an option after it")
            inner_index = index + 1
            _, inner_index = _digits(format, inner_index)
            index = inner_index
            yield _Option("align", align=max_align)
            continue
        size, index = _digits(format, index)
        if option in _INT_OPTIONS:
            default_size, signed = _INT_OPTIONS[option]
            width = size if size is not None else default_size
            if not 1 <= width <= 8:
                raise FormatError("integer size %d is not supported" % width)
            yield _Option("i", size=width, signed=signed, little=little, align=max_align)
        elif option in ("i", "I"):
            width = size if size is not None else 4
            if not 1 <= width <= 8:
                raise FormatError("integer size %d is not supported" % width)
            yield _Option("i", size=width, signed=option == "i", little=little, align=max_align)
        elif option in _FLOAT_OPTIONS:
            yield _Option("f", size=_FLOAT_OPTIONS[option], little=little, align=max_align)
        elif option == "c":
            if size is None:
                raise FormatError("'c' needs a size")
            yield _Option("c", size=size, align=max_align)
        elif option == "s":
            yield _Option("s", size=size if size is not None else 8, align=max_align)
        elif option == "z":
            yield _Option("z", align=max_align)
        else:
            raise FormatError("unsupported format option %r" % option)


def _pad(offset: int, align: int) -> int:
    if align <= 1:
        return 0
    remainder = offset % min(align, _MAX_ALIGNMENT)
    return 0 if remainder == 0 else min(align, _MAX_ALIGNMENT) - remainder


def _as_int(value: Any) -> int:
    if isinstance(value, bool):
        return 1 if value else 0
    number = float(value)
    if number != number:  # NaN
        raise FormatError("cannot pack NaN as an integer")
    return int(number)


def _as_float(value: Any) -> float:
    return float(value)


def _pack(format: str, values: Iterable[Any]) -> bytes:
    arguments = list(values)
    position = 0
    out = bytearray()
    for option in _options(format):
        if option.kind == "x":
            out.append(0)
            continue
        if option.kind == "align":
            out.extend(b"\0" * _pad(len(out), option.align))
            continue
        out.extend(b"\0" * _pad(len(out), option.align))
        if position >= len(arguments):
            raise FormatError("not enough arguments for the format")
        value = arguments[position]
        position += 1
        endian = "<" if option.little else ">"
        if option.kind == "i":
            signature = {1: "b", 2: "h", 4: "i", 8: "q"}[option.size] if option.size in (1, 2, 4, 8) \
                else None
            number = _as_int(value)
            if signature is None:
                mask = (1 << (option.size * 8)) - 1
                number &= mask
                raw = number.to_bytes(option.size, "little" if option.little else "big")
                out.extend(raw)
                continue
            if not option.signed:
                signature = signature.upper()
            try:
                out.extend(_struct.pack(endian + signature, number))
            except _struct.error as exc:
                # Lua wraps instead of raising: mask and write the low bytes.
                mask = (1 << (option.size * 8)) - 1
                raw = (number & mask).to_bytes(option.size, "little" if option.little else "big")
                out.extend(raw)
                del exc
        elif option.kind == "f":
            signature = {4: "f", 8: "d"}[option.size]
            out.extend(_struct.pack(endian + signature, _as_float(value)))
        elif option.kind == "c":
            raw = value if isinstance(value, (bytes, bytearray)) else str(value).encode("latin-1")
            if len(raw) > option.size:
                raise FormatError("string longer than the given size for 'c%d'" % option.size)
            out.extend(raw)
            out.extend(b"\0" * (option.size - len(raw)))
        elif option.kind == "s":
            raw = value if isinstance(value, (bytes, bytearray)) else str(value).encode("latin-1")
            out.extend(len(raw).to_bytes(option.size, "little" if option.little else "big"))
            out.extend(raw)
        elif option.kind == "z":
            raw = value if isinstance(value, (bytes, bytearray)) else str(value).encode("latin-1")
            if b"\0" in raw:
                raise FormatError("string contains a zero byte, which 'z' cannot carry")
            out.extend(raw)
            out.append(0)
    return bytes(out)


def _packsize(format: str) -> int:
    total = 0
    for option in _options(format):
        if option.kind in ("s", "z"):
            raise FormatError("variable-length format")
        total += _pad(total, option.align)
        if option.kind == "align":
            continue
        total += option.size
    return total


def _unpack(format: str, data: bytes, start: int = 1) -> tuple[list[Any], int]:
    offset = max(0, int(start) - 1)
    values: list[Any] = []
    for option in _options(format):
        if option.kind == "x":
            offset += 1
            continue
        offset += _pad(offset, option.align)
        if option.kind == "align":
            continue
        endian = "<" if option.little else ">"
        if option.kind == "i":
            chunk = data[offset : offset + option.size]
            if len(chunk) < option.size:
                raise FormatError("data string too short")
            number = int.from_bytes(chunk, "little" if option.little else "big")
            if option.signed:
                limit = 1 << (option.size * 8 - 1)
                if number >= limit:
                    number -= limit * 2
            values.append(number)
            offset += option.size
        elif option.kind == "f":
            chunk = data[offset : offset + option.size]
            if len(chunk) < option.size:
                raise FormatError("data string too short")
            signature = {4: "f", 8: "d"}[option.size]
            values.append(_struct.unpack(endian + signature, chunk)[0])
            offset += option.size
        elif option.kind == "c":
            chunk = data[offset : offset + option.size]
            values.append(chunk.decode("latin-1"))
            offset += option.size
        elif option.kind == "s":
            header = data[offset : offset + option.size]
            if len(header) < option.size:
                raise FormatError("data string too short")
            length = int.from_bytes(header, "little" if option.little else "big")
            offset += option.size
            values.append(data[offset : offset + length].decode("latin-1"))
            offset += length
        elif option.kind == "z":
            end = data.find(b"\0", offset)
            if end < 0:
                raise FormatError("unfinished string for 'z'")
            values.append(data[offset:end].decode("latin-1"))
            offset = end + 1
    return values, offset + 1


def _to_bytes(value: Any) -> bytes:
    if isinstance(value, (bytes, bytearray)):
        return bytes(value)
    return str(value).encode("latin-1")


#: The Python callables cross the bridge as callable *userdata*, and scripts do
#: check ``type(string.pack) == 'function'``, so each one gets a thin Lua
#: closure in front of it.
_WRAPPERS = """
string.pack = function(format, ...) return __protez_string_pack(format, ...) end
string.unpack = function(format, data, position)
  return __protez_string_unpack(format, data, position)
end
string.packsize = function(format) return __protez_string_packsize(format) end
"""


def install_string_pack(runtime: Any) -> None:
    """Fill ``string.pack``/``unpack``/``packsize`` when Lua 5.1 lacks them."""
    string_table = runtime.globals()["string"]
    if string_table["pack"] is not None and string_table["unpack"] is not None:
        return

    def pack(format: Any, *values: Any) -> bytes:
        return _pack(str(format), values)

    def packsize(format: Any) -> int:
        return _packsize(str(format))

    def unpack(format: Any, data: Any, position: Any = 1) -> tuple:
        values, next_position = _unpack(
            str(format), _to_bytes(data), int(position) if position is not None else 1
        )
        return (*values, next_position)

    globals_table = runtime.globals()
    globals_table["__protez_string_pack"] = pack
    globals_table["__protez_string_unpack"] = unpack
    globals_table["__protez_string_packsize"] = packsize
    runtime.execute(_WRAPPERS.encode("ascii"))
