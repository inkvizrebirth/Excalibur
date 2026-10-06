from __future__ import annotations

import os
import signal
import subprocess
import tempfile
import time
from dataclasses import dataclass
from pathlib import Path

MAX_MOONSEC_SOURCE_BYTES = 16 * 1024 * 1024
MAX_MOONSEC_BYTECODE_BYTES = 64 * 1024 * 1024
MAX_MOONSEC_PROCESS_OUTPUT_BYTES = 2 * 1024 * 1024
LUA51_HEADER = b"\x1bLua\x51\x00\x01\x04\x08\x04\x08\x00"


class MoonSecDevirtualizationError(RuntimeError):
    pass


@dataclass(frozen=True)
class MoonSecV3Result:
    source: str | None
    bytecode: bytes | None
    disassembly: str | None
    error: str | None
    elapsed_seconds: float
    devirtualizer_version: str
    decompiler_version: str


def _tool_path(tools_dir: Path, stem: str) -> Path:
    suffix = ".exe" if os.name == "nt" else ""
    path = tools_dir / f"{stem}{suffix}"
    if not path.is_file():
        raise MoonSecDevirtualizationError(f"required offline tool is missing: {path.name}")
    return path.resolve()


def _minimal_environment() -> dict[str, str]:
    if os.name != "nt":
        return {"PATH": "/usr/bin:/bin", "LANG": "C", "LC_ALL": "C"}
    result: dict[str, str] = {}
    for key in ("SystemRoot", "WINDIR", "TEMP", "TMP", "PATHEXT"):
        value = os.environ.get(key)
        if value:
            result[key] = value
    root = result.get("SystemRoot") or result.get("WINDIR")
    if root:
        result["PATH"] = str(Path(root) / "System32")
    return result


def _terminate(process: subprocess.Popen) -> None:
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


def _run_tool(
    command: list[str],
    *,
    cwd: Path,
    timeout_seconds: float,
    output_limit: int = MAX_MOONSEC_PROCESS_OUTPUT_BYTES,
) -> tuple[int, str]:
    creationflags = 0
    popen_options: dict[str, object] = {}
    if os.name == "nt":
        creationflags |= getattr(subprocess, "CREATE_NEW_PROCESS_GROUP", 0)
        creationflags |= getattr(subprocess, "CREATE_NO_WINDOW", 0)
    else:
        popen_options["start_new_session"] = True

    with tempfile.TemporaryFile(mode="w+b") as stdout, tempfile.TemporaryFile(mode="w+b") as stderr:
        try:
            process = subprocess.Popen(
                command,
                cwd=cwd,
                env=_tool_environment(command[0]),
                stdin=subprocess.DEVNULL,
                stdout=stdout,
                stderr=stderr,
                close_fds=True,
                creationflags=creationflags,
                **popen_options,
            )
        except OSError as exc:
            raise MoonSecDevirtualizationError(f"could not start {Path(command[0]).name}: {exc}") from exc

        deadline = time.monotonic() + timeout_seconds
        failure = None
        while process.poll() is None:
            if time.monotonic() >= deadline:
                failure = f"{Path(command[0]).name} exceeded its {timeout_seconds:.1f}s time limit"
                break
            if os.fstat(stdout.fileno()).st_size > output_limit or os.fstat(stderr.fileno()).st_size > output_limit:
                failure = f"{Path(command[0]).name} exceeded its output limit"
                break
            time.sleep(0.02)
        if failure:
            _terminate(process)
            process.wait()
            raise MoonSecDevirtualizationError(failure)

        returncode = process.wait()
        if os.fstat(stdout.fileno()).st_size > output_limit or os.fstat(stderr.fileno()).st_size > output_limit:
            raise MoonSecDevirtualizationError(f"{Path(command[0]).name} exceeded its output limit")
        stdout.seek(0)
        stderr.seek(0)
        details = (stdout.read(output_limit) + b"\n" + stderr.read(output_limit))
        return returncode, details.decode("utf-8", "replace").strip()[-6000:]


def _tool_environment(executable: str) -> dict[str, str]:
    environment = _minimal_environment()
    if Path(executable).name.lower().startswith("protez-moonsec-v3"):
        # Limit the managed heap for hostile or pathological parser inputs.
        environment["DOTNET_GCHeapHardLimit"] = "20000000"  # 512 MiB, hexadecimal bytes
        environment["DOTNET_PROCESSOR_COUNT"] = "2"
    return environment


def _check_lua51_chunk(path: Path) -> bytes:
    try:
        size = path.stat().st_size
        if size < len(LUA51_HEADER) or size > MAX_MOONSEC_BYTECODE_BYTES:
            raise MoonSecDevirtualizationError("MoonSec helper returned a chunk outside the size limit")
        chunk = path.read_bytes()
    except OSError as exc:
        raise MoonSecDevirtualizationError(f"MoonSec helper did not write bytecode: {exc}") from exc
    if not chunk.startswith(LUA51_HEADER):
        raise MoonSecDevirtualizationError("MoonSec helper output is not a standard Lua 5.1 chunk")
    return chunk


def devirtualize_moonsec_v3(
    source: str,
    *,
    tools_dir: Path,
    timeout_seconds: float,
) -> MoonSecV3Result:
    source_bytes = source.encode("utf-8")
    if len(source_bytes) > MAX_MOONSEC_SOURCE_BYTES:
        raise MoonSecDevirtualizationError("MoonSec V3 input exceeds Protez's 16 MiB source limit")
    if timeout_seconds <= 0:
        raise MoonSecDevirtualizationError("MoonSec V3 analysis time budget is exhausted")

    devirtualizer = _tool_path(tools_dir, "protez-moonsec-v3")
    decompiler = _tool_path(tools_dir, "unluac-cli")
    started = time.monotonic()
    with tempfile.TemporaryDirectory(prefix="protez-moonsec-") as temp_dir:
        work = Path(temp_dir)
        input_path = work / "protected.lua"
        bytecode_path = work / "recovered.lua51.luac"
        source_path = work / "recovered.lua"
        disassembly_path = work / "recovered.disassembly.txt"
        input_path.write_bytes(source_bytes)

        remaining = timeout_seconds - (time.monotonic() - started)
        returncode, diagnostic = _run_tool(
            [str(devirtualizer), "-dev", "-i", str(input_path), "-o", str(bytecode_path)],
            cwd=work,
            timeout_seconds=remaining,
        )
        if returncode != 0:
            raise MoonSecDevirtualizationError(
                diagnostic or f"MoonSec V3 handler recovery exited with code {returncode}"
            )
        bytecode = _check_lua51_chunk(bytecode_path)

        remaining = timeout_seconds - (time.monotonic() - started)
        source_error = None
        recovered_source = None
        if remaining > 0:
            try:
                returncode, diagnostic = _run_tool(
                    [
                        str(decompiler),
                        "-i", str(bytecode_path),
                        "-D", "lua5.1",
                        "--naming-mode", "heuristic",
                        "--generate-mode", "strict",
                        "-o", str(source_path),
                    ],
                    cwd=work,
                    timeout_seconds=remaining,
                )
                if returncode == 0 and source_path.is_file():
                    recovered_source = source_path.read_text(encoding="utf-8")
                else:
                    source_error = diagnostic or f"Lua 5.1 source lifting exited with code {returncode}"
            except (MoonSecDevirtualizationError, OSError, UnicodeDecodeError) as exc:
                source_error = str(exc)
        else:
            source_error = "the analysis time budget ended after Lua 5.1 bytecode recovery"

        disassembly = None
        if recovered_source is None and time.monotonic() - started < timeout_seconds:
            remaining = timeout_seconds - (time.monotonic() - started)
            try:
                returncode, diagnostic = _run_tool(
                    [str(devirtualizer), "-dis", "-i", str(input_path), "-o", str(disassembly_path)],
                    cwd=work,
                    timeout_seconds=remaining,
                )
                if returncode == 0 and disassembly_path.is_file():
                    disassembly = disassembly_path.read_text(encoding="utf-8", errors="replace")
                elif diagnostic:
                    source_error = f"{source_error}; disassembly also failed: {diagnostic}"
            except (MoonSecDevirtualizationError, OSError) as exc:
                source_error = f"{source_error}; disassembly also failed: {exc}"

        return MoonSecV3Result(
            source=recovered_source,
            bytecode=bytecode,
            disassembly=disassembly,
            error=source_error,
            elapsed_seconds=time.monotonic() - started,
            devirtualizer_version="MoonsecDeobfuscator 0.1.0 (adapted, GPL-3.0)",
            decompiler_version="unluac-rs 1.4.4 with Protez SETLIST recovery patch (MIT)",
        )
