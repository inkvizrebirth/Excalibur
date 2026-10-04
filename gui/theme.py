from __future__ import annotations

import customtkinter as ctk

BG = "#0a0a0a"
PANEL = "#111111"
INPUT_BG = "#050706"
BORDER = "#26312b"
NEON = "#00ff88"
ACID = "#39ff14"
TEXT = "#d4e7dc"
MUTED = "#78857d"
WARN = "#ffd166"
ERROR = "#ff3355"
RED_BG = "#330000"


class TerminalButton(ctk.CTkButton):
    """Square, bordered button with an instant foreground/background inversion."""

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
            border_color=accent,
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
        elif self._active or hover:
            background = self._accent
            foreground = BG
        else:
            background = self._base_bg
            foreground = self._base_text
        self.configure(
            fg_color=background,
            text_color=foreground,
            border_color=self._accent,
        )

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
