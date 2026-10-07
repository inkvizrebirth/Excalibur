"""Bounded adapter for the official pinned Luau AST command line tool."""
from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import time
from pathlib import Path

MAX_AST_OUTPUT_BYTES = 128 * 1024 * 1024
AST_TIMEOUT_SECONDS = 15.0


class AstToolError(RuntimeError):
    pass


def _binary() -> Path:
    configured = os.environ.get("PROTEZ_LUAU_AST")
    if configured:
        candidate = Path(configured).expanduser()
        if candidate.is_file():
            return candidate.resolve()
        raise AstToolError(f"configured Luau AST tool does not exist: {candidate}")
    suffix = ".exe" if os.name == "nt" else ""
    for candidate in (Path(__file__).resolve().parents[3] / "tools" / f"luau-ast{suffix}",):
        if candidate.is_file():
            return candidate.resolve()
    raise AstToolError("the pinned Luau AST tool is unavailable; repair Protez's native runtime")


def binary() -> Path:
    """The pinned Luau AST tool, for the vendored passes that spawn it themselves."""
    return _binary()


def parse_file(path: str | os.PathLike[str]) -> bytes:
    """Return AST JSON while bounding parser time and output size."""
    source = Path(path)
    try:
        source_size = source.stat().st_size
    except OSError as exc:
        raise AstToolError(f"cannot read source for AST parsing: {exc}") from exc
    if source_size > 16 * 1024 * 1024:
        raise AstToolError("AST input exceeds Protez's 16 MiB source limit")

    command = [str(_binary()), str(source)]
    deadline = os.environ.get("PROTEZ_ANALYSIS_DEADLINE")
    allowed_seconds = AST_TIMEOUT_SECONDS
    if deadline:
        try:
            allowed_seconds = min(allowed_seconds, float(deadline) - time.monotonic())
        except ValueError:
            raise AstToolError("invalid Protez analysis deadline")
    if allowed_seconds <= 0:
        raise AstToolError("Luraph VM lifting reached Protez's total analysis time limit")
    env = {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
    creationflags = 0
    popen_options: dict[str, object] = {}
    if os.name == "nt":
        env = {}
        for name in ("SystemRoot", "WINDIR", "TEMP", "TMP", "PATHEXT"):
            value = os.environ.get(name)
            if value:
                env[name] = value
        root = env.get("SystemRoot") or env.get("WINDIR")
        if root:
            env["PATH"] = str(Path(root) / "System32")
        creationflags = getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    else:
        popen_options["start_new_session"] = True

    with tempfile.TemporaryFile(mode="w+b") as stdout, tempfile.TemporaryFile(mode="w+b") as stderr:
        try:
            process = subprocess.Popen(
                command,
                cwd=source.parent,
                env=env,
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                close_fds=True,
                creationflags=creationflags,
                **popen_options,
            )
        except OSError as exc:
            raise AstToolError(f"could not start pinned Luau AST tool: {exc}") from exc

        timeout_at = time.monotonic() + allowed_seconds
        failure = None
        while process.poll() is None:
            if time.monotonic() >= timeout_at:
                failure = "Luau AST parsing exceeded its time budget"
                break
            if os.fstat(stdout.fileno()).st_size > MAX_AST_OUTPUT_BYTES or os.fstat(stderr.fileno()).st_size > 1024 * 1024:
                failure = "Luau AST parser output exceeded its safety limit"
                break
            time.sleep(0.02)
        if failure:
            try:
                if os.name == "nt":
                    process.kill()
                else:
                    os.killpg(process.pid, signal.SIGKILL)
            except (OSError, ProcessLookupError):
                process.kill()
            process.wait()
            raise AstToolError(failure)

        returncode = process.wait()
        stdout.seek(0, os.SEEK_END)
        output_size = stdout.tell()
        stderr.seek(0, os.SEEK_END)
        error_size = stderr.tell()
        if output_size > MAX_AST_OUTPUT_BYTES or error_size > 1024 * 1024:
            raise AstToolError("Luau AST parser output exceeded its safety limit")
        stdout.seek(0)
        output = stdout.read(MAX_AST_OUTPUT_BYTES + 1)
        stderr.seek(0)
        detail = stderr.read(8192).decode("utf-8", "replace").strip()
        if returncode != 0:
            raise AstToolError(detail or f"Luau AST tool exited with code {returncode}")
        if not output:
            raise AstToolError("Luau AST tool returned no JSON")
        return output
