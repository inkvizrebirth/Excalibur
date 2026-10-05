from __future__ import annotations

import customtkinter as ctk

from gui.theme import BG, BORDER, ERROR, MUTED, NEON, PANEL, RED_BG, TerminalButton


class Controls(ctk.CTkFrame):
    """One primary action and a compact activity/progress readout."""

    def __init__(self, master, *, title_font, body_font, on_destroy):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self._body_font = body_font
        self._busy = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, minsize=132)
        self.grid_rowconfigure(0, weight=1)

        activity = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=6,
            border_width=1,
            border_color=BORDER,
        )
        activity.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        activity.grid_columnconfigure(0, weight=1)
        activity.grid_rowconfigure(1, weight=1)

        self.progress_label = ctk.CTkLabel(
            activity,
            text="READY",
            text_color=MUTED,
            font=ctk.CTkFont(family=body_font.cget("family"), size=14),
            anchor="w",
        )
        self.progress_label.grid(row=0, column=0, sticky="ew", padx=9, pady=(4, 1))
        self.progress = ctk.CTkProgressBar(
            activity,
            height=4,
            corner_radius=2,
            border_width=0,
            fg_color=BG,
            progress_color=NEON,
        )
        self.progress.grid(row=1, column=0, sticky="ew", padx=9, pady=(0, 7))
        self.progress.set(0)

        self.destroy_button = TerminalButton(
            self,
            text="DESTROY",
            command=on_destroy,
            accent=ERROR,
            base_bg=RED_BG,
            base_text=ERROR,
            width=124,
            height=43,
            font=ctk.CTkFont(family=title_font.cget("family"), size=8),
        )
        self.destroy_button.grid(row=0, column=1, sticky="nsew")

    @property
    def busy(self) -> bool:
        return self._busy

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.destroy_button.configure(text="WORKING..." if busy else "DESTROY")
        self.destroy_button.set_enabled(not busy)

    def set_progress(self, percent: float, label: str = "WORKING") -> None:
        value = max(0.0, min(100.0, float(percent)))
        self.progress.set(value / 100.0)
        self.set_status(f"{label.upper()} · {value:.0f}%")

    def set_status(self, text: str, *, error: bool = False) -> None:
        self.progress_label.configure(
            text=str(text).upper()[:72],
            text_color=ERROR if error else MUTED,
        )
