"""Filesystem layout helpers.

Works in three environments:

* development checkout            (``<repo>/core/paths.py``)
* PyInstaller one-file/one-dir    (``sys._MEIPASS``)
* installed runtime               (``%LOCALAPPDATA%/Excalibur/runtime/...``)

All writable state (logs, dumps, downloaded runtimes) lives outside the
executable so the EXE itself stays read-only and can live on a network share.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

APP_NAME = "Excalibur"


def is_frozen() -> bool:
    """True when running from a PyInstaller bundle."""
    return bool(getattr(sys, "frozen", False))


def resource_root() -> Path:
    """Directory that contains bundled resources (``core``, ``lua``, ``assets``)."""
    if is_frozen():
        base = getattr(sys, "_MEIPASS", None)
        if base:
            return Path(base)
        return Path(sys.executable).parent
    return Path(__file__).resolve().parent.parent


def core_dir() -> Path:
    return resource_root() / "core"


def lua_dir() -> Path:
    """Directory holding the bundled Lua interpreter (may not exist in dev)."""
    return resource_root() / "lua"


def gui_dir() -> Path:
    return resource_root() / "gui"


def assets_dir() -> Path:
    return resource_root() / "assets"


def app_data_dir() -> Path:
    """Per-user writable directory (``%LOCALAPPDATA%/Excalibur`` on Windows)."""
    override = os.environ.get("EXCALIBUR_HOME")
    if override:
        return Path(override)
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or os.environ.get("APPDATA")
        if base:
            return Path(base) / APP_NAME
    return Path.home() / f".{APP_NAME.lower()}"


def runtime_dir() -> Path:
    """Where the bootstrap installs Python/uv (see :mod:`bootstrap`)."""
    return app_data_dir() / "runtime"


def logs_dir() -> Path:
    """Default artifact directory (dumps, logs, reports)."""
    override = os.environ.get("EXCALIBUR_LOGS")
    if override:
        return Path(override)
    if not is_frozen():
        return resource_root() / "logs"
    return app_data_dir() / "logs"


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path
