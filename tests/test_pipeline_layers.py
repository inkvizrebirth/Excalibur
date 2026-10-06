"""End-to-end checks for the layered recovery route.

These exercise the public ``DeobfuscationPipeline.run`` entry point with the
shapes that used to defeat the tool: a loader that builds its chunk from a
byte array, and a wrapper that probes the executor environment before doing
any real work.
"""

from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path

try:
    from lupa import lua51  # type: ignore
except Exception:  # noqa: BLE001
    lua51 = None  # type: ignore[assignment]

from core.pipeline import DeobfuscationPipeline

BANNER = "--" + "=" * 72


def artifact_body(path: Path) -> str:
    text = Path(path).read_text(encoding="utf-8")
    if text.startswith(BANNER):
        closing = text.find(BANNER, len(BANNER))
        if closing != -1:
            return text[closing + len(BANNER):].strip("\n")
    return text


def _lua_chunk() -> bytes:
    """Dump a real Lua 5.1 chunk so the fixture is not a synthetic header."""
    with tempfile.TemporaryDirectory() as temporary:
        dump_path = Path(temporary) / "chunk.luac"
        runtime = lua51.LuaRuntime()  # type: ignore[union-attr]
        runtime.execute(
            f'local file = io.open([[{dump_path}]], "wb")\n'
            "local function total(list)\n"
            "  local sum = 0\n"
            "  for index = 1, #list do sum = sum + list[index] end\n"
            "  return sum\n"
            "end\n"
            "file:write(string.dump(total))\n"
            "file:close()"
        )
        return dump_path.read_bytes()


class _PipelineCase(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.logs = self.root / "logs"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _run(self, source: str, name: str):
        pipeline = DeobfuscationPipeline(
            logger=logging.getLogger("protez.test.layers"),
            output_dir=self.output,
            logs_dir=self.logs,
            tools_dir=self.root / "no-tools",
            allow_network=False,
            max_pipeline_seconds=20,
        )
        result = pipeline.run(source, source_name=name)
        report = json.loads(Path(result.report_path).read_text(encoding="utf-8"))
        return result, report


class ByteArrayLoaderTests(_PipelineCase):
    @unittest.skipIf(lua51 is None, "lupa Lua 5.1 is unavailable")
    def test_loader_is_replaced_by_the_lifted_chunk(self) -> None:
        chunk = _lua_chunk()
        source = (
            "-- IronBrew:^3 protected\n"
            "local payload = {" + ",".join(str(byte) for byte in chunk) + "}\n"
            "local parts = {}\n"
            "for index = 1, #payload do\n"
            "  parts[index] = string.char(payload[index])\n"
            "end\n"
            "local blob = table.concat(parts)\n"
            "return loadstring(blob)()\n"
        )
        result, report = self._run(source, "byte_array_loader.lua")
        body = artifact_body(result.output_path)

        self.assertIn("Recovered from Lua 5.1 bytecode", body)
        self.assertNotIn("string.char(payload[index])", body)
        self.assertEqual(report["family"], "IronBrew")
        self.assertTrue(report["partial"], "lifted bytecode is an approximation")
        self.assertEqual(result.status, "partial")
        self.assertIn("PARTIAL RECOVERY", Path(result.output_path).read_text(encoding="utf-8"))
        self.assertEqual([item.name for item in self.output.iterdir()], ["destroyed_1.lua"])


class ExecutorProbeTests(_PipelineCase):
    def test_probe_wrapper_survives_and_stays_readable(self) -> None:
        source = (
            "-- Nexus Obfuscator v2.0\n"
            "local executor = identifyexecutor and identifyexecutor() or 'unknown'\n"
            "assert(isfunction(print) or type(print) == 'function')\n"
            "local genv = getgenv()\n"
            "genv.loaded = true\n"
            "if syn and syn.protect_gui then syn.protect_gui(nil) end\n"
            "print('running under', executor)\n"
        )
        result, report = self._run(source, "probe.lua")
        body = artifact_body(result.output_path)

        self.assertIn("identifyexecutor", body)
        self.assertIn("getgenv", body)
        self.assertIn(report["route"], {"recovery engine", "direct-source"})
        self.assertEqual([item.name for item in self.output.iterdir()], ["destroyed_1.lua"])


class PlainSourceTests(_PipelineCase):
    def test_plain_script_is_returned_unchanged(self) -> None:
        source = "local greeting = 'hi'\nprint(greeting)\n"
        result, report = self._run(source, "plain.lua")
        body = artifact_body(result.output_path)

        self.assertIn("local greeting", body)
        self.assertIn("print(greeting)", body)
        self.assertEqual(result.status, "complete")

    def test_status_field_matches_the_report(self) -> None:
        source = "local value = 40 + 2\nprint(value)\n"
        result, report = self._run(source, "status.lua")
        expected = "partial" if report["partial"] else "complete"
        self.assertEqual(result.status, expected)


if __name__ == "__main__":
    unittest.main()
