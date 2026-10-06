from __future__ import annotations

import tkinter as tk


from gui.logo_art import _BORDER, _SWORD


class ProtezLogo(tk.Canvas):
    """Compact pixel sword mark shared with the Windows application icon."""

    def __init__(self, master, *, size: int = 32, background: str = "#111318"):
        super().__init__(
            master,
            width=size,
            height=size,
            background=background,
            borderwidth=0,
            highlightthickness=0,
            takefocus=False,
        )
        self.bind("<Configure>", self._draw)
        self._draw()

    def _draw(self, _event=None) -> None:
        width = max(16, self.winfo_width())
        height = max(16, self.winfo_height())
        cell = min(width, height) / 16
        left = (width - cell * 16) / 2
        top = (height - cell * 16) / 2
        self.delete("logo")
        self.create_rectangle(
            left + cell,
            top + cell,
            left + cell * 15,
            top + cell * 15,
            fill="#070a0f",
            outline="",
            tags=("logo",),
        )
        for x, y in _BORDER:
            self._pixel(left, top, cell, x, y, "#23a4ff")
        for y, row in enumerate(_SWORD):
            for x, pixel in enumerate(row):
                if pixel == "#":
                    self._pixel(left, top, cell, x, y, "#f9fcff")

    def _pixel(self, left: float, top: float, cell: float, x: int, y: int, color: str) -> None:
        self.create_rectangle(
            left + x * cell,
            top + y * cell,
            left + (x + 1) * cell,
            top + (y + 1) * cell,
            fill=color,
            outline="",
            tags=("logo",),
        )
