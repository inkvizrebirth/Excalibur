"""Pixel-art Tk widgets drawn on canvases.

Everything here is plain :mod:`tkinter` — no third-party theme engine — so the
interface renders identically in the frozen Windows build.  Chrome is drawn
with 1px frames and the bitmap font from :mod:`gui.pixelfont`, while real text
entry and code display use Tk widgets wrapped in pixel frames.
"""

from __future__ import annotations

import tkinter as tk
from typing import Callable, Iterable, Sequence

from gui import theme
from gui.pixelfont import color_rows, photo_data, text_size

__all__ = [
    "FontCache",
    "PixelPanel",
    "PixelLabel",
    "PixelButton",
    "PixelProgress",
    "PixelToggle",
    "PixelDropdown",
    "PixelEntry",
    "PixelTextArea",
    "CodeText",
    "Scrollbar",
]


class FontCache:
    """Cache bitmap-font renders as ``PhotoImage`` objects."""

    def __init__(self) -> None:
        self._images: dict[tuple[str, str, str, int], tk.PhotoImage] = {}

    def image(
        self,
        text: str,
        *,
        ink: str,
        background: str,
        scale: int = 2,
    ) -> tk.PhotoImage:
        key = (text, ink, background, scale)
        cached = self._images.get(key)
        if cached is not None:
            return cached
        rows = color_rows(text, ink=ink, background=background, scale=scale)
        width = max((len(row) for row in rows), default=1)
        height = max(1, len(rows))
        image = tk.PhotoImage(width=width, height=height)
        image.put(photo_data(rows))
        self._images[key] = image
        return image


_CACHE = FontCache()


def cache() -> FontCache:
    return _CACHE


class PixelLabel(tk.Canvas):
    """Static bitmap-font text."""

    def __init__(
        self,
        master,
        text: str,
        *,
        ink: str = theme.TEXT_DIM,
        background: str = theme.BG,
        scale: int = 1,
        padx: int = 0,
        pady: int = 0,
        **kwargs,
    ):
        self._text = text
        self._ink = ink
        self._background = background
        self._scale = scale
        width, height = text_size(text, scale=scale)
        super().__init__(
            master,
            width=width + padx * 2,
            height=height + pady * 2,
            bg=background,
            highlightthickness=0,
            bd=0,
            **kwargs,
        )
        self._padding = (padx, pady)
        self._item = None
        self._render()

    def _render(self) -> None:
        image = _CACHE.image(
            self._text,
            ink=self._ink,
            background=self._background,
            scale=self._scale,
        )
        if self._item is None:
            self._item = self.create_image(
                self._padding[0], self._padding[1], anchor="nw", image=image
            )
        else:
            self.itemconfigure(self._item, image=image)
        self._image = image

    def set_text(self, text: str, *, ink: str | None = None) -> None:
        self._text = text
        if ink is not None:
            self._ink = ink
        width, height = text_size(text, scale=self._scale)
        self.configure(width=width + self._padding[0] * 2, height=height + self._padding[1] * 2)
        self._render()


def draw_pixel_border(
    canvas: tk.Canvas,
    width: int,
    height: int,
    *,
    color: str,
    background: str,
    corner_notch: int = 0,
    tag: str = "border",
) -> None:
    """Draw a crisp 1px frame with optional cut corners."""
    canvas.delete(tag)
    notch = max(0, corner_notch)
    if notch == 0:
        canvas.create_rectangle(0, 0, width - 1, height - 1, outline=color, fill=background, tags=tag)
        return
    canvas.create_rectangle(
        notch, 0, width - 1 - notch, height - 1, outline=color, fill=background, tags=tag
    )
    canvas.create_rectangle(
        0, notch, width - 1, height - 1 - notch, outline=color, fill=background, tags=tag
    )
    for corner in ((notch, 0), (width - 1 - notch, 0), (notch, height - 1), (width - 1 - notch, height - 1)):
        canvas.create_rectangle(
            corner[0], corner[1], corner[0], corner[1], outline=color, fill=color, tags=tag
        )
    canvas.tag_lower(tag)


class PixelPanel(tk.Frame):
    """A framed container: ``.body`` is the inner frame for real widgets."""

    def __init__(
        self,
        master,
        *,
        background: str = theme.PANEL,
        border: str = theme.BORDER,
        padding: int = theme.PANEL_PAD,
        **kwargs,
    ):
        super().__init__(master, bg=theme.BG, highlightthickness=0, bd=0, **kwargs)
        self._chrome = tk.Canvas(
            self, bg=theme.BG, highlightthickness=0, bd=0
        )
        self._chrome.place(x=0, y=0, relwidth=1, relheight=1)
        self._border_color = border
        self._background = background
        self.body = tk.Frame(self, bg=background, highlightthickness=0, bd=0)
        self.body.place(x=padding, y=padding, relwidth=1, relheight=1, width=-padding * 2, height=-padding * 2)
        self._padding = padding
        self.bind("<Configure>", self._on_configure, add="+")
        self._draw()

    def _on_configure(self, _event=None) -> None:
        self._draw()

    def _draw(self) -> None:
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        draw_pixel_border(
            self._chrome,
            width,
            height,
            color=self._border_color,
            background=self._background,
            corner_notch=2,
        )

    def set_border(self, color: str) -> None:
        self._border_color = color
        self._draw()


class PixelButton(tk.Canvas):
    """Bitmap-font button with hover, press, active and disabled states."""

    def __init__(
        self,
        master,
        text: str,
        command: Callable[[], None] | None = None,
        *,
        accent: str = theme.ACCENT,
        ink: str | None = None,
        background: str = theme.BG,
        fill: str | None = None,
        active: bool = False,
        scale: int = 1,
        padding: tuple[int, int] = (10, 6),
        width: int | None = None,
        height: int | None = None,
        tooltip: str | None = None,
    ):
        self._text = text
        self._accent = accent
        self._ink = ink or accent
        self._base_ink = self._ink
        self._background = background
        self._fill = fill
        self._active = active
        self._enabled = True
        self._scale = scale
        self._padding = padding
        self._command = command
        self._hover = False
        self._pressed = False
        self._tooltip = tooltip
        text_width, text_height = text_size(text, scale=scale)
        computed_width = width or text_width + padding[0] * 2
        computed_height = height or text_height + padding[1] * 2
        super().__init__(
            master,
            width=computed_width,
            height=computed_height,
            bg=background,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self._button_width = computed_width
        self._button_height = computed_height
        self._label_item = None
        self.bind("<Enter>", self._on_enter)
        self.bind("<Leave>", self._on_leave)
        self.bind("<ButtonPress-1>", self._on_press)
        self.bind("<ButtonRelease-1>", self._on_release)
        self._render()

    # -- painting ----------------------------------------------------------
    def _palette(self) -> tuple[str, str, str]:
        if not self._enabled:
            return theme.PANEL, theme.DISABLED, theme.BORDER
        if self._active:
            return self._accent, theme.BG, self._accent
        if self._pressed:
            return self._accent, theme.BG, self._accent
        if self._hover:
            return theme.PANEL_RAISED, self._accent, self._accent
        return self._fill or self._background, self._base_ink, theme.BORDER

    def _render(self) -> None:
        fill, ink, border = self._palette()
        self.delete("all")
        draw_pixel_border(
            self,
            self._button_width,
            self._button_height,
            color=border,
            background=fill,
            corner_notch=2,
        )
        image = _CACHE.image(self._text, ink=ink, background=fill, scale=self._scale)
        text_width, text_height = text_size(self._text, scale=self._scale)
        x = (self._button_width - text_width) // 2
        y = (self._button_height - text_height) // 2
        self._label_item = self.create_image(x, y, anchor="nw", image=image)
        self._image = image

    # -- interaction -------------------------------------------------------
    def _on_enter(self, _event=None) -> None:
        self._hover = True
        self._render()

    def _on_leave(self, _event=None) -> None:
        self._hover = False
        self._pressed = False
        self._render()

    def _on_press(self, _event=None) -> None:
        if not self._enabled:
            return
        self._pressed = True
        self._render()

    def _on_release(self, _event=None) -> None:
        if not self._enabled:
            return
        was_pressed = self._pressed
        self._pressed = False
        self._render()
        if was_pressed and self._command is not None:
            self._command()

    # -- API ---------------------------------------------------------------
    def set_enabled(self, enabled: bool) -> None:
        self._enabled = enabled
        self.configure(cursor="hand2" if enabled else "arrow")
        self._render()

    def set_active(self, active: bool) -> None:
        self._active = active
        self._render()

    def set_text(self, text: str, *, ink: str | None = None) -> None:
        self._text = text
        if ink is not None:
            self._base_ink = ink
        self._render()

    def set_accent(self, accent: str) -> None:
        self._accent = accent
        if self._base_ink == self._ink:
            self._ink = accent
        self._render()


class PixelProgress(tk.Canvas):
    """Segmented block meter with a bitmap-font caption."""

    SEGMENTS = 26

    def __init__(
        self,
        master,
        *,
        background: str = theme.BG,
        blocks: int = SEGMENTS,
        height: int = 10,
    ):
        self._background = background
        self._blocks = blocks
        self._value = 0.0
        self._label = ""
        super().__init__(
            master,
            height=height,
            bg=background,
            highlightthickness=0,
            bd=0,
        )
        self.bind("<Configure>", lambda _event: self._render())
        self._render()

    def set(self, value: float, label: str | None = None) -> None:
        self._value = max(0.0, min(100.0, float(value)))
        if label is not None:
            self._label = label
        self._render()

    def _render(self) -> None:
        self.delete("all")
        width = max(40, self.winfo_width())
        height = max(8, self.winfo_height())
        filled = int(round(self._blocks * self._value / 100.0))
        gap = 2
        block_width = max(2, (width - gap * (self._blocks - 1)) // self._blocks)
        for index in range(self._blocks):
            x = index * (block_width + gap)
            color = theme.ACCENT if index < filled else theme.PANEL_RAISED
            if index < filled and index == filled - 1:
                color = theme.CYAN
            self.create_rectangle(
                x, 0, x + block_width - 1, height - 2, outline="", fill=color
            )


class PixelToggle(tk.Canvas):
    """Pixel checkbox with a bitmap-font caption."""

    SIZE = 11

    def __init__(
        self,
        master,
        text: str,
        variable: tk.BooleanVar,
        *,
        command: Callable[[], None] | None = None,
        background: str = theme.BG,
        accent: str = theme.ACCENT,
    ):
        self._text = text
        self._variable = variable
        self._command = command
        self._accent = accent
        self._background = background
        text_width, text_height = text_size(text, scale=1)
        height = max(self.SIZE, text_height)
        super().__init__(
            master,
            width=self.SIZE + 7 + text_width,
            height=height,
            bg=background,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.bind("<Button-1>", self._toggle)
        self._variable.trace_add("write", lambda *_: self._render())
        self._render()

    def _toggle(self, _event=None) -> None:
        self._variable.set(not self._variable.get())
        if self._command is not None:
            self._command()

    def _render(self) -> None:
        self.delete("all")
        checked = bool(self._variable.get())
        color = self._accent if checked else theme.BORDER_BRIGHT
        self.create_rectangle(
            0, 1, self.SIZE - 1, self.SIZE, outline=color, fill=theme.BG_SUNKEN
        )
        if checked:
            self.create_rectangle(3, 4, self.SIZE - 4, self.SIZE - 3, outline="", fill=color)
        image = _CACHE.image(
            self._text,
            ink=self._accent if checked else theme.TEXT_DIM,
            background=self._background,
            scale=1,
        )
        self.create_image(self.SIZE + 7, (self.SIZE + 1 - 7) // 2, anchor="nw", image=image)
        self._image = image


class PixelDropdown(tk.Canvas):
    """Dropdown that pops a dark ``tk.Menu`` list."""

    def __init__(
        self,
        master,
        *,
        values: Sequence[tuple[str, str]] | Sequence[str],
        variable: tk.StringVar,
        command: Callable[[str], None] | None = None,
        width: int = 220,
        background: str = theme.BG,
        accent: str = theme.CYAN,
        label: str | None = None,
    ):
        self._background = background
        self._accent = accent
        self._command = command
        self._entries: list[tuple[str, str]] = []
        self.set_values(values)
        self._variable = variable
        self._width = width
        self._label = label
        super().__init__(
            master,
            width=width,
            height=20,
            bg=background,
            highlightthickness=0,
            bd=0,
            cursor="hand2",
        )
        self.bind("<Button-1>", self._open)
        self._variable.trace_add("write", lambda *_: self._render())
        self._render()

    def set_values(self, values: Sequence[tuple[str, str]] | Sequence[str]) -> None:
        entries: list[tuple[str, str]] = []
        for value in values:
            if isinstance(value, (tuple, list)) and len(value) == 2:
                entries.append((str(value[0]), str(value[1])))
            else:
                entries.append((str(value), str(value)))
        self._entries = entries
        self._labels = {key: label for key, label in entries}

    def _display(self) -> str:
        current = self._variable.get()
        return self._labels.get(current, current or "—")

    def _open(self, _event=None) -> None:
        if not self._entries:
            return
        menu = tk.Menu(
            self,
            tearoff=0,
            bg=theme.PANEL_ALT,
            fg=theme.TEXT,
            activebackground=theme.ACCENT_SOFT,
            activeforeground=theme.ACCENT,
            bd=0,
            relief="flat",
            font=(theme.ui_family(), 9),
        )
        for key, label in self._entries:
            menu.add_command(
                label=label,
                command=lambda key=key: self._select(key),
            )
        try:
            menu.tk_popup(self.winfo_rootx(), self.winfo_rooty() + self.winfo_height())
        finally:
            menu.grab_release()

    def _select(self, key: str) -> None:
        self._variable.set(key)
        if self._command is not None:
            self._command(key)

    def _render(self) -> None:
        self.delete("all")
        height = max(20, self.winfo_height())
        draw_pixel_border(
            self,
            self._width,
            height,
            color=theme.BORDER_BRIGHT,
            background=theme.PANEL_ALT,
            corner_notch=2,
        )
        label = self._display()
        max_pixels = (self._width - 26) // 1
        while label and text_size(label, scale=1)[0] > max_pixels:
            label = label[:-2]
        image = _CACHE.image(
            label, ink=theme.TEXT, background=theme.PANEL_ALT, scale=1
        )
        self.create_image(8, (height - 7) // 2, anchor="nw", image=image)
        arrow = _CACHE.image("▼", ink=self._accent, background=theme.PANEL_ALT, scale=1)
        self.create_image(self._width - 14, (height - 7) // 2, anchor="nw", image=arrow)
        self._image = image
        self._arrow_image = arrow


class PixelEntry(tk.Frame):
    """Single-line entry wrapped in a pixel frame."""

    def __init__(
        self,
        master,
        *,
        variable: tk.StringVar | None = None,
        width: int = 160,
        placeholder: str = "",
        background: str = theme.BG,
        show: str | None = None,
    ):
        super().__init__(master, bg=background, highlightthickness=0, bd=0)
        self._chrome = tk.Canvas(self, width=width, height=22, bg=background, highlightthickness=0, bd=0)
        self._chrome.pack(fill="both", expand=True)
        self._entry = tk.Entry(
            self._chrome,
            textvariable=variable,
            bg=theme.BG_SUNKEN,
            fg=theme.TEXT,
            insertbackground=theme.ACCENT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            font=(theme.ui_family(), 9),
            show=show or "",
        )
        self._entry.place(x=6, y=3, relwidth=1, width=-12, height=16)
        self._chrome.bind("<Configure>", lambda _event: self._draw())
        self._placeholder = placeholder
        self._draw()

    def _draw(self) -> None:
        width = max(1, self._chrome.winfo_width())
        height = max(1, self._chrome.winfo_height())
        draw_pixel_border(
            self._chrome,
            width,
            height,
            color=theme.BORDER,
            background=theme.BG_SUNKEN,
            corner_notch=2,
        )
        self._chrome.tag_lower("border")

    def entry(self) -> tk.Entry:
        return self._entry

    def get(self) -> str:
        return self._entry.get()

    def set(self, value: str) -> None:
        self._entry.delete(0, "end")
        self._entry.insert(0, value)


class PixelTextArea(tk.Frame):
    """Multi-line editor wrapped in a pixel frame, with a slim scrollbar."""

    def __init__(
        self,
        master,
        *,
        background: str = theme.BG,
        height: int = 8,
        monospace: bool = True,
    ):
        super().__init__(master, bg=background, highlightthickness=0, bd=0)
        self._chrome = tk.Canvas(self, bg=background, highlightthickness=0, bd=0)
        self._chrome.place(x=0, y=0, relwidth=1, relheight=1)
        family = theme.code_family() if monospace else theme.ui_family()
        self.text = tk.Text(
            self._chrome,
            bg=theme.BG_SUNKEN,
            fg=theme.TEXT,
            insertbackground=theme.ACCENT,
            selectbackground=theme.SELECT,
            selectforeground=theme.TEXT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            wrap="none",
            undo=True,
            height=height,
            font=(family, 10),
            padx=6,
            pady=4,
        )
        self.text.place(x=4, y=4, relwidth=1, width=-22, relheight=1, height=-8)
        self.scrollbar = Scrollbar(self._chrome, command=self.text.yview, background=background)
        self.scrollbar.place(relx=1.0, y=4, anchor="ne", width=8, relheight=1, height=-8)
        self.text.configure(yscrollcommand=self._on_scroll)
        self._chrome.bind("<Configure>", lambda _event: self._draw())
        self._draw()

    def _on_scroll(self, first: str, last: str) -> None:
        self.scrollbar.set(first, last)

    def _draw(self) -> None:
        width = max(1, self._chrome.winfo_width())
        height = max(1, self._chrome.winfo_height())
        draw_pixel_border(
            self._chrome,
            width,
            height,
            color=theme.BORDER,
            background=theme.BG_SUNKEN,
            corner_notch=2,
        )
        self._chrome.tag_lower("border")

    def get_text(self) -> str:
        return self.text.get("1.0", "end-1c")

    def set_text(self, value: str) -> None:
        self.text.delete("1.0", "end")
        self.text.insert("1.0", value)

    def focus_text(self) -> None:
        self.text.focus_set()


class CodeText(tk.Frame):
    """Read-only code view with a line-number gutter."""

    def __init__(
        self,
        master,
        *,
        background: str = theme.BG,
        wrap: str = "none",
    ):
        super().__init__(master, bg=background, highlightthickness=0, bd=0)
        self._chrome = tk.Canvas(self, bg=background, highlightthickness=0, bd=0)
        self._chrome.place(x=0, y=0, relwidth=1, relheight=1)
        family = theme.code_family()
        self.gutter = tk.Text(
            self._chrome,
            width=5,
            bg=theme.BG_SUNKEN,
            fg=theme.MUTED,
            relief="flat",
            bd=0,
            highlightthickness=0,
            wrap="none",
            font=(family, 10),
            padx=4,
            pady=4,
            takefocus=0,
            cursor="arrow",
        )
        self.gutter.place(x=4, y=4, width=44, relheight=1, height=-8)
        self.text = tk.Text(
            self._chrome,
            bg=theme.BG_SUNKEN,
            fg=theme.TEXT,
            insertbackground=theme.ACCENT,
            selectbackground=theme.SELECT,
            selectforeground=theme.TEXT,
            relief="flat",
            bd=0,
            highlightthickness=0,
            wrap=wrap,
            font=(family, 10),
            padx=6,
            pady=4,
            undo=False,
        )
        self.text.place(x=52, y=4, relwidth=1, width=-64, relheight=1, height=-8)
        self.scrollbar = Scrollbar(self._chrome, command=self._scroll, background=background)
        self.scrollbar.place(relx=1.0, y=4, anchor="ne", width=8, relheight=1, height=-8)
        self.text.configure(yscrollcommand=self._on_scroll)
        self.gutter.configure(yscrollcommand=self._on_scroll)
        self._chrome.bind("<Configure>", lambda _event: self._draw())
        self.text.bind("<MouseWheel>", self._on_wheel, add="+")
        self.text.bind("<Button-4>", lambda event: self._scroll(-3, "units"), add="+")
        self.text.bind("<Button-5>", lambda event: self._scroll(3, "units"), add="+")
        self.bind("<Configure>", lambda _event: self._sync_gutter())
        self._draw()

    def _draw(self) -> None:
        width = max(1, self._chrome.winfo_width())
        height = max(1, self._chrome.winfo_height())
        draw_pixel_border(
            self._chrome,
            width,
            height,
            color=theme.BORDER,
            background=theme.BG_SUNKEN,
            corner_notch=2,
        )
        self._chrome.tag_lower("border")

    def _scroll(self, *args) -> None:
        self.text.yview(*args)
        self.gutter.yview(*args)

    def _on_wheel(self, event) -> None:
        delta = -1 if event.delta > 0 else 1
        self._scroll(delta * 3, "units")

    def _on_scroll(self, first: str, last: str) -> None:
        self.scrollbar.set(first, last)
        self.gutter.yview_moveto(first)

    def load(self, content: str) -> None:
        self.text.configure(state="normal")
        self.text.delete("1.0", "end")
        self.text.insert("1.0", content)
        self.text.configure(state="disabled")
        self._sync_gutter()

    def _sync_gutter(self) -> None:
        line_count = int(self.text.index("end-1c").split(".")[0])
        self.gutter.configure(state="normal")
        self.gutter.delete("1.0", "end")
        self.gutter.insert("1.0", "\n".join(str(number) for number in range(1, line_count + 1)))
        self.gutter.configure(state="disabled")

    def set_wrap(self, wrap: str) -> None:
        self.text.configure(wrap=wrap)
        self._sync_gutter()


class Scrollbar(tk.Canvas):
    """Eight-pixel scrollbar drawn as a block track."""

    def __init__(self, master, *, command, background: str = theme.BG, width: int = 8):
        super().__init__(
            master,
            width=width,
            bg=background,
            highlightthickness=0,
            bd=0,
            cursor="arrow",
        )
        self._command = command
        self._first = 0.0
        self._last = 1.0
        self._background = background
        self._drag_origin: tuple[int, float] | None = None
        self.bind("<Button-1>", self._on_press)
        self.bind("<B1-Motion>", self._on_drag)
        self.bind("<ButtonRelease-1>", lambda _event: setattr(self, "_drag_origin", None))
        self.bind("<Configure>", lambda _event: self._render())
        self._render()

    def set(self, first: str, last: str) -> None:
        try:
            self._first = float(first)
            self._last = float(last)
        except (TypeError, ValueError):
            return
        self._render()

    def _track(self) -> tuple[int, int, int]:
        height = max(1, self.winfo_height())
        start = int(self._first * height)
        end = max(start + 8, int(self._last * height))
        return start, min(end, height), height

    def _render(self) -> None:
        self.delete("all")
        width = max(1, self.winfo_width())
        height = max(1, self.winfo_height())
        self.create_rectangle(0, 0, width - 1, height - 1, outline="", fill=theme.BG_SUNKEN)
        start, end, _ = self._track()
        self.create_rectangle(1, start, width - 2, end - 2, outline="", fill=theme.BORDER_BRIGHT)

    def _on_press(self, event) -> None:
        start, end, height = self._track()
        if start <= event.y <= end:
            self._drag_origin = (event.y, self._first)
            return
        self._command("moveto", max(0.0, min(1.0, event.y / max(1, height) - 0.05)))

    def _on_drag(self, event) -> None:
        if self._drag_origin is None:
            return
        origin_y, origin_fraction = self._drag_origin
        delta = (event.y - origin_y) / max(1, self.winfo_height())
        self._command("moveto", max(0.0, min(1.0, origin_fraction + delta)))
