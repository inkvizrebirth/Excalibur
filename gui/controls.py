from __future__ import annotations

import logging

import customtkinter as ctk

from gui.theme import ACCENT, BG, BORDER, ERROR, MUTED, NEON, PANEL, RED_BG


class Controls(ctk.CTkFrame):
    """Primary run action with visible state and a compact progress meter."""

    def __init__(self, master, *, title_font, body_font, on_destroy):
        super().__init__(master, fg_color="transparent", corner_radius=0)
        self._busy = False
        self._on_destroy = on_destroy
        self._logger = logging.getLogger("protez")

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, minsize=118)
        self.grid_rowconfigure(0, weight=1)

        activity = ctk.CTkFrame(
            self,
            fg_color=PANEL,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
        )
        activity.grid(row=0, column=0, sticky="nsew", padx=(0, 7))
        activity.grid_columnconfigure(0, weight=1)
        activity.grid_rowconfigure(1, weight=1)

        self.progress_label = ctk.CTkLabel(
            activity,
            text="READY",
            text_color=MUTED,
            font=ctk.CTkFont(family=body_font.cget("family"), size=10, weight="bold"),
            anchor="w",
        )
        self.progress_label.grid(row=0, column=0, sticky="ew", padx=8, pady=(3, 1))
        self.progress = ctk.CTkProgressBar(
            activity,
            height=4,
            corner_radius=0,
            border_width=0,
            fg_color=BG,
            progress_color=ACCENT,
        )
        self.progress.grid(row=1, column=0, sticky="ew", padx=8, pady=(0, 5))
        self.progress.set(0)

        self.destroy_button = ctk.CTkButton(
            self,
            text="DESTROY",
            command=self._activate,
            width=108,
            height=37,
            corner_radius=0,
            border_width=0,
            fg_color=RED_BG,
            hover_color="#dce4f0",
            text_color="#090a0d",
            font=ctk.CTkFont(family=body_font.cget("family"), size=10, weight="bold"),
            state="normal",
        )
        self.destroy_button.grid(row=0, column=1, sticky="nsew")

    @property
    def busy(self) -> bool:
        return self._busy

    def _activate(self) -> None:
        if self._busy:
            return
        self._logger.info("DESTROY action clicked")
        try:
            self._on_destroy()
        except Exception:
            self._logger.exception("The DESTROY action could not be started")
            self.set_status("COULD NOT START · SEE ACTIVITY", error=True)

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.destroy_button.configure(
            text="PROCESSING…" if busy else "DESTROY",
            state="disabled" if busy else "normal",
            fg_color="#2a2d34" if busy else RED_BG,
            text_color=MUTED if busy else "#090a0d",
        )

    def set_progress(self, percent: float, label: str = "WORKING") -> None:
        value = max(0.0, min(100.0, float(percent)))
        self.progress.set(value / 100.0)
        self.set_status(f"{label.upper()} · {value:.0f}%")

    def set_status(self, text: str, *, error: bool = False) -> None:
        self.progress_label.configure(
            text=str(text).upper()[:72],
            text_color=ERROR if error else NEON,
        )
