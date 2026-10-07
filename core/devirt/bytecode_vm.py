"""Bytecode-VM devirtualizer.

The largest group of Roblox obfuscators -- WeAreDevs v2.4, IronBrew2/3, PSU
v1.0, Nexus v2.0, AztupBrew, MoonSec V2 and friends -- does not interpret the
user script directly.  They compile it to Lua 5.1 bytecode, pack the chunk into
a table or a string, and then run a *bytecode* "VM" over it.  The VM does not
need to be understood at all: recover the chunk and ``core.lua51``'s lifter has
the whole payload.

Two doors lead to the same chunk:

* **static** -- the loader text still holds the container (numeric array,
  ``string.char`` call, escape run, base64/hex blob);
* **runtime** -- the loader decoded the chunk into a table while it ran under
  the portable backend, and ``core.vm_dump`` snapshotted that table.  This is
  the door that opens when the container is built by arithmetic the static
  passes cannot follow.

The module tries both and reports which one produced the chunk.
"""

from __future__ import annotations

from typing import Any, Iterable, Sequence

from core.devirt.common import (
    chunk_from_strings,
    chunk_from_values,
    describe_chunk,
    find_lua51_chunk,
    safe_decompile,
    static_byte_containers,
    static_source_containers,
)

__all__ = ["devirtualize", "candidates_from_tables", "lift_tables"]

METHOD_STATIC = "static container extraction"
METHOD_RUNTIME = "runtime table reconstruction"


def _snapshot_values(snapshots: Iterable[Any]) -> list[tuple[str, Sequence[Any]]]:
    """``(label, raw values)`` for every snapshot that could carry a chunk."""
    collected: list[tuple[str, Sequence[Any]]] = []
    for snapshot in snapshots:
        values = getattr(snapshot, "values", None)
        label = getattr(snapshot, "label", "?")
        kind = getattr(snapshot, "kind", "")
        if not values:
            continue
        if kind == "numbers" or all(isinstance(value, (int, float)) for value in values):
            collected.append((str(label), tuple(values)))
        elif kind == "strings":
            collected.append((str(label), tuple(values)))
    return collected


def candidates_from_tables(snapshots: Sequence[Any]) -> list[tuple[str, bytes]]:
    """Every Lua 5.1 chunk the runtime tables of a loader contain."""
    found: list[tuple[str, bytes]] = []
    for label, values in _snapshot_values(snapshots):
        chunk = chunk_from_values(values) or chunk_from_strings(values)
        if chunk is None:
            continue
        if all(chunk != existing for _, existing in found):
            found.append((label, chunk))
    return found


def lift_tables(snapshots: Sequence[Any]) -> list[tuple[str, bytes, str]]:
    """``(label, bytecode, pseudocode)`` for each chunk found in the tables."""
    lifted: list[tuple[str, bytes, str]] = []
    for label, chunk in candidates_from_tables(snapshots):
        source = safe_decompile(chunk)
        if source:
            lifted.append((label, chunk, source))
    return lifted


def devirtualize(
    source: str,
    *,
    vm_tables: Sequence[Any] | None = None,
    captured_source: str | None = None,
    family: str = "generic",
) -> dict[str, Any] | None:
    """Recover the chunk behind a bytecode VM.

    Returns a mapping with ``source``/``bytecode``/``method``/``notes``/
    ``confidence``/``partial`` or ``None`` when this family is not a bytecode
    VM after all.
    """
    if captured_source:
        captured_chunk = find_lua51_chunk(captured_source)
        if captured_chunk is not None:
            pseudocode = safe_decompile(captured_chunk)
            if pseudocode:
                return {
                    "source": pseudocode,
                    "bytecode": captured_chunk,
                    "method": "runtime capture + Lua 5.1 pseudo-source recovery",
                    "notes": (
                        "the loader handed a bytecode chunk to loadstring and Protez captured it",
                        "register names and comments cannot be restored from stripped bytecode",
                    ),
                    "confidence": 0.85,
                    "partial": False,
                }
        recovered = static_source_containers(captured_source)
        if recovered:
            return {
                "source": recovered[0],
                "bytecode": None,
                "method": "runtime capture",
                "notes": ("the loader handed Lua source to loadstring and Protez captured it",),
                "confidence": 0.8,
                "partial": False,
            }

    # Runtime door first: a table the loader filled is the most reliable copy.
    for label, chunk, pseudocode in lift_tables(vm_tables or ()):
        return {
            "source": pseudocode,
            "bytecode": chunk,
            "method": f"{METHOD_RUNTIME} + Lua 5.1 pseudo-source recovery",
            "notes": (
                f"rebuilt the chunk from the table {label!r} the loader built at runtime "
                f"({describe_chunk(chunk)})",
                "register names and comments cannot be restored from stripped bytecode",
            ),
            "confidence": 0.9,
            "partial": False,
        }

    # Static door: containers still visible in the text.
    for candidate in static_byte_containers(source):
        chunk = find_lua51_chunk(candidate)
        if chunk is None:
            continue
        pseudocode = safe_decompile(chunk)
        if not pseudocode:
            continue
        return {
            "source": pseudocode,
            "bytecode": chunk,
            "method": f"{METHOD_STATIC} + Lua 5.1 pseudo-source recovery",
            "notes": (
                f"decoded {describe_chunk(chunk)} from a container in the loader",
                "register names and comments cannot be restored from stripped bytecode",
            ),
            "confidence": 0.8,
            "partial": True,
        }

    for recovered in static_source_containers(source):
        return {
            "source": recovered,
            "bytecode": None,
            "method": f"{METHOD_STATIC} (source, not bytecode)",
            "notes": ("the container held Lua source rather than a bytecode chunk",),
            "confidence": 0.7,
            "partial": True,
        }
    return None
