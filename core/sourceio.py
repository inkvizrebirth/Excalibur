"""Byte faithful source reading and writing.

Obfuscated Lua is *bytes*, not text: WRD string pools contain arbitrary binary
payloads.  Reading such a file with ``encoding="utf-8", errors="replace"`` would
silently corrupt those bytes, and writing the transformed result back with a
different encoding would corrupt them a second time.

Rules implemented here:

* decode as UTF-8 when the file really is UTF-8 (keeps non-ASCII identifiers
  readable), otherwise fall back to latin-1, which maps bytes 1:1 onto code
  points and therefore never loses information;
* always write back with the encoding the file was read with, so a
  read -> transform -> write round trip is byte exact when nothing changed.
"""

from __future__ import annotations

import codecs
from dataclasses import dataclass
from pathlib import Path

UTF8 = "utf-8"
LATIN1 = "latin-1"


@dataclass
class LuaSource:
    """A Lua source file with the encoding it was decoded with."""

    text: str
    encoding: str = UTF8
    path: Path | None = None

    @property
    def bytes(self) -> bytes:
        return self.text.encode(self.encoding, "replace")

    @property
    def byte_length(self) -> int:
        return len(self.bytes)

    def ascii_safe(self) -> bool:
        return all(ord(ch) < 128 for ch in self.text)


def decode_source(data: bytes) -> LuaSource:
    """Decode ``data`` choosing the encoding that preserves every byte."""
    try:
        text = data.decode(UTF8)
        if codecs.lookup(UTF8).name == UTF8:
            # A UTF-8 BOM is legal Lua but noise for the pipeline.
            if text.startswith("\ufeff"):
                text = text[1:]
            return LuaSource(text=text, encoding=UTF8)
    except UnicodeDecodeError:
        pass
    return LuaSource(text=data.decode(LATIN1), encoding=LATIN1)


def read_source(path: str | Path) -> LuaSource:
    """Read a Lua file byte faithfully."""
    file_path = Path(path)
    source = decode_source(file_path.read_bytes())
    source.path = file_path
    return source


def write_source(path: str | Path, source: LuaSource | str, encoding: str = UTF8) -> Path:
    """Write ``source`` back, preserving bytes when the encoding allows it."""
    file_path = Path(path)
    if isinstance(source, LuaSource):
        data = source.text.encode(source.encoding, "replace")
    else:
        data = source.encode(encoding, "replace")
    file_path.parent.mkdir(parents=True, exist_ok=True)
    file_path.write_bytes(data)
    return file_path


__all__ = ["LATIN1", "UTF8", "LuaSource", "decode_source", "read_source", "write_source"]
