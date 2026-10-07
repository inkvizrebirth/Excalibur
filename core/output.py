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
    "collapse_to_one_line",
    "single_line_chunk_document",
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


def collapse_to_one_line(source: str) -> str:
    """The same program with its comments removed and every line joined.

    Joining lines is only safe through the token stream: a newline ends a
    ``--`` comment, and the contents of a long string are line-sensitive, so
    the raw text is rebuilt token by token (comments dropped, one space
    between tokens) instead of with a regular expression.  A program that
    contains a multi-line string cannot be collapsed and keeps its newlines,
    which the caller checks for.
    """
    from core.formatter import tokenize

    pieces = [source[token.start:token.end] for token in tokenize(source) if token.kind != "comment"]
    return " ".join(pieces).strip()


def _long_bracket_level(text: str) -> str:
    """A long-bracket level that ``text`` cannot close by accident."""
    level = 1
    while True:
        fence = "=" * level
        if "]" + fence + "]" not in text and "[" + fence + "[" not in text:
            return fence
        level += 1


def single_line_chunk_document(body: str, *, one_line: str) -> str:
    """Delivery form for a loader that refuses to be reformatted.

    WeAreDevs and the Prometheus family compare ``linedefined`` with
    ``lastlinedefined`` on their own chunk: as soon as the file they run from
    spans more than one line they raise their "Tamper Detected" guard, which
    every readable result would trip.  The program therefore travels twice in
    one file - the readable copy as a block comment, and a one-line copy handed
    to ``loadstring``, so the chunk that actually runs is a single line long.
    """
    fence = _long_bracket_level(body)
    line_fence = _long_bracket_level(one_line)
    rule = "-- " + "=" * 76
    literal = "[" + line_fence + "[" + one_line + "]" + line_fence + "]"
    return "\n".join((
        rule,
        "-- Readable recovered source (the runnable copy is at the end of the file).",
        "-- This loader verifies that the chunk it runs from is one line long and raises",
        "-- its tamper guard otherwise, so the copy below is kept as a comment and the",
        "-- loader is fed a one-line copy of the same program instead.",
        rule,
        "--[" + fence + "[",
        body.rstrip(),
        "]" + fence + "]",
        "",
        rule,
        "-- Runnable copy: the same program as a single line.",
        rule,
        "return (loadstring or load)(" + literal + ', "=protez-recovered")(...)',
        "",
    ))


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
