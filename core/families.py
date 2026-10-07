"""Obfuscator family registry: identification plus recovery strategies.

Protez does not promise a magic "any obfuscator" button, but it does try the
techniques that actually work per family, in order of how much source they
recover:

1. family-specific static lifting (Luraph containers, MoonSec V3 handlers,
   embedded Lua 5.1 bytecode),
2. running the loader under the executor environment and capturing every
   ``loadstring``/``load`` payload (portable Lua backend or the native Luau
   worker),
3. decompiling captured Lua 5.1 bytecode into structured pseudocode,
4. a clearly labelled partially cleaned preview when only strings could be
   recovered.

Every handler reports what it actually did, so a partial result never looks
like a full one.
"""

from __future__ import annotations

import base64
import re
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from core.lua51 import (
    BytecodeError,
    Lua51Scanner,
    decompile,
    is_lua51_bytecode,
    looks_like_luau_bytecode,
    read_chunk,
)
from core.protection import ProtectionProfile, inspect_protection

__all__ = [
    "FamilyMatch",
    "FamilyOutcome",
    "FamilyHandler",
    "FAMILY_HANDLERS",
    "detect_families",
    "best_family",
    "family_report",
    "scan_embedded_bytecode",
    "scan_embedded_source",
    "MAX_EMBEDDED_SCAN_BYTES",
]

MAX_EMBEDDED_SCAN_BYTES = 12 * 1024 * 1024


@dataclass(frozen=True)
class FamilyMatch:
    key: str
    display_name: str
    version: str | None
    confidence: float
    evidence: tuple[str, ...] = ()

    @property
    def label(self) -> str:
        return f"{self.display_name} v{self.version}" if self.version else self.display_name


@dataclass
class FamilyOutcome:
    family: str
    method: str
    source: str | None = None
    bytecode: bytes | None = None
    notes: tuple[str, ...] = ()
    partial: bool = True
    confidence: float = 0.0

    @property
    def recovered(self) -> bool:
        return bool(self.source and self.source.strip())


class FamilyHandler:
    """Base class: a family knows how to recognise and how to approach itself.

    Two kinds of name markers exist because the two are not equally reliable:

    * ``markers`` are searched across the whole file.  They are only used for
      tokens an obfuscator's *code* carries and other families' pools do not
      (``LPH``, ``syn.protect``, ...).
    * ``banner_markers`` are searched only in the preamble
      (``banner_window`` characters).  A family's own name is a banner: every
      obfuscator puts it at the top, while an *obfuscated* payload's string
      pool is full of other obfuscators' names (PSU, MoonSec and Wynfuscate
      loaders all carry an ``IB2``/``IB3`` detection list), so a whole-file
      search for ``IronBrew`` used to outrank the real banner and route the
      sample to the wrong devirtualizer.
    """

    key = "generic"
    display_name = "Unknown obfuscator"
    version: str | None = None
    markers: tuple[str, ...] = ()
    banner_markers: tuple[str, ...] = ()
    banner_window: int = 512
    structural: tuple[str, ...] = ()
    version_pattern: str | None = None
    marker_threshold: float = 0.85

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        return self.marker_confidence(source)

    def evidence(self, source: str) -> tuple[str, ...]:
        lowered = source.lower()
        found = [marker for marker in self.markers if marker.lower() in lowered]
        if self.banner_markers:
            head = lowered[: self.banner_window]
            found += [marker for marker in self.banner_markers if marker.lower() in head]
        return tuple(found)

    def structural_evidence(self, source: str) -> tuple[str, ...]:
        found: list[str] = []
        for pattern in self.structural:
            try:
                if re.search(pattern, source, re.IGNORECASE):
                    found.append(pattern)
            except re.error:
                continue
        return tuple(found)

    def detect_version(self, source: str) -> str | None:
        if not self.version_pattern:
            return self.version
        match = re.search(self.version_pattern, source, re.IGNORECASE)
        if match is None:
            return self.version
        groups = [group for group in match.groups() if group]
        return groups[0] if groups else self.version

    def marker_confidence(self, source: str, *, structural_base: float = 0.55) -> float:
        """Confidence from a named marker, else from a structural fingerprint."""
        if self.evidence(source):
            return self.marker_threshold
        if self.structural_evidence(source):
            return structural_base
        return 0.0

    def recover(
        self,
        source: str,
        *,
        embedded_bytecode: bytes | None = None,
        captured_source: str | None = None,
        vm_summary: str | None = None,
    ) -> FamilyOutcome | None:
        """Try to recover this family's payload.

        ``embedded_bytecode``/``captured_source`` come from the static and
        dynamic passes.  ``vm_summary`` describes the custom VM surface a
        running loader exposed (instruction count, opcodes, constants) and is
        always worth reporting: it is what a partial result can honestly show
        when no lifter understands the VM.
        """
        if vm_summary:
            return FamilyOutcome(
                family=self.display_name,
                method="running-loader VM introspection",
                notes=(vm_summary,),
                partial=True,
                confidence=0.3,
            )
        return None

    def vm_surface_outcome(self, vm_summary: str) -> FamilyOutcome:
        """What can be said when the loader ran but its VM was not lifted."""
        return FamilyOutcome(
            family=self.display_name,
            method="running-loader VM introspection",
            notes=(
                vm_summary,
                "the VM ran inside the portable backend, so its tables were read; "
                "lifting its opcodes to source needs a per-family opcode map",
            ),
            partial=True,
            confidence=0.35,
        )

    # Shared helpers -------------------------------------------------
    @staticmethod
    def decompile_bytecode(bytecode: bytes) -> str | None:
        try:
            return decompile(bytecode)
        except BytecodeError:
            return None

    @staticmethod
    def outcome_from_bytecode(bytecode: bytes, *, family: str, method: str) -> FamilyOutcome:
        recovered = FamilyHandler.decompile_bytecode(bytecode)
        if recovered is None:
            return FamilyOutcome(
                family=family,
                method=method,
                notes=("embedded bytecode was found but its layout is unsupported",),
            )
        return FamilyOutcome(
            family=family,
            method=f"{method} + Lua 5.1 pseudo-source recovery",
            source=recovered,
            bytecode=bytecode,
            partial=True,
            confidence=0.75,
            notes=(
                "recovered from embedded Lua 5.1 bytecode",
                "register names and comments cannot be restored from stripped bytecode",
            ),
        )


_NUMBER_ARRAY = re.compile(
    r"""\{\s*(?P<body>
         (?:\s*(?:0[xX][0-9a-fA-F]+|\d+)\s*,){8,}\s*
         (?:0[xX][0-9a-fA-F]+|\d+)\s*
        )\}""",
    re.VERBOSE,
)


def _decode_number_arrays(text: str) -> list[bytes]:
    """Decode ``{27, 76, 117, 97, ...}`` style byte tables used by loaders.

    Most bytecode-based Roblox obfuscators (IronBrew, WeAreDevs v2.4, PSU,
    Nexus) build their chunk from a numeric table, so recognising decimal and
    hex arrays is worth more than any single family signature.
    """
    decoded: list[bytes] = []
    for match in _NUMBER_ARRAY.finditer(text[: MAX_EMBEDDED_SCAN_BYTES * 2]):
        entries = re.findall(r"0[xX][0-9a-fA-F]+|\d+", match.group("body"))
        if len(entries) < 24:
            continue
        values: list[int] = []
        for entry in entries:
            try:
                value = int(entry, 16) if entry[:2].lower() == "0x" else int(entry)
            except ValueError:
                values = []
                break
            if not 0 <= value <= 255:
                values = []
                break
            values.append(value)
        if values:
            decoded.append(bytes(values))
    return decoded


def scan_embedded_bytecode(data: str | bytes, *, minimum: int = 64) -> bytes | None:
    """Find a Lua 5.1 chunk inside text, hex, base64, escapes or byte arrays."""
    if isinstance(data, bytes):
        candidates: list[bytes] = [data, data.replace(b"\x00", b"")]
    else:
        candidates = [data.encode("utf-8", "ignore")]
        candidates.extend(_decode_text_layers(data))
        candidates.extend(_decode_number_arrays(data))
    for candidate in candidates:
        if is_lua51_bytecode(candidate):
            try:
                read_chunk(candidate)
                return candidate
            except BytecodeError:
                continue
        found = Lua51Scanner(candidate).find(minimum=minimum)
        if found:
            best = found[0][1]
            try:
                read_chunk(best)
                return best
            except BytecodeError:
                continue
    return None


_CHAR_CALL = re.compile(r"string\.char\s*\(\s*((?:0[xX][0-9a-fA-F]+|\d+)(?:\s*,\s*(?:0[xX][0-9a-fA-F]+|\d+)){11,})\s*\)")
_ESCAPE_RUN = re.compile(r"((?:\\[0-9]{1,3}){12,})")


def _decode_char_calls(text: str, *, limit: int = 512) -> list[bytes]:
    """Decode ``string.char(...)`` runs a loader uses to build a payload."""
    decoded: list[bytes] = []
    for match in _CHAR_CALL.finditer(text[: MAX_EMBEDDED_SCAN_BYTES * 2]):
        entries = re.findall(r"0[xX][0-9a-fA-F]+|\d+", match.group(1))
        values: list[int] = []
        for entry in entries:
            try:
                value = int(entry, 16) if entry[:2].lower() == "0x" else int(entry)
            except ValueError:
                values = []
                break
            if not 0 <= value <= 255:
                values = []
                break
            values.append(value)
        if len(values) >= 12:
            decoded.append(bytes(values))
        if len(decoded) >= limit:
            break
    return decoded


def _decode_escape_runs(text: str, *, limit: int = 256) -> list[bytes]:
    """Decode Lua string escapes: ``"\\104\\101\\108..."`` spells source."""
    decoded: list[bytes] = []
    for match in _ESCAPE_RUN.finditer(text[: MAX_EMBEDDED_SCAN_BYTES * 2]):
        parts = re.findall(r"\\([0-9]{1,3})", match.group(1))
        try:
            values = bytes(int(part) for part in parts)
        except ValueError:
            continue
        decoded.append(values)
        if len(decoded) >= limit:
            break
    return decoded


# A blob made only of these characters carries no Lua structure: it is
# encoded data that survived a decode step, not a recovered script.
_DATA_ALPHABET = re.compile(r"[A-Za-z0-9+/=\\s]+")


def scan_embedded_source(data: str | bytes, *, minimum: int = 48) -> str | None:
    """Find Lua **source** hidden in escapes, hex/base64 or numeric arrays.

    Several families (PSU, Nexus, WeAreDevs variants, home-made packers) never
    store bytecode: they store the original script as numbers, escape runs or
    ``string.char`` calls and rebuild it at run time.  That payload is readable
    source, so it is worth looking for directly instead of only for a chunk.
    """
    from core.executor_api import looks_like_lua_source

    if isinstance(data, bytes):
        candidates: list[bytes] = [data]
    else:
        candidates = []
        candidates.extend(_decode_text_layers(data))
        candidates.extend(_decode_number_arrays(data))
        candidates.extend(_decode_char_calls(data))
        candidates.extend(_decode_escape_runs(data))
    best: str | None = None
    fallback: str | None = None
    for candidate in candidates:
        text = candidate.decode("utf-8", "replace")
        if is_lua51_bytecode(candidate) or looks_like_luau_bytecode(candidate):
            continue
        if len(text.strip()) < minimum:
            continue
        if looks_like_lua_source(text):
            if best is None or len(text) > len(best):
                best = text
        elif fallback is None:
            fallback = text
    if best is not None:
        return best
    # No Lua keyword found, but a decoded blob that is plain printable text and
    # much larger than a single string is still a candidate worth reporting --
    # unless it is *data*: a blob made only of base64 characters (no whitespace,
    # no punctuation a script needs) is an encoded payload, not source, and
    # calling it recovered source would send an analyst chasing noise.  WRD and
    # MoonSec wrappers decode to exactly that shape.
    if fallback is not None:
        head = fallback[:2000]
        printable = sum(1 for character in head if character.isprintable() or character in "\n\r\t")
        structured = any(character.isspace() for character in head) and any(
            character in ",()=;[]{}'\"\n" for character in head
        )
        if (printable >= len(head) * 0.95 and len(fallback.strip()) >= max(minimum, 96)
                and structured and not _DATA_ALPHABET.fullmatch(head.strip())):
            return fallback
    return None


def _decode_text_layers(text: str) -> list[bytes]:
    """Decode string escapes, hex blobs and base64 blobs from text."""
    decoded: list[bytes] = []

    escaped = re.search(r"\\27\\76\\117\\97|\x1bLua|\\\\27Lua", text)
    if escaped is not None:
        decoded.append(text.encode("latin-1", "ignore").replace(b"\\27Lua", b"\x1bLua"))

    for match in re.finditer(r"(?i)((?:\\x[0-9a-f]{2}){16,})", text):
        try:
            decoded.append(bytes.fromhex(match.group(1).replace("\\x", "")))
        except ValueError:
            continue

    for match in re.finditer(r"(?i)((?:\\[0-9]{1,3}){16,})", text):
        parts = re.findall(r"\\([0-9]{1,3})", match.group(1))
        try:
            values = bytes(int(part) for part in parts)
        except ValueError:
            continue
        if values.startswith(b"\x1bLua"):
            decoded.append(values)

    if len(text) <= 4 * 1024 * 1024:
        compact = re.sub(r"\s+", "", text)
        if len(compact) >= 32 and re.fullmatch(r"[A-Za-z0-9+/=]+", compact):
            try:
                decoded.append(base64.b64decode(compact, validate=False))
            except Exception:  # noqa: BLE001 - best effort decoding
                pass
    return decoded


class LuraphHandler(FamilyHandler):
    key = "luraph"
    display_name = "Luraph Obfuscator"
    markers = ("LPH",)
    banner_markers = ("Luraph",)
    version_pattern = r"luraph(?:\s+obfuscator)?\s+v?(\d+(?:\.\d+)*)"

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        if profile is not None and profile.family == "Luraph Obfuscator":
            return 0.97
        evidence = self.evidence(source)
        return 0.6 if evidence else 0.0

    def recover(
        self,
        source,
        *,
        embedded_bytecode=None,
        captured_source=None,
        vm_summary=None,
    ):
        if captured_source:
            return FamilyOutcome(
                family=self.display_name,
                method="isolated execution capture",
                source=captured_source,
                partial=False,
                confidence=0.8,
                notes=("payload captured from the Luraph wrapper at runtime",),
            )
        return FamilyOutcome(
            family=self.display_name,
            method="bounded container extraction",
            notes=(
                "Luraph stores a custom VM stream; Protez extracts containers and lifts "
                "the supported v14.7-v14.9 and v15 layouts",
            ),
        )


class MoonSecHandler(FamilyHandler):
    key = "moonsec"
    display_name = "MoonSec"
    # "diu9u" is MoonSec V2's own signature: its wrapper banner is a rude
    # ASCII comment that never spells the product name.
    banner_markers = ("MoonSec", "MoonSecV2", "MoonSecV3", "moonsec", "diu9u")
    version_pattern = r"moonsec\s*v?(\d+(?:\.\d+)*)"

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        if profile is not None and profile.family == "MoonSec":
            return 0.95
        return 0.55 if self.evidence(source) else 0.0

    def recover(
        self,
        source,
        *,
        embedded_bytecode=None,
        captured_source=None,
        vm_summary=None,
    ):
        if embedded_bytecode is not None:
            return self.outcome_from_bytecode(
                embedded_bytecode, family=self.display_name, method="static handler mapping"
            )
        if captured_source:
            return FamilyOutcome(
                family=self.display_name,
                method="isolated execution capture",
                source=captured_source,
                partial=False,
                confidence=0.8,
            )
        if vm_summary:
            return self.vm_surface_outcome(vm_summary)
        return None


class WeAreDevsHandler(FamilyHandler):
    key = "wearedevs"
    display_name = "WeAreDevs Obfuscator"
    version = "2.4"
    banner_markers = ("WeAreDevs", "wearedevs", "wad_obfuscator")
    version_pattern = r"wearedevs[^0-9]{0,12}v?(\d+(?:\.\d+)*)"

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        if self.evidence(source):
            return 0.85
        if _looks_like_numeric_loader(source):
            return 0.5
        return 0.0

    def recover(
        self,
        source,
        *,
        embedded_bytecode=None,
        captured_source=None,
        vm_summary=None,
    ):
        if captured_source:
            recovered = scan_embedded_bytecode(captured_source)
            if recovered is not None:
                return self.outcome_from_bytecode(
                    recovered, family=self.display_name, method="runtime capture"
                )
            return FamilyOutcome(
                family=self.display_name,
                method="runtime capture",
                source=captured_source,
                partial=False,
                confidence=0.75,
            )
        if embedded_bytecode is not None:
            return self.outcome_from_bytecode(
                embedded_bytecode, family=self.display_name, method="static array decoding"
            )
        if vm_summary:
            return self.vm_surface_outcome(vm_summary)
        return None


class IronBrewHandler(FamilyHandler):
    key = "ironbrew"
    display_name = "IronBrew"
    banner_markers = ("IronBrew", "ironbrew", "IB2", "IB3")
    version_pattern = r"ironbrew[^0-9]{0,4}(\d+(?:\.\d+)*)"

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        if self.evidence(source):
            return 0.9
        if _looks_like_numeric_loader(source) and "getfenv" in source:
            return 0.45
        return 0.0

    def recover(
        self,
        source,
        *,
        embedded_bytecode=None,
        captured_source=None,
        vm_summary=None,
    ):
        if captured_source:
            recovered = scan_embedded_bytecode(captured_source) or (
                captured_source.encode("latin-1", "ignore")
                if is_lua51_bytecode(captured_source)
                else None
            )
            if recovered is not None:
                return self.outcome_from_bytecode(
                    recovered, family=self.display_name, method="runtime capture"
                )
            return FamilyOutcome(
                family=self.display_name,
                method="runtime capture",
                source=captured_source,
                partial=False,
                confidence=0.7,
            )
        if embedded_bytecode is not None:
            return self.outcome_from_bytecode(
                embedded_bytecode, family=self.display_name, method="static extraction"
            )
        if vm_summary:
            return self.vm_surface_outcome(vm_summary)
        return None


class PsuHandler(FamilyHandler):
    key = "psu"
    display_name = "PSU Obfuscator"
    version = "1.0"
    banner_markers = ("PSU", "psu_obfuscator", "PsuObf", "PSU Obfuscator")
    version_pattern = r"psu(?:\s+obfuscator)?\s*v?(\d+(?:\.\d+)*)"

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        if self.evidence(source):
            return 0.85
        return 0.3 if _looks_like_numeric_loader(source) else 0.0


class NexusHandler(FamilyHandler):
    key = "nexus"
    display_name = "Nexus Obfuscator"
    version = "2.0"
    banner_markers = (
        "Nexus Obfuscator",
        "nexus_obfuscator",
        "NexusObf",
        "obfuscated by nexus",
        "nexus obfuscator",
    )
    structural = (
        r"\\27\\76\\117\\97",  # \27Lua escaped bytecode header
        r"getfenv\s*\(\s*0\s*\)",
    )
    version_pattern = r"nexus(?:\s+obfuscator)?\s*v?(\d+(?:\.\d+)*)"


class PrometheusHandler(FamilyHandler):
    key = "prometheus"
    display_name = "Prometheus"
    banner_markers = ("Prometheus", "prometheus", "levno-710")
    structural = (r"\\27\\76\\117\\97", r"\\27Lua")
    version_pattern = r"prometheus\s*v?(\d+(?:\.\d+)*)"


class WynfuscateHandler(FamilyHandler):
    key = "wynfuscate"
    display_name = "Wynfuscate"
    version = "5"
    banner_markers = (
        "Wynfuscate",
        "wynfuscate",
        "Wynf",
        "obfuscated by wyn",
        "wyn obfuscator",
    )
    structural = (r"\bwyn\b", r"string\.char\s*\(\s*0x")
    version_pattern = r"wyn(?:fuscate)?\s*v?(\d+(?:\.\d+)*)"


class AztupHandler(FamilyHandler):
    key = "aztup"
    display_name = "AztupBrew"
    version = "2"
    banner_markers = ("AztupBrew", "aztupbrew", "Aztup Brew", "aztup")
    version_pattern = r"aztup(?:brew)?\s*v?(\d+(?:\.\d+)*)"


class XenHandler(FamilyHandler):
    key = "xen"
    display_name = "Xen Obfuscator"
    banner_markers = ("Xen Obfuscator", "xen_obf", "obfuscated by xen")
    version_pattern = r"xen(?:\s+obfuscator)?\s*v?(\d+(?:\.\d+)*)"


class SynapseHandler(FamilyHandler):
    key = "synapse-protected"
    display_name = "Synapse-protected payload"
    markers = ("syn.protect",)
    banner_markers = ("Synapse", "synapse secure")
    structural = (r"syn\s*\.\s*protect(_gui)?",)


class HyperionHandler(FamilyHandler):
    key = "hyperion"
    display_name = "Hyperion (Roblox client)"
    banner_markers = ("Hyperion", "Byfron", "hyperion-protected")


class LuauVmHandler(FamilyHandler):
    key = "luau-vm"
    display_name = "Luau VM (custom bytecode)"
    markers = ()
    structural = (
        r"string\.char\s*\(\s*\d+\s*\)\s*\.\.",  # byte-by-byte string build
        r"string\.dump\s*\(",
        r"buffer\.(fromstring|readu8|tostring)",
    )

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        evidence = self.structural_evidence(source)
        if not evidence:
            return 0.0
        lowered = source.lower()
        if "loadstring" in lowered or "buffer.fromstring" in lowered:
            return 0.5
        return 0.35


class GenericVmHandler(FamilyHandler):
    key = "generic-vm"
    display_name = "custom VM / unknown obfuscator"
    markers = ()

    def confidence(self, source: str, profile: ProtectionProfile | None) -> float:
        if _looks_like_numeric_loader(source) and "loadstring" in source.lower():
            return 0.35
        if re.search(r"(?i)\bload(?:string)?\s*\(\s*(?:game\s*[.:]\s*)?(?:HttpGet|request)", source):
            return 0.4
        # Untouched scripts stay unlabelled: a family hint has to mean something.
        if _looks_like_obfuscated_blob(source):
            return 0.15
        return 0.0


FAMILY_HANDLERS: tuple[FamilyHandler, ...] = (
    LuraphHandler(),
    MoonSecHandler(),
    WeAreDevsHandler(),
    IronBrewHandler(),
    PsuHandler(),
    NexusHandler(),
    PrometheusHandler(),
    WynfuscateHandler(),
    AztupHandler(),
    XenHandler(),
    SynapseHandler(),
    HyperionHandler(),
    LuauVmHandler(),
    GenericVmHandler(),
)

_HANDLERS_BY_KEY = {handler.key: handler for handler in FAMILY_HANDLERS}


def _looks_like_obfuscated_blob(source: str) -> bool:
    """Cheap "machine-generated text" probe for unlabelled obfuscators."""
    if not source:
        return False
    sample = source[:200_000]
    lines = sample.count("\n") + 1
    escaped = sample.count("\\") + sample.count("%")
    symbols = sum(1 for character in sample if not character.isalnum() and not character.isspace())
    long_line = len(sample) / lines > 300 if lines else False
    return long_line or escaped > 400 or symbols > len(sample) * 0.28


def _looks_like_numeric_loader(source: str) -> bool:
    if not source:
        return False
    digits = sum(1 for character in source[:200_000] if character.isdigit())
    commas = source.count(",")
    return digits > 2000 and commas > 300


def detect_families(source: str, *, profile: ProtectionProfile | None = None) -> tuple[FamilyMatch, ...]:
    """Return every family match, most confident first."""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    if profile is None:
        try:
            profile = inspect_protection(source)
        except Exception:  # noqa: BLE001 - detection must never break a run
            profile = None
    matches: list[FamilyMatch] = []
    for handler in FAMILY_HANDLERS:
        confidence = handler.confidence(source, profile)
        if confidence <= 0:
            continue
        matches.append(
            FamilyMatch(
                key=handler.key,
                display_name=handler.display_name,
                version=handler.detect_version(source),
                confidence=confidence,
                evidence=(
                    handler.evidence(source) + handler.structural_evidence(source)
                ),
            )
        )
    matches.sort(key=lambda match: match.confidence, reverse=True)
    return tuple(matches)


def best_family(source: str, *, profile: ProtectionProfile | None = None) -> FamilyMatch | None:
    matches = detect_families(source, profile=profile)
    return matches[0] if matches else None


def handler_for(key: str) -> FamilyHandler | None:
    return _HANDLERS_BY_KEY.get(key)


def family_report(source: str, *, profile: ProtectionProfile | None = None) -> list[dict[str, object]]:
    return [
        {
            "key": match.key,
            "family": match.display_name,
            "version": match.version,
            "confidence": round(match.confidence, 2),
            "evidence": list(match.evidence),
        }
        for match in detect_families(source, profile=profile)
    ]


def supported_families() -> list[tuple[str, str]]:
    return [(handler.key, handler.display_name) for handler in FAMILY_HANDLERS]
