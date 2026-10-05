from __future__ import annotations

import logging
import queue
from datetime import datetime

import customtkinter as ctk

from gui.theme import ACCENT, BG, BORDER, ERROR, MUTED, NEON, PANEL, WARN


class QueueLogHandler(logging.Handler):
    """Forwards log records to the UI without touching Tk from worker threads."""

    def __init__(self, records: queue.Queue[logging.LogRecord]):
        super().__init__()
        self.records = records

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.records.put_nowait(record)
        except Exception:
            self.handleError(record)


class LogPanel(ctk.CTkFrame):
    MAX_LINES = 1000

    def __init__(self, master, records: queue.Queue[logging.LogRecord], font, log_font=None):
        super().__init__(
            master,
            corner_radius=9,
            border_width=1,
            border_color=BORDER,
            fg_color=PANEL,
        )
        self._records = records
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=22)
        header.grid(row=0, column=0, sticky="ew", padx=9, pady=(3, 1))
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="ACTIVITY",
            text_color=NEON,
            font=ctk.CTkFont(family=font.cget("family"), size=9, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text="● LIVE",
            text_color=ACCENT,
            font=ctk.CTkFont(family=font.cget("family"), size=9, weight="bold"),
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        self.textbox = ctk.CTkTextbox(
            self,
            width=300,
            height=44,
            corner_radius=7,
            border_width=0,
            fg_color=BG,
            text_color=NEON,
            font=log_font or font,
            wrap="word",
            activate_scrollbars=True,
        )
        self.textbox.grid(row=1, column=0, sticky="nsew", padx=6, pady=(0, 6))
        self._text = self.textbox._textbox
        self._text.tag_configure("INFO", foreground=NEON)
        self._text.tag_configure("WARNING", foreground=WARN)
        self._text.tag_configure("ERROR", foreground=ERROR)
        self._text.tag_configure("DEBUG", foreground=MUTED)
        self.textbox.configure(state="disabled")
        self.after(60, self._drain_records)

    @staticmethod
    def _tag_for(levelno: int) -> str:
        if levelno >= logging.ERROR:
            return "ERROR"
        if levelno >= logging.WARNING:
            return "WARNING"
        if levelno <= logging.DEBUG:
            return "DEBUG"
        return "INFO"

    def _render_record(self, record: logging.LogRecord) -> None:
        timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
        level = record.levelname.upper()
        message = record.getMessage()
        if record.exc_info:
            message = f"{message}\n{logging.Formatter().formatException(record.exc_info)}"
        tag = self._tag_for(record.levelno)

        self.textbox.configure(state="normal")
        for line in message.splitlines() or [""]:
            self._text.insert("end", f"{timestamp}  {level:<7} {line}\n", tag)
        line_count = int(self._text.index("end-1c").split(".", maxsplit=1)[0])
        if line_count > self.MAX_LINES + 1:
            self._text.delete("1.0", f"{line_count - self.MAX_LINES}.0")
        self._text.see("end")
        self.textbox.configure(state="disabled")

    def _drain_records(self) -> None:
        for _ in range(300):
            try:
                record = self._records.get_nowait()
            except queue.Empty:
                break
            try:
                self._render_record(record)
            except Exception:
                continue
        try:
            self.after(60, self._drain_records)
        except Exception:
            pass
