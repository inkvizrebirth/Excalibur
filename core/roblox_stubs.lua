--[[
    Compatibility entry point.

    The Roblox / executor API stubs the sandbox installs live in
    core/lua/roblox_stubs.lua (next to the runner and the hooks, so the whole Lua
    side travels as one folder).  This file exposes the same module at the path
    named by the project specification.

        Excalibur's sandbox  ->  core/lua/roblox_stubs.lua   (used at runtime)
        spec path            ->  core/roblox_stubs.lua       (this forwarder)

    Usage from Lua:  local stubs = dofile("core/roblox_stubs.lua")
                     local env = stubs.build("codex", {capture = print})
]]

local source = (debug.getinfo(1, "S") or {}).source or ""
local here = source:gsub("^@", "")
local dir = here:match("^(.*)[/\\][^/\\]*$") or "."
local implementation = dir .. "/lua/roblox_stubs.lua"

local chunk, err = loadfile(implementation)
if not chunk then
    error("core/roblox_stubs.lua: cannot load " .. implementation .. ": " .. tostring(err), 0)
end

local module = chunk()
if type(module) ~= "table" then
    error("core/roblox_stubs.lua: " .. implementation .. " did not return a module table", 0)
end

module.implementation = implementation
return module
