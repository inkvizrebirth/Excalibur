from __future__ import annotations

import argparse
import json
import logging
import os
from pathlib import Path

from core.pipeline import DeobfuscationPipeline


def _run_family(
    *,
    family: str,
    fixture: Path,
    tools_dir: Path,
    work_dir: Path,
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

    print(
        f"{family}: recovered {result.output_path.stat().st_size} source bytes "
        f"through {result.route}; output passed Luau syntax validation."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Protez family-specific source recovery.")
    parser.add_argument("--luraph-fixture", type=Path, required=True)
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
