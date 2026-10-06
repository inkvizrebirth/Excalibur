from __future__ import annotations

import json
import tempfile
import time
import unittest
from pathlib import Path
from unittest.mock import patch

from core.deobfuscator import deobfuscate_source
from core.luraph_devirtualizer import (
    LuraphDevirtualizationResult,
    _lift_incomplete_reasons,
    _prepare_lifted_source,
)
from core.pipeline import DeobfuscationPipeline, _LuauCompiler
from core.protection import inspect_protection


class LuraphLiftQualityTests(unittest.TestCase):
    def test_removes_unused_shared_runtime_error_stub(self) -> None:
        source = (
            'local function luraph_runtime1(...)\n'
            '\terror("Luraph runtime function, not devirtualized")\n'
            "end\n"
            "return 42\n"
        )

        cleaned, unresolved, placeholders = _prepare_lifted_source(source)

        self.assertEqual(cleaned, "return 42\n")
        self.assertEqual(unresolved, ())
        self.assertEqual(sum(placeholders.values()), 0)
        self.assertEqual(
            _lift_incomplete_reasons(
                source=cleaned,
                stats={"functions": 1, "errors": 0, "fallbacks": 0},
                unresolved_constant_count=0,
                unresolved_runtime_functions=unresolved,
                placeholder_counts=placeholders,
            ),
            (),
        )

    def test_used_shared_runtime_function_is_reported_without_fake_behavior(self) -> None:
        source = (
            'local function luraph_runtime2(...)\n'
            '\terror("Luraph runtime function, not devirtualized")\n'
            "end\n"
            "return luraph_runtime2(payload)\n"
        )

        cleaned, unresolved, _placeholders = _prepare_lifted_source(source)

        self.assertNotIn('error("Luraph runtime function, not devirtualized")', cleaned)
        self.assertNotIn("local function luraph_runtime2", cleaned)
        self.assertIn("Unresolved Luraph runtime function luraph_runtime2 was omitted", cleaned)
        self.assertIn("luraph_runtime2(payload)", cleaned)
        self.assertEqual(unresolved, ("luraph_runtime2",))

    def test_unresolved_markers_in_strings_are_not_mistaken_for_placeholders(self) -> None:
        source = 'return "nil --[[ constant not decoded ]]"\n'

        _cleaned, _unresolved, placeholders = _prepare_lifted_source(source)

        self.assertEqual(placeholders["undecoded_constants"], 0)

    def test_unlifted_blocks_and_unknown_constants_force_partial_status(self) -> None:
        source = "return nil --[[ constant not decoded ]]\n"
        cleaned, unresolved, placeholders = _prepare_lifted_source(source)
        reasons = _lift_incomplete_reasons(
            source=cleaned,
            stats={"functions": 3, "errors": 2, "fallbacks": 4},
            unresolved_constant_count=1,
            unresolved_runtime_functions=unresolved,
            placeholder_counts=placeholders,
        )

        self.assertIn("2 VM blocks could not be lifted", reasons)
        self.assertIn("1 lazy constants remain unresolved", reasons)
        self.assertIn("1 undecoded constants remain in the lifted source", reasons)

    def test_pipeline_keeps_unlifted_luau_as_a_partial_candidate(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            root = Path(temporary_directory)
            output = root / "output"
            tools = root / "tools"
            output.mkdir()
            tools.mkdir()
            pipeline = DeobfuscationPipeline(output_dir=output, tools_dir=tools)
            original = "-- Luraph Obfuscator v15\nreturn 42"
            profile = inspect_protection(original)
            assert profile is not None
            candidate = "return 42\n"
            devirtualized = LuraphDevirtualizationResult(
                source=candidate,
                route="luraph-v15-vm-lifter",
                run_results=(),
                trace_source=None,
                source_bytes=len(original.encode("utf-8")),
                elapsed_seconds=0.1,
                lift_stats={"functions": 3, "errors": 2, "fallbacks": 1},
                unresolved_constant_count=0,
                unresolved_constant_samples=(),
                constant_misses={},
                unresolved_runtime_functions=(),
                placeholder_counts={"undecoded_constants": 0},
                incomplete_reasons=("2 VM blocks could not be lifted",),
            )
            compiler = _LuauCompiler(
                tools_dir=tools,
                timeout_seconds=2.0,
                logger=pipeline.logger,
            )
            with (
                patch("core.pipeline._LuauCompiler.verify_text"),
                patch.object(
                    pipeline,
                    "_format_verified_candidate",
                    return_value=(candidate, False),
                ),
            ):
                result = pipeline._write_luraph_devirtualized_result(
                    source=original,
                    source_name="input.luau",
                    profile=profile,
                    source_analysis=deobfuscate_source(original),
                    devirtualized=devirtualized,
                    compiler=compiler,
                    started=time.monotonic(),
                    deadline=time.monotonic() + 10.0,
                )

            self.assertEqual(result.status, "partial")
            self.assertIn(".candidate.luau", result.output_path.name)
            self.assertIsNotNone(result.preview_path)
            report = json.loads(result.report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["status"], "partial")
            self.assertIsNone(report["outputs"]["source"])
            self.assertEqual(report["outputs"]["partial_source_candidate"], str(result.output_path))
            self.assertEqual(
                report["family_specific_analysis"]["lift_stats"]["errors"],
                2,
            )


if __name__ == "__main__":
    unittest.main()
