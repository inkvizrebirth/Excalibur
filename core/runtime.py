"""Lua runtime discovery, probing and execution.

Two engines are supported and both drive the *same* Lua runner
(``core/lua/runner.lua``):

``lupa``
    In-process embedding.  Lupa ships wheels with Lua 5.1, LuaJIT, 5.2, 5.3 and
    5.4 for CPython on Windows/Linux/macOS, so the packaged EXE gets a Lua
    runtime with no extra download at all.  Preferred engine.

``exe``
    A bundled/``PATH`` interpreter (``lua51.exe``, ``lua54.exe``, ``luau.exe``,
    ``luajit.exe``).  Used when the app runs from a source checkout without
    lupa, or when the user drops a binary into ``lua/``.

Why a *ladder* of runtimes
--------------------------
Real WRD v1.0.0 samples are single-line files of hundreds of kilobytes.  PUC Lua
5.1, 5.2, 5.3 and LuaJIT 2.1 refuse to compile them::

    x:1: control structure too long near 'end'

Lua 5.4 compiles the same file, which is why it is in the ladder as the fallback
(paired with :mod:`core.lua51_compat` shims so that 5.1 semantics survive).
See ``docs/REAL_WORLD_NOTES.md`` for the measurements.
"""

from __future__ import annotations

import json
import importlib
import importlib.util
import os
import shutil
import subprocess
import sys
import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Iterable, List, Optional, Sequence, Tuple

from . import paths
from .config import SandboxConfig
from .errors import RuntimeUnavailable

#: lupa modules, best fidelity first, with the Lua dialect they embed.
LUPA_MODULES: Dict[str, Tuple[str, str]] = {
    # name          lupa module   dialect
    "lua51": ("lua51", "Lua 5.1"),
    "luajit21": ("luajit21", "Lua 5.1 (LuaJIT)"),
    "lua52": ("lua52", "Lua 5.2"),
    "lua53": ("lua53", "Lua 5.3"),
    "lua54": ("lua54", "Lua 5.4"),
    "lua55": ("lua55", "Lua 5.5"),
}

#: Executable file names searched for in ``lua/`` and on ``PATH``.
EXE_NAMES: Tuple[str, ...] = (
    "lua51.exe",
    "lua5.1.exe",
    "luajit.exe",
    "lua54.exe",
    "lua5.4.exe",
    "luau.exe",
    "lua.exe",
    "lua51",
    "luajit",
    "lua54",
    "lua5.4",
    "luau",
    "lua",
)

PROBE_LUA = """
local jitv = rawget(_G, "jit") and rawget(_G, "jit").version or ""
return _VERSION .. "|" .. jitv .. "|" .. tostring(type(load)) .. "|" .. tostring(type(debug) == "table" and type(debug.sethook))
"""

COMPILE_CHECK_LUA = """
local ok, res = pcall(function()
  local f, e
  if _VERSION == "Lua 5.1" then f, e = loadstring(SRC, "@check")
  else f, e = load(SRC, "@check", "t", {}) end
  if f then return "OK" end
  return "ERR:" .. tostring(e)
end)
if not ok then return "ERR:" .. tostring(res) end
return res
"""


@dataclass
class RuntimeSpec:
    """A concrete, usable Lua runtime."""

    name: str
    kind: str  # "lupa" | "exe"
    detail: str  # module name or executable path
    version: str = ""
    jit: str = ""
    probe_error: str = ""

    @property
    def label(self) -> str:
        suffix = f" [{self.jit}]" if self.jit else ""
        return f"{self.name} ({self.kind}){suffix}"

    def as_dict(self) -> dict:
        return {
            "name": self.name,
            "kind": self.kind,
            "detail": self.detail,
            "version": self.version,
            "jit": self.jit,
        }


@dataclass
class RunOutcome:
    """Result of one sandboxed execution."""

    ok: bool
    report: dict = field(default_factory=dict)
    stdout: str = ""
    stderr: str = ""
    runtime: Optional[RuntimeSpec] = None
    error: str = ""
    duration_ms: int = 0

    @property
    def loads(self) -> List[dict]:
        return list(self.report.get("loads") or [])

    @property
    def captures(self) -> List[dict]:
        return list(self.report.get("captures") or [])

    @property
    def ran(self) -> bool:
        return bool(self.report.get("ran"))

    @property
    def timed_out(self) -> bool:
        return bool(self.report.get("timed_out"))

    @property
    def run_error(self) -> str:
        return str(self.report.get("run_error") or self.report.get("error") or self.error or "")


def _lupa_available() -> bool:
    return importlib.util.find_spec("lupa") is not None


def discover_runtimes(
    wanted: Sequence[str],
    *,
    prefer_exe: bool = False,
    exe_dirs: Optional[Iterable[Path]] = None,
) -> List[RuntimeSpec]:
    """Return every *working* runtime, ordered by the ``wanted`` list.

    Probing is cheap (one tiny script per runtime) and results are cached for the
    process lifetime by :func:`probe_all`.
    """
    specs: List[RuntimeSpec] = []
    search_dirs = [paths.lua_dir(), *(exe_dirs or [])]

    exe_candidates: Dict[str, Path] = {}
    for directory in search_dirs:
        if not directory or not Path(directory).is_dir():
            continue
        for name in EXE_NAMES:
            candidate = Path(directory) / name
            if candidate.is_file():
                exe_candidates.setdefault(candidate.stem.lower(), candidate)
    for name in EXE_NAMES:
        found = shutil.which(name)
        if found:
            exe_candidates.setdefault(Path(found).stem.lower(), Path(found))

    for name in wanted:
        if name in exe_candidates and (prefer_exe or name not in LUPA_MODULES):
            specs.append(RuntimeSpec(name=name, kind="exe", detail=str(exe_candidates[name])))
        if name in LUPA_MODULES and _lupa_available() and not prefer_exe:
            module_name = LUPA_MODULES[name][0]
            specs.append(RuntimeSpec(name=name, kind="lupa", detail=module_name))

    # anything else the user dropped in lua/ (still useful)
    if not prefer_exe:
        for exe_name, path in exe_candidates.items():
            if not any(s.kind == "exe" and s.detail == str(path) for s in specs):
                specs.append(RuntimeSpec(name=exe_name, kind="exe", detail=str(path)))

    probed: List[RuntimeSpec] = []
    for spec in specs:
        result = probe_runtime(spec)
        if result is not None:
            probed.append(result)
    return probed


_PROBE_CACHE: Dict[str, Optional[RuntimeSpec]] = {}


def probe_runtime(spec: RuntimeSpec) -> Optional[RuntimeSpec]:
    """Verify that ``spec`` starts and can compile Lua; returns None on failure."""
    key = f"{spec.kind}:{spec.detail}"
    if key in _PROBE_CACHE:
        cached = _PROBE_CACHE[key]
        if cached is None:
            return None
        # refresh the display fields on the caller's object
        spec.version = cached.version
        spec.jit = cached.jit
        return spec

    try:
        if spec.kind == "lupa":
            module = importlib.import_module(f"lupa.{spec.detail}")
            lua = module.LuaRuntime()
            raw = lua.execute(PROBE_LUA)
            version, jit, load_type, sethook = (str(raw).split("|") + ["", "", "", ""])[:4]
            if sethook != "function":
                spec.probe_error = "debug.sethook unavailable (watchdog would not work)"
                _PROBE_CACHE[key] = None
                return None
            spec.version = version
            spec.jit = jit
        else:
            proc = subprocess.run(
                [spec.detail, "-v"],
                capture_output=True,
                text=True,
                timeout=20,
                creationflags=_creationflags(),
            )
            output = (proc.stdout or "") + (proc.stderr or "")
            if proc.returncode != 0 and "Lua" not in output:
                spec.probe_error = f"exit {proc.returncode}: {output.strip()[:200]}"
                _PROBE_CACHE[key] = None
                return None
            spec.version = _parse_version(output)
            spec.jit = "LuaJIT" if "luajit" in spec.detail.lower() else ""
    except Exception as exc:  # pragma: no cover - depends on host
        spec.probe_error = f"{type(exc).__name__}: {exc}"
        _PROBE_CACHE[key] = None
        return None

    _PROBE_CACHE[key] = RuntimeSpec(
        name=spec.name, kind=spec.kind, detail=spec.detail, version=spec.version, jit=spec.jit
    )
    return spec


def _parse_version(text: str) -> str:
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("Lua") or line.startswith("luajit") or "Lua 5." in line:
            return line[:80]
    return (text.strip().splitlines() or [""])[0][:80]


def _creationflags() -> int:
    return getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0) if os.name == "nt" else 0


class LuaRuntime:
    """Facade over the chosen engine for one execution."""

    def __init__(self, spec: RuntimeSpec, runner_path: Optional[Path] = None):
        self.spec = spec
        self.runner_path = runner_path or (paths.core_dir() / "lua" / "runner.lua")

    # ---------------------------------------------------------------- compile
    def compile_check(self, source: str) -> Tuple[bool, str]:
        """Compile ``source`` without executing it.  Returns ``(ok, error)``."""
        if self.spec.kind == "lupa":
            module = importlib.import_module(f"lupa.{self.spec.detail}")
            lua = module.LuaRuntime()
            lua.globals()["SRC"] = source
            result = str(lua.execute(COMPILE_CHECK_LUA))
            if result == "OK":
                return True, ""
            return False, result[4:] if result.startswith("ERR:") else result

        script = tempfile.NamedTemporaryFile("w", suffix=".lua", delete=False, encoding="utf-8")
        try:
            script.write(
                'local p = os.getenv("EXCALIBUR_CHECK_SRC")\n'
                'local f = io.open(p, "rb")\n'
                "if not f then print('ERR:cannot open source') return end\n"
                "local SRC = f:read('*a')\n"
                "f:close()\n" + COMPILE_CHECK_LUA + "\n"
            )
            script.close()
            env = dict(os.environ)
            source_file = tempfile.NamedTemporaryFile("w", suffix=".lua", delete=False, encoding="utf-8")
            source_file.write(source)
            source_file.close()
            env["EXCALIBUR_CHECK_SRC"] = source_file.name
            proc = subprocess.run(
                [self.spec.detail, script.name],
                capture_output=True,
                text=True,
                timeout=120,
                env=env,
                creationflags=_creationflags(),
            )
            out = (proc.stdout or "").strip()
            if out == "OK":
                return True, ""
            return False, out or (proc.stderr or "unknown compile failure").strip()[:400]
        finally:
            for tmp in (locals().get("script"), locals().get("source_file")):
                try:
                    if tmp is not None:
                        os.unlink(tmp.name)
                except OSError:
                    pass

    # -------------------------------------------------------------------- run
    def run_runner(self, config: Dict[str, str], sandbox_cfg: SandboxConfig) -> RunOutcome:
        """Execute ``runner.lua`` in this runtime and return the parsed report."""
        logs_dir = Path(config["logs_dir"])
        report_path = logs_dir / "report.json"
        if report_path.exists():
            report_path.unlink()

        started = time.time()
        if self.spec.kind == "lupa":
            ok, stdout, stderr, error = self._run_lupa(config, sandbox_cfg)
        else:
            ok, stdout, stderr, error = self._run_exe(config, sandbox_cfg)

        duration_ms = int((time.time() - started) * 1000)
        report: dict = {}
        if report_path.exists():
            try:
                report = json.loads(report_path.read_text(encoding="utf-8"))
            except json.JSONDecodeError as exc:
                error = error or f"corrupt report.json: {exc}"
        elif not error:
            error = "runner produced no report.json"

        return RunOutcome(
            ok=ok and bool(report) and not error,
            report=report,
            stdout=stdout,
            stderr=stderr,
            runtime=self.spec,
            error=error,
            duration_ms=duration_ms,
        )

    def _run_lupa(self, config: Dict[str, str], sandbox_cfg: SandboxConfig) -> Tuple[bool, str, str, str]:
        module = importlib.import_module(f"lupa.{self.spec.detail}")
        lua = module.LuaRuntime(unpack_returned_tuples=True)
        setter = getattr(lua, "set_max_memory", None)
        if callable(setter):
            try:
                setter(2048 * 1024 * 1024)
            except Exception:  # pragma: no cover - depends on lupa build
                pass
        # Build the config table by item assignment: `LuaRuntime.table()` has
        # changed semantics across lupa releases (dict vs. kwargs), item
        # assignment works on every version.
        table = lua.table()
        for key, value in config.items():
            if value is not None:
                table[key] = str(value)
        lua.globals()["EXCALIBUR"] = table
        code = Path(self.runner_path).read_text(encoding="utf-8")
        error = ""
        try:
            lua.execute(code)
        except Exception as exc:
            error = f"{type(exc).__name__}: {str(exc)[:400]}"
        return True, "", "", error

    def _run_exe(self, config: Dict[str, str], sandbox_cfg: SandboxConfig) -> Tuple[bool, str, str, str]:
        env = dict(os.environ)
        for key, value in config.items():
            if value is None:
                continue
            env[f"EXCALIBUR_{key.upper()}"] = str(value)
        env["EXCALIBUR_ENGINE"] = "exe"
        timeout = sandbox_cfg.timeout + 15
        try:
            proc = subprocess.run(
                [self.spec.detail, str(self.runner_path)],
                capture_output=True,
                text=True,
                timeout=timeout,
                env=env,
                creationflags=_creationflags(),
            )
        except subprocess.TimeoutExpired:
            return False, "", "", f"interpreter exceeded {timeout:.0f}s hard limit"
        error = ""
        if proc.returncode != 0 and not (Path(config["logs_dir"]) / "report.json").exists():
            error = f"interpreter exit {proc.returncode}: {(proc.stderr or '').strip()[:300]}"
        return True, proc.stdout or "", proc.stderr or "", error


def runtime_ladder(
    wanted: Sequence[str],
    source: Optional[str] = None,
    *,
    prefer_exe: bool = False,
) -> Tuple[List[RuntimeSpec], List[Tuple[RuntimeSpec, str]]]:
    """Split available runtimes into those that compile ``source`` and the rest.

    Returns ``(usable, rejected)`` where ``rejected`` carries the compile error,
    which is surfaced in the report so the user learns *why* a runtime was
    skipped (e.g. "control structure too long").
    """
    specs = discover_runtimes(wanted, prefer_exe=prefer_exe)
    if not specs:
        raise RuntimeUnavailable(
            "no Lua runtime available: install lupa (pip install lupa) or drop a "
            "lua51.exe/lua54.exe/luau.exe next to the executable"
        )
    if source is None:
        return specs, []

    usable: List[RuntimeSpec] = []
    rejected: List[Tuple[RuntimeSpec, str]] = []
    for spec in specs:
        runtime = LuaRuntime(spec)
        ok, err = runtime.compile_check(source)
        if ok:
            usable.append(spec)
        else:
            rejected.append((spec, err))
    return usable, rejected


def describe_environment() -> List[dict]:
    """Diagnostics for the GUI/CLI: what is available on this machine."""
    info = [
        {"key": "python", "value": sys.version.split()[0]},
        {"key": "frozen", "value": str(paths.is_frozen())},
        {"key": "lupa", "value": "yes" if _lupa_available() else "no"},
        {"key": "resource_root", "value": str(paths.resource_root())},
        {"key": "app_data", "value": str(paths.app_data_dir())},
        {"key": "logs", "value": str(paths.logs_dir())},
    ]
    for spec in discover_runtimes(("lua51", "luajit21", "lua52", "lua53", "lua54", "luau")):
        info.append({"key": f"runtime:{spec.name}", "value": f"{spec.version or 'ok'} ({spec.detail})"})
    return info


__all__ = [
    "EXE_NAMES",
    "LUPA_MODULES",
    "LuaRuntime",
    "RunOutcome",
    "RuntimeSpec",
    "describe_environment",
    "discover_runtimes",
    "probe_runtime",
    "runtime_ladder",
]
