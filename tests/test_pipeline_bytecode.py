from __future__ import annotations

import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.pipeline import DeobfuscationPipeline, InvalidLuauPayload


class BytecodePipelineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.tools = self.root / "tools"
        self.output.mkdir()
        self.tools.mkdir()

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _run_pipeline(self, *, reject_formatted: bool = False, bundled: bool = False):
        original = "local x=1;return x"
        formatted = "local x = 1;\nreturn x"
        verified: list[tuple[str, str]] = []

        def verify(_compiler, source: str, *, label: str) -> None:
            verified.append((source, label))
            if reject_formatted and source == formatted:
                raise InvalidLuauPayload("test-only rejection of the formatted candidate")

        pipeline = DeobfuscationPipeline(
            output_dir=self.output,
            tools_dir=self.tools,
            compiler_timeout_seconds=2,
            max_pipeline_seconds=10,
        )
        with (
            patch(
                "core.pipeline.LocalBytecodeDecompiler.decompile",
                return_value=(original, Path("/local/luau-decompiler")),
            ),
            patch(
                "core.pipeline.LocalBytecodeDecompiler.is_bundled_binary",
                return_value=bundled,
            ),
            patch("core.pipeline._LuauCompiler.verify_text", autospec=True, side_effect=verify),
        ):
            result = pipeline.run(b"compiled bytecode", source_name="input.luac")
        return result, verified, original, formatted

    def test_saves_only_compile_verified_formatting_and_reports_unverified_provenance(self) -> None:
        result, verified, original, formatted = self._run_pipeline()

        self.assertEqual(result.status, "complete")
        self.assertEqual(result.output_path.read_text(encoding="utf-8"), formatted)
        self.assertEqual(verified, [
            (original, "decompiled bytecode output"),
            (formatted, "formatted decompiled bytecode"),
        ])
        report = json.loads(result.report_path.read_text(encoding="utf-8"))
        self.assertFalse(report["bytecode_executed"])
        self.assertTrue(report["source_compiled_for_syntax_check_only"])
        self.assertTrue(report["formatting_applied"])
        self.assertEqual(report["formatting_validation"], "compile-only")
        self.assertEqual(report["decompiler_provenance"], "local-binary-unverified")
        self.assertIsNone(report["decompiler_source_commit"])

    def test_records_pinned_source_only_for_a_verified_bundled_binary(self) -> None:
        result, _verified, _original, _formatted = self._run_pipeline(bundled=True)
        report = json.loads(result.report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["decompiler_provenance"], "verified-frozen-bundle")
        self.assertEqual(
            report["decompiler_repository"],
            "https://github.com/PumbaaDev/luau-decompiler",
        )
        self.assertEqual(report["decompiler_source_commit"], "ee07098c31e11601a9ca434bc12932a4ded65f7b")

    def test_keeps_original_decompiler_output_when_formatted_candidate_fails(self) -> None:
        result, verified, original, formatted = self._run_pipeline(reject_formatted=True)

        self.assertEqual(result.output_path.read_text(encoding="utf-8"), original)
        self.assertEqual(verified[-1][0], formatted)
        report = json.loads(result.report_path.read_text(encoding="utf-8"))
        self.assertFalse(report["formatting_applied"])

    def test_source_pipeline_formats_only_after_static_compile_checks(self) -> None:
        source = "local x=1;return x"
        pipeline = DeobfuscationPipeline(
            output_dir=self.output,
            tools_dir=self.tools,
            compiler_timeout_seconds=2,
            max_pipeline_seconds=10,
        )
        with (
            patch("core.pipeline._LuauCompiler.verify_text", autospec=True),
            patch(
                "core.pipeline.DeobfuscationPipeline._trace_source",
                side_effect=RuntimeError("native worker unavailable in this test"),
            ),
        ):
            result = pipeline.run(source, source_name="input.luau")

        self.assertEqual(
            result.output_path.read_text(encoding="utf-8"),
            "local x = 1;\nreturn 1",
        )
        report = json.loads(result.report_path.read_text(encoding="utf-8"))
        self.assertTrue(report["formatting_applied"])
        self.assertIn("compile-verified whitespace formatting", report["selected_transformations"])


if __name__ == "__main__":
    unittest.main()
