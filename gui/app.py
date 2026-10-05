from __future__ import annotations

import logging
import os
import platform
import queue
import shutil
import subprocess
import sys
import threading
import traceback
from pathlib import Path

import customtkinter as ctk
from tkinter import font as tkfont

from core.pipeline import DeobfuscationPipeline, PipelineError
from core.runtime_paths import FONTS_DIR
from core.source_input import SourceInputError, resolve_source_input
from core.version import VERSION
from gui.controls import Controls
from gui.input_panel import InputPanel
from gui.log_panel import LogPanel, QueueLogHandler
from gui.theme import BG, BORDER, MUTED, TEXT, TerminalButton

try:
    from tkinterdnd2 import DND_FILES, TkinterDnD
except ImportError:
    DND_FILES = None
    TkinterDnD = None


class ProtezApp(ctk.CTk):
    WINDOW_WIDTH = 560
    WINDOW_HEIGHT = 500
    MIN_WIDTH = 470
    MIN_HEIGHT = 410

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
        self._last_output_path: Path | None = None

        self.title("PROTEZ")
        self.overrideredirect(True)
        self.geometry(self._centered_geometry(self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.configure(fg_color=BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        self._drag_offset: tuple[int, int] | None = None
        self._resize_anchor: tuple[int, int, int, int] | None = None
        self._restore_chrome_after_map = False
        self.bind("<Map>", self._on_map, add="+")
        self.bind("<Control-Return>", self._start_deobfuscation, add="+")

        self.logger.info("Protez %s initialized", VERSION)
        self.logger.info("Loading fonts...")
        self.display_family, self.body_family = self._load_fonts()
        self.title_font = ctk.CTkFont(
            family=self.display_family,
            size=10,
            weight="normal",
        )
        self.body_font = ctk.CTkFont(family=self.body_family, size=17)
        self.code_font = ctk.CTkFont(family=self.body_family, size=18)

        self._build_layout()
        self._enable_drag_and_drop()
        self.after(60, self._poll_ui_events)
        self.logger.info("Ready. Paste source, a code link, or choose a file.")

    def _centered_geometry(self, width: int, height: int) -> str:
        try:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
        except Exception:
            screen_width, screen_height = width, height
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 2 - 24)
        return f"{width}x{height}+{x}+{y}"

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
        manager = getattr(ctk, "FontManager", None)
        load_font = getattr(manager, "load_font", None)
        windows_load_font = getattr(manager, "windows_load_font", None)
        font_specs = (
            ("PressStart2P-Regular.ttf", "Press Start 2P", "display"),
            ("VT323-Regular.ttf", "VT323", "body"),
        )

        for filename, expected_family, role in font_specs:
            font_path = FONTS_DIR / filename
            if not font_path.is_file():
                self.logger.warning("Font not found: %s; using a system monospace font", filename)
                continue
            try:
                loaded = False
                if sys.platform.startswith("win"):
                    # CustomTkinter's default Windows loader marks private fonts
                    # non-enumerable; Tk then silently substitutes another font.
                    if callable(windows_load_font):
                        loaded = bool(
                            windows_load_font(
                                str(font_path),
                                private=True,
                                enumerable=True,
                            )
                        )
                    if not loaded:
                        from ctypes import byref, create_unicode_buffer, windll

                        font_buffer = create_unicode_buffer(str(font_path))
                        loaded = bool(
                            windll.gdi32.AddFontResourceExW(byref(font_buffer), 0x10, 0)
                        )
                elif callable(load_font):
                    loaded = bool(load_font(str(font_path)))
                if not loaded:
                    raise RuntimeError("the font manager could not register the font")

                try:
                    available = {family.lower(): family for family in tkfont.families(self)}
                except Exception:
                    available = {}
                matched = available.get(expected_family.lower())
                if matched is None:
                    # Tk can use a registered family before it appears in the
                    # cached family list on some Windows/Tk combinations.
                    probe = tkfont.Font(self, family=expected_family, size=12)
                    actual_family = str(probe.actual("family"))
                    if actual_family.lower() == expected_family.lower():
                        matched = actual_family
                if matched:
                    loaded_families[role] = matched
                    self.logger.info("Loaded pixel font: %s", matched)
                else:
                    self.logger.warning(
                        "Registered %s but Tk could not select it; using a system fallback",
                        filename,
                    )
            except Exception as exc:
                self.logger.warning("Could not load font %s: %s", filename, exc)

        display_family = loaded_families.get("display", fallback)
        body_family = loaded_families.get("body", fallback)
        if len(loaded_families) == len(font_specs):
            self.logger.info("Pixel fonts ready")
        else:
            self.logger.warning("One or more pixel fonts are unavailable; using a system fallback")
        return display_family, body_family

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        title_bar = ctk.CTkFrame(
            self,
            fg_color=BG,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
            height=36,
        )
        title_bar.grid(row=0, column=0, sticky="ew")
        title_bar.grid_propagate(False)
        title_bar.grid_columnconfigure(0, weight=1)

        heading = ctk.CTkFrame(title_bar, fg_color=BG, corner_radius=0)
        heading.grid(row=0, column=0, sticky="nsew", padx=(12, 4))
        self.title_text = ctk.CTkLabel(
            heading,
            text="PROTEZ",
            text_color=TEXT,
            font=self.title_font,
            anchor="w",
        )
        self.title_text.grid(row=0, column=0, sticky="w")

        window_buttons = ctk.CTkFrame(title_bar, fg_color=BG, corner_radius=0)
        window_buttons.grid(row=0, column=1, sticky="e", padx=(4, 6), pady=4)
        button_font = ctk.CTkFont(family=self.body_family, size=18)
        button_style = {
            "accent": TEXT,
            "base_bg": BG,
            "base_text": TEXT,
            "width": 27,
            "height": 25,
            "font": button_font,
        }
        self.minimize_button = TerminalButton(
            window_buttons,
            text="—",
            command=self._minimize_window,
            **button_style,
        )
        self.minimize_button.grid(row=0, column=0, padx=(0, 3))
        self.close_button = TerminalButton(
            window_buttons,
            text="×",
            command=self._on_close,
            **button_style,
        )
        self.close_button.grid(row=0, column=1, padx=(3, 0))

        for widget in (title_bar, heading, self.title_text):
            widget.bind("<ButtonPress-1>", self._begin_window_drag, add="+")
            widget.bind("<B1-Motion>", self._drag_window, add="+")

        content = ctk.CTkFrame(self, fg_color=BG, corner_radius=0)
        content.grid(row=1, column=0, sticky="nsew", padx=10, pady=(8, 9))
        content.grid_columnconfigure(0, weight=1)
        content.grid_rowconfigure(0, weight=7, minsize=235)
        content.grid_rowconfigure(1, weight=0, minsize=47)
        content.grid_rowconfigure(2, weight=2, minsize=83)

        self.input_panel = InputPanel(
            content,
            title_font=self.title_font,
            body_font=self.code_font,
        )
        self.input_panel.grid(row=0, column=0, sticky="nsew", pady=(0, 8))

        self.controls = Controls(
            content,
            title_font=self.title_font,
            body_font=self.body_font,
            on_destroy=self._start_deobfuscation,
        )
        self.controls.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.log_panel = LogPanel(content, self.log_records, self.body_font)
        self.log_panel.grid(row=2, column=0, sticky="nsew")

        self.resize_grip = ctk.CTkLabel(
            self,
            text="◢",
            width=12,
            height=12,
            text_color=MUTED,
            fg_color=BG,
            font=ctk.CTkFont(family=self.body_family, size=11),
        )
        self.resize_grip.place(relx=1, rely=1, anchor="se")
        self.resize_grip.bind("<ButtonPress-1>", self._begin_resize)
        self.resize_grip.bind("<B1-Motion>", self._resize_window)

    def _begin_window_drag(self, event) -> None:
        self._drag_offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _drag_window(self, event) -> None:
        if self._drag_offset is None:
            return
        x = event.x_root - self._drag_offset[0]
        y = event.y_root - self._drag_offset[1]
        self.geometry(f"+{x}+{y}")

    def _begin_resize(self, event) -> None:
        self._resize_anchor = (
            event.x_root,
            event.y_root,
            self.winfo_width(),
            self.winfo_height(),
        )

    def _resize_window(self, event) -> None:
        if self._resize_anchor is None:
            return
        start_x, start_y, start_width, start_height = self._resize_anchor
        width = max(self.MIN_WIDTH, start_width + event.x_root - start_x)
        height = max(self.MIN_HEIGHT, start_height + event.y_root - start_y)
        self.geometry(f"{width}x{height}+{self.winfo_x()}+{self.winfo_y()}")

    def _minimize_window(self) -> None:
        try:
            self._restore_chrome_after_map = True
            self.overrideredirect(False)
            self.iconify()
        except Exception:
            self._restore_chrome_after_map = False
            self.overrideredirect(True)
            self.logger.warning("Window manager does not support minimizing this window")

    def _on_map(self, _event=None) -> None:
        if self._restore_chrome_after_map and self.state() == "normal":
            self._restore_chrome_after_map = False
            self.after_idle(lambda: self.overrideredirect(True))

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

    def _start_deobfuscation(self, _event=None) -> str:
        if self.controls.busy:
            return "break"
        source = self.input_panel.get_script()
        if not source.strip():
            self.logger.warning("No source or code link was provided")
            self.controls.set_status("PASTE SOURCE OR URL")
            return "break"

        source_path = self.input_panel.file_path
        source_name = source_path.name if source_path else "pasted input"
        self.logger.info("Started source processing")
        self.controls.set_busy(True)
        self.controls.set_progress(0, "STARTING")
        self._worker = threading.Thread(
            target=self._run_pipeline,
            args=(source, source_name),
            name="protez-deobfuscation",
            daemon=True,
        )
        self._worker.start()
        return "break"

    def _run_pipeline(self, source: str, source_name: str) -> None:
        try:
            resolved = resolve_source_input(
                source,
                source_name=source_name,
                logger=self.logger,
            )
            if resolved.fetched_urls:
                self.ui_events.put(("progress", 3, "FETCHED"))
            pipeline = DeobfuscationPipeline(
                logger=self.logger,
                progress_callback=lambda percent, stage: self.ui_events.put(
                    ("progress", percent, stage)
                ),
            )
            result = pipeline.run(resolved.source, source_name=resolved.source_name)
            self.ui_events.put(("output", str(result.output_path)))
        except SourceInputError as exc:
            self.logger.error("Could not resolve source input: %s", exc)
            self.ui_events.put(("failed", str(exc)))
        except PipelineError as exc:
            self.logger.error("Processing stopped: %s", exc)
            self.ui_events.put(("failed", str(exc)))
        except Exception:
            self.logger.exception("Source processing failed")
            self.ui_events.put(("failed", "See the activity log for details"))
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
                elif event[0] == "output":
                    path = Path(event[1])
                    self._last_output_path = path
                    self.controls.set_progress(100, "DONE")
                    try:
                        self._open_result(path)
                    except Exception:
                        self.logger.exception(
                            "Could not launch an editor; opening the result in Protez"
                        )
                        self._show_result_in_app(path)
                elif event[0] == "failed":
                    self.controls.set_status(f"FAILED · {event[1]}", error=True)
                elif event[0] == "finished":
                    self.controls.set_busy(False)
            except Exception:
                self.logger.exception("Could not update the interface")
        self.after(60, self._poll_ui_events)

    def _open_result(self, path: Path) -> None:
        if not path.is_file():
            raise FileNotFoundError(f"Result file not found: {path}")

        system = platform.system().lower()
        if system == "windows":
            system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
            editor_candidates = (
                system_root / "System32" / "notepad.exe",
                Path(shutil.which("notepad.exe") or ""),
            )
            editor = next(
                (candidate for candidate in editor_candidates if candidate.is_file()),
                None,
            )
            if editor is not None:
                subprocess.Popen(
                    [str(editor), str(path)],
                    stdin=subprocess.DEVNULL,
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                    close_fds=True,
                    creationflags=getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0),
                )
            else:
                startfile = getattr(os, "startfile", None)
                if startfile is None:
                    raise RuntimeError("No Windows text editor is available")
                startfile(str(path))
        elif system == "darwin":
            subprocess.Popen(
                ["open", str(path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        else:
            opener = shutil.which("xdg-open")
            if opener is None:
                raise RuntimeError("No desktop file opener is available")
            subprocess.Popen(
                [opener, str(path)],
                stdin=subprocess.DEVNULL,
                stdout=subprocess.DEVNULL,
                stderr=subprocess.DEVNULL,
                close_fds=True,
            )
        self.logger.info("Opened recovered script automatically: %s", path)

    def _show_result_in_app(self, path: Path) -> None:
        try:
            with path.open("r", encoding="utf-8", errors="replace") as source_file:
                content = source_file.read(1_000_001)
        except OSError:
            self.logger.exception("Could not open recovered script")
            return
        truncated = len(content) > 1_000_000
        if truncated:
            content = content[:1_000_000]

        window = ctk.CTkToplevel(self)
        window.title("PROTEZ")
        window.geometry("680x520")
        window.minsize(500, 360)
        window.configure(fg_color=BG)
        window.grid_columnconfigure(0, weight=1)
        window.grid_rowconfigure(1, weight=1)
        window.transient(self)

        header = ctk.CTkFrame(window, fg_color=BG, corner_radius=0)
        header.grid(row=0, column=0, sticky="ew", padx=12, pady=(10, 5))
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="PROTEZ",
            text_color=TEXT,
            font=self.title_font,
            anchor="w",
        ).grid(row=0, column=0, sticky="w")
        ctk.CTkLabel(
            header,
            text=path.name,
            text_color=MUTED,
            font=self.body_font,
            anchor="e",
        ).grid(row=0, column=1, sticky="e")

        code = ctk.CTkTextbox(
            window,
            fg_color="#050505",
            text_color=TEXT,
            font=self.code_font,
            wrap="none",
            activate_scrollbars=True,
        )
        code.grid(row=1, column=0, sticky="nsew", padx=10, pady=5)
        code.insert("1.0", content)
        code.configure(state="disabled")

        details = f"SAVED · {path}"
        if truncated:
            details = f"PREVIEW LIMITED TO 1,000,000 CHARACTERS · {details}"
        ctk.CTkLabel(
            window,
            text=details,
            text_color=MUTED,
            font=ctk.CTkFont(family=self.body_family, size=13),
            anchor="w",
            wraplength=640,
        ).grid(row=2, column=0, sticky="ew", padx=12, pady=(3, 10))
        window.lift()
        window.focus_force()

    def _on_close(self) -> None:
        if self._closed:
            return
        self._closed = True
        try:
            self.logger.removeHandler(self._queue_handler)
        except Exception:
            pass
        try:
            self.destroy()
        except Exception:
            traceback.print_exc()
