"""Pixel-art theme: palette, metrics and font stacks.

The interface is built from bitmap text and 1px frames on a dark grid, so the
theme file only carries colours, spacings and the monospace stacks used for
code and logs.
"""

from __future__ import annotations

try:  # Tk is optional for headless tooling (preview rendering, tests)
    import tkinter.font as tkfont
except Exception:  # noqa: BLE001 - no display or no Tk build
    tkfont = None  # type: ignore[assignment]

# ---------------------------------------------------------------------------
# Palette — deep slate grid, mint accent, amber warning.
# ---------------------------------------------------------------------------

BG = "#0a0d12"
BG_SUNKEN = "#070a10"
PANEL = "#121822"
PANEL_ALT = "#161e2a"
PANEL_RAISED = "#1b2534"
BORDER = "#26313f"
BORDER_BRIGHT = "#3a4c63"
GRID_LINE = "#18202c"

TEXT = "#e6eefc"
TEXT_DIM = "#9fb0c7"
MUTED = "#66788f"
DISABLED = "#465468"

ACCENT = "#3fe0a5"
ACCENT_DARK = "#187a58"
ACCENT_SOFT = "#123a2e"
CYAN = "#57c8ff"
CYAN_SOFT = "#12303f"
WARN = "#ffc463"
WARN_SOFT = "#3a2f14"
ERROR = "#ff6b81"
ERROR_SOFT = "#3a1a22"
SELECT = "#1d3247"
SELECT_ALT = "#16283a"

# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

PIXEL = 1
FRAME_PAD = 2
PANEL_PAD = 10
ROW_GAP = 8
SECTION_GAP = 12
MIN_WIDTH = 720
MIN_HEIGHT = 520
DEFAULT_WIDTH = 820
DEFAULT_HEIGHT = 620

# ---------------------------------------------------------------------------
# Fonts
# ---------------------------------------------------------------------------

_CODE_CANDIDATES = (
    "Cascadia Mono",
    "JetBrains Mono",
    "Consolas",
    "DejaVu Sans Mono",
    "Menlo",
    "Courier New",
    "TkFixedFont",
)
_UI_CANDIDATES = (
    "Segoe UI",
    "Inter",
    "DejaVu Sans",
    "Helvetica",
    "TkDefaultFont",
)


def _pick_family(candidates: tuple[str, ...]) -> str:
    if tkfont is None:
        return candidates[-1]
    try:
        available = {name.lower() for name in tkfont.families()}
    except Exception:
        return candidates[-1]
    for name in candidates:
        if name.lower() in available:
            return name
    return candidates[-1]


def code_family() -> str:
    return _pick_family(_CODE_CANDIDATES)


def ui_family() -> str:
    return _pick_family(_UI_CANDIDATES)


def font(family: str, size: int, *, bold: bool = False) -> tuple:
    return (family, size, "bold") if bold else (family, size)


# ---------------------------------------------------------------------------
# Log levels
# ---------------------------------------------------------------------------

LEVEL_COLORS = {
    "DEBUG": MUTED,
    "INFO": TEXT_DIM,
    "WARNING": WARN,
    "ERROR": ERROR,
    "CRITICAL": ERROR,
}

# ---------------------------------------------------------------------------
# Syntax colours (viewer)
# ---------------------------------------------------------------------------

SYNTAX_COLORS = {
    "keyword": "#ff8ec7",
    "constant": "#ffd479",
    "builtin": "#7fe1ff",
    "standard": "#a9c2ff",
    "executor": "#3fe0a5",
    "string": "#b7f5c9",
    "number": "#ffc463",
    "comment": "#5d6c81",
    "operator": "#8fa3bd",
    "function": "#ffe08a",
    "property": "#c9d6ea",
    "label": "#e6eefc",
    "search": "#2a4a63",
    "active_match": "#3fe0a5",
}
