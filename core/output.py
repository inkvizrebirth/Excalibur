"""Single-artifact output policy.

``output/`` keeps exactly one readable result per run - ``destroyed_N.lua`` -
and nothing else.  Reports, traces and captured payloads live under ``logs/``
so the folder a user opens after a run always contains clean, readable Lua.
"""

from __future__ import annotations

import json
import os
import re
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Iterable

OUTPUT_STEM = "destroyed"
OUTPUT_SUFFIX = ".lua"
_INDEX_PATTERN = re.compile(rf"^{OUTPUT_STEM}_(\d+){re.escape(OUTPUT_SUFFIX)}$", re.IGNORECASE)
_LEGACY_PATTERNS = (
    "deobfuscated_*.luau",
    "deobfuscated_*.report.json",
    "analysis_*.report.json",
    "*.candidate.luau",
    "captured_payload_*.luau",
    "*.lua.tmp",
    "*.report.json.tmp",
)

__all__ = [
    "OutputPaths",
    "existing_outputs",
    "next_output_path",
    "next_output_index",
    "prune_legacy_artifacts",
    "write_text_atomic",
    "write_report",
    "clean_result_header",
]


@dataclass(frozen=True)
class OutputPaths:
    script: Path
    report: Path


def existing_outputs(output_dir: Path | str) -> tuple[Path, ...]:
    directory = Path(output_dir)
    if not directory.is_dir():
        return ()
    results: list[tuple[int, Path]] = []
    for entry in directory.iterdir():
        match = _INDEX_PATTERN.match(entry.name)
        if match is None or not entry.is_file():
            continue
        results.append((int(match.group(1)), entry))
    return tuple(path for _index, path in sorted(results))


def next_output_index(output_dir: Path | str) -> int:
    highest = 0
    for entry in Path(output_dir).glob(f"{OUTPUT_STEM}_*{OUTPUT_SUFFIX}") if Path(output_dir).is_dir() else ():
        match = _INDEX_PATTERN.match(entry.name)
        if match is not None:
            highest = max(highest, int(match.group(1)))
    return highest + 1


def next_output_path(output_dir: Path | str) -> Path:
    directory = Path(output_dir)
    directory.mkdir(parents=True, exist_ok=True)
    return directory / f"{OUTPUT_STEM}_{next_output_index(directory)}{OUTPUT_SUFFIX}"


def report_path(logs_dir: Path | str, *, source_name: str = "input") -> Path:
    directory = Path(logs_dir)
    directory.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe = re.sub(r"[^A-Za-z0-9_.-]+", "_", Path(source_name).name)[:48] or "input"
    return directory / f"report_{stamp}_{safe}.json"


def prune_legacy_artifacts(output_dir: Path | str) -> tuple[Path, ...]:
    """Delete earlier multi-file artifacts, keeping every ``destroyed_N.lua``."""
    directory = Path(output_dir)
    if not directory.is_dir():
        return ()
    removed: list[Path] = []
    for pattern in _LEGACY_PATTERNS:
        for entry in directory.glob(pattern):
            try:
                if entry.is_file():
                    entry.unlink()
                    removed.append(entry)
            except OSError:
                continue
    return tuple(removed)


def write_text_atomic(path: Path | str, text: str) -> Path:
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_name(target.name + ".tmp")
    try:
        with temporary.open("w", encoding="utf-8", newline="\n") as handle:
            handle.write(text)
        os.replace(temporary, target)
    except OSError:
        temporary.unlink(missing_ok=True)
        raise
    return target


def write_report(path: Path | str, report: dict) -> Path:
    return write_text_atomic(path, json.dumps(report, indent=2, ensure_ascii=False) + "\n")


def clean_result_header(
    *,
    source_name: str,
    family_label: str,
    method: str,
    partial: bool,
    notes: Iterable[str] = (),
    profile_label: str | None = None,
    layers: int = 0,
) -> str:
    """Readable banner prepended to every recovered script."""
    status = "PARTIAL RECOVERY" if partial else "RECOVERED"
    lines = [
        "--" + "=" * 72,
        f"-- Protez - {status}",
        f"-- input      : {source_name}",
        f"-- family     : {family_label}",
        f"-- method     : {method}",
    ]
    if profile_label:
        lines.append(f"-- injector   : {profile_label}")
    if layers:
        lines.append(f"-- layers     : {layers}")
    for note in notes:
        lines.append(f"-- note       : {note}")
    if partial:
        lines.append("--")
        lines.append("-- This output is an approximation: the outer layers were removed and")
        lines.append("-- the code below is the most readable form Protez could reach. Names,")
        lines.append("-- comments and some idioms cannot be restored from protected input.")
    lines.append("--" + "=" * 72)
    return "\n".join(lines) + "\n\n"
