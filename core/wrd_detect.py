"""Format detection for obfuscated Lua sources.

Detection is *structural* first and AST-based second:

* WRD v1.0.0 files are single-line, hundreds-of-kilobytes monsters that most
  Lua parsers (and every pure-python recursive descent parser) struggle with.
  The structural pass therefore runs on a **masked** copy of the source - a copy
  where every string and comment body has been blanked out - so the regular
  expressions cannot be confused by string contents, and it stays O(n) with a
  ``str.find`` driven scanner.
* When :mod:`luaparser` is installed (``pip install luaparser``) the AST pass
  adds precise statement statistics.  The TZ asked for ``luaparse``; that
  package does **not** exist on PyPI (404), ``luaparser`` is its maintained
  equivalent, so both import names are probed and the AST pass is optional.

The detector never raises on malformed input: it returns a report with
``is_obfuscated=False`` and a ``reason``.
"""

from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

# ------------------------------------------------------------------ markers

WRD_HEADER_RE = re.compile(r"--\[\[\s*v?([0-9][0-9A-Za-z._-]*)\s+https?://wearedevs\.net/obfuscator\s*\]\]")
WRD_HEADER_ANY_RE = re.compile(r"wearedevs\.net/obfuscator")
WRD_RETURN_WRAPPER_RE = re.compile(r"return\s*\(\s*function\s*\(\s*\.\.\.\s*\)")
WRD_TAIL_RE = re.compile(r"end\s*\)\s*\(\s*\.\.\.\s*\)\s*$")

# Other obfuscators: only identification for now (registry placeholders).
OTHER_FORMATS: Tuple[Tuple[str, re.Pattern], ...] = (
    ("luraph", re.compile(r"Luraph|LPH_|lph_|--\[\[\s*Luraph", re.I)),
    ("moonsec", re.compile(r"moonsec|MoonSec|--\[\[\s*Moonsec", re.I)),
    ("ironbrew", re.compile(r"ironbrew|IronBrew", re.I)),
    ("prometheus", re.compile(r"prometheus", re.I)),
)

ESCAPED_DECIMAL_STRING_RE = re.compile(r'"((?:\\\d{1,3}){4,})"')
#: A pool resolver: ``local function h(i) return j[i - 42384] end`` or the
#: anonymous form ``local h = function(i) return j[i - 42384] end``.
#: Groups: 1|2 = name (named form | anonymous form), 3|4 = parameter,
#: 5 = pool variable, 6 = operator, 7 = offset expression.
RESOLVER_DEF_RE = re.compile(
    r"local\s+(?:function\s+([A-Za-z_]\w*)\s*\(\s*([A-Za-z_]\w*)\s*\)"
    r"|([A-Za-z_]\w*)\s*=\s*function\s*\(\s*([A-Za-z_]\w*)\s*\))"
    r"\s*return\s+([A-Za-z_]\w*)\s*\[\s*([A-Za-z_]\w*)\s*([+\-])\s*(.+?)\s*\]\s*end",
    re.S,
)
DISPATCH_LOOP_RE = re.compile(r"while\s+[A-Za-z_]\w*\s+do")
LOADSTRING_NAME_RE = re.compile(r"\bloadstring\b|\bload\s*\(")


# ------------------------------------------------------------------ masking


def mask_lua(source: str) -> str:
    """Return a copy of ``source`` where strings and comments are blanked.

    The copy has exactly the same length as the input so that offsets found in
    the mask can be used on the original text.
    """
    out = list(source)
    n = len(source)
    i = 0
    while i < n:
        ch = source[i]
        if ch == "-" and source.startswith("--", i):
            # comment: line or long
            j = i + 2
            long_open = re.match(r"\[(=*)\[", source[j:])
            if long_open:
                close = "]" + long_open.group(1) + "]"
                end = source.find(close, j + long_open.end())
                end = n if end < 0 else end + len(close)
            else:
                end = source.find("\n", j)
                end = n if end < 0 else end
            for k in range(i, end):
                if source[k] != "\n":
                    out[k] = " "
            i = end
            continue
        if ch in "\"'":
            quote = ch
            j = i + 1
            while j < n:
                c = source[j]
                if c == "\\":
                    j += 2
                    continue
                if c == quote:
                    j += 1
                    break
                if c == "\n":
                    break
                j += 1
            for k in range(i, min(j, n)):
                if source[k] != "\n":
                    out[k] = " "
            i = j
            continue
        if ch == "[":
            long_open = re.match(r"\[(=*)\[", source[i:])
            if long_open:
                close = "]" + long_open.group(1) + "]"
                end = source.find(close, i + long_open.end())
                end = n if end < 0 else end + len(close)
                for k in range(i, end):
                    if source[k] != "\n":
                        out[k] = " "
                i = end
                continue
        i += 1
    return "".join(out)


def mask_strings(source: str) -> str:
    """Blank *string literals* only, leaving comments readable.

    ``mask_lua`` blanks comments too, which is exactly wrong for the WRD header:
    the signature ``--[[ v1.0.0 https://wearedevs.net/obfuscator ]]`` lives in a
    long comment, so it has to be matched against a mask that keeps comments.
    String contents are still blanked so that a script merely *mentioning* the
    URL inside a plain string cannot fake a signature.
    """
    out = list(source)
    n = len(source)
    i = 0
    while i < n:
        ch = source[i]
        if ch == "-" and source.startswith("--", i):
            j = i + 2
            long_open = re.match(r"\[(=*)\[", source[j:])
            if long_open:
                close = "]" + long_open.group(1) + "]"
                end = source.find(close, j + long_open.end())
                i = n if end < 0 else end + len(close)
            else:
                end = source.find("\n", j)
                i = n if end < 0 else end
            continue
        if ch in "\"'":
            quote = ch
            j = i + 1
            while j < n:
                c = source[j]
                if c == "\\":
                    j += 2
                    continue
                if c == quote:
                    j += 1
                    break
                if c == "\n":
                    break
                j += 1
            for k in range(i, min(j, n)):
                if source[k] != "\n":
                    out[k] = " "
            i = j
            continue
        if ch == "[":
            long_open = re.match(r"\[(=*)\[", source[i:])
            if long_open:
                close = "]" + long_open.group(1) + "]"
                end = source.find(close, i + long_open.end())
                end = n if end < 0 else end + len(close)
                for k in range(i, end):
                    if source[k] != "\n":
                        out[k] = " "
                i = end
                continue
        i += 1
    return "".join(out)


# ------------------------------------------------------------------ result


@dataclass
class DetectionResult:
    """Outcome of :func:`detect`."""

    is_obfuscated: bool
    format: str = "unknown"
    version: Optional[str] = None
    confidence: float = 0.0
    reason: str = ""
    features: Dict[str, object] = field(default_factory=dict)
    reasons: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)

    def as_dict(self) -> dict:
        return {
            "is_obfuscated": self.is_obfuscated,
            "format": self.format,
            "version": self.version,
            "confidence": round(self.confidence, 3),
            "reason": self.reason,
            "features": {k: v for k, v in self.features.items() if not isinstance(v, (list, dict)) or len(v) < 40},
            "reasons": self.reasons,
            "warnings": self.warnings,
        }

    @property
    def summary(self) -> str:
        if not self.is_obfuscated:
            return f"not obfuscated ({self.reason or 'no known signature'})"
        ver = f" v{self.version}" if self.version else ""
        return f"{self.format}{ver} (confidence {self.confidence:.0%})"


# ------------------------------------------------------------------ ast pass


def _ast_statistics(source: str) -> Tuple[Optional[dict], Optional[str]]:
    """Optional AST pass.  Returns ``(stats, error)``."""
    parser = None
    for module_name in ("luaparser", "luaparse"):
        try:  # pragma: no cover - depends on optional dependency
            module = __import__(module_name)
        except Exception:
            continue
        parser = module
        break
    if parser is None:
        return None, "luaparser not installed (optional)"

    try:  # pragma: no cover - depends on optional dependency
        import contextlib
        import io

        from luaparser import ast as lua_ast  # type: ignore

        # ANTLR reports lexer noise (the escaped-decimal string pool) straight to
        # stderr; the caller only wants the statistics, not the parser's chatter.
        with contextlib.redirect_stderr(io.StringIO()):
            tree = lua_ast.parse(source)
    except RecursionError:
        return None, "parser recursion limit reached (very large one-liner)"
    except Exception as exc:
        return None, f"{type(exc).__name__}: {exc}"

    try:  # pragma: no cover - depends on optional dependency
        names = [type(node).__name__ for node in lua_ast.walk(tree)]
    except Exception:
        return None, "AST walk failed"
    counts = {name: names.count(name) for name in set(names)}
    return counts, None


# ------------------------------------------------------------------ detect


def detect(source: str, *, deep: bool = True) -> DetectionResult:
    """Analyse ``source`` and describe which obfuscator produced it."""
    source = source or ""
    size = len(source.encode("utf-8", "replace"))
    features: Dict[str, object] = {"bytes": size, "sha1": hashlib.sha1(source.encode("utf-8", "replace")).hexdigest()}
    reasons: List[str] = []
    warnings: List[str] = []

    mask = mask_lua(source)
    features["masked"] = True
    # comments survive in this mask, strings do not: see mask_strings()
    comment_mask = mask_strings(source)

    header = WRD_HEADER_RE.search(comment_mask) or WRD_HEADER_ANY_RE.search(comment_mask)
    version = None
    if header:
        m = WRD_HEADER_RE.search(comment_mask)
        if m:
            version = m.group(1)

    pool_literals = ESCAPED_DECIMAL_STRING_RE.findall(source)
    features["escaped_decimal_literals"] = len(pool_literals)

    resolvers = []
    for m in RESOLVER_DEF_RE.finditer(mask):
        name, param, pool, indexed, op, offset = (
            m.group(1) or m.group(3), m.group(2) or m.group(4), m.group(5), m.group(6), m.group(7), m.group(8)
        )
        if param != indexed:
            continue  # indexing something that is not the parameter: not a pool resolver
        resolvers.append({"name": name, "param": param, "pool": pool, "op": op, "offset": offset.strip()[:60]})
    features["resolvers"] = resolvers
    features["dispatch_loops"] = len(DISPATCH_LOOP_RE.findall(mask))
    features["has_loadstring_name"] = bool(LOADSTRING_NAME_RE.search(mask))

    # ---- WRD (WeAreDevs) ----
    score = 0.0
    if header:
        score += 0.45
        reasons.append("wearedevs.net/obfuscator header")
    if WRD_RETURN_WRAPPER_RE.search(mask):
        score += 0.2
        reasons.append("a payload starting with return(function(...)")
    if WRD_TAIL_RE.search(mask):
        score += 0.1
        reasons.append("wrapper invoked with `...` at end of file")
    if len(pool_literals) >= 50:
        score += 0.2
        reasons.append(f"escaped-decimal string pool ({len(pool_literals)} entries)")
    elif len(pool_literals) >= 8:
        score += 0.1
        reasons.append(f"small escaped-decimal string pool ({len(pool_literals)} entries)")
    if resolvers:
        score += 0.15
        reasons.append("pool resolver function " + ", ".join(r["name"] for r in resolvers[:3]))
    if features["dispatch_loops"]:
        score += 0.05
        reasons.append(f"{features['dispatch_loops']} dispatch loop(s)")
    if size > 20_000_000:
        warnings.append("source larger than 20 MB: dynamic execution may be slow")

    if deep:
        stats, error = _ast_statistics(source)
        if stats:
            features["ast"] = stats
            features["ast_error"] = None  # always present: callers read it unconditionally
            if stats.get("WhileStatement"):
                score += 0.05
                reasons.append(f"AST: {stats['WhileStatement']} while statements")
        elif error:
            features["ast_error"] = error
            if "recursion" in error:
                warnings.append("AST pass skipped: " + error)

    if score >= 0.45:
        return DetectionResult(
            is_obfuscated=True,
            format="wrd",
            version=version,
            confidence=min(score, 1.0),
            reason="wrd-signature",
            features=features,
            reasons=reasons,
            warnings=warnings,
        )

    # ---- other known formats (routing only) ----
    for name, pattern in OTHER_FORMATS:
        # banners live in comments ("--[[ Luraph v14 ]]"), so comments are kept here
        if pattern.search(comment_mask):
            return DetectionResult(
                is_obfuscated=True,
                format=name,
                confidence=0.4,
                reason=f"{name}-marker",
                features=features,
                reasons=reasons + [f"{name} marker present"],
                warnings=warnings + [f"{name} support is a placeholder (see core/registry.py)"],
            )

    reason = "no known obfuscator signature"
    if len(pool_literals) < 8 and not header:
        reason = "missing string pool / header"
    if features.get("ast_error"):
        warnings.append(f"AST analysis unavailable: {features['ast_error']}")

    return DetectionResult(
        is_obfuscated=False,
        format="unknown",
        confidence=min(score, 0.44),
        reason=reason,
        features=features,
        reasons=reasons,
        warnings=warnings,
    )


def looks_like_wrd(source: str) -> bool:
    """Cheap boolean shortcut used by the registry."""
    return bool(WRD_HEADER_ANY_RE.search(source) or (ESCAPED_DECIMAL_STRING_RE.search(source)
                                                     and WRD_RETURN_WRAPPER_RE.search(source)))


__all__ = ["DetectionResult", "detect", "looks_like_wrd", "mask_lua", "mask_strings"]
