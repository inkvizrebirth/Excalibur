from __future__ import annotations

import base64
import binascii
import json
import logging
import math
import re
import secrets
import threading
from dataclasses import dataclass
from pathlib import Path
from typing import Callable

from core.runtime_paths import LOGS_DIR, TOOLS_DIR
from core.sandbox import Sandbox, SandboxResult

DEFAULT_LOGS_DIR = LOGS_DIR
DEFAULT_TOOLS_DIR = TOOLS_DIR
DEFAULT_TRACE_PATH = DEFAULT_LOGS_DIR / "trace.jsonl"
TRACE_ROTATION_BYTES = 100 * 1024 * 1024
TRACE_PROCESS_OUTPUT_BYTES = 256 * 1024 * 1024
TRACE_TIMEOUT_SECONDS = 120.0
_EVENT_NAME = re.compile(r"^[A-Z0-9_]{1,48}$")


class TraceError(RuntimeError):
    pass


@dataclass(frozen=True)
class TraceResult:
    event_count: int
    trace_files: tuple[Path, ...]
    native_hooks_available: bool
    timed_out: bool
    output_limited: bool
    sandbox_result: SandboxResult


class _RotatingJsonlWriter:
    def __init__(self, path: Path, max_bytes: int):
        if max_bytes <= 0:
            raise ValueError("max_bytes must be positive")
        self.path = path
        self.max_bytes = max_bytes
        self._segment = 0
        self._written = 0
        self._file = None
        self.paths: list[Path] = []
        self._remove_previous_segments()
        self._open_segment()

    def _remove_previous_segments(self) -> None:
        self.path.unlink(missing_ok=True)
        for old_path in self.path.parent.glob(f"{self.path.stem}.*{self.path.suffix}"):
            old_path.unlink(missing_ok=True)

    def _segment_path(self) -> Path:
        if self._segment == 0:
            return self.path
        return self.path.with_name(
            f"{self.path.stem}.{self._segment:03d}{self.path.suffix}"
        )

    def _open_segment(self) -> None:
        current = self._segment_path()
        self._file = current.open("wb")
        self._written = 0
        self.paths.append(current)

    def write(self, record: dict) -> None:
        if self._file is None:
            raise TraceError("Trace writer is closed")
        encoded = (json.dumps(record, ensure_ascii=False, separators=(",", ":")) + "\n").encode(
            "utf-8"
        )
        if self._written and self._written + len(encoded) > self.max_bytes:
            self._file.close()
            self._segment += 1
            self._open_segment()
        self._file.write(encoded)
        self._written += len(encoded)

    def close(self) -> None:
        if self._file is not None:
            self._file.flush()
            self._file.close()
            self._file = None


class Tracer:
    """Collect structured hook/API events without retaining a trace in RAM.

    Stock Luau does not implement debug.sethook, so a normal Luau CLI run can
    only provide mock/API events. The optional pinned native host additionally
    emits instruction-step events from Luau's C API debugstep callback.
    """

    def __init__(
        self,
        *,
        logger: logging.Logger | None = None,
        progress_callback: Callable[[float, str], None] | None = None,
        logs_dir: Path | str = DEFAULT_LOGS_DIR,
        tools_dir: Path | str = DEFAULT_TOOLS_DIR,
        trace_path: Path | str | None = None,
        max_trace_bytes: int = TRACE_ROTATION_BYTES,
        timeout_seconds: float = TRACE_TIMEOUT_SECONDS,
        max_process_output_bytes: int = TRACE_PROCESS_OUTPUT_BYTES,
        sandbox: Sandbox | None = None,
    ):
        if timeout_seconds <= 0:
            raise ValueError("timeout_seconds must be positive")
        self.logger = logger or logging.getLogger("protez")
        self.progress_callback = progress_callback
        self.logs_dir = Path(logs_dir).expanduser().resolve()
        self.tools_dir = Path(tools_dir).expanduser().resolve()
        self.trace_path = (
            Path(trace_path).expanduser().resolve()
            if trace_path is not None
            else self.logs_dir / DEFAULT_TRACE_PATH.name
        )
        self.max_trace_bytes = max_trace_bytes
        self.timeout_seconds = timeout_seconds
        self.max_process_output_bytes = max_process_output_bytes
        self.sandbox = sandbox or Sandbox(
            tools_dir=self.tools_dir,
            logs_dir=self.logs_dir,
            timeout_seconds=timeout_seconds,
            max_output_bytes=max_process_output_bytes,
            logger=self.logger,
        )
        self._run_lock = threading.Lock()

    def trace(self, source: str, *, source_name: str = "input") -> TraceResult:
        with self._run_lock:
            return self._trace_once(source, source_name)

    def _trace_once(self, source: str, source_name: str) -> TraceResult:
        self.logs_dir.mkdir(parents=True, exist_ok=True)
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        self.logger.info("Tracing started: mock/API events plus native VM steps when available")
        self.logger.warning(
            "Instruction stepping requires the optional native host; stock Luau CLI records mock/API events only"
        )
        self._progress(20, "TRACE")

        token = secrets.token_hex(16)
        prefix = f"__PROTEZ_TRACE_{token}|".encode("ascii")
        writer = _RotatingJsonlWriter(self.trace_path, self.max_trace_bytes)
        state = {"event_count": 0, "hooks_available": False, "error": None}

        def consume_line(line: bytes) -> None:
            if not line.startswith(prefix):
                return
            record = self._decode_record(line.rstrip(b"\r\n"), prefix)
            if record is None:
                return
            record["seq"] = state["event_count"] + 1
            try:
                writer.write(record)
            except Exception as exc:
                state["error"] = exc
                return

            state["event_count"] += 1
            if record["op"] == "HOOK_READY" and record["backend"] == "luau-native-debugstep":
                state["hooks_available"] = True

            count = state["event_count"]
            if count % 100_000 == 0:
                self.logger.info("Trace recorded: %s events", f"{count:,}".replace(",", " "))
                self._progress(min(59, 20 + count // 100_000), "TRACE")

        try:
            sandbox_result = self.sandbox.run(
                source,
                source_name=source_name,
                trace=True,
                trace_token=token,
                output_line_callback=consume_line,
            )
        finally:
            writer.close()

        if state["error"] is not None:
            raise TraceError(f"Could not write trace event: {state['error']}") from state["error"]
        if sandbox_result.trace_token != token:
            raise TraceError("Sandbox returned a mismatched trace token")
        if sandbox_result.timed_out:
            self.logger.warning("Trace run reached the %s second timeout", self.timeout_seconds)
        if sandbox_result.output_limited:
            self.logger.warning("Trace run reached its process-output limit")
        if state["hooks_available"]:
            self.logger.info(
                "Native trace records include proto-relative PCs and opcode headers; the full register file is not captured"
            )
        else:
            self.logger.warning(
                "Trace contains mock/API events only; build the optional native host for instruction-step events"
            )
        event_count = state["event_count"]
        self.logger.info("Trace recorded: %s events", f"{event_count:,}".replace(",", " "))
        self.logger.info("Trace written to %s", self.trace_path)
        self._progress(60, "TRACE")

        return TraceResult(
            event_count=event_count,
            trace_files=tuple(writer.paths),
            native_hooks_available=state["hooks_available"],
            timed_out=sandbox_result.timed_out,
            output_limited=sandbox_result.output_limited,
            sandbox_result=sandbox_result,
        )

    @staticmethod
    def _decode_record(line: bytes, prefix: bytes) -> dict | None:
        fields = line[len(prefix) :].split(b"|", maxsplit=6)
        if len(fields) != 7:
            return None
        try:
            sequence = int(fields[0])
            op = fields[1].decode("ascii")
            elapsed = float(fields[2])
            source_line = int(fields[3])
            if sequence < 1 or not _EVENT_NAME.fullmatch(op) or not math.isfinite(elapsed):
                return None
            name = base64.b64decode(fields[4], validate=True).decode("utf-8", errors="replace")
            source = base64.b64decode(fields[5], validate=True).decode("utf-8", errors="replace")
            detail = base64.b64decode(fields[6], validate=True).decode("utf-8", errors="replace")
        except (ValueError, UnicodeDecodeError, binascii.Error):
            return None

        record = {
            "t": max(0.0, elapsed),
            "pc": None,
            "op": op,
            "seq": sequence,
            "line": source_line or None,
            "name": name or None,
            "source": source or None,
            "detail": detail or None,
            "backend": (
                "luau-native-debugstep"
                if op in {"VM_STEP", "VM_STEP_LIMIT"}
                else "luau-hook"
                if op in {"CALL", "RETURN", "LINE", "COUNT", "TAIL_RETURN", "HOOK_READY", "HOOK_UNAVAILABLE"}
                else "mock-api"
            ),
        }
        if op in {"VM_STEP", "VM_STEP_LIMIT", "HOOK_READY"}:
            try:
                metadata = json.loads(detail)
            except (TypeError, json.JSONDecodeError):
                metadata = None
            if isinstance(metadata, dict) and (
                op in {"VM_STEP", "VM_STEP_LIMIT"}
                or metadata.get("mode") == "instruction-step"
            ):
                record.update(metadata)
                record["detail"] = None
                if op == "HOOK_READY":
                    record["backend"] = "luau-native-debugstep"
        return record

    def _progress(self, percent: float, stage: str) -> None:
        if self.progress_callback is not None:
            self.progress_callback(percent, stage)


__all__ = ["TraceError", "TraceResult", "Tracer"]
