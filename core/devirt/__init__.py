"""Protez's own devirtualizers, one recovery method per obfuscator family.

No open-source lifter could be vendored for the families Protez targets (the
build sandbox has no access to code hosting), so the recovery methods are
implemented here instead of being guessed at:

======================  =====================================================
family                  method
======================  =====================================================
Luraph v14/v15          static container unpack, then VM introspection with
                        opcode names read from Luraph's own interpreter
MoonSec V2/V3           bytecode-VM recovery (static container or runtime
                        table), plus the vendored v3 tool in the pipeline
WeAreDevs v2.4 / WRD    static string-pool recovery (permuted-base64 pool,
                        triple-reversal shuffle, alphabet map), then
                        bytecode-VM recovery
IronBrew 2/3            bytecode-VM recovery
PSU v1.0                bytecode-VM recovery
Nexus v2.0              concatenated-literal reassembly, then bytecode-VM
Prometheus              control-flow flattening removal (state-machine
                        dispatcher traced and re-ordered into straight code)
Wynfuscate v5           table-VM introspection with annotated disassembly
Xen / Synapse / Hyperion  table-VM introspection
Luau VM                 table-VM introspection
generic                 bytecode-VM, then table-VM
======================  =====================================================

Every strategy is a plain function ``devirtualize(source, *, vm_tables,
vm_analysis, family)`` returning a mapping or ``None``; nothing here raises out
of a run, and a strategy that cannot do more than describe a VM says so in its
notes rather than inventing source.
"""

from __future__ import annotations

import importlib
import logging
from dataclasses import dataclass, field
from typing import Any, Sequence

__all__ = [
    "DevirtResult",
    "devirtualize",
    "available_families",
    "report_table",
]

# family key -> strategies in the order they should be tried
_STRATEGIES: dict[str, tuple[tuple[str, str], ...]] = {
    "luraph": (("core.devirt.luraph", "devirtualize"),),
    "moonsec": (("core.devirt.bytecode_vm", "devirtualize"),),
    "wearedevs": (
        ("core.devirt.wrd", "devirtualize"),
        ("core.devirt.bytecode_vm", "devirtualize"),
    ),
    "ironbrew": (("core.devirt.bytecode_vm", "devirtualize"),),
    "psu": (("core.devirt.bytecode_vm", "devirtualize"),),
    "aztup": (("core.devirt.bytecode_vm", "devirtualize"),),
    "nexus": (("core.devirt.nexus", "devirtualize"),),
    "prometheus": (("core.devirt.prometheus", "devirtualize"),),
    "wynfuscate": (("core.devirt.table_vm", "devirtualize"),),
    "xen": (("core.devirt.table_vm", "devirtualize"),),
    "synapse-protected": (("core.devirt.table_vm", "devirtualize"),),
    "hyperion": (("core.devirt.table_vm", "devirtualize"),),
    "luau-vm": (("core.devirt.table_vm", "devirtualize"),),
    "generic-vm": (
        ("core.devirt.bytecode_vm", "devirtualize"),
        ("core.devirt.table_vm", "devirtualize"),
        ("core.devirt.prometheus", "devirtualize"),
    ),
    "generic": (
        ("core.devirt.bytecode_vm", "devirtualize"),
        ("core.devirt.table_vm", "devirtualize"),
        ("core.devirt.prometheus", "devirtualize"),
    ),
}
_FALLBACK = (
    ("core.devirt.bytecode_vm", "devirtualize"),
    ("core.devirt.table_vm", "devirtualize"),
    ("core.devirt.prometheus", "devirtualize"),
)

_METHOD_NAMES = {
    "core.devirt.luraph": "Luraph container unpack + VM introspection",
    "core.devirt.bytecode_vm": "Lua 5.1 bytecode reconstruction",
    "core.devirt.wrd": "WRD/WeAreDevs string-pool recovery",
    "core.devirt.nexus": "literal reassembly + bytecode reconstruction",
    "core.devirt.prometheus": "control-flow flattening removal",
    "core.devirt.table_vm": "custom VM introspection",
}


@dataclass(frozen=True)
class DevirtResult:
    family: str
    method: str
    source: str | None = None
    bytecode: bytes | None = None
    notes: tuple[str, ...] = ()
    partial: bool = True
    confidence: float = 0.0
    listing: str = ""
    opcode_names: tuple[tuple[int, str], ...] = field(default_factory=tuple)

    @property
    def recovered(self) -> bool:
        return bool(self.source and self.source.strip())

    def as_dict(self) -> dict[str, object]:
        return {
            "family": self.family,
            "method": self.method,
            "recovered": self.recovered,
            "partial": self.partial,
            "confidence": round(self.confidence, 3),
            "notes": list(self.notes),
            "bytecode_bytes": len(self.bytecode) if self.bytecode else 0,
            "opcode_names": {str(opcode): name for opcode, name in self.opcode_names},
            "has_listing": bool(self.listing),
        }


def _load(path: str, name: str) -> Any | None:
    try:
        module = importlib.import_module(path)
    except Exception:  # noqa: BLE001 - an unavailable strategy is not an error
        return None
    return getattr(module, name, None)


def _call(strategy: Any, source: str, *, vm_tables: Sequence[Any] | None,
          vm_analysis: Any | None, family: str, logger: logging.Logger | None) -> dict[str, Any] | None:
    kwargs: dict[str, Any] = {"family": family}
    if vm_tables:
        kwargs["vm_tables"] = vm_tables
    if vm_analysis is not None:
        kwargs["vm_analysis"] = vm_analysis
    try:
        result = strategy(source, **kwargs)
    except TypeError:
        try:
            result = strategy(source)
        except Exception as exc:  # noqa: BLE001
            if logger is not None:
                logger.debug("Devirtualizer %r failed: %s", strategy, exc)
            return None
    except Exception as exc:  # noqa: BLE001
        if logger is not None:
            logger.debug("Devirtualizer %r failed: %s", strategy, exc)
        return None
    return dict(result) if isinstance(result, dict) else None


def devirtualize(
    family: str,
    source: str,
    *,
    vm_tables: Sequence[Any] | None = None,
    vm_analysis: Any | None = None,
    logger: logging.Logger | None = None,
) -> DevirtResult | None:
    """Run the family's own recovery method and normalise the outcome.

    Strategies are tried in order; the first one that recovers source wins,
    otherwise the most confident description is returned (a VM surface, an
    annotated disassembly, ...).  Failures never propagate.
    """
    if not source:
        return None
    key = (family or "generic").lower()
    chosen = _STRATEGIES.get(key, _FALLBACK)
    best: DevirtResult | None = None
    for path, name in chosen:
        strategy = _load(path, name)
        if strategy is None:
            continue
        raw = _call(
            strategy,
            source,
            vm_tables=vm_tables,
            vm_analysis=vm_analysis,
            family=key,
            logger=logger,
        )
        if raw is None:
            continue
        result = DevirtResult(
            family=raw.get("family", key),
            method=str(raw.get("method") or _METHOD_NAMES.get(path, path)),
            source=raw.get("source"),
            bytecode=raw.get("bytecode"),
            notes=tuple(raw.get("notes", ()) or ()),
            partial=bool(raw.get("partial", True)),
            confidence=float(raw.get("confidence", 0.0) or 0.0),
            listing=str(raw.get("listing", "") or ""),
            opcode_names=tuple(sorted((raw.get("opcode_names") or {}).items())),
        )
        if best is None or (result.recovered, result.confidence, len(result.notes)) > (
            best.recovered,
            best.confidence,
            len(best.notes),
        ):
            best = result
        if result.recovered:
            break
    return best


def available_families() -> tuple[str, ...]:
    """Family keys that have an own recovery method."""
    return tuple(sorted(_STRATEGIES))


def report_table() -> tuple[tuple[str, str], ...]:
    """``(family, method)`` pairs, for docs and the analysis report."""
    table: list[tuple[str, str]] = []
    for family in available_families():
        paths = {path for path, _ in _STRATEGIES[family]}
        names = ", ".join(
            _METHOD_NAMES.get(path, path) for path in sorted(paths)
        )
        table.append((family, names))
    return tuple(table)
