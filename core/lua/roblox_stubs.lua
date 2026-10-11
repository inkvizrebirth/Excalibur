--[[----------------------------------------------------------------------------
Excalibur :: roblox_stubs.lua

Roblox / executor API stubs used to execute obfuscated scripts outside Roblox.

The stubs are intentionally *permissive*: an obfuscated script walks deep
property chains such as

    game:GetService("Players").LocalPlayer.Character:FindFirstChild("Humanoid")

and a plain `nil` anywhere in that chain aborts the run before the interesting
code (the string decoder / payload loader) has a chance to execute.

Three policies are provided because no single policy is right for every script:

  strict      unknown globals return nil.  Best for scripts that use random
              "canary" global accesses to detect instrumentation (see
              docs/REAL_WORLD_NOTES.md).  Roblox names are still stubbed.
  codex       (default) Roblox / executor API names are stubbed, anything else
              returns nil.
  permissive  every unknown global returns an auto-vivifying stub.  Keeps
              control-flow-flattened scripts alive, but lets canaries pass.

The runner retries with a different policy when a run dies early, and keeps the
best result - `core/sandbox.py` drives that ladder.

Every stub records accesses into the shared log, and I/O style calls (HttpGet,
http_request, readfile, ...) are additionally recorded as *captures* so the
deobfuscator can report hidden URLs / file names.
--]]----------------------------------------------------------------------------

local M = {}

local unpack = table.unpack or unpack

--------------------------------------------------------------------------------
-- logging / capture plumbing (injected by the runner)
--------------------------------------------------------------------------------
local ctx = {
  log = function() end,
  capture = function() end,
  url_count = 0,
}

function M.set_context(c)
  if c.log then ctx.log = c.log end
  if c.capture then ctx.capture = c.capture end
end

local function log(fmt, ...)
  local ok, msg = pcall(string.format, fmt, ...)
  ctx.log(ok and msg or tostring(fmt))
end

--------------------------------------------------------------------------------
-- auto-vivifying stub object family
--------------------------------------------------------------------------------
-- A stub is a table with a metatable whose __index creates child stubs on
-- demand.  Arithmetic / comparison / call metamethods are supplied so that
-- stubs never raise "attempt to perform arithmetic on a table value".

local function new_stub(kind, name)
  local s = {
    __kind = kind or "Instance",
    __name = name or "",
    __props = {},
  }
  return setmetatable(s, M.stub_mt)
end

local function stub_index(t, k)
  if type(k) == "string" then
    local props = rawget(t, "__props")
    if props and props[k] ~= nil then return props[k] end
    if k == "Name" then return rawget(t, "__name") or "" end
    if k == "ClassName" then return rawget(t, "__kind") or "Instance" end
    if k == "Parent" then return nil end
    if k == "PlaceId" then return 0 end
    if k == "JobId" then return "excalibur-job" end
    if k == "UserId" then return 1 end
    if k == "GameId" then return 0 end
    if k == "Value" or k == "Text" or k == "AbsoluteSize" then return 0 end
    if k == "Magnitude" then return 0 end
    if k == "Unit" then return new_stub("Vector3", "Unit") end
    if k == "X" or k == "Y" or k == "Z" then return 0 end
    if k == "Position" then return new_stub("Vector3", "Position") end
    if k == "Loaded" then return true end
    if k == "HttpEnabled" then return true end
  elseif type(k) == "number" then
    return new_stub("Instance", tostring(k))
  end
  local child = new_stub(rawget(t, "__kind"), tostring(k))
  return child
end

local function stub_call(t, ...)
  return new_stub(rawget(t, "__kind"), rawget(t, "__name"))
end

M.stub_mt = {
  __index = stub_index,
  __newindex = function(t, k, v)
    local props = rawget(t, "__props")
    if props then props[k] = v end
  end,
  __call = stub_call,
  __tostring = function(t) return rawget(t, "__name") or "Instance" end,
  __len = function() return 0 end,
  __add = function() return 0 end,
  __sub = function() return 0 end,
  __mul = function() return 0 end,
  __div = function() return 0 end,
  __mod = function() return 0 end,
  __pow = function() return 0 end,
  __unm = function() return 0 end,
  __concat = function(a, b) return tostring(a) .. tostring(b) end,
  __eq = function() return false end,
  __lt = function() return false end,
  __le = function() return false end,
  __name = "Instance",
  __metatable = false, -- Roblox instances expose `getmetatable(inst) == "locked"`.
}

function M.new_stub(kind, name)
  return new_stub(kind, name)
end

--------------------------------------------------------------------------------
-- small value types
--------------------------------------------------------------------------------

local function vector3_mt()
  local v3 = {}
  v3.__index = function(t, k)
    if k == "X" then return rawget(t, 1) end
    if k == "Y" then return rawget(t, 2) end
    if k == "Z" then return rawget(t, 3) end
    if k == "Magnitude" then
      return math.sqrt(rawget(t, 1) ^ 2 + rawget(t, 2) ^ 2 + rawget(t, 3) ^ 2)
    end
    if k == "Unit" then return new_stub("Vector3", "Unit") end
    return stub_index(t, k)
  end
  v3.__add = function(a, b) return M.Vector3.new(a[1] + b[1], a[2] + b[2], a[3] + b[3]) end
  v3.__sub = function(a, b) return M.Vector3.new(a[1] - b[1], a[2] - b[2], a[3] - b[3]) end
  v3.__mul = function(a, b)
    if type(b) == "number" then return M.Vector3.new(a[1] * b, a[2] * b, a[3] * b) end
    if type(a) == "number" then return M.Vector3.new(b[1] * a, b[2] * a, b[3] * a) end
    return M.Vector3.new(0, 0, 0)
  end
  v3.__unm = function(a) return M.Vector3.new(-a[1], -a[2], -a[3]) end
  v3.__tostring = function(a) return string.format("%g, %g, %g", a[1], a[2], a[3]) end
  v3.__eq = function(a, b) return a[1] == b[1] and a[2] == b[2] and a[3] == b[3] end
  v3.__name = "Vector3"
  return v3
end

local V3MT = vector3_mt()

M.Vector3 = {
  new = function(x, y, z) return setmetatable({ x or 0, y or 0, z or 0 }, V3MT) end,
  FromNormalId = function() return setmetatable({ 0, 0, 0 }, V3MT) end,
  zero = setmetatable({ 0, 0, 0 }, V3MT),
  one = setmetatable({ 1, 1, 1 }, V3MT),
}

M.Vector2 = {
  new = function(x, y)
    local v = { x or 0, y or 0 }
    return setmetatable(v, {
      __index = function(t, k)
        if k == "X" then return rawget(t, 1) end
        if k == "Y" then return rawget(t, 2) end
        if k == "Magnitude" then return math.sqrt(rawget(t, 1) ^ 2 + rawget(t, 2) ^ 2) end
        return stub_index(t, k)
      end,
      __name = "Vector2",
      __tostring = function(t) return string.format("%g, %g", t[1], t[2]) end,
    })
  end,
}

local function color_index(t, k)
  if k == "R" then return rawget(t, 1) end
  if k == "G" then return rawget(t, 2) end
  if k == "B" then return rawget(t, 3) end
  return stub_index(t, k)
end

M.Color3 = {
  new = function(r, g, b) return setmetatable({ r or 0, g or 0, b or 0 }, { __index = color_index, __name = "Color3" }) end,
  fromRGB = function(r, g, b) return M.Color3.new((r or 0) / 255, (g or 0) / 255, (b or 0) / 255) end,
  fromHSV = function() return M.Color3.new(0, 0, 0) end,
}

M.UDim = { new = function(s, o) return setmetatable({ s or 0, o or 0 }, { __name = "UDim" }) end }
M.UDim2 = {
  new = function(xs, xo, ys, yo) return setmetatable({ xs or 0, xo or 0, ys or 0, yo or 0 }, { __name = "UDim2" }) end,
  fromScale = function(x, y) return M.UDim2.new(x, 0, y, 0) end,
  fromOffset = function(x, y) return M.UDim2.new(0, x, 0, y) end,
}
M.BrickColor = {
  new = function(v) return setmetatable({ Number = 1, Name = tostring(v or "Medium stone grey") }, { __name = "BrickColor" }) end,
  Random = function() return M.BrickColor.new(1) end,
  palette = function() return M.BrickColor.new(1) end,
}
M.NumberRange = { new = function(a, b) return { Min = a or 0, Max = b or a or 0 } end }
M.NumberSequence = { new = function(a, b) return { a or 0, b or 0 } end }
M.NumberSequenceKeypoint = { new = function(t, v) return { Time = t or 0, Value = v or 0 } end }
M.ColorSequence = { new = function(c) return { c or M.Color3.new(0, 0, 0) } end }
M.ColorSequenceKeypoint = { new = function(t, c) return { Time = t or 0, Value = c } end }
M.Ray = {
  new = function(o, d) return setmetatable({ Origin = o or M.Vector3.new(0, 0, 0), Direction = d or M.Vector3.new(0, 0, 0) }, { __name = "Ray" }) end,
}
M.Rect = { new = function(...) return setmetatable({ ... }, { __name = "Rect" }) end }
M.Region3 = { new = function() return setmetatable({}, { __name = "Region3" }) end }
M.TweenInfo = { new = function(t, s, e, d, r, rev)
  return setmetatable({ Time = t or 0, EasingStyle = e, EasingDirection = d, RepeatCount = r or 0, Reverses = rev or false }, { __name = "TweenInfo" })
end }
M.RaycastParams = { new = function() return new_stub("RaycastParams", "RaycastParams") end }
M.OverlapParams = { new = function() return new_stub("OverlapParams", "OverlapParams") end }
M.PhysicalProperties = { new = function() return new_stub("PhysicalProperties", "PhysicalProperties") end }

--- Minimal but structurally plausible CFrame.
M.CFrame = (function()
  local function cframe_index(t, k)
    if k == "X" or k == "Y" or k == "Z" then return rawget(t, "p")[k == "X" and 1 or (k == "Y" and 2 or 3)] end
    if k == "Position" or k == "p" then return rawget(t, "p") end
    if k == "LookVector" then return M.Vector3.new(0, 0, -1) end
    if k == "RightVector" then return M.Vector3.new(1, 0, 0) end
    if k == "UpVector" then return M.Vector3.new(0, 1, 0) end
    return stub_index(t, k)
  end
  local mt = {
    __index = cframe_index,
    __mul = function(a, b)
      if type(b) == "number" or getmetatable(b) == V3MT or (type(b) == "table" and b[1] ~= nil and b.X == nil) then
        return a
      end
      return a
    end,
    __add = function(a, b) return setmetatable({ p = M.Vector3.new(b.X or 0, b.Y or 0, b.Z or 0), m = a.m }, mt) end,
    __sub = function(a, b) return a end,
    __tostring = function() return "CFrame" end,
    __name = "CFrame",
  }
  local CFrame = {}
  CFrame.new = function(x, y, z)
    if type(x) == "table" and x ~= nil and getmetatable(x) == V3MT then
      return setmetatable({ p = x, m = {} }, mt)
    end
    return setmetatable({ p = M.Vector3.new(x or 0, y or 0, z or 0), m = {} }, mt)
  end
  CFrame.identity = setmetatable({ p = M.Vector3.new(0, 0, 0), m = {} }, mt)
  CFrame.Angles = function() return CFrame.new(0, 0, 0) end
  CFrame.fromEulerAnglesXYZ = CFrame.Angles
  CFrame.fromEulerAnglesYXZ = CFrame.Angles
  CFrame.fromAxisAngle = function() return CFrame.new(0, 0, 0) end
  CFrame.fromMatrix = function(p) return CFrame.new(p) end
  CFrame.lookAt = function(a, b) return CFrame.new(a) end
  return CFrame
end)()

M.Enum = setmetatable({}, {
  __index = function(t, k)
    local enum = setmetatable({}, {
      __index = function(_, item)
        if item == "GetEnumItems" then return function() return {} end end
        return setmetatable({ Name = tostring(item), Value = 0, EnumType = k }, { __name = "EnumItem", __tostring = function(s) return "Enum." .. k .. "." .. tostring(s.Name) end })
      end,
      __tostring = function() return "Enum." .. tostring(k) end,
    })
    rawset(t, k, enum)
    return enum
  end,
})

--------------------------------------------------------------------------------
-- IO style captures (hidden URLs / file names)
--------------------------------------------------------------------------------
local function record_url(kind, url)
  ctx.url_count = ctx.url_count + 1
  local s = tostring(url)
  log("HTTP %s -> %s", kind, s:sub(1, 500))
  ctx.capture({ kind = "url", name = kind, value = s })
end

local function record_file(kind, path, size)
  log("FILE %s %s%s", kind, tostring(path), size and (" (" .. tostring(size) .. " bytes)") or "")
  ctx.capture({ kind = "file", name = kind, value = tostring(path) })
end

--------------------------------------------------------------------------------
-- global table
--------------------------------------------------------------------------------

--- Builds the stub global table.
--- @param policy string "strict" | "codex" | "permissive"
--- @param opts table|nil { place_id = number, deterministic = bool }
--- @return table globals
function M.build(policy, opts)
  opts = opts or {}
  policy = policy or "codex"
  local G = {}
  local fixed_time = 1700000000

  local function stub(kind) return new_stub(kind or "Instance", kind or "Instance") end

  -- ---- core services / containers ----
  local game = stub("DataModel")
  rawget(game, "__props").PlaceId = opts.place_id or 0
  rawget(game, "__props").JobId = "excalibur-job"
  rawget(game, "__props").CreatorId = 0
  rawget(game, "__props").GameId = 0
  rawget(game, "__props").PlaceVersion = 1
  rawget(game, "__props").Workspace = stub("Workspace")
  rawget(game, "__props").Players = stub("Players")
  rawget(game, "__props").Lighting = stub("Lighting")
  rawget(game, "__props").ReplicatedStorage = stub("ReplicatedStorage")
  rawget(game, "__props").ServerStorage = stub("ServerStorage")
  rawget(game, "__props").HttpService = stub("HttpService")
  G.game = game
  G.workspace = rawget(game, "__props").Workspace
  G.Workspace = G.workspace
  G.script = stub("LocalScript")
  G.shared = {}
  G.plugin = stub("Plugin")
  G.owner = stub("Player")
  G.Players = rawget(game, "__props").Players

  G.Instance = setmetatable({
    new = function(class, parent)
      local i = new_stub(class or "Instance", tostring(class or "Instance"))
      if parent ~= nil then rawget(i, "__props").Parent = parent end
      return i
    end,
    fromExisting = function(v) return v end,
  }, { __call = function(_, ...) return G.Instance.new(...) end, __name = "Instance" })

  G.Enum = M.Enum
  G.Vector3 = M.Vector3
  G.Vector2 = M.Vector2
  G.CFrame = M.CFrame
  G.Color3 = M.Color3
  G.UDim = M.UDim
  G.UDim2 = M.UDim2
  G.BrickColor = M.BrickColor
  G.NumberRange = M.NumberRange
  G.NumberSequence = M.NumberSequence
  G.ColorSequence = M.ColorSequence
  G.Ray = M.Ray
  G.Rect = M.Rect
  G.Region3 = M.Region3
  G.TweenInfo = M.TweenInfo
  G.RaycastParams = M.RaycastParams
  G.OverlapParams = M.OverlapParams
  G.PhysicalProperties = M.PhysicalProperties
  G.Font = M.Enum.Font
  G.Axes = M.Enum.Axes
  G.EasingStyle = M.Enum.EasingStyle
  G.TweenStatus = M.Enum.TweenStatus

  G.Random = {
    new = function(seed)
      return {
        NextNumber = function() return 0.5 end,
        NextInteger = function(a, b) return a or 1 end,
        NextUnitVector = function() return M.Vector3.new(0, 0, 0) end,
        Clone = function(self) return self end,
      }
    end,
  }

  G.typeof = function(v)
    if type(v) == "table" then
      local mt = getmetatable(v)
      if mt == "locked" or mt == false then return "Instance" end
      local n = type(v.__name)
      if n ~= "nil" then return v.__name end
      if rawget(v, "__kind") then return "Instance" end
    end
    return type(v)
  end
  G.tick = function() return fixed_time + 0.5 end
  G.time = function() return 0.5 end
  G.elapsedTime = function() return 0.5 end
  G.wait = function() return 0.03 end
  G.waitForChild = function() return stub("Instance") end
  G.spawn = function(f, ...) if type(f) == "function" then pcall(f, ...) end return nil end
  G.delay = G.spawn
  G.settings = function() return stub("Settings") end
  G.getfenv = G.getfenv
  G.printidentity = function() end

  G.task = {
    wait = function(t) return t or 0 end,
    spawn = function(f, ...) if type(f) == "function" then pcall(f, ...) end return nil end,
    delay = function(_, f, ...) if type(f) == "function" then pcall(f, ...) end return nil end,
    defer = function(f, ...) if type(f) == "function" then pcall(f, ...) end return nil end,
    cancel = function() end,
    synchronize = function(f, ...) return f(...) end,
    desynchronize = function(f, ...) return f(...) end,
  }

  -- ---- Http / JSON (URLs are captured) ----
  local function http_stub(kind)
    return function(self, url, ...)
      record_url(kind, url)
      return ""
    end
  end
  G.HttpService = {
    GetAsync = http_stub("HttpService:GetAsync"),
    PostAsync = http_stub("HttpService:PostAsync"),
    RequestAsync = http_stub("HttpService:RequestAsync"),
    JSONDecode = function(_, s) return {} end,
    JSONEncode = function(_, t) return "{}" end,
    GenerateGUID = function() return "00000000-0000-0000-0000-000000000000" end,
    UrlEncode = function(_, s) return tostring(s) end,
    UrlDecode = function(_, s) return tostring(s) end,
  }
  rawget(game, "__props").HttpService = G.HttpService

  G.http_request = function(params)
    if type(params) == "table" then
      record_url("http_request", params.Url or params.url)
      return { StatusCode = 200, Body = "", Headers = {} }
    end
    return { StatusCode = 200, Body = "", Headers = {} }
  end
  G.request = G.http_request
  G.syn = { request = G.http_request }
  G.fluxus = { request = G.http_request }

  -- ---- data / serialisation ----
  G.buffer = G.buffer
  G.utf8 = G.utf8 or { char = string.char, len = string.len, offset = function() return 1 end, codepoint = function(s) return string.byte(s) end }
  G.crypt = { base64 = { encode = function(s) return s end, decode = function(s) return s end }, hash = function() return "" end }
  G.JSONDecode = G.HttpService.JSONDecode
  G.JSONEncode = G.HttpService.JSONEncode

  -- ---- executor style helpers ----
  G.getgenv = function() return G.__env end
  G.getrenv = function() return G.__env end
  G.getreg = function() return {} end
  G.getrawmetatable = function(v) return getmetatable(v) or {} end
  G.setreadonly = function() return true end
  G.isreadonly = function() return false end
  G.hookfunction = function(f) return f end
  G.hookmetamethod = function() return function() end end
  G.restorefunction = function(f) return f end
  G.getnamecallmethod = function() return "GetService" end
  G.setnamecallmethod = function() end
  G.checkcaller = function() return true end
  G.is_synapse_function = function() return false end
  G.getscriptbytecode = function() return string.dump(function() end) end
  G.setclipboard = function() return true end
  G.getclipboard = function() return "" end
  G.writefile = function(name, data) record_file("writefile", name, data and #tostring(data) or 0) end
  G.appendfile = G.writefile
  G.readfile = function(name)
    record_file("readfile", name)
    return ""
  end
  G.isfile = function() return false end
  G.delfile = function(name) record_file("delfile", name) end
  G.listfiles = function(path) record_file("listfiles", path); return {} end
  G.makefolder = function(path) record_file("makefolder", path) end
  G.loadfile = function(name)
    record_file("loadfile", name)
    return function() end
  end
  G.dofile = G.loadfile
  G.identifyexecutor = function() return "Excalibur", "1.0.0" end
  G.getexecutorname = G.identifyexecutor
  G.decompile = function() return "--[[ Excalibur: decompile() is not implemented ]]" end
  G.getconnections = function() return {} end
  G.firetouchinterest = function(...) return nil end
  G.fireclickdetector = function() end
  G.fireproximityprompt = function() end
  G.setfpscap = function() return 60 end
  G.getgc = function() return collectgarbage("count") end
  G.stats = G.getgc

  -- ---- Drawing / misc UI libraries ----
  local function ui_factory()
    return function() return stub("Drawing") end
  end
  G.Drawing = setmetatable({}, { __index = function(t, k) local v = ui_factory(); rawset(t, k, v); return v end })
  G.gethui = function() return stub("Instance") end
  G.getcustomasset = function(p) return tostring(p) end

  -- ---- fallback policy ----
  G.__policy = policy
  M.policy = policy
  M.globals = G
  return G
end

--- Returns true when the given global name is a known Roblox/executor name.
--- Used by "codex" policy to decide between stubbing and returning nil.
function M.is_known_api(name)
  local known = M.known_api
  return known ~= nil and known[name] == true
end

M.known_api = {
  game = true, workspace = true, Workspace = true, script = true, shared = true, plugin = true,
  Instance = true, Enum = true, Vector3 = true, Vector2 = true, CFrame = true, Color3 = true,
  UDim = true, UDim2 = true, BrickColor = true, NumberRange = true, NumberSequence = true,
  ColorSequence = true, Ray = true, Rect = true, Region3 = true, TweenInfo = true,
  RaycastParams = true, OverlapParams = true, PhysicalProperties = true, Random = true,
  typeof = true, tick = true, time = true, elapsedTime = true, wait = true, spawn = true,
  delay = true, settings = true, task = true, HttpService = true, Players = true, owner = true,
  request = true, http_request = true, syn = true, fluxus = true, getgenv = true, getrenv = true,
  getreg = true, getrawmetatable = true, setreadonly = true, isreadonly = true, hookfunction = true,
  hookmetamethod = true, restorefunction = true, getnamecallmethod = true, setnamecallmethod = true,
  checkcaller = true, is_synapse_function = true, getscriptbytecode = true, setclipboard = true,
  getclipboard = true, writefile = true, appendfile = true, readfile = true, isfile = true,
  delfile = true, listfiles = true, makefolder = true, loadfile = true, dofile = true,
  identifyexecutor = true, getexecutorname = true, decompile = true, getconnections = true,
  firetouchinterest = true, fireclickdetector = true, fireproximityprompt = true, setfpscap = true,
  getgc = true, stats = true, Drawing = true, gethui = true, getcustomasset = true,
  UTF8 = true, utf8 = true, buffer = true, crypt = true, JSONDecode = true, JSONEncode = true,
  printidentity = true, waitForChild = true, Font = true, Axes = true, EasingStyle = true,
}

return M
