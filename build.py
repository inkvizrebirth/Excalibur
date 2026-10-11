"""Build and packaging helper.

Commands::

    python build.py doctor          show what this machine can build
    python build.py dev             run the GUI from source through uv (fast loop)
    python build.py wheels          collect wheels into wheels/ for an offline first run
    python build.py fetch-lua       place a Lua 5.1 interpreter into lua/ (optional)
    python build.py exe             PyInstaller --onefile --windowed build
    python build.py all             wheels + exe

The EXE is built so that:

* ``core/lua/*.lua``, ``assets/`` and (when present) ``lua/``, ``vendor/`` and
  ``wheels/`` are embedded with ``--add-data``;
* ``main.py`` is the entry point and the GUI is created by ``gui.app``;
* the result is checked against the 80 MB budget from the TZ and the size
  report is printed (one-file builds unpack into ``%TEMP%/_MEIxxxx`` at runtime).
"""

from __future__ import annotations

import argparse
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence

ROOT = Path(__file__).resolve().parent
APP_NAME = "Excalibur"
ENTRY = ROOT / "main.py"
DIST = ROOT / "dist"
BUILD = ROOT / "build"
SIZE_BUDGET_MB = 80.0
WORK_DIR = ROOT / ".pyinstaller"

#: Data directories embedded into the EXE: source path -> destination name.
DATA_TREES = ("core/lua", "assets", "lua", "vendor", "wheels", "docs")
#: Modules that must be collected explicitly (lupa ships compiled wheels).
HIDDEN_IMPORTS = ("lupa", "lupa.lua51", "lupa.lua54", "lupa.luajit21", "tkinter", "tkinter.ttk")
#: Big packages we never need.
EXCLUDES = ("numpy", "pandas", "matplotlib", "scipy", "PyQt5", "PyQt6", "PySide2", "PySide6",
            "IPython", "notebook", "pytest", "setuptools", "pip", "wheel")


def log(message: str) -> None:
    print(f"[build] {message}", flush=True)


def run(command: Sequence[str], *, check: bool = True, timeout: Optional[int] = None) -> int:
    log("$ " + " ".join(str(c) for c in command))
    try:
        completed = subprocess.run(list(map(str, command)), cwd=ROOT, timeout=timeout)
    except FileNotFoundError as exc:
        log(f"command not found: {exc}")
        return 127
    except subprocess.TimeoutExpired:
        log("command timed out")
        return 124
    if check and completed.returncode != 0:
        raise SystemExit(f"command failed with {completed.returncode}")
    return completed.returncode


def have(module: str) -> bool:
    try:
        import importlib.util

        return importlib.util.find_spec(module) is not None
    except Exception:
        return False


def tool(*names: str) -> Optional[Path]:
    for name in names:
        found = shutil.which(name)
        if found:
            return Path(found)
    return None


# --------------------------------------------------------------------------- doctor
def doctor() -> int:
    log(f"python      : {sys.version.split()[0]} ({sys.executable})")
    log(f"platform    : {sys.platform}")
    log(f"uv          : {tool('uv', 'uv.exe') or 'not found'}")
    log(f"pyinstaller : {(tool('pyinstaller') or 'module ' + str(have('pyinstaller')))}")
    for module in ("lupa", "luaparser", "darkdetect", "tkinter", "PIL"):
        log(f"{module:<11} : {'yes' if have(module) else 'no'}")
    for directory in DATA_TREES:
        path = ROOT / directory
        files = list(path.rglob("*")) if path.exists() else []
        log(f"{directory:<11} : {len([f for f in files if f.is_file()])} file(s)")
    return 0


# --------------------------------------------------------------------------- dev loop
def dev(extra: Sequence[str]) -> int:
    """Fast source loop: ``uv run python main.py`` when uv is available."""
    uv = tool("uv", "uv.exe")
    if uv is not None:
        return run([uv, "run", "--python", "3.12", "python", str(ENTRY), *extra], check=False)
    return run([sys.executable, str(ENTRY), *extra], check=False)


# --------------------------------------------------------------------------- wheels
def wheels() -> int:
    """Download runtime wheels so the first run can work without the network."""
    uv = tool("uv", "uv.exe")
    target = ROOT / "wheels"
    target.mkdir(exist_ok=True)
    requirements = ["lupa>=2.0", "luaparser>=3.0", "darkdetect>=0.8"]
    if uv is not None:
        return run([uv, "pip", "download", "--dest", str(target), "--python-version", "3.12",
                    *requirements], check=False)
    return run([sys.executable, "-m", "pip", "download", "--dest", str(target),
                "--only-binary", ":all:", "--python-version", "3.12", *requirements], check=False)


# --------------------------------------------------------------------------- lua
LUA_SOURCES = {
    "lua51": "https://www.lua.org/ftp/lua-5.1.5.tar.gz",
}


def fetch_lua() -> int:
    """Explain how to vendor a Lua 5.1 interpreter (optional, lupa is the default)."""
    log("the sandbox prefers an external Lua 5.1 because that is the interpreter")
    log("Roblox-era scripts target; without it the bundled lupa runtime is used")
    target = ROOT / "lua"
    target.mkdir(exist_ok=True)
    existing = [p.name for p in target.glob("lua*")]
    if existing:
        log(f"already present: {', '.join(existing)}")
        return 0
    log("")
    log("option A (recommended, reproducible): build Lua 5.1 from source")
    log(f"  1) download {LUA_SOURCES['lua51']}")
    log("  2) build it with MSVC/mingw (Windows) or cc (linux) and copy the binary to lua/lua51.exe")
    log("option B: copy an existing interpreter (lua5.1 / lua51 / luajit) into ./lua/")
    log("option C: do nothing - lupa (pip wheel, ships Lua 5.1 + 5.4 + LuaJIT) is used instead")
    return 0


# --------------------------------------------------------------------------- exe
def _data_args() -> List[str]:
    args: List[str] = []
    separator = ";" if os.name == "nt" else ":"
    for tree in DATA_TREES:
        source = ROOT / tree
        if not source.exists():
            continue
        if not any(source.rglob("*")):
            continue
        destination = tree.replace("/", os.sep)
        args += ["--add-data", f"{source}{separator}{destination}"]
    return args


def build_exe(*, clean: bool = False, console: bool = False) -> int:
    if not have("PyInstaller") and not have("pyinstaller"):
        log("PyInstaller is not installed: python -m pip install pyinstaller")
        return 2
    if clean:
        shutil.rmtree(DIST, ignore_errors=True)
        shutil.rmtree(BUILD, ignore_errors=True)

    icon = ROOT / "assets" / "icon.ico"
    command: List[str] = [
        sys.executable, "-m", "PyInstaller",
        "--noconfirm", "--clean",
        "--onefile",
        "--name", APP_NAME,
        "--distpath", str(DIST),
        "--workpath", str(BUILD),
        "--specpath", str(WORK_DIR),
        # the GUI must not flash a console window
        "--console" if console else "--windowed",
        "--noupx",
    ] + _data_args()
    if icon.exists():
        command += ["--icon", str(icon)]
    for name in HIDDEN_IMPORTS:
        command += ["--hidden-import", name]
    for name in EXCLUDES:
        command += ["--exclude-module", name]
    command += [str(ENTRY)]

    started = time.time()
    code = run(command, check=False)
    if code != 0:
        log(f"PyInstaller failed with exit code {code}")
        return code

    exe = DIST / (APP_NAME + (".exe" if os.name == "nt" else ""))
    if not exe.exists():
        log(f"expected {exe} to exist")
        return 3
    size_mb = exe.stat().st_size / (1024 * 1024)
    log(f"built {exe} in {time.time() - started:.1f}s - {size_mb:.1f} MB")
    if size_mb > SIZE_BUDGET_MB:
        log(f"WARNING: {size_mb:.1f} MB exceeds the {SIZE_BUDGET_MB:.0f} MB budget from the TZ")
        log("         exclusions are already applied; the biggest contributors are lupa's Lua")
        log("         libraries - drop the ones the sandbox does not need in HIDDEN_IMPORTS")
        return 4
    log("size is inside the 80 MB budget")
    return 0


def build_all() -> int:
    wheels()
    return build_exe(clean=True)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description="Excalibur build helper")
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("doctor", help="report the local toolchain")
    dev_parser = sub.add_parser("dev", help="run the GUI from source")
    dev_parser.add_argument("args", nargs="*", help="extra arguments for main.py")
    sub.add_parser("wheels", help="collect wheels for an offline first run")
    sub.add_parser("fetch-lua", help="instructions for vendoring Lua 5.1")
    exe_parser = sub.add_parser("exe", help="build the one-file EXE")
    exe_parser.add_argument("--no-clean", action="store_true", help="keep previous build output")
    exe_parser.add_argument("--console", action="store_true", help="keep the console for debugging")
    sub.add_parser("all", help="wheels + EXE")
    args = parser.parse_args(argv)

    if args.command == "doctor":
        return doctor()
    if args.command == "dev":
        return dev(args.args)
    if args.command == "wheels":
        return wheels()
    if args.command == "fetch-lua":
        return fetch_lua()
    if args.command == "exe":
        return build_exe(clean=not args.no_clean, console=args.console)
    if args.command == "all":
        return build_all()
    parser.print_help()
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
