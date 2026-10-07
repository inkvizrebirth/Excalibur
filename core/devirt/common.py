"""Shared plumbing for Protez's own devirtualizers.

Every family below ends up at the same two questions:

* *is there a Lua 5.1 chunk in here?* -- the byte containers (numeric arrays,
  ``string.char`` calls, escape runs, hex/base64 blobs) and the runtime tables
  the loader builds all hold the same bytes, only spelled differently;
* *what does the recovered chunk say?* -- which is ``core.lua51``'s job.

The container decoders live in ``core.families`` and are already covered by
tests; they are imported lazily here so ``core.devirt`` and ``core.families``
can depend on each other without an import cycle.
"""

from __future__ import annotations

import re
import struct
from typing import Any, Iterable, Sequence

from core.lua51 import (
    LUA51_SIGNATURE,
    BytecodeError,
    Chunk,
    decompile,
    disassemble,
    read_chunk,
)

__all__ = [
    "MIN_CHUNK_BYTES",
    "lua51_slice",
    "find_lua51_chunk",
    "chunk_score",
    "numbers_to_bytes",
    "chunk_from_values",
    "chunk_from_strings",
    "static_byte_containers",
    "static_source_containers",
    "lua_string_value",
    "string_runs",
    "pool_source",
    "safe_decompile",
    "safe_disassemble",
    "describe_chunk",
]

MIN_CHUNK_BYTES = 64
MAX_STATIC_CONTAINERS = 24
_TRAILING_TRIM = (0, 1, 2, 3, 5, 7, 11)


def lua51_slice(data: bytes) -> bytes | None:
    """Return ``data`` starting at the first Lua 5.1 signature, or ``None``."""
    index = bytes(data).find(LUA51_SIGNATURE)
    if index < 0 or len(data) - index < MIN_CHUNK_BYTES:
        return None
    return bytes(data)[index:]


def find_lua51_chunk(data: bytes | str) -> bytes | None:
    """Find and validate a Lua 5.1 chunk anywhere inside ``data``.

    Trailing junk is harmless for the reader, but some loaders glue a counter
    or a checksum right behind the chunk; when the full slice does not parse we
    retry with a few trailing bytes trimmed off.
    """
    if isinstance(data, str):
        data = data.encode("latin-1", "ignore")
    sliced = lua51_slice(data)
    if sliced is None:
        return None
    for trim in _TRAILING_TRIM:
        candidate = sliced if trim == 0 else sliced[: len(sliced) - trim]
        if len(candidate) < MIN_CHUNK_BYTES:
            break
        try:
            read_chunk(candidate)
        except BytecodeError:
            continue
        except Exception:  # noqa: BLE001 - a malformed container must never abort a run
            continue
        return candidate
    return None


def chunk_score(chunk: Chunk) -> int:
    """How much real code a parsed chunk carries (used to pick between candidates)."""
    total = 0
    for proto in chunk.protos():
        total += 1 + len(proto.code) // 4
    return total


def numbers_to_bytes(values: Sequence[Any]) -> list[bytes]:
    """Pack a numeric table into byte strings, one candidate per plausible layout.

    Byte tables are the norm (``{27, 76, 117, 97, ...}``), but the same payload
    shows up as 1-based codes, as 16-bit words and as 32-bit instruction words,
    in either endianness, so every layout is offered and the caller validates.
    """
    integers: list[int] = []
    for value in values:
        if isinstance(value, bool):
            integers.append(int(value))
        elif isinstance(value, int):
            integers.append(value)
        elif isinstance(value, float) and value.is_integer():
            integers.append(int(value))
        else:
            return []
    if not integers:
        return []
    candidates: list[bytes] = []
    if any(value == 0 for value in integers) or max(integers) <= 255:
        # A normal byte table, or one whose zeroes were folded away: the
        # identity packing is always worth a try when the range allows it.
        candidates.append(bytes(value & 0xFF for value in integers))
    if all(1 <= value <= 256 for value in integers):
        # Lua's own ``string.byte`` is 1-based in some packers, and a chunk with
        # no zero byte gives no other hint that the codes are shifted.
        candidates.append(bytes((value - 1) & 0xFF for value in integers))
    maximum = max(abs(value) for value in integers)
    if maximum > 255 and maximum < 65536:
        candidates.append(b"".join(struct.pack("<H", value & 0xFFFF) for value in integers))
        candidates.append(b"".join(struct.pack(">H", value & 0xFFFF) for value in integers))
    if maximum >= 256:
        candidates.append(b"".join(struct.pack("<I", value & 0xFFFFFFFF) for value in integers))
        candidates.append(b"".join(struct.pack(">I", value & 0xFFFFFFFF) for value in integers))
    unique: list[bytes] = []
    for candidate in candidates:
        if candidate not in unique:
            unique.append(candidate)
    return unique


def chunk_from_values(values: Sequence[Any]) -> bytes | None:
    """Best Lua 5.1 chunk hidden in a numeric table, or ``None``."""
    best: tuple[int, bytes] | None = None
    for candidate in numbers_to_bytes(values):
        chunk = find_lua51_chunk(candidate)
        if chunk is None:
            continue
        try:
            score = chunk_score(read_chunk(chunk))
        except Exception:  # noqa: BLE001
            continue
        if best is None or score > best[0]:
            best = (score, chunk)
    return best[1] if best else None


def chunk_from_strings(values: Iterable[Any]) -> bytes | None:
    """Bytecode assembled from single-character or numeric strings.

    A VM that keeps its program in a *string* table builds ``table.concat``
    output elsewhere; when the snapshot holds the pieces themselves this is the
    same payload one ``concat`` away.
    """
    pieces = [value for value in values if isinstance(value, str)]
    if not pieces:
        return None
    joined = "".join(pieces)
    if LUA51_SIGNATURE in joined.encode("latin-1", "ignore"):
        return find_lua51_chunk(joined.encode("latin-1", "ignore"))
    if all(re.fullmatch(r"\d{1,3}", piece) for piece in pieces):
        return find_lua51_chunk(bytes(int(piece) & 0xFF for piece in pieces))
    return None


def static_byte_containers(text: str) -> list[bytes]:
    """Every byte container a loader may hide its chunk in."""
    from core.families import (  # lazy: families imports core.devirt
        _decode_char_calls,
        _decode_escape_runs,
        _decode_number_arrays,
        _decode_text_layers,
    )

    containers: list[bytes] = []

    def add(items: Iterable[bytes]) -> None:
        for item in items:
            if item and item not in containers and len(containers) < MAX_STATIC_CONTAINERS:
                containers.append(item)

    add(_decode_number_arrays(text))
    add(_decode_char_calls(text))
    add(_decode_escape_runs(text))
    add(_decode_text_layers(text))
    return containers


def static_source_containers(text: str) -> list[str]:
    """Lua source hidden in an array/escape/char-call blob inside a loader."""
    from core.families import scan_embedded_source  # lazy import (cycle)

    recovered = scan_embedded_source(text)
    return [recovered] if recovered else []


_STRING_CONCAT_RUN = re.compile(
    r"""(?:[ \t]*"(?:\\.|[^"\\])*"[ \t]*)(?:\.\.[ \t]*"(?:\\.|[^"\\])*"[ \t]*){3,}""",
    re.DOTALL,
)
_LUA_ESCAPES = {"n": 10, "t": 9, "r": 13, "a": 7, "b": 8, "f": 12, "v": 11, "\\": 92, '"': 34, "'": 39}


def lua_string_value(literal: str) -> bytes:
    """Decode one Lua/Luau string literal (quotes included) into bytes."""
    text = literal.strip()
    if len(text) >= 2 and text[0] in "\"'" and text[-1] == text[0]:
        text = text[1:-1]
    elif text.startswith("[") and "[" in text[1:]:
        opening = text.index("[")
        closing = text.index("]", opening)
        text = text[closing + 1 : -abs(closing - opening)]
    out = bytearray()
    index = 0
    while index < len(text):
        character = text[index]
        if character != "\\":
            out.extend(character.encode("utf-8", "surrogatepass"))
            index += 1
            continue
        index += 1
        if index >= len(text):
            break
        marker = text[index]
        if marker.isdigit():
            digits = ""
            while index < len(text) and text[index].isdigit() and len(digits) < 3:
                digits += text[index]
                index += 1
            out.append(int(digits) & 0xFF)
            continue
        if marker in ("x", "X") and index + 2 < len(text):
            try:
                out.append(int(text[index + 1 : index + 3], 16) & 0xFF)
                index += 3
                continue
            except ValueError:
                pass
        if marker == "z":
            index += 1
            while index < len(text) and text[index].isspace():
                index += 1
            continue
        out.append(_LUA_ESCAPES.get(marker, ord(marker) & 0xFF))
        index += 1
    return bytes(out)


def string_runs(text: str) -> list[bytes]:
    """Payloads hidden in ``"..." .. "..." .. "..."`` runs.

    Splitting an encrypted payload across many short literals joined with ``..``
    is the oldest trick in the book, and it defeats every single-literal pass.
    """
    payloads: list[bytes] = []
    for match in _STRING_CONCAT_RUN.finditer(text):
        pieces = [
            lua_string_value(literal)
            for literal in re.findall(r'"(?:\\.|[^"\\])*"', match.group(0), re.DOTALL)
        ]
        if not pieces:
            continue
        joined = b"".join(pieces)
        if joined and joined not in payloads:
            payloads.append(joined)
    return payloads


def pool_source(pool: Any) -> str | None:
    """Source that a VM's constant pool spells out word by word.

    VM obfuscators keep the payload's strings in the pool; when the payload is
    itself Lua source, the pool holds it as a run of pieces.
    """
    values = getattr(pool, "values", None)
    if not values:
        return None
    pieces = [value for value in values if isinstance(value, str) and value]
    if not pieces:
        return None
    joined = "\n".join(pieces)
    from core.executor_api import looks_like_lua_source  # lazy import (cycle)

    for candidate in (joined, "".join(pieces)):
        recovered = static_source_containers(candidate)
        if recovered:
            return recovered[0]
        if looks_like_lua_source(candidate):
            return candidate
    return None


def safe_decompile(bytecode: bytes) -> str | None:
    try:
        return decompile(bytes(bytecode))
    except BytecodeError:
        return None
    except Exception:  # noqa: BLE001 - a broken chunk is not a crash
        return None


def safe_disassemble(bytecode: bytes, *, limit: int = 400) -> str | None:
    try:
        chunk = read_chunk(bytes(bytecode))
    except Exception:  # noqa: BLE001
        return None
    try:
        return disassemble(chunk.root, limit=limit)
    except Exception:  # noqa: BLE001
        return None


def describe_chunk(bytecode: bytes) -> str:
    """One line about a chunk, for notes and report text."""
    try:
        chunk = read_chunk(bytes(bytecode))
    except Exception:  # noqa: BLE001
        return f"Lua 5.1 chunk ({len(bytecode)} bytes)"
    root = chunk.root
    return (
        f"Lua 5.1 chunk ({len(bytecode)} bytes, {chunk.proto_count} prototype(s), "
        f"{len(root.code) // 4} root instruction(s))"
    )
