--[[----------------------------------------------------------------------------
Excalibur :: runner.lua

Entry point executed inside the embedded Lua runtime.  It builds the isolated
environment, installs the hooks, runs the obfuscated chunk and writes a machine
readable report (`report.json`) plus the human readable `hook_log.txt`.

Configuration is taken from the global table `EXCALIBUR` (used by the
in-process lupa engine) and falls back to environment variables (used by the
subprocess engine, which is also how a bundled lua51.exe / lua54.exe is driven).

Two different sources of configuration keep the runner usable in both engines
without duplicating any logic.

Report / dump files are written next to `EXCALIBUR.logs_dir`:

    hook_log.txt        event log (lo ad, captures, notes)
    dump_NNN.lua        chunks passed to load()/loadstring()
    concat_NNN.lua      strings rebuilt through table.concat()
    trace.txt           dispatch states recorded in trace mode
    report.json         structured run report consumed by Python
--]]----------------------------------------------------------------------------

local EXC = rawget(_G, "EXCALIBUR") or {}
if type(EXC) ~= "table" then EXC = {} end

local function cfg(key, env_key, default)
  local v = EXC[key]
  if v == nil then v = os.getenv(env_key) end
  if v == nil then return default end
  return v
end

--------------------------------------------------------------------------------
-- small JSON encoder (no external dependency inside the sandbox)
--------------------------------------------------------------------------------
local json = {}
do
  local escapes = {
    ['"'] = '\\"', ["\\"] = "\\\\", ["\b"] = "\\b", ["\f"] = "\\f",
    ["\n"] = "\\n", ["\r"] = "\\r", ["\t"] = "\\t",
  }
  local function esc(s)
    return (tostring(s):gsub('[%z\1-\31"\\]', function(c)
      return escapes[c] or string.format("\\u%04x", string.byte(c))
    end))
  end

  local function is_array(t)
    if type(t) ~= "table" then return false end
    local n = 0
    for k in pairs(t) do
      if type(k) ~= "number" then return false end
      n = n + 1
    end
    return n == #t
  end

  local encode

  local function encode_number(v)
    if v ~= v or v == math.huge or v == -math.huge then return '"' .. tostring(v) .. '"' end
    if v % 1 == 0 and math.abs(v) < 1e15 then return string.format("%d", v) end
    return string.format("%.17g", v)
  end

  encode = function(v, depth)
    depth = (depth or 0) + 1
    if depth > 40 then return '"<deep>"' end
    local t = type(v)
    if v == nil then return "null" end
    if t == "boolean" then return v and "true" or "false" end
    if t == "number" then return encode_number(v) end
    if t == "string" then return '"' .. esc(v) .. '"' end
    if t == "table" then
      if is_array(v) then
        local parts = {}
        for i = 1, #v do parts[#parts + 1] = encode(v[i], depth) end
        return "[" .. table.concat(parts, ",") .. "]"
      end
      local parts = {}
      for k, val in pairs(v) do
        if type(k) == "string" or type(k) == "number" then
          parts[#parts + 1] = '"' .. esc(tostring(k)) .. '":' .. encode(val, depth)
        end
      end
      table.sort(parts)
      return "{" .. table.concat(parts, ",") .. "}"
    end
    return '"<' .. t .. '>"'
  end

  json.encode = function(v) return encode(v, 0) end
end

local unpack = table.unpack or unpack

--------------------------------------------------------------------------------
-- paths / config
--------------------------------------------------------------------------------
local base_dir = cfg("base_dir", "EXCALIBUR_BASE_DIR", ".")
local logs_dir = cfg("logs_dir", "EXCALIBUR_LOGS_DIR", base_dir .. "/logs")
local source_path = cfg("source_path", "EXCALIBUR_SOURCE_PATH", nil)
local policy = cfg("policy", "EXCALIBUR_POLICY", "codex")
local mode = cfg("mode", "EXCALIBUR_MODE", "run")
local timeout = tonumber(cfg("timeout", "EXCALIBUR_TIMEOUT", 30)) or 30
local max_instructions = tonumber(cfg("max_instructions", "EXCALIBUR_MAX_INSTRUCTIONS", 400000000)) or 400000000
local instr_period = tonumber(cfg("instr_period", "EXCALIBUR_INSTR_PERIOD", 400000)) or 400000
local allow_unsafe = cfg("allow_unsafe", "EXCALIBUR_ALLOW_UNSAFE", "0") == "1" or cfg("allow_unsafe", "EXCALIBUR_ALLOW_UNSAFE", false) == true
local deterministic_random = cfg("deterministic_random", "EXCALIBUR_DETERMINISTIC_RANDOM", "1") == "1"
local random_seed = tonumber(cfg("random_seed", "EXCALIBUR_RANDOM_SEED", 123456789)) or 123456789
local hostname = cfg("hostname", "EXCALIBUR_HOSTNAME", "lua-runtime")

local report = {
  runtime = { lua_version = _VERSION, is_lua51 = (_VERSION == "Lua 5.1"), jit = rawget(_G, "jit") and rawget(_G, "jit").version or nil },
  engine = cfg("engine", "EXCALIBUR_ENGINE", "unknown"),
  policy = policy,
  mode = mode,
  base_dir = base_dir,
  logs_dir = logs_dir,
  source_path = source_path,
  timeout_seconds = timeout,
  allow_unsafe = allow_unsafe,
  compiled = false,
  compile_error = nil,
  ran = false,
  run_error = nil,
  timed_out = false,
  duration_ms = 0,
  instructions = 0,
  installed_shims = {},
  notes = {},
}

local log_file
local function log(msg)
  if log_file then
    log_file:write(tostring(msg), "\n")
    log_file:flush()
  end
end

local t_start = os.clock()
local t_wall_start = os.time()

--------------------------------------------------------------------------------
-- modules
--------------------------------------------------------------------------------
local function dofile_required(path)
  local f, err = loadfile(path)
  if not f then
    error("cannot load " .. path .. ": " .. tostring(err))
  end
  return f()
end

local compat, stubs, hooks
local function load_modules()
  local ok, res = pcall(dofile_required, base_dir .. "/lua51_compat.lua")
  if not ok then error("lua51_compat.lua failed: " .. tostring(res)) end
  compat = res
  local ok2, res2 = pcall(dofile_required, base_dir .. "/roblox_stubs.lua")
  if not ok2 then error("roblox_stubs.lua failed: " .. tostring(res2)) end
  stubs = res2
  local ok3, res3 = pcall(dofile_required, base_dir .. "/hooks.lua")
  if not ok3 then error("hooks.lua failed: " .. tostring(res3)) end
  hooks = res3
end

--------------------------------------------------------------------------------
-- main
--------------------------------------------------------------------------------
local function main()
  os.execute("mkdir 2>nul") -- no-op everywhere; directory creation is done by Python
  log_file = io.open(logs_dir .. "/hook_log.txt", "w")
  if not log_file then
    -- last resort: report through the error channel; Python surfaces this.
    error("cannot open log file in " .. tostring(logs_dir))
  end

  log("# Excalibur run report")
  log("# runtime=" .. tostring(_VERSION) .. " policy=" .. tostring(policy) .. " mode=" .. tostring(mode) .. " host=" .. tostring(hostname))
  log("# source=" .. tostring(source_path))

  load_modules()
  hooks.set_deps({
    logs_dir = logs_dir,
    log = log,
    is_log_open = function() return log_file ~= nil end,
  })
  stubs.set_context({
    log = log,
    capture = function(c) hooks.captures[#hooks.captures + 1] = c end,
  })

  -- ---- compatibility shims (5.2+ -> 5.1 behaviour) ----
  local compat_report = compat.install({
    deterministic_random = deterministic_random,
    seed = random_seed,
  })
  report.installed_shims = compat_report.installed
  report.runtime.bit32 = type(rawget(_G, "bit32")) == "table"

  if not source_path then error("no source_path configured") end
  local f = io.open(source_path, "rb")
  if not f then error("cannot read source: " .. tostring(source_path)) end
  local source = f:read("*a")
  f:close()
  report.source_bytes = #source

  -- ---- environment ----
  local env = {}
  local base_globals = {
    "assert", "error", "ipairs", "pairs", "next", "pcall", "xpcall", "select", "tonumber",
    "tostring", "type", "unpack", "setmetatable", "getmetatable", "rawget", "rawset",
    "rawequal", "rawlen", "collectgarbage", "load", "loadstring", "newproxy", "getfenv",
    "setfenv", "string", "table", "math", "coroutine", "utf8", "bit32", "bit", "debug",
  }
  for _, k in ipairs(base_globals) do
    local v = rawget(_G, k)
    if v ~= nil then env[k] = v end
  end

  -- Restricted os: no os.exit / os.execute / os.remove / os.rename (sandbox).
  -- Time functions return *fixed* values so repeated runs are comparable.
  local fixed = tonumber(cfg("fixed_time", "EXCALIBUR_FIXED_TIME", 1700000000)) or 1700000000
  env.os = {
    clock = function() return os.clock() end,
    time = function() return fixed end,
    date = os.date,
    difftime = os.difftime,
    getenv = function() return nil end,
    exit = function() error("os.exit is blocked in the Excalibur sandbox", 2) end,
  }
  if allow_unsafe then
    env.os = os
    env.io = io
    env.require = require
    env.dofile = dofile
    env.loadfile = loadfile
  else
    env.io = {
      open = function() return nil, "io.open is blocked in the Excalibur sandbox" end,
      write = function() return nil, "io.write is blocked in the Excalibur sandbox" end,
      read = function() return nil end,
      lines = function() return function() return nil end end,
    }
    env.require = function(name) error("require('" .. tostring(name) .. "') is blocked", 2) end
    env.dofile = function() error("dofile is blocked", 2) end
    env.loadfile = function() return nil, "loadfile is blocked" end
  end
  env.debug = {
    traceback = debug and debug.traceback or function() return "" end,
    getinfo = debug and debug.getinfo or function() return nil end,
    sethook = function() end,   -- scripts must not disable the watchdog
    gethook = function() return nil end,
    getmetatable = debug and debug.getmetatable or getmetatable,
    setmetatable = debug and debug.setmetatable or setmetatable,
    getregistry = function() return {} end,
    getupvalue = debug and debug.getupvalue or function() return nil end,
    setupvalue = debug and debug.setupvalue or function() return nil end,
    getlocal = debug and debug.getlocal or function() return nil end,
  }

  -- ---- Roblox / executor stubs ----
  local stub_globals = stubs.build(policy, { place_id = 0, deterministic = deterministic_random })
  local known_api = stubs.known_api
  for k, v in pairs(stub_globals) do
    if k:sub(1, 2) ~= "__" then env[k] = v end
  end

  -- ---- hooks: load / loadstring / table.concat / string.char ----
  local function compile_fn(body, name, override_env)
    if _VERSION == "Lua 5.1" then
      local fn, err = loadstring(body, name or "=(load)")
      if fn and (override_env or env) then setfenv(fn, override_env or env) end
      return fn, err
    end
    return load(body, name or "=(load)", "t", override_env or env)
  end

  local loader = hooks.make_loader(compile_fn)
  env.load = loader
  env.loadstring = loader
  if _VERSION == "Lua 5.1" then
    env.loadstring = loader
  end

  local real_concat = table.concat
  env.table = setmetatable({ concat = hooks.make_concat(real_concat) }, { __index = table })
  if type(table.unpack) == "function" then env.table.unpack = table.unpack end
  if type(table.getn) == "function" then env.table.getn = table.getn end

  local real_char = string.char
  env.string = setmetatable({ char = hooks.make_char(real_char) }, { __index = string })

  env.print = function(...)
    local parts = {}
    for i = 1, select("#", ...) do
      parts[i] = tostring((select(i, ...)))
    end
    log("PRINT " .. table.concat(parts, "\t"))
  end

  -- ---- spec injections ----
  rawset(env, "loadstring", env.loadstring)
  rawset(env, "load", env.load)
  rawset(env, "__sandbox_writefile", hooks.make_writefile())
  rawset(env, "__sandbox_trace", {})
  rawset(env, "__sandbox_trace_state", hooks.make_trace_state())
  rawset(env, "__G", env)
  rawset(env, "_G", env)
  rawset(env, "_ENV", env)
  rawset(env, "__policy", policy)

  -- ---- policy based __index / logging __newindex ----
  setmetatable(env, {
    __index = function(t, k)
      local kk = tostring(k)
      if kk == "_G" or kk == "_ENV" or kk == "__G" then return env end
      hooks.track_read(kk)
      if policy == "permissive" then
        hooks.track_miss(kk)
        local v = stubs.new_stub("Instance", kk)
        rawset(t, kk, v)
        return v
      end
      if policy == "codex" and known_api[kk] and stub_globals[kk] == nil then
        local v = stubs.new_stub("Instance", kk)
        rawset(t, kk, v)
        return v
      end
      hooks.track_miss(kk)
      return nil
    end,
    __newindex = function(t, k, v)
      hooks.track_write(tostring(k))
      rawset(t, k, v)
    end,
    __metatable = "ExcaliburSandbox",
  })

  -- script visible hooks list (the spec asks for these names to exist)
  env.__sandbox_trace.env = nil

  -- ---- compile ----
  report.source_head = (source:sub(1, 400):gsub("\n", "\\n"))
  local chunk, err
  if _VERSION == "Lua 5.1" then
    chunk, err = loadstring(source, "@obfuscated")
    if chunk then setfenv(chunk, env) end
  else
    chunk, err = load(source, "@obfuscated", "t", env)
  end
  if not chunk then
    report.compiled = false
    report.compile_error = tostring(err)
    log("COMPILE_FAIL " .. tostring(err))
    return
  end
  report.compiled = true

  -- ---- run with watchdog ----
  local instruction_count = 0
  local returned = nil
  local ran_ok, run_err = true, nil

  local function watchdog()
    instruction_count = instruction_count + instr_period
    if instruction_count > max_instructions then
      error("__EXCALIBUR_TIMEOUT__ (instruction budget exhausted)", 0)
    end
    if os.clock() - t_start > timeout then
      error("__EXCALIBUR_TIMEOUT__ (wall clock budget exhausted)", 0)
    end
  end

  if mode ~= "compile" then
    if debug and debug.sethook then debug.sethook(watchdog, "", instr_period) end
    ran_ok, run_err = xpcall(chunk, function(e)
      local trace = debug and debug.traceback and debug.traceback("", 2) or ""
      return tostring(e) .. "\n" .. trace
    end)
    if debug and debug.sethook then debug.sethook() end
  end

  report.instructions = instruction_count
  report.ran = ran_ok
  if not ran_ok then
    local msg = tostring(run_err or "")
    if msg:find("__EXCALIBUR_TIMEOUT__", 1, true) then
      report.timed_out = true
      report.run_error = "timeout"
      log("RUN_TIMEOUT after " .. string.format("%.2f", os.clock() - t_start) .. "s")
    else
      report.run_error = msg:sub(1, 4000)
      log("RUN_ERROR " .. (msg:sub(1, 4000)))
    end
  else
    log("RUN_OK")
  end

  -- ---- collect the report ----
  report.duration_ms = math.floor((os.clock() - t_start) * 1000)

  local function top(map, limit)
    local list = {}
    for k, v in pairs(map) do list[#list + 1] = { name = k, count = v } end
    table.sort(list, function(a, b)
      if a.count ~= b.count then return a.count > b.count end
      return tostring(a.name) < tostring(b.name)
    end)
    local out = {}
    for i = 1, math.min(#list, limit or 50) do out[i] = list[i] end
    return out, #list
  end

  local missed, missed_total = top(hooks.missed, 80)
  report.missed_globals = missed
  report.missed_global_count = missed_total or 0

  local reads, reads_total = top(hooks.reads, 60)
  report.top_global_reads = reads
  report.distinct_globals = hooks.read_order

  local writes, writes_total = top(hooks.writes, 60)
  report.global_writes = writes
  report.write_count = writes_total or 0

  report.stats = hooks.stats
  report.loads = hooks.loads
  report.captures = hooks.captures
  report.notes = hooks.notes
  report.trace_states = hooks.stats.trace_states
  report.host_time = os.time() - t_wall_start

  return report
end

local ok, result = xpcall(main, function(e)
  return tostring(e) .. "\n" .. (debug and debug.traceback and debug.traceback("", 2) or "")
end)

if not ok then
  report.error = tostring(result):sub(1, 4000)
  if log_file then log("FATAL " .. report.error) end
end

-- trace dump
if hooks and hooks.trace_states and #(hooks.trace_states or {}) > 0 then
  local path = logs_dir .. "/trace.txt"
  local f = io.open(path, "w")
  if f then
    for i = 1, #hooks.trace_states do f:write(hooks.trace_states[i], "\n") end
    f:close()
    report.trace_path = path
  end
end

if hooks and hooks.char_fragments and #hooks.char_fragments > 0 then
  local path = logs_dir .. "/char_fragments.txt"
  local f = io.open(path, "w")
  if f then
    for i = 1, #hooks.char_fragments do
      f:write((hooks.char_fragments[i]:gsub("\n", "\\n")), "\n")
    end
    f:close()
    report.char_fragments_path = path
  end
end

-- final report (written last so Python can rely on its presence/absence)
local rp = logs_dir .. "/report.json"
local rf = io.open(rp, "w")
if rf then
  rf:write(json.encode(report))
  rf:close()
end
if log_file then
  log("REPORT " .. tostring(rp))
  log("DONE ok=" .. tostring(ok))
  log_file:close()
end

-- Expose the report to the host (lupa can read EXCALIBUR_RESULT).  When the
-- runner is executed as a standalone script the file above is authoritative.
rawset(_G, "EXCALIBUR_RESULT", report)
rawset(_G, "EXCALIBUR_OK", ok)
