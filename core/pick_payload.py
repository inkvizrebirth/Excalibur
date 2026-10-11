"""Choose the most promising payload from everything the sandbox captured.

The sandbox can produce dozens of artefacts for one input:

* ``dump_NNN.lua``      chunks passed to ``load``/``loadstring``
* ``concat_NNN.lua``    strings rebuilt with ``table.concat`` (WRD reassembles
                        its decoded pool that way - verified on real samples)
* ``sandbox_*.lua``     content the script itself pushed through
                        ``__sandbox_writefile``
* the static layer's rewritten source

Scoring is deliberately explainable: every point added or removed is recorded so
the GUI/report can show *why* a candidate was chosen, which matters when several
payloads come from a control-flow-flattened script and none of them is the
original source.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Iterable, List, Optional, Sequence, Tuple

#: Text that looks like ordinary Lua source.
SOURCE_SIGNALS: Tuple[Tuple[str, int], ...] = (
    ("local ", 3), ("function", 3), ("if ", 2), ("then", 1), ("for ", 2), ("while ", 1),
    ("return", 2), ("end", 1), ("print", 1), ("=", 1), (".", 1), ("--", 1), ("\n", 1),
)

#: Text that indicates we captured *obfuscated* code instead of the original.
OBFUSCATION_SIGNALS: Tuple[Tuple[str, int], ...] = (
    ("wearedevs.net/obfuscator", 40),
    ("return(function(...)", 25),
)

ESCAPED_RUN_RE = re.compile(r'(?:\\\d{1,3}){6,}')
ARITH_RUN_RE = re.compile(r"\d+\s*[-+]\s*\d+")
BINARY_CONTROL_RE = re.compile(r"[\x00-\x08\x0b\x0c\x0e-\x1f]")


@dataclass
class PayloadPick:
    """A scored payload candidate."""

    path: Optional[Path]
    text: str
    score: float
    reasons: List[str] = field(default_factory=list)
    source: str = "unknown"  # "load" | "concat" | "static" | "writefile" | "text"

    @property
    def length(self) -> int:
        return len(self.text)

    def as_dict(self, *, preview: int = 200) -> dict:
        return {
            "path": str(self.path) if self.path else None,
            "source": self.source,
            "score": round(self.score, 3),
            "length": self.length,
            "reasons": self.reasons,
            "preview": self.text[:preview],
        }


def printable_ratio(text: str) -> float:
    if not text:
        return 0.0
    ok = sum(1 for ch in text if 32 <= ord(ch) < 127 or ch in "\n\r\t")
    return ok / len(text)


def score_text(text: str, *, weight_structure: float = 1.0) -> Tuple[float, List[str]]:
    """Score how much ``text`` looks like a clean Lua source file."""
    score = 0.0
    reasons: List[str] = []
    if not text:
        return -1000.0, ["empty"]

    length = len(text)
    ratio = printable_ratio(text)
    if ratio < 0.6:
        score -= 60
        reasons.append(f"mostly non printable ({ratio:.0%})")
    else:
        score += ratio * 8

    signals = 0
    hits: List[str] = []
    for token, weight in SOURCE_SIGNALS:
        count = text.count(token)
        if count:
            signals += weight * min(count, 40)
            hits.append(f"{token.strip() or 'nl'}x{count}")
    score += min(signals, 220) * weight_structure
    if hits:
        reasons.append("lua constructs: " + ", ".join(hits[:6]))

    for token, penalty in OBFUSCATION_SIGNALS:
        if token in text:
            score -= penalty
            reasons.append(f"still obfuscated ({token[:28]}...)")

    escaped = len(ESCAPED_RUN_RE.findall(text))
    if escaped > 20:
        score -= min(escaped / 4.0, 45)
        reasons.append(f"{escaped} escaped-decimal runs")

    arith = len(ARITH_RUN_RE.findall(text))
    if length:
        density = arith / max(length / 1000.0, 1.0)
        if density > 30:
            score -= min(density / 6.0, 30)
            reasons.append(f"constant arithmetic density {density:.0f}/kB")

    if BINARY_CONTROL_RE.search(text):
        score -= 25
        reasons.append("binary control characters")

    if length < 80:
        score -= 50
        reasons.append("too short")
    elif length < 400:
        score -= 8
        reasons.append("small payload")
    elif length > 4_000_000:
        score -= 10
        reasons.append("unusually large payload")
    else:
        score += min(length / 4000.0, 20)

    return score, reasons


def looks_like_same_file(candidate: str, source: str) -> bool:
    """True when the candidate is (a normalisation of) the input itself."""
    if not candidate or not source:
        return False
    if len(candidate) == len(source) and candidate == source:
        return True
    a = hashlib.sha1(candidate.strip().encode("utf-8", "replace")).hexdigest()
    b = hashlib.sha1(source.strip().encode("utf-8", "replace")).hexdigest()
    return a == b


def _source_kind(path: Path) -> str:
    name = path.name
    if name.startswith("dump_"):
        return "load"
    if name.startswith("concat_"):
        return "concat"
    if name.startswith("sandbox_"):
        return "writefile"
    if name.endswith(".decoded.lua") or name.startswith("decoded"):
        return "static"
    return "text"


def pick_payload(
    candidates: Sequence[Path],
    source: str,
    *,
    min_chars: int = 80,
    max_candidates: int = 400,
    source_hash: Optional[str] = None,
    extra_texts: Optional[Iterable[Tuple[str, str]]] = None,
) -> Optional[PayloadPick]:
    """Score every candidate and return the best one (or None)."""
    picks: List[PayloadPick] = []

    for path in list(candidates)[:max_candidates]:
        try:
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            continue
        if len(text) < min_chars:
            continue
        kind = _source_kind(path)
        score, reasons = score_text(text)
        if kind == "concat":
            # table.concat captures are frequently intermediate decode steps,
            # they are still useful but rank below real chunks.
            score -= 5
            reasons.append("intermediate concat capture")
        if kind == "load":
            score += 12
            reasons.append("passed to load/loadstring (primary payload path)")
        if looks_like_same_file(text, source):
            score -= 100
            reasons.append("identical to the input")
        if source_hash and hashlib.sha1(text.encode("utf-8", "replace")).hexdigest() == source_hash:
            score -= 100
            reasons.append("equals source hash")
        picks.append(PayloadPick(path=path, text=text, score=score, reasons=reasons, source=kind))

    for name, text in extra_texts or ():
        if len(text) < min_chars:
            continue
        score, reasons = score_text(text)
        if looks_like_same_file(text, source):
            score -= 100
            reasons.append("identical to the input")
        picks.append(PayloadPick(path=None, text=text, score=score, reasons=reasons, source=name))

    if not picks:
        return None
    picks.sort(key=lambda p: (p.score, p.length), reverse=True)
    return picks[0]


def rank_payloads(picks: Sequence[PayloadPick]) -> List[PayloadPick]:
    return sorted(picks, key=lambda p: (p.score, p.length), reverse=True)


__all__ = [
    "PayloadPick",
    "looks_like_same_file",
    "pick_payload",
    "printable_ratio",
    "rank_payloads",
    "score_text",
]
