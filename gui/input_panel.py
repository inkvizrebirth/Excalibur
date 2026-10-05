from __future__ import annotations

import logging
import re
from pathlib import Path
from tkinter import filedialog

import customtkinter as ctk

from gui.theme import BG, BORDER, INPUT_BG, MUTED, NEON, PANEL, TEXT, TerminalButton

LOGGER = logging.getLogger("protez")
BYTECODE_EXTENSIONS = {".luac", ".lbc", ".bin"}
ALLOWED_EXTENSIONS = {".lua", ".luau", ".txt", *BYTECODE_EXTENSIONS}
MAX_INPUT_FILE_BYTES = 64 * 1024 * 1024
_DIRECT_URL = re.compile(r"(?i)^\s*<?https?://\S+>?\s*$")


class InputPanel(ctk.CTkFrame):
    def __init__(self, master, *, title_font, body_font, code_font=None):
        super().__init__(
            master,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
            fg_color=PANEL,
        )
        self._active_tab = "paste"
        self._file_path: Path | None = None
        self._file_content: str | bytes = ""
        self._drop_enabled = False
        self._body_font = body_font
        self._code_font = code_font or body_font

        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)

        header = ctk.CTkFrame(self, fg_color=PANEL, corner_radius=0, height=32)
        header.grid(row=0, column=0, sticky="ew", padx=10, pady=(4, 3))
        header.grid_propagate(False)
        header.grid_columnconfigure(0, weight=1)
        ctk.CTkLabel(
            header,
            text="SOURCE",
            text_color=NEON,
            font=ctk.CTkFont(family=body_font.cget("family"), size=10, weight="bold"),
            anchor="w",
        ).grid(row=0, column=0, sticky="w")

        tabs = ctk.CTkFrame(header, fg_color=PANEL, corner_radius=0)
        tabs.grid(row=0, column=1, sticky="e")
        tab_font = ctk.CTkFont(family=body_font.cget("family"), size=9, weight="bold")
        self.paste_tab = TerminalButton(
            tabs,
            text="PASTE",
            command=lambda: self._select_tab("paste"),
            accent=NEON,
            base_bg=BG,
            width=64,
            height=25,
            font=tab_font,
        )
        self.paste_tab.grid(row=0, column=0, padx=(0, 5))
        self.file_tab = TerminalButton(
            tabs,
            text="FILE",
            command=lambda: self._select_tab("file"),
            accent=NEON,
            base_bg=BG,
            width=52,
            height=25,
            font=tab_font,
        )
        self.file_tab.grid(row=0, column=1)
        self.paste_tab.set_active(True)

        self.content = ctk.CTkFrame(self, fg_color="transparent", corner_radius=0)
        self.content.grid(row=1, column=0, sticky="nsew", padx=7, pady=(0, 3))
        self.content.grid_columnconfigure(0, weight=1)
        self.content.grid_rowconfigure(0, weight=1)

        self.paste_view = ctk.CTkFrame(
            self.content,
            fg_color=INPUT_BG,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
        )
        self.paste_view.grid(row=0, column=0, sticky="nsew")
        self.paste_view.grid_columnconfigure(0, weight=1)
        self.paste_view.grid_rowconfigure(0, weight=1)
        self.textbox = ctk.CTkTextbox(
            self.paste_view,
            width=340,
            height=100,
            corner_radius=0,
            border_width=0,
            fg_color=INPUT_BG,
            text_color=TEXT,
            font=self._code_font,
            wrap="none",
            activate_scrollbars=True,
            undo=True,
        )
        self.textbox.grid(row=0, column=0, sticky="nsew", padx=6, pady=6)
        self.textbox.bind("<KeyRelease>", self._update_status)
        self.textbox.bind("<<Paste>>", self._update_status_after_idle)
        self.textbox.bind("<<Cut>>", self._update_status_after_idle)

        self.file_view = ctk.CTkFrame(
            self.content,
            fg_color=INPUT_BG,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
        )
        self.file_view.grid(row=0, column=0, sticky="nsew")
        self.file_view.grid_columnconfigure(0, weight=1)
        self.file_view.grid_rowconfigure(0, weight=1)
        self.drop_zone = ctk.CTkFrame(
            self.file_view,
            fg_color=INPUT_BG,
            corner_radius=0,
            border_width=1,
            border_color="#414651",
        )
        self.drop_zone.grid(row=0, column=0, sticky="nsew", padx=14, pady=12)
        self.drop_zone.grid_columnconfigure(0, weight=1)
        self.drop_zone.grid_rowconfigure(0, weight=1)
        self.drop_label = ctk.CTkLabel(
            self.drop_zone,
            text="DROP A SCRIPT HERE\nOR BROWSE FOR A FILE",
            text_color=MUTED,
            font=ctk.CTkFont(family=body_font.cget("family"), size=13),
            justify="center",
        )
        self.drop_label.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10, 4))
        self.browse_button = ctk.CTkButton(
            self.drop_zone,
            text="BROWSE",
            command=self._browse_file,
            width=100,
            height=29,
            corner_radius=0,
            border_width=1,
            border_color=BORDER,
            fg_color="#17191e",
            hover_color="#252932",
            text_color=TEXT,
            font=tab_font,
        )
        self.browse_button.grid(row=1, column=0, pady=(3, 12))
        self.file_view.grid_remove()

        self.status = ctk.CTkLabel(
            self,
            text="READY · PASTE SOURCE OR URL",
            text_color=MUTED,
            font=ctk.CTkFont(family=body_font.cget("family"), size=10, weight="bold"),
            anchor="w",
        )
        self.status.grid(row=2, column=0, sticky="ew", padx=10, pady=(0, 4))

    @property
    def file_path(self) -> Path | None:
        return self._file_path if self._active_tab == "file" else None

    def enable_drag_and_drop(self, file_type: str) -> bool:
        target = getattr(self.drop_label, "_label", None)
        if target is None or not hasattr(target, "drop_target_register"):
            return False
        try:
            target.drop_target_register(file_type)
            target.dnd_bind("<<Drop>>", self._handle_drop)
            self._drop_enabled = True
            self.drop_label.configure(text="DROP A SCRIPT HERE\nOR BROWSE FOR A FILE")
            return True
        except Exception as exc:
            LOGGER.warning("Could not enable file drag-and-drop: %s", exc)
            return False

    def get_script(self) -> str | bytes:
        if self._active_tab == "file":
            return self._file_content
        try:
            return self.textbox.get("1.0", "end-1c")
        except Exception:
            LOGGER.exception("Could not read input text")
            return ""

    def _select_tab(self, tab: str) -> None:
        if tab not in {"paste", "file"}:
            return
        self._active_tab = tab
        if tab == "paste":
            self.file_view.grid_remove()
            self.paste_view.grid()
            self.paste_tab.set_active(True)
            self.file_tab.set_active(False)
        else:
            self.paste_view.grid_remove()
            self.file_view.grid()
            self.paste_tab.set_active(False)
            self.file_tab.set_active(True)
        self._update_status()

    def _browse_file(self) -> None:
        try:
            selected = filedialog.askopenfilename(
                parent=self.winfo_toplevel(),
                title="Select a source file",
                filetypes=(
                    ("Lua / Luau source", "*.lua *.luau"),
                    ("Compiled Luau bytecode", "*.luac *.lbc *.bin"),
                    ("Text files", "*.txt"),
                    ("All files", "*.*"),
                ),
            )
            if selected:
                self._load_file(Path(selected))
        except Exception:
            LOGGER.exception("File picker failed")

    def _handle_drop(self, event):
        try:
            paths = self.winfo_toplevel().tk.splitlist(event.data)
            if not paths:
                return "break"
            if len(paths) > 1:
                LOGGER.warning("Only the first dropped file will be loaded")
            self._load_file(Path(paths[0]))
        except Exception:
            LOGGER.exception("Could not handle dropped file")
        return "break"

    def _load_file(self, path: Path) -> None:
        extension = path.suffix.lower()
        if extension not in ALLOWED_EXTENSIONS:
            LOGGER.warning("Unsupported file type: %s", path.name)
            return
        try:
            size = path.stat().st_size
            if size > MAX_INPUT_FILE_BYTES:
                LOGGER.warning(
                    "Input file exceeds the %s MiB file limit: %s",
                    MAX_INPUT_FILE_BYTES // (1024 * 1024),
                    path.name,
                )
                return
            if extension in BYTECODE_EXTENSIONS:
                content: str | bytes = path.read_bytes()
            else:
                content = path.read_text(encoding="utf-8", errors="replace")
        except OSError:
            LOGGER.exception("Could not read input file: %s", path)
            return

        self._file_path = path
        self._file_content = content
        unit = "BYTES" if isinstance(content, bytes) else "CHARACTERS"
        self.drop_label.configure(text=f"{path.name}\n{len(content):,} {unit}")
        self._select_tab("file")
        LOGGER.info("Loaded input file: %s (%s %s)", path.name, f"{len(content):,}", unit.lower())

    def _update_status_after_idle(self, _event=None) -> None:
        self.after_idle(self._update_status)

    def _update_status(self, _event=None) -> None:
        source = self.get_script()
        if isinstance(source, bytes):
            kind = "LUAU BYTECODE" if source.strip() else "READY"
            self.status.configure(text=f"{kind} · {len(source):,} BYTES")
            return
        if not source.strip():
            kind = "READY"
        elif _DIRECT_URL.match(source):
            kind = "CODE LINK"
        elif "loadstring" in source.lower() or "httpget" in source.lower():
            kind = "LOADER"
        else:
            kind = "SOURCE"
        self.status.configure(text=f"{kind} · {len(source):,} CHARACTERS")
