"""Pixel-styled result viewer.

The viewer is what the user sees right after a run: the recovered script with
line numbers, Lua highlighting, search and a metadata strip read from the
artifact banner.  It also offers copy / save-as / open-in-editor actions.
"""

from __future__ import annotations

import logging
import platform
import shutil
import subprocess
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from gui import highlight, theme
from gui.pixelkit import (
    CodeText,
    PixelButton,
    PixelEntry,
    PixelLabel,
    PixelPanel,
    PixelToggle,
    draw_pixel_border,
)

MAX_VIEW_CHARS = 4_000_000
META_KEYS = ("input", "family", "version", "method", "injector", "layers", "profile")


def parse_banner(content: str) -> dict[str, str]:
    """Read ``-- key : value`` lines from the artifact banner."""
    meta: dict[str, str] = {}
    for line in content.splitlines()[:40]:
        stripped = line.strip()
        if not stripped.startswith("--"):
            if stripped:
                break
            continue
        body = stripped.lstrip("-").strip()
        if ":" not in body:
            continue
        key, _, value = body.partition(":")
        key = key.strip().lower()
        if key in META_KEYS:
            meta[key] = value.strip()
    return meta


class CodeViewer(tk.Toplevel):
    """Frameless window showing one recovered artifact."""

    def __init__(
        self,
        master: tk.Misc,
        path: Path,
        *,
        logger: logging.Logger | None = None,
        initial_search: str | None = None,
    ):
        super().__init__(master)
        self.path = Path(path)
        self.logger = logger or logging.getLogger("protez")
        self.title(f"Protez — {self.path.name}")
        self.configure(bg=theme.BG)
        self.geometry("900x640")
        self.minsize(620, 420)

        self._wrap = tk.BooleanVar(value=False)
        self._matches: list[str] = []
        self._match_index = -1
        self._drag_offset: tuple[int, int] | None = None
        self._content = ""
        self._meta: dict[str, str] = {}

        self._load()
        self._build_layout()
        if initial_search:
            self.search_entry.set(initial_search)
            self.find_next()

    # ------------------------------------------------------------------
    # loading
    # ------------------------------------------------------------------
    def _load(self) -> None:
        try:
            raw = self.path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self.logger.error("Could not read %s: %s", self.path, exc)
            raw = f"-- Protez could not read {self.path.name}: {exc}\n"
        truncated = len(raw) > MAX_VIEW_CHARS
        self.truncated = truncated
        self._content = raw[:MAX_VIEW_CHARS]
        self._meta = parse_banner(self._content)

    # ------------------------------------------------------------------
    # layout
    # ------------------------------------------------------------------
    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        self._title_bar = tk.Canvas(self, height=30, bg=theme.PANEL, highlightthickness=0, bd=0)
        self._title_bar.grid(row=0, column=0, sticky="ew")
        self._title_bar.bind("<Configure>", lambda _event: self._draw_title_bar())
        self._title_bar.bind("<ButtonPress-1>", self._begin_drag)
        self._title_bar.bind("<B1-Motion>", self._drag)

        self._strip = tk.Canvas(self, height=22, bg=theme.BG, highlightthickness=0, bd=0)
        self._strip.grid(row=1, column=0, sticky="ew", padx=8, pady=(6, 0))
        self._strip.bind("<Configure>", lambda _event: self._draw_strip())

        code_panel = tk.Frame(self, bg=theme.BG, highlightthickness=0, bd=0)
        code_panel.grid(row=2, column=0, sticky="nsew", padx=8, pady=(6, 4))
        code_panel.grid_columnconfigure(0, weight=1)
        code_panel.grid_rowconfigure(1, weight=1)

        toolbar = tk.Frame(code_panel, bg=theme.BG, highlightthickness=0, bd=0)
        toolbar.grid(row=0, column=0, sticky="ew", pady=(0, 6))

        self.search_entry = PixelEntry(toolbar, width=190, placeholder="search")
        self.search_entry.pack(side="left")
        self.search_entry.entry().bind("<Return>", lambda _event: self.find_next())
        PixelButton(toolbar, "FIND", self.find_next, accent=theme.CYAN, scale=1, padding=(8, 5)).pack(
            side="left", padx=(6, 0)
        )
        PixelButton(toolbar, "PREV", self.find_previous, accent=theme.CYAN, scale=1, padding=(8, 5)).pack(
            side="left", padx=(4, 0)
        )
        PixelToggle(
            toolbar,
            "WRAP",
            self._wrap,
            command=self._apply_wrap,
            background=theme.BG,
        ).pack(side="left", padx=(10, 0))

        PixelButton(toolbar, "CLOSE", self.destroy, accent=theme.ERROR, scale=1, padding=(8, 5)).pack(
            side="right"
        )
        PixelButton(toolbar, "OPEN", self.open_externally, accent=theme.TEXT_DIM, scale=1, padding=(8, 5)).pack(
            side="right", padx=(0, 4)
        )
        PixelButton(toolbar, "SAVE AS", self.save_as, accent=theme.TEXT_DIM, scale=1, padding=(8, 5)).pack(
            side="right", padx=(0, 4)
        )
        PixelButton(toolbar, "COPY", self.copy_all, accent=theme.ACCENT, scale=1, padding=(8, 5)).pack(
            side="right", padx=(0, 4)
        )

        self.code = CodeText(code_panel)
        self.code.grid(row=1, column=0, sticky="nsew")
        self.code.load(self._content)
        self._configure_tags()
        self._apply_highlighting()

        self._status = tk.Canvas(self, height=20, bg=theme.BG, highlightthickness=0, bd=0)
        self._status.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, 8))
        self._status.bind("<Configure>", lambda _event: self._draw_status())

        self.bind("<Escape>", lambda _event: self.destroy())
        self.bind("<Control-f>", lambda _event: self.search_entry.focus_text())

    # ------------------------------------------------------------------
    # painting helpers
    # ------------------------------------------------------------------
    def _draw_title_bar(self) -> None:
        canvas = self._title_bar
        canvas.delete("all")
        width = max(1, canvas.winfo_width())
        height = 30
        canvas.create_rectangle(0, 0, width - 1, height - 1, outline="", fill=theme.PANEL)
        canvas.create_rectangle(0, height - 1, width - 1, height - 1, outline="", fill=theme.ACCENT)
        canvas.create_text(
            12,
            height // 2,
            anchor="w",
            text="DEOBFUSCATED SOURCE",
            fill=theme.ACCENT,
            font=(theme.ui_family(), 10, "bold"),
        )
        canvas.create_text(
            width - 14,
            height // 2,
            anchor="e",
            text=self.path.name,
            fill=theme.TEXT_DIM,
            font=(theme.code_family(), 9),
        )

    def _draw_strip(self) -> None:
        canvas = self._strip
        canvas.delete("all")
        width = max(1, canvas.winfo_width())
        height = 22
        draw_pixel_border(
            canvas,
            width,
            height,
            color=theme.BORDER,
            background=theme.PANEL_ALT,
            corner_notch=2,
        )
        parts: list[str] = []
        family = self._meta.get("family")
        if family:
            parts.append(family)
        method = self._meta.get("method")
        if method:
            parts.append(method)
        layers = self._meta.get("layers")
        if layers:
            parts.append(f"{layers} layer(s)")
        injector = self._meta.get("injector")
        if injector:
            parts.append(injector)
        if not parts:
            parts.append("recovered source")
        canvas.create_text(
            10,
            height // 2,
            anchor="w",
            text="  ·  ".join(parts),
            fill=theme.TEXT_DIM,
            font=(theme.ui_family(), 9),
        )

    def _draw_status(self) -> None:
        canvas = self._status
        canvas.delete("all")
        canvas.create_rectangle(
            0, 0, max(1, canvas.winfo_width()) - 1, 19, outline="", fill=theme.BG
        )
        lines = self._content.count("\n") + 1
        text = f"{lines:,} LINES · {len(self._content):,} CHARS · {self.path.name}"
        if self.truncated:
            text += " · PREVIEW TRUNCATED"
        canvas.create_text(
            2,
            10,
            anchor="w",
            text=text,
            fill=theme.WARN if self.truncated else theme.MUTED,
            font=(theme.ui_family(), 8),
        )
        if self._matches:
            canvas.create_text(
                max(1, canvas.winfo_width()) - 2,
                10,
                anchor="e",
                text=f"MATCH {self._match_index + 1}/{len(self._matches)}",
                fill=theme.CYAN,
                font=(theme.ui_family(), 8),
            )

    # ------------------------------------------------------------------
    # highlighting
    # ------------------------------------------------------------------
    def _configure_tags(self) -> None:
        widget = self.code.text
        for tag, color in theme.SYNTAX_COLORS.items():
            widget.tag_configure(tag, foreground=color)
        widget.tag_configure("search", background=theme.SYNTAX_COLORS["search"])
        widget.tag_configure(
            "active_match", background=theme.SYNTAX_COLORS["search"], foreground=theme.ACCENT
        )

    def _apply_highlighting(self) -> None:
        widget = self.code.text
        for tag in highlight.TAG_ORDER:
            widget.tag_remove(tag, "1.0", "end")
        for number, spans in enumerate(highlight.highlight_lines(self._content), start=1):
            for span in spans:
                widget.tag_add(
                    span.tag,
                    f"{number}.{span.start}",
                    f"{number}.{span.end}",
                )

    def _apply_wrap(self) -> None:
        self.code.set_wrap("word" if self._wrap.get() else "none")

    # ------------------------------------------------------------------
    # search
    # ------------------------------------------------------------------
    def find_next(self) -> None:
        query = self.search_entry.get().strip()
        if not query:
            return
        self._refresh_matches(query)
        if not self._matches:
            self.logger.info("No match for %r", query)
            return
        self._match_index = (self._match_index + 1) % len(self._matches)
        self._focus_match()

    def find_previous(self) -> None:
        query = self.search_entry.get().strip()
        if not query:
            return
        self._refresh_matches(query)
        if not self._matches:
            return
        self._match_index = (self._match_index - 1) % len(self._matches)
        self._focus_match()

    def _refresh_matches(self, query: str) -> None:
        widget = self.code.text
        widget.tag_remove("search", "1.0", "end")
        widget.tag_remove("active_match", "1.0", "end")
        self._matches = []
        if not query:
            return
        start = "1.0"
        while True:
            found = widget.search(query, start, stopindex="end", nocase=True)
            if not found:
                break
            end = f"{found}+{len(query)}c"
            widget.tag_add("search", found, end)
            self._matches.append(found)
            start = end
        self._draw_status()

    def _focus_match(self) -> None:
        widget = self.code.text
        widget.tag_remove("active_match", "1.0", "end")
        index = self._matches[self._match_index]
        end = f"{index}+{len(self.search_entry.get().strip())}c"
        widget.tag_add("active_match", index, end)
        widget.see(index)
        self._draw_status()

    # ------------------------------------------------------------------
    # actions
    # ------------------------------------------------------------------
    def copy_all(self) -> None:
        self.clipboard_clear()
        self.clipboard_append(self._content)
        self.logger.info("Copied %s to the clipboard", self.path.name)

    def save_as(self) -> None:
        target = filedialog.asksaveasfilename(
            parent=self,
            title="Save recovered source",
            initialfile=self.path.name,
            defaultextension=".lua",
            filetypes=[("Lua source", "*.lua"), ("All files", "*.*")],
        )
        if not target:
            return
        try:
            Path(target).write_text(self._content, encoding="utf-8")
            self.logger.info("Saved recovered source to %s", target)
        except OSError as exc:
            self.logger.error("Could not save the recovered source: %s", exc)

    def open_externally(self) -> None:
        target = str(self.path)
        system = platform.system().lower()
        try:
            if system == "windows":
                import os

                startfile = getattr(os, "startfile", None)
                if startfile is not None:
                    startfile(target)
                    return
                editor = shutil.which("notepad.exe")
                if editor:
                    subprocess.Popen([editor, target])
                return
            if system == "darwin":
                subprocess.Popen(["open", target])
                return
            opener = shutil.which("xdg-open")
            if opener:
                subprocess.Popen([opener, target])
        except Exception as exc:  # noqa: BLE001 - the viewer stays usable
            self.logger.warning("Could not open an external editor: %s", exc)

    # ------------------------------------------------------------------
    # window chrome
    # ------------------------------------------------------------------
    def _begin_drag(self, event) -> None:
        self._drag_offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _drag(self, event) -> None:
        if self._drag_offset is None:
            return
        self.geometry(f"+{event.x_root - self._drag_offset[0]}+{event.y_root - self._drag_offset[1]}")
