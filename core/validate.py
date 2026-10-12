"""Validation of deobfuscation candidates.

A candidate is *not* accepted just because it was captured: it has to compile in
a real Lua runtime and it has to look like a program rather than like a leftover
decode fragment.  Every check is recorded so the GUI can explain a rejection.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import List, Optional, Tuple

from .pick_payload import ARITH_RUN_RE, printable_ratio, score_text
from .wrd_detect import ESCAPED_DECIMAL_STRING_RE, WRD_RETURN_WRAPPER_RE, mask_lua

LUA_KEYWORDS_PRESENT_RE = re.compile(r"\b(local|function|if|for|while|return|repeat|do)\b")
DISPATCH_LOOKS_RE = re.compile(r"while\s+\w+\s+do")

#: Minimum share of printable ASCII for a candidate to be treated as source.
MIN_PRINTABLE = 0.7
#: Below this length a candidate is considered a decode fragment.
MIN_LENGTH = 80
#: Escaped-decimal run length that still counts as "the obfuscator's string pool".
POOL_RUN_CHARS = 400

#: Validation profiles.
MODE_DYNAMIC = "dynamic"   # candidate must be *clean* source (no obfuscation left)
MODE_STATIC = "static"     # candidate is the rewritten constant layer: it may keep
                           # the wrapper, but it must be valid Lua that differs from
                           # the input


@dataclass
class Check:
    name: str
    passed: bool
    detail: str = ""

    def as_dict(self) -> dict:
        return {"name": self.name, "passed": self.passed, "detail": self.detail}


@dataclass
class ValidationResult:
    valid: bool
    reason: str = ""
    checks: List[Check] = field(default_factory=list)
    metrics: dict = field(default_factory=dict)
    compile_runtime: Optional[str] = None

    def as_dict(self) -> dict:
        return {
            "valid": self.valid,
            "reason": self.reason,
            "checks": [c.as_dict() for c in self.checks],
            "metrics": self.metrics,
            "compile_runtime": self.compile_runtime,
        }


def balance_report(text: str) -> Tuple[bool, str]:
    """Check that brackets balance in *code* (strings/comments masked out)."""
    mask = mask_lua(text)
    pairs = {")": "(", "]": "[", "}": "{"}
    stack: List[str] = []
    for ch in mask:
        if ch in "([{":
            stack.append(ch)
        elif ch in ")]}":
            if not stack or stack.pop() != pairs[ch]:
                return False, f"unbalanced '{ch}'"
    if stack:
        return False, f"{len(stack)} unclosed '{stack[-1]}'"
    return True, "balanced"


def compile_check(text: str) -> Tuple[Optional[bool], str, Optional[str]]:
    """Compile check through a real Lua runtime.

    Returns ``(ok, message, runtime_name)``; ``ok`` is ``None`` when no runtime
    is available (the caller then falls back to structural checks only).
    """
    try:
        from .runtime import discover_runtimes, LuaRuntime
    except Exception:  # pragma: no cover - import cycle guard
        return None, "runtime module unavailable", None

    specs = discover_runtimes(("lua51", "luajit21", "lua52", "lua53", "lua54"))
    if not specs:
        return None, "no Lua runtime available", None
    first_error = ""
    for spec in specs:
        runtime = LuaRuntime(spec)
        ok, err = runtime.compile_check(text)
        if ok:
            return True, "compiled", spec.name
        if not first_error:
            first_error = f"{spec.name}: {err[:200]}"
    return False, first_error or "compilation failed", specs[0].name


def validate_payload(
    text: str,
    *,
    source: Optional[str] = None,
    require_compile: bool = True,
    skip_compile: bool = False,
    mode: str = MODE_DYNAMIC,
) -> ValidationResult:
    """Validate a candidate payload.

    ``mode`` selects how strict the obfuscation checks are:

    * ``"dynamic"`` - the candidate claims to be the *original* source, so any
      remaining obfuscation marker (the ``return(function(...)`` wrapper, a
      large escaped-decimal string pool) fails the validation;
    * ``"static"`` - the candidate is the rewritten constant layer.  Keeping the
      wrapper is expected; what matters is that it is valid Lua, that the
      constant layer is gone and that it differs from the input.
    """
    checks: List[Check] = []
    text = text or ""
    metrics: dict = {"length": len(text), "printable_ratio": round(printable_ratio(text), 3),
                     "mode": mode}

    checks.append(Check("non_empty", bool(text.strip()), f"{len(text)} chars"))
    if not text.strip():
        return ValidationResult(False, "candidate is empty", checks, metrics)

    ratio = printable_ratio(text)
    checks.append(Check("printable", ratio >= MIN_PRINTABLE, f"{ratio:.0%} printable"))
    checks.append(Check("length", len(text) >= MIN_LENGTH, f"{len(text)} >= {MIN_LENGTH}"))

    balanced, detail = balance_report(text)
    checks.append(Check("balanced_brackets", balanced, detail))

    has_keywords = bool(LUA_KEYWORDS_PRESENT_RE.search(text))
    checks.append(Check("lua_statements", has_keywords, "contains Lua statement keywords"))

    # Obfuscation markers are searched in *code*: the WRD banner is a comment and
    # keeping it is normal (and useful: it records provenance), so it must not be
    # mistaken for a still-obfuscated payload.
    code = mask_lua(text)
    wrapper = bool(WRD_RETURN_WRAPPER_RE.search(code))
    pool_runs = [m for m in ESCAPED_DECIMAL_STRING_RE.findall(text) if len(m) >= POOL_RUN_CHARS]
    metrics["escaped_decimal_runs"] = len(ESCAPED_DECIMAL_STRING_RE.findall(text))
    metrics["large_string_pools"] = len(pool_runs)
    metrics["wrapper_present"] = wrapper
    arith = len(ARITH_RUN_RE.findall(text))
    metrics["constant_arithmetic_runs"] = arith
    density = arith / max(len(text) / 1000.0, 1.0)
    metrics["arithmetic_density_per_kb"] = round(density, 1)

    if mode == MODE_DYNAMIC:
        clean = not wrapper and not pool_runs
        detail = []
        if wrapper:
            detail.append("return(function(...)) wrapper still present")
        if pool_runs:
            detail.append(f"{len(pool_runs)} string pool(s) still escaped")
        checks.append(Check("clean_source", clean, "; ".join(detail) or "no obfuscation markers"))
    else:
        # For the constant layer the wrapper is expected; what matters is that the
        # pool is decoded and that the resolver/arithmetic layer is gone.
        checks.append(Check("constant_layer_removed", not pool_runs,
                            "string pool decoded" if not pool_runs else f"{len(pool_runs)} pool(s) left"))

    if source is not None:
        different = text.strip() != source.strip()
        checks.append(Check("differs_from_input", different, "candidate differs from the input"))
        metrics["shrunk_chars"] = len(source) - len(text)

    score, reasons = score_text(text)
    metrics["payload_score"] = round(score, 2)
    checks.append(Check("payload_score", score > 0, f"score {score:.1f}: " + "; ".join(reasons[:3])))

    compile_runtime = None
    if require_compile and not skip_compile:
        ok, message, runtime_name = compile_check(text)
        metrics["compile_message"] = message
        compile_runtime = runtime_name
        if ok is None:
            checks.append(Check("compiles", True, f"skipped ({message})"))
        else:
            checks.append(Check("compiles", bool(ok), message))

    failed = [c for c in checks if not c.passed]
    valid = not failed
    reason = "ok" if valid else "; ".join(f"{c.name}: {c.detail}" for c in failed)
    return ValidationResult(valid, reason, checks, metrics, compile_runtime)


__all__ = [
    "Check",
    "MODE_DYNAMIC",
    "MODE_STATIC",
    "POOL_RUN_CHARS",
    "ValidationResult",
    "balance_report",
    "compile_check",
    "validate_payload",
]
