"""Luraph devirtualizer.

Luraph v14/v15 compresses the payload into a long-bracket stream, ships its own
VM interpreter as a second stream, and interprets a private instruction format.
``core.luraph_static`` already unpacks the container; ``core.luraph_devirtualizer``
lifts the v15 format with the vendored analyser when it is installed.  What this
module adds is the middle ground: given the unpacked container it

* lifts the payload when it is a Lua 5.1 chunk after all,
* recovers source hidden in the decoded streams,
* names the VM's opcodes using the *interpreter's own* dispatcher (the VM source
  is right there, so opcode numbers stop being magic), and
* hands the annotated disassembly to ``core.devirt.table_vm`` otherwise.
"""

from __future__ import annotations

from typing import Any, Sequence

from core.devirt import bytecode_vm, table_vm
from core.devirt.common import (
    find_lua51_chunk,
    safe_decompile,
    static_source_containers,
)

__all__ = ["devirtualize", "unpack"]


def unpack(source: str) -> Any | None:
    """Unpack the Luraph container without executing it, if it is one."""
    try:
        from core.luraph_static import LuraphStaticError, unpack_luraph_static

        return unpack_luraph_static(source)
    except Exception:  # noqa: BLE001 - a container that will not unpack is not a crash
        return None


def devirtualize(
    source: str,
    *,
    vm_tables: Sequence[Any] | None = None,
    vm_analysis: Any | None = None,
    family: str = "luraph",
) -> dict[str, Any] | None:
    """Lift whatever the unpacked Luraph container exposes."""
    result = unpack(source)
    notes: list[str] = []
    if result is not None:
        notes.append(f"Luraph container unpacked statically (layout: {result.layout})")
        custom = bytes(getattr(result, "custom_bytecode", b"") or b"")
        if custom:
            chunk = find_lua51_chunk(custom)
            if chunk is not None:
                pseudocode = safe_decompile(chunk)
                if pseudocode:
                    notes.append(
                        "the custom stream was a Lua 5.1 chunk after all; it was lifted"
                    )
                    return {
                        "source": pseudocode,
                        "bytecode": chunk,
                        "method": "static container unpack + Lua 5.1 pseudo-source recovery",
                        "notes": tuple(notes),
                        "confidence": 0.85,
                        "partial": True,
                    }
            notes.append(
                f"the custom stream ({len(custom)} bytes) is Luraph's own format, not Lua bytecode"
            )
            for recovered in static_source_containers(
                custom.decode("latin-1", "ignore")
            ):
                notes.append("the custom stream carried Lua source; it was reassembled")
                return {
                    "source": recovered,
                    "bytecode": None,
                    "method": "static container unpack + hidden source reassembly",
                    "notes": tuple(notes),
                    "confidence": 0.75,
                    "partial": True,
                }

        vm_source = getattr(result, "vm_source", None)
        interpreter = ""
        if vm_source:
            interpreter = bytes(vm_source).decode("utf-8", "replace")
            if "function" in interpreter:
                notes.append(
                    "the unpacked VM interpreter is available, so opcode names come from "
                    "Luraph's own dispatcher"
                )
        surface = table_vm.devirtualize(
            interpreter or source,
            vm_tables=vm_tables,
            vm_analysis=vm_analysis,
            family=family,
        )
        if surface is not None:
            surface["notes"] = tuple(notes) + tuple(surface.get("notes", ()))
            surface["method"] = "static container unpack + " + str(surface["method"])
            # The interpreter is *not* the payload: it is only read for opcode
            # names, and the pipeline writes it to logs as its own artifact.
            return surface

    fallback = bytecode_vm.devirtualize(
        source, vm_tables=vm_tables, family=family
    )
    if fallback is None:
        return None
    if notes:
        fallback["notes"] = tuple(notes) + tuple(fallback.get("notes", ()))
    return fallback
