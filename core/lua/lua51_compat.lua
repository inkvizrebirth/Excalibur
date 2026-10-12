--[[----------------------------------------------------------------------------
Excalibur :: lua51_compat.lua

Lua 5.1 compatibility layer for newer runtimes (5.2 / 5.3 / 5.4 / LuaJIT).

WHY THIS FILE EXISTS
--------------------
WeAreDevs (WRD) output and the Roblox/Luau environment it targets are Lua 5.1
flavoured.  Research on real WRD v1.0.0 samples (see docs/REAL_WORLD_NOTES.md)
showed that PUC Lua 5.1, 5.2, 5.3 and LuaJIT 2.1 refuse to *compile* large
obfuscated one-liners:

    "control structure too long"          (Lua 5.1 / 5.2 / 5.3 / LuaJIT)
    -> Lua 5.4 compiles the same file.

Real obfuscated scripts therefore need a runtime that (a) parses, and (b) still
behaves like 5.1.  This module provides the observable 5.1 behaviour on top of
5.2+:

  * getfenv / setfenv (implemented over the `_ENV` upvalue)
  * loadstring, unpack, table.getn, table.setn, string.gfind, math.pow
  * newproxy (table backed emulation)
  * 5.1 number formatting: tostring, string.format, table.concat
  * bit32 / bit library (Roblox exposes bit32; obfuscators use it heavily)
  * deterministic math.random replacement (opt-in) + math.randomseed
  * string.rep / string.sub style integer coercion of float arguments

Everything is written so that the file can be loaded under Lua 5.1 as well
(it only installs what is missing and keeps 5.1 semantics untouched).

The module returns a table describing what it changed, which the runner stores
in the run report.
--]]----------------------------------------------------------------------------

local M = {
  installed = {},
  runtime = _VERSION,
  is_lua51 = (_VERSION == "Lua 5.1"),
}

local function mark(name)
  M.installed[#M.installed + 1] = name
end

--- 5.1 prints numbers with "%.14g" (LUAI_NUMFMT); 5.2+ prints floats with a
--- trailing ".0" and prints integral floats differently.  Obfuscators build
--- strings out of numbers, so this difference alone breaks execution.
local function num_to_51_string(n)
  if n ~= n then return "nan" end
  if n == math.huge then return "inf" end
  if n == -math.huge then return "-inf" end
  return (string.format("%.14g", n))
end
M.num_to_51_string = num_to_51_string

--- Truncate a float towards zero the way C's (int) cast does in 5.1.
local function to_int(v)
  if math.type and math.type(v) == "integer" then return v end
  if type(v) ~= "number" then return v end
  if v % 1 == 0 then return v end
  return v - (v % 1)
end

--------------------------------------------------------------------------------
-- getfenv / setfenv
--------------------------------------------------------------------------------
-- Lua 5.2+ has no function environments, but every Lua 5.2+ function created by
-- the compiler carries `_ENV` as (usually) its first upvalue.  Rewriting that
-- upvalue is the faithful equivalent of setfenv.

local function env_of(f)
  if type(f) == "function" then
    local name, value = debug.getupvalue(f, 1)
    if name == "_ENV" then return value end
    return _G
  end
  return _G
end

--------------------------------------------------------------------------------
-- string.format / table.concat / string.rep
--------------------------------------------------------------------------------

local real_format = string.format
local real_concat = table.concat

--- Rewrites arguments so that `%d`-style conversions on non-integral floats do
--- not raise "number has no integer representation" (5.4) and instead truncate
--- like C's cast does in 5.1.
local function format_51(fmt, ...)
  local args = { ... }
  local nargs = select("#", ...)
  if nargs == 0 then return real_format(fmt) end

  local argi = 1
  local out = {}
  local i = 1
  local len = #fmt
  while i <= len do
    local ch = fmt:sub(i, i)
    if ch == "%" then
      local j = i + 1
      local spec = "%"
      -- flags / width / precision
      while j <= len and fmt:sub(j, j):match("[%-+ #0-9%.]") do
        spec = spec .. fmt:sub(j, j)
        j = j + 1
      end
      local conv = fmt:sub(j, j)
      if conv == "%" then
        out[#out + 1] = "%%"
      elseif conv == "" then
        out[#out + 1] = spec
      else
        spec = spec .. conv
        if argi <= nargs then
          local v = args[argi]
          if conv:match("[diouxXc]") and type(v) == "number" then
            args[argi] = to_int(v)
          end
        end
        argi = argi + 1
        out[#out + 1] = spec
      end
      i = j + 1
    else
      out[#out + 1] = ch
      i = i + 1
    end
  end
  return real_format(table.concat(out), unpack(args, 1, nargs))
end

local function concat_51(t, sep, i, j)
  sep = sep or ""
  local n = #t
  if i == nil then i = 1 end
  if j == nil then j = n end
  local copy = {}
  for k = i, j do
    local v = t[k]
    if type(v) == "number" then
      copy[k - i + 1] = num_to_51_string(v)
    else
      copy[k - i + 1] = v
    end
  end
  return real_concat(copy, sep)
end

local real_rep = string.rep
local function rep_51(s, n, sep)
  if type(n) == "number" then n = to_int(n) end
  return real_rep(s, n, sep)
end

--------------------------------------------------------------------------------
-- bit32 (Roblox) implemented in pure Lua 5.1 arithmetic
--------------------------------------------------------------------------------
local function build_bit_library()
  local BAND, BOR, BXOR = {}, {}, {}
  for a = 0, 15 do
    for b = 0, 15 do
      local x, y = a, b
      local r1, r2, r3, bit = 0, 0, 0, 1
      for _ = 1, 4 do
        local bx, by = x % 2, y % 2
        if bx == 1 and by == 1 then r1 = r1 + bit end
        if bx == 1 or by == 1 then r2 = r2 + bit end
        if bx ~= by then r3 = r3 + bit end
        x = (x - bx) / 2
        y = (y - by) / 2
        bit = bit * 2
      end
      BAND[a * 16 + b], BOR[a * 16 + b], BXOR[a * 16 + b] = r1, r2, r3
    end
  end

  local MASK32 = 4294967296

  local function normalize(v)
    if type(v) ~= "number" then v = tonumber(v) or 0 end
    v = v % MASK32
    if v < 0 then v = v + MASK32 end
    return to_int(v)
  end

  local function bitop(lib, a, b)
    a, b = normalize(a), normalize(b)
    local res, mul = 0, 1
    for _ = 1, 8 do
      local an, bn = a % 16, b % 16
      res = res + lib[an * 16 + bn] * mul
      a, b = (a - an) / 16, (b - bn) / 16
      mul = mul * 16
    end
    return res
  end

  local bit = {}
  bit.band = function(...)
    local n = select("#", ...)
    if n == 0 then return 0 end
    local r = normalize((select(1, ...)))
    for i = 2, n do r = bitop(BAND, r, (select(i, ...))) end
    return r
  end
  bit.bor = function(...)
    local n = select("#", ...)
    if n == 0 then return 0 end
    local r = normalize((select(1, ...)))
    for i = 2, n do r = bitop(BOR, r, (select(i, ...))) end
    return r
  end
  bit.bxor = function(...)
    local n = select("#", ...)
    if n == 0 then return 0 end
    local r = normalize((select(1, ...)))
    for i = 2, n do r = bitop(BXOR, r, (select(i, ...))) end
    return r
  end
  bit.bnot = function(a) return bit.bxor(normalize(a), 4294967295) end
  bit.lshift = function(a, n) return (normalize(a) * 2 ^ (n % 32)) % MASK32 end
  bit.rshift = function(a, n) return to_int(normalize(a) / 2 ^ (n % 32)) end
  bit.arshift = function(a, n)
    a = normalize(a)
    if a >= 2147483648 then a = a - MASK32 end
    return to_int(a / 2 ^ (n % 32)) % MASK32
  end
  bit.btest = function(...) return bit.band(...) ~= 0 end
  bit.extract = function(a, field, width)
    width = width or 1
    return bit.band(bit.rshift(a, field or 0), 2 ^ width - 1)
  end
  bit.replace = function(a, repl, field, width)
    width = width or 1
    local mask = 2 ^ width - 1
    local value = bit.band(repl, mask)
    local shift = field or 0
    local cleared = bit.band(a, bit.bnot(bit.lshift(mask, shift)))
    return bit.bor(cleared, bit.lshift(value, shift))
  end
  bit.lrotate = function(a, n) return bit.bor(bit.lshift(a, n % 32), bit.rshift(a, 32 - n % 32)) end
  bit.rrotate = function(a, n) return bit.lrotate(a, 32 - n % 32) end
  bit.countlz = function(a)
    a = normalize(a)
    local c = 0
    for i = 31, 0, -1 do
      if bit.band(a, 2 ^ i) ~= 0 then break end
      c = c + 1
    end
    return c
  end
  bit.countrz = function(a)
    a = normalize(a)
    if a == 0 then return 32 end
    local c = 0
    while bit.band(a, 1) == 0 do a = bit.rshift(a, 1); c = c + 1 end
    return c
  end
  bit.byteswap = function(a)
    local b = normalize(a)
    return bit.bor(bit.lshift(bit.band(b, 0xFF), 24), bit.lshift(bit.band(b, 0xFF00), 8),
      bit.rshift(bit.band(b, 0xFF0000), 8), bit.rshift(bit.band(b, 0xFF000000), 24))
  end
  bit.normalize = normalize
  bit.tobit = normalize
  return bit, BAND, BOR, BXOR
end

--------------------------------------------------------------------------------
-- install
--------------------------------------------------------------------------------
--- @param opts table|nil  { deterministic_random = bool, seed = number }
--- @return table report
function M.install(opts)
  opts = opts or {}
  local bitlib

  if not M.is_lua51 then
    -- ---- tables ----
    if type(table.unpack) == "function" and type(unpack) ~= "function" then
      _G.unpack = table.unpack
      mark("unpack")
    end
    if type(table.getn) ~= "function" then
      table.getn = function(t) return #t end
      mark("table.getn")
    end
    if type(table.setn) ~= "function" then
      table.setn = function() return nil end
      mark("table.setn")
    end
    if type(table.pack) ~= "function" then
      table.pack = function(...) return { n = select("#", ...), ... } end
      mark("table.pack")
    end

    -- ---- strings ----
    if type(string.gfind) ~= "function" and type(string.gmatch) == "function" then
      string.gfind = string.gmatch
      mark("string.gfind")
    end
    string.rep = rep_51
    mark("string.rep(5.1)")
    string.format = format_51
    mark("string.format(5.1)")
    table.concat = concat_51
    mark("table.concat(5.1)")

    -- ---- numbers ----
    if type(math.pow) ~= "function" then
      math.pow = function(a, b) return a ^ b end
      mark("math.pow")
    end
    if type(math.ldexp) ~= "function" then
      math.ldexp = function(m, e) return m * 2 ^ e end
      mark("math.ldexp")
    end

    -- ---- tostring ----
    local real_tostring = tostring
    _G.tostring = function(v)
      if type(v) == "number" then return num_to_51_string(v) end
      return real_tostring(v)
    end
    mark("tostring(5.1)")

    -- ---- environments ----
    if type(getfenv) ~= "function" then
      _G.getfenv = function(f)
        if f == nil or f == 0 or f == 1 then f = 2 end
        if type(f) == "number" then
          local info = debug.getinfo(f + 1, "f")
          if not info then return _G end
          return env_of(info.func)
        end
        return env_of(f)
      end
      mark("getfenv")
    end
    if type(setfenv) ~= "function" then
      _G.setfenv = function(f, env)
        if type(f) == "number" then
          local info = debug.getinfo(f + 1, "f")
          if not info then return f end
          f = info.func
        end
        if type(f) == "function" then
          local name = debug.getupvalue(f, 1)
          if name == "_ENV" then debug.setupvalue(f, 1, env) end
        end
        return f
      end
      mark("setfenv")
    end

    -- ---- loadstring ----
    if type(loadstring) ~= "function" then
      _G.loadstring = function(chunk, chunkname)
        if type(chunk) ~= "string" then return nil, "bad argument #1 to 'loadstring' (string expected)" end
        return load(chunk, chunkname or chunk, "t", _G)
      end
      mark("loadstring")
    end

    -- ---- newproxy ----
    if type(newproxy) ~= "function" then
      local proxy_states = setmetatable({}, { __mode = "k" })
      _G.newproxy = function(proxy)
        local mt
        if proxy == true then
          mt = {}
          local handle = setmetatable({}, mt)
          proxy_states[mt] = handle
          return handle
        elseif type(proxy) == "table" then
          local parent_mt = getmetatable(proxy)
          mt = parent_mt or {}
          return setmetatable({}, mt)
        end
        return error("newproxy expects true or a proxy", 2)
      end
      mark("newproxy")
    end
  else
    mark("native-5.1")
  end

  -- ---- bit32 (both 5.1 and 5.2 sometimes lack it) ----
  if type(bit32) ~= "table" then
    bitlib = build_bit_library()
    _G.bit32 = bitlib
    mark("bit32")
  else
    bitlib = bit32
  end
  if type(bit) ~= "table" then
    _G.bit = bitlib
    mark("bit")
  end
  M.bit32 = bitlib

  -- ---- deterministic random (optional) ----
  -- NOTE: exact bit-for-bit reproduction of C `rand()` is impossible (glibc,
  -- msvcrt and 5.4's xoshiro all differ), so Excalibur offers a *reproducible*
  -- generator instead: repeated runs of the same script produce the same
  -- sequence, which is what matters for stable traces and diffs.
  if opts.deterministic_random then
    local seed = opts.seed or 123456789
    local state = seed % 4294967296
    if state == 0 then state = 2463534242 end
    local function shl(v, n) return (v * 2 ^ n) % 4294967296 end
    local function shr(v, n) return to_int(v / 2 ^ n) % 4294967296 end
    local function xs()
      local x = state
      x = bitlib.bxor(shl(x, 13), x)
      x = bitlib.bxor(shr(x, 17), x)
      x = bitlib.bxor(shl(x, 5), x)
      state = x
      return x
    end
    math.randomseed = function(s)
      state = (tonumber(s) or 123456789) % 4294967296
      if state == 0 then state = 2463534242 end
    end
    math.random = function(a, b)
      local r = xs() / 4294967296 -- [0, 1)
      if a == nil then return r end
      if b == nil then a, b = 1, a end
      if a > b then a, b = b, a end
      a, b = math.floor(to_int(a)), math.floor(to_int(b))
      return a + math.floor(r * (b - a + 1))
    end
    mark("math.random(deterministic)")
  end

  M.bit32 = bitlib
  return M
end

return M
