-- Minimal local Roblox-shaped environment for the Protez Luau process.
-- This is a mock only: HTTP, filesystem access and asynchronous work are disabled.

local __protez_type = type
local __protez_tostring = tostring
local __protez_raw_print = print
local __protez_raw_pcall = pcall
local __protez_raw_xpcall = xpcall
local __protez_raw_error = error
local __protez_pack = table.pack
local __protez_unpack = table.unpack or unpack
local __protez_concat = table.concat
local __protez_sub = string.sub
local __protez_byte = string.byte
local __protez_floor = math.floor
local __protez_rawset = rawset
local __protez_setmetatable = setmetatable
local __protez_native_debug = debug
local __protez_native_sethook = nil
local __protez_native_debug_info = nil
local __protez_native_clock = nil
if __protez_type(__protez_native_debug) == "table" then
    __protez_native_sethook = __protez_native_debug.sethook
    __protez_native_debug_info = __protez_native_debug.info
end
if __protez_type(os) == "table" then
    __protez_native_clock = os.clock
end
local __protez_capture_nonce = "__PROTEZ_CAPTURE_TOKEN__"
local __protez_marker = "__PROTEZ_CAPTURE_" .. __protez_capture_nonce .. "|"
local __protez_capture_count = 0
local __protez_clock_value = 0

local function __protez_log(level, message)
    __protez_raw_print("[PROTEZ:" .. level .. "] " .. __protez_tostring(message))
    local emitter = _G and _G.__PROTEZ_TRACE_EVENT
    if __protez_type(emitter) == "function" then
        emitter("MOCK", level, "", 0, __protez_tostring(message))
    end
end

local function __protez_base64(source)
    local alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"
    local output = {}
    local source_length = #source

    for index = 1, source_length, 3 do
        local first = __protez_byte(source, index) or 0
        local second = __protez_byte(source, index + 1) or 0
        local third = __protez_byte(source, index + 2) or 0
        local packed = first * 65536 + second * 256 + third
        local a = __protez_floor(packed / 262144) % 64 + 1
        local b = __protez_floor(packed / 4096) % 64 + 1
        local c = __protez_floor(packed / 64) % 64 + 1
        local d = packed % 64 + 1

        output[#output + 1] = __protez_sub(alphabet, a, a)
        output[#output + 1] = __protez_sub(alphabet, b, b)
        output[#output + 1] = index + 1 <= source_length
            and __protez_sub(alphabet, c, c) or "="
        output[#output + 1] = index + 2 <= source_length
            and __protez_sub(alphabet, d, d) or "="
    end

    return __protez_concat(output)
end

local function __protez_capture(source, kind)
    if __protez_type(source) ~= "string" or #source == 0 then
        return
    end

    __protez_capture_count = __protez_capture_count + 1
    local index = __protez_capture_count
    local encoded = __protez_base64(source)
    __protez_raw_print(__protez_marker .. "B|" .. index .. "|" .. kind)

    for offset = 1, #encoded, 4096 do
        __protez_raw_print(
            __protez_marker .. "C|" .. index .. "|" ..
            __protez_sub(encoded, offset, offset + 4095)
        )
    end

    __protez_raw_print(__protez_marker .. "E|" .. index .. "|" .. #source)
    __protez_log("INFO", "captured payload via " .. kind)
end

local function __protez_noop(...)
    return nil
end

local __protez_services = {}
local __protez_game
local __protez_proxy

local function __protez_service(service_name)
    local name = __protez_tostring(service_name or "UnknownService")
    if not __protez_services[name] then
        __protez_services[name] = __protez_proxy(name, name)
    end
    return __protez_services[name]
end

__protez_proxy = function(name, class_name)
    local object = {
        Name = class_name or name,
        ClassName = class_name or "Folder",
    }

    return __protez_setmetatable(object, {
        __index = function(self, key)
            if key == "Parent" then
                return nil
            end
            if name == "game" then
                if key == "GetService" or key == "FindService" then
                    return function(_, service_name)
                        __protez_log("DEBUG", "GetService(" .. __protez_tostring(service_name) .. ")")
                        return __protez_service(service_name)
                    end
                end
                if key == "HttpGet" or key == "HttpGetAsync" then
                    return function(_, _url, ...)
                        __protez_log("WARN", "game:HttpGet blocked; network access is disabled")
                        return ""
                    end
                end
                if key == "Workspace" or key == "workspace" then
                    return __protez_service("Workspace")
                end
                if key == "Players" or key == "ReplicatedStorage" or
                    key == "RunService" or key == "HttpService" or
                    key == "UserInputService" or key == "TweenService" then
                    return __protez_service(key)
                end
            end
            if key == "WaitForChild" then
                return function(_, child_name, ...)
                    __protez_log("DEBUG", name .. ":WaitForChild(" .. __protez_tostring(child_name) .. ")")
                    return __protez_proxy(name .. "." .. __protez_tostring(child_name), child_name)
                end
            end
            if key == "FindFirstChild" or key == "FindFirstChildOfClass" then
                return function(_, child_name, ...)
                    return __protez_proxy(name .. "." .. __protez_tostring(child_name), child_name)
                end
            end
            if key == "GetChildren" or key == "GetDescendants" then
                return function()
                    return {}
                end
            end
            if key == "IsA" then
                return function(_, requested_class)
                    return class_name == requested_class
                end
            end
            if key == "Destroy" or key == "ClearAllChildren" or key == "Disconnect" then
                return function()
                    __protez_log("DEBUG", name .. ":" .. key .. "()")
                end
            end
            if key == "Connect" or key == "Once" then
                return function(_, _callback)
                    __protez_log("DEBUG", name .. ":" .. key .. "()")
                    return __protez_proxy(name .. ".Connection", "RBXScriptConnection")
                end
            end
            if key == "Parent" then
                return nil
            end
            return __protez_proxy(name .. "." .. __protez_tostring(key), key)
        end,
        __newindex = function(self, key, value)
            __protez_rawset(self, key, value)
            if key ~= "Parent" then
                __protez_log("DEBUG", name .. "." .. __protez_tostring(key) .. " assigned")
            end
        end,
        __call = function(_, ...)
            __protez_log("DEBUG", name .. " called")
            return nil
        end,
        __tostring = function()
            return name
        end,
    })
end

__protez_game = __protez_proxy("game", "DataModel")
__protez_rawset(__protez_game, "PlaceId", 0)
__protez_rawset(__protez_game, "GameId", 0)
__protez_rawset(__protez_game, "JobId", "protez-local")

local __protez_global = _G or getfenv(0)
__protez_rawset(__protez_global, "game", __protez_game)
__protez_rawset(__protez_global, "workspace", __protez_service("Workspace"))
__protez_rawset(__protez_global, "Workspace", __protez_service("Workspace"))
__protez_rawset(__protez_global, "Players", __protez_service("Players"))
__protez_rawset(__protez_global, "Instance", {
    new = function(class_name, parent)
        local class = __protez_tostring(class_name or "Instance")
        __protez_log("INFO", "Instance.new(" .. class .. ")")
        local instance = __protez_proxy(class, class)
        if parent ~= nil then
            instance.Parent = parent
        end
        return instance
    end,
})

for _, type_name in ipairs({
    "Enum", "Vector2", "Vector3", "Vector3int16", "CFrame", "Color3",
    "UDim", "UDim2", "TweenInfo", "RaycastParams", "BrickColor",
    "NumberRange", "Rect", "Region3",
}) do
    __protez_rawset(__protez_global, type_name, __protez_proxy(type_name, type_name))
end

local __protez_original_pcall = __protez_raw_pcall
local __protez_original_xpcall = __protez_raw_xpcall
local __protez_original_error = __protez_raw_error

__protez_rawset(__protez_global, "loadstring", function(source, chunk_name)
    __protez_capture(source, "loadstring")
    return __protez_noop
end)
__protez_rawset(__protez_global, "load", function(source, chunk_name, mode, environment)
    __protez_capture(source, "load")
    return __protez_noop
end)
__protez_rawset(__protez_global, "require", function(module)
    if __protez_type(module) == "string" and
        (module:find("\n", 1, true) or module:match("^%s*return%s") or
        module:match("^%s*local%s") or module:match("^%s*function%s")) then
        __protez_capture(module, "require")
    else
        __protez_log("DEBUG", "require intercepted; module loading is disabled")
    end
    return __protez_noop
end)

__protez_rawset(__protez_global, "pcall", function(callback, ...)
    local result = __protez_pack(__protez_original_pcall(callback, ...))
    if not result[1] then
        __protez_log("WARN", "pcall caught: " .. __protez_tostring(result[2]))
    end
    return __protez_unpack(result, 1, result.n)
end)
__protez_rawset(__protez_global, "xpcall", function(callback, handler, ...)
    local result = __protez_pack(__protez_original_xpcall(callback, handler, ...))
    if not result[1] then
        __protez_log("WARN", "xpcall caught an error")
    end
    return __protez_unpack(result, 1, result.n)
end)
__protez_rawset(__protez_global, "error", function(message, level)
    __protez_log("WARN", "error intercepted: " .. __protez_tostring(message))
    return __protez_original_error(message, level)
end)
__protez_rawset(__protez_global, "warn", function(message, ...)
    __protez_log("WARN", message)
end)

local __protez_debug = {
    traceback = function(message, ...)
        return __protez_tostring(message or "") .. "\nstack traceback: [Protez stub]"
    end,
    getinfo = function(...)
        return {
            source = "@Protez",
            short_src = "Protez",
            what = "Lua",
            linedefined = 0,
            lastlinedefined = 0,
            currentline = 0,
            nups = 0,
        }
    end,
    info = function(...)
        return nil
    end,
    gethook = function(...)
        return nil
    end,
    sethook = function(...)
        return nil
    end,
    getregistry = function(...)
        return {}
    end,
    getupvalue = function(...)
        return nil
    end,
    setupvalue = function(...)
        return nil
    end,
    getlocal = function(...)
        return nil
    end,
    setlocal = function(...)
        return nil
    end,
    profilebegin = function(...)
        return nil
    end,
    profileend = function(...)
        return nil
    end,
}
__protez_rawset(__protez_global, "debug", __protez_debug)

__protez_rawset(__protez_global, "getgenv", function()
    return __protez_global
end)
__protez_rawset(__protez_global, "getrenv", function()
    return __protez_global
end)
__protez_rawset(__protez_global, "getfenv", function(...)
    return __protez_global
end)
__protez_rawset(__protez_global, "setfenv", function(callback, ...)
    return callback
end)
__protez_rawset(__protez_global, "setclipboard", __protez_noop)

local function __protez_clock()
    local current = __protez_clock_value
    __protez_clock_value = __protez_clock_value + 0.01
    return current
end
__protez_rawset(__protez_global, "tick", __protez_clock)
__protez_rawset(__protez_global, "time", __protez_clock)
__protez_rawset(__protez_global, "wait", function(duration)
    local delay = tonumber(duration) or 0
    __protez_clock_value = __protez_clock_value + delay
    return delay
end)
__protez_rawset(__protez_global, "spawn", __protez_noop)

__protez_rawset(__protez_global, "task", {
    wait = function(duration)
        local delay = tonumber(duration) or 0
        __protez_clock_value = __protez_clock_value + delay
        return delay
    end,
    spawn = function(...)
        __protez_log("DEBUG", "task.spawn ignored")
        return nil
    end,
    defer = function(...)
        __protez_log("DEBUG", "task.defer ignored")
        return nil
    end,
    delay = function(...)
        __protez_log("DEBUG", "task.delay ignored")
        return nil
    end,
    cancel = __protez_noop,
})

__protez_rawset(__protez_global, "request", function(...)
    __protez_log("WARN", "request blocked; network access is disabled")
    return { StatusCode = 0, Success = false, Body = "" }
end)
__protez_rawset(__protez_global, "http_request", __protez_global.request)

__protez_rawset(__protez_global, "io", nil)
__protez_rawset(__protez_global, "dofile", nil)
__protez_rawset(__protez_global, "loadfile", nil)
__protez_rawset(__protez_global, "package", nil)
__protez_rawset(__protez_global, "os", {
    clock = __protez_clock,
    time = function()
        return 0
    end,
    date = function()
        return "1970-01-01"
    end,
    difftime = function(first, second)
        return (tonumber(first) or 0) - (tonumber(second) or 0)
    end,
})
