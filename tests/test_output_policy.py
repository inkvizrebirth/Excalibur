from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.output import (
    OUTPUT_STEM,
    clean_result_header,
    existing_outputs,
    next_output_index,
    next_output_path,
    prune_legacy_artifacts,
    report_path,
    write_text_atomic,
)


class OutputNamingTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_first_output_is_number_one(self) -> None:
        self.assertEqual(next_output_path(self.root).name, f"{OUTPUT_STEM}_1.lua")

    def test_index_increments_per_run(self) -> None:
        (self.root / "destroyed_1.lua").write_text("-- one\n", encoding="utf-8")
        (self.root / "destroyed_2.lua").write_text("-- two\n", encoding="utf-8")
        self.assertEqual(next_output_index(self.root), 3)
        self.assertEqual(next_output_path(self.root).name, "destroyed_3.lua")

    def test_invalid_names_are_ignored(self) -> None:
        (self.root / "destroyed.lua").write_text("-- x\n", encoding="utf-8")
        (self.root / "notes.txt").write_text("x\n", encoding="utf-8")
        self.assertEqual(existing_outputs(self.root), ())
        self.assertEqual(next_output_index(self.root), 1)

    def test_atomic_write_replaces_content(self) -> None:
        target = self.root / "destroyed_1.lua"
        write_text_atomic(target, "-- first\n")
        write_text_atomic(target, "-- second\n")
        self.assertEqual(target.read_text(encoding="utf-8"), "-- second\n")
        self.assertEqual([item.name for item in self.root.iterdir()], ["destroyed_1.lua"])


class PruneTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_legacy_artifacts_are_removed_and_results_kept(self) -> None:
        legacy = {
            "deobfuscated_20240101_000000.luau": "x",
            "analysis_20240101.report.json": "{}",
            "payload.candidate.luau": "x",
            "captured_payload_1.luau": "x",
        }
        for name, body in legacy.items():
            (self.root / name).write_text(body, encoding="utf-8")
        keeper = self.root / "destroyed_7.lua"
        keeper.write_text("-- keep\n", encoding="utf-8")

        removed = prune_legacy_artifacts(self.root)

        self.assertEqual({path.name for path in removed}, set(legacy))
        self.assertEqual([item.name for item in self.root.iterdir()], ["destroyed_7.lua"])


class HeaderTests(unittest.TestCase):
    def test_header_reports_the_essentials(self) -> None:
        header = clean_result_header(
            source_name="loader.lua",
            family_label="Luraph Obfuscator v15.1",
            method="multi-layer recovery",
            partial=True,
            notes=("layer 1: payload captured",),
            profile_label="Auto — all executors (recommended)",
            layers=2,
        )
        self.assertIn("PARTIAL RECOVERY", header)
        self.assertIn("loader.lua", header)
        self.assertIn("Luraph Obfuscator v15.1", header)
        self.assertIn("layer 1: payload captured", header)
        self.assertTrue(header.startswith("--" + "=" * 72))

    def test_complete_header_has_no_approximation_notice(self) -> None:
        header = clean_result_header(
            source_name="clean.lua",
            family_label="custom VM / unknown obfuscator",
            method="multi-layer recovery",
            partial=False,
        )
        self.assertIn("-- Protez - RECOVERED", header)
        self.assertNotIn("approximation", header)

    def test_report_path_carries_source_name(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = report_path(Path(temporary), source_name="loader.lua")
            self.assertTrue(path.name.startswith("report_"))
            self.assertTrue(path.name.endswith("loader.lua.json"))
            self.assertTrue(path.parent.is_dir())


if __name__ == "__main__":
    unittest.main()
