from __future__ import annotations

import customtkinter as ctk

# Near-black surfaces with restrained icy accents. The animated outline carries
# the color; controls and code remain high-contrast and calm.
BG = "#08090b"
PANEL = "#111318"
INPUT_BG = "#07080a"
BORDER = "#282c34"
NEON = "#f5f7fb"
ACID = "#ffffff"
TEXT = "#f7f8fc"
MUTED = "#a7adba"
WARN = "#f4cb7a"
ERROR = "#ff8792"
RED_BG = "#f2f4f8"
ACCENT = "#a4eaff"


class TerminalButton(ctk.CTkButton):
    """Square monochrome utility button with a clear inverse hover state."""

    def __init__(
        self,
        master,
        *,
        accent: str = NEON,
        base_bg: str = BG,
        base_text: str | None = None,
        active: bool = False,
        **kwargs,
    ):
        self._accent = accent
        self._base_bg = base_bg
        self._base_text = base_text or accent
        self._active = active
        self._enabled = True
        super().__init__(
            master,
            corner_radius=0,
            border_width=1,
            border_color=BORDER if not active else accent,
            fg_color=accent if active else base_bg,
            text_color=BG if active else self._base_text,
            hover=False,
            **kwargs,
        )
        self.bind("<Enter>", self._on_enter, add="+")
        self.bind("<Leave>", self._on_leave, add="+")
        self._apply_palette(hover=False)

    def _apply_palette(self, *, hover: bool) -> None:
        if not self._enabled:
            background = self._base_bg
            foreground = MUTED
            border = BORDER
        elif self._active or hover:
            background = self._accent
            foreground = BG
            border = self._accent
        else:
            background = self._base_bg
            foreground = self._base_text
            border = BORDER
        self.configure(fg_color=background, text_color=foreground, border_color=border)

    def _on_enter(self, _event=None) -> None:
        if self._enabled:
            self._apply_palette(hover=True)

    def _on_leave(self, _event=None) -> None:
        self._apply_palette(hover=False)

    def set_active(self, active: bool) -> None:
        self._active = active
        self._apply_palette(hover=False)

    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.configure(state="normal" if enabled else "disabled")
        self._apply_palette(hover=False)
