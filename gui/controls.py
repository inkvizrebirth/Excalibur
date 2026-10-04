from __future__ import annotations

import customtkinter as ctk

from gui.theme import (
    BG,
    BORDER,
    MUTED,
    NEON,
    PANEL,
    RED_BG,
    ERROR,
    TerminalButton,
)


class Controls(ctk.CTkFrame):
    def __init__(
        self,
        master,
        *,
        title_font,
        body_font,
        on_destroy,
        on_clear_logs,
        on_open_output,
        on_copy_result,
    ):
        super().__init__(
            master,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
            fg_color=PANEL,
        )
        self._title_font = title_font
        self._body_font = body_font
        self._busy = False

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=28)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(3, 1))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="CONTROLS",
            text_color=NEON,
            font=title_font,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="ONE INPUT  /  ONE OUTPUT",
            text_color=MUTED,
            font=ctk.CTkFont(family=body_font.cget("family"), size=14),
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        actions = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        actions.grid(row=1, column=0, sticky="nsew", padx=10, pady=(0, 4))
        actions.grid_columnconfigure(0, weight=1)
        actions.grid_columnconfigure(1, minsize=184)
        actions.grid_rowconfigure(0, weight=1)

        self.destroy_button = TerminalButton(
            actions,
            text="DESTROY",
            command=on_destroy,
            accent=ERROR,
            base_bg=RED_BG,
            base_text=ERROR,
            width=400,
            height=76,
            font=ctk.CTkFont(family=title_font.cget("family"), size=13),
        )
        self.destroy_button.grid(row=0, column=0, sticky="nsew", padx=(0, 9))

        utility = ctk.CTkFrame(actions, fg_color=PANEL, corner_radius=0)
        utility.grid(row=0, column=1, sticky="nsew")
        utility.grid_columnconfigure(0, weight=1)
        for row in range(3):
            utility.grid_rowconfigure(row, weight=1)
        utility_style = {
            "accent": NEON,
            "base_bg": BG,
            "font": ctk.CTkFont(family=body_font.cget("family"), size=17),
            "height": 29,
        }
        self.clear_button = TerminalButton(
            utility,
            text="CLEAR LOGS",
            command=on_clear_logs,
            **utility_style,
        )
        self.clear_button.grid(row=0, column=0, sticky="ew", pady=(0, 3))
        self.open_button = TerminalButton(
            utility,
            text="OPEN OUTPUT",
            command=on_open_output,
            **utility_style,
        )
        self.open_button.grid(row=1, column=0, sticky="ew", pady=3)
        self.copy_button = TerminalButton(
            utility,
            text="COPY RESULT",
            command=on_copy_result,
            **utility_style,
        )
        self.copy_button.grid(row=2, column=0, sticky="ew", pady=(3, 0))

        progress_row = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0)
        progress_row.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 8))
        progress_row.grid_columnconfigure(0, weight=1)
        self.progress = ctk.CTkProgressBar(
            progress_row,
            height=5,
            corner_radius=0,
            border_width=0,
            fg_color=BG,
            progress_color=NEON,
        )
        self.progress.grid(row=0, column=0, sticky="ew", padx=(0, 12), pady=4)
        self.progress.set(0)
        self.progress_label = ctk.CTkLabel(
            progress_row,
            text="0% / IDLE",
            text_color=MUTED,
            font=ctk.CTkFont(family=body_font.cget("family"), size=14),
            width=126,
            anchor="e",
        )
        self.progress_label.grid(row=0, column=1, sticky="e")

    @property
    def busy(self) -> bool:
        return self._busy

    def set_busy(self, busy: bool) -> None:
        self._busy = busy
        self.destroy_button.configure(text="DESTROYING..." if busy else "DESTROY")
        self.destroy_button.set_enabled(not busy)

    def set_progress(self, percent: float, label: str = "WORKING") -> None:
        value = max(0.0, min(100.0, float(percent)))
        self.progress.set(value / 100.0)
        self.progress_label.configure(text=f"{value:.0f}% / {label.upper()}")
