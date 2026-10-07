"""Bounded, local-cached retrieval of payloads an obfuscated loader asks for.

Private libraries such as Luarmor, Linkvertise-style key systems and plain
``loadstring(game:HttpGet(url))`` loaders keep the real script behind an HTTP
hop.  This module resolves those hops *as data*: an allow-listed URL set is
built statically from the input, every response is size-capped and cached
under ``logs/remote_cache``, and nothing is ever executed here.

Two consumers use it:

* :class:`PayloadFetcher` itself, for the static path and for the two-pass
  native worker (discover URLs, then replay with the pre-fetched bodies).
* :meth:`PayloadFetcher.bridge`, exposed to the Python-side Lua emulator as
  ``__protez_http`` so a loader can run its own request logic.
"""

from __future__ import annotations

import base64
import hashlib
import json
import logging
import re
import time
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable, Mapping

from core.runtime_paths import LOGS_DIR
from core.version import VERSION

MAX_REMOTE_PAYLOAD_BYTES = 8 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 20.0
DEFAULT_MAX_FETCHES = 16
ROBLOX_USER_AGENT = "Roblox/WinInet"
PROTEZ_USER_AGENT = f"Protez/{VERSION} (payload resolver)"

_URL_RE = re.compile(r"(?i)\bhttps?://[^\s\"'<>`\\]+")
_LUARMOR_LOADER_RE = re.compile(
    r"(?i)https?://api\.luarmor\.(?:net|cc|xyz)/files/v[0-9]+/loaders/([0-9a-f]{16,64})\.lua"
)
_LUARMOR_API_RE = re.compile(r"(?i)https?://api\.luarmor\.(?:net|cc|xyz)/v[0-9]+/")
_SCRIPT_KEY_RE = re.compile(
    r"""(?i)(?:^|[^A-Za-z0-9_])script_key\s*=\s*(?P<quote>["'])(?P<value>[^"'\r\n]{4,512})(?P=quote)"""
)
_HWID_HINTS = ("hwid", "hardware", "identifier")

_ROBLOX_HEADER_HOSTS = (
    "luarmor.net",
    "luarmor.cc",
    "luarmor.xyz",
    "linkvertise.com",
    "keyrblx.com",
    "pandadevelopment.net",
    "gateway.platoboost.com",
    "roblox.com",
)


class RemotePayloadError(RuntimeError):
    """A requested payload could not be retrieved safely."""


@dataclass(frozen=True)
class FetchRecord:
    url: str
    size_bytes: int
    status: str
    cached: bool
    detail: str = ""


def extract_script_key(source: str) -> str | None:
    """Return ``script_key = "..."`` when a loader carries its own key."""
    if not isinstance(source, str):
        return None
    match = _SCRIPT_KEY_RE.search(source)
    if match is None:
        return None
    value = match.group("value").strip()
    return value or None


def extract_urls(source: str, *, limit: int = 64) -> tuple[str, ...]:
    """Collect HTTP(S) URLs that appear in string literals or raw text."""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    seen: list[str] = []
    for match in _URL_RE.finditer(source):
        candidate = match.group(0).rstrip(".,;:!?)]}\"'")
        if candidate and candidate not in seen:
            seen.append(candidate)
        if len(seen) >= limit:
            break
    return tuple(seen)


def luarmor_loader_id(source: str) -> str | None:
    """Extract the Luarmor loader identifier from a loader URL."""
    match = _LUARMOR_LOADER_RE.search(source or "")
    return match.group(1) if match else None


def is_luarmor(source: str) -> bool:
    return bool(_LUARMOR_LOADER_RE.search(source or "") or _LUARMOR_API_RE.search(source or ""))


def looks_like_loader(source: str) -> bool:
    """Heuristic: is this a thin loader that fetches its payload?"""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    lowered = source.lower()
    fetch_hint = any(
        token in lowered
        for token in ("httpget", "request(", "http_request", "https://", "loadstring(", "load(")
    )
    if not fetch_hint:
        return False
    return len(source) < 200_000 or lowered.count("http") > 0


def _is_roblox_host(host: str) -> bool:
    return any(host == item or host.endswith("." + item) for item in _ROBLOX_HEADER_HOSTS)


class PayloadFetcher:
    """Allow-listed, cached, size-capped text fetcher."""

    def __init__(
        self,
        *,
        enabled: bool = True,
        logger: logging.Logger | None = None,
        cache_dir: Path | str | None = None,
        timeout: float = DEFAULT_TIMEOUT_SECONDS,
        max_bytes: int = MAX_REMOTE_PAYLOAD_BYTES,
        max_fetches: int = DEFAULT_MAX_FETCHES,
        allowed_hosts: Iterable[str] | None = None,
        fetcher: Callable[[str], str] | None = None,
    ):
        self.enabled = bool(enabled)
        self.logger = logger or logging.getLogger("protez")
        self.cache_dir = Path(cache_dir) if cache_dir else LOGS_DIR / "remote_cache"
        self.timeout = float(timeout)
        self.max_bytes = int(max_bytes)
        self.max_fetches = int(max_fetches)
        self.allowed_hosts = tuple(host.lower() for host in (allowed_hosts or ()))
        self._fetcher = fetcher
        self._records: list[FetchRecord] = []
        self._responses: dict[str, str] = {}
        self._count = 0

    # ------------------------------------------------------------------
    # Introspection
    # ------------------------------------------------------------------
    @property
    def records(self) -> tuple[FetchRecord, ...]:
        return tuple(self._records)

    @property
    def responses(self) -> Mapping[str, str]:
        return dict(self._responses)

    @property
    def fetch_count(self) -> int:
        return self._count

    def summary(self) -> list[dict[str, object]]:
        return [
            {
                "url": record.url,
                "size_bytes": record.size_bytes,
                "status": record.status,
                "cached": record.cached,
                "detail": record.detail,
            }
            for record in self._records
        ]

    # ------------------------------------------------------------------
    # Fetching
    # ------------------------------------------------------------------
    def _cache_path(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
        return self.cache_dir / f"{digest}.txt"

    def _cache_meta(self, url: str) -> Path:
        digest = hashlib.sha256(url.encode("utf-8")).hexdigest()[:32]
        return self.cache_dir / f"{digest}.json"

    def _allowed(self, url: str) -> bool:
        try:
            parsed = urllib.parse.urlsplit(url)
        except ValueError:
            return False
        if parsed.scheme.lower() not in {"http", "https"}:
            return False
        host = (parsed.hostname or "").lower()
        if not host:
            return False
        if not self.allowed_hosts:
            return True
        return any(host == item or host.endswith("." + item) for item in self.allowed_hosts)

    def fetch(self, url: str, *, use_roblox_headers: bool | None = None) -> str:
        """Return the text body of ``url`` or raise :class:`RemotePayloadError`."""
        if not self.enabled:
            raise RemotePayloadError("remote payload fetching is disabled")
        if not self._allowed(url):
            raise RemotePayloadError(f"host is not on the payload allow-list: {url[:120]}")
        if self._count >= self.max_fetches:
            raise RemotePayloadError(
                f"payload fetch limit reached ({self.max_fetches} requests per run)"
            )

        cached = self._read_cache(url)
        if cached is not None:
            self._responses[url] = cached
            self._records.append(
                FetchRecord(url=url, size_bytes=len(cached), status="cached", cached=True)
            )
            self.logger.info("Reused cached payload (%s bytes) from %s", f"{len(cached):,}", url)
            return cached

        self._count += 1
        text = self._download(url, use_roblox_headers=use_roblox_headers)
        self._responses[url] = text
        self._write_cache(url, text)
        self._records.append(
            FetchRecord(url=url, size_bytes=len(text), status="fetched", cached=False)
        )
        return text

    def _download(self, url: str, *, use_roblox_headers: bool | None = None) -> str:
        from core.source_input import SourceInputError, fetch_code_url

        if self._fetcher is not None:
            try:
                return self._fetcher(url)
            except Exception as exc:  # noqa: BLE001 - surfaced to the report
                raise RemotePayloadError(f"could not fetch {url[:120]}: {exc}") from exc

        parsed = urllib.parse.urlsplit(url)
        host = (parsed.hostname or "").lower()
        headers = use_roblox_headers if use_roblox_headers is not None else _is_roblox_host(host)
        if not headers:
            try:
                return fetch_code_url(url, timeout=self.timeout, max_bytes=self.max_bytes)
            except SourceInputError as exc:
                raise RemotePayloadError(str(exc)) from exc

        request = urllib.request.Request(
            url,
            headers={
                "User-Agent": ROBLOX_USER_AGENT,
                "Accept": "*/*",
                "Accept-Encoding": "identity",
            },
        )
        try:
            with urllib.request.urlopen(request, timeout=self.timeout) as response:
                declared = int(response.headers.get("Content-Length", "0") or 0)
                if declared > self.max_bytes:
                    raise RemotePayloadError(
                        f"payload is larger than the {self.max_bytes // (1024 * 1024)} MiB limit"
                    )
                payload = bytearray()
                while True:
                    block = response.read(min(64 * 1024, self.max_bytes + 1 - len(payload)))
                    if not block:
                        break
                    payload.extend(block)
                    if len(payload) > self.max_bytes:
                        raise RemotePayloadError(
                            f"payload is larger than the {self.max_bytes // (1024 * 1024)} MiB limit"
                        )
        except RemotePayloadError:
            raise
        except urllib.error.HTTPError as exc:
            raise RemotePayloadError(f"HTTP {exc.code} while fetching {url[:120]}") from exc
        except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
            reason = getattr(exc, "reason", exc)
            raise RemotePayloadError(f"could not fetch {url[:120]}: {reason}") from exc

        for encoding in ("utf-8-sig", "utf-8", "cp1252"):
            try:
                text = bytes(payload).decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            raise RemotePayloadError("payload is not readable text")
        self.logger.info("Downloaded payload (%s bytes) from %s", f"{len(text):,}", url[:120])
        return text

    # ------------------------------------------------------------------
    # Cache
    # ------------------------------------------------------------------
    def _read_cache(self, url: str) -> str | None:
        payload_path = self._cache_path(url)
        meta_path = self._cache_meta(url)
        if not payload_path.is_file() or not meta_path.is_file():
            return None
        try:
            meta = json.loads(meta_path.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            return None
        if meta.get("url") != url:
            return None
        created = float(meta.get("created", 0) or 0)
        if created and time.time() - created > 24 * 3600:
            return None
        try:
            return payload_path.read_text(encoding="utf-8")
        except OSError:
            return None

    def _write_cache(self, url: str, text: str) -> None:
        try:
            self.cache_dir.mkdir(parents=True, exist_ok=True)
            self._cache_path(url).write_text(text, encoding="utf-8")
            self._cache_meta(url).write_text(
                json.dumps({"url": url, "created": time.time()}, ensure_ascii=False),
                encoding="utf-8",
            )
        except OSError as exc:
            self.logger.debug("Could not cache %s: %s", url[:120], exc)

    # ------------------------------------------------------------------
    # Lua bridge
    # ------------------------------------------------------------------
    def request_bridge(self, options: object) -> dict[str, object]:
        """Callable exposed to the Lua emulator as the ``request`` bridge.

        Loaders post their ``script_key`` (and other secrets) to an API and read
        the payload out of the JSON answer, so the response is handed back as a
        Roblox-shaped ``{StatusCode, StatusMessage, Headers, Body, Success}``
        table instead of a bare body.
        """
        fields = self._as_mapping(options)
        url = str(fields.get("Url") or fields.get("url") or "")
        method = str(fields.get("Method") or fields.get("method") or "GET").upper()
        body = fields.get("Body")
        if not url.lower().startswith(("http://", "https://")):
            return self._empty_response("no url", method)
        try:
            text = self.fetch(url)
        except RemotePayloadError as exc:
            self._records.append(
                FetchRecord(url=url, size_bytes=0, status="failed", cached=False, detail=str(exc))
            )
            self.logger.info("Loader request skipped (%s): %s", url[:100], exc)
            return self._empty_response(str(exc), method)
        except Exception as exc:  # noqa: BLE001 - never let Lua see a Python traceback
            self.logger.info("Loader request failed (%s): %s", url[:100], exc)
            return self._empty_response(str(exc), method)
        payload = text if isinstance(text, str) else str(text)
        self.logger.info(
            "Loader request %s %s -> %s byte(s)%s",
            method,
            url[:100],
            len(payload),
            f" (body {len(body)} byte(s))" if isinstance(body, str) and body else "",
        )
        return self._response(payload, method)

    def _response(self, body: str, method: str) -> dict[str, object]:
        return {
            "StatusCode": 200 if body else 404,
            "StatusMessage": "OK" if body else "no payload",
            "Headers": {"Content-Type": "application/octet-stream"},
            "Body": body,
            "Success": bool(body),
            "Method": method,
        }

    def _empty_response(self, reason: str, method: str) -> dict[str, object]:
        return {
            "StatusCode": 0,
            "StatusMessage": reason[:120],
            "Headers": {},
            "Body": "",
            "Success": False,
            "Method": method,
        }

    @staticmethod
    def _as_mapping(value: object) -> dict[str, object]:
        if isinstance(value, dict):
            return {str(key): item for key, item in value.items()}
        fields: dict[str, object] = {}
        for key in ("Url", "url", "Method", "method", "Headers", "headers", "Body", "body"):
            item = getattr(value, key, None)
            if item is not None:
                fields[key] = item
        items = getattr(value, "items", None)
        if callable(items):
            try:
                for key, item in items():
                    fields[str(key)] = item
            except Exception:  # noqa: BLE001 - Lua tables are not always iterable
                pass
        return fields

    def bridge(self, url: object, method: object = "GET") -> str:
        """Callable exposed to the Lua emulator as ``__protez_http``.

        The Lua side calls ``HttpGet(url)`` or ``game:HttpGet(url)``; the
        second form passes the instance table first, so non-string arguments
        are skipped when looking for the URL.
        """
        candidates = [url, method]
        target: str | None = None
        for candidate in candidates:
            if isinstance(candidate, str) and candidate.lower().startswith(("http://", "https://")):
                target = candidate
                break
        if target is None:
            return ""
        try:
            return self.fetch(target)
        except RemotePayloadError as exc:
            self._records.append(
                FetchRecord(url=target, size_bytes=0, status="failed", cached=False, detail=str(exc))
            )
            self.logger.warning("Payload request failed: %s", exc)
            return ""
        except Exception as exc:  # noqa: BLE001 - never let Lua see a Python traceback
            self.logger.warning("Payload request failed: %s", exc)
            return ""


def luarmor_payload_url(loader_id: str) -> str:
    return f"https://api.luarmor.net/files/v4/loaders/{loader_id}.lua"


def luarmor_signature(source: str) -> dict[str, object] | None:
    """Describe a Luarmor loader without running it."""
    loader_id = luarmor_loader_id(source or "")
    if loader_id is None:
        return None
    return {
        "vendor": "Luarmor",
        "loader_id": loader_id,
        "loader_url": luarmor_payload_url(loader_id),
        "script_key": extract_script_key(source or ""),
        "needs_runtime_key": "script_key" not in (source or ""),
    }


def encode_payload_for_prefetch(payload: str) -> str:
    """Base64 helper used by tests and by the GUI when staging responses."""
    return base64.b64encode(payload.encode("utf-8")).decode("ascii")


__all__ = [
    "FetchRecord",
    "PayloadFetcher",
    "RemotePayloadError",
    "extract_script_key",
    "extract_urls",
    "looks_like_loader",
    "luarmor_loader_id",
    "luarmor_payload_url",
    "luarmor_signature",
    "is_luarmor",
    "MAX_REMOTE_PAYLOAD_BYTES",
]
