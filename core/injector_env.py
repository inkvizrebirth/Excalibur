"""Executor/injector environment emulation for isolated analysis.

Scripts that are protected for Roblox executers routinely bootstrap themselves
from the *injector* globals, not from the script body:

    local executor = identifyexecutor()
    local env = getgenv()
    if syn and syn.protect_gui then syn.protect_gui(ui) end
    local body = game:HttpGet("https://example.invalid/payload.lua")

When those names are missing, a static or dynamic run stops at the first
lookup with "attempt to index nil" or "attempt to call a nil value", and the
payload stays locked.  This module describes real executor profiles (Synapse X,
Krnl, Fluxus, Solara, Delta, Wave, Xeno, ...) and synthesises both a static
evaluator environment and a Lua prelude that presents the same globals inside
the isolated Luau worker or the portable Lua backend.

Nothing here grants real powers: file, process and hooking APIs are inert
stubs, and network access only happens when the caller wires up a fetch bridge.
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping

from core.executor_api import EXECUTOR_API_SURFACE

__all__ = [
    "ExecutorProfile",
    "EXECUTOR_PROFILES",
    "DEFAULT_PROFILE_KEY",
    "get_profile",
    "profile_choices",
    "profile_keys",
    "detect_executor_keys",
    "static_call",
    "build_static_environment",
    "build_lua_prelude",
    "build_http_stub_prelude",
    "FETCH_FUNCTION_NAMES",
    "PREFETCH_FUNCTION_NAMES",
]


# ---------------------------------------------------------------------------
# Profiles
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ExecutorProfile:
    """A named injector environment.

    ``markers`` are globals a protected script can test for (``if Krnl then``),
    ``features`` are the capability keys used by feature probes
    (``if syn.protect_gui then``), and ``aliases`` are extra global names that
    resolve to the same executor table.
    """

    key: str
    label: str
    executor_name: str
    version: str = "1.0.0"
    markers: tuple[str, ...] = ()
    aliases: tuple[str, ...] = ()
    features: tuple[str, ...] = ()
    universal: bool = False
    notes: str = ""


_BASE_FEATURES = (
    "getgenv",
    "getrenv",
    "getgc",
    "getreg",
    "identifyexecutor",
    "loadstring",
    "request",
    "http_get",
    "base64",
    "cloneref",
    "checkcaller",
    "getrawmetatable",
    "setreadonly",
    "islclosure",
    "is_sirhurt_closure",
    "getscriptbytecode",
    "getscripthash",
    "getinstances",
    "getnilinstances",
    "getloadedmodules",
    "getcallingscript",
    "fireclickdetector",
    "firetouchinterest",
    "fireproximityprompt",
    "getthreadidentity",
    "setthreadidentity",
    "queue_on_teleport",
    "setclipboard",
    "writefile",
    "readfile",
    "appendfile",
    "listfiles",
    "isfile",
    "delfile",
    "makefolder",
    "delfolder",
    "getcustomasset",
    "cache_replace",
    "decompile",
)

_FILE_FEATURES = (
    "writefile",
    "readfile",
    "appendfile",
    "listfiles",
    "isfile",
    "delfile",
    "makefolder",
    "delfolder",
    "getcustomasset",
)

_HOOK_FEATURES = (
    "hookfunction",
    "hookmetamethod",
    "getconnections",
    "getupvalues",
    "getupvalue",
    "setupvalue",
    "getconstants",
    "getprotos",
    "getinfo",
    "newcclosure",
    "iscclosure",
    "replaceclosure",
    "getscripts",
)


_REAL_FEATURES = (
    # Files, clipboard, assets
    "writefile", "appendfile", "readfile", "isfile", "isfolder", "makefolder",
    "delfile", "delfolder", "listfiles", "loadfile", "dofile", "getcustomasset",
    "getcustomassetasync", "setclipboard", "getclipboard", "setrbxclipboard",
    # HTTP
    "request", "http_request", "http_get", "http_post", "httpget", "httpgetasync",
    "fetch", "requestasync", "websocket",
    # Identity, HWID, timing
    "identifyexecutor", "getexecutorname", "getexecutor", "getexploit", "getversion",
    "getexecutorversion", "gethwid", "getusername", "getuserid", "getgenv", "getrenv",
    "getidentity", "getthreadidentity", "setthreadidentity", "getthreadcontext",
    "setthreadcontext", "printidentity", "getfpscap", "setfpscap", "getping",
    "getserverping", "tick", "time", "elapsedTime", "getmemoryusage", "getspecialinfo",
    # Hooks, closures, metatables, introspection
    "hookfunction", "hookmetamethod", "restorefunction", "replaceclosure",
    "newcclosure", "newlclosure", "clonefunction", "checkcaller", "iscclosure",
    "islclosure", "isexecutorclosure", "isourclosure", "getrawmetatable",
    "setrawmetatable", "setreadonly", "isreadonly", "make_writeable",
    "getupvalue", "getupvalues", "setupvalue", "getconstants", "getconstant",
    "setconstant", "getproto", "getprotos", "getstack", "getnamecallmethod",
    "setnamecallmethod", "getfunctionhash", "getscripts", "getrunningscripts",
    "getloadedmodules", "getinstances", "getnilinstances", "getgc", "getreg",
    "getobjects", "getsenv", "getmenv", "getcallingscript", "getscriptclosure",
    "getscriptfunction", "getscriptbytecode", "getscripthash", "decompile",
    "dumpstring", "getconnections", "firesignal", "getheap",
    # Instances, GUI, rendering, input, signals
    "fireclickdetector", "firetouchinterest", "fireproximityprompt", "replicatesignal",
    "sethiddenproperty", "gethiddenproperty", "isscriptable", "setscriptable",
    "setsimulationradius", "isnetworkowner", "getcallbackvalue", "setrenderproperty",
    "getrenderproperty", "isrenderobj", "protect_gui", "unprotect_gui",
    "is_protected_gui", "gethui", "getgui", "cloneref", "compareinstances", "isvalid",
    "queue_on_teleport", "queueonteleport", "clearteleportqueue", "saveinstance",
    "keypress", "keyrelease", "iskeydown", "mouse1click", "mouse1press",
    "mouse1release", "mouse2click", "mousemoverel", "mousemoveabs", "getmouse",
    # Libraries
    "crypt", "base64", "hash", "sha256", "lz4", "bit32", "utf8", "task",
)


def _features(*extra: str) -> tuple[str, ...]:
    return tuple(dict.fromkeys((*_BASE_FEATURES, *extra)))


EXECUTOR_PROFILES: tuple[ExecutorProfile, ...] = (
    ExecutorProfile(
        key="real",
        label="Real - full executor API (recommended)",
        executor_name="Real",
        version="1.0.0",
        markers=(
            "real",
            "Real",
            "syn",
            "krnl",
            "KRNL_LOADED",
            "fluxus",
            "FLUXUS_LOADED",
            "xeno",
            "delta",
            "Delta",
            "wave",
            "hydrogen",
            "solara",
            "is_solara",
            "swift",
            "codex",
            "WeAreDevs",
        ),
        aliases=("Protez",),
        features=tuple(dict.fromkeys(_REAL_FEATURES)),
        universal=True,
        notes=(
            "The Real injector: identifyexecutor() reports 'Real' and the whole "
            "executor API answers (workspace files, request tables, hooks, crypt, "
            "HWID, input, GUI signals).  Compatibility namespaces (syn.*, krnl.*, "
            "fluxus.*, ...) are installed too, so executor-specific branches in a "
            "protected wrapper still run."
        ),
    ),
    ExecutorProfile(
        key="universal",
        label="Auto - all executors (recommended)",
        executor_name="Synapse X",
        version="3.0.0",
        markers=(
            "syn",
            "KRNL_LOADED",
            "krnl",
            "fluxus",
            "FLUXUS_LOADED",
            "is_solara",
            "solara",
            "Delta",
            "is_delta",
            "delta",
            "wave",
            "is_wave",
            "xeno",
            "is_xeno",
            "hydrogen",
            "is_hydrogen",
            "swift",
            "is_swift",
            "nihon",
            "macsploit",
            "SW",
            "SW_M",
            "sirhurt",
            "protosmasher",
            "WeAreDevs",
            "sentinel",
            "AWP",
            "zorara",
            "evon",
            "codex",
            "Arceus",
            "Electron",
            "trigon",
            "OxygenU",
            "JJSploit",
        ),
        features=_features(*_FILE_FEATURES, *_HOOK_FEATURES, "protect_gui", "unprotect_gui"),
        universal=True,
        notes=(
            "Every known executor marker is exposed at once. Feature probes "
            "succeed and identifyexecutor() reports a common name, which keeps "
            "executor-specific branches reachable instead of erroring."
        ),
    ),
    ExecutorProfile(
        key="synapse",
        label="Synapse X",
        executor_name="Synapse X",
        version="3.0.0",
        markers=("syn",),
        aliases=("Synapse", "synapse"),
        features=_features(
            *_HOOK_FEATURES,
            *_FILE_FEATURES,
            "protect_gui",
            "unprotect_gui",
            "getspecialinfo",
        ),
        notes="syn.protect_gui / syn.request / syn.queue_on_teleport style probes.",
    ),
    ExecutorProfile(
        key="krnl",
        label="Krnl",
        executor_name="Krnl",
        markers=("KRNL_LOADED", "krnl"),
        aliases=("KRNL",),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="fluxus",
        label="Fluxus",
        executor_name="Fluxus",
        version="2.0.0",
        markers=("fluxus", "FLUXUS_LOADED", "Fluxus"),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="solara",
        label="Solara",
        executor_name="Solara",
        version="3.0.0",
        markers=("solara", "is_solara", "Solara"),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="delta",
        label="Delta",
        executor_name="Delta",
        markers=("Delta", "delta", "is_delta", "DELTA_LOADED"),
        aliases=("DeltaExecutor",),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="wave",
        label="Wave",
        executor_name="Wave",
        markers=("wave", "Wave", "is_wave"),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="xeno",
        label="Xeno",
        executor_name="Xeno",
        markers=("xeno", "Xeno", "is_xeno"),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="hydrogen",
        label="Hydrogen",
        executor_name="Hydrogen",
        markers=("hydrogen", "Hydrogen", "is_hydrogen"),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="swift",
        label="Swift",
        executor_name="Swift",
        markers=("swift", "Swift", "is_swift"),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="scriptware",
        label="Script-Ware",
        executor_name="Script-Ware",
        markers=("SW", "SW_M", "sw"),
        aliases=("scriptware",),
        features=_features(*_FILE_FEATURES, "protect_gui"),
    ),
    ExecutorProfile(
        key="sirhurt",
        label="SirHurt",
        executor_name="SirHurt V4",
        version="4.0.0",
        markers=("sirhurt", "SirHurt", "is_sirhurt_closure"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="wearedevs",
        label="WeAreDevs API",
        executor_name="WeAreDevs API",
        version="2.4.0",
        markers=("WeAreDevs", "servercontrol"),
        features=_features(*_FILE_FEATURES),
        notes="The WeAreDevs v2.4 API exposes identifyexecutor() and a compact global set.",
    ),
    ExecutorProfile(
        key="nihon",
        label="Nihon",
        executor_name="Nihon",
        markers=("nihon", "Nihon"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="macsploit",
        label="Macsploit",
        executor_name="Macsploit",
        markers=("macsploit", "Macsploit"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="protosmasher",
        label="ProtoSmasher",
        executor_name="ProtoSmasher",
        markers=("protosmasher", "PS_LOADED", "proto"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="sentinel",
        label="Sentinel",
        executor_name="Sentinel",
        markers=("sentinel", "Sentinel"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="awp",
        label="AWP.GG",
        executor_name="AWP",
        markers=("AWP", "AWPGG"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="zorara",
        label="Zorara",
        executor_name="Zorara",
        markers=("zorara", "Zorara"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="evon",
        label="Evon",
        executor_name="Evon",
        markers=("evon", "Evon"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="codex",
        label="Codex",
        executor_name="Codex",
        markers=("codex", "Codex"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="arceus",
        label="Arceus X",
        executor_name="Arceus X",
        markers=("Arceus", "arceus"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="electron",
        label="Electron",
        executor_name="Electron",
        markers=("Electron", "electron"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="trigon",
        label="Trigon Evo",
        executor_name="Trigon Evo",
        markers=("trigon", "Trigon"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="oxygen",
        label="Oxygen U",
        executor_name="Oxygen U",
        markers=("OxygenU", "Oxygen"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="jjsploit",
        label="JJSploit",
        executor_name="JJSploit",
        markers=("JJSploit", "jjsploit"),
        features=_features(*_FILE_FEATURES),
    ),
    ExecutorProfile(
        key="plain",
        label="No injector (raw Lua environment)",
        executor_name="Protez",
        markers=(),
        features=("loadstring", "http_get"),
        notes="Only the plain Lua/Luau standard library; useful for unprotected scripts.",
    ),
)

DEFAULT_PROFILE_KEY = "real"

_PROFILE_BY_KEY = {profile.key: profile for profile in EXECUTOR_PROFILES}


def get_profile(key: str | None) -> ExecutorProfile:
    """Return a profile by key, falling back to the default profile."""
    if not key:
        return _PROFILE_BY_KEY[DEFAULT_PROFILE_KEY]
    return _PROFILE_BY_KEY.get(str(key).strip().lower(), _PROFILE_BY_KEY[DEFAULT_PROFILE_KEY])


def profile_keys() -> tuple[str, ...]:
    return tuple(profile.key for profile in EXECUTOR_PROFILES)


def profile_choices() -> tuple[tuple[str, str], ...]:
    """(key, label) pairs ready for a dropdown."""
    return tuple((profile.key, profile.label) for profile in EXECUTOR_PROFILES)


# ---------------------------------------------------------------------------
# Detection
# ---------------------------------------------------------------------------


def _iter_identifiers(source: str) -> Iterable[str]:
    import re

    for match in re.finditer(r"[A-Za-z_][A-Za-z0-9_]*", source):
        yield match.group(0)


def detect_executor_keys(source: str) -> tuple[str, ...]:
    """Report executor profiles referenced by name in ``source``.

    A cheap lexical probe used for logging and auto-selection; it never
    executes anything.
    """
    if not isinstance(source, str):
        raise TypeError("source must be text")
    if not source:
        return ()
    identifiers = set(_iter_identifiers(source))
    lowered = {name.lower() for name in identifiers}
    found: list[str] = []
    for profile in EXECUTOR_PROFILES:
        if profile.key in {"universal", "plain"}:
            continue
        markers = {*profile.markers, *profile.aliases}
        if any(marker in identifiers for marker in markers) or any(
            marker.lower() in lowered for marker in markers
        ):
            found.append(profile.key)
    return tuple(found)


# ---------------------------------------------------------------------------
# Static evaluator environment
# ---------------------------------------------------------------------------


def static_call(
    name: str,
    arguments: list[Any],
    *,
    profile: ExecutorProfile | None = None,
) -> tuple[bool, Any]:
    """Resolve an injector-related call for the static constant folder.

    Returns ``(handled, value)``; ``handled`` is False when the name is not an
    injector function, in which case the caller keeps the original expression.
    """
    active = profile or get_profile(None)

    if name in {"identifyexecutor", "getexecutorname", "getexecutor", "get_exploit", "getexploit"}:
        return True, active.executor_name.encode("utf-8")
    if name in {"getexecutorversion", "getversion"}:
        return True, active.version.encode("utf-8")
    if name in {"is_sirhurt_closure", "issirhurt"}:
        return True, active.key == "sirhurt"
    if name in {"iskrnl", "is_krnl"}:
        return True, active.key in {"krnl", "universal"}
    if name in {"checkcaller", "iscclosure"}:
        return True, True
    if name in {"islclosure", "isfile", "isfolder"}:
        return True, False
    if name in {"getthreadidentity", "getidentity", "getthreadcontext"}:
        return True, 8
    if name in {"getgenv", "getrenv"}:
        return True, None
    if name in {"getscriptbytecode", "getscripthash"}:
        return True, b""
    if name in {"base64_encode", "base64encode"}:
        if len(arguments) == 1 and isinstance(arguments[0], bytes):
            import base64

            return True, base64.b64encode(arguments[0])
        return True, None
    if name in {"base64_decode", "base64decode"}:
        if len(arguments) == 1 and isinstance(arguments[0], bytes):
            import base64

            try:
                return True, base64.b64decode(arguments[0], validate=False)
            except Exception:  # noqa: BLE001
                return True, None
        return True, None
    if name in {"typeof"} and len(arguments) == 1:
        value = arguments[0]
        if value is None:
            return True, b"nil"
        if isinstance(value, bool):
            return True, b"boolean"
        if isinstance(value, (int, float)):
            return True, b"number"
        if isinstance(value, bytes):
            return True, b"string"
        return True, b"table"
    if name in {"getfpscap", "get_fps_cap"}:
        return True, 60
    if name in {"gethwid", "get_hwid", "gethwid"}:
        # Stable so two calls in the same script agree with each other.
        return True, b"PROTEZ-00000000-00000000-00000000"
    if name == "tick":
        return True, 0.0
    if name in {"time", "os.time", "os.clock"}:
        return True, 0.0
    if name in {"warn", "print", "debug.getinfo"}:
        return True, None
    return False, None


def build_static_environment(
    profile: ExecutorProfile | None = None,
    *,
    script_key: str | None = None,
) -> dict[str, Any]:
    """Values the static token evaluator can fold safely."""
    active = profile or get_profile(None)
    environment: dict[str, Any] = {
        "identifyexecutor": lambda *_: active.executor_name.encode("utf-8"),
        "getexecutorname": lambda *_: active.executor_name.encode("utf-8"),
        "getexecutor": lambda *_: active.executor_name.encode("utf-8"),
        "getversion": lambda *_: active.version.encode("utf-8"),
        "getexecutorversion": lambda *_: active.version.encode("utf-8"),
        "get_exploit": lambda *_: active.executor_name.encode("utf-8"),
        "getexploit": lambda *_: active.executor_name.encode("utf-8"),
        "getgenv": lambda *_: None,
        "getrenv": lambda *_: None,
        "gettenv": lambda *_: None,
        "checkcaller": lambda *_: True,
        "iscclosure": lambda *_: False,
        "islclosure": lambda *_: True,
        "is_sirhurt_closure": lambda *_: active.key == "sirhurt",
        "is_pro_sirhurt": lambda *_: active.key == "sirhurt",
        "iskrnl": lambda *_: active.key in {"krnl", "universal"},
        "getthreadidentity": lambda *_: 8,
        "getthreadcontext": lambda *_: 8,
        "getidentity": lambda *_: 8,
        "getfpscap": lambda *_: 60,
        "isfile": lambda *_: False,
        "isfolder": lambda *_: False,
        "getscriptbytecode": lambda *_: b"",
        "getscripthash": lambda *_: b"",
        "tick": lambda *_: 0.0,
        "time": lambda *_: 0.0,
    }
    if script_key:
        environment["script_key"] = script_key
    return environment


# ---------------------------------------------------------------------------
# Lua prelude
# ---------------------------------------------------------------------------

FETCH_FUNCTION_NAMES = (
    "HttpGet",
    "HttpGetAsync",
    "httpget",
    "http_get",
    "httpgetasync",
    "request",
    "http_request",
)

PREFETCH_FUNCTION_NAMES = ("game.HttpGet", "game:HttpGet", "HttpGet")


def _lua_string(value: str) -> str:
    escaped = (
        str(value)
        .replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\n", "\\n")
    )
    return f'"{escaped}"'


def _feature_flags(profile: ExecutorProfile) -> str:
    features = sorted({*profile.features})
    if profile.key == "plain":
        features = ["loadstring", "http_get"]
    return ", ".join(f"[{_lua_string(name)}] = true" for name in features)


def build_lua_prelude(
    profile: ExecutorProfile | None = None,
    *,
    roblox: bool = True,
    script_key: str | None = None,
    fetch_hook: str = "__protez_http",
    extra_globals: Mapping[str, str] | None = None,
    marker: str = "protez-env",
) -> str:
    """Return a Lua prelude that installs an injector/Roblox environment.

    Conservative Lua 5.1 syntax keeps the same prelude usable in the bundled
    Luau worker and in the optional portable backend.  No real file, process,
    hooking or network power is granted: the HTTP helpers call ``fetch_hook``,
    which the caller decides how to wire.
    """
    active = profile or get_profile(None)
    body = _PRELUDE_HEADER.replace("@@MARKER@@", marker)
    body = body.replace("@@PROFILE_KEY@@", _lua_string(active.key))
    body = body.replace("@@PROFILE_NAME@@", _lua_string(active.label))
    body = body.replace("@@EXECUTOR_NAME@@", _lua_string(active.executor_name))
    body = body.replace("@@EXECUTOR_VERSION@@", _lua_string(active.version))
    body = body.replace("@@IS_UNIVERSAL@@", "true" if active.universal else "false")
    body = body.replace("@@FEATURES@@", _feature_flags(active))
    body = body.replace("@@FETCH_HOOK@@", _lua_string(fetch_hook))
    if active.key == "plain":
        body = body.replace("@@EXECUTOR_SURFACE@@", _PLAIN_SURFACE)
        body = body.replace("@@EXECUTOR_API_SURFACE@@", "-- Plain environment: no executor API.")
    else:
        body = body.replace("@@EXECUTOR_SURFACE@@", _EXECUTOR_SURFACE)
        body = body.replace("@@EXECUTOR_API_SURFACE@@", EXECUTOR_API_SURFACE)
    if roblox:
        body = body.replace("@@ROBLOX_SURFACE@@", _ROBLOX_SURFACE)
    else:
        body = body.replace("@@ROBLOX_SURFACE@@", "-- Roblox surface disabled for this run.")

    if active.universal:
        markers = sorted(
            {
                marker
                for profile in EXECUTOR_PROFILES
                for marker in (*profile.markers, *profile.aliases)
            }
        )
    else:
        markers = sorted({*active.markers, *active.aliases})
    body = body.replace("@@MARKERS@@", "\n".join(f"  {_lua_string(name)}," for name in markers))
    trailing: list[str] = []
    if script_key:
        trailing.extend(
            [
                f"script_key = {_lua_string(script_key)}",
                "if type(getgenv) == 'function' and script_key then",
                "  local __protez_env = getgenv()",
                "  if type(__protez_env) == 'table' and __protez_env.script_key == nil then",
                "    __protez_env.script_key = script_key",
                "  end",
                "end",
            ]
        )
    for name, value in (extra_globals or {}).items():
        trailing.append(
            f"if rawget(_G, {_lua_string(name)}) == nil then rawset(_G, {_lua_string(name)}, {value}) end"
        )
    if trailing:
        body = body + "\n".join(trailing) + "\n"
    return body


_PRELUDE_HEADER = r"""--[[ @@MARKER@@: injector + Roblox environment shim. Inert stubs only. ]]
local __protez_profile = {
  key = @@PROFILE_KEY@@,
  name = @@PROFILE_NAME@@,
  executor = @@EXECUTOR_NAME@@,
  version = @@EXECUTOR_VERSION@@,
  universal = @@IS_UNIVERSAL@@,
  features = {@@FEATURES@@},
}
local function __protez_has(feature)
  return __protez_profile.features[feature] == true
end
local function __protez_noop() return nil end
local function __protez_empty() return '' end
local function __protez_false() return false end
local function __protez_true() return true end
local function __protez_zero() return 0 end
local function __protez_table() return {} end

-- Base64 without host support: several obfuscators call these.
local __protez_b64_alphabet = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/'
local function __protez_b64_encode(value)
  if type(value) ~= 'string' then value = tostring(value) end
  local output = {}
  for index = 1, #value, 3 do
    local first, second, third = value:byte(index, index + 2)
    local group = first * 65536 + (second or 0) * 256 + (third or 0)
    local a = math.floor(group / 262144) % 64
    local b = math.floor(group / 4096) % 64
    local c = math.floor(group / 64) % 64
    local d = group % 64
    output[#output + 1] = __protez_b64_alphabet:sub(a + 1, a + 1)
    output[#output + 1] = __protez_b64_alphabet:sub(b + 1, b + 1)
    output[#output + 1] = second and __protez_b64_alphabet:sub(c + 1, c + 1) or '='
    output[#output + 1] = third and __protez_b64_alphabet:sub(d + 1, d + 1) or '='
  end
  return table.concat(output)
end
local function __protez_b64_decode(value)
  if type(value) ~= 'string' then return '' end
  value = value:gsub('%s', '')
  local output = {}
  local index = 1
  while index <= #value do
    local chunk = value:sub(index, index + 3)
    local a = __protez_b64_alphabet:find(chunk:sub(1, 1), 1, true) or 1
    local b = __protez_b64_alphabet:find(chunk:sub(2, 2), 1, true) or 1
    local c = __protez_b64_alphabet:find(chunk:sub(3, 3), 1, true) or 1
    local d = __protez_b64_alphabet:find(chunk:sub(4, 4), 1, true) or 1
    local group = (a - 1) * 262144 + (b - 1) * 4096 + (c - 1) * 64 + (d - 1)
    output[#output + 1] = string.char(math.floor(group / 65536) % 256)
    if #chunk > 2 and chunk:sub(3, 3) ~= '=' then
      output[#output + 1] = string.char(math.floor(group / 256) % 256)
    end
    if #chunk > 3 and chunk:sub(4, 4) ~= '=' then
      output[#output + 1] = string.char(group % 256)
    end
    index = index + 4
  end
  return table.concat(output)
end

-- Luau/Roblox compatibility: bit32, utf8 and the Luau additions to the
-- standard library that loader stubs routinely call.
if rawget(_G, 'bit32') == nil then
  local function __protez_u32(value)
    value = math.floor(tonumber(value) or 0) % 4294967296
    if value < 0 then value = value + 4294967296 end
    return value
  end
  local function __protez_s32(value)
    value = __protez_u32(value)
    if value >= 2147483648 then value = value - 4294967296 end
    return value
  end
  local function __protez_bitop(left, right, mode)
    local a, b = __protez_u32(left), __protez_u32(right)
    local out, place = 0, 1
    for _ = 1, 32 do
      local abit = a % 2
      local bbit = b % 2
      local keep
      if mode == 'and' then keep = (abit == 1 and bbit == 1)
      elseif mode == 'or' then keep = (abit == 1 or bbit == 1)
      else keep = (abit ~= bbit) end
      if keep then out = out + place end
      place = place * 2
      a = (a - abit) / 2
      b = (b - bbit) / 2
    end
    return out
  end
  local function __protez_fold(mode, ...)
    local count = select('#', ...)
    local result = __protez_u32((select(1, ...)) or 0)
    for index = 2, count do
      result = __protez_bitop(result, select(index, ...), mode)
    end
    return result
  end
  -- Roblox/Luau `bit32` works on unsigned 32-bit values: bit32.bnot(0) is
  -- 4294967295 and bit32.band(-1, -1) is 4294967295, not -1.  Returning signed
  -- values here made obfuscator decoders compute negative indices, so their
  -- payload tables came back nil and the VM died with "arithmetic on a nil
  -- value".  The legacy `bit` library keeps the same results reinterpreted as
  -- signed 32-bit numbers, which is what old clients returned.
  local bit32_table = {}
  bit32_table.band = function(...) return __protez_fold('and', ...) end
  bit32_table.bor = function(...) return __protez_fold('or', ...) end
  bit32_table.bxor = function(...) return __protez_fold('xor', ...) end
  bit32_table.bnot = function(value) return 4294967295 - __protez_u32(value) end
  bit32_table.btest = function(...) return __protez_fold('and', ...) ~= 0 end
  bit32_table.lshift = function(value, displacement)
    displacement = math.floor(tonumber(displacement) or 0)
    if displacement < 0 then return bit32_table.rshift(value, -displacement) end
    if displacement >= 32 then return 0 end
    return (__protez_u32(value) * 2 ^ displacement) % 4294967296
  end
  bit32_table.rshift = function(value, displacement)
    displacement = math.floor(tonumber(displacement) or 0)
    if displacement < 0 then return bit32_table.lshift(value, -displacement) end
    if displacement >= 32 then return 0 end
    return math.floor(__protez_u32(value) / 2 ^ displacement)
  end
  bit32_table.arshift = function(value, displacement)
    displacement = math.floor(tonumber(displacement) or 0)
    if displacement < 0 then return bit32_table.lshift(value, -displacement) end
    if displacement >= 32 then
      if __protez_u32(value) >= 2147483648 then return 4294967295 end
      return 0
    end
    local shifted = math.floor(__protez_s32(value) / 2 ^ displacement)
    if shifted < 0 then return 4294967296 + shifted end
    return shifted
  end
  local function __protez_rotate(value, displacement, leftward)
    displacement = math.floor(tonumber(displacement) or 0) % 32
    if displacement < 0 then displacement = displacement + 32 end
    if displacement == 0 then return __protez_u32(value) end
    local unsigned = __protez_u32(value)
    if leftward then
      return (unsigned * 2 ^ displacement) % 4294967296
        + math.floor(unsigned / 2 ^ (32 - displacement))
    end
    return math.floor(unsigned / 2 ^ displacement)
      + (unsigned * 2 ^ (32 - displacement)) % 4294967296
  end
  bit32_table.lrotate = function(value, displacement)
    return __protez_rotate(value, displacement, true)
  end
  bit32_table.rrotate = function(value, displacement)
    return __protez_rotate(value, displacement, false)
  end
  bit32_table.rotate = function(value, displacement)
    if (tonumber(displacement) or 0) < 0 then
      return __protez_rotate(value, -displacement, false)
    end
    return __protez_rotate(value, displacement, true)
  end
  bit32_table.extract = function(value, field, width)
    width = math.floor(tonumber(width) or 1)
    field = math.floor(tonumber(field) or 0)
    return math.floor(__protez_u32(value) / 2 ^ field) % (2 ^ width)
  end
  -- Lua/Luau signature is replace(n, v, field, width): the replacement comes
  -- second, not last.
  bit32_table.replace = function(value, replacement, field, width)
    width = math.floor(tonumber(width) or 1)
    field = math.floor(tonumber(field) or 0)
    local unsigned = __protez_u32(value)
    -- Clear the whole field first: keeping the field's high part in the base
    -- and adding the replacement on top of it produced 68095 instead of 64255.
    local low = unsigned % 2 ^ field
    local high = unsigned - (unsigned % 2 ^ (field + width))
    local inserted = (__protez_u32(replacement) % 2 ^ width) * 2 ^ field
    return (high + inserted + low) % 4294967296
  end
  bit32_table.countlz = function(value)
    local unsigned = __protez_u32(value)
    for index = 0, 31 do
      if math.floor(unsigned / 2 ^ (31 - index)) % 2 == 1 then return index end
    end
    return 32
  end
  bit32_table.countrz = function(value)
    local unsigned = __protez_u32(value)
    for index = 0, 31 do
      if math.floor(unsigned / 2 ^ index) % 2 == 1 then return index end
    end
    return 32
  end
  rawset(_G, 'bit32', bit32_table)
  local bit_table = {}
  for name, fn in pairs(bit32_table) do
    if name == 'btest' then
      bit_table[name] = fn
    else
      bit_table[name] = function(...) return __protez_s32(fn(...)) end
    end
  end
  rawset(_G, 'bit', bit_table)
end
if rawget(_G, 'utf8') == nil then
  rawset(_G, 'utf8', {
    char = function(...)
      local output = {}
      for index = 1, select('#', ...) do
        local code = select(index, ...)
        if code < 128 then
          output[#output + 1] = string.char(code)
        elseif code < 2048 then
          output[#output + 1] = string.char(192 + math.floor(code / 64), 128 + code % 64)
        else
          output[#output + 1] = string.char(224 + math.floor(code / 4096), 128 + math.floor(code / 64) % 64, 128 + code % 64)
        end
      end
      return table.concat(output)
    end,
    len = function(value) return #value end,
    codepoint = function(value, index) return value:byte(index or 1) end,
    offset = function(value, count) return (count or 1) + 1 end,
  })
end
-- Luau's `buffer` library.  Obfuscators build their payloads inside buffers
-- (Luraph v15 writes a whole bytecode chunk with buffer.writeu8), so a backend
-- without it stops at the very first write; the v15 fixture died on
-- "attempt to index global 'buffer'".  The values are Lua tables; reads and
-- writes go through string.pack/unpack, which the portable backend provides.
if rawget(_G, 'buffer') == nil and string.pack ~= nil and string.unpack ~= nil then
  local pack, unpack = string.pack, string.unpack
  local character, repeat_string = string.char, string.rep
  local format_sizes = {
    ['i8'] = 'b', ['u8'] = 'B', ['i16'] = 'h', ['u16'] = 'H',
    ['i32'] = 'i4', ['u32'] = 'I4', ['f32'] = 'f', ['f64'] = 'd',
  }
  local format_bytes = { b = 1, B = 1, h = 2, H = 2, i4 = 4, I4 = 4, f = 4, d = 8 }

  local function is_buffer(value)
    return type(value) == 'table' and type(value.size) == 'number' and type(value.data) == 'string'
  end
  local function check(value, offset, count)
    if not is_buffer(value) then error('buffer expected', 3) end
    if type(offset) ~= 'number' or type(count) ~= 'number' then error('number expected', 3) end
    if offset < 0 or count < 0 or offset + count > value.size then
      error('buffer access out of bounds', 3)
    end
  end
  local function new(size)
    return { data = repeat_string('\0', size), size = size }
  end

  local buffer_table = {}
  buffer_table.create = function(size)
    size = math.floor(tonumber(size) or 0)
    if size < 0 then error('invalid buffer size', 2) end
    return new(size)
  end
  buffer_table.fromstring = function(value)
    if type(value) ~= 'string' then error('string expected', 2) end
    return { data = value, size = #value }
  end
  buffer_table.tostring = function(value)
    check(value, 0, 0)
    return value.data
  end
  buffer_table.len = function(value)
    check(value, 0, 0)
    return value.size
  end
  local function splice(value, offset, payload)
    value.data = string.sub(value.data, 1, offset)
      .. payload
      .. string.sub(value.data, offset + #payload + 1)
  end
  buffer_table.copy = function(target, target_offset, source, source_offset, count)
    target_offset = target_offset or 0
    source_offset = source_offset or 0
    count = count or (source.size - source_offset)
    check(target, target_offset, count)
    check(source, source_offset, count)
    splice(target, target_offset, string.sub(source.data, source_offset + 1, source_offset + count))
  end
  buffer_table.fill = function(value, offset, byte, count)
    check(value, offset, count or (value.size - offset))
    if type(byte) ~= 'number' then error('number expected', 2) end
    splice(value, offset, repeat_string(character(byte % 256), count or (value.size - offset)))
  end
  for name, format in pairs(format_sizes) do
    local width = format_bytes[format]
    buffer_table['read' .. name] = function(value, offset)
      check(value, offset, width)
      return (unpack('<' .. format, value.data, offset + 1))
    end
    buffer_table['write' .. name] = function(value, offset, number)
      check(value, offset, width)
      splice(value, offset, pack('<' .. format, number))
    end
  end
  buffer_table.readstring = function(value, offset, count)
    check(value, offset, count)
    return string.sub(value.data, offset + 1, offset + count)
  end
  buffer_table.writestring = function(value, offset, text, count)
    if type(text) ~= 'string' then error('string expected', 2) end
    count = count or #text
    check(value, offset, count)
    if #text < count then text = text .. repeat_string('\0', count - #text) end
    splice(value, offset, string.sub(text, 1, count))
  end
  rawset(_G, 'buffer', buffer_table)
end
if type(table.create) ~= 'function' then
  rawset(table, 'create', function(count, value)
    local result = {}
    for index = 1, count do result[index] = value end
    return result
  end)
end
if type(table.find) ~= 'function' then
  rawset(table, 'find', function(haystack, needle, start)
    for index = start or 1, #haystack do
      if haystack[index] == needle then return index end
    end
    return nil
  end)
end
if type(table.clear) ~= 'function' then
  rawset(table, 'clear', function(target)
    for key in pairs(target) do target[key] = nil end
    return target
  end)
end
if type(table.pack) ~= 'function' then
  rawset(table, 'pack', function(...) return { n = select('#', ...), ... } end)
end
if type(table.unpack) ~= 'function' and type(unpack) == 'function' then
  rawset(table, 'unpack', unpack)
end
if type(string.split) ~= 'function' then
  rawset(string, 'split', function(value, separator)
    if separator == nil or separator == '' then return { value } end
    local parts = {}
    local start = 1
    while true do
      local position = string.find(value, separator, start, true)
      if position == nil then
        parts[#parts + 1] = string.sub(value, start)
        break
      end
      parts[#parts + 1] = string.sub(value, start, position - 1)
      start = position + #separator
    end
    return parts
  end)
end
if type(math.round) ~= 'function' then
  rawset(math, 'round', function(value) return math.floor(value + 0.5) end)
end
if type(math.clamp) ~= 'function' then
  rawset(math, 'clamp', function(value, low, high)
    if value < low then return low end
    if value > high then return high end
    return value
  end)
end
if type(math.sign) ~= 'function' then
  rawset(math, 'sign', function(value)
    if value > 0 then return 1 end
    if value < 0 then return -1 end
    return 0
  end)
end
if rawget(_G, 'unpack') == nil and type(table.unpack) == 'function' then rawset(_G, 'unpack', table.unpack) end
if rawget(_G, 'printidentity') == nil then rawset(_G, 'printidentity', __protez_noop) end

@@ROBLOX_SURFACE@@

@@EXECUTOR_SURFACE@@

@@EXECUTOR_API_SURFACE@@

-- Scripts that re-sandbox themselves with setfenv() must keep seeing the
-- executor surface; otherwise the payload dies on its first environment probe.
local __protez_real_setfenv = rawget(_G, 'setfenv')
local __protez_real_getfenv = rawget(_G, 'getfenv')
if type(__protez_real_setfenv) == 'function' and rawget(_G, '__PROTEZ_SETFENV_WRAPPED') == nil then
  rawset(_G, '__PROTEZ_SETFENV_WRAPPED', true)
  local __protez_surface = rawget(_G, '__protez_globals_table') or {}
  rawset(_G, 'setfenv', function(target, environment)
    if type(environment) == 'table' and rawequal(environment, _G) == false then
      local previous = getmetatable(environment)
      local previous_index = type(previous) == 'table' and rawget(previous, '__index') or nil
      local previous_newindex = type(previous) == 'table' and rawget(previous, '__newindex') or nil
      -- A function metamethod cannot take part in Lua's metatable loop, so
      -- this lookup always terminates.
      setmetatable(environment, {
        __index = function(self, key)
          local value = __protez_surface[key]
          if value ~= nil then return value end
          if type(previous_index) == 'function' then return previous_index(self, key) end
          if type(previous_index) == 'table' then return previous_index[key] end
          return rawget(_G, key)
        end,
        __newindex = previous_newindex,
      })
      return __protez_real_setfenv(target, environment)
    end
    return __protez_real_setfenv(target, environment)
  end)
end
if type(__protez_real_getfenv) == 'function' then
  rawset(_G, 'getfenv', function(target)
    local environment = __protez_real_getfenv(target)
    if type(environment) ~= 'table' then return environment end
    -- The real environment already carries every global and every executor
    -- function; returning it unchanged is what a Roblox executor does.  The
    -- previous version wrapped it, which put a metatable on _G itself and made
    -- every later miss walk _G -> surface -> _G until Lua gave up.
    if rawequal(environment, _G) then return environment end
    local meta = getmetatable(environment)
    if meta == nil then
      setmetatable(environment, {
        __index = function(_, key)
          local value = __protez_surface[key]
          if value ~= nil then return value end
          return rawget(_G, key)
        end,
      })
    end
    return environment
  end)
end
"""


def _profile_features(profile: ExecutorProfile) -> frozenset[str]:
    return frozenset(profile.features)


_ROBLOX_SURFACE = r"""-- ---------------------------------------------------------------------------
-- Roblox surface.  Objects are proxy tables: reading an unknown member or
-- calling an unknown method yields another proxy instead of nil, which is what
-- keeps a Roblox script alive long enough to reveal its payload.  Nothing is
-- networked unless the fetch hook is wired by the caller.
-- ---------------------------------------------------------------------------
rawset(_G, '__protez_globals', rawget(_G, '__protez_globals') or {})

local __protez_fetch

-- Real signal objects: `:Connect` remembers the callback, `getconnections`
-- lists it and `firesignal` can run it.  Nothing runs on its own.
local function __protez_new_signal(label)
  local connections = {}
  local signal = { __protez_type = 'RBXScriptSignal', __protez_connections = connections }
  local function connect(callback)
    local connection = {
      Enabled = true,
      Function = callback,
      Connected = true,
      __protez_type = 'RBXScriptConnection',
    }
    connection.Disconnect = function()
      connection.Connected = false
      connection.Enabled = false
      for index, item in ipairs(connections) do
        if item == connection then table.remove(connections, index) break end
      end
      return true
    end
    connections[#connections + 1] = connection
    return connection
  end
  signal.Connect = function(self, callback) return connect(callback) end
  signal.connect = signal.Connect
  signal.Once = function(self, callback)
    local connection
    connection = connect(function(...)
      if connection ~= nil then connection:Disconnect() end
      return callback(...)
    end)
    return connection
  end
  signal.Wait = function() return nil end
  signal.wait = signal.Wait
  signal.Fire = function(self, ...)
    for _, connection in ipairs(connections) do
      if connection.Enabled ~= false and type(connection.Function) == 'function' then
        pcall(connection.Function, ...)
      end
    end
    return #connections
  end
  signal.Destroy = function() connections = {} return true end
  signal.__protez_signal_name = label
  return signal
end

local __protez_signal_names = {
  RenderStepped = true, Heartbeat = true, Stepped = true, PreRender = true,
  PreSimulation = true, PreAnimation = true, PostSimulation = true,
  InputBegan = true, InputChanged = true, InputEnded = true,
  MouseButton1Click = true, MouseButton1Down = true, MouseButton1Up = true,
  MouseButton2Click = true, MouseEnter = true, MouseLeave = true,
  MouseMoved = true, MouseWheel = true, Changed = true, ChildAdded = true,
  ChildRemoved = true, DescendantAdded = true, DescendantRemoving = true,
  AncestryChanged = true, CharacterAdded = true, CharacterRemoving = true,
  Died = true, Touched = true, TouchEnded = true, Activated = true,
  Triggered = true, Died = true, Loaded = true, Focused = true, FocusLost = true,
  PromptButtonHoldBegan = true, PromptButtonHoldEnded = true, OnClientEvent = true,
  OnServerEvent = true, Event = true, StateChanged = true, Equipped = true,
  Unequipped = true, Running = true, Jumping = true, GamepadConnected = true,
  GamepadDisconnected = true, PlayerAdded = true, PlayerRemoving = true,
}

local function __protez_is_signal_name(key)
  if __protez_signal_names[key] then return true end
  local text = tostring(key)
  if text:sub(-7) == 'Changed' or text:sub(-5) == 'Added' or text:sub(-7) == 'Removed' then
    return true
  end
  return false
end

rawset(_G, '__protez_namecall_default', nil)

local function __protez_default_namecall(self, ...)
  -- Roblox instances answer `__namecall` with the method that
  -- `getnamecallmethod()` names; the default implementation simply runs the
  -- pending call recorded by the dispatcher.
  local pending = rawget(_G, '__protez_namecall_default')
  if type(pending) == 'function' then
    return pending()
  end
  return nil
end
rawset(_G, '__protez_default_namecall', __protez_default_namecall)

-- Roblox locks the metatables of its instances: `getmetatable(instance)` hands
-- back a string, and only the executor's own `getrawmetatable` sees the real
-- table.  Payloads probe for exactly that difference (it is how they tell a live
-- Roblox from a re-implementation), so the proxies behave the same way.
local __protez_locked_metatable = 'The metatable is locked'
local function __protez_raw_metatable(value)
  local debug_api = rawget(_G, 'debug')
  if type(debug_api) == 'table' and type(debug_api.getmetatable) == 'function' then
    local ok, meta = pcall(debug_api.getmetatable, value)
    if ok then return meta end
  end
  return getmetatable(value)
end
rawset(_G, '__protez_raw_metatable', __protez_raw_metatable)
rawset(_G, '__protez_locked_metatable', __protez_locked_metatable)

local function __protez_new_proxy(label, fields)
  local store = fields or {}
  local cache = {}
  local proxy
  proxy = setmetatable(store, {
    __metatable = __protez_locked_metatable,
    __namecall = __protez_default_namecall,
    __index = function(self, key)
      local value = rawget(cache, key)
      if value ~= nil then return value end
      if key == 'ClassName' or key == 'Name' then return label end
      if key == 'HttpGet' or key == 'HttpGetAsync' or key == 'GetAsync' then
        local fetcher = function(self, url, ...)
          local extra = { url, ... }
          local method = key
          local function default_call()
            return __protez_fetch(extra[1], extra[2], extra[3], extra[4])
          end
          -- Namecall hooks (hookmetamethod, or the classic
          -- `getrawmetatable(game).__namecall = ...` dance) must see the real
          -- arguments, exactly like they would inside a Roblox instance call.
          local invoke = rawget(_G, '__protez_namecall_invoke')
          if type(invoke) == 'function' then
            return invoke(self, method, default_call, extra[1], extra[2], extra[3], extra[4])
          end
          local meta = __protez_raw_metatable(self)
          local hook = type(meta) == 'table' and rawget(meta, '__namecall') or nil
          if type(hook) == 'function' then
            local previous = rawget(_G, '__protez_namecall_default')
            rawset(_G, '__protez_namecall_default', default_call)
            local ok, value = pcall(hook, self, extra[1], extra[2], extra[3], extra[4])
            rawset(_G, '__protez_namecall_default', previous)
            if ok then return value end
          end
          return default_call()
        end
        rawset(cache, key, fetcher)
        return fetcher
      end
      if key == 'PostAsync' or key == 'RequestAsync' or key == 'GetObjects' then
        local fetcher = function(_, url, ...) return __protez_fetch(url, ...) end
        rawset(cache, key, fetcher)
        return fetcher
      end
      if __protez_is_signal_name(key) then
        local signal = __protez_new_signal(label .. '.' .. tostring(key))
        rawset(cache, key, signal)
        return signal
      end
      if key == 'WaitForChild' or key == 'FindFirstChild' or key == 'FindFirstChildOfClass' or key == 'FindFirstAncestor' then
        local finder = function(_, ...) return __protez_new_proxy(label .. '.' .. tostring(key)) end
        rawset(cache, key, finder)
        return finder
      end
      if key == 'IsA' then
        local isa = function(_, ...) return true end
        rawset(cache, key, isa)
        return isa
      end
      if key == 'GetChildren' or key == 'GetDescendants' then
        local children = function() return {} end
        rawset(cache, key, children)
        return children
      end
      if key == 'Connect' or key == 'connect' or key == 'Once' then
        local connect = function() return { Disconnect = function() end, disconnect = function() end, Connected = true } end
        rawset(cache, key, connect)
        return connect
      end
      local child = __protez_new_proxy(label .. '.' .. tostring(key))
      rawset(cache, key, child)
      return child
    end,
    __newindex = function(self, key, value)
      rawset(cache, key, value)
      rawset(self, key, value)
    end,
    __call = function(self, ...)
      return __protez_new_proxy(label .. '()')
    end,
    __tostring = function() return label end,
    __len = function() return 0 end,
    __eq = function(left, right) return rawequal(left, right) end,
    __add = function() return 0 end,
    __sub = function() return 0 end,
    __mul = function() return 0 end,
  })
  return proxy
end
rawset(_G, '__protez_new_proxy', __protez_new_proxy)

local __protez_players = __protez_new_proxy('Players', {
  Name = 'Players',
  ClassName = 'Players',
  LocalPlayer = __protez_new_proxy('Player', {
    Name = 'Protez',
    DisplayName = 'Protez',
    UserId = 1,
    AccountAge = 1,
  }),
  MaxPlayers = 12,
  NumPlayers = 1,
})

local __protez_services = { Players = __protez_players }
local function __protez_service(name)
  local key = tostring(name)
  local cached = __protez_services[key]
  if cached ~= nil then return cached end
  local service = __protez_new_proxy(key, { Name = key, ClassName = key })
  __protez_services[key] = service
  return service
end
rawset(_G, '__protez_services', __protez_services)
rawset(_G, 'gethui', function() return __protez_service('CoreGui') end)
rawset(_G, 'getgui', rawget(_G, 'gethui'))

local __protez_place_id = tonumber(rawget(_G, '__protez_place_id')) or 0
if __protez_place_id <= 0 then
  -- Emulated session identifiers: non-zero so loaders that refuse to run
  -- outside a place do not bail out.
  __protez_place_id = 1500000000
end
local __protez_game = __protez_new_proxy('game', {
  PlaceId = __protez_place_id,
  GameId = __protez_place_id,
  JobId = tostring(rawget(_G, '__protez_job_id') or 'protez0000-0000-0000-0000-protez000000'),
  PlaceVersion = 1,
  Workspace = __protez_new_proxy('Workspace', { Name = 'Workspace', ClassName = 'Workspace' }),
  GetService = function(self, name) return __protez_service(name) end,
  FindService = function(self, name) return __protez_service(name) end,
  IsLoaded = function() return true end,
  GetObjects = function() return {} end,
  BindToClose = function() end,
})

local function __protez_is_host_callable(value)
  local kind = type(value)
  return kind == 'function' or kind == 'userdata'
end
function __protez_fetch(url, options)
  if type(url) == 'table' and url.Url then
    options = url
    url = url.Url
  end
  if type(__protez_http_bridge) == 'function' then
    local ok, body = pcall(__protez_http_bridge, tostring(url), options)
    if ok and type(body) == 'string' then return body end
  end
  local host_http = rawget(_G, '__protez_http')
  if __protez_is_host_callable(host_http) then
    local ok, body = pcall(host_http, tostring(url), 'GET')
    if ok and type(body) == 'string' then return body end
  end
  return ''
end
rawset(_G, '__protez_fetch', __protez_fetch)

__protez_game.__protez_fetch = __protez_fetch

rawset(_G, 'game', __protez_game)
rawset(_G, 'Game', __protez_game)
rawset(_G, 'workspace', __protez_game.Workspace)
rawset(_G, 'Workspace', __protez_game.Workspace)
rawset(_G, 'script', __protez_new_proxy('Script', { Name = 'ProtezScript', ClassName = 'Script' }))
rawset(_G, 'shared', rawget(_G, '__protez_globals'))
if rawget(_G, 'settings') == nil then
  rawset(_G, 'settings', function() return __protez_new_proxy('Settings') end)
end

if rawget(_G, 'Instance') == nil then
  rawset(_G, 'Instance', {
    new = function(className, parent)
      local instance = __protez_new_proxy(tostring(className), {
        Name = tostring(className),
        ClassName = tostring(className),
        Parent = parent,
      })
      return instance
    end,
    fromExisting = function(value) return value end,
  })
end
if rawget(_G, 'Enum') == nil then
  rawset(_G, 'Enum', __protez_new_proxy('Enum'))
end
if rawget(_G, 'Color3') == nil then
  rawset(_G, 'Color3', {
    new = function(red, green, blue)
      return { R = red or 0, G = green or 0, B = blue or 0, __protez_type = 'Color3' }
    end,
    fromRGB = function(red, green, blue)
      return { R = (red or 0) / 255, G = (green or 0) / 255, B = (blue or 0) / 255, __protez_type = 'Color3' }
    end,
    fromHSV = function() return { R = 0, G = 0, B = 0, __protez_type = 'Color3' } end,
  })
end
if rawget(_G, 'UDim2') == nil then
  rawset(_G, 'UDim2', { new = function(...) return { __protez_type = 'UDim2' } end, fromScale = function() return {} end, fromOffset = function() return {} end })
end
if rawget(_G, 'UDim') == nil then
  rawset(_G, 'UDim', { new = function(...) return { __protez_type = 'UDim' } end })
end
-- Luau's `vector` library.  Luraph v15 builds vectors out of its constants
-- (`vector.create`), so a backend without it stops at the first component.
if rawget(_G, 'vector') == nil then
  local vector_mt
  local function component(value, index)
    if type(value) == 'number' then return value end
    if type(value) ~= 'table' then error('vector or number expected', 3) end
    if index == 1 then return value.x or value.X or value[1] or 0 end
    if index == 2 then return value.y or value.Y or value[2] or 0 end
    return value.z or value.Z or value[3] or 0
  end
  local function make(x, y, z)
    return setmetatable({ x = x, y = y, z = z, X = x, Y = y, Z = z }, vector_mt)
  end
  vector_mt = {
    __index = function(self, key)
      if key == 'Magnitude' or key == 'magnitude' then
        return math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
      end
      if key == 'Unit' or key == 'unit' then
        local length = math.sqrt(self.x * self.x + self.y * self.y + self.z * self.z)
        if length == 0 then return make(0, 0, 0) end
        return make(self.x / length, self.y / length, self.z / length)
      end
      return nil
    end,
    __add = function(a, b) return make(component(a, 1) + component(b, 1), component(a, 2) + component(b, 2), component(a, 3) + component(b, 3)) end,
    __sub = function(a, b) return make(component(a, 1) - component(b, 1), component(a, 2) - component(b, 2), component(a, 3) - component(b, 3)) end,
    __mul = function(a, b) return make(component(a, 1) * component(b, 1), component(a, 2) * component(b, 2), component(a, 3) * component(b, 3)) end,
    __div = function(a, b)
      local bx, by, bz = component(b, 1), component(b, 2), component(b, 3)
      return make(component(a, 1) / bx, component(a, 2) / by, component(a, 3) / bz)
    end,
    __unm = function(a) return make(-component(a, 1), -component(a, 2), -component(a, 3)) end,
    __eq = function(a, b)
      return component(a, 1) == component(b, 1) and component(a, 2) == component(b, 2)
        and component(a, 3) == component(b, 3)
    end,
    __tostring = function(self) return self.x .. ', ' .. self.y .. ', ' .. self.z end,
  }
  local vector_table = {}
  vector_table.create = function(x, y, z) return make(x or 0, y or 0, z or 0) end
  vector_table.zero = make(0, 0, 0)
  vector_table.one = make(1, 1, 1)
  vector_table.magnitude = function(value)
    return math.sqrt(component(value, 1) ^ 2 + component(value, 2) ^ 2 + component(value, 3) ^ 2)
  end
  vector_table.normalize = function(value)
    local length = vector_table.magnitude(value)
    if length == 0 then return make(0, 0, 0) end
    return make(component(value, 1) / length, component(value, 2) / length, component(value, 3) / length)
  end
  vector_table.dot = function(a, b)
    return component(a, 1) * component(b, 1) + component(a, 2) * component(b, 2) + component(a, 3) * component(b, 3)
  end
  vector_table.cross = function(a, b)
    local ax, ay, az = component(a, 1), component(a, 2), component(a, 3)
    local bx, by, bz = component(b, 1), component(b, 2), component(b, 3)
    return make(ay * bz - az * by, az * bx - ax * bz, ax * by - ay * bx)
  end
  vector_table.angle = function(a, b, axis)
    local denominator = vector_table.magnitude(a) * vector_table.magnitude(b)
    if denominator == 0 then return 0 end
    local cosine = vector_table.dot(a, b) / denominator
    if cosine > 1 then cosine = 1 elseif cosine < -1 then cosine = -1 end
    return math.acos(cosine)
  end
  local function unary(value, operation)
    return make(operation(component(value, 1)), operation(component(value, 2)), operation(component(value, 3)))
  end
  vector_table.floor = function(value) return unary(value, math.floor) end
  vector_table.ceil = function(value) return unary(value, math.ceil) end
  vector_table.abs = function(value) return unary(value, math.abs) end
  vector_table.sign = function(value)
    return unary(value, function(number)
      if number > 0 then return 1 end
      if number < 0 then return -1 end
      return 0
    end)
  end
  vector_table.clamp = function(value, minimum, maximum)
    return make(
      math.max(component(minimum, 1), math.min(component(maximum, 1), component(value, 1))),
      math.max(component(minimum, 2), math.min(component(maximum, 2), component(value, 2))),
      math.max(component(minimum, 3), math.min(component(maximum, 3), component(value, 3)))
    )
  end
  vector_table.max = function(...)
    local result = { math.huge, math.huge, math.huge }
    for index = 1, select('#', ...) do
      local value = select(index, ...)
      for axis = 1, 3 do
        result[axis] = math.max(result[axis], component(value, axis))
      end
    end
    return make(result[1], result[2], result[3])
  end
  vector_table.min = function(...)
    local result = { -math.huge, -math.huge, -math.huge }
    for index = 1, select('#', ...) do
      local value = select(index, ...)
      for axis = 1, 3 do
        result[axis] = math.min(result[axis], component(value, axis))
      end
    end
    return make(result[1], result[2], result[3])
  end
  rawset(_G, 'vector', vector_table)
end
-- Remaining Luau standard-library gaps loaders probe for.
if type(table.move) ~= 'function' then
  rawset(table, 'move', function(source, first, last, target, destination)
    local out = destination or source
    if source == out and target > first and target <= last then
      for offset = last - first, 0, -1 do out[target + offset] = source[first + offset] end
    else
      for offset = 0, last - first do out[target + offset] = source[first + offset] end
    end
    return out
  end)
end
if type(table.clone) ~= 'function' then
  rawset(table, 'clone', function(source)
    local out = {}
    for key, value in pairs(source) do out[key] = value end
    return out
  end)
end
if type(math.noise) ~= 'function' then
  rawset(math, 'noise', function(x, y, z)
    local total = (x or 0) * 12.9898 + (y or 0) * 78.233 + (z or 0) * 37.719
    local fract = total - math.floor(total)
    return fract * 2 - 1
  end)
end
if type(bit32.byteswap) ~= 'function' then
  rawset(bit32, 'byteswap', function(value)
    value = value % 4294967296
    if value < 0 then value = value + 4294967296 end
    local first = value % 256
    local second = math.floor(value / 256) % 256
    local third = math.floor(value / 65536) % 256
    local fourth = math.floor(value / 16777216) % 256
    return ((first * 256 + second) * 256 + third) * 256 + fourth
  end)
end
if type(coroutine.close) ~= 'function' then
  rawset(coroutine, 'close', function(thread) return true end)
end
if type(utf8.charpattern) ~= 'string' then
  rawset(utf8, 'charpattern', '[\\0-\\127\\194-\\244][\\128-\\191]*')
end
if rawset ~= nil and rawget(_G, 'utf8') ~= nil and type(utf8.nfcnormalize) ~= 'function' then
  rawset(utf8, 'nfcnormalize', function(value) return value end)
  rawset(utf8, 'nfdnormalize', function(value) return value end)
end
if rawget(_G, 'Vector2') == nil then
  rawset(_G, 'Vector2', { new = function(x, y) return { X = x or 0, Y = y or 0, __protez_type = 'Vector2' } end, zero = { X = 0, Y = 0 } })
end
if rawget(_G, 'Vector3') == nil then
  rawset(_G, 'Vector3', {
    new = function(x, y, z) return { X = x or 0, Y = y or 0, Z = z or 0, __protez_type = 'Vector3' } end,
    zero = { X = 0, Y = 0, Z = 0 },
    one = { X = 1, Y = 1, Z = 1 },
  })
end
if rawget(_G, 'CFrame') == nil then
  rawset(_G, 'CFrame', {
    new = function(...) return __protez_new_proxy('CFrame', { __protez_type = 'CFrame' }) end,
    Angles = function() return __protez_new_proxy('CFrame') end,
    fromEulerAnglesXYZ = function() return __protez_new_proxy('CFrame') end,
  })
end
if rawget(_G, 'Random') == nil then
  rawset(_G, 'Random', { new = function() return __protez_new_proxy('Random') end })
end
if rawget(_G, 'Ray') == nil then
  rawset(_G, 'Ray', { new = function() return __protez_new_proxy('Ray') end })
end
if rawget(_G, 'Region3') == nil then
  rawset(_G, 'Region3', { new = function() return __protez_new_proxy('Region3') end })
end
if rawget(_G, 'TweenInfo') == nil then
  rawset(_G, 'TweenInfo', { new = function() return {} end })
end
if rawget(_G, 'BrickColor') == nil then
  rawset(_G, 'BrickColor', {
    new = function(value) return __protez_new_proxy('BrickColor', { Number = 1, Name = tostring(value or 'Medium stone grey') }) end,
    random = function() return __protez_new_proxy('BrickColor') end,
    Red = function() return __protez_new_proxy('BrickColor') end,
  })
end
if rawget(_G, 'TaskScheduler') == nil then
  rawset(_G, 'TaskScheduler', __protez_new_proxy('TaskScheduler'))
end
if rawget(_G, 'typeof') == nil or type(rawget(_G, 'typeof')) ~= 'function' then
  rawset(_G, 'typeof', function(value)
    if type(value) == 'table' and rawget(value, '__protez_type') then return rawget(value, '__protez_type') end
    return type(value)
  end)
end

-- Scheduler shims.  Everything runs inline; protected calls keep a failing
-- task from taking the whole analysis down.
if rawget(_G, 'wait') == nil or type(rawget(_G, 'wait')) ~= 'function' then
  rawset(_G, 'wait', function() return 0.0 end)
end
local function __protez_run_task(callback, ...)
  if type(callback) == 'function' then
    local ok, err = pcall(callback, ...)
    if not ok then return nil, err end
    return true
  end
  return true
end
if rawget(_G, 'spawn') == nil or type(rawget(_G, 'spawn')) ~= 'function' then
  rawset(_G, 'spawn', function(callback, ...) return __protez_run_task(callback, ...) end)
end
if rawget(_G, 'delay') == nil or type(rawget(_G, 'delay')) ~= 'function' then
  rawset(_G, 'delay', function(_, callback, ...) return __protez_run_task(callback, ...) end)
end
if rawget(_G, 'tick') == nil or type(rawget(_G, 'tick')) ~= 'function' then
  rawset(_G, 'tick', function() return 0.0 end)
end
if rawget(_G, 'time') == nil or type(rawget(_G, 'time')) ~= 'function' then
  rawset(_G, 'time', function() return 0.0 end)
end
if rawget(_G, 'task') == nil then
  rawset(_G, 'task', {
    wait = function() return 0.0 end,
    spawn = function(callback, ...) return __protez_run_task(callback, ...) end,
    defer = function(callback, ...) return __protez_run_task(callback, ...) end,
    delay = function(_, callback, ...) return __protez_run_task(callback, ...) end,
    desynchronize = function(callback, ...)
      if type(callback) == 'function' then return __protez_run_task(callback, ...) end
      return nil
    end,
    synchronize = function(callback, ...)
      if type(callback) == 'function' then return __protez_run_task(callback, ...) end
      return nil
    end,
    cancel = function() end,
  })
end
if rawget(_G, 'require') == nil then
  rawset(_G, 'require', function(module)
    if type(module) == 'table' then return module end
    return __protez_new_proxy('ModuleScript' .. tostring(module))
  end)
end
if rawget(_G, 'debug') == nil then rawset(_G, 'debug', {}) end
if type(rawget(_G, 'debug').getinfo) ~= 'function' then
  rawget(_G, 'debug').getinfo = function() return { source = '@Protez', short_src = '@Protez', currentline = 1, what = 'Lua' } end
end
if type(rawget(_G, 'debug').traceback) ~= 'function' then
  rawget(_G, 'debug').traceback = function() return 'protez stub traceback' end
end
if type(rawget(_G, 'debug').sethook) ~= 'function' then
  rawget(_G, 'debug').sethook = function() end
end
if type(rawget(_G, 'debug').getregistry) ~= 'function' then
  rawget(_G, 'debug').getregistry = function() return {} end
end
if type(rawget(_G, 'os')) ~= 'table' then rawset(_G, 'os', {}) end
if type(rawget(_G, 'os').clock) ~= 'function' then rawget(_G, 'os').clock = function() return 0.0 end end
if type(rawget(_G, 'os').time) ~= 'function' then rawget(_G, 'os').time = function() return 0 end end
if type(rawget(_G, 'os').date) ~= 'function' then rawget(_G, 'os').date = function() return '1970-01-01' end end
if type(rawget(_G, 'os').getenv) ~= 'function' then rawget(_G, 'os').getenv = function() return nil end end
"""


_EXECUTOR_SURFACE = r"""-- ---------------------------------------------------------------------------
-- Executor surface.  getgenv() returns a live table backed by the globals, so
-- libraries written as `getgenv().lib = {}` behave the same as direct global
-- writes.  File and hooking APIs are inert: they answer with plausible values
-- and remember nothing outside this table.
-- ---------------------------------------------------------------------------
local __protez_globals = rawget(_G, '__protez_globals') or {}
setmetatable(__protez_globals, {
  __index = _G,
  __newindex = function(self, key, value)
    rawset(self, key, value)
    rawset(_G, key, value)
  end,
})
rawset(_G, '__protez_globals', __protez_globals)
rawset(_G, 'shared', __protez_globals)
rawset(_G, '__protez_globals_table', __protez_globals)

local function __protez_noop() return nil end
local function __protez_empty() return '' end
local function __protez_true() return true end
local function __protez_false() return false end
local function __protez_zero() return 0 end
local function __protez_table() return {} end
local function __protez_pass_first(value) return value end

local __protez_executor = {}
local executor_table = __protez_executor

local function __protez_declare(key, value)
  if rawget(_G, key) == nil then rawset(_G, key, value) end
  __protez_globals[key] = value
end

local __protez_host_http = rawget(_G, '__protez_http')
local function __protez_http(url, options)
  if type(url) == 'table' and url.Url then
    options = url
    url = url.Url
  end
  if type(__protez_http_bridge) == 'function' then
    local ok, body = pcall(__protez_http_bridge, tostring(url), options)
    if ok and type(body) == 'string' then return body end
  end
  if __protez_is_host_callable(__protez_host_http) then
    local ok, body = pcall(__protez_host_http, tostring(url), 'GET')
    if ok and type(body) == 'string' then return body end
  end
  return ''
end
if not __protez_is_host_callable(__protez_host_http) then
  rawset(_G, '__protez_http', __protez_http)
end
rawset(_G, '__protez_fetch', __protez_http)

local function __protez_request(options)
  local body = __protez_http(options)
  return {
    StatusCode = 200,
    StatusMessage = 'OK',
    Body = body,
    Headers = {},
    Success = true,
  }
end

local __protez_request_functions = {
  request = __protez_request,
  http_request = __protez_request,
  httpget = __protez_http,
  HttpGet = __protez_http,
  HttpGetAsync = __protez_http,
  httpgetasync = __protez_http,
  requestasync = function(options) return __protez_request(options) end,
}
for name, fn in pairs(__protez_request_functions) do
  __protez_declare(name, fn)
end

__protez_declare('identifyexecutor', function() return __protez_profile.executor end)
__protez_declare('getexecutorname', function() return __protez_profile.executor end)
__protez_declare('getexecutor', function() return __protez_profile.executor end)
__protez_declare('getexploit', function() return __protez_profile.executor end)
__protez_declare('getversion', function() return __protez_profile.version end)
__protez_declare('getexecutorversion', function() return __protez_profile.version end)
__protez_declare('getgenv', function() return __protez_globals end)
__protez_declare('getrenv', function() return _G end)
__protez_declare('getgc', __protez_table)
__protez_declare('getreg', __protez_table)
__protez_declare('getinstances', __protez_table)
__protez_declare('getnilinstances', __protez_table)
__protez_declare('getloadedmodules', __protez_table)
__protez_declare('getscripts', __protez_table)
__protez_declare('getcallingscript', function() return __protez_new_proxy('Script') end)
__protez_declare('getscripthash', __protez_empty)
__protez_declare('getscriptbytecode', __protez_empty)
__protez_declare('decompile', function(chunk) return '-- protez: decompilation requirement is not reachable here\n' end)
__protez_declare('checkcaller', __protez_true)
__protez_declare('is_sirhurt_closure', function() return __protez_profile.key == 'sirhurt' end)
__protez_declare('issirhurt', function() return __protez_profile.key == 'sirhurt' end)
__protez_declare('iskrnl', function() return __protez_profile.key == 'krnl' or __protez_profile.universal end)
__protez_declare('islclosure', __protez_false)
__protez_declare('iscclosure', __protez_true)
__protez_declare('isfunction', function(value) return type(value) == 'function' end)
__protez_declare('newcclosure', function(fn) return fn end)
__protez_declare('hookfunction', function(original, replacement) return original end)
__protez_declare('replaceclosure', function(original, replacement) return original end)
__protez_declare('hookmetamethod', function(object, method, hook) return function() return nil end end)
__protez_declare('getconnections', __protez_table)
__protez_declare('getrawmetatable', function(value)
  -- The real metatable, even when the object is locked: this is exactly what
  -- an executor's `getrawmetatable` is for.
  local raw = rawget(_G, '__protez_raw_metatable')
  if type(raw) == 'function' then return raw(value) end
  return getmetatable(value)
end)
__protez_declare('setreadonly', __protez_true)
__protez_declare('isreadonly', __protez_false)
__protez_declare('getupvalue', function(fn, index) return nil end)
__protez_declare('getupvalues', __protez_table)
__protez_declare('setupvalue', __protez_pass_first)
__protez_declare('getconstants', __protez_table)
__protez_declare('getprotos', __protez_table)
__protez_declare('getinfo', __protez_table)
__protez_declare('getnamecallmethod', __protez_empty)
__protez_declare('setnamecallmethod', __protez_noop)
__protez_declare('getsenv', function() return __protez_globals end)
__protez_declare('getthreadidentity', function() return 8 end)
__protez_declare('getidentity', function() return 8 end)
__protez_declare('setthreadidentity', __protez_noop)
__protez_declare('getheap', __protez_table)
__protez_declare('queue_on_teleport', __protez_noop)
__protez_declare('setclipboard', __protez_true)
__protez_declare('writefile', __protez_true)
__protez_declare('readfile', __protez_empty)
__protez_declare('appendfile', __protez_true)
__protez_declare('listfiles', __protez_table)
__protez_declare('isfile', __protez_false)
__protez_declare('isfolder', __protez_false)
__protez_declare('delfile', __protez_true)
__protez_declare('makefolder', __protez_true)
__protez_declare('delfolder', __protez_true)
__protez_declare('getcustomasset', function(path) return 'rbxasset://' .. tostring(path) end)
__protez_declare('cache_replace', __protez_pass_first)
__protez_declare('cache_invalidate', __protez_noop)
__protez_declare('fireclickdetector', __protez_noop)
__protez_declare('firetouchinterest', __protez_noop)
__protez_declare('fireproximityprompt', __protez_noop)
__protez_declare('sethiddenproperty', __protez_true)
__protez_declare('gethiddenproperty', function() return nil, false end)
__protez_declare('setscriptable', __protez_true)
__protez_declare('getcallbackvalue', __protez_noop)
__protez_declare('setfpscap', __protez_noop)
__protez_declare('getfpscap', function() return 60 end)
__protez_declare('setrenderproperty', __protez_noop)
__protez_declare('getrenderproperty', __protez_noop)
__protez_declare('protect_gui', __protez_pass_first)
__protez_declare('unprotect_gui', __protez_pass_first)
__protez_declare('cloneref', __protez_pass_first)
__protez_declare('compareinstances', function(left, right) return rawequal(left, right) end)
__protez_declare('getconnections', __protez_table)
__protez_declare('getcustomasset', function(path) return 'rbxasset://' .. tostring(path) end)

local function __protez_b64(value, encode)
  if encode then return __protez_b64_encode(value) end
  return __protez_b64_decode(value)
end
__protez_declare('base64_encode', function(value) return __protez_b64_encode(value) end)
__protez_declare('base64_decode', function(value) return __protez_b64_decode(value) end)
__protez_declare('base64encode', function(value) return __protez_b64_encode(value) end)
__protez_declare('base64decode', function(value) return __protez_b64_decode(value) end)
__protez_declare('crypt', __protez_noop)
__protez_declare('hash', __protez_empty)

-- Per-executor namespaces (syn.request, krnl.loadstring, ...).  In universal
-- mode every marker exists at once so any executor probe succeeds.
local __protez_marker_names = {
@@MARKERS@@
}
for _, name in ipairs(__protez_marker_names) do
  if rawget(_G, name) == nil then
    rawset(_G, name, setmetatable({}, { __index = __protez_globals, __call = function() return nil end }))
  end
  local namespace = rawget(_G, name)
  if type(namespace) == 'table' and getmetatable(namespace) ~= nil then
    namespace.request = __protez_request
    namespace.http_request = __protez_request
    namespace.HttpGet = __protez_http
    namespace.HttpGetAsync = __protez_http
    namespace.protect_gui = __protez_pass_first
    namespace.unprotect_gui = __protez_pass_first
    namespace.queue_on_teleport = __protez_noop
    namespace.setclipboard = __protez_true
    namespace.writefile = __protez_true
    namespace.readfile = __protez_empty
    namespace.getgenv = function() return __protez_globals end
    namespace.getversions = function() return { version = __protez_profile.version } end
    namespace.is_beta = __protez_false
    namespace.loadstring = loadstring or load
    namespace.crypt = __protez_noop
    namespace.setthreadidentity = __protez_noop
    namespace.getthreadidentity = __protez_zero
    namespace.getscriptbytecode = __protez_empty
    namespace.decompile = function() return '-- protez stub\n' end
    namespace.getcallingscript = function() return __protez_new_proxy('Script') end
    namespace.version = __protez_profile.version
    namespace.name = __protez_profile.executor
  end
end
rawset(_G, '__protez_executor_namespace', __protez_executor)
rawset(_G, '__protez_profile_table', __protez_profile)
"""


_PLAIN_SURFACE = r"""-- No injector emulation requested: only the plain Lua/Luau environment.
if rawget(_G, 'getgenv') == nil then
  local __protez_plain_globals = rawget(_G, '__protez_globals') or {}
  setmetatable(__protez_plain_globals, { __index = _G })
  rawset(_G, '__protez_globals', __protez_plain_globals)
  rawset(_G, 'shared', __protez_plain_globals)
  rawset(_G, '__protez_globals_table', __protez_plain_globals)
  rawset(_G, 'getgenv', function() return __protez_plain_globals end)
  rawset(_G, 'getrenv', function() return _G end)
end
if type(rawget(_G, '__protez_http')) ~= 'function' and type(rawget(_G, '__protez_http')) ~= 'userdata' then
  rawset(_G, '__protez_http', function(url, options)
    if type(url) == 'table' and url.Url then url = url.Url end
    if type(__protez_http_bridge) == 'function' then
      local ok, body = pcall(__protez_http_bridge, tostring(url), options)
      if ok and type(body) == 'string' then return body end
    end
    return ''
  end)
end
if rawget(_G, '__protez_fetch') == nil then
  rawset(_G, '__protez_fetch', rawget(_G, '__protez_http'))
end
"""


__all__.append("EXECUTOR_GLOBAL_TABLE")


def build_http_stub_prelude(
    responses: Mapping[str, str] | None = None,
    *,
    fallback: str | None = None,
) -> str:
    """Install a canned response table as the HTTP bridge.

    ``responses`` maps a URL (or a URL prefix) to a body.  The second pass of
    the two-pass native analysis calls this with whatever the first pass
    captured, so a payload that needs a live fetch still gets executed.
    """
    lines = ["-- Canned HTTP responses from the capture pass."]
    lines.append("__protez_http_responses = {}")
    for url, body in (responses or {}).items():
        lines.append(
            f"__protez_http_responses[{_lua_string(str(url))}] = {_lua_string(str(body))}"
        )
    lines.append(
        "local __protez_http_lookup = function(url)\n"
        "  url = tostring(url)\n"
        "  if __protez_http_responses[url] ~= nil then return __protez_http_responses[url] end\n"
        "  for pattern, body in pairs(__protez_http_responses) do\n"
        "    if #pattern > 0 and url:sub(1, #pattern) == pattern then return body end\n"
        "  end\n"
        "  return nil\n"
        "end"
    )
    lines.append(
        "rawset(_G, '__protez_http_bridge', function(url, options)\n"
        "  local body = __protez_http_lookup(url)\n"
        "  if body ~= nil then return body end\n"
        + (f"  return {_lua_string(fallback)}" if fallback is not None else "  return nil")
        + "\nend)"
    )
    return "\n".join(lines) + "\n"

