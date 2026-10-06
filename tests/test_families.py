from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.families import (
    best_family,
    detect_families,
    family_report,
    handler_for,
    scan_embedded_bytecode,
    supported_families,
)

NAMED_SAMPLES = {
    "luraph": ("-- This file was protected using Luraph Obfuscator v15.1 [https://lura.ph/]", "15.1"),
    "luraph-v14": ("-- protected using Luraph v14.7", "14.7"),
    "wearedevs": ("-- WeAreDevs Obfuscator v2.4", "2.4"),
    "wynfuscate": ("-- Wynfuscate v5", "5"),
    "ironbrew": ("-- IronBrew:^3", "3"),
    "prometheus": ("--[[ Prometheus ]]\n-- by levno-710", None),
    "nexus": ("-- Nexus Obfuscator v2.0", "2.0"),
    "psu": ("-- PSU Obfuscator v1.0", "1.0"),
    "moonsec": ("-- MoonSec V3", "3"),
    "aztup": ("-- AztupBrew 2.0.0", "2.0.0"),
}


class DetectionTests(unittest.TestCase):
    def test_every_named_family_is_detected(self) -> None:
        for key, (sample, expected_version) in NAMED_SAMPLES.items():
            with self.subTest(family=key):
                matches = detect_families(sample)
                self.assertTrue(matches, f"{key} produced no match")
                top = matches[0]
                self.assertGreaterEqual(top.confidence, 0.5)
                if expected_version is not None:
                    self.assertEqual(top.version, expected_version)

    def test_plain_scripts_stay_unlabelled(self) -> None:
        source = "local value = 1\nprint(value)\nlocal function double(x) return x * 2 end"
        self.assertEqual(detect_families(source), ())
        self.assertIsNone(best_family(source))

    def test_family_report_is_serialisable(self) -> None:
        report = family_report(NAMED_SAMPLES["luraph"][0])
        self.assertTrue(report)
        self.assertEqual(report[0]["key"], "luraph")
        self.assertIn("confidence", report[0])
        self.assertIn("evidence", report[0])

    def test_handler_lookup(self) -> None:
        handler = handler_for("ironbrew")
        self.assertIsNotNone(handler)
        self.assertEqual(handler.display_name, "IronBrew")
        self.assertIsNone(handler_for("nope"))

    def test_supported_families_lists_the_named_set(self) -> None:
        keys = {key for key, _label in supported_families()}
        for expected in (
            "luraph",
            "moonsec",
            "wearedevs",
            "ironbrew",
            "psu",
            "nexus",
            "prometheus",
            "wynfuscate",
            "aztup",
            "generic-vm",
        ):
            self.assertIn(expected, keys)


class EmbeddedBytecodeTests(unittest.TestCase):
    def _lua_chunk(self) -> bytes | None:
        try:
            from lupa import lua51
        except Exception:  # noqa: BLE001
            return None
        with tempfile.TemporaryDirectory() as temporary:
            dump_path = Path(temporary) / "chunk.luac"
            runtime = lua51.LuaRuntime()
            runtime.execute(
                f'local file = io.open([[{dump_path}]], "wb")\n'
                "file:write(string.dump(function(value) return value * 2 end))\n"
                "file:close()"
            )
            return dump_path.read_bytes()

    def test_finds_a_lua51_chunk_inside_a_numeric_array(self) -> None:
        chunk = self._lua_chunk()
        if chunk is None:
            self.skipTest("lupa is unavailable")
        text = "local data = {" + ",".join(str(byte) for byte in chunk) + "}"
        found = scan_embedded_bytecode(text)
        self.assertIsNotNone(found)
        assert found is not None
        self.assertIn(b"\x1bLua", found)

    def test_returns_none_without_a_chunk(self) -> None:
        self.assertIsNone(scan_embedded_bytecode("local value = 1\nprint(value)"))


if __name__ == "__main__":
    unittest.main()
