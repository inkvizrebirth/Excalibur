from __future__ import annotations

import os
import sys
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1]
IS_FROZEN = bool(getattr(sys, "frozen", False))
RESOURCE_ROOT = Path(getattr(sys, "_MEIPASS", SOURCE_ROOT)).resolve()


def _default_data_root() -> Path:
    override = os.environ.get("PROTEZ_DATA_DIR")
    if override:
        return Path(override).expanduser().resolve()
    if not IS_FROZEN:
        return SOURCE_ROOT

    if os.name == "nt":
        base = Path(os.environ.get("LOCALAPPDATA", Path.home() / "AppData" / "Local"))
        return base / "Protez"
    if sys.platform == "darwin":
        return Path.home() / "Library" / "Application Support" / "Protez"
    base = Path(os.environ.get("XDG_DATA_HOME", Path.home() / ".local" / "share"))
    return base / "Protez"


DATA_ROOT = _default_data_root()
OUTPUT_DIR = DATA_ROOT / "output"
LOGS_DIR = DATA_ROOT / "logs"
TOOLS_DIR = DATA_ROOT / "tools" if IS_FROZEN else SOURCE_ROOT / "tools"
PACKAGED_TOOLS_DIR = RESOURCE_ROOT / "tools"
LICENSES_DIR = RESOURCE_ROOT / "licenses"
ICON_PATH = RESOURCE_ROOT / "assets" / "icons" / "protez.ico"
