from __future__ import annotations

import hashlib
import logging
import os
import shutil
import signal
import subprocess
import tempfile
from pathlib import Path

from core.runtime_paths import IS_FROZEN, PACKAGED_TOOLS_DIR

MAX_BYTECODE_BYTES = 64 * 1024 * 1024
MAX_DECOMPILED_BYTES = 64 * 1024 * 1024
DEFAULT_TIMEOUT_SECONDS = 30.0
BUNDLED_DECOMPILER_REPOSITORY = "https://github.com/PumbaaDev/luau-decompiler"
BUNDLED_DECOMPILER_COMMIT = "ee07098c31e11601a9ca434bc12932a4ded65f7b"


class BytecodeDecompilerError(RuntimeError):
    pass


class LocalBytecodeDecompiler:
    """Run the optional offline Luau bytecode decompiler as a real local CLI."""

    def __init__(
        self,
        *,
        tools_dir: Path,
        timeout_seconds: float = DEFAULT_TIMEOUT_SECONDS,
        logger: logging.Logger | None = None,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.tools_dir = Path(tools_dir).expanduser().resolve()
        self.timeout_seconds = timeout_seconds
        self.logger = logger or logging.getLogger("protez")

    def resolve_binary(self) -> Path | None:
        names = ("luau-decompiler.exe", "luau-decompiler") if os.name == "nt" else (
            "luau-decompiler",
            "luau-decompiler.exe",
        )
        candidates: list[Path] = []
        override = os.environ.get("PROTEZ_LUAU_DECOMPILER")
        if override:
            candidates.append(Path(override).expanduser())
        candidates.extend(self.tools_dir / name for name in names)
        for command_name in ("luau-decompiler", "luau-decompiler.exe"):
            discovered = shutil.which(command_name)
            if discovered:
                candidates.append(Path(discovered))

        for candidate in candidates:
            try:
                if candidate.is_file() and (os.name == "nt" or os.access(candidate, os.X_OK)):
                    return candidate.resolve()
            except OSError:
                continue
        return None

    def is_bundled_binary(self, binary: Path) -> bool:
        """Return true only when the frozen executable's tool matches its packaged copy."""
        if not IS_FROZEN:
            return False
        packaged = PACKAGED_TOOLS_DIR / binary.name
        try:
            return (
                packaged.is_file()
                and binary.is_file()
                and self._sha256_file(packaged) == self._sha256_file(binary)
            )
        except OSError:
            return False

    @staticmethod
    def _sha256_file(path: Path) -> str:
        digest = hashlib.sha256()
        with path.open("rb") as file:
            for chunk in iter(lambda: file.read(1024 * 1024), b""):
                digest.update(chunk)
        return digest.hexdigest()

    def decompile(self, bytecode: bytes, *, source_name: str = "input.luac") -> tuple[str, Path]:
        if not isinstance(bytecode, bytes):
            raise TypeError("bytecode must be bytes")
        if not bytecode:
            raise BytecodeDecompilerError("The selected bytecode file is empty")
        if len(bytecode) > MAX_BYTECODE_BYTES:
            raise BytecodeDecompilerError(
                f"Bytecode exceeds the {MAX_BYTECODE_BYTES // (1024 * 1024)} MiB input limit"
            )

        binary = self.resolve_binary()
        if binary is None:
            raise BytecodeDecompilerError(
                "No local Luau bytecode decompiler was found. Install the offline "
                "`luau-decompiler` CLI or place it in Protez's tools folder."
            )

        try:
            with tempfile.TemporaryDirectory(prefix="protez-bytecode-") as temporary:
                workspace = Path(temporary).resolve()
                input_path = workspace / self._safe_filename(source_name)
                output_path = workspace / "recovered.luau"
                input_path.write_bytes(bytecode)
                command = [
                    str(binary),
                    str(input_path),
                    "--output",
                    str(output_path),
                ]
                self.logger.info(
                    "Running local Luau bytecode decompiler: %s (static; bytecode is not executed)",
                    binary.name,
                )
                diagnostic = self._run(command, cwd=workspace)
                if not output_path.is_file():
                    raise BytecodeDecompilerError(
                        "The local bytecode decompiler returned success without writing source"
                    )
                output_size = output_path.stat().st_size
                if output_size == 0:
                    raise BytecodeDecompilerError("The local bytecode decompiler produced an empty file")
                if output_size > MAX_DECOMPILED_BYTES:
                    raise BytecodeDecompilerError(
                        f"Decompiled output exceeds the {MAX_DECOMPILED_BYTES // (1024 * 1024)} MiB limit"
                    )
                try:
                    source = output_path.read_text(encoding="utf-8", errors="strict")
                except UnicodeDecodeError as exc:
                    raise BytecodeDecompilerError(
                        "The local bytecode decompiler returned non-UTF-8 source"
                    ) from exc
                if not source.strip():
                    detail = f" Diagnostic: {diagnostic}" if diagnostic else ""
                    raise BytecodeDecompilerError(f"The local bytecode decompiler produced no source.{detail}")
                return source, binary
        except BytecodeDecompilerError:
            raise
        except OSError as exc:
            raise BytecodeDecompilerError(f"Could not prepare bytecode decompilation: {exc}") from exc

    def _run(self, command: list[str], *, cwd: Path) -> str:
        creationflags = 0
        options: dict[str, object] = {}
        if os.name == "nt":
            creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
            creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
        else:
            options["start_new_session"] = True

        try:
            with tempfile.TemporaryFile(mode="w+b") as diagnostics:
                process = subprocess.Popen(
                    command,
                    cwd=cwd,
                    env=self._minimal_environment(cwd),
                    stdin=subprocess.DEVNULL,
                    stdout=diagnostics,
                    stderr=subprocess.STDOUT,
                    close_fds=True,
                    creationflags=creationflags,
                    **options,
                )
                try:
                    returncode = process.wait(timeout=self.timeout_seconds)
                except subprocess.TimeoutExpired as exc:
                    self._kill(process)
                    process.wait()
                    raise BytecodeDecompilerError(
                        f"Local bytecode decompilation exceeded {self.timeout_seconds:.0f} seconds"
                    ) from exc
                diagnostics.seek(0, os.SEEK_END)
                size = diagnostics.tell()
                diagnostics.seek(max(0, size - 8192))
                detail = diagnostics.read().decode("utf-8", errors="replace").strip()
        except OSError as exc:
            raise BytecodeDecompilerError(f"Could not start the local Luau decompiler: {exc}") from exc
        if returncode != 0:
            message = detail or f"the CLI exited with code {returncode}"
            raise BytecodeDecompilerError(f"Luau bytecode decompilation failed: {message}")
        return detail

    @staticmethod
    def _safe_filename(source_name: str) -> str:
        name = Path(source_name).name
        if not name or name in {".", ".."}:
            return "input.luac"
        return name if Path(name).suffix else name + ".luac"

    @staticmethod
    def _minimal_environment(workspace: Path) -> dict[str, str]:
        environment: dict[str, str] = {}
        if os.name == "nt":
            for name in ("SystemRoot", "WINDIR", "PATHEXT"):
                value = os.environ.get(name)
                if value:
                    environment[name] = value
            system_root = environment.get("SystemRoot") or environment.get("WINDIR")
            if system_root:
                environment["PATH"] = str(Path(system_root) / "System32")
            environment["TEMP"] = str(workspace)
            environment["TMP"] = str(workspace)
            environment["USERPROFILE"] = str(workspace)
            environment["HOME"] = str(workspace)
            environment["APPDATA"] = str(workspace)
            environment["LOCALAPPDATA"] = str(workspace)
        else:
            environment.update({"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"})
            environment["HOME"] = str(workspace)
            environment["TMPDIR"] = str(workspace)
        return environment

    @staticmethod
    def _kill(process: subprocess.Popen) -> None:
        if process.poll() is not None:
            return
        try:
            if os.name == "nt":
                process.kill()
            else:
                os.killpg(process.pid, signal.SIGKILL)
        except (OSError, ProcessLookupError):
            try:
                process.kill()
            except OSError:
                pass


__all__ = ["BytecodeDecompilerError", "LocalBytecodeDecompiler"]
