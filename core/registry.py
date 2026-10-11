"""Deobfuscator registry - the extension point for new obfuscators.

Adding a new obfuscator means:

1. subclass :class:`Deobfuscator`,
2. implement :meth:`Deobfuscator.detect` (a thin wrapper around structural
   markers) and :meth:`Deobfuscator.deobfuscate` (usually by reusing
   :class:`core.sandbox.Sandbox` and :mod:`core.pick_payload`),
3. register it in ``DEOBFUSCATORS``.

Everything else - the GUI, the CLI, ``bootstrap.py``, the report format - picks
it up automatically, which is what the TZ asked for ("архитектура должна
позволять добавлять другие обфускаторы без переписывания").
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple, Type

from .wrd_detect import DetectionResult, detect


class Deobfuscator:
    """Base class for format specific deobfuscators."""

    #: registry key, e.g. ``"wrd"``
    name: str = "base"
    #: human readable label used by the GUI
    label: str = "Base"
    #: False for formats that are recognised but not implemented yet
    implemented: bool = False
    #: short note shown when the format is recognised but unsupported
    note: str = ""

    def detect(self, source: str) -> DetectionResult:  # pragma: no cover - overridden
        raise NotImplementedError

    def deobfuscate(self, source: str, **kwargs):  # pragma: no cover - overridden
        raise NotImplementedError(
            f"{self.label} support is not implemented yet. {self.note or ''}".strip()
        )


class WRDDeobfuscator(Deobfuscator):
    """WeAreDevs (v1.0.0 and compatible) - the primary target."""

    name = "wrd"
    label = "WeAreDevs"
    implemented = True

    def detect(self, source: str) -> DetectionResult:
        return detect(source)

    def deobfuscate(self, source: str, **kwargs):
        from .deobfuscate import deobfuscate  # local import: avoids a cycle

        return deobfuscate(source, **kwargs)


class UnsupportedDeobfuscator(Deobfuscator):
    """Recognised, routed, not implemented yet.

    These placeholders exist on purpose: the TZ asks for the architecture to be
    ready for Luraph/Moonside-style obfuscators without pretending they work
    today.  Each one carries a note describing what the implementation would
    need, and the GUI reports it as "recognised, not supported" instead of
    failing with a stack trace.
    """

    implemented = False

    def detect(self, source: str) -> DetectionResult:
        return detect(source)


class LuraphDeobfuscator(UnsupportedDeobfuscator):
    name = "luraph"
    label = "Luraph"
    note = (
        "Luraph uses a bytecode VM with a per-build instruction set; support needs a "
        "custom lifter plus a dynamic trace stage (core/vm_trace.py already provides "
        "the tracing half)."
    )


class MoonsecDeobfuscator(UnsupportedDeobfuscator):
    name = "moonsec"
    label = "Moonsec"
    note = (
        "Moonsec v3 needs the string pool decoder re-implemented and the shuffle "
        "replayed (core/wrd_static.py shows the pattern)."
    )


class IronBrewDeobfuscator(UnsupportedDeobfuscator):
    name = "ironbrew"
    label = "IronBrew"
    note = "IronBrew 2 needs Lua 5.1 bytecode support and the VM interpreter lifted."


DEOBFUSCATORS: Dict[str, Type[Deobfuscator]] = {
    "wrd": WRDDeobfuscator,
    "luraph": LuraphDeobfuscator,
    "moonsec": MoonsecDeobfuscator,
    "ironbrew": IronBrewDeobfuscator,
}


@dataclass
class Route:
    """Result of :func:`detect_and_route`."""

    deobfuscator: Optional[Deobfuscator]
    detection: DetectionResult

    @property
    def supported(self) -> bool:
        return bool(self.deobfuscator and self.deobfuscator.implemented)

    @property
    def message(self) -> str:
        if self.deobfuscator is None:
            return f"unknown format ({self.detection.reason})"
        if not self.deobfuscator.implemented:
            return f"{self.deobfuscator.label} recognised, not supported yet. {self.deobfuscator.note}".strip()
        return f"{self.deobfuscator.label} {('v' + self.detection.version) if self.detection.version else ''}".strip()


def detect_and_route(source: str) -> Route:
    """Detect the format and return the deobfuscator that can handle it."""
    detection = detect(source)
    if detection.is_obfuscated:
        deobfuscator_type = DEOBFUSCATORS.get(detection.format)
        if deobfuscator_type:
            return Route(deobfuscator_type(), detection)
    return Route(None, detection)


def available() -> List[Tuple[str, str, bool]]:
    """``(name, label, implemented)`` for every registered format."""
    return [(key, cls.label, cls.implemented) for key, cls in DEOBFUSCATORS.items()]


__all__ = [
    "DEOBFUSCATORS",
    "Deobfuscator",
    "IronBrewDeobfuscator",
    "LuraphDeobfuscator",
    "MoonsecDeobfuscator",
    "Route",
    "UnsupportedDeobfuscator",
    "WRDDeobfuscator",
    "available",
    "detect_and_route",
]
