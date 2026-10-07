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
import os
import logging
import signal
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
from core.vm_dump import (
    VM_DUMP_LUA,
    VmSnapshot,
    constant_pool,
    instruction_table,
    snapshot_from_bridge,
)

__all__ = [
    "backend_terminates",
    "EmulatorCapture",
    "EmulatorResult",
    "EmulatorUnavailable",
    "LuaEmulator",
    "emulator_available",
    "classify_chunk",
]

# The instruction hook fires every HOOK_STEP VM instructions.  A small step
# keeps VM-table introspection dense enough to catch a loader mid-decode; the
# VM scanner gates itself (dense early, sparse later) and is budgeted, so the
# cost stays bounded on long-running payloads (see core.vm_dump).
HOOK_STEP = 500

MAX_INSTRUCTIONS = 80_000_000 // HOOK_STEP
#: Once the budget is spent, re-escalate this often: a loader that keeps catching
#: the error gets its newly created handlers neutered as well.
ESCALATE_EVERY = 2_000
MAX_CAPTURES = 200
MAX_VM_TABLES = 160
MAX_CAPTURE_BYTES = 8 * 1024 * 1024
MAX_PRINT_LINES = 400

_LUA_BOOTSTRAP = r"""
-- Python callables arrive as callable userdata; wrap them in Lua closures.
local __protez_real_pcall = pcall
local __protez_real_xpcall = xpcall
local __protez_real_resume = coroutine and coroutine.resume
local __protez_real_wrap = coroutine and coroutine.wrap
-- Forward declaration: ``__protez_run_payload`` is defined before the real
-- loader is captured, and Lua locals are only visible after their declaration.
local __protez_real_loadstring

local function __protez_host_call(name, ...)
  -- Host callbacks are Python callables, which cross the lupa bridge as
  -- callable *userdata*: ``type(fn) == 'function'`` is false for them, so a
  -- guard on the type silently disables the bridge.  Call by name instead.
  local fn = rawget(_G, name)
  if fn == nil then return nil end
  local ok, result = pcall(fn, ...)
  if not ok then return nil end
  return result
end


-- A loader that wraps its own loop in ``pcall`` swallows the step budget and
-- keeps running (AztupBrew does exactly that), which used to hang the whole
-- process: the error was caught, the loop retried, the hook raised again.
-- Once the budget is spent the hook is allowed to *edit* the paused script:
-- every reachable ``pcall``/``xpcall``/``coroutine.resume`` reference is
-- replaced by a function that raises, so the next error propagates out of the
-- chunk instead of being caught.  This only ever runs after the budget is gone.
local __protez_fatal_fn = function()
  error('Protez step budget exceeded', 2)
end

local function __protez_patch_table(target)
  if type(target) ~= 'table' then return end
  local seen = 0
  for key, value in pairs(target) do
    if value == __protez_real_pcall or value == __protez_real_xpcall
       or value == __protez_real_resume or value == __protez_real_wrap then
      rawset(target, key, __protez_fatal_fn)
    end
    seen = seen + 1
    if seen > 256 then break end
  end
end

local function __protez_neuter()
  rawset(_G, 'pcall', __protez_fatal_fn)
  rawset(_G, 'xpcall', __protez_fatal_fn)
  if coroutine then
    coroutine.resume = __protez_fatal_fn
    coroutine.wrap = __protez_fatal_fn
  end
  for level = 2, 200 do
    local info = debug.getinfo(level, 'f')
    if info == nil then break end
    local fn = info.func
    if fn ~= nil then
      local index = 1
      while true do
        local name, value = debug.getupvalue(fn, index)
        if name == nil then break end
        if value == __protez_real_pcall or value == __protez_real_xpcall
           or value == __protez_real_resume or value == __protez_real_wrap then
          debug.setupvalue(fn, index, __protez_fatal_fn)
        elseif type(value) == 'table' then
          __protez_patch_table(value)
        end
        index = index + 1
      end
    end
  end
end

local __protez_position_tick = 0

local function __protez_report_position(kind)
  -- Where the script currently is.  Recorded when the budget runs out, and
  -- periodically when the host asked for a position log: a loader that
  -- disappears into one long C call leaves that log as the only clue.
  if rawget(_G, '__protez_note_position') == nil then return end
  -- Walk out of Protez's own frames (report -> step -> the combined hook) to
  -- the payload's frame, which is the one worth reporting.
  local own_source = debug.getinfo(1, 'S').source
  local best = nil
  for level = 2, 8 do
    local info = debug.getinfo(level, 'Sl')
    if info == nil then break end
    best = info
    if info.what == 'Lua' and info.source ~= own_source then break end
  end
  if best == nil then return end
  __protez_host_call('__protez_note_position', kind, tostring(best.short_src or ''),
                     tostring(best.currentline or 0), tostring(best.what or ''))
end

-- Diagnostic: on a payload error, describe the failing frames and their
-- locals.  Enabled by the host (PROTEZ_EMU_TRACEBACK=1) when a family stops
-- with an error that the payload itself caught and re-raised somewhere else.
local function __protez_traceback(err)
  local parts = { tostring(err) }
  for level = 2, 14 do
    local info = debug.getinfo(level, 'Sl')
    if info == nil then break end
    parts[#parts + 1] = string.format('  #%d %s:%s %s', level - 1,
      tostring(info.short_src or '?'), tostring(info.currentline or -1), tostring(info.what or ''))
    for index = 1, 26 do
      local name, value = debug.getlocal(level, index)
      if name == nil then break end
      local kind = type(value)
      local shown = ''
      if kind == 'table' then
        local ok, count = pcall(function() return #value end)
        shown = '#' .. tostring(ok and count or '?')
      elseif kind ~= 'function' and kind ~= 'userdata' then
        shown = tostring(value):sub(1, 60)
      end
      parts[#parts + 1] = string.format('      %s = %s %s', tostring(name), kind, shown)
    end
  end
  return table.concat(parts, '\n')
end
rawset(_G, '__protez_traceback', __protez_traceback)

-- Runs the payload through ``xpcall`` so a failure carries a traceback with the
-- failing frames' locals.  The real ``loadstring`` is used on purpose: the
-- instrumented one would record the payload as a captured chunk.
local function __protez_run_payload()
  local source = rawget(_G, '__protez_payload_source')
  if type(source) ~= 'string' then return false, 'no payload source' end
  local fn, load_error = __protez_real_loadstring(source, '@payload')
  if fn == nil then return false, tostring(load_error) end
  local ok, message = __protez_real_xpcall(fn, __protez_traceback)
  return ok, tostring(message)
end
rawset(_G, '__protez_run_payload', __protez_run_payload)

local function __protez_step_fn()
  local verdict = __protez_step()
  if verdict == 'escalate' then
    __protez_report_position('budget')
    __protez_neuter()
    error('Protez step budget exceeded', 0)
  end
  if verdict == 'trace' then
    __protez_position_tick = __protez_position_tick + 1
    if __protez_position_tick >= 200 then
      __protez_position_tick = 0
      __protez_report_position('trace')
    end
  end
end
local __protez_print_fn = function(text) __protez_record_print(text) end
local __protez_clock_fn = function() return __protez_clock() end
local __protez_time_fn = function() return __protez_time() end
local __protez_http_fn = function(url, method) return __protez_http(url, method) end
rawset(_G, '__protez_step_fn', __protez_step_fn)
rawset(_G, '__protez_http_lua', __protez_http_fn)

__protez_real_loadstring = loadstring
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
local function __protez_normalise(chunk)
  -- The payload may be Luau (numeric separators, type arrows, continue) while
  -- the portable backend is Lua 5.1.  The host lowers it when it can; the
  -- original chunk is what gets recorded, this is an execution-only copy.
  if type(chunk) ~= 'string' then return nil end
  local lowered = __protez_host_call('__protez_normalise_luau', chunk)
  if type(lowered) == 'string' and lowered ~= chunk then return lowered end
  return nil
end

local function __protez_load_any(chunk, chunkname)
  local fn, err = __protez_real_loadstring(chunk, chunkname)
  if fn ~= nil then return fn, err end
  local lowered = __protez_normalise(chunk)
  if lowered then
    local second, second_err = __protez_real_loadstring(lowered, chunkname)
    if second ~= nil then
      __protez_guard_record('luau-lowered', chunk, chunkname)
      return second, second_err
    end
  end
  return fn, err
end

local function __protez_safe_loadstring(chunk, chunkname)
  __protez_guard_record('loadstring', chunk, chunkname)
  if type(chunk) == 'string' then return __protez_load_any(chunk, chunkname) end
  return __protez_real_loadstring(chunk, chunkname)
end
loadstring = __protez_safe_loadstring
load = function(chunk, chunkname, mode, environment)
  -- Roblox/Luau `load` accepts a string as well as a function; Lua 5.1 does
  -- not, so route strings through loadstring and keep the capture.
  if type(chunk) == 'string' then
    __protez_guard_record('load', chunk, chunkname)
    return __protez_load_any(chunk, chunkname)
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
    -- The step budget belongs to Protez; scripts may not clear it.  The VM
    -- dump step rides along so the obfuscator's own tables are snapshotted.
    local vm_step = rawget(_G, '__protez_vm_step')
    if type(vm_step) == 'function' then
      local function __protez_combined_step(event, line)
        __protez_step_fn(event, line)
        vm_step(event, line)
      end
      return __protez_real_sethook(__protez_combined_step, '', __protez_hook_count())
    end
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

#: Runs between the executor prelude and the payload.  Everything reachable from
#: ``_G`` at this point belongs to Protez (its surface, the standard library, the
#: backend's own bookkeeping), never to the obfuscator, so the VM scanner can
#: skip it by tag.  Without this the scanner reported Protez's executor-name
#: list as an "instruction stream" -- a confident but completely wrong dump.
_TAG_PRELUDE_TABLES = r"""
do
  local marked, queue, head = {}, {}, 1
  local function tag(value, depth)
    if type(value) ~= 'table' or marked[value] then return end
    marked[value] = true
    if depth > 0 then rawset(value, '__protez_own', true) end
    if depth < 4 then queue[#queue + 1] = { value, depth } end
  end
  tag(_G, 0)
  while head <= #queue and #queue <= 4000 do
    local item = queue[head]
    head = head + 1
    local ok, keys = pcall(function()
      local found = {}
      local count = 0
      for key, value in pairs(item[1]) do
        count = count + 1
        if count > 512 then break end
        found[#found + 1] = value
      end
      return found
    end)
    if ok and type(keys) == 'table' then
      for index = 1, #keys do
        tag(keys[index], item[2] + 1)
      end
    end
  end
  -- Start the VM dumper's schedule at the payload's first instruction.
  local reset = rawget(_G, '__protez_vm_reset')
  if reset ~= nil then pcall(reset) end
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
    vm_tables: tuple[VmSnapshot, ...] = ()

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
    def instruction_stream(self) -> VmSnapshot | None:
        """The most instruction-stream-like table the obfuscator built."""
        return instruction_table(self.vm_tables)

    @property
    def constant_table(self) -> VmSnapshot | None:
        """The most constant-pool-like table the obfuscator built."""
        return constant_pool(self.vm_tables)

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


#: Slack added to the probe's wall clock before its child is killed: the budget
#: is enforced inside Lua, and this covers process start-up and a slow tail.
PROBE_SLACK_SECONDS = 5.0


def backend_terminates(
    source: str,
    *,
    timeout_seconds: float,
    max_instructions: int | None = None,
    logger: logging.Logger | None = None,
) -> bool | None:
    """Whether the portable backend finishes this script instead of hanging.

    A loader that catches the step-budget error and keeps looping cannot be
    stopped from inside its own Lua state: one C call (or a hook the script
    cleared) freezes the interpreter, and the library cannot take control back.
    The only reliable stop is process-level, so the script is first run in a
    forked child that is killed when the wall clock runs out.  ``None`` means
    process isolation is unavailable (Windows), and the caller should keep the
    previous behaviour of running the backend in-process.
    """
    if os.name == "nt" or not hasattr(os, "fork"):
        return None
    read_fd, write_fd = os.pipe()
    try:
        pid = os.fork()
    except OSError as exc:  # pragma: no cover - fork limits are environmental
        os.close(read_fd)
        os.close(write_fd)
        if logger is not None:
            logger.debug("Portable backend probe could not fork: %s", exc)
        return None
    if pid == 0:  # pragma: no cover - the child never returns to the test suite
        try:
            os.close(read_fd)
            verdict = b"0"
            try:
                if max_instructions is None:
                    emulator = LuaEmulator(timeout_seconds=timeout_seconds)
                else:
                    emulator = LuaEmulator(
                        timeout_seconds=timeout_seconds, max_instructions=max_instructions
                    )
                emulator.run(source)
                verdict = b"1"
            except BaseException:  # noqa: BLE001 - a failed probe is a "no"
                verdict = b"0"
            os.write(write_fd, verdict)
            os.close(write_fd)
        finally:
            os._exit(0)

    os.close(write_fd)
    deadline = time.monotonic() + timeout_seconds + PROBE_SLACK_SECONDS
    finished = False
    while time.monotonic() < deadline:
        try:
            done, _ = os.waitpid(pid, os.WNOHANG)
        except ChildProcessError:  # pragma: no cover - the child vanished
            done = pid
        if done == pid:
            finished = True
            break
        time.sleep(0.05)
    if not finished:
        try:
            os.kill(pid, signal.SIGKILL)
        except OSError:  # pragma: no cover - already gone
            pass
        try:
            os.waitpid(pid, 0)
        except ChildProcessError:  # pragma: no cover
            pass
    verdict = b""
    try:
        verdict = os.read(read_fd, 1)
    except OSError:  # pragma: no cover - nothing was written
        verdict = b""
    finally:
        os.close(read_fd)
    # Only a child that *returned a result* counts: a killed child, or one that
    # raised before finishing, must not be re-run in this process.
    return finished and verdict == b"1"


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
    def _luau_ready(self, runtime: Any, source: str) -> tuple[str, tuple[str, ...]]:
        """Return source the Lua 5.1 backend can actually compile.

        Every obfuscator in the Luraph family emits Luau: numeric separators
        (``0Xf5__e``), type arrows (``->``), ``continue``, compound assignment.
        Lua 5.1 rejects all of it, so a wrapper that would run fine under an
        executor failed here at the first line -- in the sweep this was the
        whole Luraph v14.6/v15.0 fixture set.

        The raw source is tried first (its layout is the one diagnostics should
        quote); only when it does not compile is the Luau lowering applied, and
        then only if the lowered source *does* compile.  Nothing is executed
        twice: the probe is ``loadstring``, which never runs the chunk.
        """
        if not source.strip():
            return source, ()
        try:
            from core.devirt.luau_normalize import luau_only_features, normalize_luau
        except Exception as exc:  # noqa: BLE001 - normaliser is optional
            self.logger.debug("Luau normaliser unavailable: %s", exc)
            return source, ()

        def compiles(text: str) -> bool:
            try:
                loader = runtime.eval("loadstring")
                outcome = loader(text)
            except Exception:  # noqa: BLE001 - a failed probe is just "no"
                return False
            # ``loadstring`` returns ``(nil, message)`` on a syntax error; the
            # bridge hands that back as a tuple, so "not None" is not enough.
            if isinstance(outcome, tuple):
                return bool(outcome) and outcome[0] is not None
            return outcome is not None

        if compiles(source):
            return source, ()
        # The lowering is attempted whenever the raw source does not compile:
        # the feature detector knows the common markers but not every construct
        # (an if-expression, for one), and a missed marker would leave the run
        # failing on a syntax error it could have handled.
        features = luau_only_features(source)
        try:
            normalized = normalize_luau(source)
        except Exception as exc:  # noqa: BLE001 - keep the original then
            return source, (f"Luau syntax could not be lowered ({exc})",)
        if normalized.source == source or not compiles(normalized.source):
            if not features:
                return source, ()
            return source, (
                "the loader uses Luau syntax the Lua 5.1 backend cannot compile: "
                + ", ".join(features[:6]),
            )
        note = (
            "Luau syntax lowered to plain Lua before the run: "
            + ", ".join(normalized.applied or features[:6])
        )
        return normalized.source, (note,)

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
            "escalations": 0,
            "stopped": None,
            "fetches": [],
            "requests": [],
            "writes": [],
            "inputs": [],
            "clipboard": "",
            "vm_tables": [],
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

        positions: list[str] = []
        position_log = os.environ.get("PROTEZ_EMU_POSITIONS")

        def note_position(kind: Any, source: Any, line: Any, what: Any = "") -> None:
            """Record where the script was, on request and when the budget runs out."""
            entry = "%d %s %s:%s %s" % (
                state["instructions"] * HOOK_STEP, kind, source, line, what
            )
            positions.append(entry)
            del positions[:-16]
            if position_log:
                try:
                    with open(position_log, "a", encoding="utf-8") as handle:
                        handle.write(entry + "\n")
                except OSError:  # pragma: no cover - diagnostics only
                    pass

        def step_hook() -> str | None:
            """Count a step and stop a script that keeps catching the stop.

            The first trip hands the decision back to Lua, which neuters every
            ``pcall`` it can reach before raising: otherwise a loader that wraps
            its loop in ``pcall`` simply retries and the run never ends.  While
            the script keeps running, every later trip escalates again, so
            handlers created since the last pass are caught too.
            """
            state["instructions"] += 1
            if state["stopped"] is None:
                if state["instructions"] > self.max_instructions:
                    state["stopped"] = "instruction budget"
                elif time.monotonic() > deadline:
                    state["stopped"] = "time budget"
            if state["stopped"] is not None:
                escalations = state["escalations"]
                if escalations == 0 or state["instructions"] - escalations >= ESCALATE_EVERY:
                    state["escalations"] = state["instructions"]
                    return "escalate"
                raise RuntimeError(f"Protez stopped by the {state['stopped']}")
            return "trace" if position_log else None

        def clock() -> float:
            return time.monotonic() - started

        def wall_time() -> float:
            return time.time()

        def hook_count() -> int:
            return HOOK_STEP

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

        def vm_table(kind: Any, label: Any, payload: Any, count: Any = 0, width: Any = 1) -> bool:
            """Receive a snapshot of a table the obfuscator built for its VM."""
            if len(state["vm_tables"]) >= MAX_VM_TABLES:
                return False
            snapshot = snapshot_from_bridge(kind, label, payload, count, width)
            if snapshot is None:
                return False
            state["vm_tables"].append(snapshot)
            self.logger.debug("VM snapshot: %s", snapshot.describe())
            return True

        try:
            # Lua strings are byte strings.  ``latin-1`` is the only codec that
            # round-trips every byte, so a Roblox loader may hand the host raw
            # binary (dumped chunks, packed tables) without failing the run.
            runtime = lua_module.LuaRuntime(
                unpack_returned_tuples=True, encoding="latin-1"
            )
        except Exception as exc:  # noqa: BLE001
            return EmulatorResult(
                status="unavailable", error=str(exc), profile=self.profile.key
            )

        globals_table = runtime.globals()
        globals_table["__protez_record"] = record
        globals_table["__protez_record_print"] = record_print
        globals_table["__protez_step"] = step_hook
        if position_log:
            globals_table["__protez_note_position"] = note_position
        globals_table["__protez_clock"] = clock
        globals_table["__protez_time"] = wall_time
        globals_table["__protez_hook_count"] = hook_count
        globals_table["__protez_vm_table"] = vm_table
        globals_table["__protez_http"] = http
        globals_table["__protez_request"] = request
        globals_table["__protez_fs"] = fs_bridge
        globals_table["__protez_clipboard"] = clipboard
        globals_table["__protez_hwid"] = hwid
        globals_table["__protez_hash"] = hash_text
        globals_table["__protez_decompile"] = decompile
        globals_table["__protez_input"] = input_event

        def normalise_luau(chunk: Any) -> str | None:
            """Lower Luau-only syntax in a captured payload, for ``loadstring``."""
            try:
                from core.devirt.luau_normalize import normalize_luau

                lowered = normalize_luau(str(chunk)).source
            except Exception as exc:  # noqa: BLE001 - a payload that cannot be
                # lowered still gets recorded; it simply cannot be executed.
                self.logger.debug("Luau lowering failed for a payload: %s", exc)
                return None
            return lowered if lowered != str(chunk) else None

        globals_table["__protez_normalise_luau"] = normalise_luau
        # Luau ships string.pack/unpack; Lua 5.1 does not, and Roblox loaders
        # probe for them before they decode anything (IronBrew3 refuses to run).
        try:
            from core.luau_compat import install_string_pack

            install_string_pack(runtime)
        except Exception as exc:  # noqa: BLE001 - a missing gap must not fail the run
            self.logger.debug("string.pack compat install failed: %s", exc)

        status = "completed"
        error: str | None = None
        # The Luau check runs before the bootstrap replaces ``loadstring``: the
        # probe compiles a copy of the whole script, and going through the
        # instrumented loader would record that copy as a payload capture.
        variant, luau_notes = self._luau_ready(runtime, source)
        try:
            # Order matters.  Protez's own code runs *before* the step hook is
            # installed: the hook counts instructions and drives the VM dumper,
            # and charging the executor prelude (thousands of statements) to
            # that schedule used to leave the dumper scanning its own tables
            # while the payload went unobserved.
            runtime.execute((_SAFE_OS + "\n" + _LUA_BOOTSTRAP).encode("utf-8"))
            if os.environ.get("PROTEZ_EMU_NO_VM_DUMP") != "1":
                runtime.execute(VM_DUMP_LUA.encode("utf-8"))
            runtime.execute(self._prelude.encode("latin-1", "replace"))
            runtime.execute(_TAG_PRELUDE_TABLES.encode("utf-8"))
            # The budget and the VM dumper start with the payload's first step.
            runtime.execute("debug.sethook()")
            if os.environ.get("PROTEZ_EMU_DIAGNOSE"):
                # A loader that dies on "arithmetic on a nil value" usually read
                # a global this environment does not define.  Recording the
                # misses turns that hunt into a list.
                runtime.execute(
                    b"local __protez_missing = {}\n"
                    b"local __protez_missing_where = {}\n"
                    b"setmetatable(_G, { __index = function(_, key)\n"
                    b"  if type(key) == 'string' then\n"
                    b"    __protez_missing[key] = (__protez_missing[key] or 0) + 1\n"
                    b"    if __protez_missing_where[key] == nil then\n"
                    b"      local info = debug.getinfo(2, 'Sl')\n"
                    b"      __protez_missing_where[key] = tostring(info and info.short_src or '?')\n"
                    b"        .. ':' .. tostring(info and info.currentline or -1)\n"
                    b"    end\n"
                    b"  end\n"
                    b"  return nil\n"
                    b"end })\n"
                    b"rawset(_G, '__protez_missing', __protez_missing)\n"
                    b"rawset(_G, '__protez_missing_where', __protez_missing_where)"
                )
            # The bridge is latin-1, so the payload must travel back as the very
            # bytes the file had; ``utf-8`` would inflate every byte above 0x7f.
            if os.environ.get("PROTEZ_EMU_TRACEBACK") == "1":
                globals_table["__protez_payload_source"] = variant
                runtime.execute(
                    b"local ok, message = __protez_run_payload()\n"
                    b"if not ok then error(message, 0) end\n"
                )
            else:
                runtime.execute(variant.encode("latin-1", "replace"))
        except Exception as exc:  # noqa: BLE001 - LuaError and Python errors alike
            if os.environ.get("PROTEZ_EMU_TB"):
                import traceback

                traceback.print_exc()
            status = "limit" if state["stopped"] else "error"
            error = str(exc)
            if state["stopped"]:
                error = f"{error} (stopped by the {state['stopped']})"
            if status == "error" and self.logger:
                self.logger.debug("Portable backend stopped: %s", error)

        try:
            # A last sweep: tables the loader was still filling when the run
            # ended are recorded at their final size.
            runtime.eval("__protez_vm_scan_now and __protez_vm_scan_now()")
        except Exception:  # noqa: BLE001 - the sweep is best effort
            pass

        vm_stats: tuple[int, int, int, int] = (0, 0, 0, 0)
        try:
            stats = runtime.eval("__protez_vm_stats and __protez_vm_stats() or nil")
            if stats is not None:
                vm_stats = tuple(int(value) for value in stats)  # type: ignore[assignment]
        except Exception:  # noqa: BLE001 - diagnostics only
            pass

        duration = time.monotonic() - started
        notes = [f"portable backend: {runtime_label}", f"executor profile: {self.profile.label}"]
        if os.environ.get("PROTEZ_EMU_DIAGNOSE"):
            try:
                missing = runtime.eval("__protez_missing")
                entries = [(str(key), int(value)) for key, value in (missing or {}).items()]
            except Exception:  # noqa: BLE001 - diagnostics must never fail a run
                entries = []
            entries.sort(key=lambda item: (-item[1], item[0]))
            if entries:
                try:
                    where = {
                        str(key): str(value)
                        for key, value in (runtime.eval("__protez_missing_where") or {}).items()
                    }
                except Exception:  # noqa: BLE001 - diagnostics only
                    where = {}
                notes.append(
                    "globals the loader read but the environment does not define: "
                    + ", ".join(
                        f"{name} ({count} at {where.get(name, '?')})" for name, count in entries[:12]
                    )
                )
        notes.extend(note for note in luau_notes if note not in notes)
        if state["fetches"]:
            notes.append(f"{len(state['fetches'])} HTTP request(s) issued by the loader")
        if state["writes"]:
            notes.append(f"{len(state['writes'])} file(s) written to the executor workspace")
        if state["inputs"]:
            notes.append(f"{len(state['inputs'])} input event(s) recorded, none delivered")
        if state["vm_tables"]:
            notes.append(
                f"{len(state['vm_tables'])} VM table(s) snapshotted from the running loader"
            )
        elif vm_stats[1]:
            self.logger.debug(
                "VM dumper ran %s scan(s) over %s hook event(s) without a match",
                vm_stats[1],
                vm_stats[0],
            )
        if positions:
            # Where the loader was every time it swallowed the step budget.
            notes.append("budget spent at: " + "; ".join(positions[-4:]))
        return EmulatorResult(
            status=status,
            captures=tuple(captures),
            error=error,
            instructions=state["instructions"] * HOOK_STEP,
            duration_seconds=duration,
            runtime=runtime_label,
            profile=self.profile.key,
            notes=tuple(notes),
            fetches=tuple(dict.fromkeys(state["fetches"])),
            requests=tuple(state["requests"]),
            written_files=tuple(state["writes"]),
            vm_tables=tuple(state["vm_tables"]),
        )
