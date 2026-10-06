-- Trace event bridge. The host runtime may provide native debug hooks; stock Luau does not.
local __protez_trace_token = "__PROTEZ_TRACE_TOKEN__"
local __protez_trace_prefix = "__PROTEZ_TRACE_" .. __protez_trace_token .. "|"
local __protez_trace_sequence = 0
local __protez_trace_started = 0

if __protez_type(__protez_native_clock) == "function" then
    local ok, value = __protez_raw_pcall(__protez_native_clock)
    if ok and __protez_type(value) == "number" then
        __protez_trace_started = value
    end
end

local function __protez_trace_encode(value)
    local text = __protez_tostring(value or "")
    if #text > 2048 then
        text = __protez_sub(text, 1, 2048)
    end
    return __protez_base64(text)
end

local function __protez_trace_emit(event, name, source, line, detail)
    __protez_trace_sequence = __protez_trace_sequence + 1
    local elapsed = __protez_trace_sequence / 1000
    if __protez_type(__protez_native_clock) == "function" then
        local ok, value = __protez_raw_pcall(__protez_native_clock)
        if ok and __protez_type(value) == "number" then
            elapsed = value - __protez_trace_started
        end
    end

    local event_name = __protez_tostring(event or "UNKNOWN"):upper():gsub("%s+", "_")
    local line_number = tonumber(line) or 0
    __protez_raw_print(
        __protez_trace_prefix .. __protez_trace_sequence .. "|" .. event_name .. "|" ..
        __protez_tostring(elapsed) .. "|" .. line_number .. "|" ..
        __protez_trace_encode(name) .. "|" .. __protez_trace_encode(source) .. "|" ..
        __protez_trace_encode(detail)
    )
end

_G.__PROTEZ_TRACE_EVENT = __protez_trace_emit

local __protez_hook_active = false
if __protez_type(__protez_native_sethook) == "function" then
    local function __protez_debug_hook(event, hook_line)
        local source_name = ""
        local function_name = ""
        local line_number = tonumber(hook_line) or 0
        if __protez_type(__protez_native_debug_info) == "function" then
            local ok, source_value, current_line, name_value = __protez_raw_pcall(
                __protez_native_debug_info,
                2,
                "sln"
            )
            if ok then
                source_name = __protez_tostring(source_value or "")
                line_number = tonumber(current_line) or line_number
                function_name = __protez_tostring(name_value or "")
            end
        end
        __protez_trace_emit(event, function_name, source_name, line_number, "")
    end

    local ok, error_message = __protez_raw_pcall(
        __protez_native_sethook,
        __protez_debug_hook,
        "crl",
        1000
    )
    if ok then
        __protez_hook_active = true
        __protez_trace_emit("HOOK_READY", "debug.sethook", "", 0, "mode=crl,count=1000")
    else
        __protez_trace_emit(
            "HOOK_UNAVAILABLE",
            "debug.sethook",
            "",
            0,
            __protez_tostring(error_message)
        )
    end
else
    __protez_trace_emit(
        "HOOK_UNAVAILABLE",
        "debug.sethook",
        "",
        0,
        "Luau runtime does not expose native debug hooks"
    )
end

_G.__PROTEZ_NATIVE_HOOKS_ACTIVE = __protez_hook_active
