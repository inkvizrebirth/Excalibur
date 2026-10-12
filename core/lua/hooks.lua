--[[----------------------------------------------------------------------------
Excalibur :: hooks.lua

Instrumentation placed inside the sandbox environment:

  * `load` / `loadstring` interception  -> every dynamically compiled chunk is
    written to logs/dump_NNN.lua.  This is the primary payload capture path for
    obfuscators that rebuild the original source and execute it at runtime.
  * `table.concat` capture              -> obfuscators that rebuild the source by
    concatenating decoded fragments are captured here as well (the WRD v1.0.0
    decoder assembles decoded pool entries with table.concat, verified on real
    samples).
  * `string.char` capture               -> decoded byte fragments (helps when the
    script assembles bytes directly).
  * global read / write logging         -> "silent failure" diagnosis (see
    docs/REAL_WORLD_NOTES.md): a script that reads a randomized global and then
    quietly returns has detected the emulated environment.
  * `__sandbox_writefile`, `__sandbox_trace`, `__sandbox_trace_state`
                                        -> the injection points used by
    `core/vm_trace.py` to record dispatch-loop states.
--]]----------------------------------------------------------------------------

local M = {}

local unpack = table.unpack or unpack

M.config = {
  capture_loads = true,
  capture_concat = true,
  capture_char = true,
  track_globals = true,
  max_dumps = 128,          -- hard cap on dumped chunks per run
  max_dump_bytes = 8 * 1024 * 1024,
  concat_min_length = 120,  -- ignore short concatenations
  concat_min_parts = 3,
  max_concat_dumps = 128,
  max_char_dumps = 4000,
  max_trace_states = 200000,
  max_distinct_globals = 5000,
}

M.stats = {
  loads = 0,
  concats = 0,
  char_calls = 0,
  global_reads = 0,
  global_writes = 0,
  trace_states = 0,
  loads_skipped = 0,
  files_written = 0,
}

M.loads = {}       -- [{n, name, len, path, head}]
M.missed = {}      -- {name = count}  globals that resolved to nil
M.reads = {}       -- {name = count}
M.read_order = {}  -- distinct global names, in first-seen order (bounded)
M.writes = {}      -- {name = count}
M.captures = {}    -- [{kind, name, value}] url / file / concat captures
M.notes = {}

--------------------------------------------------------------------------------
-- helpers passed in by the runner
--------------------------------------------------------------------------------
local deps = {
  logs_dir = ".",
  log = function() end,
  is_log_open = function() return false end,
}

function M.set_deps(d)
  for k, v in pairs(d) do deps[k] = v end
end

local function note(msg)
  M.notes[#M.notes + 1] = msg
  deps.log("NOTE " .. tostring(msg))
end

local function sanitize(name)
  return (tostring(name):gsub("[^%w%._%-]", "_"))
end

local function write_file(path, data)
  local f, err = io.open(path, "wb")
  if not f then
    note("cannot write " .. tostring(path) .. ": " .. tostring(err))
    return false
  end
  f:write(data)
  f:close()
  M.stats.files_written = M.stats.files_written + 1
  return true
end

local function head_of(s, n)
  return (tostring(s):sub(1, n):gsub("\n", "\\n"))
end

--------------------------------------------------------------------------------
-- __sandbox_writefile / __sandbox_trace
--------------------------------------------------------------------------------
function M.make_writefile()
  return function(name, data)
    data = tostring(data or "")
    if #data > M.config.max_dump_bytes then
      note("writefile truncated: " .. tostring(name))
      data = data:sub(1, M.config.max_dump_bytes)
    end
    local idx = M.stats.files_written + 1
    local path = string.format("%s/sandbox_%03d_%s", deps.logs_dir, idx, sanitize(name))
    if write_file(path, data) then
      deps.log(string.format("SANDBOX_WRITEFILE %s (%d bytes)", path, #data))
    end
    return true
  end
end

function M.make_trace_state()
  return function(state)
    if M.stats.trace_states < M.config.max_trace_states then
      M.stats.trace_states = M.stats.trace_states + 1
      M.trace_states = M.trace_states or {}
      M.trace_states[#M.trace_states + 1] = tostring(state)
    end
    return state
  end
end

--------------------------------------------------------------------------------
-- load / loadstring interception
--------------------------------------------------------------------------------
function M.make_loader(compile_fn)
  -- compile_fn(body, name, env) -> function|nil, err
  return function(chunk, name, mode, env)
    if type(chunk) == "function" then
      -- incremental loaders: read the producer function fully
      local parts = {}
      while true do
        local piece = chunk()
        if piece == nil or piece == "" then break end
        parts[#parts + 1] = piece
      end
      chunk = table.concat(parts)
    end
    if type(chunk) ~= "string" then
      return nil, "bad argument #1 to 'load' (string expected)"
    end

    M.stats.loads = M.stats.loads + 1
    local n = M.stats.loads
    local body = tostring(chunk)

    if M.config.capture_loads then
      if n > M.config.max_dumps then
        M.stats.loads_skipped = M.stats.loads_skipped + 1
      else
        local path = string.format("%s/dump_%03d.lua", deps.logs_dir, n)
        local payload = body
        if #payload > M.config.max_dump_bytes then
          payload = payload:sub(1, M.config.max_dump_bytes)
          note("dump truncated: " .. path)
        end
        write_file(path, payload)
        M.loads[#M.loads + 1] = {
          n = n, name = tostring(name or ""), len = #body, path = path, head = head_of(body, 240),
        }
        deps.log(string.format("LOAD #%d name=%s len=%d path=%s", n, tostring(name), #body, path))
        deps.log("LOAD_HEAD: " .. head_of(body, 240))
      end
    end

    local fn, err = compile_fn(body, name, env)
    return fn, err
  end
end

--------------------------------------------------------------------------------
-- table.concat / string.char capture
--------------------------------------------------------------------------------
function M.make_concat(real_concat)
  return function(t, sep, i, j)
    local result = real_concat(t, sep, i, j)
    if M.config.capture_concat and type(result) == "string" and #result >= M.config.concat_min_length then
      local n = 0
      if type(t) == "table" then
        for _ in pairs(t) do
          n = n + 1
          if n > 100000 then break end
        end
      end
      if n >= M.config.concat_min_parts and M.stats.concats < M.config.max_concat_dumps then
        M.stats.concats = M.stats.concats + 1
        local path = string.format("%s/concat_%03d.lua", deps.logs_dir, M.stats.concats)
        write_file(path, result)
        M.captures[#M.captures + 1] = {
          kind = "concat", name = "table.concat", value = path, len = #result, parts = n,
        }
        deps.log(string.format("CONCAT #%d len=%d parts=%d path=%s", M.stats.concats, #result, n, path))
      end
    end
    return result
  end
end

function M.make_char(real_char)
  return function(...)
    local result = real_char(...)
    M.stats.char_calls = M.stats.char_calls + 1
    if M.config.capture_char and M.stats.char_calls <= M.config.max_char_dumps then
      M.char_fragments = M.char_fragments or {}
      M.char_fragments[#M.char_fragments + 1] = result
    end
    return result
  end
end

--------------------------------------------------------------------------------
-- global access tracking
--------------------------------------------------------------------------------
local distinct_reads = 0

function M.track_read(name)
  M.stats.global_reads = M.stats.global_reads + 1
  local c = M.reads[name]
  if c then
    M.reads[name] = c + 1
  else
    M.reads[name] = 1
    if distinct_reads < M.config.max_distinct_globals then
      distinct_reads = distinct_reads + 1
      M.read_order[#M.read_order + 1] = name
    end
  end
end

function M.track_miss(name)
  M.missed[name] = (M.missed[name] or 0) + 1
end

function M.track_write(name)
  M.stats.global_writes = M.stats.global_writes + 1
  M.writes[name] = (M.writes[name] or 0) + 1
end

return M
