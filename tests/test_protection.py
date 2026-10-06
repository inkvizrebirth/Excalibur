from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.pipeline import DeobfuscationPipeline
from core.protection import inspect_protection


class ProtectionDetectionTests(unittest.TestCase):
    def test_detects_luraph_version_and_large_lph_payload_statically(self) -> None:
        source = (
            "-- This file was protected using Luraph Obfuscator v14.7 [https://lura.ph/]\n"
            'local payload = [=[LPH&'
            + "A" * 5000
            + "]=]\nlocal label = \"Visible label\""
        )

        profile = inspect_protection(source)

        self.assertIsNotNone(profile)
        assert profile is not None
        self.assertEqual(profile.display_name, "Luraph Obfuscator v14.7")
        self.assertGreater(profile.embedded_payload_chars, 5000)
        self.assertIn("Visible label", profile.visible_literals)

    def test_ignores_a_luraph_header_mentioned_only_in_a_string(self) -> None:
        source = 'local label = "Luraph Obfuscator v14.7"'
        self.assertIsNone(inspect_protection(source))

    def test_pipeline_returns_partial_report_when_isolated_worker_is_unavailable(self) -> None:
        source = (
            "-- This file was protected using Luraph Obfuscator v14.7 [https://lura.ph/]\n"
            'local payload = [=[LPH&'
            + "B" * 6000
            + "]=]\nlocal greeting = \"Hello from the wrapper\""
        )
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            pipeline = DeobfuscationPipeline(
                logger=logging.getLogger("protez.test.protection"),
                output_dir=output_dir,
                tools_dir=output_dir / "no-tools",
            )

            with patch.object(
                DeobfuscationPipeline,
                "_trace_source",
                side_effect=RuntimeError("native worker unavailable"),
            ):
                result = pipeline.run(source, source_name="luraph-sample.luau")

            self.assertEqual(result.status, "partial")
            self.assertEqual(result.route, "static-protection-report")
            self.assertIsNone(result.sandbox_result)
            self.assertIsNotNone(result.preview_path)
            self.assertTrue(result.output_path.is_file())
            self.assertTrue(result.report_path.is_file())
            assert result.preview_path is not None
            self.assertTrue(result.preview_path.is_file())

            summary = result.output_path.read_text(encoding="utf-8")
            self.assertIn("ORIGINAL SOURCE NOT RECONSTRUCTED", summary)
            self.assertIn("wrapper did not run", summary.lower())
            self.assertIn("Luraph Obfuscator v14.7", summary)

            preview = result.preview_path.read_text(encoding="utf-8")
            self.assertIn("static preview only", preview)
            self.assertIn("not reconstructed source", preview)
            self.assertIn("LPH&", preview)

            machine_report = json.loads(result.report_path.read_text(encoding="utf-8"))
            self.assertFalse(machine_report["source_reconstructed"])
            self.assertFalse(machine_report["dynamic_analysis"]["worker_started"])
            self.assertEqual(machine_report["wrapper_execution_outcome"], "not-started")
            self.assertEqual(machine_report["status"], "partial")

            # Output hygiene: the run leaves a single destroyed_N.lua behind and
            # parks the raw intermediates next to the report under logs/.
            self.assertEqual([item.name for item in output_dir.iterdir()], ["destroyed_1.lua"])
            parked = [
                Path(value)
                for value in machine_report.get("outputs", {}).values()
                if isinstance(value, str)
            ]
            for parked_path in parked:
                if parked_path.suffix in {".luau", ".luac", ".bin"}:
                    self.assertTrue(parked_path.is_file(), parked_path)

    def test_valid_source_is_kept_when_isolated_worker_cannot_start(self) -> None:
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            pipeline = DeobfuscationPipeline(
                logger=logging.getLogger("protez.test.elevated"),
                output_dir=output_dir,
                tools_dir=output_dir / "no-tools",
            )
            with (
                patch("core.pipeline._LuauCompiler") as compiler_factory,
                patch.object(
                    DeobfuscationPipeline,
                    "_trace_source",
                    side_effect=RuntimeError("native worker unavailable"),
                ),
            ):
                compiler_factory.return_value.timeout_seconds = 10.0
                result = pipeline.run("local answer = 42", source_name="static.luau")

            self.assertEqual(result.status, "complete")
            self.assertIsNone(result.sandbox_result)
            report = json.loads(result.report_path.read_text(encoding="utf-8"))
            self.assertEqual(report["dynamic_analysis"]["execution_outcome"], "not-started")
            self.assertIn("native worker unavailable", report["dynamic_analysis"]["error"])
            # The engine route validates the recovered candidate and the legacy
            # route re-checks the kept original, so verification runs at least once.
            self.assertTrue(compiler_factory.return_value.verify_text.called)
            labels = {
                call.kwargs.get("label")
                for call in compiler_factory.return_value.verify_text.call_args_list
            }
            self.assertIn("recovered candidate", labels)


if __name__ == "__main__":
    unittest.main()
