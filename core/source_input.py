from __future__ import annotations

import ipaddress
import logging
import re
import socket
import urllib.error
import urllib.parse
import urllib.request
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core.deobfuscator import MAX_SOURCE_BYTES, deobfuscate_source
from core.version import VERSION

MAX_REMOTE_LAYERS = 4
REMOTE_TIMEOUT_SECONDS = 20
REMOTE_USER_AGENT = f"Protez/{VERSION} (source input)"

_URL_RE = re.compile(r"(?i)\bhttps?://[^\s\"'<>`]+")
_MARKDOWN_LINK_RE = re.compile(r"(?is)^\[[^\]]*\]\((https?://[^)\s]+)\)$")
_HTML_PREFIXES = (b"<!doctype html", b"<html", b"<head", b"<body")


class SourceInputError(ValueError):
    """An input URL could not be safely resolved to readable source text."""


@dataclass(frozen=True)
class ResolvedInput:
    source: str
    source_name: str
    fetched_urls: tuple[str, ...] = ()


def _normalise_escaped_url_text(value: str) -> str:
    value = value.replace(r"\/", "/")
    value = re.sub(r"\\x2f", "/", value, flags=re.IGNORECASE)
    value = re.sub(r"\\u002f", "/", value, flags=re.IGNORECASE)
    return value


def _normalise_code_url(value: str) -> str:
    """Canonicalise common code-host sharing links without fetching page HTML."""
    value = _normalise_escaped_url_text(value.strip())
    value = value.rstrip(".,;:!?)\\]}\"'")
    try:
        parsed = urllib.parse.urlsplit(value)
        port = parsed.port
    except ValueError as exc:
        raise SourceInputError(f"Invalid code link: {exc}") from exc

    scheme = parsed.scheme.lower()
    if scheme not in {"http", "https"}:
        raise SourceInputError("Only HTTP and HTTPS code links are supported")
    if not parsed.hostname:
        raise SourceInputError("The code link is missing a host name")
    if parsed.username is not None or parsed.password is not None:
        raise SourceInputError("Links containing a user name or password are not accepted")

    host = parsed.hostname.rstrip(".").lower()
    path = parsed.path or "/"
    query = parsed.query

    if host == "www.github.com":
        host = "github.com"
    if host == "github.com":
        segments = path.split("/")
        if len(segments) >= 6 and segments[3] == "blob":
            host = "raw.githubusercontent.com"
            path = "/" + "/".join((*segments[1:3], *segments[4:]))
    if host in {"pastebin.com", "www.pastebin.com"}:
        host = "pastebin.com"
        segments = [part for part in path.split("/") if part]
        if segments and segments[0].lower() != "raw":
            path = "/raw/" + segments[0]
        elif segments:
            path = "/" + "/".join(segments)

    if ":" in host and not host.startswith("["):
        netloc = f"[{host}]"
    else:
        netloc = host
    if port is not None:
        netloc = f"{netloc}:{port}"

    return urllib.parse.urlunsplit((scheme, netloc, path, query, ""))


def _extract_url_candidates(source: str) -> list[str]:
    normalised = _normalise_escaped_url_text(source)
    candidates: list[str] = []
    for match in _URL_RE.finditer(normalised):
        candidate = match.group(0).rstrip(".,;:!?)\\]}")
        if candidate and candidate not in candidates:
            candidates.append(candidate)
    return candidates


def _direct_url(source: str) -> str | None:
    value = source.strip()
    markdown_match = _MARKDOWN_LINK_RE.fullmatch(value)
    if markdown_match:
        value = markdown_match.group(1)
    elif len(value) >= 2 and value[0] == "<" and value[-1] == ">":
        value = value[1:-1].strip()
    elif len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
        value = value[1:-1].strip()

    value = _normalise_escaped_url_text(value).rstrip(".,;:!?)\\]}")
    try:
        parsed = urllib.parse.urlsplit(value)
    except ValueError:
        return None
    is_http = parsed.scheme.lower() in {"http", "https"}
    if is_http and parsed.hostname and not re.search(r"\s", value):
        return value
    return None


def _loader_url(source: str) -> str | None:
    lowered = source.lower()
    if "loadstring" not in lowered and "httpget" not in lowered:
        return None

    candidates = _extract_url_candidates(source)
    if not candidates and ("loadstring" in lowered or "httpget" in lowered):
        # Detect a URL assembled from constant Luau strings, but never execute it.
        try:
            candidates = _extract_url_candidates(deobfuscate_source(source).source)
        except (TypeError, ValueError):
            candidates = []

    if len(candidates) > 1:
        raise SourceInputError(
            "This loader contains more than one code link. Paste the exact URL to choose one."
        )
    return candidates[0] if candidates else None


def _url_for_source(source: str) -> str | None:
    return _direct_url(source) or _loader_url(source)


def _assert_public_http_url(url: str) -> None:
    try:
        parsed = urllib.parse.urlsplit(url)
        port = parsed.port or (443 if parsed.scheme.lower() == "https" else 80)
    except ValueError as exc:
        raise SourceInputError(f"Invalid code link: {exc}") from exc

    scheme = parsed.scheme.lower()
    host = (parsed.hostname or "").rstrip(".").lower()
    if scheme not in {"http", "https"} or not host:
        raise SourceInputError("Only public HTTP and HTTPS code links are supported")
    local_suffixes = (".localhost", ".local", ".internal")
    if host in {"localhost", "localhost.localdomain"} or host.endswith(local_suffixes):
        raise SourceInputError("Local network and private-machine URLs are blocked")

    try:
        addresses = {ipaddress.ip_address(host)}
    except ValueError:
        try:
            results = socket.getaddrinfo(host, port, type=socket.SOCK_STREAM)
        except OSError as exc:
            raise SourceInputError(f"Could not resolve code host {host}: {exc}") from exc
        addresses = {
            ipaddress.ip_address(result[4][0].split("%", maxsplit=1)[0])
            for result in results
        }

    if not addresses:
        raise SourceInputError(f"Code host {host} has no usable address")
    if any(not address.is_global for address in addresses):
        raise SourceInputError("Local network and private-machine URLs are blocked")


class _SafeRedirectHandler(urllib.request.HTTPRedirectHandler):
    max_redirections = 5
    max_repeats = 2

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        absolute_url = urllib.parse.urljoin(req.full_url, newurl)
        _assert_public_http_url(absolute_url)
        return super().redirect_request(req, fp, code, msg, headers, absolute_url)


def _response_charset(headers) -> str | None:
    get_charset = getattr(headers, "get_content_charset", None)
    if callable(get_charset):
        try:
            return get_charset()
        except (LookupError, TypeError, ValueError):
            return None
    return None


def _response_content_type(headers) -> str:
    get_type = getattr(headers, "get_content_type", None)
    if callable(get_type):
        try:
            return str(get_type()).lower()
        except (TypeError, ValueError):
            pass
    try:
        return str(headers.get("Content-Type", "")).split(";", 1)[0].strip().lower()
    except AttributeError:
        return ""


def fetch_code_url(
    url: str,
    *,
    timeout: float = REMOTE_TIMEOUT_SECONDS,
    max_bytes: int = MAX_SOURCE_BYTES,
    opener=None,
) -> str:
    """Fetch source text only; never evaluates code and rejects local/private hosts."""
    normalized_url = _normalise_code_url(url)
    _assert_public_http_url(normalized_url)
    request = urllib.request.Request(
        normalized_url,
        headers={
            "User-Agent": REMOTE_USER_AGENT,
            "Accept": "text/plain, application/octet-stream, application/javascript, */*;q=0.5",
            "Accept-Encoding": "identity",
        },
    )
    if opener is None:
        opener = urllib.request.build_opener(_SafeRedirectHandler())

    try:
        response = opener.open(request, timeout=timeout)
    except SourceInputError:
        raise
    except urllib.error.HTTPError as exc:
        raise SourceInputError(f"Code link returned HTTP {exc.code}: {exc.reason}") from exc
    except (urllib.error.URLError, TimeoutError, OSError, ValueError) as exc:
        reason = getattr(exc, "reason", exc)
        raise SourceInputError(f"Could not download code from the link: {reason}") from exc

    try:
        with response:
            get_final_url = getattr(response, "geturl", None)
            final_url = get_final_url() if callable(get_final_url) else normalized_url
            _assert_public_http_url(final_url)
            headers = getattr(response, "headers", {})
            try:
                declared_length = int(headers.get("Content-Length", "0") or 0)
            except (AttributeError, TypeError, ValueError):
                declared_length = 0
            if declared_length > max_bytes:
                raise SourceInputError(
                    f"Code link is larger than the {max_bytes // (1024 * 1024)} MB limit"
                )

            payload = bytearray()
            while True:
                block = response.read(min(64 * 1024, max_bytes + 1 - len(payload)))
                if not block:
                    break
                payload.extend(block)
                if len(payload) > max_bytes:
                    raise SourceInputError(
                        f"Code link is larger than the {max_bytes // (1024 * 1024)} MB limit"
                    )
    except SourceInputError:
        raise
    except (OSError, TimeoutError, ValueError) as exc:
        raise SourceInputError(f"Could not read code from the link: {exc}") from exc

    raw = bytes(payload)
    if not raw:
        raise SourceInputError("The code link returned an empty file")
    content_type = _response_content_type(headers)
    starts_with_html = raw.lstrip()[:32].lower().startswith(_HTML_PREFIXES)
    if content_type in {"text/html", "application/xhtml+xml"} or starts_with_html:
        raise SourceInputError(
            "The link returned a web page, not source code. Use a raw-file or direct-download link."
        )

    charset = _response_charset(headers)
    encodings = [charset, "utf-8-sig", "cp1252"] if charset else ["utf-8-sig", "cp1252"]
    text = None
    for encoding in dict.fromkeys(item for item in encodings if item):
        try:
            text = raw.decode(encoding)
            break
        except (LookupError, UnicodeDecodeError):
            continue
    if text is None:
        raise SourceInputError("The link did not return readable text")
    if "\x00" in text:
        raise SourceInputError("The link returned binary data, not readable source code")
    if not text.strip():
        raise SourceInputError("The code link returned an empty file")
    return text


def _source_name(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    name = Path(urllib.parse.unquote(parsed.path)).name
    name = "".join(
        character
        for character in name
        if character.isprintable() and character not in "\r\n"
    )
    if not name:
        name = f"{parsed.hostname or 'remote-source'}.luau"
    return name[:120]


def _safe_log_url(url: str) -> str:
    parsed = urllib.parse.urlsplit(url)
    host = parsed.hostname or "unknown-host"
    if parsed.port is not None:
        host = f"{host}:{parsed.port}"
    return urllib.parse.urlunsplit((parsed.scheme, host, parsed.path, "", ""))


def resolve_source_input(
    source: str,
    *,
    source_name: str = "pasted input",
    logger: logging.Logger | None = None,
    fetcher: Callable[[str], str] | None = None,
    max_remote_layers: int = MAX_REMOTE_LAYERS,
) -> ResolvedInput:
    """Resolve direct code links and simple HttpGet/loadstring links as text."""
    if not isinstance(source, str):
        raise TypeError("source must be text")
    if max_remote_layers < 0:
        raise ValueError("max_remote_layers cannot be negative")

    fetch = fetcher or fetch_code_url
    current_source = source
    current_name = source_name
    fetched: list[str] = []
    seen: set[str] = set()

    for layer in range(max_remote_layers):
        candidate_url = _url_for_source(current_source)
        if candidate_url is None:
            return ResolvedInput(current_source, current_name, tuple(fetched))

        normalized_url = _normalise_code_url(candidate_url)
        if normalized_url in seen:
            raise SourceInputError(
                "The linked loader points back to a source that was already fetched"
            )
        seen.add(normalized_url)
        display_url = _safe_log_url(normalized_url)
        if logger:
            logger.info(
                "Fetching source link (%s/%s): %s",
                layer + 1,
                max_remote_layers,
                display_url,
            )
        try:
            current_source = fetch(normalized_url)
        except SourceInputError:
            raise
        except Exception as exc:
            raise SourceInputError(f"Could not resolve source link: {exc}") from exc
        if not isinstance(current_source, str) or not current_source.strip():
            raise SourceInputError("The code link returned no source text")
        current_name = _source_name(normalized_url)
        fetched.append(display_url)
        if logger:
            logger.info("Fetched %s characters from %s", f"{len(current_source):,}", display_url)

    if _url_for_source(current_source) is not None:
        raise SourceInputError(
            f"This input contains more than {max_remote_layers} linked loader layers; "
            "stop and inspect it manually."
        )
    return ResolvedInput(current_source, current_name, tuple(fetched))
