from __future__ import annotations

import logging
import queue
import threading
import tkinter as tk
from tkinter import ttk
from datetime import datetime

from core.version import VERSION


class _QueueHandler(logging.Handler):
    def __init__(self, records: queue.Queue[logging.LogRecord]):
        super().__init__()
        self.records = records

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.records.put_nowait(record)
        except Exception:
            self.handleError(record)


class BootstrapWindow(tk.Tk):
    """Small stdlib-only repair window, shown before optional Python packages load."""

    def __init__(self):
        super().__init__()
        self.title(f"PROTEZ / STARTUP CHECK / {VERSION}")
        self.geometry("780x570")
        self.minsize(680, 480)
        self.configure(bg="#050505")
        self.resizable(True, True)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.records: queue.Queue[logging.LogRecord] = queue.Queue()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.logger = logging.getLogger("protez")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.handler = _QueueHandler(self.records)
        self.handler._protez_bootstrap_handler = True
        self.logger.addHandler(self.handler)
        self._worker: threading.Thread | None = None
        self._running = False
        self._retry_force = False
        self.success = False

        self._configure_style()
        self._build_layout()
        self.after(60, self._drain_logs)
        self.after(180, self._start_check)

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#050505")
        style.configure("TLabel", background="#050505", foreground="#ededed")
        style.configure("Muted.TLabel", foreground="#858585")
        style.configure(
            "TButton",
            background="#111111",
            foreground="#f4f4f4",
            bordercolor="#686868",
            padding=(14, 8),
            font=("TkFixedFont", 10, "bold"),
        )
        style.map("TButton", background=[("active", "#eeeeee")], foreground=[("active", "#080808")])
        style.configure("TProgressbar", background="#f1f1f1", troughcolor="#161616", bordercolor="#454545")

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=18)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(3, weight=1)

        header = ttk.Frame(root)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 12))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="PROTEZ", font=("TkFixedFont", 16, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(header, text="SELF-REPAIR / LOCAL RUNTIME", style="Muted.TLabel").grid(
            row=1, column=0, sticky="w", pady=(5, 0)
        )

        self.status = ttk.Label(root, text="Checking required components…")
        self.status.grid(row=1, column=0, sticky="w", pady=(0, 7))
        self.progress = ttk.Progressbar(root, mode="indeterminate")
        self.progress.grid(row=2, column=0, sticky="new", pady=(0, 10))
        self.log = tk.Text(
            root,
            bg="#000000",
            fg="#dedede",
            insertbackground="#ffffff",
            selectbackground="#7a7a7a",
            font=("TkFixedFont", 9),
            relief="flat",
            borderwidth=1,
            highlightthickness=1,
            highlightbackground="#383838",
            highlightcolor="#aaaaaa",
            wrap="word",
            state="disabled",
        )
        self.log.grid(row=3, column=0, sticky="nsew", pady=(0, 10))
        self.log.tag_configure("INFO", foreground="#e1e1e1")
        self.log.tag_configure("WARNING", foreground="#bbbbbb")
        self.log.tag_configure("ERROR", foreground="#ffffff")
        self.log.tag_configure("DEBUG", foreground="#777777")

        footer = ttk.Frame(root)
        footer.grid(row=4, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.hint = ttk.Label(
            footer,
            text="Bundled builds repair their local runtime without downloading Python or CMake.",
            style="Muted.TLabel",
        )
        self.hint.grid(row=0, column=0, sticky="w")
        self.retry_button = ttk.Button(footer, text="REPAIR AGAIN", command=self._retry, state="disabled")
        self.retry_button.grid(row=0, column=1, sticky="e", padx=(8, 0))

    def _start_check(self) -> None:
        if self._running:
            return
        self._running = True
        self.retry_button.configure(state="disabled")
        self.status.configure(text="Checking and repairing Protez prerequisites…")
        self.progress.start(12)
        self._worker = threading.Thread(
            target=self._check_worker,
            args=(self._retry_force,),
            name="protez-startup-repair",
            daemon=True,
        )
        self._worker.start()

    def _check_worker(self, force: bool) -> None:
        try:
            from installer import ensure_installed

            ensure_installed(force=force)
            # Validate the packaged GUI modules before closing this repair window.
            from gui.app import ProtezApp  # noqa: F401
        except Exception as exc:
            self.logger.exception("Startup repair failed")
            self.events.put(("failure", str(exc)))
        else:
            self.events.put(("success", "Runtime is ready"))

    def _drain_logs(self) -> None:
        for _ in range(500):
            try:
                record = self.records.get_nowait()
            except queue.Empty:
                break
            try:
                timestamp = datetime.fromtimestamp(record.created).strftime("%H:%M:%S")
                message = record.getMessage()
                if record.exc_info:
                    message += "\n" + logging.Formatter().formatException(record.exc_info)
                tag = (
                    "ERROR" if record.levelno >= logging.ERROR
                    else "WARNING" if record.levelno >= logging.WARNING
                    else "DEBUG" if record.levelno <= logging.DEBUG
                    else "INFO"
                )
                self.log.configure(state="normal")
                for line in message.splitlines() or [""]:
                    self.log.insert("end", f"[{timestamp}] {tag:<7} {line}\n", tag)
                line_count = int(self.log.index("end-1c").split(".", maxsplit=1)[0])
                if line_count > 2500:
                    self.log.delete("1.0", f"{line_count - 2000}.0")
                self.log.see("end")
                self.log.configure(state="disabled")
            except tk.TclError:
                return

        while True:
            try:
                event, payload = self.events.get_nowait()
            except queue.Empty:
                break
            if event == "success":
                self.success = True
                self._running = False
                self.progress.stop()
                self.status.configure(text="Startup repair complete — opening Protez…")
                self.retry_button.configure(state="disabled")
                self.after(550, self._finish)
            else:
                self._running = False
                self.progress.stop()
                self.status.configure(text=f"Repair needs attention: {payload}")
                self.hint.configure(
                    text="See the log above. Retry performs a forced dependency/runtime repair."
                )
                self.retry_button.configure(state="normal")
        try:
            self.after(60, self._drain_logs)
        except tk.TclError:
            pass

    def _retry(self) -> None:
        self._retry_force = True
        self._start_check()

    def _on_close(self) -> None:
        if self._running:
            self.status.configure(text="Repair is in progress; wait for it to finish before closing.")
            return
        self._finish()

    def _finish(self) -> None:
        try:
            self.logger.removeHandler(self.handler)
        except Exception:
            pass
        self.destroy()
