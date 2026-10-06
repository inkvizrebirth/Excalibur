from __future__ import annotations

import io
import lzma
import re
import time
from dataclasses import dataclass
from typing import Sequence

from core.deobfuscator import MAX_SOURCE_BYTES, Token, tokenize

MAX_LURAPH_DECODED_BYTES = 64 * 1024 * 1024
MAX_LURAPH_DECOMPRESSION_SECONDS = 12.0
_MAX_STREAM_CANDIDATES = 3
_MAX_DECODE_CHUNK_BYTES = 1024 * 1024
_ZSTD_MAGIC = b"\x28\xb5\x2f\xfd"
_LONG_BRACKET_OPEN = re.compile(r"\[(=*)\[")


class LuraphStaticError(ValueError):
    """A Luraph container could not be safely classified or statically unpacked."""


@dataclass(frozen=True)
class LuraphContainerInfo:
    detected: bool
    layout: str
    long_string_count: int
    raw_stream_count: int
    valid_stream_count: int
    zstd_stream_count: int
    legacy_signature: bool


@dataclass(frozen=True)
class LuraphStaticUnpackResult:
    layout: str
    vm_source: bytes | None
    custom_bytecode: bytes
    compressed_stream_sizes: tuple[int, ...]
    decoded_stream_sizes: tuple[int, ...]


def _long_bracket_value(text: str) -> str | None:
    """Return a long-bracket string's Lua value, including newline semantics."""
    opening = _LONG_BRACKET_OPEN.match(text)
    if opening is None:
        return None
    closing = "]" + opening.group(1) + "]"
    if not text.endswith(closing):
        return None
    value = text[opening.end() : -len(closing)]
    if value.startswith("\r\n"):
        return value[2:]
    if value.startswith(("\n", "\r")):
        return value[1:]
    return value


def _long_bracket_payloads(
    source: str,
    tokens: Sequence[Token] | None = None,
) -> tuple[list[str], int, int]:
    if tokens is None:
        tokens = tokenize(source)
    values: list[str] = []
    long_string_count = 0
    raw_stream_count = 0
    for token in tokens:
        if token.kind != "string" or not token.text.startswith("["):
            continue
        value = _long_bracket_value(token.text)
        if value is None:
            continue
        long_string_count += 1
        if value.startswith("LPH"):
            raw_stream_count += 1
            if len(values) < _MAX_STREAM_CANDIDATES:
                values.append(value)
    return values, long_string_count, raw_stream_count


def _looks_like_stream(payload: str) -> bool:
    """Check only the LPH envelope and Ascii85 alphabet; do not decompress it."""
    if len(payload) < 9 or not payload.startswith("LPH"):
        return False
    body = payload[4:]
    if len(body) < 5:
        return False
    for character in body:
        codepoint = ord(character)
        if character != "z" and not 33 <= codepoint <= 117:
            return False
    return True


def decode_luraph_base85(
    payload: str,
    *,
    max_output_bytes: int = MAX_LURAPH_DECODED_BYTES,
    max_groups: int | None = None,
) -> bytes:
    """Decode Luraph's little-endian 32-bit Ascii85 stream without evaluation."""
    if not isinstance(payload, str):
        raise TypeError("payload must be text")
    if len(payload) > MAX_SOURCE_BYTES:
        raise LuraphStaticError("LPH Ascii85 payload exceeds the static-analysis input limit")
    if not payload.startswith("LPH") or len(payload) < 9:
        raise LuraphStaticError("not a complete LPH Ascii85 stream")
    if max_output_bytes <= 0:
        raise ValueError("max_output_bytes must be positive")
    if max_output_bytes > MAX_LURAPH_DECODED_BYTES:
        raise ValueError(
            f"max_output_bytes cannot exceed {MAX_LURAPH_DECODED_BYTES:,} bytes"
        )
    if max_groups is not None and max_groups <= 0:
        raise ValueError("max_groups must be positive when provided")

    # The four-byte LPH/version header is stripped by the original loader.
    body = payload[4:]
    digits: list[int] = []
    output = bytearray()
    groups = 0

    for character in body:
        if character == "z":
            digits.extend((0, 0, 0, 0, 0))
        else:
            codepoint = ord(character)
            if not 33 <= codepoint <= 117:
                raise LuraphStaticError("invalid character in LPH Ascii85 stream")
            digits.append(codepoint - 33)

        while len(digits) >= 5:
            value = 0
            for digit in digits[:5]:
                value = value * 85 + digit
            del digits[:5]
            if len(output) + 4 > max_output_bytes:
                raise LuraphStaticError(
                    f"decoded LPH stream exceeds the {max_output_bytes:,}-byte safety limit"
                )
            output.extend((value & 0xFFFFFFFF).to_bytes(4, "little"))
            groups += 1
            if max_groups is not None and groups >= max_groups:
                return bytes(output)

    # As in Luraph's loader, any incomplete final Ascii85 group is ignored.
    return bytes(output)


def _stream_has_zstd_magic(payload: str) -> bool:
    try:
        return decode_luraph_base85(payload, max_output_bytes=4, max_groups=1).startswith(
            _ZSTD_MAGIC
        )
    except (LuraphStaticError, ValueError):
        return False


def inspect_luraph_container(
    source: str,
    *,
    tokens: Sequence[Token] | None = None,
) -> LuraphContainerInfo:
    """Classify known Luraph container shapes using static string inspection only."""
    payloads, long_string_count, raw_stream_count = _long_bracket_payloads(source, tokens)
    valid = [payload for payload in payloads if _looks_like_stream(payload)]
    zstd_flags = [_stream_has_zstd_magic(payload) for payload in valid]
    zstd_stream_count = sum(zstd_flags)
    legacy_signature = "52200625" in source and "614125" in source

    if len(valid) > 2:
        layout = "ambiguous-multi-stream"
    elif len(valid) == 2:
        if all(zstd_flags):
            layout = "two-stream-zstandard"
        elif any(zstd_flags):
            layout = "mixed-two-stream"
        else:
            layout = "two-stream-range"
    elif len(valid) == 1 and zstd_flags[0]:
        layout = "single-stream-zstandard"
    elif len(valid) == 1 and "DecompressBuffer" in source:
        layout = "single-stream-unknown-compression"
    elif raw_stream_count:
        layout = "unsupported-lph-stream"
    else:
        layout = "no-luraph-container"

    detected = (
        len(valid) >= 2
        or (len(valid) == 1 and (zstd_stream_count == 1 or "DecompressBuffer" in source))
        or (legacy_signature and raw_stream_count >= 2)
    )
    return LuraphContainerInfo(
        detected=detected,
        layout=layout,
        long_string_count=long_string_count,
        raw_stream_count=raw_stream_count,
        valid_stream_count=len(valid),
        zstd_stream_count=zstd_stream_count,
        legacy_signature=legacy_signature,
    )


def _zstd_frame_length(data: bytes) -> int:
    """Read a single standard Zstandard frame's boundary without decompressing it."""
    if len(data) < 5 or not data.startswith(_ZSTD_MAGIC):
        raise LuraphStaticError("Zstandard frame magic was not found")

    cursor = 4
    descriptor = data[cursor]
    cursor += 1
    if descriptor & 0x18:
        raise LuraphStaticError("Zstandard frame uses a reserved or unused descriptor bit")

    content_size_flag = descriptor >> 6
    single_segment = bool(descriptor & 0x20)
    has_checksum = bool(descriptor & 0x04)
    dictionary_flag = descriptor & 0x03

    if not single_segment:
        if cursor >= len(data):
            raise LuraphStaticError("truncated Zstandard window descriptor")
        cursor += 1

    dictionary_size = (0, 1, 2, 4)[dictionary_flag]
    content_size = (1 if single_segment else 0, 2, 4, 8)[content_size_flag]
    header_tail = dictionary_size + content_size
    if cursor + header_tail > len(data):
        raise LuraphStaticError("truncated Zstandard frame header")
    cursor += header_tail

    while True:
        if cursor + 3 > len(data):
            raise LuraphStaticError("truncated Zstandard block header")
        block_header = int.from_bytes(data[cursor : cursor + 3], "little")
        cursor += 3
        last_block = bool(block_header & 1)
        block_type = (block_header >> 1) & 0x03
        block_size = block_header >> 3
        if block_type == 3:
            raise LuraphStaticError("Zstandard frame uses a reserved block type")
        stored_size = 1 if block_type == 1 else block_size
        if cursor + stored_size > len(data):
            raise LuraphStaticError("truncated Zstandard block content")
        cursor += stored_size
        if last_block:
            break

    if has_checksum:
        if cursor + 4 > len(data):
            raise LuraphStaticError("truncated Zstandard content checksum")
        cursor += 4
    return cursor


def _trim_ascii85_padding(data: bytes) -> bytes:
    frame_length = _zstd_frame_length(data)
    trailing = data[frame_length:]
    if len(trailing) > 3 or any(trailing):
        raise LuraphStaticError(
            "unexpected trailing data after the Luraph Zstandard frame"
        )
    return data[:frame_length]


def _decompress_zstd(data: bytes, *, max_output_bytes: int, deadline: float) -> bytes:
    try:
        import zstandard
    except ImportError as exc:
        raise LuraphStaticError(
            "Zstandard support is unavailable; install Protez's bundled zstandard runtime"
        ) from exc

    output = bytearray()
    try:
        decompressor = zstandard.ZstdDecompressor(
            max_window_size=max(1024, max_output_bytes // 1024)
        )
        with decompressor.stream_reader(io.BytesIO(data)) as reader:
            while True:
                if time.monotonic() > deadline:
                    raise LuraphStaticError(
                        "Luraph static decompression exceeded its time budget"
                    )
                chunk = reader.read(_MAX_DECODE_CHUNK_BYTES)
                if not chunk:
                    break
                if len(output) + len(chunk) > max_output_bytes:
                    raise LuraphStaticError(
                        f"decoded Luraph data exceeds the {max_output_bytes:,}-byte safety limit"
                    )
                output.extend(chunk)
    except LuraphStaticError:
        raise
    except zstandard.ZstdError as exc:
        raise LuraphStaticError(f"invalid Luraph Zstandard stream: {exc}") from exc
    return bytes(output)


def _decompress_legacy_range(
    data: bytes,
    *,
    max_output_bytes: int,
    deadline: float,
) -> bytes:
    """Decode the legacy v14-style range/LZ stream as raw LZMA1 data."""
    filters = [
        {
            "id": lzma.FILTER_LZMA1,
            "dict_size": max(4096, max_output_bytes),
            "lc": 3,
            "lp": 0,
            "pb": 0,
        }
    ]
    try:
        decoder = lzma.LZMADecompressor(format=lzma.FORMAT_RAW, filters=filters)
    except (lzma.LZMAError, ValueError, MemoryError) as exc:
        raise LuraphStaticError(f"could not initialise the legacy Luraph decoder: {exc}") from exc

    output = bytearray()
    offset = 0
    idle_rounds = 0
    while True:
        if time.monotonic() > deadline:
            raise LuraphStaticError("Luraph static decompression exceeded its time budget")
        if decoder.needs_input:
            if offset >= len(data):
                raise LuraphStaticError("legacy Luraph range stream ended before its terminator")
            chunk_in = data[offset : offset + 64 * 1024]
            offset += len(chunk_in)
        else:
            chunk_in = b""

        remaining_plus_one = max_output_bytes - len(output) + 1
        if remaining_plus_one <= 0:
            raise LuraphStaticError(
                f"decoded Luraph data exceeds the {max_output_bytes:,}-byte safety limit"
            )
        try:
            chunk_out = decoder.decompress(
                chunk_in,
                max_length=min(_MAX_DECODE_CHUNK_BYTES, remaining_plus_one),
            )
        except (lzma.LZMAError, EOFError, ValueError) as exc:
            raise LuraphStaticError(f"invalid legacy Luraph range stream: {exc}") from exc

        if chunk_out:
            output.extend(chunk_out)
        if len(output) > max_output_bytes:
            raise LuraphStaticError(
                f"decoded Luraph data exceeds the {max_output_bytes:,}-byte safety limit"
            )
        if chunk_out or decoder.needs_input:
            idle_rounds = 0
        else:
            idle_rounds += 1
            if idle_rounds > 4:
                raise LuraphStaticError("legacy Luraph decoder made no progress")
        if decoder.eof:
            trailing = decoder.unused_data + data[offset:]
            if len(trailing) > 3 or any(trailing):
                raise LuraphStaticError("unexpected trailing data after the legacy Luraph stream")
            return bytes(output)
        if decoder.needs_input and offset >= len(data):
            raise LuraphStaticError("legacy Luraph range stream ended before its terminator")


def _looks_like_vm_source(data: bytes) -> bool:
    if not data:
        return False
    printable = sum(byte in (9, 10, 13) or 32 <= byte < 127 for byte in data)
    if printable / len(data) < 0.80:
        return False
    try:
        text = data.decode("utf-8")
    except UnicodeDecodeError:
        return False
    return "function" in text and ("return" in text or "while" in text)


def unpack_luraph_static(
    source: str,
    *,
    max_output_bytes: int = MAX_LURAPH_DECODED_BYTES,
    timeout_seconds: float = MAX_LURAPH_DECOMPRESSION_SECONDS,
) -> LuraphStaticUnpackResult:
    """Statically unpack a recognized Luraph container; never execute its code."""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    if len(source) > MAX_SOURCE_BYTES:
        raise LuraphStaticError(
            f"Luraph source exceeds the {MAX_SOURCE_BYTES // (1024 * 1024)} MiB analysis limit"
        )
    source_bytes = len(source.encode("utf-8", errors="surrogatepass"))
    if source_bytes > MAX_SOURCE_BYTES:
        raise LuraphStaticError(
            f"Luraph source exceeds the {MAX_SOURCE_BYTES // (1024 * 1024)} MiB analysis limit"
        )
    if max_output_bytes <= 0 or max_output_bytes > MAX_LURAPH_DECODED_BYTES:
        raise ValueError(
            f"max_output_bytes must be between 1 and {MAX_LURAPH_DECODED_BYTES:,}"
        )
    if timeout_seconds <= 0:
        raise ValueError("timeout_seconds must be positive")

    payloads, _, raw_stream_count = _long_bracket_payloads(source)
    if raw_stream_count > _MAX_STREAM_CANDIDATES:
        raise LuraphStaticError("ambiguous Luraph container: too many encoded stream candidates")
    valid = [payload for payload in payloads if _looks_like_stream(payload)]
    if len(valid) > 2:
        raise LuraphStaticError("ambiguous Luraph container: more than two encoded streams")
    if not valid:
        raise LuraphStaticError("no valid LPH Ascii85 streams were found")

    deadline = time.monotonic() + min(timeout_seconds, 60.0)
    coded = [
        decode_luraph_base85(payload, max_output_bytes=max_output_bytes)
        for payload in valid
    ]
    zstd_flags = [stream.startswith(_ZSTD_MAGIC) for stream in coded]
    compressed_sizes = tuple(len(stream) for stream in coded)

    if len(coded) == 1:
        if not zstd_flags[0]:
            raise LuraphStaticError(
                "a single Luraph stream was found, but its compression layout is unsupported"
            )
        compressed = _trim_ascii85_padding(coded[0])
        bytecode = _decompress_zstd(
            compressed,
            max_output_bytes=max_output_bytes,
            deadline=deadline,
        )
        if not bytecode:
            raise LuraphStaticError("Luraph Zstandard stream decoded to empty bytecode")
        return LuraphStaticUnpackResult(
            layout="single-stream-zstandard",
            vm_source=None,
            custom_bytecode=bytecode,
            compressed_stream_sizes=compressed_sizes,
            decoded_stream_sizes=(len(bytecode),),
        )

    if all(zstd_flags):
        compressed_streams = tuple(_trim_ascii85_padding(stream) for stream in coded)
        decoded = tuple(
            _decompress_zstd(
                stream,
                max_output_bytes=max_output_bytes,
                deadline=deadline,
            )
            for stream in compressed_streams
        )
        codec = "zstandard"
    elif any(zstd_flags):
        raise LuraphStaticError("mixed Luraph compression formats are not supported")
    else:
        decoded = tuple(
            _decompress_legacy_range(
                stream,
                max_output_bytes=max_output_bytes,
                deadline=deadline,
            )
            for stream in coded
        )
        codec = "range"

    first_is_vm = _looks_like_vm_source(decoded[0])
    second_is_vm = _looks_like_vm_source(decoded[1])
    if first_is_vm == second_is_vm:
        raise LuraphStaticError(
            "could not safely identify exactly one VM-interpreter stream in the Luraph container"
        )
    vm_source, custom_bytecode = (
        (decoded[0], decoded[1]) if first_is_vm else (decoded[1], decoded[0])
    )
    if not custom_bytecode:
        raise LuraphStaticError("Luraph container decoded to an empty custom-bytecode stream")
    return LuraphStaticUnpackResult(
        layout=f"two-stream-{codec}",
        vm_source=vm_source,
        custom_bytecode=custom_bytecode,
        compressed_stream_sizes=compressed_sizes,
        decoded_stream_sizes=tuple(len(item) for item in decoded),
    )


__all__ = [
    "LuraphContainerInfo",
    "LuraphStaticError",
    "LuraphStaticUnpackResult",
    "MAX_LURAPH_DECODED_BYTES",
    "MAX_LURAPH_DECOMPRESSION_SECONDS",
    "decode_luraph_base85",
    "inspect_luraph_container",
    "unpack_luraph_static",
]
