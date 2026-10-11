"""Monochrome theme for the Excalibur GUI.

The TZ asks for a strict monochrome look (black / greys / white, no colour
anywhere) rendered with Consolas.  Everything visual lives here so that the
widgets in :mod:`gui.app` stay free of colour literals.

Palette (dark, default)::

    background   #0a0a0a
    surface      #141414
    surface+     #1c1c1c   (hover / selection fill)
    border       #2a2a2a
    text         #e0e0e0
    text dim     #8a8a8a
    accent       #ffffff

A light variant is provided for users who prefer it - it keeps the same
monochrome discipline (pure whites / greys, no hue).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict

MONO_FONTS = ("Consolas", "Cascadia Mono", "DejaVu Sans Mono", "Courier New", "Courier")
UI_FONTS = ("Segoe UI", "Segoe UI Variable", "Inter", "Helvetica", "TkDefaultFont")


@dataclass(frozen=True)
class Palette:
    background: str
    surface: str
    surface_alt: str
    border: str
    text: str
    text_dim: str
    accent: str
    accent_text: str
    selection: str
    ok: str
    warn: str
    error: str

    def as_dict(self) -> Dict[str, str]:
        return {
            "background": self.background,
            "surface": self.surface,
            "surface_alt": self.surface_alt,
            "border": self.border,
            "text": self.text,
            "text_dim": self.text_dim,
            "accent": self.accent,
            "accent_text": self.accent_text,
            "selection": self.selection,
            "ok": self.ok,
            "warn": self.warn,
            "error": self.error,
        }


#: Default dark, strictly monochrome palette from the TZ.
DARK = Palette(
    background="#0a0a0a",
    surface="#141414",
    surface_alt="#1c1c1c",
    border="#2a2a2a",
    text="#e0e0e0",
    text_dim="#8a8a8a",
    accent="#ffffff",
    accent_text="#0a0a0a",
    selection="#2f2f2f",
    ok="#e0e0e0",      # monochrome: status is carried by the glyph, not the hue
    warn="#c8c8c8",
    error="#ffffff",
)

#: Optional light variant - still monochrome.
LIGHT = Palette(
    background="#f4f4f4",
    surface="#ffffff",
    surface_alt="#eaeaea",
    border="#d0d0d0",
    text="#141414",
    text_dim="#6a6a6a",
    accent="#000000",
    accent_text="#ffffff",
    selection="#dcdcdc",
    ok="#141414",
    warn="#3c3c3c",
    error="#000000",
)

#: Glyphs used instead of colour to convey state (monochrome discipline).
GLYPH_OK = "[ok]"
GLYPH_WARN = "[!]"
GLYPH_ERROR = "[x]"
GLYPH_WORK = "[..]"


def pick_font(root, families, size: int, weight: str = "normal"):
    """Return the first installed family, falling back to Tk's default."""
    try:
        from tkinter import font as tkfont

        available = set(tkfont.families(root))
    except Exception:  # pragma: no cover - headless / exotic Tk builds
        available = set()
    for family in families:
        if family in available:
            return (family, size, weight)
    return ("TkFixedFont" if families is MONO_FONTS else "TkDefaultFont", size, weight)


def detect_preference() -> str:
    """Return ``"dark"`` or ``"light"`` for the current session.

    ``darkdetect`` is optional: when it is missing we default to dark, which is
    the palette the TZ specifies.
    """
    try:
        import darkdetect  # type: ignore

        theme = darkdetect.theme()
        if theme and theme.lower() == "light":
            return "light"
    except Exception:
        pass
    return "dark"


def palette_for(name: str) -> Palette:
    return LIGHT if str(name).lower() == "light" else DARK


def apply_theme(root, palette: Palette = DARK, *, scaling: float = 1.0) -> dict:
    """Apply ``palette`` to ``root`` and return the resolved font dict.

    Only ``ttk`` styles are configured here: classic Tk widgets are styled
    explicitly by the app so that the look stays identical on Windows.
    """
    from tkinter import ttk

    ui_size = max(8, int(round(9 * scaling)))
    mono_size = max(8, int(round(9 * scaling)))
    title_size = max(10, int(round(13 * scaling)))
    heading_size = max(9, int(round(10 * scaling)))

    fonts = {
        "mono": pick_font(root, MONO_FONTS, mono_size),
        "mono_small": pick_font(root, MONO_FONTS, max(8, mono_size - 1)),
        "ui": pick_font(root, UI_FONTS, ui_size),
        "ui_bold": pick_font(root, UI_FONTS, ui_size, "bold"),
        "title": pick_font(root, UI_FONTS, title_size, "bold"),
        "heading": pick_font(root, UI_FONTS, heading_size, "bold"),
    }

    style = ttk.Style(root)
    try:
        style.theme_use("clam")  # the only stock theme that respects flat colours
    except Exception:  # pragma: no cover
        pass

    style.configure(".", background=palette.background, foreground=palette.text,
                    fieldbackground=palette.surface, bordercolor=palette.border,
                    focuscolor=palette.accent, font=fonts["ui"])
    style.configure("TFrame", background=palette.background)
    style.configure("Surface.TFrame", background=palette.surface)
    style.configure("TLabel", background=palette.background, foreground=palette.text, font=fonts["ui"])
    style.configure("Dim.TLabel", background=palette.background, foreground=palette.text_dim, font=fonts["ui"])
    style.configure("Title.TLabel", background=palette.background, foreground=palette.accent, font=fonts["title"])
    style.configure("Heading.TLabel", background=palette.background, foreground=palette.text, font=fonts["heading"])
    style.configure("Mono.TLabel", background=palette.background, foreground=palette.text, font=fonts["mono"])
    style.configure("Status.TLabel", background=palette.background, foreground=palette.text_dim, font=fonts["mono_small"])

    style.configure("TButton", background=palette.surface, foreground=palette.text, font=fonts["ui"],
                    bordercolor=palette.border, focusthickness=1, padding=(10, 6), relief="flat")
    style.map("TButton",
              background=[("active", palette.surface_alt), ("disabled", palette.background)],
              foreground=[("disabled", palette.text_dim)],
              bordercolor=[("focus", palette.accent)])
    style.configure("Accent.TButton", background=palette.accent, foreground=palette.accent_text,
                    font=fonts["ui_bold"], bordercolor=palette.accent, padding=(12, 6))
    style.map("Accent.TButton",
              background=[("active", palette.text), ("disabled", palette.border)],
              foreground=[("disabled", palette.text_dim)])

    style.configure("TCheckbutton", background=palette.background, foreground=palette.text, font=fonts["ui"],
                    focuscolor=palette.accent)
    style.map("TCheckbutton", background=[("active", palette.background)])

    style.configure("TProgressbar", background=palette.accent, troughcolor=palette.surface,
                    bordercolor=palette.border, lightcolor=palette.accent, darkcolor=palette.accent,
                    thickness=6)
    style.configure("TSeparator", background=palette.border)
    style.configure("TNotebook", background=palette.background, bordercolor=palette.border, tabmargins=(0, 4, 0, 0))
    style.configure("TNotebook.Tab", background=palette.surface, foreground=palette.text_dim,
                    font=fonts["ui"], padding=(12, 6), bordercolor=palette.border)
    style.map("TNotebook.Tab",
              background=[("selected", palette.background)],
              foreground=[("selected", palette.accent)])
    style.configure("Vertical.TScrollbar", background=palette.surface, troughcolor=palette.background,
                    bordercolor=palette.border, arrowcolor=palette.text_dim, relief="flat")
    style.configure("Horizontal.TScrollbar", background=palette.surface, troughcolor=palette.background,
                    bordercolor=palette.border, arrowcolor=palette.text_dim, relief="flat")
    style.configure("TCombobox", fieldbackground=palette.surface, background=palette.surface,
                    foreground=palette.text, arrowcolor=palette.text_dim, bordercolor=palette.border)
    style.map("TCombobox", fieldbackground=[("readonly", palette.surface)],
              foreground=[("readonly", palette.text)])

    root.configure(background=palette.background)
    return fonts


__all__ = [
    "DARK",
    "GLYPH_ERROR",
    "GLYPH_OK",
    "GLYPH_WARN",
    "GLYPH_WORK",
    "LIGHT",
    "MONO_FONTS",
    "Palette",
    "UI_FONTS",
    "apply_theme",
    "detect_preference",
    "palette_for",
    "pick_font",
]
