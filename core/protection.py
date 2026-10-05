from __future__ import annotations

import re
from dataclasses import dataclass

from core.deobfuscator import _decode_string, tokenize

_LURAPH_VERSION = re.compile(
    r"\bLuraph\s+Obfuscator\s+(?:v|version\s*)?([0-9]+(?:\.[0-9]+)*)\b",
    re.IGNORECASE,
)
_MAX_VISIBLE_LITERAL_BYTES = 256
_MAX_VISIBLE_LITERALS = 80


@dataclass(frozen=True)
class ProtectionProfile:
    family: str
    version: str | None
    embedded_payload_chars: int
    visible_literals: tuple[str, ...]

    @property
    def display_name(self) -> str:
        if self.version:
            return f"{self.family} v{self.version}"
        return self.family


def inspect_protection(source: str) -> ProtectionProfile | None:
    """Identify a known VM wrapper without evaluating or invoking its payload."""
    if not isinstance(source, str):
        raise TypeError("source must be text")

    if not _LURAPH_VERSION.search(source):
        return None

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
    if version_match is None:
        return None

    payload_chars = 0
    literals: list[str] = []
    seen: set[str] = set()
    for token in tokens:
        if token.kind != "string":
            continue
        if len(token.text) > 4096:
            if "LPH&" in token.text[:64]:
                payload_chars = max(payload_chars, len(token.text))
            continue
        raw = _decode_string(token)
        if raw is None or len(raw) > _MAX_VISIBLE_LITERAL_BYTES:
            continue
        try:
            value = raw.decode("utf-8")
        except UnicodeDecodeError:
            continue
        if "LPH&" in value[:64]:
            payload_chars = max(payload_chars, len(value))
            continue
        if len(value) < 3 or any(
            ord(character) < 32 and character not in "\t\r\n" for character in value
        ):
            continue
        if value not in seen:
            seen.add(value)
            literals.append(value)
            if len(literals) >= _MAX_VISIBLE_LITERALS:
                break

    # A short header literal may be below the large-string threshold.
    if not payload_chars:
        for token in tokens:
            if token.kind == "string" and "LPH&" in token.text[:64]:
                payload_chars = len(token.text)
                break

    return ProtectionProfile(
        family="Luraph Obfuscator",
        version=version_match.group(1),
        embedded_payload_chars=payload_chars,
        visible_literals=tuple(literals),
    )


__all__ = ["ProtectionProfile", "inspect_protection"]
