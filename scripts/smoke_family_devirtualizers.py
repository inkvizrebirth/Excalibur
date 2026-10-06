from __future__ import annotations

import argparse
import json
import logging
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from core.pipeline import DeobfuscationPipeline
from core.sandbox import Sandbox


def _print_top_level_return(source: str, *, label: str) -> str:
    """Turn the pinned sample's final return expression into an observable print."""
    lines = source.splitlines()
    final = next((index for index in range(len(lines) - 1, -1, -1) if lines[index].strip()), None)
    if final is None:
        raise RuntimeError(f"{label} contains no source statements")
    match = re.fullmatch(r"return\s+(.+?)\s*", lines[final])
    if match is None:
        raise RuntimeError(f"{label} does not end in a top-level return expression")
    lines[final] = f"print({match.group(1)})"
    return "\n".join(lines) + "\n"


def _run_semantic_sample(source: str, *, label: str, tools_dir: Path, work_dir: Path) -> str:
    sandbox = Sandbox(
        tools_dir=tools_dir,
        logs_dir=work_dir / "semantic-logs",
        timeout_seconds=10.0,
        max_input_bytes=2 * 1024 * 1024,
        max_output_bytes=1024 * 1024,
    )
    result = sandbox.run(
        _print_top_level_return(source, label=label),
        source_name=label,
        trace=False,
    )
    if result.returncode != 0 or result.timed_out or result.output_limited:
        detail = result.run_log_path.read_text(encoding="utf-8", errors="replace")[-2000:]
        raise RuntimeError(f"{label} failed in the isolated Luau worker: {detail}")
    return result.run_log_path.read_text(encoding="utf-8", errors="replace").strip()


def _run_family(
    *,
    family: str,
    fixture: Path,
    tools_dir: Path,
    work_dir: Path,
    luraph_ground_truth: Path | None = None,
) -> None:
    source = fixture.read_text(encoding="utf-8")
    output_dir = work_dir / family.lower()
    logger = logging.getLogger(f"protez.smoke.{family.lower()}")
    pipeline = DeobfuscationPipeline(
        logger=logger,
        output_dir=output_dir,
        tools_dir=tools_dir,
        compiler_timeout_seconds=30.0,
        sandbox_timeout_seconds=45.0,
        max_pipeline_seconds=150.0,
    )
    result = pipeline.run(source, source_name=fixture.name)
    report = json.loads(result.report_path.read_text(encoding="utf-8"))
    if result.status != "complete":
        raise RuntimeError(f"{family} smoke analysis was partial: {result.notice}")
    if not result.output_path.is_file() or result.output_path.stat().st_size == 0:
        raise RuntimeError(f"{family} did not write recovered source")
    recovered = result.output_path.read_text(encoding="utf-8")
    if "[unluac error]" in recovered or "static preview only" in recovered.lower():
        raise RuntimeError(f"{family} output contains an analysis placeholder")

    if family == "MoonSec":
        analysis = report["family_specific_analysis"]
        if report["bytecode_executed"] or not analysis["lua51_bytecode_recovered"]:
            raise RuntimeError("MoonSec smoke route did not recover bytecode statically")
        if not analysis["source_parsed_as_luau"]:
            raise RuntimeError("MoonSec smoke output did not pass Luau syntax validation")
    elif family == "Luraph" and os.name == "nt":
        dynamic = report["dynamic_analysis"]
        if not dynamic["attempted"] or dynamic["isolation_backend"] != "Windows AppContainer":
            raise RuntimeError("Luraph VM analysis did not run through Windows AppContainer isolation")
        if luraph_ground_truth is None or not luraph_ground_truth.is_file():
            raise RuntimeError("pinned Luraph source ground truth is required for semantic validation")
        if report["family_specific_analysis"].get("partial_reasons"):
            raise RuntimeError(
                "Luraph lifter reported unresolved VM logic: "
                + "; ".join(report["family_specific_analysis"]["partial_reasons"])
            )
        if "Luraph runtime function, not devirtualized" in recovered:
            raise RuntimeError("Luraph output contains a generated runtime error stub")
        original_source = luraph_ground_truth.read_text(encoding="utf-8")
        original_result = _run_semantic_sample(
            original_source,
            label="luraph-ground-truth",
            tools_dir=tools_dir,
            work_dir=output_dir,
        )
        recovered_result = _run_semantic_sample(
            recovered,
            label="luraph-lifted-source",
            tools_dir=tools_dir,
            work_dir=output_dir,
        )
        if original_result != "34" or recovered_result != original_result:
            raise RuntimeError(
                "Luraph lifted source did not match the pinned original's result: "
                f"original={original_result!r}, lifted={recovered_result!r}"
            )

    print(
        f"{family}: recovered {result.output_path.stat().st_size} source bytes "
        f"through {result.route}; output passed Luau syntax validation."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Protez family-specific source recovery.")
    parser.add_argument("--luraph-fixture", type=Path, required=True)
    parser.add_argument("--luraph-ground-truth", type=Path)
    parser.add_argument("--moonsec-fixture", type=Path, required=True)
    parser.add_argument("--tools-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args.work_dir.mkdir(parents=True, exist_ok=True)
    _run_family(
        family="Luraph",
        fixture=args.luraph_fixture,
        tools_dir=args.tools_dir,
        work_dir=args.work_dir,
        luraph_ground_truth=args.luraph_ground_truth,
    )
    _run_family(
        family="MoonSec",
        fixture=args.moonsec_fixture,
        tools_dir=args.tools_dir,
        work_dir=args.work_dir,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
