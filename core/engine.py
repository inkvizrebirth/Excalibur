"""Multi-layer recovery engine.

The engine is the part that actually "destroys" an obfuscated file.  For every
layer it tries, in order:

1. static constant/string decoding,
2. family-specific handling (Luraph/MoonSec containers, embedded Lua 5.1
   bytecode),
3. remote payload resolution for thin loaders (Luarmor, ``HttpGet`` chains),
4. the portable Lua backend with a full executor environment,
5. the native Luau worker with the same environment plus pre-fetched bodies,
6. Lua 5.1 bytecode decompilation for anything captured as bytecode.

Whichever step produces a better (larger, protection-free, syntax-valid)
candidate becomes the input of the next layer, up to the configured depth.
"""

from __future__ import annotations

import hashlib
import logging
import re
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Sequence

from core.deobfuscator import deobfuscate_source
from core.emulator import EmulatorResult, LuaEmulator, emulator_available
from core.families import best_family, detect_families, handler_for, scan_embedded_bytecode
from core.injector_env import (
    ExecutorProfile,
    build_http_stub_prelude,
    build_lua_prelude,
    detect_executor_keys,
    get_profile,
)
from core.lua51 import BytecodeError, decompile, is_lua51_bytecode, looks_like_luau_bytecode
from core.protection import inspect_protection
from core.remote_payloads import PayloadFetcher, RemotePayloadError, extract_script_key, extract_urls, is_luarmor
from core.sandbox import Sandbox, SandboxError, SandboxResult

__all__ = [
    "RecoveryEngine",
    "RecoveryResult",
    "LayerRecord",
    "static_decode_is_useful",
]

# A captured chunk only replaces the current input when it is clearly richer
# than the stub that produced it.
MIN_IMPROVEMENT_BYTES = 96


@dataclass(frozen=True)
class LayerRecord:
    index: int
    kind: str
    method: str
    source_bytes: int
    sha256: str
    note: str = ""


@dataclass
class RecoveryResult:
    source: str
    family: str
    version: str | None
    method: str
    partial: bool
    layers: tuple[LayerRecord, ...] = ()
    notes: tuple[str, ...] = ()
    bytecode: bytes | None = None
    bytecode_source: str | None = None
    emulator: EmulatorResult | None = None
    sandbox_results: tuple[SandboxResult, ...] = ()
    fetches: tuple[dict[str, object], ...] = ()
    profile: str = "universal"
    direct: bool = False
    strong: bool = False

    @property
    def layer_count(self) -> int:
        return len(self.layers)


def static_decode_is_useful(before: str, candidate: str) -> bool:
    """True when a constant/string decode is worth showing to the user.

    Decoding a few escapes in an otherwise readable script makes the output
    *less* readable, so it only counts when the input was a machine-made blob
    or when the decode strips a real layer (escapes, hex or a size drop).
    """
    if RecoveryEngine._obfuscation_score(before) >= 0.5:
        return True
    if len(candidate) <= len(before) * 0.8:
        return True
    if "\n" not in before and len(before) > 12:
        # A one-line script is machine output (minified or assembled); folding
        # its constants and re-indenting it is more readable than echoing it.
        return True
    # Escape or hex layers still hide the payload even in short scripts.
    if re.search(r"\\\d{1,3}|0[xX][0-9a-fA-F]{2}\b|\\x[0-9a-fA-F]{2}", before):
        return True
    return False


class RecoveryEngine:
    """Layer-by-layer recovery with per-layer reporting."""

    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        progress: Callable[[float, str], None] | None = None,
        profile: ExecutorProfile | str | None = None,
        allow_network: bool = True,
        script_key: str | None = None,
        use_emulator: bool = True,
        use_native: bool = True,
        sandbox: Sandbox | None = None,
        tools_dir: Path | str | None = None,
        logs_dir: Path | str | None = None,
        format_source: Callable[[str], str] | None = None,
        validate_source: Callable[[str], bool] | None = None,
        max_layers: int = 6,
        max_seconds: float = 120.0,
        emulator_timeout: float = 25.0,
        fetch_max_bytes: int = 8 * 1024 * 1024,
        max_fetches: int = 12,
    ):
        self.logger = logger or logging.getLogger("protez")
        self.progress = progress or (lambda _percent, _stage: None)
        self.profile = profile if isinstance(profile, ExecutorProfile) else get_profile(
            profile if isinstance(profile, str) else None
        )
        self.allow_network = bool(allow_network)
        self.script_key = script_key or None
        self.use_emulator = bool(use_emulator)
        self.use_native = bool(use_native)
        self.sandbox = sandbox
        self.tools_dir = Path(tools_dir) if tools_dir else None
        self.logs_dir = Path(logs_dir) if logs_dir else None
        self.format_source = format_source or (lambda text: text)
        self.validate_source = validate_source or (lambda text: bool(text.strip()))
        self.max_layers = max(1, int(max_layers))
        self.max_seconds = float(max_seconds)
        self.emulator_timeout = float(emulator_timeout)
        self.fetch_max_bytes = int(fetch_max_bytes)
        self.max_fetches = int(max_fetches)

    # ------------------------------------------------------------------
    def recover(self, source: str, *, source_name: str = "input") -> RecoveryResult:
        started = time.monotonic()
        deadline = started + self.max_seconds
        notes: list[str] = []
        layers: list[LayerRecord] = []
        sandbox_results: list[SandboxResult] = []
        emulator_result: EmulatorResult | None = None
        bytecode: bytes | None = None
        bytecode_source: str | None = None
        static_bytecode_found = False
        strong = False

        detected_keys = detect_executor_keys(source)
        if detected_keys:
            notes.append("executor probes detected: " + ", ".join(detected_keys[:6]))

        fetcher = PayloadFetcher(
            enabled=self.allow_network,
            logger=self.logger,
            max_bytes=self.fetch_max_bytes,
            max_fetches=self.max_fetches,
        )
        extracted_key = self.script_key or extract_script_key(source)
        if is_luarmor(source):
            notes.append("Luarmor private-library loader detected")

        current = source
        seen: set[str] = {self._digest(source)}
        family_match = best_family(source)
        method = "multi-layer recovery"
        partial = True
        depth = 0

        while depth < self.max_layers and time.monotonic() < deadline:
            depth += 1
            improved = False

            # 1. static decoding
            try:
                decoded = deobfuscate_source(current)
            except Exception as exc:  # noqa: BLE001 - decoding must never abort a run
                self.logger.debug("Static decoding stopped: %s", exc)
                decoded = None
            if decoded is not None and decoded.changed and decoded.source.strip():
                candidate = decoded.source
                if self._digest(candidate) not in seen:
                    before = current
                    # Rewriting a script that was already plain Luau only makes
                    # it less readable, so a static decode is adopted when the
                    # input is a machine-made blob or when the decode strips a
                    # real layer (escapes, hex, base64).
                    if static_decode_is_useful(before, candidate):
                        current = candidate
                        seen.add(self._digest(current))
                        layers.append(
                            self._record(len(layers) + 1, "static", "constant/string decoding", current)
                        )
                        if self._obfuscation_score(before) >= 0.5:
                            strong = True
                        improved = True

            family_match = best_family(current) or family_match
            self.progress(min(60.0, 10.0 + depth * 6), f"LAYER {depth}")

            # 2. remote payload (thin loader or private library)
            if self.allow_network and self._needs_remote(current):
                remote = self._resolve_remote(current, fetcher, script_key=extracted_key)
                if remote is not None:
                    candidate, remote_note = remote
                    if self._digest(candidate) not in seen:
                        current = candidate
                        seen.add(self._digest(current))
                        layers.append(self._record(len(layers) + 1, "remote", remote_note, current))
                        notes.append(f"layer {depth}: {remote_note}")
                        strong = True
                        improved = True
                        continue

            # 3. embedded Lua 5.1 bytecode inside the current text
            embedded = scan_embedded_bytecode(current)
            if embedded is not None:
                bytecode = embedded
                static_bytecode_found = True
                recovered = self._decompile(embedded)
                if recovered:
                    bytecode_source = recovered
                    strong = True
                    if "embedded Lua 5.1 bytecode decompiled" not in notes:
                        notes.append("embedded Lua 5.1 bytecode decompiled")

            # 4. portable backend
            if self.use_emulator and emulator_available() and time.monotonic() < deadline:
                self.progress(min(70.0, 16.0 + depth * 8), "EMULATE")
                emulator_result = self._run_emulator(current, fetcher)
                if emulator_result is not None and emulator_result.status != "completed":
                    self.logger.info(
                        "Portable backend status: %s%s",
                        emulator_result.status,
                        f" ({emulator_result.error})" if emulator_result.error else "",
                    )
                if emulator_result is not None and emulator_result.captures:
                    self.logger.info(
                        "Portable backend captured %s chunk(s)", len(emulator_result.captures)
                    )
                candidate, candidate_note, captured_bytecode, captured_source = self._best_capture(
                    emulator_result, current
                )
                if captured_bytecode is not None and bytecode is None:
                    bytecode = captured_bytecode
                if candidate is not None and self._digest(candidate) not in seen:
                    current = candidate
                    seen.add(self._digest(current))
                    layers.append(self._record(len(layers) + 1, "emulated", candidate_note, current))
                    notes.append(f"layer {depth}: {candidate_note}")
                    strong = True
                    improved = True
                    continue
                if captured_source and bytecode_source is None:
                    bytecode_source = captured_source
                    strong = True

            # 5. native worker with pre-fetched responses
            if self.use_native and self.sandbox is not None and time.monotonic() < deadline:
                self.progress(min(80.0, 24.0 + depth * 8), "SANDBOX")
                native = self._run_native(current, fetcher)
                if native is not None:
                    sandbox_results.append(native)
                    candidate, candidate_note = self._best_sandbox_capture(native, current)
                    if candidate is not None and self._digest(candidate) not in seen:
                        current = candidate
                        seen.add(self._digest(current))
                        layers.append(self._record(len(layers) + 1, "native", candidate_note, current))
                        notes.append(f"layer {depth}: {candidate_note}")
                        strong = True
                        improved = True
                        continue

            if not improved:
                break

        # Choose the final body: the recovered bytecode source wins when it is
        # richer than the current candidate, otherwise keep the current text.
        final_source = current
        from_bytecode = False
        if bytecode_source and static_bytecode_found:
            # The input only rebuilds a chunk that we already lifted: show the
            # lifted code instead of the byte-array loader that wraps it.
            final_source = bytecode_source
            from_bytecode = True
            notes.append("the input built this chunk from a byte array; showing the lifted code")
        elif bytecode_source and len(bytecode_source) > len(current) * 1.2:
            final_source = bytecode_source
            from_bytecode = True
            notes.append("bytecode pseudocode was richer than the captured source layer")
        elif bytecode_source and self._looks_like_stub(current):
            final_source = bytecode_source
            from_bytecode = True
            notes.append("input was a stub; showing decompiled bytecode")

        protection = inspect_protection(source)
        is_stub = self._looks_like_stub(final_source)
        partial = bool(protection is not None and is_stub) or (
            not self.validate_source(final_source) and bytecode_source is None
        )
        if from_bytecode:
            # Register names and idioms of lifted bytecode are synthetic, so the
            # result is honestly labelled as an approximation.
            notes.append("lifted from bytecode: register and local names are synthetic")
            partial = True
        if protection is not None:
            notes.append(f"{protection.display_name} signature present in the input")
        if fetcher.records:
            for record in fetcher.records:
                if record.status != "fetched" and record.status != "cached":
                    notes.append(f"remote fetch failed: {record.detail or record.status}")

        self.progress(88, "FORMAT")
        if from_bytecode:
            # The lifter already emits one statement per line: re-flowing it
            # through the whitespace formatter only merges statements.
            notes.append("listing kept verbatim because it was lifted from bytecode")
        else:
            try:
                final_source = self.format_source(final_source)
            except Exception as exc:  # noqa: BLE001
                self.logger.debug("Formatting skipped: %s", exc)
                notes.append("formatting was skipped because the recovered code did not validate")

        return RecoveryResult(
            source=final_source,
            family=(family_match.display_name if family_match else "unknown"),
            version=family_match.version if family_match else None,
            method=method,
            partial=partial,
            layers=tuple(layers),
            notes=tuple(notes),
            bytecode=bytecode,
            bytecode_source=bytecode_source,
            emulator=emulator_result,
            sandbox_results=tuple(sandbox_results),
            fetches=tuple(fetcher.summary()),
            profile=self.profile.key,
            direct=not layers,
            strong=strong or (from_bytecode and static_bytecode_found),
        )

    # ------------------------------------------------------------------
    # Layer helpers
    # ------------------------------------------------------------------
    @staticmethod
    def _digest(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8", "replace")).hexdigest()

    @staticmethod
    def _record(index: int, kind: str, method: str, source: str) -> LayerRecord:
        return LayerRecord(
            index=index,
            kind=kind,
            method=method,
            source_bytes=len(source.encode("utf-8", "replace")),
            sha256=hashlib.sha256(source.encode("utf-8", "replace")).hexdigest()[:16],
        )

    @staticmethod
    def _obfuscation_score(source: str) -> float:
        """Rough "this is a machine-generated blob" score in 0..1."""
        sample = source[:200_000]
        if not sample:
            return 0.0
        interesting = sum(
            1
            for character in sample
            if character.isdigit() or character in "\\x%$&*^~"
        )
        lines = sample.count("\n") + 1
        average_line = len(sample) / lines
        density = interesting / len(sample)
        return min(1.0, density + (0.15 if average_line > 400 else 0.0))

    def _candidate_is_better(self, candidate: str, current: str) -> bool:
        """Decide whether a captured chunk is a real improvement over the input."""
        if not candidate.strip() or len(candidate.strip()) < 24:
            return False
        if self._digest(candidate) == self._digest(current):
            return False
        try:
            if inspect_protection(candidate) is not None:
                return False
        except Exception:  # noqa: BLE001
            pass
        if len(candidate) > len(current) + MIN_IMPROVEMENT_BYTES:
            return True
        current_score = self._obfuscation_score(current)
        candidate_score = self._obfuscation_score(candidate)
        if current_score >= 0.18 and candidate_score < current_score * 0.6:
            return True
        return self._looks_like_stub(current) and len(candidate) > 64

    @staticmethod
    def _looks_like_stub(source: str) -> bool:
        if len(source) > 6000:
            return False
        lowered = source.lower()
        return "loadstring" in lowered or "httpget" in lowered or "request(" in lowered

    def _needs_remote(self, source: str) -> bool:
        lowered = source.lower()
        if is_luarmor(source):
            return True
        if "httpget" in lowered or "loadstring(" in lowered or "http_request" in lowered or "request(" in lowered:
            return bool(extract_urls(source, limit=8))
        return False

    def _resolve_remote(
        self,
        source: str,
        fetcher: PayloadFetcher,
        *,
        script_key: str | None,
    ) -> tuple[str, str] | None:
        if not fetcher.enabled:
            return None
        urls = [url for url in extract_urls(source, limit=12) if self._is_payload_like(url)]
        if not urls:
            return None
        best: tuple[int, str] | None = None
        for url in urls:
            if time.monotonic() > self._deadline_guard():
                break
            try:
                body = fetcher.fetch(url)
            except RemotePayloadError as exc:
                self.logger.info("Remote payload skipped (%s): %s", url[:80], exc)
                continue
            if not body.strip():
                continue
            if best is None or len(body) > best[0]:
                best = (len(body), body)
        if best is None:
            return None
        body = best[1]
        target = self._digest(body)
        _ = target
        note = f"payload downloaded ({len(body):,} bytes)"
        if is_luarmor(source):
            note = f"Luarmor payload downloaded ({len(body):,} bytes)"
        return body, note

    @staticmethod
    def _is_payload_like(url: str) -> bool:
        lowered = url.lower()
        if any(lowered.endswith(extension) for extension in (".png", ".jpg", ".jpeg", ".gif", ".mp3", ".ico", ".css")):
            return False
        return True

    def _deadline_guard(self) -> float:
        return time.monotonic() + self.max_seconds

    def _run_emulator(self, source: str, fetcher: PayloadFetcher) -> EmulatorResult | None:
        try:
            emulator = LuaEmulator(
                profile=self.profile,
                script_key=self.script_key,
                timeout_seconds=self.emulator_timeout,
                http_bridge=fetcher.bridge if fetcher.enabled else None,
                logger=self.logger,
            )
            return emulator.run(source)
        except Exception as exc:  # noqa: BLE001 - the portable backend is optional
            self.logger.info("Portable backend skipped: %s", exc)
            return None

    def _run_native(self, source: str, fetcher: PayloadFetcher) -> SandboxResult | None:
        assert self.sandbox is not None
        prelude = build_lua_prelude(self.profile, script_key=self.script_key)
        responses = dict(fetcher.responses) if fetcher.enabled else {}
        if responses:
            prelude += "\n" + build_http_stub_prelude(responses)
        else:
            # First pass: let the worker report which URLs the loader wants.
            prelude += "\n" + build_http_stub_prelude({})
        try:
            return self.sandbox.run(source, source_name="layer", prelude=prelude)
        except SandboxError as exc:
            self.logger.info("Native worker unavailable: %s", exc)
            return None
        except Exception as exc:  # noqa: BLE001
            self.logger.info("Native worker skipped: %s", exc)
            return None

    def _captures_from_sandbox(self, result: SandboxResult) -> list[tuple[str, str]]:
        """Return (kind, text) pairs captured by the native worker."""
        paths = result.captured_paths or ((result.captured_path,) if result.captured_path else ())
        captures: list[tuple[str, str]] = []
        for index, capture in enumerate(result.captures):
            path = paths[index] if index < len(paths) else None
            if path is None:
                continue
            try:
                text = path.read_text(encoding="utf-8", errors="replace")
            except OSError:
                continue
            if text.strip():
                captures.append((capture.kind, text))
        return captures

    def _best_capture(
        self,
        result: EmulatorResult | None,
        current: str,
    ) -> tuple[str | None, str, bytes | None, str | None]:
        """Pick the best payload from a portable-backend run."""
        if result is None:
            return None, "", None, None
        best_source: str | None = None
        best_note = ""
        captured_bytecode: bytes | None = None
        bytecode_source: str | None = None
        for capture in result.captures:
            if capture.kind not in {"loadstring", "load", "bytecode"}:
                continue
            text = capture.text
            # A captured chunk may be dumped bytecode rather than source: the
            # portable backend transfers it as latin-1/hex text.
            raw = self._capture_bytes(text)
            if raw is not None:
                captured_bytecode = raw
                recovered = self._decompile(raw)
                if recovered and (bytecode_source is None or len(recovered) > len(bytecode_source)):
                    bytecode_source = recovered
                continue
            if not text.strip() or capture.binary:
                continue
            if looks_like_luau_bytecode(text):
                continue
            if not self._candidate_is_better(text, current):
                continue
            if best_source is None or len(text) > len(best_source):
                best_source = text
                best_note = f"payload captured by the portable Lua backend ({len(text):,} bytes)"
        for capture in result.bytecode:
            raw = self._capture_bytes(capture.text)
            if raw is None:
                continue
            captured_bytecode = raw
            recovered = self._decompile(raw)
            if recovered and (bytecode_source is None or len(recovered) > len(bytecode_source)):
                bytecode_source = recovered
        return best_source, best_note, captured_bytecode, bytecode_source

    def _best_sandbox_capture(
        self,
        result: SandboxResult,
        current: str,
    ) -> tuple[str | None, str]:
        best: str | None = None
        note = ""
        for kind, text in self._captures_from_sandbox(result):
            if kind.lower() not in {"loadstring", "load"}:
                continue
            if not text.strip() or text.lstrip().startswith("\x1b"):
                continue
            if not self._candidate_is_better(text, current):
                continue
            if best is None or len(text) > len(best):
                best = text
                note = f"payload captured by the native Luau worker ({len(text):,} bytes)"
        return best, note

    @staticmethod
    def _capture_bytes(text: str) -> bytes | None:
        if not text:
            return None
        raw = text.encode("latin-1", "replace")
        if is_lua51_bytecode(raw):
            return raw
        return None

    def _decompile(self, bytecode: bytes) -> str | None:
        try:
            return decompile(bytecode)
        except BytecodeError as exc:
            self.logger.info("Bytecode layout unsupported: %s", exc)
        except Exception as exc:  # noqa: BLE001
            self.logger.info("Bytecode recovery failed: %s", exc)
        return None

    def recover_bytecode(self, bytecode: bytes) -> RecoveryResult:
        """Bytecode input (``.luac``/``.lbc``) route: decompile directly."""
        if looks_like_luau_bytecode(bytecode) and not is_lua51_bytecode(bytecode):
            return RecoveryResult(
                source="",
                family="Luau bytecode",
                version=None,
                method="unsupported bytecode container",
                partial=True,
                notes=(
                    "Luau bytecode is compiled output; use the source-level route or a native Luau "
                    "worker for this container",
                ),
                profile=self.profile.key,
            )
        recovered = self._decompile(bytecode)
        if recovered is None:
            return RecoveryResult(
                source="",
                family="Lua 5.1 bytecode",
                version=None,
                method="bytecode decompilation failed",
                partial=True,
                notes=("the bytecode container could not be parsed",),
                profile=self.profile.key,
            )
        formatted = recovered
        try:
            formatted = self.format_source(recovered)
        except Exception:  # noqa: BLE001
            formatted = recovered
        return RecoveryResult(
            source=formatted,
            family="Lua 5.1 bytecode",
            version=None,
            method="Lua 5.1 bytecode to structured pseudocode",
            partial=True,
            notes=(
                "decompiled from bytecode: names and comments are unavailable",
                "the output is pseudocode and may not run unchanged",
            ),
            bytecode=bytecode,
            bytecode_source=recovered,
            profile=self.profile.key,
        )
