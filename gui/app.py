"""Protez main window: compact, frameless, pixel-styled.

The window keeps the proven structure (frameless chrome, drag and drop, worker
thread, event queue) but the whole surface is drawn with the pixel toolkit and
the result is opened in :class:`gui.viewer.CodeViewer` instead of a text editor.
"""

from __future__ import annotations

import ctypes
import logging
import os
import platform
import queue
import shutil
import subprocess
import sys
import threading
import tkinter as tk
from pathlib import Path
from tkinter import filedialog

from core.injector_env import DEFAULT_PROFILE_KEY, profile_choices
from core.pipeline import DeobfuscationPipeline, PipelineError, PipelineResult
from core.runtime_paths import ICON_PATH
from core.source_input import SourceInputError, resolve_source_input
from core.version import VERSION
from gui import theme
from gui.logo import ProtezLogo
from gui.pixelkit import (
    PixelButton,
    PixelDropdown,
    PixelEntry,
    PixelLabel,
    PixelPanel,
    PixelProgress,
    PixelTextArea,
    PixelToggle,
    draw_pixel_border,
)
from gui.viewer import CodeViewer

try:  # optional: drag and drop is a convenience, not a requirement
    from tkinterdnd2 import DND_FILES, TkinterDnD
except Exception:  # noqa: BLE001
    TkinterDnD = None
    DND_FILES = None


class _QueueHandler(logging.Handler):
    def __init__(self, records: queue.Queue[logging.LogRecord]):
        super().__init__()
        self.records = records

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.records.put_nowait(record)
        except Exception:  # noqa: BLE001
            self.handleError(record)


class ProtezApp(tk.Tk):
    WINDOW_WIDTH = theme.DEFAULT_WIDTH
    WINDOW_HEIGHT = theme.DEFAULT_HEIGHT
    MIN_WIDTH = theme.MIN_WIDTH
    MIN_HEIGHT = theme.MIN_HEIGHT

    def __init__(self):
        super().__init__()
        self.log_records: queue.Queue[logging.LogRecord] = queue.Queue()
        self.ui_events: queue.Queue[tuple] = queue.Queue()
        self.logger = logging.getLogger("protez")
        self._configure_logger()

        self._worker: threading.Thread | None = None
        self._closed = False
        self._closing = False
        self._shape_pending = False
        self._restore_chrome_after_map = False
        self._drag_offset: tuple[int, int] | None = None
        self._resize_anchor: tuple[int, int, int, int] | None = None
        self._last_result: Path | None = None
        self._pending_bytes: bytes | None = None
        self._pending_name: str | None = None

        self.title("PROTEZ")
        if ICON_PATH.is_file():
            try:
                self.iconbitmap(str(ICON_PATH))
                self.iconbitmap(default=str(ICON_PATH))
            except Exception as exc:  # noqa: BLE001
                self.logger.warning("Could not set the Protez window icon: %s", exc)
        self.overrideredirect(True)
        self.geometry(self._centered_geometry(self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        self.minsize(self.MIN_WIDTH, self.MIN_HEIGHT)
        self.configure(bg=theme.BG)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.bind("<Configure>", self._schedule_native_shape, add="+")
        self.bind("<Map>", self._on_map, add="+")
        self.bind("<Control-Return>", self._start_deobfuscation, add="+")
        self.bind("<Control-o>", lambda _event: self._browse_file(), add="+")

        self.body_family = theme.ui_family()
        self.code_family = theme.code_family()

        self.injector_var = tk.StringVar(value=DEFAULT_PROFILE_KEY)
        self.network_var = tk.BooleanVar(value=True)
        self.script_key_var = tk.StringVar(value="")

        self._build_layout()
        self._enable_drag_and_drop()
        self.after(35, self._apply_native_shape)
        self.after(60, self._poll_ui_events)
        self.logger.info("Protez %s ready — paste source, a loader URL, or drop a file", VERSION)

    # ------------------------------------------------------------------
    # chrome
    # ------------------------------------------------------------------
    def _centered_geometry(self, width: int, height: int) -> str:
        try:
            screen_width = self.winfo_screenwidth()
            screen_height = self.winfo_screenheight()
        except Exception:  # noqa: BLE001
            return f"{width}x{height}"
        x = max(0, (screen_width - width) // 2)
        y = max(0, (screen_height - height) // 3)
        return f"{width}x{height}+{x}+{y}"

    def _configure_logger(self) -> None:
        self.logger.setLevel(logging.DEBUG)
        handler = _QueueHandler(self.log_records)
        handler.setFormatter(logging.Formatter("%(message)s"))
        self.logger.addHandler(handler)

    def _build_layout(self) -> None:
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=3, minsize=150)
        self.grid_rowconfigure(4, weight=2, minsize=96)

        self._build_title_bar()

        source = PixelPanel(self, background=theme.PANEL)
        source.grid(row=1, column=0, sticky="nsew", padx=8, pady=(0, theme.ROW_GAP))
        source.body.grid_columnconfigure(0, weight=1)
        source.body.grid_rowconfigure(1, weight=1)

        header = tk.Frame(source.body, bg=theme.PANEL, highlightthickness=0, bd=0)
        header.grid(row=0, column=0, sticky="ew")
        PixelLabel(header, "SOURCE", ink=theme.ACCENT, background=theme.PANEL, scale=1).pack(side="left")
        PixelLabel(
            header,
            "PASTE · URL · DROP FILE · CTRL+ENTER",
            ink=theme.MUTED,
            background=theme.PANEL,
            scale=1,
        ).pack(side="left", padx=(10, 0))
        PixelButton(
            header,
            "CLEAR",
            self._clear_input,
            accent=theme.MUTED,
            background=theme.PANEL,
            scale=1,
            padding=(7, 4),
        ).pack(side="right")
        PixelButton(
            header,
            "PASTE",
            self._paste_clipboard,
            accent=theme.CYAN,
            background=theme.PANEL,
            scale=1,
            padding=(7, 4),
        ).pack(side="right", padx=(0, 4))
        PixelButton(
            header,
            "FILE",
            self._browse_file,
            accent=theme.CYAN,
            background=theme.PANEL,
            scale=1,
            padding=(7, 4),
        ).pack(side="right", padx=(0, 4))

        self.input_area = PixelTextArea(source.body, background=theme.PANEL, height=7)
        self.input_area.grid(row=1, column=0, sticky="nsew", pady=(6, 0))

        self._build_options_row()
        self._build_action_row()

        log_panel = PixelPanel(self, background=theme.PANEL)
        log_panel.grid(row=4, column=0, sticky="nsew", padx=8, pady=(0, 8))
        log_panel.body.grid_columnconfigure(0, weight=1)
        log_panel.body.grid_rowconfigure(1, weight=1)
        log_header = tk.Frame(log_panel.body, bg=theme.PANEL, highlightthickness=0, bd=0)
        log_header.grid(row=0, column=0, sticky="ew")
        PixelLabel(log_header, "ACTIVITY", ink=theme.ACCENT, background=theme.PANEL, scale=1).pack(
            side="left"
        )
        self.result_button = PixelButton(
            log_header,
            "OPEN RESULT",
            self._open_last_result,
            accent=theme.ACCENT,
            background=theme.PANEL,
            scale=1,
            padding=(7, 4),
        )
        self.result_button.pack(side="right")
        self.result_button.set_enabled(False)

        self.log_view = tk.Text(
            log_panel.body,
            bg=theme.BG_SUNKEN,
            fg=theme.TEXT_DIM,
            relief="flat",
            bd=0,
            highlightthickness=1,
            highlightbackground=theme.BORDER,
            highlightcolor=theme.BORDER,
            wrap="word",
            height=6,
            font=(self.code_family, 9),
            padx=6,
            pady=4,
            state="disabled",
        )
        self.log_view.grid(row=1, column=0, sticky="nsew", pady=(6, 0))
        for level, color in theme.LEVEL_COLORS.items():
            self.log_view.tag_configure(level, foreground=color)
        self.log_view.tag_configure("TIME", foreground=theme.MUTED)

        self.resize_grip = tk.Canvas(self, width=12, height=12, bg=theme.BG, highlightthickness=0, bd=0)
        self.resize_grip.create_rectangle(2, 2, 10, 10, outline=theme.BORDER_BRIGHT, fill="")
        self.resize_grip.place(relx=1.0, rely=1.0, anchor="se")
        self.resize_grip.bind("<ButtonPress-1>", self._begin_resize)
        self.resize_grip.bind("<B1-Motion>", self._resize_window)

    def _build_title_bar(self) -> None:
        bar = tk.Canvas(self, height=34, bg=theme.PANEL, highlightthickness=0, bd=0)
        bar.grid(row=0, column=0, sticky="ew", padx=8, pady=(8, theme.ROW_GAP))
        bar.bind("<Configure>", lambda _event: self._draw_title_bar())
        bar.bind("<ButtonPress-1>", self._begin_window_drag)
        bar.bind("<B1-Motion>", self._drag_window)
        self.title_bar = bar

        self.logo = ProtezLogo(bar, size=22, background=theme.PANEL)
        self.logo.place(x=8, y=6)
        for widget in (bar, self.logo):
            widget.bind("<ButtonPress-1>", self._begin_window_drag, add="+")
            widget.bind("<B1-Motion>", self._drag_window, add="+")

        self.minimize_button = PixelButton(
            bar,
            "−",
            self._minimize_window,
            accent=theme.MUTED,
            background=theme.PANEL,
            scale=1,
            padding=(7, 4),
        )
        self.minimize_button.place(relx=1.0, x=-40, y=6, anchor="ne")
        self.close_button = PixelButton(
            bar,
            "×",
            self._on_close,
            accent=theme.ERROR,
            background=theme.PANEL,
            scale=1,
            padding=(7, 4),
        )
        self.close_button.place(relx=1.0, x=-8, y=6, anchor="ne")

    def _draw_title_bar(self) -> None:
        canvas = self.title_bar
        canvas.delete("chrome")
        width = max(1, canvas.winfo_width())
        height = 34
        canvas.create_rectangle(0, 0, width - 1, height - 1, outline=theme.BORDER, fill=theme.PANEL, tags="chrome")
        canvas.create_rectangle(0, height - 1, width - 1, height - 1, outline="", fill=theme.ACCENT, tags="chrome")
        canvas.create_text(
            38,
            height // 2,
            anchor="w",
            text="PROTEZ",
            fill=theme.TEXT,
            font=(self.body_family, 13, "bold"),
            tags="chrome",
        )
        canvas.create_text(
            108,
            height // 2,
            anchor="w",
            text=f"v{VERSION}  ·  ROBLOX SCRIPT RECOVERY",
            fill=theme.MUTED,
            font=(self.body_family, 8),
            tags="chrome",
        )
        canvas.tag_lower("chrome")

    def _build_options_row(self) -> None:
        row = tk.Frame(self, bg=theme.BG, highlightthickness=0, bd=0)
        row.grid(row=2, column=0, sticky="ew", padx=8, pady=(0, theme.ROW_GAP))
        PixelLabel(row, "INJECTOR", ink=theme.MUTED, background=theme.BG, scale=1).pack(
            side="left", padx=(2, 6)
        )
        self.injector_dropdown = PixelDropdown(
            row,
            values=profile_choices(),
            variable=self.injector_var,
            width=232,
            accent=theme.CYAN,
        )
        self.injector_dropdown.pack(side="left")

        PixelToggle(
            row,
            "FETCH REMOTE PAYLOADS",
            self.network_var,
            background=theme.BG,
        ).pack(side="left", padx=(14, 0))

        PixelLabel(row, "SCRIPT KEY", ink=theme.MUTED, background=theme.BG, scale=1).pack(
            side="left", padx=(14, 6)
        )
        self.script_key_entry = PixelEntry(row, variable=self.script_key_var, width=170)
        self.script_key_entry.pack(side="left", fill="y")

    def _build_action_row(self) -> None:
        row = tk.Frame(self, bg=theme.BG, highlightthickness=0, bd=0)
        row.grid(row=3, column=0, sticky="ew", padx=8, pady=(0, theme.ROW_GAP))
        row.grid_columnconfigure(1, weight=1)

        self.destroy_button = PixelButton(
            row,
            "DESTROY",
            self._start_deobfuscation,
            accent=theme.ACCENT,
            active=True,
            scale=2,
            padding=(14, 8),
        )
        self.destroy_button.grid(row=0, column=0, sticky="w")

        meter = tk.Frame(row, bg=theme.BG, highlightthickness=0, bd=0)
        meter.grid(row=0, column=1, sticky="ew", padx=(12, 0))
        meter.grid_columnconfigure(0, weight=1)
        self.progress = PixelProgress(meter, background=theme.BG)
        self.progress.grid(row=0, column=0, sticky="ew")
        self.status_label = PixelLabel(
            meter,
            "IDLE",
            ink=theme.MUTED,
            background=theme.BG,
            scale=1,
        )
        self.status_label.grid(row=1, column=0, sticky="w", pady=(4, 0))

    # ------------------------------------------------------------------
    # window behaviour
    # ------------------------------------------------------------------
    def _schedule_native_shape(self, _event=None) -> None:
        if sys.platform != "win32" or self._shape_pending or self._closing:
            return
        self._shape_pending = True
        try:
            self.after_idle(self._apply_native_shape)
        except Exception:  # noqa: BLE001
            self._shape_pending = False

    def _apply_native_shape(self) -> None:
        self._shape_pending = False
        if sys.platform != "win32" or self._closing:
            return
        try:
            import ctypes.wintypes
            from ctypes import byref, sizeof

            hwnd = ctypes.c_void_p(self.winfo_id())
            user32 = ctypes.windll.user32
            self._ensure_taskbar_presence(user32, hwnd, ctypes)
            user32.GetWindowRect.argtypes = [ctypes.c_void_p, ctypes.POINTER(ctypes.wintypes.RECT)]
            user32.GetWindowRect.restype = ctypes.c_int
            rect = ctypes.wintypes.RECT()
            if user32.GetWindowRect(hwnd, byref(rect)):
                width = max(1, rect.right - rect.left)
                height = max(1, rect.bottom - rect.top)
            else:
                width = max(1, self.winfo_width())
                height = max(1, self.winfo_height())
            gdi = ctypes.windll.gdi32
            gdi.CreateRectRgn.argtypes = [ctypes.c_int, ctypes.c_int, ctypes.c_int, ctypes.c_int]
            gdi.CreateRectRgn.restype = ctypes.c_void_p
            gdi.SetWindowRgn.argtypes = [ctypes.c_void_p, ctypes.c_void_p, ctypes.c_int]
            gdi.SetWindowRgn.restype = ctypes.c_int
            gdi.DeleteObject.argtypes = [ctypes.c_void_p]
            region = gdi.CreateRectRgn(0, 0, width + 1, height + 1)
            if not region:
                return
            if not gdi.SetWindowRgn(hwnd, region, 1):
                gdi.DeleteObject(region)
            dwm = ctypes.windll.dwmapi
            dwm.DwmSetWindowAttribute.argtypes = [
                ctypes.c_void_p,
                ctypes.c_uint,
                ctypes.c_void_p,
                ctypes.c_uint,
            ]
            border_color = ctypes.c_int(0xFFFFFFFE)
            corner_preference = ctypes.c_int(1)
            dwm.DwmSetWindowAttribute(hwnd, 34, byref(border_color), sizeof(border_color))
            dwm.DwmSetWindowAttribute(hwnd, 33, byref(corner_preference), sizeof(corner_preference))
        except Exception:  # noqa: BLE001
            return

    def _ensure_taskbar_presence(self, user32, hwnd, ctypes_module) -> None:
        try:
            get_style = getattr(user32, "GetWindowLongPtrW", None) or user32.GetWindowLongW
            set_style = getattr(user32, "SetWindowLongPtrW", None) or user32.SetWindowLongW
            get_style.argtypes = [ctypes_module.c_void_p, ctypes_module.c_int]
            get_style.restype = ctypes_module.c_ssize_t
            set_style.argtypes = [ctypes_module.c_void_p, ctypes_module.c_int, ctypes_module.c_ssize_t]
            set_style.restype = ctypes_module.c_ssize_t
            ex_style_index = -20
            app_window = 0x00040000
            tool_window = 0x00000080
            current = get_style(hwnd, ex_style_index)
            desired = (current | app_window) & ~tool_window
            if desired == current:
                return
            set_style(hwnd, ex_style_index, desired)
            user32.SetWindowPos.argtypes = [
                ctypes_module.c_void_p,
                ctypes_module.c_void_p,
                ctypes_module.c_int,
                ctypes_module.c_int,
                ctypes_module.c_int,
                ctypes_module.c_int,
                ctypes_module.c_uint,
            ]
            user32.SetWindowPos.restype = ctypes_module.c_int
            user32.SetWindowPos(hwnd, None, 0, 0, 0, 0, 0x0001 | 0x0002 | 0x0004 | 0x0010 | 0x0020)
        except Exception as exc:  # noqa: BLE001
            self.logger.debug("Taskbar registration skipped: %s", exc)

    def _begin_window_drag(self, event) -> None:
        self._drag_offset = (event.x_root - self.winfo_x(), event.y_root - self.winfo_y())

    def _drag_window(self, event) -> None:
        if self._drag_offset is None:
            return
        self.geometry(f"+{event.x_root - self._drag_offset[0]}+{event.y_root - self._drag_offset[1]}")

    def _begin_resize(self, event) -> None:
        self._resize_anchor = (event.x_root, event.y_root, self.winfo_width(), self.winfo_height())

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
        except Exception:  # noqa: BLE001
            self._restore_chrome_after_map = False
            self.overrideredirect(True)

    def _on_map(self, _event=None) -> None:
        if self._restore_chrome_after_map and self.state() == "normal":
            self._restore_chrome_after_map = False
            self.after_idle(lambda: self.overrideredirect(True))
            self.after(80, self._apply_native_shape)

    def _enable_drag_and_drop(self) -> None:
        if TkinterDnD is None or DND_FILES is None:
            self.logger.debug("Drag and drop unavailable; use the FILE button")
            return
        try:
            TkinterDnD.require(self)
            self.input_area.text.drop_target_register(DND_FILES)
            self.input_area.text.dnd_bind("<<Drop>>", self._on_drop)
            self.logger.debug("File drag and drop ready")
        except Exception as exc:  # noqa: BLE001
            self.logger.debug("Drag and drop unavailable: %s", exc)

    def _on_drop(self, event) -> None:
        raw = getattr(event, "data", "") or ""
        for candidate in self.tk.splitlist(raw):
            path = Path(candidate)
            if path.is_file():
                self._load_file(path)
                break

    # ------------------------------------------------------------------
    # input helpers
    # ------------------------------------------------------------------
    def _browse_file(self) -> None:
        selected = filedialog.askopenfilename(
            parent=self,
            title="Choose a script to analyse",
            filetypes=[
                ("Roblox scripts", "*.lua *.luau *.txt"),
                ("All files", "*.*"),
            ],
        )
        if selected:
            self._load_file(Path(selected))

    def _load_file(self, path: Path) -> None:
        try:
            if path.suffix.lower() in {".luac", ".lbc"}:
                self.logger.info("Binary input is analysed as bytecode: %s", path.name)
                self.input_area.set_text(f"-- binary bytecode input: {path}")
                self._pending_bytes = path.read_bytes()
                self._pending_name = path.name
                return
            text = path.read_text(encoding="utf-8", errors="replace")
        except OSError as exc:
            self.logger.error("Could not read %s: %s", path, exc)
            return
        self._pending_bytes = None
        self._pending_name = path.name
        self.input_area.set_text(text)
        self.logger.info("Loaded %s (%s characters)", path.name, f"{len(text):,}")

    def _paste_clipboard(self) -> None:
        try:
            text = self.clipboard_get()
        except Exception:  # noqa: BLE001
            self.logger.warning("The clipboard does not contain text")
            return
        self.input_area.set_text(text)
        self.logger.info("Pasted %s characters from the clipboard", f"{len(text):,}")

    def _clear_input(self) -> None:
        self.input_area.set_text("")
        self._pending_bytes = None
        self._pending_name = None
        self.status_label.set_text("IDLE", ink=theme.MUTED)
        self.progress.set(0, "IDLE")

    def _open_last_result(self) -> None:
        if self._last_result is not None and self._last_result.is_file():
            try:
                CodeViewer(self, self._last_result, logger=self.logger)
            except Exception:  # noqa: BLE001
                self.logger.exception("Could not open the result viewer")

    # ------------------------------------------------------------------
    # pipeline
    # ------------------------------------------------------------------
    def _start_deobfuscation(self, _event=None) -> str:
        if self._closing or self._closed or (self._worker is not None and self._worker.is_alive()):
            return "break"
        pending_bytes = self._pending_bytes
        if pending_bytes is None and not self.input_area.get_text().strip():
            self.logger.warning("No source or code link was provided")
            self.status_label.set_text("PASTE SOURCE OR URL", ink=theme.WARN)
            return "break"

        if pending_bytes is not None:
            source: str | bytes = pending_bytes
            source_name = self._pending_name or "input.luac"
        else:
            source = self.input_area.get_text()
            source_name = self._pending_name or "pasted input"

        self.destroy_button.set_enabled(False)
        self.result_button.set_enabled(False)
        self.progress.set(2, "STARTING")
        self.status_label.set_text("STARTING", ink=theme.CYAN)
        self.logger.info("Started source processing")
        self._worker = threading.Thread(
            target=self._run_pipeline,
            args=(source, source_name),
            name="protez-deobfuscation",
            daemon=True,
        )
        self._worker.start()
        return "break"

    def _run_pipeline(self, source: str | bytes, source_name: str) -> None:
        try:
            if isinstance(source, bytes):
                resolved_source: str | bytes = source
                resolved_name = source_name
            else:
                self.ui_events.put(("progress", 4, "RESOLVING"))
                resolved = resolve_source_input(source, source_name=source_name, logger=self.logger)
                if resolved.fetched_urls:
                    self.ui_events.put(("progress", 8, "FETCHED"))
                resolved_source = resolved.source
                resolved_name = resolved.source_name

            pipeline = DeobfuscationPipeline(
                logger=self.logger,
                progress_callback=lambda percent, stage: self.ui_events.put(
                    ("progress", percent, stage)
                ),
                injector_profile=self.injector_var.get() or DEFAULT_PROFILE_KEY,
                allow_network=bool(self.network_var.get()),
                script_key=self.script_key_var.get().strip() or None,
            )
            result: PipelineResult = pipeline.run(resolved_source, source_name=resolved_name)
            if result.notice:
                self.logger.warning("Result limitation: %s", result.notice)
            self.ui_events.put(("output", str(result.output_path), result.status))
        except SourceInputError as exc:
            self.logger.error("Could not resolve source input: %s", exc)
            self.ui_events.put(("failed", str(exc)))
        except PipelineError as exc:
            self.logger.error("Processing stopped: %s", exc)
            self.ui_events.put(("failed", str(exc)))
        except Exception:  # noqa: BLE001
            self.logger.exception("Source processing failed")
            self.ui_events.put(("failed", "See the activity log for details"))
        finally:
            self.ui_events.put(("finished",))

    def _poll_ui_events(self) -> None:
        if self._closed or self._closing:
            return
        for _ in range(200):
            try:
                event = self.ui_events.get_nowait()
            except queue.Empty:
                break
            try:
                self._handle_event(event)
            except Exception:  # noqa: BLE001
                self.logger.exception("Could not update the interface")
        self._drain_logs()
        self.after(60, self._poll_ui_events)

    def _handle_event(self, event: tuple) -> None:
        kind = event[0]
        if kind == "progress":
            self.progress.set(event[1], event[2])
            self.status_label.set_text(str(event[2]), ink=theme.CYAN)
        elif kind == "output":
            path = Path(event[1])
            self._last_result = path
            self.progress.set(100, "DONE")
            self.status_label.set_text(f"SAVED {path.name}", ink=theme.ACCENT)
            self.result_button.set_enabled(True)
            self.logger.info("Result: %s", path)
            try:
                CodeViewer(self, path, logger=self.logger)
            except Exception:  # noqa: BLE001
                self.logger.exception("Could not open the result viewer")
        elif kind == "failed":
            self.status_label.set_text(f"FAILED · {event[1]}", ink=theme.ERROR)
            self.progress.set(100, "FAILED")
        elif kind == "finished":
            self.destroy_button.set_enabled(True)

    def _drain_logs(self) -> None:
        for _ in range(400):
            try:
                record = self.log_records.get_nowait()
            except queue.Empty:
                break
            stamp = f"{record.levelname:<7}"
            color = theme.LEVEL_COLORS.get(record.levelname, theme.TEXT_DIM)
            self.log_view.configure(state="normal")
            self.log_view.insert("end", f"{stamp}", record.levelname)
            self.log_view.insert("end", f"{record.getMessage()}\n", record.levelname)
            self.log_view.see("end")
            self.log_view.configure(state="disabled")
            if record.levelno >= logging.WARNING:
                self.log_view.tag_configure(record.levelname, foreground=color)

    # ------------------------------------------------------------------
    def _on_close(self) -> None:
        if self._closed or self._closing:
            return
        self._closing = True
        self._finish_close()

    def _finish_close(self) -> None:
        self._closed = True
        try:
            self.destroy()
        except Exception:  # noqa: BLE001
            pass


def main() -> int:
    app = ProtezApp()
    app.mainloop()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
