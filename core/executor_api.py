"""Full executor API surface used by the ``Real`` injector profile.

The scripts Protez has to survive are written for a real Roblox executor: they
bootstrap with ``identifyexecutor()``, cache a workspace through ``writefile``,
authenticate with ``request{Headers=..., Body=...}``, hash the machine id with
``crypt.hash``, hook ``__namecall`` to watch ``HttpGet`` and dump whatever the
loader decrypts.  Every one of those calls has to succeed and behave sensibly,
otherwise the wrapper stops before it reveals anything.

This module holds the Lua half of that environment.  It is deliberately plain
Lua 5.1 so the *same* text runs in the bundled Luau worker and in the portable
``lupa`` backend, and it never grants real power on its own:

* the filesystem is a per-run workspace (in-memory, mirrored to disk through a
  host bridge when one is available) so ``writefile`` output can be captured;
* HTTP goes through the caller's fetch bridge; by default it returns nothing;
* input, hook and render APIs record what the script asked for instead of
  performing it.

The Python half (workspace paths, capture classification, bridges) lives in
:mod:`core.emulator`, :mod:`core.remote_payloads` and :mod:`core.pipeline`.
"""

from __future__ import annotations

import hashlib
import re
from typing import Iterable

__all__ = [
    "EXECUTOR_API_SURFACE",
    "WORKSPACE_MAX_FILE_BYTES",
    "WORKSPACE_MAX_FILES",
    "classify_written_file",
    "looks_like_lua_source",
    "normalise_workspace_path",
    "workspace_file_name",
]

WORKSPACE_MAX_FILE_BYTES = 8 * 1024 * 1024
WORKSPACE_MAX_FILES = 256

_LUA_HEADER = b"\x1bLua"
_LUAU_HEADER = b"\x1bLuau"
_LUA_KEYWORDS = re.compile(
    r"\b(local|function|return|then|end|for|while|repeat|until|if|elseif|else|do|"
    r"print|loadstring|game|script|task)\b"
)


def normalise_workspace_path(path: str) -> str:
    """Return a safe, relative workspace path for ``path``.

    Executor paths are workspace-relative; ``..`` segments and absolute roots
    are stripped so a script cannot escape the run directory.
    """
    text = str(path or "").replace("\\", "/")
    segments: list[str] = []
    for segment in text.split("/"):
        if segment in {"", ".", ".."}:
            if segment == ".." and segments:
                segments.pop()
            continue
        cleaned = re.sub(r"[^0-9A-Za-z._@%+=()\[\]{}~!$&,#;'` -]", "_", segment)
        cleaned = cleaned.strip().replace("\x00", "")
        if cleaned:
            segments.append(cleaned)
    return "/".join(segments) or "unnamed"


def workspace_file_name(path: str, *, index: int = 1) -> str:
    """Name for a file parked under ``logs/`` for cross-process bridge calls."""
    safe = normalise_workspace_path(path).replace("/", "__")
    digest = hashlib.sha256(str(path).encode("utf-8", "replace")).hexdigest()[:8]
    return f"{index:03d}_{digest}_{safe}"[:120]


def looks_like_lua_source(text: str) -> bool:
    """True when ``text`` looks like Lua/Luau source rather than data."""
    if not text or len(text) < 12:
        return False
    head = text[:4000]
    if head.startswith("--"):
        return True
    if len(text) > 40 and _LUA_KEYWORDS.search(head):
        return True
    return False


def classify_written_file(path: str, data: str | bytes) -> str:
    """Classify content written by a script: ``bytecode``, ``source`` or ``data``."""
    raw = data.encode("latin-1", "ignore") if isinstance(data, str) else bytes(data)
    if raw.startswith(_LUA_HEADER) or raw.startswith(_LUAU_HEADER):
        return "bytecode"
    lowered = str(path).lower()
    if lowered.endswith((".luac", ".luauc", ".lbc", ".bin")):
        return "bytecode"
    text = data if isinstance(data, str) else raw.decode("utf-8", "replace")
    if lowered.endswith((".lua", ".luau", ".lua.txt")) or looks_like_lua_source(text):
        return "source"
    return "data"


def iter_workspace_files(store: dict[str, str]) -> Iterable[tuple[str, str]]:
    """Yield ``(path, content)`` for every file in a mirrored workspace store."""
    for path, content in store.items():
        yield path, content


# ---------------------------------------------------------------------------
# Lua surface
# ---------------------------------------------------------------------------

EXECUTOR_API_SURFACE = r"""-- ---------------------------------------------------------------------------
-- Real executor runtime: files, HTTP tables, hooks, HWID, crypt, input and
-- every "does this executor support X" probe a protected script can make.
-- Behavior is real enough for the wrapper to finish; side effects stay inside
-- the run (workspace files, recorded input) unless the host wires a bridge.
-- ---------------------------------------------------------------------------
local __protez_real = {}
local __protez_state = rawget(_G, '__protez_executor_state')
if type(__protez_state) ~= 'table' then
  __protez_state = {
    identity = 8,
    fpscap = 60,
    hwid = nil,
    clipboard = '',
    teleport_queue = {},
    writes = {},
    hooks = {},
    calls = {},
  }
  rawset(_G, '__protez_executor_state', __protez_state)
end

-- Overwrite earlier inert stubs with the working implementation.
local function __protez_set(key, value)
  rawset(_G, key, value)
  __protez_globals[key] = value
  return value
end
local function __protez_host(name)
  local value = rawget(_G, name)
  if type(value) == 'function' or type(value) == 'userdata' then return value end
  return nil
end
local function __protez_call_host(name, ...)
  local fn = __protez_host(name)
  if fn == nil then return nil end
  local ok, value = pcall(fn, ...)
  if ok then return value end
  return nil
end
local function __protez_record(kind, detail)
  local list = __protez_state.calls
  if #list < 400 then
    list[#list + 1] = tostring(kind) .. ':' .. tostring(detail)
  end
end

-- ---------------------------------------------------------------------------
-- Workspace filesystem (writefile/readfile/isfile/... and loadfile/dofile)
-- ---------------------------------------------------------------------------
local __protez_fs_store = rawget(_G, '__protez_fs_store')
if type(__protez_fs_store) ~= 'table' then
  __protez_fs_store = {}
  rawset(_G, '__protez_fs_store', __protez_fs_store)
end
local __protez_fs_folders = rawget(_G, '__protez_fs_folders')
if type(__protez_fs_folders) ~= 'table' then
  __protez_fs_folders = {}
  rawset(_G, '__protez_fs_folders', __protez_fs_folders)
end
local __protez_fs_bridge = rawget(_G, '__protez_fs')

local function __protez_fs_normalize(path)
  local text = tostring(path or ''):gsub('\\', '/')
  local parts = {}
  for part in text:gmatch('[^/]+') do
    if part == '..' then
      if #parts > 0 then table.remove(parts) end
    elseif part ~= '.' then
      parts[#parts + 1] = part
    end
  end
  local joined = table.concat(parts, '/')
  if joined == '' then joined = 'unnamed' end
  return joined
end
local function __protez_fs_host(op, ...)
  if __protez_is_host_callable(__protez_fs_bridge) then
    return __protez_call_host('__protez_fs', op, ...)
  end
  return nil
end
local function __protez_fs_parents(path)
  local folder = path:match('^(.*)/[^/]*$')
  while folder and folder ~= '' do
    __protez_fs_folders[folder] = true
    folder = folder:match('^(.*)/[^/]*$')
  end
end

local function __protez_write_file(path, data, append)
  local key = __protez_fs_normalize(path)
  if type(data) ~= 'string' then data = tostring(data) end
  if append and type(__protez_fs_store[key]) == 'string' then
    __protez_fs_store[key] = __protez_fs_store[key] .. data
  else
    __protez_fs_store[key] = data
  end
  __protez_fs_parents(key)
  __protez_fs_host('write', key, data, append and 'append' or 'write')
  __protez_record('writefile', key .. ' (' .. tostring(#data) .. ' bytes)')
  return true
end
local function __protez_read_file(path)
  local key = __protez_fs_normalize(path)
  local value = __protez_fs_store[key]
  if type(value) == 'string' then return value end
  local host = __protez_fs_host('read', key)
  if type(host) == 'string' then
    __protez_fs_store[key] = host
    return host
  end
  return ''
end
local function __protez_isfile(path)
  local key = __protez_fs_normalize(path)
  if type(__protez_fs_store[key]) == 'string' then return true end
  return __protez_fs_host('isfile', key) == true
end
local function __protez_isfolder(path)
  local key = __protez_fs_normalize(path)
  if __protez_fs_folders[key] then return true end
  if __protez_fs_host('isfolder', key) == true then return true end
  local prefix = key .. '/'
  for stored in pairs(__protez_fs_store) do
    if stored:sub(1, #prefix) == prefix then return true end
  end
  return false
end
local function __protez_makefolder(path)
  local key = __protez_fs_normalize(path)
  __protez_fs_folders[key] = true
  __protez_fs_parents(key)
  __protez_fs_host('makefolder', key)
  return true
end
local function __protez_delfile(path)
  local key = __protez_fs_normalize(path)
  __protez_fs_store[key] = nil
  __protez_fs_host('delfile', key)
  return true
end
local function __protez_delfolder(path)
  local key = __protez_fs_normalize(path)
  __protez_fs_folders[key] = nil
  __protez_fs_host('delfolder', key)
  return true
end
local function __protez_listfiles(path)
  local key = __protez_fs_normalize(path)
  local prefix = (key == 'unnamed' or key == '') and '' or (key .. '/')
  local listed, seen = {}, {}
  for stored in pairs(__protez_fs_store) do
    if prefix == '' or stored:sub(1, #prefix) == prefix then
      if not seen[stored] then
        seen[stored] = true
        listed[#listed + 1] = stored
      end
    end
  end
  for folder in pairs(__protez_fs_folders) do
    if prefix ~= '' and folder:sub(1, #prefix) == prefix and folder ~= key then
      if not seen[folder] then
        seen[folder] = true
        listed[#listed + 1] = folder
      end
    end
  end
  table.sort(listed)
  return listed
end
local function __protez_loadfile(path)
  local chunk, err = loadstring(__protez_read_file(path), '@' .. __protez_fs_normalize(path))
  if chunk == nil then return nil, tostring(err) end
  return chunk
end
local function __protez_dofile(path)
  local chunk, err = __protez_loadfile(path)
  if chunk == nil then return nil, err end
  return chunk()
end
local function __protez_custom_asset(path)
  local key = __protez_fs_normalize(path)
  local host = __protez_fs_host('customasset', key)
  if type(host) == 'string' and host ~= '' then return host end
  local digest = tostring(#key) .. tostring(#__protez_read_file(key))
  return 'rbxasset://protez/' .. digest .. '_' .. key:gsub('[^%w]', '_')
end

__protez_set('writefile', __protez_write_file)
__protez_set('appendfile', function(path, data) return __protez_write_file(path, data, true) end)
__protez_set('readfile', __protez_read_file)
__protez_set('isfile', __protez_isfile)
__protez_set('isfolder', __protez_isfolder)
__protez_set('makefolder', __protez_makefolder)
__protez_set('delfile', __protez_delfile)
__protez_set('delfolder', __protez_delfolder)
__protez_set('listfiles', __protez_listfiles)
__protez_set('loadfile', __protez_loadfile)
__protez_set('dofile', __protez_dofile)
__protez_set('getcustomasset', __protez_custom_asset)
__protez_set('getcustomassetasync', __protez_custom_asset)
__protez_set('setclipboard', function(value)
  __protez_state.clipboard = tostring(value or '')
  __protez_call_host('__protez_clipboard', 'set', __protez_state.clipboard)
  __protez_record('setclipboard', tostring(#__protez_state.clipboard) .. ' bytes')
  return true
end)
__protez_set('toclipboard', rawget(_G, 'setclipboard'))
__protez_set('setrbxclipboard', rawget(_G, 'setclipboard'))
__protez_set('getclipboard', function()
  local host = __protez_call_host('__protez_clipboard', 'get')
  if type(host) == 'string' then return host end
  return __protez_state.clipboard
end)

-- ---------------------------------------------------------------------------
-- HTTP: request tables, http_get helpers, raw bridge access
-- ---------------------------------------------------------------------------
local function __protez_normalize_headers(headers)
  if type(headers) ~= 'table' then return nil end
  local copy = {}
  for key, value in pairs(headers) do
    copy[tostring(key)] = tostring(value)
  end
  return copy
end
local function __protez_http_request(options)
  if type(options) == 'string' then options = { Url = options } end
  if type(options) ~= 'table' then options = { Url = tostring(options or '') } end
  local url = options.Url or options.url or options.URL
  if url == nil then
    return { StatusCode = 0, StatusMessage = 'Bad Request', Body = '', Headers = {}, Success = false }
  end
  local request = {
    Url = tostring(url),
    Method = tostring(options.Method or options.method or 'GET'):upper(),
    Headers = __protez_normalize_headers(options.Headers or options.headers) or {},
    Body = options.Body or options.body,
    Compress = options.Compress,
  }
  if request.Body ~= nil and type(request.Body) ~= 'string' then request.Body = tostring(request.Body) end
  __protez_record('request', request.Method .. ' ' .. request.Url)
  local host_response = __protez_call_host('__protez_request', request)
  if type(host_response) == 'table' or type(host_response) == 'userdata' then
    local body = host_response.Body
    if body == nil then body = host_response.body end
    if type(body) == 'string' then
      return {
        StatusCode = tonumber(host_response.StatusCode or host_response.status_code) or 200,
        StatusMessage = tostring(host_response.StatusMessage or host_response.status_message or 'OK'),
        Headers = host_response.Headers or {},
        Body = body,
        Success = host_response.Success ~= false,
      }
    end
  end
  local body = __protez_fetch(request.Url, request.Method)
  return {
    StatusCode = 200,
    StatusMessage = 'OK',
    Headers = {},
    Body = type(body) == 'string' and body or '',
    Success = true,
  }
end
local function __protez_http_get(url, _norestore)
  return __protez_http_request({ Url = url, Method = 'GET' }).Body
end
local function __protez_http_post(url, body, headers)
  return __protez_http_request({ Url = url, Method = 'POST', Body = body, Headers = headers }).Body
end

__protez_set('request', __protez_http_request)
__protez_set('http_request', __protez_http_request)
__protez_set('httprequest', __protez_http_request)
__protez_set('requestasync', __protez_http_request)
__protez_set('httpget', __protez_http_get)
__protez_set('http_get', __protez_http_get)
__protez_set('HttpGet', __protez_http_get)
__protez_set('HttpGetAsync', __protez_http_get)
__protez_set('httpgetasync', __protez_http_get)
__protez_set('http_post', __protez_http_post)
__protez_set('http', { get = __protez_http_get, post = __protez_http_post, request = __protez_http_request })
__protez_set('fetch', __protez_http_get)

-- ---------------------------------------------------------------------------
-- HWID, identity, timing
-- ---------------------------------------------------------------------------
local function __protez_hwid()
  if type(__protez_state.hwid) == 'string' then return __protez_state.hwid end
  local host = __protez_call_host('__protez_hwid')
  if type(host) == 'string' and host ~= '' then
    __protez_state.hwid = host
    return host
  end
  __protez_state.hwid = 'PROTEZ-REAL-0123456789ABCDEF0123456789ABCDEF'
  return __protez_state.hwid
end
local function __protez_now()
  local value = __protez_call_host('__protez_time')
  if type(value) == 'number' then return value end
  local os_table = rawget(_G, 'os')
  if type(os_table) == 'table' and type(os_table.time) == 'function' then
    local ok, seconds = pcall(os_table.time)
    if ok and type(seconds) == 'number' then return seconds end
  end
  return 1735689600
end
local function __protez_civil_from_days(days)
  local z = days + 719468
  local era = math.floor(z / 146097)
  local doe = z - era * 146097
  local yoe = math.floor((doe - math.floor(doe / 1460) + math.floor(doe / 36524) - math.floor(doe / 146096)) / 365)
  local y = yoe + era * 400
  local doy = doe - (365 * yoe + math.floor(yoe / 4) - math.floor(yoe / 100))
  local mp = math.floor((5 * doy + 2) / 153)
  local d = doy - math.floor((153 * mp + 2) / 5) + 1
  local m = mp + (mp < 10 and 3 or -9)
  if m <= 2 then y = y + 1 end
  return y, m, d
end
local __protez_weekdays = { 'Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday' }
local __protez_months = {
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
}
local function __protez_os_date(format, timestamp)
  local seconds = tonumber(timestamp) or __protez_now()
  local days = math.floor(seconds / 86400)
  local rest = seconds - days * 86400
  local year, month, day = __protez_civil_from_days(days)
  local hour = math.floor(rest / 3600)
  local minute = math.floor((rest - hour * 3600) / 60)
  local second = math.floor(rest - hour * 3600 - minute * 60)
  local weekday = __protez_weekdays[(days % 7) + 2]
  if weekday == nil then weekday = __protez_weekdays[1] end
  local replacements = {
    Y = string.format('%04d', year),
    y = string.format('%02d', year % 100),
    m = string.format('%02d', month),
    d = string.format('%02d', day),
    H = string.format('%02d', hour),
    M = string.format('%02d', minute),
    S = string.format('%02d', second),
    p = hour < 12 and 'AM' or 'PM',
    A = weekday,
    a = weekday:sub(1, 3),
    B = __protez_months[month],
    b = __protez_months[month]:sub(1, 3),
    c = string.format('%s %s %2d %02d:%02d:%02d %04d', weekday:sub(1, 3),
      __protez_months[month]:sub(1, 3), day, hour, minute, second, year),
    X = string.format('%02d:%02d:%02d', hour, minute, second),
    x = string.format('%02d/%02d/%02d', month, day, year % 100),
  }
  if type(format) ~= 'string' then format = '%c' end
  local converted = format:gsub('%%([%a%%])', function(code)
    if code == '%' then return '%' end
    return replacements[code] or code
  end)
  if format:sub(1, 1) == '!' then converted = converted:sub(2) end
  return converted
end

__protez_set('gethwid', __protez_hwid)
__protez_set('get_hwid', __protez_hwid)
__protez_set('getusername', function() return 'Protez' end)
__protez_set('getuserid', function() return 1 end)
__protez_set('identifyexecutor', function() return __protez_profile.executor end)
__protez_set('getexecutorname', function() return __protez_profile.executor end)
__protez_set('getexecutor', function() return __protez_profile.executor end)
__protez_set('getexploit', function() return __protez_profile.executor end)
__protez_set('get_exploit', function() return __protez_profile.executor end)
__protez_set('getversion', function() return __protez_profile.version end)
__protez_set('getexecutorversion', function() return __protez_profile.version end)
__protez_set('gettenv', function() return rawget(_G, '__protez_globals') end)
__protez_set('requiress', function(name) return rawget(_G, tostring(name)) end)
__protez_set('getgenv', function() return __protez_globals end)
__protez_set('getrenv', function() return _G end)
__protez_set('getidentity', function() return __protez_state.identity end)
__protez_set('getthreadidentity', function() return __protez_state.identity end)
__protez_set('getthreadcontext', function() return __protez_state.identity end)
__protez_set('setidentity', function(value)
  __protez_state.identity = tonumber(value) or 8
  return __protez_state.identity
end)
__protez_set('setthreadidentity', rawget(_G, 'setidentity'))
__protez_set('setthreadcontext', rawget(_G, 'setidentity'))
__protez_set('printidentity', function(prefix)
  print(tostring(prefix or '') .. 'Current identity is ' .. tostring(__protez_state.identity))
end)
__protez_set('getfpscap', function() return __protez_state.fpscap end)
__protez_set('setfpscap', function(value)
  __protez_state.fpscap = tonumber(value) or 60
  return __protez_state.fpscap
end)
__protez_set('getping', function() return 42 end)
__protez_set('getserverping', function() return 42 end)
__protez_set('tick', function() return __protez_now() end)
__protez_set('time', function() return __protez_now() end)
__protez_set('elapsedTime', function() return 0.0 end)
__protez_set('getmemoryusage', function() return 512 end)

local __protez_os = rawget(_G, 'os')
if type(__protez_os) ~= 'table' then
  __protez_os = {}
  rawset(_G, 'os', __protez_os)
end
rawset(__protez_os, 'time', function() return __protez_now() end)
rawset(__protez_os, 'date', __protez_os_date)
rawset(__protez_os, 'clock', function()
  local host = __protez_call_host('__protez_clock')
  if type(host) == 'number' then return host end
  return 0.0
end)
rawset(__protez_os, 'difftime', function(a, b) return (tonumber(a) or 0) - (tonumber(b) or 0) end)

-- ---------------------------------------------------------------------------
-- Hooks, closures, metatables, debugging helpers
-- ---------------------------------------------------------------------------
local __protez_namecall = { method = '', hook = nil, default = nil }
local function __protez_dispatch(self, name, default_callable, ...)
  __protez_namecall.method = tostring(name)
  __protez_namecall.default = default_callable
  -- Hooks arrive either through `hookmetamethod(game, '__namecall', hook)` or
  -- through the classic `getrawmetatable(game).__namecall = hook` swap.
  local hook = __protez_namecall.hook
  if hook == nil then
    local meta = getmetatable(self)
    if type(meta) == 'table' then hook = rawget(meta, '__namecall') end
    if hook == __protez_default_namecall then hook = nil end
  end
  local result
  if type(hook) == 'function' then
    rawset(_G, '__protez_namecall_default', default_callable)
    local ok, value = pcall(hook, self, ...)
    rawset(_G, '__protez_namecall_default', nil)
    if ok then
      result = value
    else
      __protez_record('namecall-error', tostring(value))
      result = default_callable()
    end
  else
    result = default_callable()
  end
  __protez_namecall.method = ''
  __protez_namecall.default = nil
  return result
end
local function __protez_namecall_original(_self, ...)
  local default_callable = __protez_namecall.default
  if type(default_callable) == 'function' then return default_callable() end
  return nil
end
local __protez_default_namecall = rawget(_G, '__protez_default_namecall')
rawset(_G, '__protez_namecall_invoke', __protez_dispatch)

local function __protez_hookfunction(target, replacement)
  if type(replacement) ~= 'function' then return target end
  local ledger = __protez_state.hooks
  ledger[#ledger + 1] = { target = target, replacement = replacement }
  __protez_record('hookfunction', tostring(replacement))
  return target
end
local function __protez_hash_text(value)
  local text = tostring(value or '')
  local hash = 5381
  for index = 1, #text do
    hash = (hash * 33 + text:byte(index)) % 4294967296
  end
  return string.format('%08x', hash)
end
local __protez_debug = rawget(_G, 'debug')
if type(__protez_debug) ~= 'table' then
  __protez_debug = {}
  rawset(_G, 'debug', __protez_debug)
end
local function __protez_debug_call(func, ...)
  if type(__protez_debug[func]) ~= 'function' then return nil end
  local ok, value = pcall(__protez_debug[func], ...)
  if ok then return value end
  return nil
end

__protez_set('newcclosure', function(fn) return fn end)
__protez_set('newlclosure', function(fn) return fn end)
__protez_set('clonefunction', function(fn) return fn end)
__protez_set('hookfunction', __protez_hookfunction)
__protez_set('replaceclosure', function(target, replacement)
  __protez_hookfunction(target, replacement)
  return target
end)
__protez_set('restorefunction', function(target) return target end)
__protez_set('hookmetamethod', function(object, method, hook)
  local name = tostring(method)
  if name == '__namecall' then
    __protez_namecall.hook = hook
    local meta = getmetatable(object)
    if type(meta) == 'table' then
      local previous = rawget(meta, name)
      pcall(rawset, meta, name, hook)
      if type(previous) == 'function' then return previous end
    end
    return __protez_namecall_original
  end
  local existing = getmetatable(object)
  if type(existing) == 'table' and type(hook) == 'function' then
    local previous = rawget(existing, name)
    if rawget(existing, '__protez_hooked') == nil then
      rawset(existing, '__protez_hooked', {})
    end
    rawset(rawget(existing, '__protez_hooked'), name, hook)
    local wrapper = function(self, ...)
      local ok, value = pcall(hook, self, ...)
      if ok and value ~= nil then return value end
      if not ok then __protez_record('metamethod-error', name .. ': ' .. tostring(value)) end
      if previous ~= nil then return previous(self, ...) end
      return nil
    end
    pcall(rawset, existing, name, wrapper)
    return previous or __protez_noop
  end
  return __protez_noop
end)
__protez_set('getnamecallmethod', function() return __protez_namecall.method end)
__protez_set('setnamecallmethod', function(name) __protez_namecall.method = tostring(name or '') end)
__protez_set('checkcaller', function() return true end)
__protez_set('iscclosure', function(fn) return false end)
__protez_set('islclosure', function(fn) return true end)
__protez_set('isexecutorclosure', function(fn) return true end)
__protez_set('isourclosure', function(fn) return true end)
__protez_set('getrawmetatable', function(value)
  local meta = __protez_debug_call('getmetatable', value)
  if meta == nil then meta = getmetatable(value) end
  return meta
end)
__protez_set('setrawmetatable', function(value, meta)
  if type(__protez_debug.setmetatable) == 'function' then
    local ok = pcall(__protez_debug.setmetatable, value, meta)
    if ok then return true end
  end
  local ok = pcall(setmetatable, value, meta)
  return ok and true or false
end)
__protez_set('setreadonly', function(value, readonly) return true end)
__protez_set('isreadonly', function(value) return false end)
__protez_set('make_writeable', function(value) return true end)
__protez_set('getupvalue', function(fn, index) return __protez_debug_call('getupvalue', fn, index) end)
__protez_set('setupvalue', function(fn, index, value)
  if index == nil then return nil end
  return __protez_debug_call('setupvalue', fn, index, value)
end)
__protez_set('getupvalues', function(fn)
  local values = {}
  for index = 1, 64 do
    local name, value = __protez_debug_call('getupvalue', fn, index)
    if name == nil then break end
    values[index] = { Name = name, Value = value }
  end
  return values
end)
__protez_set('getconstants', function(fn)
  local constants = __protez_debug_call('getconstants', fn)
  if type(constants) == 'table' then return constants end
  return {}
end)
__protez_set('getconstant', function(fn, index) return __protez_debug_call('getconstant', fn, index) end)
__protez_set('setconstant', function(fn, index, value) return true end)
__protez_set('getprotos', function(fn)
  local protos = __protez_debug_call('getprotos', fn)
  if type(protos) == 'table' then return protos end
  return { fn }
end)
__protez_set('getproto', function(fn, index)
  local proto = __protez_debug_call('getproto', fn, index)
  return proto
end)
__protez_set('getstack', function(level, index) return __protez_debug_call('getlocal', level or 1, index or 1) end)
__protez_set('getconstantstable', function(fn) return {} end)
__protez_set('getfunctionhash', function(fn) return __protez_hash_text(tostring(fn)) end)
__protez_set('getscripthash', function(script) return __protez_hash_text(tostring(script)) end)
__protez_set('getscriptbytecode', function(script) return '' end)
__protez_set('getsenv', function(script) return __protez_globals end)
__protez_set('getmenv', function(module) return __protez_globals end)
__protez_set('getcallingscript', function() return __protez_new_proxy('Script') end)
__protez_set('getscriptclosure', function(script) return function() return nil end end)
__protez_set('getscriptfunction', rawget(_G, 'getscriptclosure'))
__protez_set('getscripts', function() return {} end)
__protez_set('getrunningscripts', function() return {} end)
__protez_set('getloadedmodules', function() return {} end)
__protez_set('getinstances', function() return {} end)
__protez_set('getnilinstances', function() return {} end)
__protez_set('getgc', function() return {} end)
__protez_set('getreg', function() return __protez_debug_call('getregistry') or {} end)
__protez_set('getobjects', function() return {} end)
__protez_set('getheap', function() return {} end)
__protez_set('decompile', function(chunk)
  if type(chunk) == 'string' and chunk:sub(1, 1) == '\27' then
    local host = __protez_call_host('__protez_decompile', chunk)
    if type(host) == 'string' and host ~= '' then return host end
  end
  return '-- ' .. __protez_profile.executor .. ': decompile() received a function; bytecode is needed\n'
end)
__protez_set('dumpstring', function(chunk) return tostring(chunk) end)
__protez_set('getspecialinfo', function() return { ProcessorCount = 4, MaxClusterMemory = 4096 } end)
__protez_set('is_sirhurt_closure', function(fn) return false end)
__protez_set('issirhurt', function(fn) return false end)
__protez_set('iskrnl', function() return true end)
__protez_set('is_protected_gui', function() return true end)
__protez_set('protect_gui', function(gui) return gui end)
__protez_set('unprotect_gui', function(gui) return gui end)
__protez_set('queue_on_teleport', function(code)
  table.insert(__protez_state.teleport_queue, tostring(code or ''))
  return true
end)
__protez_set('queueonteleport', rawget(_G, 'queue_on_teleport'))
__protez_set('clearteleportqueue', function()
  __protez_state.teleport_queue = {}
  return true
end)
__protez_set('saveinstance', function() return false end)
__protez_set('saveplace', function() return false end)
__protez_set('setrenderproperty', function(object, property, value) return true end)
__protez_set('getrenderproperty', function(object, property) return nil end)
__protez_set('isrenderobj', function(object) return true end)
__protez_set('sethiddenproperty', function(object, property, value) return true end)
__protez_set('gethiddenproperty', function(object, property) return nil, false end)
__protez_set('isscriptable', function(object, property) return true, false end)
__protez_set('setscriptable', function(object, property, value) return true end)
__protez_set('setsimulationradius', function(radius, max) return true end)
__protez_set('isnetworkowner', function(part) return false end)
__protez_set('getcallbackvalue', function(object, property) return nil end)
__protez_set('fireclickdetector', function(detector, distance) __protez_record('fireclickdetector', tostring(detector)) return true end)
__protez_set('firetouchinterest', function(part, target, toggle) return true end)
__protez_set('fireproximityprompt', function(prompt) return true end)
__protez_set('replicatesignal', function(signal, ...) return true end)
__protez_set('isvalid', function(value) return value ~= nil end)
__protez_set('cloneref', function(value) return value end)
__protez_set('compareinstances', function(left, right) return rawequal(left, right) end)

local function __protez_connections(signal)
  if type(signal) == 'table' and type(rawget(signal, '__protez_connections')) == 'table' then
    return rawget(signal, '__protez_connections')
  end
  return nil
end
__protez_set('getconnections', function(signal)
  local connections = __protez_connections(signal)
  local listed = {}
  if connections then
    for index, connection in ipairs(connections) do
      listed[index] = {
        Enabled = connection.Enabled ~= false,
        Function = connection.Function,
        State = 'Connected',
        Disconnect = connection.Disconnect,
      }
    end
  end
  return listed
end)
__protez_set('firesignal', function(signal, ...)
  local connections = __protez_connections(signal)
  if connections == nil then return false end
  for _, connection in ipairs(connections) do
    if connection.Enabled ~= false and type(connection.Function) == 'function' then
      pcall(connection.Function, ...)
    end
  end
  return true
end)

-- ---------------------------------------------------------------------------
-- Input (recorded, never delivered to the real desktop)
-- ---------------------------------------------------------------------------
local function __protez_input(action, detail)
  __protez_call_host('__protez_input', action, detail)
  return true
end
__protez_set('keypress', function(key) return __protez_input('keypress', tostring(key)) end)
__protez_set('keyrelease', function(key) return __protez_input('keyrelease', tostring(key)) end)
__protez_set('iskeydown', function(key) return false end)
__protez_set('mouse1click', function() return __protez_input('mouse1click', '') end)
__protez_set('mouse1press', function() return __protez_input('mouse1press', '') end)
__protez_set('mouse1release', function() return __protez_input('mouse1release', '') end)
__protez_set('mouse2click', function() return __protez_input('mouse2click', '') end)
__protez_set('mousemoverel', function(x, y) return __protez_input('mousemoverel', tostring(x) .. ',' .. tostring(y)) end)
__protez_set('mousemoveabs', function(x, y) return __protez_input('mousemoveabs', tostring(x) .. ',' .. tostring(y)) end)
__protez_set('mouseclick', rawget(_G, 'mouse1click'))
__protez_set('getmouse', function() return __protez_new_proxy('Mouse') end)

-- ---------------------------------------------------------------------------
-- crypt / base64 / hash libraries
-- ---------------------------------------------------------------------------
local __protez_sha256
do
  local __protez_bit32 = rawget(_G, 'bit32') or {}
  local band = __protez_bit32.band
  local bxor = __protez_bit32.bxor
  local bnot = __protez_bit32.bnot
  local function rrot(value, count)
    -- Luau spells it rrotate; the shim in this prelude spells it ror.
    if type(__protez_bit32.rrotate) == 'function' then return __protez_bit32.rrotate(value, count) end
    if type(__protez_bit32.ror) == 'function' then return __protez_bit32.ror(value, count) end
    local unsigned = (tonumber(value) or 0) % 4294967296
    if unsigned < 0 then unsigned = unsigned + 4294967296 end
    local low = unsigned % (2 ^ count)
    local high = math.floor(unsigned / (2 ^ count))
    return (high + low * (2 ^ (32 - count))) % 4294967296
  end
  local K = {
    0x428a2f98, 0x71374491, 0xb5c0fbcf, 0xe9b5dba5, 0x3956c25b, 0x59f111f1, 0x923f82a4, 0xab1c5ed5,
    0xd807aa98, 0x12835b01, 0x243185be, 0x550c7dc3, 0x72be5d74, 0x80deb1fe, 0x9bdc06a7, 0xc19bf174,
    0xe49b69c1, 0xefbe4786, 0x0fc19dc6, 0x240ca1cc, 0x2de92c6f, 0x4a7484aa, 0x5cb0a9dc, 0x76f988da,
    0x983e5152, 0xa831c66d, 0xb00327c8, 0xbf597fc7, 0xc6e00bf3, 0xd5a79147, 0x06ca6351, 0x14292967,
    0x27b70a85, 0x2e1b2138, 0x4d2c6dfc, 0x53380d13, 0x650a7354, 0x766a0abb, 0x81c2c92e, 0x92722c85,
    0xa2bfe8a1, 0xa81a664b, 0xc24b8b70, 0xc76c51a3, 0xd192e819, 0xd6990624, 0xf40e3585, 0x106aa070,
    0x19a4c116, 0x1e376c08, 0x2748774c, 0x34b0bcb5, 0x391c0cb3, 0x4ed8aa4a, 0x5b9cca4f, 0x682e6ff3,
    0x748f82ee, 0x78a5636f, 0x84c87814, 0x8cc70208, 0x90befffa, 0xa4506ceb, 0xbef9a3f7, 0xc67178f2,
  }
  local function __protez_u32(value)
    return value % 4294967296
  end
  __protez_sha256 = function(message)
    if type(message) ~= 'string' then message = tostring(message) end
    local length = #message
    local bits = length * 8
    message = message .. '\128'
    while (#message % 64) ~= 56 do message = message .. '\0' end
    local high = math.floor(bits / 4294967296)
    local low = bits % 4294967296
    local function be32(value)
      return string.char(
        math.floor(value / 16777216) % 256,
        math.floor(value / 65536) % 256,
        math.floor(value / 256) % 256,
        value % 256
      )
    end
    message = message .. be32(high) .. be32(low)
    local h0, h1, h2, h3 = 0x6a09e667, 0xbb67ae85, 0x3c6ef372, 0xa54ff53a
    local h4, h5, h6, h7 = 0x510e527f, 0x9b05688c, 0x1f83d9ab, 0x5be0cd19
    local w = {}
    for offset = 0, #message - 64, 64 do
      for index = 1, 16 do
        local base = offset + (index - 1) * 4
        local a, b, c, d = message:byte(base + 1, base + 4)
        w[index] = ((a * 256 + b) * 256 + c) * 256 + d
      end
      for index = 17, 64 do
        local s0 = bxor(rrot(w[index - 15], 7), rrot(w[index - 15], 18), math.floor(w[index - 15] / 8))
        local s1 = bxor(rrot(w[index - 2], 17), rrot(w[index - 2], 19), math.floor(w[index - 2] / 1024))
        w[index] = __protez_u32(w[index - 16] + s0 + w[index - 7] + s1)
      end
      local a, b, c, d, e, f, g, h = h0, h1, h2, h3, h4, h5, h6, h7
      for index = 1, 64 do
        local S1 = bxor(rrot(e, 6), rrot(e, 11), rrot(e, 25))
        local ch = bxor(band(e, f), band(bnot(e), g))
        local temp1 = __protez_u32(h + S1 + ch + K[index] + w[index])
        local S0 = bxor(rrot(a, 2), rrot(a, 13), rrot(a, 22))
        local maj = bxor(band(a, b), band(a, c), band(b, c))
        local temp2 = __protez_u32(S0 + maj)
        h = g; g = f; f = e; e = __protez_u32(d + temp1)
        d = c; c = b; b = a; a = __protez_u32(temp1 + temp2)
      end
      h0 = __protez_u32(h0 + a); h1 = __protez_u32(h1 + b)
      h2 = __protez_u32(h2 + c); h3 = __protez_u32(h3 + d)
      h4 = __protez_u32(h4 + e); h5 = __protez_u32(h5 + f)
      h6 = __protez_u32(h6 + g); h7 = __protez_u32(h7 + h)
    end
    local digest = be32(h0) .. be32(h1) .. be32(h2) .. be32(h3)
      .. be32(h4) .. be32(h5) .. be32(h6) .. be32(h7)
    return (digest:gsub('.', function(character)
      return string.format('%02x', character:byte())
    end))
  end
end
local function __protez_to_hex(value)
  return (tostring(value):gsub('.', function(character)
    return string.format('%02x', character:byte())
  end))
end
local function __protez_from_hex(value)
  local text = tostring(value or ''):gsub('%s', '')
  local output = {}
  for index = 1, #text - 1, 2 do
    local byte = tonumber(text:sub(index, index + 1), 16)
    if byte == nil then return '' end
    output[#output + 1] = string.char(byte)
  end
  return table.concat(output)
end
local function __protez_hash_algorithm(name)
  local lowered = tostring(name or 'sha256'):lower():gsub('[^%w]', '')
  if lowered == '' or lowered == 'sha256' or lowered == 'sha2' or lowered == 'sha' then return 'sha256' end
  return lowered
end
local function __protez_hash(value, algorithm)
  local name = __protez_hash_algorithm(algorithm)
  local host = __protez_call_host('__protez_hash', name, tostring(value or ''))
  if type(host) == 'string' and #host > 0 then return host end
  if name == 'sha256' then return __protez_sha256(value) end
  if name == 'md5' or name == 'sha1' then return __protez_sha256(value):sub(1, 32) end
  return __protez_sha256(value)
end
local function __protez_hmac(key, message)
  local block = 64
  local first = tostring(key or '')
  if #first > block then first = __protez_from_hex(__protez_sha256(first)) end
  first = first .. string.rep('\0', block - #first)
  local o, i = {}, {}
  for index = 1, block do
    local byte = first:byte(index)
    o[index] = string.char(bit32.bxor(byte, 0x5c))
    i[index] = string.char(bit32.bxor(byte, 0x36))
  end
  return __protez_sha256(table.concat(o) .. __protez_from_hex(__protez_sha256(table.concat(i) .. tostring(message or ''))))
end
local function __protez_generate_bytes(count)
  local size = math.max(1, math.min(1024, math.floor(tonumber(count) or 16)))
  local bytes = {}
  for index = 1, size do
    bytes[index] = string.char(math.random(0, 255))
  end
  return table.concat(bytes)
end
local function __protez_xor(value, key)
  local text, secret = tostring(value or ''), tostring(key or 'protez')
  if secret == '' then return text end
  local output = {}
  for index = 1, #text do
    local offset = ((index - 1) % #secret) + 1
    output[index] = string.char(bit32.bxor(text:byte(index), secret:byte(offset)))
  end
  return table.concat(output)
end

local __protez_crypt = {
  base64encode = __protez_b64_encode,
  base64decode = __protez_b64_decode,
  base64_encode = __protez_b64_encode,
  base64_decode = __protez_b64_decode,
  hash = __protez_hash,
  hmac = __protez_hmac,
  generatebytes = __protez_generate_bytes,
  generatekey = function() return __protez_generate_bytes(32) end,
  random = __protez_generate_bytes,
  encrypt = __protez_xor,
  decrypt = __protez_xor,
  hexencode = __protez_to_hex,
  hexdecode = __protez_from_hex,
}
local __protez_base64 = {
  encode = __protez_b64_encode,
  decode = __protez_b64_decode,
  Encode = __protez_b64_encode,
  Decode = __protez_b64_decode,
}
__protez_set('crypt', __protez_crypt)
__protez_set('base64', __protez_base64)
__protez_set('hash', __protez_hash)
__protez_set('sha256', __protez_sha256)
__protez_set('base64encode', __protez_b64_encode)
__protez_set('base64decode', __protez_b64_decode)
__protez_set('base64_encode', __protez_b64_encode)
__protez_set('base64_decode', __protez_b64_decode)
__protez_set('lz4', { compress = function(value) return tostring(value or '') end, decompress = function(value) return tostring(value or '') end })
__protez_set('websocket', { connect = function() return __protez_new_proxy('WebSocket') end })
__protez_set('WebSocket', rawget(_G, 'websocket'))

-- ---------------------------------------------------------------------------
-- Executor namespaces: syn.*, krnl.*, fluxus.*, real.* and every marker
-- ---------------------------------------------------------------------------
local __protez_namespaces = {
  'syn', 'krnl', 'fluxus', 'solara', 'delta', 'wave', 'xeno', 'hydrogen',
  'swift', 'nihon', 'macsploit', 'sirhurt', 'protosmasher', 'WeAreDevs',
  'sentinel', 'AWP', 'zorara', 'evon', 'codex', 'Arceus', 'Electron',
  'trigon', 'OxygenU', 'JJSploit', 'real', 'Real', 'protez', 'Protez',
}
local __protez_namespace_extra = {
  request = __protez_http_request,
  http_request = __protez_http_request,
  HttpGet = __protez_http_get,
  HttpGetAsync = __protez_http_get,
  httpget = __protez_http_get,
  httpgetasync = __protez_http_get,
  fetch = __protez_http_get,
  writefile = __protez_write_file,
  write_file = __protez_write_file,
  appendfile = function(path, data) return __protez_write_file(path, data, true) end,
  append_file = function(path, data) return __protez_write_file(path, data, true) end,
  readfile = __protez_read_file,
  read_file = __protez_read_file,
  isfile = __protez_isfile,
  is_file = __protez_isfile,
  isfolder = __protez_isfolder,
  is_folder = __protez_isfolder,
  makefolder = __protez_makefolder,
  make_folder = __protez_makefolder,
  delfile = __protez_delfile,
  delete_file = __protez_delfile,
  delfolder = __protez_delfolder,
  listfiles = __protez_listfiles,
  getcustomasset = __protez_custom_asset,
  protect_gui = rawget(_G, 'protect_gui'),
  unprotect_gui = rawget(_G, 'unprotect_gui'),
  is_protected_gui = rawget(_G, 'is_protected_gui'),
  queue_on_teleport = rawget(_G, 'queue_on_teleport'),
  queueonteleport = rawget(_G, 'queue_on_teleport'),
  clearteleportqueue = rawget(_G, 'clearteleportqueue'),
  setclipboard = rawget(_G, 'setclipboard'),
  getclipboard = rawget(_G, 'getclipboard'),
  getgenv = rawget(_G, 'getgenv'),
  getrenv = rawget(_G, 'getrenv'),
  gethui = rawget(_G, 'gethui'),
  get_hwid = __protez_hwid,
  gethwid = __protez_hwid,
  getthreadidentity = rawget(_G, 'getthreadidentity'),
  setthreadidentity = rawget(_G, 'setthreadidentity'),
  getthreadcontext = rawget(_G, 'getthreadcontext'),
  setthreadcontext = rawget(_G, 'setthreadcontext'),
  getscriptbytecode = rawget(_G, 'getscriptbytecode'),
  getscripthash = rawget(_G, 'getscripthash'),
  decompile = rawget(_G, 'decompile'),
  crypt = __protez_crypt,
  base64 = __protez_base64,
  getversions = function() return { version = __protez_profile.version, name = __protez_profile.executor } end,
  getspecialinfo = rawget(_G, 'getspecialinfo'),
  is_beta = function() return false end,
  version = __protez_profile.version,
  name = __protez_profile.executor,
  loadstring = loadstring,
  load = load,
  hookfunction = __protez_hookfunction,
  hookmetamethod = rawget(_G, 'hookmetamethod'),
  newcclosure = rawget(_G, 'newcclosure'),
  getnamecallmethod = rawget(_G, 'getnamecallmethod'),
  request = __protez_http_request,
}
for _, namespace_name in ipairs(__protez_namespaces) do
  local namespace = rawget(_G, namespace_name)
  if type(namespace) ~= 'table' then
    namespace = setmetatable({}, { __index = __protez_globals, __call = function() return nil end })
    rawset(_G, namespace_name, namespace)
  end
  for key, value in pairs(__protez_namespace_extra) do
    rawset(namespace, key, value)
  end
  rawset(namespace, 'request', __protez_http_request)
end
for key, value in pairs(__protez_namespace_extra) do
  if rawget(_G, key) == nil and type(value) == 'function' then rawset(_G, key, value) end
end
rawset(_G, '__protez_real_namespace', __protez_real)
rawset(_G, '__protez_crypt_table', __protez_crypt)
"""
