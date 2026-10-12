"""First-run environment setup.

The TZ requires an EXE that "[installs] Python + UV on the first run and works
offline afterwards", with no external dependencies for the user.  This module
implements that contract:

* everything writable lives in ``%LOCALAPPDATA%/Excalibur`` (:mod:`core.paths`),
  so the EXE itself can sit anywhere, even on a read-only share;
* on the **first** run the optional Python dependencies are installed into
  ``<runtime>/site-packages`` - from the bundled ``wheels/`` folder when it
  exists (fully offline), otherwise from PyPI through a bundled ``uv`` (or
  ``pip`` as a fallback);
* the result is recorded in ``<runtime>/state.json``; on every later run the
  recorded packages are reused and **no network access is attempted**, which is
  what makes the second run work offline;
* the bundled Lua interpreters (``lua/lua51.exe``, ``lua/lua54.exe``,
  ``lua/luajit.exe``) are optional: when they are absent the sandbox falls back
  to the in-process ``lupa`` runtime, and when ``lupa`` is absent too the
  pipeline still runs its static stage.

Nothing here raises: a failure is reported as a note so the GUI can show it.
"""

from __future__ import annotations

import argparse
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import sysconfig
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Sequence, Tuple

from core import paths

MIN_PYTHON = (3, 10)
STATE_VERSION = 1
#: Directory with bundled wheels (build.py fills it) - enables a fully offline first run.
WHEELS_DIRNAME = "wheels"
#: Vendored tooling bundled by build.py (uv.exe, lua51.exe, ...).
VENDOR_DIRNAME = "vendor"
INSTALL_TIMEOUT = 900

ProgressCallback = Callable[[str, str], None]


@dataclass(frozen=True)
class Dependency:
    """One installable Python dependency."""

    name: str
    spec: str = ""
    required: bool = False
    note: str = ""
    module: str = ""

    @property
    def import_name(self) -> str:
        return self.module or self.name.replace("-", "_")

    @property
    def requirement(self) -> str:
        return f"{self.name}{self.spec}"


#: ``lupa`` is the in-process Lua runtime; without it the sandbox needs an
#: external interpreter, so it is *required* unless a vendored Lua exists.
DEPENDENCIES: Tuple[Dependency, ...] = (
    Dependency("lupa", ">=2.0", required=True, note="in-process Lua 5.1/5.4/LuaJIT runtime"),
    Dependency("luaparser", ">=3.0", required=False, note="AST based format detection"),
    Dependency("darkdetect", ">=0.8", required=False, note="follow the OS light/dark preference"),
)

#: Interpreter names the sandbox probes inside ``lua/`` (see core/runtime.py).
LUA_EXECUTABLES = ("lua51.exe", "lua54.exe", "luajit.exe", "lua.exe")


@dataclass
class BootstrapReport:
    """Everything the caller may want to show the user."""

    ok: bool = True
    offline_ready: bool = False
    installed: List[str] = field(default_factory=list)
    reused: List[str] = field(default_factory=list)
    missing: List[str] = field(default_factory=list)
    notes: List[str] = field(default_factory=list)
    detail: Dict[str, object] = field(default_factory=dict)
    elapsed_ms: int = 0

    def as_dict(self) -> dict:
        return {
            "ok": self.ok,
            "offline_ready": self.offline_ready,
            "installed": self.installed,
            "reused": self.reused,
            "missing": self.missing,
            "notes": self.notes,
            "detail": self.detail,
            "elapsed_ms": self.elapsed_ms,
        }

    def text(self) -> str:
        lines = [f"bootstrap: {'ok' if self.ok else 'problems found'}"]
        lines.append(f"offline ready : {'yes' if self.offline_ready else 'no'}")
        if self.installed:
            lines.append("installed     : " + ", ".join(self.installed))
        if self.reused:
            lines.append("reused        : " + ", ".join(self.reused))
        if self.missing:
            lines.append("missing       : " + ", ".join(self.missing))
        for key, value in sorted(self.detail.items()):
            lines.append(f"{key:<14}: {value}")
        for note in self.notes:
            lines.append(f"  - {note}")
        return "\n".join(lines) + "\n"


# --------------------------------------------------------------------------- utils
def _log(progress: Optional[ProgressCallback], stage: str, message: str) -> None:
    if progress:
        try:
            progress(stage, message)
        except Exception:
            pass


def site_packages_dir() -> Path:
    """Where the optional dependencies are installed for the current user."""
    return paths.runtime_dir() / "site-packages"


def state_path() -> Path:
    return paths.runtime_dir() / "state.json"


def read_state() -> dict:
    try:
        return json.loads(state_path().read_text(encoding="utf-8"))
    except Exception:
        return {}


def write_state(state: dict) -> None:
    try:
        paths.ensure_dir(state_path().parent)
        state_path().write_text(json.dumps(state, indent=2, sort_keys=True), encoding="utf-8")
    except Exception:
        pass


def python_tag() -> str:
    return f"{sys.version_info.major}.{sys.version_info.minor}"


def module_available(name: str) -> bool:
    if name in sys.modules:
        return True
    try:
        return importlib.util.find_spec(name) is not None
    except Exception:
        return False


def available_lua_executables() -> List[Path]:
    """Vendored Lua interpreters that ship next to the EXE (if any)."""
    found: List[Path] = []
    for name in LUA_EXECUTABLES:
        for directory in (paths.lua_dir(), paths.resource_root() / VENDOR_DIRNAME / "lua"):
            candidate = directory / name
            if candidate.exists():
                found.append(candidate)
    return found


def find_tool(*names: str) -> Optional[Path]:
    """Locate a bundled tool (``vendor/uv.exe``) or one on ``PATH``."""
    for name in names:
        for directory in (paths.resource_root() / VENDOR_DIRNAME, paths.runtime_dir() / "bin"):
            candidate = directory / name
            if candidate.exists():
                return candidate
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


def wheels_available() -> bool:
    directory = paths.resource_root() / WHEELS_DIRNAME
    return directory.is_dir() and any(directory.glob("*.whl"))


def add_site_packages() -> Path:
    """Make the user site-packages importable (idempotent)."""
    target = site_packages_dir()
    path = str(target)
    if target.is_dir() and path not in sys.path:
        sys.path.insert(0, path)
    return target


# --------------------------------------------------------------------------- checks
def check_python() -> Tuple[bool, str]:
    if sys.version_info < MIN_PYTHON:
        return False, (f"Python {MIN_PYTHON[0]}.{MIN_PYTHON[1]}+ is required, "
                       f"found {sys.version.split()[0]}")
    return True, f"Python {sys.version.split()[0]} ({sysconfig.get_platform()})"


def check_resources() -> Tuple[bool, List[str], List[str]]:
    """Verify the Lua runner files that every run needs are present."""
    missing: List[str] = []
    notes: List[str] = []
    lua_dir = paths.core_dir() / "lua"
    for name in ("runner.lua", "hooks.lua", "roblox_stubs.lua", "lua51_compat.lua"):
        if not (lua_dir / name).exists():
            missing.append(f"core/lua/{name}")
    if missing:
        notes.append("bundled Lua runner files are missing; the sandbox stage cannot run")
    return (not missing), missing, notes


def check_dependencies() -> Tuple[List[Dependency], List[Dependency]]:
    """Split the dependency list into ``(available, missing)``."""
    add_site_packages()
    available: List[Dependency] = []
    missing: List[Dependency] = []
    for dependency in DEPENDENCIES:
        (available if module_available(dependency.import_name) else missing).append(dependency)
    return available, missing


# --------------------------------------------------------------------------- install
def _install_command(requirements: Sequence[str], target: Path, *, offline: bool) -> List[str]:
    uv = find_tool("uv.exe", "uv")
    wheels = paths.resource_root() / WHEELS_DIRNAME
    if uv is not None:
        command = [str(uv), "pip", "install", "--python", sys.executable, "--target", str(target)]
        if offline and wheels.is_dir():
            command += ["--no-index", "--find-links", str(wheels)]
        else:
            command += ["--find-links", str(wheels)] if wheels.is_dir() else []
        command += list(requirements)
        return command
    command = [sys.executable, "-m", "pip", "install", "--upgrade", "--target", str(target),
               "--disable-pip-version-check"]
    if offline and wheels.is_dir():
        command += ["--no-index", "--find-links", str(wheels)]
    elif wheels.is_dir():
        command += ["--find-links", str(wheels)]
    command += list(requirements)
    return command


def install_dependencies(
    requirements: Sequence[str],
    *,
    offline: bool = False,
    progress: Optional[ProgressCallback] = None,
) -> Tuple[bool, str]:
    """Install ``requirements`` into the user site-packages.  Never raises."""
    target = paths.ensure_dir(site_packages_dir())
    command = _install_command(requirements, target, offline=offline)
    _log(progress, "deps", "installing " + ", ".join(requirements))
    env = dict(os.environ)
    env.setdefault("PYTHONNOUSERSITE", "1")
    env.setdefault("PIP_NO_INPUT", "1")
    try:
        completed = subprocess.run(
            command, capture_output=True, text=True, timeout=INSTALL_TIMEOUT, env=env,
            creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0,
        )
    except FileNotFoundError as exc:
        return False, f"installer not found: {exc}"
    except subprocess.TimeoutExpired:
        return False, f"installer timed out after {INSTALL_TIMEOUT}s"
    except Exception as exc:  # pragma: no cover - defensive
        return False, f"{type(exc).__name__}: {exc}"
    output = (completed.stdout or "") + (completed.stderr or "")
    if completed.returncode != 0:
        tail = "\n".join(output.strip().splitlines()[-12:])
        return False, f"installer exited with {completed.returncode}:\n{tail}"
    return True, output.strip().splitlines()[-1] if output.strip() else "installed"


def ensure_environment(
    *,
    progress: Optional[ProgressCallback] = None,
    allow_download: Optional[bool] = None,
    force: bool = False,
) -> BootstrapReport:
    """Prepare the runtime.  Safe to call on every start; does real work once."""
    started = time.time()
    report = BootstrapReport()
    state = read_state()

    ok, detail = check_python()
    report.detail["python"] = detail
    if not ok:
        report.ok = False
        report.notes.append(detail)

    resources_ok, missing_files, notes = check_resources()
    report.missing.extend(missing_files)
    report.notes.extend(notes)

    # writable locations
    for directory in (paths.app_data_dir(), paths.runtime_dir(), paths.logs_dir()):
        try:
            paths.ensure_dir(directory)
        except Exception as exc:
            report.ok = False
            report.notes.append(f"cannot create {directory}: {exc}")

    lua_executables = available_lua_executables()
    report.detail["lua_executables"] = [str(p) for p in lua_executables] or "none (using lupa)"
    report.detail["site_packages"] = str(site_packages_dir())

    available, missing = check_dependencies()
    report.reused = [d.requirement for d in available]
    report.detail["bundled_deps"] = ", ".join(d.name for d in available) or "none"

    download_allowed = allow_download if allow_download is not None else (not state.get("installed_once", False))
    requirements = [d.requirement for d in missing]

    if requirements and (force or download_allowed):
        offline = wheels_available()
        _log(progress, "deps", f"first run: {len(requirements)} package(s) to install")
        success, message = install_dependencies(requirements, offline=offline, progress=progress)
        if success:
            report.installed.extend(requirements)
            add_site_packages()
            still_missing = [d.requirement for d in missing if not module_available(d.import_name)]
            if still_missing:
                report.notes.append("installed but not importable: " + ", ".join(still_missing))
            # refresh the split
            available, missing = check_dependencies()
            report.reused = [d.requirement for d in available]
        else:
            report.notes.append(f"dependency install failed: {message}")
            report.missing.extend(requirements)
    elif requirements:
        report.missing.extend(requirements)
        report.notes.append(
            "optional packages are missing and downloads are disabled for this run; "
            "use the 'setup' button in the GUI (or bootstrap.py --install) to fetch them"
        )

    requirements_missing = [d.requirement for d in missing]
    if requirements_missing:
        required_missing = [d.requirement for d in missing if d.required and not lua_executables]
        if required_missing:
            report.ok = False
            report.notes.append("no Lua runtime available: " + ", ".join(required_missing))
    report.detail["missing_optional"] = ", ".join(requirements_missing) or "none"

    # Cache the outcome so later runs can go offline.
    state.update({
        "state_version": STATE_VERSION,
        "python": python_tag(),
        "platform": sysconfig.get_platform(),
        "installed_once": bool(report.installed) or bool(state.get("installed_once")),
        "last_installed": report.installed,
        "requirements": [d.requirement for d in DEPENDENCIES],
        "updated": time.strftime("%Y-%m-%dT%H:%M:%S"),
    })
    write_state(state)

    try:
        from core.config import DEFAULT_RUNTIMES
        from core.runtime import discover_runtimes

        specs = discover_runtimes(DEFAULT_RUNTIMES)
        # the same name can appear twice (the lupa wheel *and* a bundled .exe):
        # show the kind as well, otherwise the list reads like a duplicate
        report.detail["runtimes"] = ", ".join(
            s.name if len({x.name for x in specs}) == len(specs) else f"{s.name} ({s.kind})"
            for s in specs
        ) or "none"
        if not specs:
            report.ok = False
            report.notes.append("no Lua runtime could be discovered (bundled lua/*.exe or lupa)")
    except Exception as exc:
        report.detail["runtimes"] = f"probe failed: {exc}"

    required_missing_now = [d.requirement for d in missing if d.required and not lua_executables]
    report.offline_ready = bool(
        not required_missing_now and resources_ok and report.detail.get("runtimes") not in (None, "none")
    )
    report.elapsed_ms = int((time.time() - started) * 1000)
    _log(progress, "deps", "environment ready" if report.ok else "environment has problems")
    return report


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Excalibur first-run setup")
    parser.add_argument("--check", action="store_true", help="check only, install nothing")
    parser.add_argument("--install", action="store_true", help="force dependency installation")
    parser.add_argument("--offline", action="store_true", help="never touch the network")
    parser.add_argument("--json", action="store_true", help="machine readable output")
    args = parser.parse_args(argv)

    if args.check:
        ok, detail = check_python()
        resources_ok, missing_files, _ = check_resources()
        available, missing = check_dependencies()
        required_ok = not [d for d in missing if d.required] or bool(available_lua_executables())
        report = BootstrapReport(
            ok=ok and resources_ok and required_ok,
            offline_ready=resources_ok and required_ok,
            reused=[d.requirement for d in available],
            missing=[d.requirement for d in missing] + missing_files,
            detail={"python": detail, "lua_executables": [str(p) for p in available_lua_executables()] or "none"},
        )
    else:
        allow = False if args.offline else True
        report = ensure_environment(allow_download=allow, force=args.install)

    if args.json:
        print(json.dumps(report.as_dict(), indent=2))
    else:
        print(report.text(), end="")
    return 0 if report.ok else 1


if __name__ == "__main__":  # pragma: no cover - manual entry point
    raise SystemExit(main())
