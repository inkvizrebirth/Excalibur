from __future__ import annotations

import re
from dataclasses import dataclass

from core.deobfuscator import _decode_string, tokenize
from core.luraph_static import inspect_luraph_container

_LURAPH_VERSION = re.compile(
    r"\bLuraph(?:\s+Obfuscator)?\s+(?:v|version\s*)?([0-9]+(?:\.[0-9]+)*)\b",
    re.IGNORECASE,
)
_MOONSEC_V3_MARKER = re.compile(r"\bMoonSec\s*V?\s*3\b|\bMoonSecV3\b", re.IGNORECASE)
_LONG_BRACKET_OPEN = re.compile(r"\[(=*)\[")
_MAX_VISIBLE_LITERAL_BYTES = 256
_MAX_VISIBLE_LITERALS = 80


@dataclass(frozen=True)
class ProtectionProfile:
    family: str
    version: str | None
    embedded_payload_chars: int
    visible_literals: tuple[str, ...]
    container_layout: str | None = None
    raw_payload_streams: int = 0
    valid_payload_streams: int = 0

    @property
    def display_name(self) -> str:
        if self.version:
            return f"{self.family} v{self.version}"
        return self.family


def _starts_lph_literal(token_text: str) -> bool:
    if token_text.startswith("["):
        opening = _LONG_BRACKET_OPEN.match(token_text)
        if opening is None:
            return False
        offset = opening.end()
        if token_text.startswith("\r\n", offset):
            offset += 2
        elif token_text.startswith(("\n", "\r"), offset):
            offset += 1
        return token_text.startswith("LPH", offset)
    return len(token_text) > 1 and token_text[0] in "\"'" and token_text.startswith("LPH", 1)


def inspect_protection(source: str) -> ProtectionProfile | None:
    """Identify a known VM wrapper by comments/container signatures only.

    This function performs lexical inspection. It does not evaluate the wrapper,
    its embedded virtual machine, or the virtual bytecode.
    """
    if not isinstance(source, str):
        raise TypeError("source must be text")

    tokens = tokenize(source)
    version_match = next(
        (
            match
            for token in tokens
            if token.kind == "comment"
            for match in [_LURAPH_VERSION.search(token.text)]
            if match is not None
        ),
        None,
    )
    container_info = inspect_luraph_container(source, tokens=tokens)
    moonsec_marker = next(
        (
            token
            for token in tokens
            if token.kind in {"comment", "string"}
            and _MOONSEC_V3_MARKER.search(token.text) is not None
        ),
        None,
    )
    if version_match is None and not container_info.detected and moonsec_marker is None:
        return None

    payload_chars = 0
    literals: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token.kind != "string":
            continue
        if _starts_lph_literal(token.text):
            payload_chars += len(token.text)
            continue
        if len(token.text) > 4096 or len(literals) >= _MAX_VISIBLE_LITERALS:
            continue
        raw = _decode_string(token)
        if raw is None or len(raw) > _MAX_VISIBLE_LITERAL_BYTES:
            continue
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if len(value) < 3 or any(
            ord(character) < 32 and character not in "\t\r\n" for character in value
        ):
            continue
        if value not in seen and len(literals) < _MAX_VISIBLE_LITERALS:
            seen.add(value)
            literals.append(value)

    return ProtectionProfile(
        family=(
            "Luraph Obfuscator"
            if version_match is not None or container_info.detected
            else "MoonSec"
        ),
        version=(
            version_match.group(1)
            if version_match is not None
            else "3" if moonsec_marker is not None else None
        ),
        embedded_payload_chars=payload_chars,
        visible_literals=tuple(literals),
        container_layout=container_info.layout,
        raw_payload_streams=container_info.raw_stream_count,
        valid_payload_streams=container_info.valid_stream_count,
    )


__all__ = ["ProtectionProfile", "inspect_protection"]
