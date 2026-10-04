from __future__ import annotations

import logging
import os
import platform
import queue
import subprocess
import threading
from pathlib import Path

import customtkinter as ctk
from tkinter import font as tkfont

from gui.controls import Controls
from gui.input_panel import InputPanel
from gui.log_panel import LogPanel, QueueLogHandler
from gui.theme import BG, BORDER, MUTED, NEON, PANEL

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None

ROOT = Path(__file__).resolve().parents[1]
OUTPUT_DIR = ROOT / "output"


class ProtezApp(ctk.CTk):
    def __init__(self):
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("dark-blue")
        super().__init__()

        self.log_records: queue.Queue[logging.LogRecord] = queue.Queue()
        self.ui_events: queue.Queue[tuple] = queue.Queue()
        self.logger = logging.getLogger("protez")
        self._configure_logger()
        self._worker: threading.Thread | None = None
        self._closed = False

        self.title("PROTEZ // Luau Deobfuscator")
        self.geometry("1220x860")
        self.minsize(1000, 720)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.logger.info("Protez v1.0 initialized")
        self.logger.info("Loading fonts...")
        self.display_family, self.body_family = self._load_fonts()
        self.title_font = ctk.CTkFont(
            family=self.display_family,
            size=9,
            weight="normal",
        )
        self.body_font = ctk.CTkFont(family=self.body_family, size=17)
        self.code_font = ctk.CTkFont(family=self.body_family, size=18)

        self._build_layout()
        self._enable_drag_and_drop()
        self.after(50, self._poll_ui_events)
        self.logger.info("Ready. Awaiting input.")

    def _configure_logger(self) -> None:
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        for handler in list(self.logger.handlers):
            if getattr(handler, "_protez_ui_handler", False):
                self.logger.removeHandler(handler)
        handler = QueueLogHandler(self.log_records)
        handler._protez_ui_handler = True
        self.logger.addHandler(handler)
        self._queue_handler = handler

    def _load_fonts(self) -> tuple[str, str]:
        try:
            available = {family.lower(): family for family in tkfont.families(self)}
        except Exception:
            available = {}

        fallback = next(
            (
                available[name]
                for name in ("dejavu sans mono", "courier new", "courier", "fixed")
                if name in available
            ),
            "TkFixedFont",
        )
        loaded_families: dict[str, str] = {}
        font_specs = (
            ("PressStart2P-Regular.ttf", "Press Start 2P", "display"),
            ("VT323-Regular.ttf", "VT323", "body"),
        )
        manager = getattr(ctk, "FontManager", None)
        load_font = getattr(manager, "load_font", None)

        for filename, expected_family, role in font_specs:
            font_path = ROOT / "assets" / "fonts" / filename
            if not font_path.is_file():
                self.logger.warning("Font not found: %s; using a system monospace font", filename)
                continue
            if load_font is None:
                self.logger.warning("CustomTkinter font manager is unavailable")
                continue
            try:
                reported_family = load_font(str(font_path))
                try:
                    available = {family.lower(): family for family in tkfont.families(self)}
                except Exception:
                    available = {}
                expected = str(reported_family) if isinstance(reported_family, str) else expected_family
                matched = available.get(expected.lower()) or available.get(expected_family.lower())
                if matched:
                    loaded_families[role] = matched
                    self.logger.info("Loaded font: %s", matched)
                else:
                    self.logger.warning(
                        "Font was downloaded but could not be registered: %s", filename
                    )
            except Exception as exc:
                self.logger.warning("Could not load font %s: %s", filename, exc)

        display_family = loaded_families.get("display", fallback)
        body_family = loaded_families.get("body", fallback)
        if len(loaded_families) == len(font_specs):
            self.logger.info("Loading fonts... OK")
        else:
            self.logger.warning("Pixel font unavailable; using system monospace fallback")
        return display_family, body_family

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=4, minsize=210)
        self.grid_rowconfigure(1, weight=4, minsize=290)
        self.grid_rowconfigure(2, weight=2, minsize=150)

        self.log_panel = LogPanel(self, self.log_records, self.body_font)
        self.log_panel.grid(row=0, column=0, sticky="nsew", padx=12, pady=(12, 5))

        self.input_panel = InputPanel(
            self,
            title_font=self.title_font,
            body_font=self.code_font,
        )
        self.input_panel.grid(row=1, column=0, sticky="nsew", padx=12, pady=5)

        self.controls = Controls(
            self,
            title_font=self.title_font,
            body_font=self.body_font,
            on_destroy=self._start_deobfuscation,
            on_clear_logs=self._clear_logs,
            on_open_output=self._open_output,
            on_copy_result=self._copy_result,
        )
        self.controls.grid(row=2, column=0, sticky="nsew", padx=12, pady=(5, 12))

    def _enable_drag_and_drop(self) -> None:
        if TkinterDnD is None or DND_FILES is None:
            self.logger.warning("Drag-and-drop support unavailable; use BROWSE instead")
            return
        try:
            TkinterDnD.require(self)
            if not self.input_panel.enable_drag_and_drop(DND_FILES):
                raise RuntimeError("file drop target could not be registered")
            self.logger.info("File drag-and-drop ready")
        except Exception as exc:
            self.logger.warning("Drag-and-drop unavailable; BROWSE remains active: %s", exc)

    def _start_deobfuscation(self) -> None:
        if self.controls.busy:
            return
        source = self.input_panel.get_script()
        if not source.strip():
            self.logger.warning("No input provided")
            return

        self.logger.info("Deobfuscation started")
        self.controls.set_busy(True)
        self.controls.set_progress(0, "STARTING")
        self._worker = threading.Thread(
            target=self._run_pipeline,
            args=(source,),
            name="protez-deobfuscation",
            daemon=True,
        )
        self._worker.start()

    def _run_pipeline(self, source: str) -> None:
        try:
            # The core pipeline is added in later implementation milestones.
            self.logger.warning(
                "Deobfuscation core is not available yet; input was not executed"
            )
            self.ui_events.put(("progress", 0, "NOT READY"))
        except Exception:
            self.logger.exception("Deobfuscation worker failed")
        finally:
            self.ui_events.put(("finished",))

    def _poll_ui_events(self) -> None:
        if self._closed:
            return
        for _ in range(200):
            try:
                event = self.ui_events.get_nowait()
            except queue.Empty:
                break
            try:
                if event[0] == "progress":
                    self.controls.set_progress(event[1], event[2])
                elif event[0] == "finished":
                    self.controls.set_busy(False)
            except Exception:
                self.logger.exception("Could not update the interface")
        self.after(50, self._poll_ui_events)

    def _clear_logs(self) -> None:
        self.log_panel.clear()

    def _open_output(self) -> None:
        try:
            OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
            system = platform.system().lower()
            if system == "windows":
                startfile = getattr(os, "startfile", None)
                if startfile is None:
                    raise RuntimeError("Windows Explorer opener is unavailable")
                startfile(str(OUTPUT_DIR))
            elif system == "darwin":
                subprocess.Popen(
                    ["open", str(OUTPUT_DIR)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                subprocess.Popen(
                    ["xdg-open", str(OUTPUT_DIR)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            self.logger.info("Opened output folder")
        except Exception:
            self.logger.exception("Could not open output folder")

    def _copy_result(self) -> None:
        try:
            results = list(OUTPUT_DIR.glob("deobfuscated_*.luau"))
            results.extend(OUTPUT_DIR.glob("deobfuscated_*.lua"))
            results = [path for path in results if path.is_file()]
            if not results:
                self.logger.warning("No result is available to copy")
                return
            latest = max(results, key=lambda path: path.stat().st_mtime)
            content = latest.read_text(encoding="utf-8", errors="replace")
            self.clipboard_clear()
            self.clipboard_append(content)
            self.logger.info("Copied result: %s", latest.name)
        except Exception:
            self.logger.exception("Could not copy result to clipboard")

    def _on_close(self) -> None:
        self._closed = True
        try:
            self.logger.removeHandler(self._queue_handler)
        except Exception:
            pass
        self.destroy()
