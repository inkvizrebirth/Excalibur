#include "lua.h"
#include "lualib.h"
#include "luacode.h"
#include "lbytecode.h"
#include "lfunc.h"
#include "lstate.h"
#include "Luau/BytecodeDump.h"
#include "appcontainer_launcher.h"

#include <algorithm>
#include <chrono>
#include <clocale>
#include <cmath>
#include <cstddef>
#include <cstdint>
#include <cstdio>
#include <exception>
#include <cstdlib>
#include <cstring>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <locale>
#include <sstream>
#include <string>
#include <string_view>
#include <vector>

#ifdef _WIN32
#include <fcntl.h>
#include <io.h>
#endif

namespace
{
constexpr size_t kMaxSourceBytes = 64 * 1024 * 1024;
constexpr size_t kMaxVmBytes = 256 * 1024 * 1024;
constexpr size_t kMaxDynamicChunkBytes = 16 * 1024 * 1024;
constexpr size_t kMaxTraceStringBytes = 128;
constexpr size_t kMaxLocalsPerSnapshot = 16;
constexpr uint64_t kLocalSnapshotStride = 64;

struct MemoryBudget
{
    size_t used = 0;
    size_t limit = kMaxVmBytes;
};

void* boundedAllocator(void* userdata, void* pointer, size_t oldSize, size_t newSize)
{
    auto* budget = static_cast<MemoryBudget*>(userdata);
    if (newSize == 0)
    {
        std::free(pointer);
        if (pointer)
            budget->used -= std::min(budget->used, oldSize);
        return nullptr;
    }

    const size_t current = pointer ? budget->used - std::min(budget->used, oldSize) : budget->used;
    if (newSize > budget->limit - std::min(budget->limit, current))
        return nullptr;

    void* replacement = std::realloc(pointer, newSize);
    if (replacement)
        budget->used = current + newSize;
    return replacement;
}

struct TraceContext
{
    std::string prefix;
    std::string capturePrefix;
    std::chrono::steady_clock::time_point started = std::chrono::steady_clock::now();
    uint64_t sequence = 0;
    uint64_t stepCount = 0;
    uint64_t captureCount = 0;
    uint64_t capturedBytes = 0;
    uint64_t maxSteps = 25000;
    uint64_t maxCaptures = 100;
    uint64_t maxCaptureBytes = 16 * 1024 * 1024;
    bool active = false;
    bool hookReady = false;
    bool traceStopped = false;
    bool limitReported = false;
    bool outputFailed = false;
};

int sandboxClock(lua_State* state)
{
    const auto* context = static_cast<const TraceContext*>(lua_callbacks(state)->userdata);
    const auto started = context ? context->started : std::chrono::steady_clock::now();
    const double elapsed = std::chrono::duration<double>(std::chrono::steady_clock::now() - started).count();
    lua_pushnumber(state, elapsed);
    return 1;
}

std::string base64(std::string_view input)
{
    static constexpr char alphabet[] =
        "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/";
    std::string output;
    output.reserve(((input.size() + 2) / 3) * 4);

    for (size_t i = 0; i < input.size(); i += 3)
    {
        const auto first = static_cast<unsigned char>(input[i]);
        const auto second = i + 1 < input.size() ? static_cast<unsigned char>(input[i + 1]) : 0;
        const auto third = i + 2 < input.size() ? static_cast<unsigned char>(input[i + 2]) : 0;
        const uint32_t packed = (static_cast<uint32_t>(first) << 16) |
                                (static_cast<uint32_t>(second) << 8) |
                                static_cast<uint32_t>(third);
        output.push_back(alphabet[(packed >> 18) & 0x3f]);
        output.push_back(alphabet[(packed >> 12) & 0x3f]);
        output.push_back(i + 1 < input.size() ? alphabet[(packed >> 6) & 0x3f] : '=');
        output.push_back(i + 2 < input.size() ? alphabet[packed & 0x3f] : '=');
    }
    return output;
}

void emitCapture(TraceContext& context, std::string_view source, std::string_view kind)
{
    if (context.capturePrefix.empty())
        return;
    if (context.captureCount >= context.maxCaptures ||
        source.size() > kMaxDynamicChunkBytes ||
        source.size() > context.maxCaptureBytes - std::min(context.maxCaptureBytes, context.capturedBytes))
    {
        std::fprintf(stdout, "[PROTEZ:WARN] Dynamic source capture limit reached; further chunks were not captured\n");
        return;
    }

    ++context.captureCount;
    context.capturedBytes += source.size();
    const uint64_t index = context.captureCount;
    std::fprintf(stdout, "%sB|%llu|%.*s\n", context.capturePrefix.c_str(),
                 static_cast<unsigned long long>(index), static_cast<int>(kind.size()), kind.data());
    const std::string encoded = base64(source);
    constexpr size_t chunkSize = 4096;
    for (size_t offset = 0; offset < encoded.size(); offset += chunkSize)
    {
        const size_t count = std::min(chunkSize, encoded.size() - offset);
        std::fprintf(stdout, "%sC|%llu|%.*s\n", context.capturePrefix.c_str(),
                     static_cast<unsigned long long>(index), static_cast<int>(count),
                     encoded.data() + offset);
    }
    std::fprintf(stdout, "%sE|%llu|%llu\n", context.capturePrefix.c_str(),
                 static_cast<unsigned long long>(index),
                 static_cast<unsigned long long>(source.size()));
}

int dynamicLoadString(lua_State* state, const char* kind)
{
    auto* context = static_cast<TraceContext*>(lua_callbacks(state)->userdata);
    size_t sourceSize = 0;
    const char* source = lua_tolstring(state, 1, &sourceSize);
    if (!source)
    {
        lua_settop(state, 0);
        lua_pushnil(state);
        lua_pushstring(state, "dynamic source must be a string");
        return 2;
    }
    if (sourceSize > kMaxDynamicChunkBytes)
    {
        lua_settop(state, 0);
        lua_pushnil(state);
        lua_pushstring(state, "dynamic source exceeds the 16 MiB limit");
        return 2;
    }
    if (context)
        emitCapture(*context, std::string_view(source, sourceSize), kind);

    char chunkName[64] = {};
    std::snprintf(chunkName, sizeof(chunkName), "=Protez.%s.%llu", kind,
                  static_cast<unsigned long long>(context ? context->captureCount : 0));

    lua_CompileOptions options{};
    options.optimizationLevel = 0;
    options.debugLevel = 2;
    options.typeInfoLevel = 0;
    options.coverageLevel = 0;

    size_t bytecodeSize = 0;
    char* bytecode = nullptr;
    try
    {
        bytecode = luau_compile(source, sourceSize, &options, &bytecodeSize);
    }
    catch (const std::exception& exception)
    {
        lua_settop(state, 0);
        lua_pushnil(state);
        lua_pushstring(state, exception.what());
        return 2;
    }
    catch (...)
    {
        lua_settop(state, 0);
        lua_pushnil(state);
        lua_pushstring(state, "Luau compiler failed while compiling dynamic source");
        return 2;
    }

    if (!bytecode || bytecodeSize == 0)
    {
        std::free(bytecode);
        lua_settop(state, 0);
        lua_pushnil(state);
        lua_pushstring(state, "Luau compiler returned no dynamic bytecode");
        return 2;
    }

    const int loadStatus = luau_load(state, chunkName, bytecode, bytecodeSize, 0);
    std::free(bytecode);
    if (loadStatus != 0)
    {
        const char* message = lua_tostring(state, -1);
        const std::string error = message ? message : "Luau rejected dynamic bytecode";
        lua_settop(state, 0);
        lua_pushnil(state);
        lua_pushlstring(state, error.data(), error.size());
        return 2;
    }
    return 1;
}

int protectedLoadString(lua_State* state)
{
    return dynamicLoadString(state, "loadstring");
}

int protectedLoad(lua_State* state)
{
    return dynamicLoadString(state, "load");
}

std::string jsonQuote(std::string_view input)
{
    std::string output;
    output.reserve(input.size() + 2);
    output.push_back('"');
    for (unsigned char character : input)
    {
        switch (character)
        {
        case '"':
            output += "\\\"";
            break;
        case '\\':
            output += "\\\\";
            break;
        case '\b':
            output += "\\b";
            break;
        case '\f':
            output += "\\f";
            break;
        case '\n':
            output += "\\n";
            break;
        case '\r':
            output += "\\r";
            break;
        case '\t':
            output += "\\t";
            break;
        default:
            if (character < 0x20)
            {
                static constexpr char hex[] = "0123456789abcdef";
                output += "\\u00";
                output.push_back(hex[(character >> 4) & 0x0f]);
                output.push_back(hex[character & 0x0f]);
            }
            else
            {
                output.push_back(static_cast<char>(character));
            }
        }
    }
    output.push_back('"');
    return output;
}

std::string clipped(std::string_view value, size_t limit)
{
    if (value.size() <= limit)
        return std::string(value);
    return std::string(value.substr(0, limit)) + "...";
}

void emitTrace(
    TraceContext& context,
    std::string_view operation,
    std::string_view name,
    std::string_view source,
    int line,
    std::string_view detail)
{
    if (context.prefix.empty() || context.outputFailed)
        return;

    const double elapsed = std::chrono::duration<double>(
                               std::chrono::steady_clock::now() - context.started)
                               .count();
    std::ostringstream record;
    record.imbue(std::locale::classic());
    record << context.prefix << ++context.sequence << '|' << operation << '|'
           << std::fixed << std::setprecision(6) << elapsed << '|' << std::max(0, line) << '|'
           << base64(clipped(name, 128)) << '|' << base64(clipped(source, 256)) << '|'
           << base64(detail) << '\n';
    const std::string bytes = record.str();
    if (std::fwrite(bytes.data(), 1, bytes.size(), stdout) != bytes.size())
    {
        context.outputFailed = true;
        context.traceStopped = true;
        return;
    }
    std::fflush(stdout);
}

std::string valueSummary(const TValue* value)
{
    switch (ttype(value))
    {
    case LUA_TNIL:
        return "nil";
    case LUA_TBOOLEAN:
        return bvalue(value) ? "true" : "false";
    case LUA_TNUMBER:
    {
        const double number = nvalue(value);
        if (!std::isfinite(number))
            return "number(non-finite)";
        std::ostringstream stream;
        stream.imbue(std::locale::classic());
        stream << std::setprecision(12) << number;
        return stream.str();
    }
    case LUA_TINTEGER:
    {
        return std::to_string(lvalue(value));
    }
    case LUA_TSTRING:
    {
        const TString* string = tsvalue(value);
        const size_t length = string->len;
        std::string result(getstr(string), std::min(length, kMaxTraceStringBytes));
        if (length > kMaxTraceStringBytes)
            result += "...";
        return result;
    }
    case LUA_TTABLE:
        return "<table>";
    case LUA_TFUNCTION:
        return clvalue(value)->isC ? "<c-function>" : "<function>";
    case LUA_TUSERDATA:
        return "<userdata>";
    case LUA_TLIGHTUSERDATA:
        return "<lightuserdata>";
    case LUA_TTHREAD:
        return "<thread>";
    case LUA_TBUFFER:
        return "<buffer>";
    case LUA_TVECTOR:
        return "<vector>";
    default:
        return "<value>";
    }
}

std::string snapshotLocals(lua_State* state)
{
    if (!state || !state->ci || !state->ci->p || !state->ci->savedpc ||
        !state->ci->p->code || !state->ci->base)
        return "null";

    const Proto* proto = state->ci->p;
    const std::ptrdiff_t offset = state->ci->savedpc - proto->code;
    if (offset < 0 || offset >= proto->sizecode)
        return "null";

    std::string output = "[";
    bool first = true;
    for (int index = 1; index <= static_cast<int>(kMaxLocalsPerSnapshot); ++index)
    {
        const LocVar* local = luaF_getlocal(proto, index, static_cast<int>(offset));
        if (!local)
            break;

        const TValue* value = state->ci->base + local->reg;
        const int valueType = ttype(value);
        const char* typeName = lua_typename(state, valueType);
        const std::string summary = valueSummary(value);
        if (!first)
            output.push_back(',');
        first = false;
        output += "{\"name\":";
        output += jsonQuote(getstr(local->varname));
        output += ",\"type\":";
        output += jsonQuote(typeName ? typeName : "unknown");
        output += ",\"value\":";
        output += jsonQuote(summary);
        output.push_back('}');
    }
    output.push_back(']');
    return output;
}

void onUserThread(lua_State* parent, lua_State* thread)
{
    if (!parent || !thread)
        return;
    auto* context = static_cast<TraceContext*>(lua_callbacks(parent)->userdata);
    if (context && !context->prefix.empty())
        lua_singlestep(thread, context->traceStopped ? 0 : 1);
}

void debugStep(lua_State* state, lua_Debug* info)
{
    auto* context = static_cast<TraceContext*>(lua_callbacks(state)->userdata);
    if (!context || context->prefix.empty())
        return;
    if (context->traceStopped || context->outputFailed)
    {
        lua_singlestep(state, 0);
        return;
    }
    if (!context->active)
        return;

    if (context->stepCount >= context->maxSteps)
    {
        lua_singlestep(state, 0);
        context->active = false;
        context->traceStopped = true;
        if (!context->limitReported)
        {
            context->limitReported = true;
            emitTrace(
                *context,
                "VM_STEP_LIMIT",
                "",
                "",
                0,
                "{\"max_steps\":" + std::to_string(context->maxSteps) + "}");
        }
        return;
    }

    ++context->stepCount;
    try
    {
        const bool includeLocals = context->stepCount == 1 || context->stepCount % kLocalSnapshotStride == 0;
        const int frameDepth = lua_stackdepth(state);
        // The VM fills only `currentline` and `userdata` of the debug record it
        // hands to the single-step hook; `name`, `source`, `protoid` and
        // `bytecodeid` are uninitialized stack bytes there, so reading them
        // dereferences whatever was left on the stack -- payloads that run deep
        // enough crashed the worker this way.  Ask the VM for a fresh record of
        // the running frame instead: it also gives the trace real function names
        // and sources, which the lifter can use.
        lua_Debug frame{};
        const bool frameInfo = lua_getinfo(state, 0, "nSlp", &frame) != 0;
        const int line = info ? info->currentline : 0;
        const std::string name = frameInfo && frame.name ? frame.name : "";
        const std::string source = frameInfo && frame.source ? frame.source : "";

        int pc = -1;
        int opcodeId = -1;
        uint32_t rawInstruction = 0;
        uint32_t auxiliary = 0;
        std::string opcodeName;
        if (state->ci && state->ci->p && state->ci->savedpc && state->ci->p->code)
        {
            const Proto* proto = state->ci->p;
            const std::ptrdiff_t offset = state->ci->savedpc - proto->code;
            if (offset >= 0 && offset < proto->sizecode)
            {
                pc = static_cast<int>(offset);
                rawInstruction = static_cast<uint32_t>(*state->ci->savedpc);
                opcodeId = static_cast<int>(LUAU_INSN_OP(rawInstruction));
                if (opcodeId >= 0 && opcodeId < LOP__COUNT)
                {
                    const LuauOpcode opcode = static_cast<LuauOpcode>(opcodeId);
                    if (opcode == LOP_NOP)
                    {
                        opcodeName = "NOP";
                    }
                    else if (opcode == LOP_NATIVECALL)
                    {
                        opcodeName = "NATIVECALL";
                    }
                    else
                    {
                        const char* nameFromBytecode = Luau::Bytecode::getLuauOpcodeName(opcode);
                        opcodeName = nameFromBytecode ? nameFromBytecode : "unknown";
                    }
                    if (Luau::getOpLength(opcode) == 2 && offset + 1 < proto->sizecode)
                        auxiliary = static_cast<uint32_t>(state->ci->savedpc[1]);
                }
            }
        }

        std::string detail = "{\"step\":" + std::to_string(context->stepCount) +
                             ",\"frame_depth\":" + std::to_string(std::max(0, frameDepth));
        if (frameInfo)
        {
            detail += ",\"proto_id\":" + std::to_string(frame.protoid);
            detail += ",\"bytecode_id\":" + std::to_string(frame.bytecodeid);
        }
        else
        {
            detail += ",\"proto_id\":null,\"bytecode_id\":null";
        }
        detail += ",\"pc\":" + (pc >= 0 ? std::to_string(pc) : "null");
        detail += ",\"opcode\":" + (opcodeId >= 0 ? jsonQuote(opcodeName) : "null");
        detail += ",\"opcode_id\":" + (opcodeId >= 0 ? std::to_string(opcodeId) : "null");
        detail += ",\"instruction_word\":" + (pc >= 0 ? std::to_string(rawInstruction) : "null");
        if (pc >= 0)
        {
            detail += ",\"a\":" + std::to_string(LUAU_INSN_A(rawInstruction));
            detail += ",\"b\":" + std::to_string(LUAU_INSN_B(rawInstruction));
            detail += ",\"c\":" + std::to_string(LUAU_INSN_C(rawInstruction));
            detail += ",\"d\":" + std::to_string(LUAU_INSN_D(rawInstruction));
            detail += ",\"aux\":";
            detail += opcodeId < LOP__COUNT &&
                              Luau::getOpLength(static_cast<LuauOpcode>(opcodeId)) == 2
                          ? std::to_string(auxiliary)
                          : "null";
        }
        else
        {
            detail += ",\"a\":null,\"b\":null,\"c\":null,\"d\":null,\"aux\":null";
        }
        detail += ",\"registers\":null";
        if (includeLocals)
            detail += ",\"locals\":" + snapshotLocals(state);
        else
            detail += ",\"locals\":null";
        detail.push_back('}');

        emitTrace(*context, "VM_STEP", name, source, line, detail);
        if (context->traceStopped || context->outputFailed)
        {
            context->active = false;
            lua_singlestep(state, 0);
        }
    }
    catch (...)
    {
        context->active = false;
        context->traceStopped = true;
        lua_singlestep(state, 0);
    }
}

void startTrace(lua_State* state, TraceContext& context)
{
    if (context.prefix.empty() || context.hookReady)
        return;

    context.hookReady = true;
    context.active = true;
    context.started = std::chrono::steady_clock::now();
    lua_singlestep(state, 1);
    emitTrace(
        context,
        "HOOK_READY",
        "lua_singlestep",
        "",
        0,
        "{\"mode\":\"instruction-step\",\"pc_available\":true,\"opcode_available\":true,\"registers_available\":false}");
    if (context.traceStopped || context.outputFailed)
    {
        context.active = false;
        lua_singlestep(state, 0);
    }
}

bool readSourceFile(const std::string& path, std::string& source, std::string& error)
{
    std::ifstream input(path, std::ios::binary);
    if (!input)
    {
        error = "cannot open source file: " + path;
        return false;
    }

    input.seekg(0, std::ios::end);
    const std::streamoff size = input.tellg();
    if (size < 0 || static_cast<uint64_t>(size) > kMaxSourceBytes)
    {
        error = "source file is larger than the 64 MiB host limit";
        return false;
    }
    input.seekg(0, std::ios::beg);
    source.resize(static_cast<size_t>(size));
    if (!source.empty() && !input.read(source.data(), static_cast<std::streamsize>(source.size())))
    {
        error = "could not read source file: " + path;
        return false;
    }
    return true;
}

bool readSourceStdin(std::string& source, std::string& error)
{
    source.clear();
    char buffer[64 * 1024];
    while (std::cin)
    {
        std::cin.read(buffer, sizeof(buffer));
        const std::streamsize count = std::cin.gcount();
        if (count > 0)
        {
            if (source.size() + static_cast<size_t>(count) > kMaxSourceBytes)
            {
                error = "source exceeds the 64 MiB host limit";
                return false;
            }
            source.append(buffer, static_cast<size_t>(count));
        }
    }
    if (std::cin.bad())
    {
        error = "could not read source from standard input";
        return false;
    }
    return true;
}

void setGlobalNil(lua_State* state, const char* name)
{
    lua_pushnil(state);
    lua_setglobal(state, name);
}

bool isTraceToken(const std::string& token)
{
    if (token.size() != 32)
        return false;
    return std::all_of(token.begin(), token.end(), [](unsigned char character) {
        return (character >= '0' && character <= '9') ||
               (character >= 'a' && character <= 'f');
    });
}

bool isCaptureToken(const std::string& token)
{
    return isTraceToken(token);
}

bool parsePositiveInteger(const char* text, uint64_t& value)
{
    if (!text || !*text)
        return false;
    char* end = nullptr;
    const unsigned long long parsed = std::strtoull(text, &end, 10);
    if (*end != '\0' || parsed == 0 || parsed > 10000000ULL)
        return false;
    value = static_cast<uint64_t>(parsed);
    return true;
}

void printUsage(const char* executable)
{
    std::fprintf(
        stderr,
        "Usage: %s (--source <file> | --source-stdin) [--compile-only] [--capture-token <32-hex>] [--max-captures <1..100>] [--max-capture-bytes <1..16777216>] [--trace-token <32-hex>] [--max-trace-events <count>]\n",
        executable);
}
} // namespace

int main(int argc, char** argv)
{
#ifdef _WIN32
    if (argc > 1 && std::string(argv[1]) == "--appcontainer")
    {
        _setmode(_fileno(stdin), _O_BINARY);
        _setmode(_fileno(stdout), _O_BINARY);
        return runInAppContainer(argc, argv);
    }
    _setmode(_fileno(stdin), _O_BINARY);
    _setmode(_fileno(stdout), _O_BINARY);
#endif
    std::setlocale(LC_ALL, "C");
    std::setbuf(stdout, nullptr);

    std::string sourcePath;
    std::string traceToken;
    std::string captureToken;
    bool compileOnly = false;
    bool sourceFromStdin = false;
    uint64_t maxTraceEvents = 25000;
    uint64_t maxCaptures = 100;
    uint64_t maxCaptureBytes = 16 * 1024 * 1024;

    for (int index = 1; index < argc; ++index)
    {
        const std::string argument = argv[index];
        if (argument == "--version")
        {
            std::puts("Protez native Luau host 0.3 (Luau 0.740)");
            return 0;
        }
        if ((argument == "--source" || argument == "--trace-token" ||
             argument == "--capture-token" || argument == "--max-trace-events" ||
             argument == "--max-captures" || argument == "--max-capture-bytes") && index + 1 >= argc)
        {
            printUsage(argv[0]);
            return 64;
        }
        if (argument == "--compile-only")
        {
            compileOnly = true;
        }
        else if (argument == "--source")
        {
            sourcePath = argv[++index];
        }
        else if (argument == "--source-stdin")
        {
            sourceFromStdin = true;
        }
        else if (argument == "--capture-token")
        {
            captureToken = argv[++index];
        }
        else if (argument == "--trace-token")
        {
            traceToken = argv[++index];
        }
        else if (argument == "--max-trace-events")
        {
            if (!parsePositiveInteger(argv[++index], maxTraceEvents))
            {
                std::fprintf(stderr, "Invalid --max-trace-events value (expected 1..10000000)\n");
                return 64;
            }
        }
        else if (argument == "--max-captures")
        {
            if (!parsePositiveInteger(argv[++index], maxCaptures) || maxCaptures > 100)
            {
                std::fprintf(stderr, "Invalid --max-captures value (expected 1..100)\n");
                return 64;
            }
        }
        else if (argument == "--max-capture-bytes")
        {
            if (!parsePositiveInteger(argv[++index], maxCaptureBytes) ||
                maxCaptureBytes > 16 * 1024 * 1024)
            {
                std::fprintf(stderr, "Invalid --max-capture-bytes value (expected 1..16777216)\n");
                return 64;
            }
        }
        else
        {
            std::fprintf(stderr, "Unknown option: %s\n", argument.c_str());
            printUsage(argv[0]);
            return 64;
        }
    }

    if (sourceFromStdin == !sourcePath.empty())
    {
        printUsage(argv[0]);
        return 64;
    }
    if (!traceToken.empty() && !isTraceToken(traceToken))
    {
        std::fprintf(stderr, "Invalid trace token\n");
        return 64;
    }
    if (!captureToken.empty() && !isCaptureToken(captureToken))
    {
        std::fprintf(stderr, "Invalid capture token\n");
        return 64;
    }

    std::string source;
    std::string readError;
    const bool sourceRead = sourceFromStdin ? readSourceStdin(source, readError)
                                            : readSourceFile(sourcePath, source, readError);
    if (!sourceRead)
    {
        std::fprintf(stderr, "Protez host error: %s\n", readError.c_str());
        return 66;
    }

    MemoryBudget memoryBudget;
    lua_State* state = lua_newstate(boundedAllocator, &memoryBudget);
    if (!state)
    {
        std::fprintf(stderr, "Protez host error: could not allocate a Luau VM state\n");
        return 71;
    }

    luaL_openlibs(state);
    // Roblox services are intentionally absent: no fabricated API values are supplied.
    // Host filesystem, process and module-loading functions stay unavailable.
    for (const char* name : {"io", "os", "package", "dofile", "loadfile", "require"})
        setGlobalNil(state, name);

    TraceContext trace;
    trace.maxSteps = maxTraceEvents;
    trace.maxCaptures = maxCaptures;
    trace.maxCaptureBytes = maxCaptureBytes;
    if (!captureToken.empty())
        trace.capturePrefix = "__PROTEZ_CAPTURE_" + captureToken + "|";
    lua_callbacks(state)->userdata = &trace;
    lua_newtable(state);
    lua_pushcfunction(state, sandboxClock, "clock");
    lua_setfield(state, -2, "clock");
    lua_setglobal(state, "os");
    lua_pushcfunction(state, protectedLoadString, "loadstring");
    lua_setglobal(state, "loadstring");
    lua_pushcfunction(state, protectedLoad, "load");
    lua_setglobal(state, "load");

    if (!traceToken.empty())
    {
        trace.prefix = "__PROTEZ_TRACE_" + traceToken + "|";
        lua_Callbacks* callbacks = lua_callbacks(state);
        callbacks->debugstep = debugStep;
        callbacks->userthread = onUserThread;
    }

    lua_CompileOptions options{};
    options.optimizationLevel = 0; // Keep VM instruction traces granular.
    options.debugLevel = 2; // Include local and upvalue names for snapshots.
    options.typeInfoLevel = 0;
    options.coverageLevel = 0;

    size_t bytecodeSize = 0;
    char* bytecode = nullptr;
    try
    {
        bytecode = luau_compile(source.data(), source.size(), &options, &bytecodeSize);
    }
    catch (const std::exception& exception)
    {
        std::fprintf(stderr, "Protez host error: Luau compiler failed: %s\n", exception.what());
        lua_close(state);
        return 70;
    }
    catch (...)
    {
        std::fprintf(stderr, "Protez host error: Luau compiler failed\n");
        lua_close(state);
        return 70;
    }

    if (!bytecode || bytecodeSize == 0)
    {
        std::fprintf(stderr, "Protez host error: Luau compiler returned no bytecode\n");
        std::free(bytecode);
        lua_close(state);
        return 70;
    }

    const std::string chunkName = sourceFromStdin ? "=Protez.input" : "@" + std::string(sourcePath);
    const int loadStatus = luau_load(state, chunkName.c_str(), bytecode, bytecodeSize, 0);
    std::free(bytecode);
    if (loadStatus != 0)
    {
        const char* message = lua_tostring(state, -1);
        std::fprintf(stderr, "Luau load failed: %s\n", message ? message : "unknown error");
        lua_close(state);
        return 65;
    }
    if (compileOnly)
    {
        lua_close(state);
        return 0;
    }

    if (!traceToken.empty())
        startTrace(state, trace);

    const int status = lua_pcall(state, 0, 0, 0);
    if (status != LUA_OK)
    {
        const char* message = lua_tostring(state, -1);
        std::fprintf(stderr, "Luau runtime error: %s\n", message ? message : "unknown error");
        lua_close(state);
        return 1;
    }

    lua_close(state);
    return 0;
}
