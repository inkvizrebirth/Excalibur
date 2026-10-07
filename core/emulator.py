"""In-process Lua interpreter used as a second, portable dynamic backend.

The bundled ``protez-native-host`` worker runs real Luau bytecode and is the
preferred backend, but it needs a working OS sandbox (Windows AppContainer or
Linux namespaces).  This module adds a pure in-process alternative built on
``lupa`` (Lua 5.1 / LuaJIT), which is enough to execute the *loader* half of
almost every Roblox obfuscator: IronBrew, WeAreDevs, PSU, Nexus, MoonSec V2,
AztupBrew, Luarmor-style key loaders and anything else that decrypts a
string table and finally calls ``loadstring``.

Safety model - the interpreter runs inside the Protez process, so the
capabilities are removed rather than confined:

* ``io``, ``package``, ``require``, ``dofile``, ``loadfile`` and the real
  ``os`` library are gone; ``os`` keeps a monotonic clock only.
* ``debug.sethook`` is replaced so a script cannot clear the instruction and
  wall-clock budget that aborts runaway loaders.
* ``loadstring``/``load``/``string.dump`` are wrapped to record every chunk
  the loader produces, including dumped Lua 5.1 bytecode.
* HTTP is a Python callback the caller controls; by default it answers with
  an empty body, and the caller may wire the cached :class:`PayloadFetcher`.
"""

from __future__ import annotations

import hashlib
import logging
import time
import zlib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Mapping, Sequence

from core.executor_api import (
    WORKSPACE_MAX_FILE_BYTES,
    WORKSPACE_MAX_FILES,
    classify_written_file,
    normalise_workspace_path,
)
from core.injector_env import ExecutorProfile, build_lua_prelude, get_profile

__all__ = [
    "EmulatorCapture",
    "EmulatorResult",
    "EmulatorUnavailable",
    "LuaEmulator",
    "emulator_available",
    "classify_chunk",
]

MAX_INSTRUCTIONS = 80_000_000
MAX_CAPTURES = 200
MAX_CAPTURE_BYTES = 8 * 1024 * 1024
MAX_PRINT_LINES = 400

_LUA_BOOTSTRAP = r"""
-- Python callables arrive as callable userdata; wrap them in Lua closures.
local __protez_step_fn = function() __protez_step() end
local __protez_print_fn = function(text) __protez_record_print(text) end
local __protez_clock_fn = function() return __protez_clock() end
local __protez_time_fn = function() return __protez_time() end
local __protez_http_fn = function(url, method) return __protez_http(url, method) end
rawset(_G, '__protez_step_fn', __protez_step_fn)
rawset(_G, '__protez_http_lua', __protez_http_fn)

local __protez_real_loadstring = loadstring
local __protez_real_load = load
local __protez_real_dump = string.dump
local __protez_real_sethook = debug and debug.sethook

local function __protez_flatten(value, depth)
  if type(value) == 'string' then return value end
  if type(value) == 'number' or type(value) == 'boolean' then return tostring(value) end
  if type(value) == 'table' and depth < 3 then
    local parts = {}
    for _, item in ipairs(value) do
      parts[#parts + 1] = __protez_flatten(item, depth + 1)
    end
    return table.concat(parts, '\t')
  end
  return ''
end

local function __protez_record_safe(kind, chunk)
  if type(chunk) ~= 'string' then return end
  -- Binary chunks (dumped bytecode) cannot always cross the language bridge as
  -- text; fall back to a hex transfer instead of losing the payload.
  local ok = pcall(__protez_record, kind, chunk)
  if not ok then
    local hex = chunk:gsub('.', function(character)
      return string.format('%02x', string.byte(character))
    end)
    local hex_ok = pcall(__protez_record, kind .. ':hex', hex)
    if not hex_ok then pcall(__protez_record, kind .. ':unreadable', '') end
  end
end

local function __protez_guard_record(kind, chunk, name)
  -- Empty chunks carry nothing worth recovering.
  if type(chunk) ~= 'string' or #chunk == 0 then return end
  -- Chunks that are not valid UTF-8 cannot cross into the host as text, so
  -- the host is told the size instead of losing the whole run.
  local ok = pcall(__protez_record, kind, chunk, name)
  if not ok then
    local size = type(chunk) == 'string' and #chunk or 0
    pcall(__protez_record, kind .. ':unreadable', '', tostring(name or '') .. ' (' .. size .. ' bytes)')
  end
end
local function __protez_safe_loadstring(chunk, chunkname)
  __protez_guard_record('loadstring', chunk, chunkname)
  return __protez_real_loadstring(chunk, chunkname)
end
loadstring = __protez_safe_loadstring
load = function(chunk, chunkname, mode, environment)
  -- Roblox/Luau `load` accepts a string as well as a function; Lua 5.1 does
  -- not, so route strings through loadstring and keep the capture.
  if type(chunk) == 'string' then
    __protez_guard_record('load', chunk, chunkname)
    return __protez_real_loadstring(chunk, chunkname)
  end
  return __protez_real_load(chunk, chunkname, mode, environment)
end
string.dump = function(fn, strip)
  local dumped = __protez_real_dump(fn, strip)
  __protez_record_safe('bytecode', dumped)
  return dumped
end
if debug and __protez_real_sethook then
  debug.sethook = function(...)
    -- The step budget belongs to Protez; scripts may not clear it.
    return __protez_real_sethook(__protez_step_fn, '', __protez_hook_count())
  end
end
local __protez_real_print = print
local __protez_real_warn = warn
print = function(...)
  local text = __protez_flatten({ ... }, 0)
  if not pcall(__protez_record_print, text) then
    pcall(__protez_record_print, '<binary output, ' .. #text .. ' bytes>')
  end
  return nil
end
warn = function(...)
  local text = 'warn: ' .. __protez_flatten({ ... }, 0)
  if not pcall(__protez_record_print, text) then
    pcall(__protez_record_print, 'warn: <binary output, ' .. #text .. ' bytes>')
  end
  return nil
end
"""

_SAFE_OS = r"""
os = {
  clock = function() return __protez_clock_fn() end,
  time = function() return __protez_time_fn() end,
  date = function() return '1970-01-01' end,
  difftime = function(a, b) return (a or 0) - (b or 0) end,
  getenv = function() return nil end,
}
io = nil
package = nil
require = nil
dofile = nil
loadfile = nil
"""


class EmulatorUnavailable(RuntimeError):
    """``lupa`` is not installed, so the portable backend cannot run."""


@dataclass(frozen=True)
class EmulatorCapture:
    kind: str  # loadstring | load | bytecode | print
    text: str
    chunk_name: str = ""
    binary: bool = False

    @property
    def size_bytes(self) -> int:
        return len(self.text)


@dataclass
class EmulatorResult:
    status: str  # completed | error | limit | unavailable
    captures: tuple[EmulatorCapture, ...] = ()
    error: str | None = None
    instructions: int = 0
    duration_seconds: float = 0.0
    runtime: str = ""
    profile: str = ""
    notes: tuple[str, ...] = ()
    fetches: tuple[str, ...] = ()
    requests: tuple[dict[str, Any], ...] = ()
    written_files: tuple[str, ...] = ()

    @property
    def ok(self) -> bool:
        return self.status == "completed"

    @property
    def chunks(self) -> tuple[EmulatorCapture, ...]:
        return tuple(item for item in self.captures if item.kind in {"loadstring", "load", "print"})

    @property
    def bytecode(self) -> tuple[EmulatorCapture, ...]:
        return tuple(item for item in self.captures if item.kind == "bytecode")

    @property
    def downloaded_payloads(self) -> tuple[EmulatorCapture, ...]:
        """Bodies the loader pulled over HTTP/``request``."""
        return tuple(item for item in self.captures if item.kind == "http-body")

    def source_chunks(self, *, minimum: int = 24) -> tuple[EmulatorCapture, ...]:
        return tuple(
            item
            for item in self.captures
            if item.kind in {"loadstring", "load", "file", "http-body"}
            and not item.binary
            and len(item.text.strip()) >= minimum
        )

    @property
    def written_captures(self) -> tuple[EmulatorCapture, ...]:
        """Files a script wrote through the executor workspace API."""
        return tuple(item for item in self.captures if item.kind == "file")

    @property
    def request_calls(self) -> tuple[EmulatorCapture, ...]:
        """HTTP calls the loader issued through ``request``/``HttpGet``."""
        return tuple(item for item in self.captures if item.kind == "request")


def _as_mapping(value: Any) -> dict[str, Any]:
    """Best-effort dict view over a Lua table or Python mapping."""
    if value is None:
        return {}
    if isinstance(value, dict):
        return value
    converted: dict[str, Any] = {}
    items = getattr(value, "items", None)
    if callable(items):
        try:
            for key, item in items():
                converted[str(key)] = item
            return converted
        except Exception:  # noqa: BLE001 - lupa tables can be odd
            return converted
    try:
        for key in value:  # type: ignore[union-attr]
            converted[str(key)] = value[key]
    except Exception:  # noqa: BLE001
        return converted
    return converted


def emulator_available() -> bool:
    """True when the optional ``lupa`` runtime can be imported."""
    try:
        import lupa  # noqa: F401
    except Exception:  # noqa: BLE001 - missing optional dependency
        return False
    return True


def _load_lua51():
    try:
        from lupa import lua51  # type: ignore

        return lua51, "Lua 5.1 (lupa)"
    except Exception:  # noqa: BLE001
        pass
    try:
        from lupa import luajit20  # type: ignore

        return luajit20, "LuaJIT 2.0 (lupa)"
    except Exception:  # noqa: BLE001
        pass
    raise EmulatorUnavailable(
        "the optional Lua runtime is missing; install 'lupa' to enable the portable backend"
    )


def classify_chunk(text: str) -> str:
    """Describe a captured chunk without executing it."""
    if not text:
        return "empty"
    head = text[:8]
    if head.startswith("\x1bLua"):
        return "lua51-bytecode"
    if head.startswith("\x1bLJ"):
        return "luajit-bytecode"
    if head.startswith("RSB1") or head.startswith("\x01\x02\x03"):
        return "luau-bytecode"
    stripped = text.lstrip()
    if stripped.startswith(("--", "local ", "return", "if ", "function", "for ", "while ", "do ", "repeat")):
        return "lua-source"
    printable = sum(1 for character in text[:512] if character.isprintable() or character in "\r\n\t")
    return "lua-source" if printable >= max(1, len(text[:512]) * 9 // 10) else "binary"


class LuaEmulator:
    """Run a loader inside a capability-stripped Lua 5.1 interpreter."""

    def __init__(
        self,
        *,
        profile: ExecutorProfile | str | None = None,
        prelude: str | None = None,
        script_key: str | None = None,
        timeout_seconds: float = 20.0,
        max_instructions: int = MAX_INSTRUCTIONS,
        max_captures: int = MAX_CAPTURES,
        max_capture_bytes: int = MAX_CAPTURE_BYTES,
        http_bridge: Callable[[object, object], str] | None = None,
        request_bridge: Callable[[object], object] | None = None,
        workspace_dir: Path | str | None = None,
        hwid: str | None = None,
        logger: logging.Logger | None = None,
        roblox: bool = True,
    ):
        self.profile = profile if isinstance(profile, ExecutorProfile) else get_profile(
            profile if isinstance(profile, str) else None
        )
        self.script_key = script_key
        self.timeout_seconds = float(timeout_seconds)
        self.max_instructions = int(max_instructions)
        self.max_captures = int(max_captures)
        self.max_capture_bytes = int(max_capture_bytes)
        self.http_bridge = http_bridge
        self.request_bridge = request_bridge
        self.workspace_dir = Path(workspace_dir) if workspace_dir else None
        self.hwid = hwid
        self.logger = logger or logging.getLogger("protez")
        self.roblox = roblox
        self._prelude = prelude if prelude is not None else build_lua_prelude(
            self.profile, roblox=roblox, script_key=script_key
        )

    # ------------------------------------------------------------------
    def run(self, source: str, *, depth: int = 0) -> EmulatorResult:
        if not isinstance(source, str):
            raise TypeError("source must be text")
        try:
            lua_module, runtime_label = _load_lua51()
        except EmulatorUnavailable as exc:
            return EmulatorResult(
                status="unavailable",
                error=str(exc),
                runtime="",
                profile=self.profile.key,
            )

        started = time.monotonic()
        deadline = started + self.timeout_seconds
        captures: list[EmulatorCapture] = []
        state = {
            "instructions": 0,
            "stopped": None,
            "fetches": [],
            "requests": [],
            "writes": [],
            "inputs": [],
            "clipboard": "",
        }
        output_bytes = {"value": 0}

        def record(kind: Any, text: Any, chunk_name: Any = "") -> None:
            kind = str(kind)
            if kind.endswith(":hex"):
                # Binary payload transferred as hex because the text bridge
                # cannot carry non-UTF-8 bytes.
                try:
                    text = bytes.fromhex(str(text))
                except ValueError:
                    return
                kind = kind[: -len(":hex")]
                captures.append(
                    EmulatorCapture(
                        kind=kind,
                        text=text.decode("latin-1"),
                        chunk_name=str(chunk_name or ""),
                        binary=True,
                    )
                )
                return
            if kind.endswith(":unreadable"):
                captures.append(
                    EmulatorCapture(
                        kind=kind[: -len(":unreadable")],
                        text="",
                        chunk_name="binary chunk could not be transferred",
                        binary=True,
                    )
                )
                return
            if isinstance(text, bytes):
                try:
                    decoded = text.decode("utf-8")
                    binary = classify_chunk(decoded) not in {"lua-source", "empty"}
                except UnicodeDecodeError:
                    decoded = text.decode("latin-1")
                    binary = True
            elif isinstance(text, str):
                binary = classify_chunk(text) not in {"lua-source", "empty"}
                decoded = text
            else:
                return
            if len(captures) >= self.max_captures:
                return
            output_bytes["value"] += len(decoded)
            if output_bytes["value"] > self.max_capture_bytes:
                raise RuntimeError("captured chunks exceed the configured byte budget")
            captures.append(
                EmulatorCapture(
                    kind=str(kind),
                    text=decoded,
                    chunk_name=str(chunk_name or ""),
                    binary=binary,
                )
            )

        printed = {"count": 0}

        def record_print(text: Any) -> None:
            if printed["count"] >= MAX_PRINT_LINES:
                return
            printed["count"] += 1
            captures.append(
                EmulatorCapture(kind="print", text=str(text), chunk_name="", binary=False)
            )

        def step_hook() -> None:
            state["instructions"] += 1
            if state["instructions"] > self.max_instructions:
                state["stopped"] = "instruction budget"
                raise RuntimeError("Protez step budget exceeded")
            if time.monotonic() > deadline:
                state["stopped"] = "time budget"
                raise RuntimeError("Protez time budget exceeded")

        def clock() -> float:
            return time.monotonic() - started

        def wall_time() -> float:
            return time.time()

        def hook_count() -> int:
            return 20000

        def record_download(url: Any, body: Any) -> str:
            """Keep a downloaded body when it can be a payload."""
            if not isinstance(body, str) or not body:
                return body
            label = str(url or "download")
            kind = classify_written_file(label, body)
            if kind == "source":
                record("http-body", body, label)
            elif kind == "bytecode":
                record("http-body:hex", body.encode("latin-1", "replace").hex(), label)
            return body

        def http(url: Any, method: Any = "GET") -> str:
            if isinstance(url, str) and url.lower().startswith(("http://", "https://")):
                state["fetches"].append(url)
            if self.http_bridge is None:
                return ""
            try:
                result = self.http_bridge(url, method)
            except Exception as exc:  # noqa: BLE001 - bridge failures must not crash Lua
                self.logger.warning("HTTP bridge failed: %s", exc)
                return ""
            return record_download(url, result) if isinstance(result, str) else ""

        def request(options: Any) -> dict[str, Any]:
            """Serve `request{Url=..., Method=..., Headers=..., Body=...}`."""
            fields = _as_mapping(options)
            url = fields.get("Url") or fields.get("url") or fields.get("URL")
            method = str(fields.get("Method") or fields.get("method") or "GET").upper()
            headers = _as_mapping(fields.get("Headers") or fields.get("headers"))
            body = fields.get("Body", fields.get("body"))
            if isinstance(url, str) and url.lower().startswith(("http://", "https://")):
                state["fetches"].append(url)
            body_bytes = len(body) if isinstance(body, (str, bytes)) else 0
            state["requests"].append(
                {
                    "url": url if isinstance(url, str) else "",
                    "method": method,
                    "headers": {str(key): str(value) for key, value in headers.items()},
                    "body_bytes": body_bytes,
                }
            )
            if isinstance(url, str) and url.lower().startswith(("http://", "https://")):
                header_names = ", ".join(sorted(str(key) for key in headers)) or "none"
                record(
                    "request",
                    f"{method} {url} ({body_bytes} byte(s) of body, headers: {header_names})",
                    url,
                )
            if self.request_bridge is not None:
                try:
                    response = self.request_bridge(
                        {
                            "Url": url,
                            "Method": method,
                            "Headers": {str(key): str(value) for key, value in headers.items()},
                            "Body": body if isinstance(body, str) else None,
                        }
                    )
                except Exception as exc:  # noqa: BLE001 - never let a bridge kill the run
                    self.logger.warning("Request bridge failed: %s", exc)
                    response = None
                if isinstance(response, dict):
                    body_text = response.get("Body")
                    if isinstance(body_text, str):
                        record_download(url, body_text)
                    return {
                        "StatusCode": int(response.get("StatusCode") or 0),
                        "StatusMessage": str(response.get("StatusMessage") or ""),
                        "Headers": response.get("Headers") or {},
                        "Body": body_text if isinstance(body_text, str) else "",
                        "Success": bool(response.get("Success")),
                    }
            text = http(url, method)
            return {
                "StatusCode": 200 if text else 0,
                "StatusMessage": "OK" if text else "no response",
                "Headers": {},
                "Body": text,
                "Success": bool(text),
            }

        def workspace_write(path: Any, data: Any, mode: Any = "write") -> bool:
            """Mirror a script's `writefile` into the run workspace and capture it."""
            raw = "" if data is None else (data if isinstance(data, str) else str(data))
            name = normalise_workspace_path(str(path))
            if len(state["writes"]) >= WORKSPACE_MAX_FILES:
                return False
            if len(raw) > WORKSPACE_MAX_FILE_BYTES:
                raw = raw[:WORKSPACE_MAX_FILE_BYTES]
            state["writes"].append(name)
            if self.workspace_dir is not None:
                target = self.workspace_dir / name
                try:
                    target.parent.mkdir(parents=True, exist_ok=True)
                    mode_text = "ab" if str(mode) == "append" else "wb"
                    with target.open(mode_text) as handle:
                        handle.write(raw.encode("latin-1", "replace"))
                except OSError as exc:
                    self.logger.debug("Workspace write failed for %s: %s", name, exc)
            kind = classify_written_file(name, raw)
            if kind == "source" and len(raw.strip()) >= 8:
                record("file", raw, name)
            elif kind == "bytecode":
                record("file:hex", raw.encode("latin-1", "replace").hex(), name)
            return True

        def workspace_read(path: Any) -> str:
            name = normalise_workspace_path(str(path))
            if self.workspace_dir is None:
                return ""
            try:
                return (self.workspace_dir / name).read_text(encoding="latin-1", errors="replace")
            except OSError:
                return ""

        def workspace_exists(path: Any, kind: Any = "isfile") -> bool:
            name = normalise_workspace_path(str(path))
            if self.workspace_dir is None:
                return False
            target = self.workspace_dir / name
            return target.is_dir() if str(kind) == "isfolder" else target.is_file()

        def workspace_list(path: Any = "") -> list[str]:
            name = normalise_workspace_path(str(path)) if path else ""
            if self.workspace_dir is None:
                return []
            root = self.workspace_dir / name if name and name != "unnamed" else self.workspace_dir
            listed: list[str] = []
            try:
                for item in sorted(root.rglob("*")):
                    listed.append(str(item.relative_to(self.workspace_dir)))
                    if len(listed) >= WORKSPACE_MAX_FILES:
                        break
            except OSError:
                return []
            return listed

        def workspace_delete(path: Any, kind: Any = "file") -> bool:
            name = normalise_workspace_path(str(path))
            if self.workspace_dir is None:
                return True
            target = self.workspace_dir / name
            try:
                if str(kind) == "folder":
                    if target.is_dir():
                        for child in sorted(target.rglob("*"), reverse=True):
                            child.unlink(missing_ok=True)
                        target.rmdir()
                else:
                    target.unlink(missing_ok=True)
            except OSError as exc:
                self.logger.debug("Workspace delete failed for %s: %s", name, exc)
            return True

        def workspace_makefolder(path: Any) -> bool:
            name = normalise_workspace_path(str(path))
            if self.workspace_dir is not None:
                try:
                    (self.workspace_dir / name).mkdir(parents=True, exist_ok=True)
                except OSError as exc:
                    self.logger.debug("Workspace mkdir failed for %s: %s", name, exc)
            return True

        def fs_bridge(operation: Any, *arguments: Any) -> Any:
            name = str(operation)
            if name == "write":
                first, second, mode = (list(arguments) + [None, None, "write"])[:3]
                return workspace_write(first, second, mode)
            if name == "read":
                return workspace_read(arguments[0] if arguments else "")
            if name == "isfile":
                return workspace_exists(arguments[0] if arguments else "", "isfile")
            if name == "isfolder":
                return workspace_exists(arguments[0] if arguments else "", "isfolder")
            if name == "list":
                return workspace_list(arguments[0] if arguments else "")
            if name == "makefolder":
                return workspace_makefolder(arguments[0] if arguments else "")
            if name in {"delfile", "delfolder"}:
                first = arguments[0] if arguments else ""
                return workspace_delete(first, "folder" if name == "delfolder" else "file")
            if name == "customasset":
                return ""
            return None

        def clipboard(operation: Any, value: Any = None) -> str:
            if str(operation) == "set":
                state["clipboard"] = "" if value is None else str(value)
                return state["clipboard"]
            return state.get("clipboard", "")

        def hwid() -> str:
            if self.hwid:
                return self.hwid
            digest = hashlib.sha256(b"protez-real-executor").hexdigest().upper()
            return f"PROTEZ-{digest[:8]}-{digest[8:16]}-{digest[16:24]}"

        def hash_text(algorithm: Any, value: Any) -> str:
            name = str(algorithm or "sha256").lower()
            data = value.encode("latin-1", "replace") if isinstance(value, str) else bytes(value or b"")
            if name in {"sha256", "sha2", "sha"}:
                return hashlib.sha256(data).hexdigest()
            if name == "sha1":
                return hashlib.sha1(data).hexdigest()
            if name == "md5":
                return hashlib.md5(data).hexdigest()
            if name == "sha512":
                return hashlib.sha512(data).hexdigest()
            return hashlib.sha256(data).hexdigest()

        def decompile(bytecode: Any) -> str:
            raw = bytecode.encode("latin-1", "replace") if isinstance(bytecode, str) else bytes(bytecode or b"")
            try:
                from core.lua51 import decompile as lua51_decompile

                return lua51_decompile(raw)
            except Exception as exc:  # noqa: BLE001 - the helper is best effort
                self.logger.debug("decompile() bridge failed: %s", exc)
                return ""

        def input_event(action: Any, detail: Any = "") -> bool:
            state["inputs"].append(f"{action}:{detail}")
            return True

        try:
            runtime = lua_module.LuaRuntime(unpack_returned_tuples=True)
        except Exception as exc:  # noqa: BLE001
            return EmulatorResult(
                status="unavailable", error=str(exc), profile=self.profile.key
            )

        globals_table = runtime.globals()
        globals_table["__protez_record"] = record
        globals_table["__protez_record_print"] = record_print
        globals_table["__protez_step"] = step_hook
        globals_table["__protez_clock"] = clock
        globals_table["__protez_time"] = wall_time
        globals_table["__protez_hook_count"] = hook_count
        globals_table["__protez_http"] = http
        globals_table["__protez_request"] = request
        globals_table["__protez_fs"] = fs_bridge
        globals_table["__protez_clipboard"] = clipboard
        globals_table["__protez_hwid"] = hwid
        globals_table["__protez_hash"] = hash_text
        globals_table["__protez_decompile"] = decompile
        globals_table["__protez_input"] = input_event

        status = "completed"
        error: str | None = None
        try:
            runtime.execute((_SAFE_OS + "\n" + _LUA_BOOTSTRAP).encode("utf-8"))
            # The step budget is installed last so the bootstrap itself runs free.
            runtime.execute("debug.sethook(__protez_step_fn, '', 20000)")
            script = self._prelude + "\n" + source
            runtime.execute(script.encode("utf-8", "replace"))
        except Exception as exc:  # noqa: BLE001 - LuaError and Python errors alike
            status = "limit" if state["stopped"] else "error"
            error = str(exc)
            if state["stopped"]:
                error = f"{error} (stopped by the {state['stopped']})"
            if status == "error" and self.logger:
                self.logger.debug("Portable backend stopped: %s", error)

        duration = time.monotonic() - started
        notes = [f"portable backend: {runtime_label}", f"executor profile: {self.profile.label}"]
        if state["fetches"]:
            notes.append(f"{len(state['fetches'])} HTTP request(s) issued by the loader")
        if state["writes"]:
            notes.append(f"{len(state['writes'])} file(s) written to the executor workspace")
        if state["inputs"]:
            notes.append(f"{len(state['inputs'])} input event(s) recorded, none delivered")
        return EmulatorResult(
            status=status,
            captures=tuple(captures),
            error=error,
            instructions=state["instructions"] * 20000,
            duration_seconds=duration,
            runtime=runtime_label,
            profile=self.profile.key,
            notes=tuple(notes),
            fetches=tuple(dict.fromkeys(state["fetches"])),
            requests=tuple(state["requests"]),
            written_files=tuple(state["writes"]),
        )
