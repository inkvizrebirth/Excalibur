from __future__ import annotations

import ctypes
import hashlib
import json
import logging
import os
import queue
import subprocess
import sys
import threading
import tkinter as tk
import traceback
from datetime import datetime
from pathlib import Path
from tkinter import filedialog, messagebox, ttk

from core.version import VERSION

APP_EXE_NAME = "Protez.exe"


def _resource_payload_dir() -> Path:
    root = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent))
    return root / "installer_payload"


def _is_administrator() -> bool:
    if os.name != "nt":
        return False
    try:
        return bool(ctypes.windll.shell32.IsUserAnAdmin())
    except (AttributeError, OSError):
        return False


class _QueueHandler(logging.Handler):
    def __init__(self, records: queue.Queue[logging.LogRecord]):
        super().__init__()
        self.records = records

    def emit(self, record: logging.LogRecord) -> None:
        try:
            self.records.put_nowait(record)
        except Exception:
            self.handleError(record)


class ProtezSetup(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("PROTEZ / INSTALLER")
        self.geometry("820x650")
        self.minsize(700, 540)
        self.configure(bg="#050505")
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self.records: queue.Queue[logging.LogRecord] = queue.Queue()
        self.events: queue.Queue[tuple[str, object]] = queue.Queue()
        self.logger = logging.getLogger("protez.setup")
        self.logger.setLevel(logging.DEBUG)
        self.logger.propagate = False
        self.handler = _QueueHandler(self.records)
        self.logger.addHandler(self.handler)
        self.busy = False

        self._configure_style()
        self._build_layout()
        self.after(60, self._drain)
        self.logger.info("Protez Setup ready")
        self.logger.info("The application is self-contained; no Python, pip, or CMake install is needed")
        if os.name == "nt" and not _is_administrator():
            self.logger.error("Administrator access is required. Close this window and choose Run as administrator.")
            self.status.configure(text="Run the installer as Administrator")
            self.install_button.configure(state="disabled")

    def _configure_style(self) -> None:
        style = ttk.Style(self)
        try:
            style.theme_use("clam")
        except tk.TclError:
            pass
        style.configure("TFrame", background="#050505")
        style.configure("TLabel", background="#050505", foreground="#ededed")
        style.configure("TLabelframe", background="#050505", foreground="#ededed")
        style.configure("TLabelframe.Label", background="#050505", foreground="#ededed")
        style.configure("Muted.TLabel", foreground="#858585")
        style.configure("TCheckbutton", background="#050505", foreground="#dddddd")
        style.map("TCheckbutton", background=[("active", "#050505")])
        style.configure(
            "TButton",
            background="#111111",
            foreground="#f4f4f4",
            bordercolor="#686868",
            padding=(14, 9),
            font=("TkFixedFont", 10, "bold"),
        )
        style.map("TButton", background=[("active", "#eeeeee")], foreground=[("active", "#080808")])
        style.configure("TProgressbar", background="#f1f1f1", troughcolor="#161616", bordercolor="#454545")

    def _build_layout(self) -> None:
        root = ttk.Frame(self, padding=20)
        root.pack(fill="both", expand=True)
        root.columnconfigure(0, weight=1)
        root.rowconfigure(5, weight=1)

        header = ttk.Frame(root)
        header.grid(row=0, column=0, sticky="ew", pady=(0, 14))
        header.columnconfigure(0, weight=1)
        ttk.Label(header, text="PROTEZ", font=("TkFixedFont", 18, "bold")).grid(
            row=0, column=0, sticky="w"
        )
        ttk.Label(
            header,
            text=f"SELF-CONTAINED WINDOWS INSTALLER  /  v{VERSION}",
            style="Muted.TLabel",
        ).grid(row=1, column=0, sticky="w", pady=(5, 0))

        destination = ttk.LabelFrame(root, text=" INSTALL LOCATION ", padding=12)
        destination.grid(row=1, column=0, sticky="ew", pady=(0, 10))
        destination.columnconfigure(0, weight=1)
        self.path = tk.StringVar(value=self._default_path())
        self.path_entry = tk.Entry(
            destination,
            textvariable=self.path,
            bg="#000000",
            fg="#eeeeee",
            insertbackground="#ffffff",
            relief="flat",
            highlightthickness=1,
            highlightbackground="#454545",
            highlightcolor="#aaaaaa",
            font=("TkFixedFont", 10),
        )
        self.path_entry.grid(row=0, column=0, sticky="ew", padx=(0, 8), ipady=8)
        self.browse_button = ttk.Button(destination, text="BROWSE…", command=self._browse)
        self.browse_button.grid(row=0, column=1, sticky="e")

        options = ttk.Frame(root)
        options.grid(row=2, column=0, sticky="ew", pady=(0, 10))
        self.desktop_shortcut = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            options,
            text="Create a desktop shortcut (Start Menu shortcut is always created)",
            variable=self.desktop_shortcut,
        ).pack(anchor="w")
        ttk.Label(
            options,
            text="Protez requests Administrator access when launched; Windows may show a confirmation prompt.",
            style="Muted.TLabel",
            wraplength=750,
        ).pack(anchor="w", pady=(6, 0))

        self.status = ttk.Label(root, text="Choose a folder, then install or repair Protez.")
        self.status.grid(row=3, column=0, sticky="w", pady=(0, 7))
        self.progress = ttk.Progressbar(root, mode="determinate", maximum=100)
        self.progress.grid(row=4, column=0, sticky="ew", pady=(0, 10))

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
        self.log.grid(row=5, column=0, sticky="nsew", pady=(0, 12))
        self.log.tag_configure("INFO", foreground="#e1e1e1")
        self.log.tag_configure("WARNING", foreground="#bbbbbb")
        self.log.tag_configure("ERROR", foreground="#ffffff")
        self.log.tag_configure("DEBUG", foreground="#777777")

        footer = ttk.Frame(root)
        footer.grid(row=6, column=0, sticky="ew")
        footer.columnconfigure(0, weight=1)
        self.result_hint = ttk.Label(
            footer,
            text="Setup repairs the installation by safely replacing damaged app files.",
            style="Muted.TLabel",
        )
        self.result_hint.grid(row=0, column=0, sticky="w")
        self.install_button = ttk.Button(footer, text="INSTALL / REPAIR", command=self._install)
        self.install_button.grid(row=0, column=1, sticky="e")
        self.close_button = ttk.Button(footer, text="CLOSE", command=self._on_close)
        self.close_button.grid(row=0, column=2, sticky="e", padx=(8, 0))

    @staticmethod
    def _default_path() -> str:
        program_files = os.environ.get("ProgramFiles")
        if program_files:
            return str(Path(program_files) / "Protez")
        local = os.environ.get("LOCALAPPDATA")
        if local:
            return str(Path(local) / "Programs" / "Protez")
        return str(Path.home() / "Protez")

    def _browse(self) -> None:
        selected = filedialog.askdirectory(
            parent=self,
            title="Choose Protez installation folder",
            initialdir=self.path.get() or str(Path.home()),
            mustexist=False,
        )
        if selected:
            self.path.set(selected)

    def _install(self) -> None:
        if self.busy:
            return
        if os.name == "nt" and not _is_administrator():
            self.logger.error("Installation cancelled: start Protez-Setup.exe as Administrator")
            return
        raw_path = self.path.get().strip().strip('"')
        if not raw_path:
            self.logger.error("Choose an installation folder first")
            return
        try:
            install_path = Path(raw_path).expanduser().resolve()
        except (OSError, RuntimeError) as exc:
            self.logger.exception("Invalid installation path: %s", exc)
            return
        if install_path == install_path.parent:
            self.logger.error("Installing directly into a drive root is not allowed")
            return

        self.busy = True
        self.progress.configure(value=0, mode="indeterminate")
        self.progress.start(12)
        self.status.configure(text="Installing Protez…")
        self.install_button.configure(state="disabled")
        self.browse_button.configure(state="disabled")
        self.path_entry.configure(state="disabled")
        self.close_button.configure(state="disabled")
        self.logger.info("Install destination: %s", install_path)
        worker = threading.Thread(
            target=self._install_worker,
            args=(install_path, self.desktop_shortcut.get()),
            name="protez-installer-worker",
            daemon=True,
        )
        worker.start()

    def _install_worker(self, install_path: Path, desktop: bool) -> None:
        try:
            payload_dir = _resource_payload_dir()
            executable = payload_dir / APP_EXE_NAME
            manifest_path = payload_dir / "manifest.json"
            manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
            expected_hash = str(manifest.get("sha256", ""))
            expected_size = int(manifest.get("size_bytes", 0))
            version = str(manifest.get("version", "unknown"))
            if not executable.is_file() or not expected_hash or expected_size <= 0:
                raise RuntimeError("The embedded application payload is incomplete")

            actual_size = executable.stat().st_size
            if actual_size != expected_size or self._hash_file(executable) != expected_hash:
                raise RuntimeError("The embedded application failed its SHA-256 integrity check")
            self.logger.info("Verified embedded Protez %s (%s bytes)", version, f"{actual_size:,}")

            install_path.mkdir(parents=True, exist_ok=True)
            destination = install_path / APP_EXE_NAME
            temporary = install_path / (APP_EXE_NAME + ".installing")
            self.logger.info("Copying self-contained application")
            self._copy_with_progress(executable, temporary, actual_size)
            copied_hash = self._hash_file(temporary)
            if copied_hash != expected_hash:
                temporary.unlink(missing_ok=True)
                raise RuntimeError("Copied app checksum mismatch; the previous installation was left untouched")
            try:
                os.replace(temporary, destination)
            except OSError as exc:
                temporary.unlink(missing_ok=True)
                raise RuntimeError(
                    f"Could not replace {destination}. Close Protez if it is running, then retry. ({exc})"
                ) from exc
            self.logger.info("Installed Protez.exe (%s)", version)

            metadata = {
                "version": version,
                "installed_at": datetime.now().astimezone().isoformat(timespec="seconds"),
                "executable": str(destination),
            }
            (install_path / "install.json").write_text(
                json.dumps(metadata, indent=2) + "\n", encoding="utf-8"
            )
            self._create_shortcuts(destination, desktop)
            self.events.put(("success", destination))
        except Exception as exc:
            self.logger.exception("Installation failed")
            self.events.put(("failure", str(exc)))

    def _copy_with_progress(self, source: Path, destination: Path, size: int) -> None:
        copied = 0
        with source.open("rb") as source_file, destination.open("wb") as destination_file:
            while True:
                block = source_file.read(1024 * 1024)
                if not block:
                    break
                destination_file.write(block)
                copied += len(block)
                self.events.put(("progress", int(copied * 100 / max(1, size))))
            destination_file.flush()
            os.fsync(destination_file.fileno())

    @staticmethod
    def _hash_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as source:
            for block in iter(lambda: source.read(1024 * 1024), b""):
                digest.update(block)
        return digest.hexdigest()

    def _create_shortcuts(self, executable: Path, desktop: bool) -> None:
        if os.name != "nt":
            self.logger.warning("Windows shortcuts are only available on Windows")
            return
        start_menu = Path(os.environ.get("APPDATA", Path.home())) / "Microsoft" / "Windows" / "Start Menu" / "Programs"
        links = [(start_menu / "Protez.lnk", "Start Menu")]
        if desktop:
            links.append((Path(os.environ.get("USERPROFILE", Path.home())) / "Desktop" / "Protez.lnk", "Desktop"))
        system_root = Path(os.environ.get("SystemRoot", r"C:\Windows"))
        powershell_path = system_root / "System32" / "WindowsPowerShell" / "v1.0" / "powershell.exe"
        if not powershell_path.is_file():
            self.logger.warning("Windows PowerShell was not found; app installed, but shortcuts could not be created")
            return
        powershell = str(powershell_path)

        script = (
            "$ErrorActionPreference='Stop';"
            "$w=New-Object -ComObject WScript.Shell;"
            "$s=$w.CreateShortcut($env:PROTEZ_LINK);"
            "$s.TargetPath=$env:PROTEZ_EXE;"
            "$s.WorkingDirectory=(Split-Path -Parent $env:PROTEZ_EXE);"
            "$s.IconLocation=$env:PROTEZ_EXE;"
            "$s.Save()"
        )
        for link_path, label in links:
            try:
                link_path.parent.mkdir(parents=True, exist_ok=True)
                environment = os.environ.copy()
                environment["PROTEZ_LINK"] = str(link_path)
                environment["PROTEZ_EXE"] = str(executable)
                command = [powershell, "-NoProfile", "-NonInteractive", "-Command", script]
                self.logger.info("Creating %s shortcut", label)
                result = subprocess.run(
                    command,
                    env=environment,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    text=True,
                    encoding="utf-8",
                    errors="replace",
                    timeout=25,
                    check=False,
                    creationflags=getattr(subprocess, "CREATE_NO_WINDOW", 0),
                )
                for line in (result.stdout or "").splitlines():
                    self.logger.info("PowerShell: %s", line[:1000])
                if result.returncode != 0:
                    self.logger.warning("Could not create %s shortcut (exit %s)", label, result.returncode)
                else:
                    self.logger.info("%s shortcut created", label)
            except (OSError, subprocess.TimeoutExpired) as exc:
                self.logger.warning("Could not create %s shortcut: %s", label, exc)

    def _drain(self) -> None:
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
            if event == "progress":
                self.progress.stop()
                self.progress.configure(mode="determinate", value=int(payload))
            elif event == "success":
                self.busy = False
                self.progress.stop()
                self.progress.configure(mode="determinate", value=100)
                self.status.configure(text="Installation complete")
                self.result_hint.configure(
                    text=f"Installed to {payload}. Close setup; Protez will request Administrator approval when started."
                )
                self.install_button.configure(text="REPAIR / REINSTALL", state="normal")
                self.browse_button.configure(state="normal")
                self.path_entry.configure(state="normal")
                self.close_button.configure(state="normal")
                self.logger.info("Setup complete. Protez requests Administrator approval when launched.")
            else:
                self.busy = False
                self.progress.stop()
                self.progress.configure(mode="determinate", value=0)
                self.status.configure(text=f"Install/repair failed: {payload}")
                self.result_hint.configure(text="See the detailed log. You can repair and retry from this window.")
                self.install_button.configure(state="normal")
                self.browse_button.configure(state="normal")
                self.path_entry.configure(state="normal")
                self.close_button.configure(state="normal")
        try:
            self.after(60, self._drain)
        except tk.TclError:
            pass

    def _on_close(self) -> None:
        if self.busy:
            self.status.configure(text="Installation is in progress; wait before closing this window.")
            return
        self.logger.removeHandler(self.handler)
        self.destroy()


def main() -> int:
    if os.name != "nt":
        print("The Protez Setup executable is for Windows.")
        return 1
    try:
        app = ProtezSetup()
        app.mainloop()
        return 0
    except Exception as exc:
        if sys.stderr is not None:
            traceback.print_exc()
        try:
            messagebox.showerror("Protez Setup", f"The installer could not open:\n{exc}")
        except tk.TclError:
            pass
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
