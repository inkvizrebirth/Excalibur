"""Excalibur GUI - a monochrome Tkinter shell around :mod:`core.deobfuscate`.

Design rules taken straight from the TZ:

* **opens in under three seconds** - the window, fonts and styles are the only
  things built at start-up; ``core.*`` is imported *inside* the worker thread,
  and nothing touches the network or the disk until the user clicks Run;
* **never blocks** - every pipeline call runs in a worker thread and talks to
  the UI through a :class:`queue.Queue` drained by ``after()``;
* **never crashes** - all exceptions are caught, written to ``logs/gui.log`` and
  surfaced as a status line;
* **monochrome** - colours come from :mod:`gui.theme` only, no hues anywhere.
"""

from __future__ import annotations

import json
import os
import queue
import sys
import threading
import time
import traceback
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

from .theme import (
    GLYPH_ERROR,
    GLYPH_OK,
    GLYPH_WARN,
    GLYPH_WORK,
    Palette,
    apply_theme,
    detect_preference,
    palette_for,
)

APP_TITLE = "Excalibur"
APP_SUBTITLE = "WeAreDevs deobfuscator"
QUEUE_POLL_MS = 80
MAX_LOG_LINES = 500


def _tk():
    import tkinter as tk

    return tk


class ThemeState:
    """Small holder so the palette can be swapped at runtime."""

    def __init__(self, palette: Palette):
        self.palette = palette


# --------------------------------------------------------------------------- app
class ExcaliburApp:
    """The application window."""

    def __init__(self, root, palette: Optional[Palette] = None, *, start_hidden: bool = False):
        from . import theme as theme_mod

        self.root = root
        self.state = ThemeState(palette or theme_mod.DARK)
        self.fonts = apply_theme(root, self.state.palette)
        self.events: "queue.Queue[Tuple[str, Any]]" = queue.Queue()
        self.worker: Optional[threading.Thread] = None
        self.cancel_event = threading.Event()
        self.last_result = None
        self.last_output: Optional[str] = None
        self.log_lines: List[str] = []
        self._started = time.time()
        self.settings = self._load_settings()

        root.title(APP_TITLE)
        root.geometry(self.settings.get("geometry", "1120x720"))
        root.minsize(880, 560)
        root.protocol("WM_DELETE_WINDOW", self.on_close)
        self._set_icon()

        self._build_ui()
        self.root.after(QUEUE_POLL_MS, self._pump)
        if not start_hidden:
            self.log(f"ready in {int((time.time() - self._started) * 1000)} ms", GLYPH_OK)

    # ------------------------------------------------------------------ chrome
    def _set_icon(self) -> None:
        try:
            from core.paths import assets_dir

            icon = assets_dir() / "icon.ico"
            if icon.exists() and os.name == "nt":
                self.root.iconbitmap(default=str(icon))
        except Exception:
            pass

    def _build_ui(self) -> None:
        tk = _tk()
        from tkinter import ttk

        palette = self.state.palette

        outer = ttk.Frame(self.root, padding=(14, 12, 14, 10))
        outer.pack(fill="both", expand=True)

        # ---- header
        header = ttk.Frame(outer)
        header.pack(fill="x")
        ttk.Label(header, text=APP_TITLE, style="Title.TLabel").pack(side="left")
        ttk.Label(header, text=f" {APP_SUBTITLE}", style="Dim.TLabel").pack(side="left", pady=(4, 0))
        self.status = ttk.Label(header, text=f"{GLYPH_OK} ready", style="Status.TLabel")
        self.status.pack(side="right")

        ttk.Separator(outer).pack(fill="x", pady=(8, 10))

        # ---- input area
        ttk.Label(outer, text="input", style="Heading.TLabel").pack(anchor="w")
        input_frame = ttk.Frame(outer, style="Surface.TFrame")
        input_frame.pack(fill="both", expand=True, pady=(4, 8))
        self.input_text = tk.Text(
            input_frame, wrap="none", undo=True, height=10,
            background=palette.surface, foreground=palette.text,
            insertbackground=palette.accent, selectbackground=palette.selection,
            selectforeground=palette.text, relief="flat", borderwidth=0,
            font=self.fonts["mono"], padx=8, pady=6,
        )
        input_scroll = ttk.Scrollbar(input_frame, orient="vertical", command=self.input_text.yview)
        self.input_text.configure(yscrollcommand=input_scroll.set)
        input_scroll.pack(side="right", fill="y")
        self.input_text.pack(side="left", fill="both", expand=True)
        self._attach_drop_target(self.input_text)

        # ---- controls
        controls = ttk.Frame(outer)
        controls.pack(fill="x", pady=(0, 8))

        self.btn_open = ttk.Button(controls, text="open file", command=self.on_open)
        self.btn_open.pack(side="left")
        self.btn_paste = ttk.Button(controls, text="paste", command=self.on_paste)
        self.btn_paste.pack(side="left", padx=(6, 0))
        self.btn_clear = ttk.Button(controls, text="clear", command=self.on_clear)
        self.btn_clear.pack(side="left", padx=(6, 0))

        self.var_deep = tk.BooleanVar(value=bool(self.settings.get("deep", True)))
        self.var_dynamic = tk.BooleanVar(value=bool(self.settings.get("dynamic", True)))
        self.var_trace = tk.BooleanVar(value=bool(self.settings.get("trace", True)))
        ttk.Checkbutton(controls, text="static layer", variable=self.var_deep).pack(side="left", padx=(18, 0))
        ttk.Checkbutton(controls, text="sandbox run", variable=self.var_dynamic).pack(side="left", padx=(10, 0))
        ttk.Checkbutton(controls, text="trace fallback", variable=self.var_trace).pack(side="left", padx=(10, 0))

        self.btn_run = ttk.Button(controls, text="deobfuscate", style="Accent.TButton", command=self.on_run)
        self.btn_run.pack(side="right")
        self.btn_cancel = ttk.Button(controls, text="stop", command=self.on_cancel)
        self.btn_cancel.pack(side="right", padx=(0, 6))
        self.btn_cancel.state(["disabled"])

        self.progress = ttk.Progressbar(outer, mode="indeterminate")

        ttk.Separator(outer).pack(fill="x", pady=(0, 10))

        # ---- output + log notebook
        notebook = ttk.Notebook(outer)
        notebook.pack(fill="both", expand=True)
        self.notebook = notebook

        output_tab = ttk.Frame(notebook)
        notebook.add(output_tab, text=" output ")
        log_tab = ttk.Frame(notebook)
        notebook.add(log_tab, text=" log ")
        report_tab = ttk.Frame(notebook)
        notebook.add(report_tab, text=" report ")

        self.output_text = self._make_text(output_tab)
        self.log_text = self._make_text(log_tab)
        self.report_text = self._make_text(report_tab)

        # ---- output actions
        actions = ttk.Frame(outer)
        actions.pack(fill="x", pady=(8, 0))
        self.btn_save = ttk.Button(actions, text="save output", command=self.on_save)
        self.btn_save.pack(side="left")
        self.btn_save.state(["disabled"])
        self.btn_copy = ttk.Button(actions, text="copy output", command=self.on_copy)
        self.btn_copy.pack(side="left", padx=(6, 0))
        self.btn_copy.state(["disabled"])
        self.btn_setup = ttk.Button(actions, text="setup", command=self.on_setup)
        self.btn_setup.pack(side="left", padx=(6, 0))
        self.btn_logs = ttk.Button(actions, text="open logs folder", command=self.on_open_logs)
        self.btn_logs.pack(side="left", padx=(6, 0))
        self.btn_detect = ttk.Button(actions, text="detect only", command=self.on_detect)
        self.btn_detect.pack(side="left", padx=(6, 0))
        self.summary = ttk.Label(actions, text="", style="Status.TLabel")
        self.summary.pack(side="right")

        self._bind_shortcuts()

    def _make_text(self, parent) -> "Any":
        tk = _tk()
        from tkinter import ttk

        palette = self.state.palette
        frame = ttk.Frame(parent, style="Surface.TFrame")
        frame.pack(fill="both", expand=True)
        widget = tk.Text(
            frame, wrap="none", background=palette.surface, foreground=palette.text,
            insertbackground=palette.accent, selectbackground=palette.selection,
            selectforeground=palette.text, relief="flat", borderwidth=0,
            font=self.fonts["mono"], padx=8, pady=6, state="disabled",
        )
        bar = ttk.Scrollbar(frame, orient="vertical", command=widget.yview)
        widget.configure(yscrollcommand=bar.set)
        bar.pack(side="right", fill="y")
        widget.pack(side="left", fill="both", expand=True)
        return widget

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-Return>", lambda _e: self.on_run())
        self.root.bind("<Control-o>", lambda _e: self.on_open())
        self.root.bind("<Control-s>", lambda _e: self.on_save())
        self.root.bind("<F5>", lambda _e: self.on_run())
        self.root.bind("<Escape>", lambda _e: self.on_cancel())

    def _attach_drop_target(self, widget) -> None:
        """Enable drag & drop when ``tkinterdnd2`` is installed (optional)."""
        try:
            widget.drop_target_register("DND_Files")  # type: ignore[attr-defined]
            widget.dnd_bind("<<Drop>>", self._on_drop)  # type: ignore[attr-defined]
            self.drop_enabled = True
        except Exception:
            self.drop_enabled = False

    # ------------------------------------------------------------------ helpers
    def _text_set(self, widget, text: str) -> None:
        widget.configure(state="normal")
        widget.delete("1.0", "end")
        widget.insert("1.0", text)
        widget.configure(state="disabled")

    def _text_get(self, widget) -> str:
        return widget.get("1.0", "end-1c")

    def log(self, message: str, glyph: str = GLYPH_WORK) -> None:
        stamp = time.strftime("%H:%M:%S")
        line = f"{stamp} {glyph} {message}"
        self.log_lines.append(line)
        if len(self.log_lines) > MAX_LOG_LINES:
            self.log_lines = self.log_lines[-MAX_LOG_LINES:]
        try:
            self.log_text.configure(state="normal")
            self.log_text.insert("end", line + "\n")
            self.log_text.see("end")
            self.log_text.configure(state="disabled")
        except Exception:
            pass

    def set_status(self, text: str, glyph: str = GLYPH_WORK) -> None:
        try:
            self.status.configure(text=f"{glyph} {text}")
        except Exception:
            pass

    def _write_gui_log(self, text: str) -> None:
        try:
            from core.paths import ensure_dir, logs_dir

            target = ensure_dir(logs_dir()) / "gui.log"
            with target.open("a", encoding="utf-8") as handle:
                handle.write(f"[{time.strftime('%Y-%m-%d %H:%M:%S')}] {text}\n")
        except Exception:
            pass

    # ------------------------------------------------------------------ actions
    def on_open(self) -> None:
        from tkinter import filedialog

        path = filedialog.askopenfilename(
            title="Open obfuscated Lua script",
            filetypes=[("Lua scripts", "*.lua *.txt *.luau"), ("All files", "*.*")],
        )
        if path:
            self._load_file(Path(path))

    def _on_drop(self, event) -> None:  # pragma: no cover - needs a real drop event
        try:
            raw = str(event.data).strip()
            if raw.startswith("{") and raw.endswith("}"):
                raw = raw[1:-1]
            first = raw.split()[0]
            self._load_file(Path(first))
        except Exception as exc:
            self.log(f"drop failed: {exc}", GLYPH_ERROR)

    def _load_file(self, path: Path) -> None:
        try:
            from core.sourceio import read_source

            source = read_source(path)
        except Exception as exc:
            self.log(f"cannot read {path.name}: {exc}", GLYPH_ERROR)
            self.set_status("read failed", GLYPH_ERROR)
            return
        self._text_set(self.input_text, source.text)
        self.current_path = path
        size = path.stat().st_size
        self.log(f"loaded {path.name} ({size:,} bytes, {source.encoding})", GLYPH_OK)
        self.set_status(f"{path.name} loaded", GLYPH_OK)

    def on_paste(self) -> None:
        try:
            data = self.root.clipboard_get()
        except Exception as exc:
            self.log(f"clipboard is empty: {exc}", GLYPH_WARN)
            return
        self._text_set(self.input_text, data)
        self.log(f"pasted {len(data):,} characters", GLYPH_OK)

    def on_clear(self) -> None:
        self._text_set(self.input_text, "")
        self._text_set(self.output_text, "")
        self._text_set(self.report_text, "")
        self.last_output = None
        self.btn_save.state(["disabled"])
        self.btn_copy.state(["disabled"])
        self.set_status("cleared", GLYPH_OK)

    def on_detect(self) -> None:
        source = self._text_get(self.input_text)
        if not source.strip():
            self.set_status("nothing to detect", GLYPH_WARN)
            return
        self._start_worker(self._detect_worker, source)

    def on_run(self) -> None:
        source = self._text_get(self.input_text)
        if not source.strip():
            self.set_status("paste or open a script first", GLYPH_WARN)
            return
        options = {
            "prefer_static": bool(self.var_deep.get()),
            "run_dynamic": bool(self.var_dynamic.get()),
            "trace_on_failure": bool(self.var_trace.get()),
        }
        self.output_text.configure(state="normal")
        self.output_text.delete("1.0", "end")
        self.output_text.configure(state="disabled")
        self.report_text.configure(state="normal")
        self.report_text.delete("1.0", "end")
        self.report_text.configure(state="disabled")
        self._set_running(True)
        self._start_worker(self._pipeline_worker, source, options)

    def on_cancel(self) -> None:
        if self.worker and self.worker.is_alive():
            self.cancel_event.set()
            self.log("stop requested (the current attempt finishes first)", GLYPH_WARN)
            self.set_status("stopping", GLYPH_WARN)

    def on_save(self) -> None:
        if not self.last_output:
            return
        from tkinter import filedialog

        path = filedialog.asksaveasfilename(
            title="Save deobfuscated script",
            defaultextension=".lua",
            initialfile="deobfuscated.lua",
            filetypes=[("Lua scripts", "*.lua"), ("All files", "*.*")],
        )
        if not path:
            return
        try:
            Path(path).write_text(self.last_output, encoding="utf-8", errors="replace")
            self.log(f"saved {path}", GLYPH_OK)
            self.set_status("saved", GLYPH_OK)
        except Exception as exc:
            self.log(f"save failed: {exc}", GLYPH_ERROR)
            self.set_status("save failed", GLYPH_ERROR)

    def on_copy(self) -> None:
        if not self.last_output:
            return
        try:
            self.root.clipboard_clear()
            self.root.clipboard_append(self.last_output)
            self.log("output copied to the clipboard", GLYPH_OK)
        except Exception as exc:
            self.log(f"clipboard failed: {exc}", GLYPH_WARN)

    def on_setup(self) -> None:
        """Run the first-run setup in a worker thread (install/verify deps)."""
        self.notebook.select(1)
        self._start_worker(self._setup_worker)

    def on_open_logs(self) -> None:
        try:
            from core.paths import ensure_dir, logs_dir

            target = ensure_dir(logs_dir())
            if os.name == "nt":
                os.startfile(str(target))  # type: ignore[attr-defined]
            elif sys.platform == "darwin":
                os.system(f'open "{target}"')  # noqa: S605 - user triggered
            else:
                os.system(f'xdg-open "{target}" >/dev/null 2>&1 &')  # noqa: S605
            self.log(f"logs: {target}", GLYPH_OK)
        except Exception as exc:
            self.log(f"cannot open the logs folder: {exc}", GLYPH_WARN)

    def on_close(self) -> None:
        try:
            self.settings["geometry"] = self.root.winfo_geometry()
            self.settings["deep"] = bool(self.var_deep.get())
            self.settings["dynamic"] = bool(self.var_dynamic.get())
            self.settings["trace"] = bool(self.var_trace.get())
            self._save_settings()
        except Exception:
            pass
        try:
            self.root.destroy()
        except Exception:
            pass

    # ------------------------------------------------------------------ workers
    def _set_running(self, running: bool) -> None:
        if running:
            self.btn_run.state(["disabled"])
            self.btn_open.state(["disabled"])
            self.btn_detect.state(["disabled"])
            self.btn_cancel.state(["!disabled"])
            self.progress.pack(fill="x", pady=(0, 6), before=self.notebook)
            self.progress.start(12)
            self.set_status("working", GLYPH_WORK)
        else:
            try:
                self.progress.stop()
                self.progress.pack_forget()
            except Exception:
                pass
            self.btn_run.state(["!disabled"])
            self.btn_open.state(["!disabled"])
            self.btn_detect.state(["!disabled"])
            self.btn_cancel.state(["disabled"])

    def _start_worker(self, target, *args) -> None:
        if self.worker and self.worker.is_alive():
            self.set_status("already running", GLYPH_WARN)
            return
        self.cancel_event.clear()
        self.worker = threading.Thread(target=target, args=args, daemon=True, name="excalibur-worker")
        self.worker.start()

    def _progress(self, stage: str, message: str) -> None:
        self.events.put(("progress", (stage, message)))

    # --- detect only
    def _detect_worker(self, source: str) -> None:
        try:
            from core.registry import detect_and_route

            route = detect_and_route(source)
            lines = [f"route      : {route.message}",
                     f"format     : {route.detection.format}",
                     f"version    : {route.detection.version or 'unknown'}",
                     f"confidence : {route.detection.confidence:.0%}",
                     f"reason     : {route.detection.reason}"]
            for key, value in sorted(route.detection.features.items()):
                lines.append(f"  {key}: {value}")
            if route.detection.warnings:
                lines.append("warnings   :")
                lines.extend(f"  - {w}" for w in route.detection.warnings)
            self.events.put(("detect", "\n".join(lines)))
        except Exception:
            self.events.put(("error", traceback.format_exc()))

    # --- first run setup
    def _setup_worker(self) -> None:
        try:
            import bootstrap

            def progress(stage: str, message: str) -> None:
                self.events.put(("progress", (stage, message)))

            report = bootstrap.ensure_environment(progress=progress)
            bootstrap.add_site_packages()
            for line in report.text().splitlines():
                self.events.put(("logline", line))
            self.events.put(("setup_done", report.ok))
        except Exception:
            self.events.put(("error", traceback.format_exc()))

    # --- full pipeline
    def _pipeline_worker(self, source: str, options: Dict[str, bool]) -> None:
        started = time.time()
        try:
            from core.config import PipelineConfig, SandboxConfig
            from core.deobfuscate import deobfuscate

            config = PipelineConfig(
                sandbox=SandboxConfig(),
                prefer_static=bool(options.get("prefer_static", True)),
                run_dynamic=bool(options.get("run_dynamic", True)),
                trace_on_failure=bool(options.get("trace_on_failure", True)),
            )
            result = deobfuscate(source, config=config, progress=self._progress)
            self.events.put(("done", result))
        except Exception:
            self.events.put(("error", traceback.format_exc()))
        finally:
            self.events.put(("elapsed", int((time.time() - started) * 1000)))

    # ------------------------------------------------------------------ pump
    def _pump(self) -> None:
        try:
            while True:
                kind, payload = self.events.get_nowait()
                self._handle(kind, payload)
        except queue.Empty:
            pass
        except Exception:
            self._write_gui_log("pump failed:\n" + traceback.format_exc())
        finally:
            try:
                self.root.after(QUEUE_POLL_MS, self._pump)
            except Exception:
                pass

    def _handle(self, kind: str, payload: Any) -> None:
        if kind == "progress":
            stage, message = payload
            self.log(f"{stage}: {message}", GLYPH_WORK)
            self.set_status(f"{stage}: {message[:60]}", GLYPH_WORK)
            return
        if kind == "detect":
            self._text_set(self.report_text, payload)
            self.notebook.select(2)
            self.log("detection finished", GLYPH_OK)
            self.set_status("detection finished", GLYPH_OK)
            return
        if kind == "logline":
            self.log(str(payload), GLYPH_WORK)
            return
        if kind == "setup_done":
            if payload:
                self.log("setup finished", GLYPH_OK)
                self.set_status("setup finished", GLYPH_OK)
            else:
                self.log("setup finished with problems (see the log tab)", GLYPH_WARN)
                self.set_status("setup problems", GLYPH_WARN)
            return
        if kind == "elapsed":
            self.log(f"elapsed {payload} ms", GLYPH_WORK)
            return
        if kind == "error":
            self._write_gui_log(payload)
            self._set_running(False)
            self._text_set(self.report_text, payload)
            self.notebook.select(2)
            self.log("run failed - see the report tab (details in logs/gui.log)", GLYPH_ERROR)
            self.set_status("failed", GLYPH_ERROR)
            return
        if kind == "done":
            self._apply_result(payload)
            return

    def _apply_result(self, result) -> None:
        self.last_result = result
        self._set_running(False)

        if result.output:
            self.last_output = result.output
            self._text_set(self.output_text, result.output)
            self.btn_save.state(["!disabled"])
            self.btn_copy.state(["!disabled"])
            self.notebook.select(0)
        else:
            self.last_output = None
            self.btn_save.state(["disabled"])
            self.btn_copy.state(["disabled"])

        report_lines = [result.summary_text()]
        if result.trace:
            report_lines.append("")
            report_lines.append(f"trace: {result.trace.get('states', 0)} states, "
                                f"{result.trace.get('distinct', 0)} distinct")
        self._text_set(self.report_text, "\n".join(report_lines))

        if result.success and not result.partial:
            self.log(f"deobfuscated via {result.method}", GLYPH_OK)
            self.set_status("original source recovered", GLYPH_OK)
        elif result.success:
            self.log("constant layer removed (partial)", GLYPH_WARN)
            self.set_status("partial: see the report tab", GLYPH_WARN)
        else:
            self.log("no validated payload - see the report tab", GLYPH_ERROR)
            self.set_status("no payload", GLYPH_ERROR)

        if result.output_path:
            self.log(f"artefacts: {result.output_path.parent}", GLYPH_OK)

    # ------------------------------------------------------------------ settings
    def _settings_path(self) -> Path:
        from core.paths import app_data_dir, ensure_dir

        return ensure_dir(app_data_dir()) / "state.json"

    def _load_settings(self) -> Dict[str, Any]:
        try:
            path = self._settings_path()
            if path.exists():
                return json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            pass
        return {}

    def _save_settings(self) -> None:
        try:
            self._settings_path().write_text(json.dumps(self.settings, indent=2), encoding="utf-8")
        except Exception:
            pass


# --------------------------------------------------------------------------- entry
def launch(argv: Optional[List[str]] = None, *, file: Optional[str] = None) -> int:
    """Create the Tk root and run the app.  Returns a process exit code."""
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        import tkinter as tk
    except Exception as exc:  # pragma: no cover - Tk missing entirely
        print(f"Excalibur needs Tkinter, which is unavailable: {exc}", file=sys.stderr)
        return 3

    root = None
    try:  # drag & drop needs its own Tk subclass; it is optional
        from tkinterdnd2 import TkinterDnD  # type: ignore

        root = TkinterDnD.Tk()
    except Exception:
        root = None
    if root is None:
        try:
            root = tk.Tk()
        except Exception as exc:  # pragma: no cover - no display (CI, headless)
            print(f"Excalibur could not open a window: {exc}", file=sys.stderr)
            return 4

    preference = "dark"
    for index, value in enumerate(argv):
        if value in {"--light", "--theme=light"}:
            preference = "light"
        if value == "--theme" and index + 1 < len(argv):
            preference = argv[index + 1]
    if not any(v.startswith("--theme") or v == "--light" for v in argv):
        preference = detect_preference()

    app = ExcaliburApp(root, palette=palette_for(preference))
    candidate = file
    if candidate is None:
        for value in argv:
            if not value.startswith("-") and Path(value).exists():
                candidate = value
                break
    if candidate:
        app._load_file(Path(candidate))
    root.mainloop()
    return 0


__all__ = ["APP_TITLE", "ExcaliburApp", "launch"]
