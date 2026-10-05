from __future__ import annotations

import math
import tkinter as tk


class AnimatedBorder:
    """A low-profile moving gradient drawn around a frameless Tk window."""

    _STOPS = (
        (0.00, (164, 242, 255)),  # ice blue
        (0.27, (188, 174, 255)),  # soft violet
        (0.52, (246, 248, 255)),  # silver
        (0.76, (139, 224, 241)),  # teal
        (1.00, (164, 242, 255)),
    )

    def __init__(self, root, *, background: str = "#080808", width: float = 2.0):
        self.root = root
        self.line_width = width
        self.phase = 0.0
        self._closed = False
        self._items: list[int] = []
        self._canvas = tk.Canvas(
            root,
            background=background,
            borderwidth=0,
            highlightthickness=0,
            takefocus=False,
        )
        self._canvas.place(x=0, y=0, relwidth=1, relheight=1)
        # Created before the controls, so normal Tk stacking keeps it behind them.
        # Canvas.lower() lowers canvas items and requires a tag or item ID.
        self._canvas.bind("<Configure>", self._rebuild)
        self._rebuild()
        self._animate()

    @staticmethod
    def _rounded_path(width: float, height: float, radius: float, steps: int = 48):
        radius = max(8.0, min(radius, (width - 4) / 2, (height - 4) / 2))
        corners = (
            (width - radius - 1, radius + 1, -90, 0),
            (width - radius - 1, height - radius - 1, 0, 90),
            (radius + 1, height - radius - 1, 90, 180),
            (radius + 1, radius + 1, 180, 270),
        )
        points = []
        for cx, cy, start, end in corners:
            for index in range(steps):
                angle = math.radians(start + (end - start) * index / steps)
                points.append((cx + radius * math.cos(angle), cy + radius * math.sin(angle)))
        return points

    def _rebuild(self, _event=None) -> None:
        if self._closed:
            return
        width = max(40, self._canvas.winfo_width())
        height = max(40, self._canvas.winfo_height())
        points = self._rounded_path(width, height, radius=20)
        self._canvas.delete("animated-outline")
        self._items.clear()
        for index, point in enumerate(points):
            next_point = points[(index + 1) % len(points)]
            item = self._canvas.create_line(
                point[0],
                point[1],
                next_point[0],
                next_point[1],
                fill="#a4f2ff",
                width=self.line_width,
                capstyle="round",
                tags=("animated-outline",),
            )
            self._items.append(item)

    @classmethod
    def _color_at(cls, position: float) -> str:
        position %= 1.0
        for index in range(len(cls._STOPS) - 1):
            left_position, left_color = cls._STOPS[index]
            right_position, right_color = cls._STOPS[index + 1]
            if left_position <= position <= right_position:
                fraction = (position - left_position) / (right_position - left_position)
                channels = tuple(
                    round(left + (right - left) * fraction)
                    for left, right in zip(left_color, right_color)
                )
                return "#%02x%02x%02x" % channels
        return "#a4f2ff"

    def _animate(self) -> None:
        if self._closed:
            return
        count = len(self._items)
        if count:
            for index, item in enumerate(self._items):
                position = (index / count + self.phase) % 1.0
                self._canvas.itemconfigure(item, fill=self._color_at(position))
            self.phase = (self.phase + 0.0065) % 1.0
        try:
            self.root.after(42, self._animate)
        except tk.TclError:
            self._closed = True

    def close(self) -> None:
        self._closed = True
        try:
            self._canvas.destroy()
        except tk.TclError:
            pass
