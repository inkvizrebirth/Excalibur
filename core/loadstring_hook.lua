--[[
    Compatibility entry point for the loadstring hook.

    The real implementation is core/lua/hooks.lua: it wraps load / loadstring /
    table.concat / string.char, dumps every compiled chunk to dump_NNN.lua, every
    reassembled string to concat_NNN.txt and every string.char fragment to
    char_fragments.txt.  The runner (core/lua/runner.lua) loads that file
    directly; this forwarder keeps the path named by the project specification
    working and re-exports only the hook making half.

        local hooks = dofile("core/loadstring_hook.lua")
        local loader = hooks.make_loader(function(body, name) ... end)
]]

local source = (debug.getinfo(1, "S") or {}).source or ""
local here = source:gsub("^@", "")
local dir = here:match("^(.*)[/\\][^/\\]*$") or "."
local implementation = dir .. "/lua/hooks.lua"

local chunk, err = loadfile(implementation)
if not chunk then
    error("core/loadstring_hook.lua: cannot load " .. implementation .. ": " .. tostring(err), 0)
end

local function hooks_module()
    return chunk()
end

local module = {
    implementation = implementation,
    set_deps = function(deps)
        return hooks_module().set_deps(deps)
    end,
    -- the load/loadstring half of the instrumentation
    make_loader = function(...)
        return hooks_module().make_loader(...)
    end,
    -- the string reconstruction half (WRD rebuilds its payload this way)
    make_concat = function(...)
        return hooks_module().make_concat(...)
    end,
    make_char = function(...)
        return hooks_module().make_char(...)
    end,
    module = hooks_module,
}

return module
