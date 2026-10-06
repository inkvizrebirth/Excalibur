from __future__ import annotations

import argparse
import json
import logging
import os
import re
import shutil
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
    expect_remote_payload_loader: bool = False,
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
    analysis = report["family_specific_analysis"]
    outputs = report.get("outputs", {})
    if expect_remote_payload_loader:
        if result.status != "partial" or not analysis.get("remote_payload_loader_count"):
            raise RuntimeError(f"{family} did not report the fixture's remote payload loader as partial")
        source_path = Path(outputs.get("partial_source_candidate") or "")
        if not source_path.is_file():
            raise RuntimeError(f"{family} did not preserve its partial source candidate")
        if family == "Luraph":
            captures = outputs.get("runtime_capture_payloads", [])
            if not any(
                int(capture.get("size_bytes", 0)) >= 512
                and capture.get("output")
                and Path(capture["output"]).is_file()
                for capture in captures
            ):
                raise RuntimeError("Luraph did not preserve its captured VM payload for further analysis")
    else:
        if result.status != "complete":
            raise RuntimeError(f"{family} smoke analysis was partial: {result.notice}")
        source_path = result.output_path
    if not source_path.is_file() or source_path.stat().st_size == 0:
        raise RuntimeError(f"{family} did not write a source candidate")
    recovered = source_path.read_text(encoding="utf-8")
    if "[unluac error]" in recovered or "static preview only" in recovered.lower():
        raise RuntimeError(f"{family} output contains an analysis placeholder")

    if family == "Luraph":
        capture_dir = output_dir / "runtime-captures" / fixture.stem
        for run_index, run in enumerate(report.get("dynamic_analysis", {}).get("runs", []), start=1):
            for capture_index, capture in enumerate(run.get("captures", []), start=1):
                captured_path = Path(capture.get("path", ""))
                if captured_path.is_file():
                    capture_dir.mkdir(parents=True, exist_ok=True)
                    suffix = captured_path.suffix or ".luau"
                    destination = capture_dir / f"run-{run_index:02d}-capture-{capture_index:02d}{suffix}"
                    shutil.copyfile(captured_path, destination)

    if family == "MoonSec":
        if report["bytecode_executed"] or not analysis["lua51_bytecode_recovered"]:
            raise RuntimeError("MoonSec smoke route did not recover bytecode statically")
        if not analysis["source_parsed_as_luau"]:
            raise RuntimeError("MoonSec smoke output did not pass Luau syntax validation")
    semantic_match = False
    if family == "Luraph" and os.name == "nt":
        dynamic = report["dynamic_analysis"]
        if not dynamic["attempted"] or dynamic["isolation_backend"] != "Windows AppContainer":
            raise RuntimeError("Luraph VM analysis did not run through Windows AppContainer isolation")
        partial_reasons = report["family_specific_analysis"].get("partial_reasons", [])
        unexpected_reasons = [
            reason for reason in partial_reasons
            if not (expect_remote_payload_loader and "remotely fetched Lua payloads are not embedded" in reason)
        ]
        if unexpected_reasons:
            raise RuntimeError(
                "Luraph lifter reported unresolved VM logic: "
                + "; ".join(unexpected_reasons)
            )
        if "Luraph runtime function, not devirtualized" in recovered:
            raise RuntimeError("Luraph output contains a generated runtime error stub")
        if luraph_ground_truth is not None:
            if not luraph_ground_truth.is_file():
                raise RuntimeError("the pinned Luraph source ground truth is missing")
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
            semantic_match = True

    semantic_note = "; matched pinned original behavior" if semantic_match else ""
    print(
        f"{family} ({fixture.name}): recovered {result.output_path.stat().st_size} source bytes "
        f"through {result.route}; output passed Luau syntax validation{semantic_note}."
    )


def main() -> int:
    parser = argparse.ArgumentParser(description="Smoke-test Protez family-specific source recovery.")
    parser.add_argument("--luraph-fixture", type=Path, action="append", required=True)
    parser.add_argument("--luraph-ground-truth", type=Path)
    parser.add_argument("--moonsec-fixture", type=Path, action="append", required=True)
    parser.add_argument("--remote-payload-loader-fixture", type=Path, action="append", default=[])
    parser.add_argument("--tools-dir", type=Path, required=True)
    parser.add_argument("--work-dir", type=Path, required=True)
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO, format="%(levelname)s: %(message)s")
    args.work_dir.mkdir(parents=True, exist_ok=True)
    remote_loader_fixtures = {path.resolve() for path in args.remote_payload_loader_fixture}
    for index, fixture in enumerate(args.luraph_fixture):
        _run_family(
            family="Luraph",
            fixture=fixture,
            tools_dir=args.tools_dir,
            work_dir=args.work_dir,
            # The first fixture is the one with a published source oracle.
            luraph_ground_truth=args.luraph_ground_truth if index == 0 else None,
            expect_remote_payload_loader=fixture.resolve() in remote_loader_fixtures,
        )
    for fixture in args.moonsec_fixture:
        _run_family(
            family="MoonSec",
            fixture=fixture,
            tools_dir=args.tools_dir,
            work_dir=args.work_dir,
            expect_remote_payload_loader=fixture.resolve() in remote_loader_fixtures,
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
