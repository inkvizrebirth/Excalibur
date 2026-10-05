from __future__ import annotations

import tkinter as tk


class ProtezLogo(tk.Canvas):
    """Small hand-drawn P-mark used as Protez's compact window icon."""

    def __init__(self, master, *, size: int = 36, background: str = "#101114"):
        super().__init__(
            master,
            width=size,
            height=size,
            background=background,
            borderwidth=0,
            highlightthickness=0,
            takefocus=False,
        )
        self._size = size
        self.bind("<Configure>", self._draw)
        self._draw()

    def _draw(self, _event=None) -> None:
        size = max(24, min(self.winfo_width(), self.winfo_height(), self._size))
        self.delete("logo")
        inset = size * 0.08
        self.create_rounded_rectangle(
            inset,
            inset,
            size - inset,
            size - inset,
            radius=size * 0.25,
            fill="#15171c",
            outline="#343741",
            width=1,
            tags=("logo",),
        )
        # A cut-corner P monogram, built from a single bright stroke.
        x0, y0 = size * 0.31, size * 0.72
        self.create_line(
            x0,
            y0,
            x0,
            size * 0.28,
            size * 0.58,
            size * 0.28,
            size * 0.70,
            size * 0.40,
            size * 0.70,
            size * 0.49,
            size * 0.60,
            size * 0.58,
            x0,
            size * 0.58,
            fill="#f7f8fc",
            width=max(2, round(size * 0.075)),
            capstyle="round",
            joinstyle="round",
            tags=("logo",),
        )
        self.create_line(
            size * 0.57,
            size * 0.61,
            size * 0.71,
            size * 0.75,
            fill="#a4eaff",
            width=max(2, round(size * 0.065)),
            capstyle="round",
            tags=("logo",),
        )

    def create_rounded_rectangle(self, x1, y1, x2, y2, *, radius, **kwargs):
        radius = max(0, min(radius, (x2 - x1) / 2, (y2 - y1) / 2))
        points = [
            x1 + radius, y1,
            x2 - radius, y1,
            x2, y1,
            x2, y1 + radius,
            x2, y2 - radius,
            x2, y2,
            x2 - radius, y2,
            x1 + radius, y2,
            x1, y2,
            x1, y2 - radius,
            x1, y1 + radius,
            x1, y1,
        ]
        return self.create_polygon(points, smooth=True, splinesteps=12, **kwargs)
