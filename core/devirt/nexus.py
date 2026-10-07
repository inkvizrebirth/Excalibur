"""Nexus Obfuscator devirtualizer.

Nexus v2.0 keeps the payload as a Lua 5.1 chunk but never writes it down as a
plain array: the bytes are spread over dozens of short literals joined with
``..`` (and often spelled as ``\\ddd`` escapes), so a pass that only looks at
single strings or numeric tables sees nothing.  This module concatenates those
runs first, then reuses the bytecode-VM devirtualizer -- the same chunk, one
assembly step earlier.
"""

from __future__ import annotations

from typing import Any, Sequence

from core.devirt import bytecode_vm
from core.devirt.common import find_lua51_chunk, safe_decompile, string_runs

__all__ = ["devirtualize"]


def devirtualize(
    source: str,
    *,
    vm_tables: Sequence[Any] | None = None,
    vm_analysis: Any | None = None,
    family: str = "nexus",
) -> dict[str, Any] | None:
    """Recover a Nexus-style payload from concatenated string runs, then tables."""
    for payload in string_runs(source):
        chunk = find_lua51_chunk(payload)
        if chunk is None:
            continue
        pseudocode = safe_decompile(chunk)
        if not pseudocode:
            continue
        return {
            "source": pseudocode,
            "bytecode": chunk,
            "method": "concatenated-literal reassembly + Lua 5.1 pseudo-source recovery",
            "notes": (
                "the payload was split across string literals joined with `..`; "
                "Protez reassembled them before decoding",
                "register names and comments cannot be restored from stripped bytecode",
            ),
            "confidence": 0.8,
            "partial": True,
        }
    return bytecode_vm.devirtualize(
        source,
        vm_tables=vm_tables,
        captured_source=None,
        family=family,
    )
