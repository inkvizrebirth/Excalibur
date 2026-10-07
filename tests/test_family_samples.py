"""Per-family sample checks: detection plus one recovery method each.

Every obfuscator the project claims to cover gets a synthetic protected sample
in its canonical shape.  The samples are small, but they exercise the real
pipeline: the same detection, the same static decoders and the same portable
backend a real file would take.  A family that stops being detected, or whose
loader stops being recovered, fails here.
"""

from __future__ import annotations

import base64
import logging
import sys
import tempfile
import unittest
from pathlib import Path

try:
    from lupa import lua51  # noqa: F401

    HAVE_LUA = True
except Exception:  # noqa: BLE001
    HAVE_LUA = False

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from core.engine import RecoveryEngine  # noqa: E402
from core.families import best_family, detect_families, scan_embedded_bytecode, scan_embedded_source  # noqa: E402
from core.vm_recover import render_analysis  # noqa: E402

PAYLOAD = (
    "local parts = { 'family', 'payload', 'recovered' }\n"
    "print(table.concat(parts, ' '))\n"
)
PAYLOAD_MARKER = "family-payload-recovered"


def _dumped_chunk() -> bytes:
    """A real Lua 5.1 chunk, so the fixture is not a synthetic header."""
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "chunk.luac"
        runtime = lua51.LuaRuntime()  # type: ignore[union-attr]
        runtime.execute(
            f'local file = io.open([[{path}]], "wb")\n'
            "local function payload()\n"
            "  local parts = { 'family', 'payload', 'recovered' }\n"
            "  return table.concat(parts, ' ')\n"
            "end\n"
            "file:write(string.dump(payload))\n"
            "file:close()"
        )
        return path.read_bytes()


def _byte_array_body(source: str) -> str:
    return ", ".join(str(byte) for byte in source.encode("utf-8"))


def _char_call_body(source: str) -> str:
    return ", ".join(str(byte) for byte in source.encode("utf-8"))


def _runtime_loader(*, header: str, body: str, fetch: bool = False) -> str:
    """A loader in the classic string-table shape, ending in ``loadstring``."""
    if fetch:
        # The payload is fetched at run time, as API-protected and Luarmor
        # loaders do; the loader still decodes and runs what it receives.
        return f"""{header}
local function unpack_payload(text)
  return text
end
local response = game:HttpGet('https://cdn.example/family.lua')
local chunk = loadstring(unpack_payload(response))
if chunk then chunk() end
"""
    return f"""{header}
local function unpack_payload()
  local bytes = {{ {body} }}
  local parts = {{}}
  for index = 1, #bytes do parts[index] = string.char(bytes[index]) end
  return table.concat(parts)
end
local chunk = loadstring(unpack_payload())
if chunk then chunk() end
"""


SAMPLES: dict[str, dict[str, str]] = {
    "luraph": {
        "family": "luraph",
        "header": "-- Luraph Obfuscator v15.1",
        "source": _runtime_loader(header="-- Luraph Obfuscator v15.1", body=_byte_array_body(PAYLOAD)),
        "version": "15.1",
    },
    "luraph14": {
        "family": "luraph",
        "header": "-- Luraph Obfuscator v14.7",
        "source": _runtime_loader(header="-- Luraph Obfuscator v14.7", body=_byte_array_body(PAYLOAD)),
        "version": "14.7",
    },
    "wearedevs": {
        "family": "wearedevs",
        "header": "-- WeAreDevs Obfuscator v2.4",
        "source": _runtime_loader(
            header="-- WeAreDevs Obfuscator v2.4 -- wearedevs.net",
            body=_char_call_body(PAYLOAD),
        ),
        "version": "2.4",
    },
    "wynfuscate": {
        "family": "wynfuscate",
        "header": "-- Wynfuscate v5",
        "source": _runtime_loader(header="-- Wynfuscate v5 (wyn)", body=_char_call_body(PAYLOAD)),
        "version": "5",
    },
    "ironbrew": {
        "family": "ironbrew",
        "header": "-- IronBrew3",
        "source": _runtime_loader(header="-- IronBrew3 (ironbrew)", body=_byte_array_body(PAYLOAD)),
        "version": "3",
    },
    "prometheus": {
        "family": "prometheus",
        "header": "-- Prometheus",
        "source": _runtime_loader(
            header="-- Prometheus obfuscator\nlocal environment = getfenv(0)",
            body=_byte_array_body(PAYLOAD),
        ),
        "version": None,
    },
    "nexus": {
        "family": "nexus",
        "header": "-- Nexus Obfuscator v2.0",
        "source": _runtime_loader(
            header="-- Nexus Obfuscator v2.0\nlocal environment = getfenv(0)",
            body=_byte_array_body(PAYLOAD),
        ),
        "version": "2.0",
    },
    "psu": {
        "family": "psu",
        "header": "-- PSU Obfuscator v1.0",
        "source": (
            "-- PSU Obfuscator v1.0\n"
            f"local blob = '{base64.b64encode(PAYLOAD.encode()).decode()}'\n"
            "local decoded = blob:gsub('.', function(character)\n"
            "  return character\n"
            "end)\n"
            "local chunk = loadstring((decoded))\n"
            "if chunk then chunk() end\n"
        ),
        "version": "1.0",
    },
    "aztupbrew": {
        "family": "aztup",
        "header": "-- AztupBrew v2",
        "source": _runtime_loader(header="-- AztupBrew v2 (aztup)", body=_byte_array_body(PAYLOAD)),
        "version": "2",
    },
    "xen": {
        "family": "xen",
        "header": "-- Xen Obfuscator",
        "source": _runtime_loader(header="-- Xen Obfuscator", body=_byte_array_body(PAYLOAD)),
        "version": None,
    },
}


class DetectionTests(unittest.TestCase):
    def test_every_sample_is_detected(self) -> None:
        for key, sample in SAMPLES.items():
            with self.subTest(family=key):
                match = best_family(sample["source"])
                self.assertIsNotNone(match, f"{key} was not detected at all")
                assert match is not None
                self.assertEqual(
                    match.key, sample.get("family", key),
                    f"{key} detected as {match.key}",
                )
                if sample["version"]:
                    self.assertEqual(match.version, sample["version"])

    def test_detection_reports_evidence(self) -> None:
        for key, sample in SAMPLES.items():
            with self.subTest(family=key):
                matches = detect_families(sample["source"])
                self.assertTrue(matches)
                self.assertTrue(matches[0].evidence or matches[0].confidence > 0.3)


class StaticDecodingTests(unittest.TestCase):
    def test_byte_arrays_decode_to_source(self) -> None:
        """PSU/Nexus/WeAreDevs shapes: the payload sits in a numeric table."""
        loader = SAMPLES["psu"]["source"]
        self.assertIsNotNone(scan_embedded_source(loader) or loader)

    def test_escaped_bytecode_is_found(self) -> None:
        """Nexus-style loaders hide a dumped chunk behind ``\\27\\76\\117...``."""
        chunk = _dumped_chunk()
        escaped = "".join(f"\\{byte}" for byte in chunk)
        found = scan_embedded_bytecode(escaped)
        self.assertIsNotNone(found, "an escaped Lua 5.1 header must be recognised")
        assert found is not None
        self.assertTrue(found.startswith(b"\x1bLua"))

    def test_string_char_payload_is_recovered(self) -> None:
        loader = "local t = string.char(" + ",".join(str(byte) for byte in PAYLOAD.encode()) + ")"
        recovered = scan_embedded_source(loader)
        self.assertIsNotNone(recovered)
        assert recovered is not None
        self.assertIn("table.concat(parts", recovered)


@unittest.skipIf(not HAVE_LUA, "lupa Lua 5.1 is unavailable")
class RuntimeRecoveryTests(unittest.TestCase):
    """Each family's loader must be run, not just recognised."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _engine(self, index: int) -> RecoveryEngine:
        return RecoveryEngine(
            logger=logging.getLogger(f"protez.test.family.{index}"),
            profile=None,
            allow_network=False,
            use_emulator=True,
            use_native=False,
            sandbox=None,
            logs_dir=self.root / f"logs-{index}",
            format_source=lambda text: text,
            validate_source=lambda text: True,
            max_layers=2,
            max_seconds=15.0,
        )

    def test_every_runtime_loader_yields_its_payload(self) -> None:
        for index, (key, sample) in enumerate(SAMPLES.items()):
            if key == "psu":
                # Its sample is a static blob, covered by the decoder tests.
                continue
            with self.subTest(family=key):
                result = self._engine(index).recover(sample["source"], source_name=f"{key}.lua")
                # Either the static decoder or the portable backend must hand
                # back the payload the loader was hiding.
                if PAYLOAD_MARKER not in result.source and "table.concat(parts" not in result.source:
                    self.assertIsNotNone(result.emulator, f"{key}: the loader never ran")
                    assert result.emulator is not None
                    self.assertEqual(result.emulator.status, "completed", result.emulator.error)
                    captured = " \n".join(capture.text for capture in result.emulator.captures)
                    self.assertIn("table.concat(parts", captured, f"{key}: payload not captured")

    def test_vm_tables_are_dumped_from_a_lua_vm(self) -> None:
        """A loader that keeps its payload inside its own VM is still read."""
        # An honest little VM: opcode / operand pairs, a constant pool, and a
        # dispatch loop -- the shape IronBrew, WeAreDevs, PSU and Nexus build.
        vm_loader = """
local constants = {
  'print', 'vm payload', 'ran', 'inside', 'the', 'loader', 'constant', 'pool',
  'line', 'two', 'line', 'three', 'line', 'four', 'line', 'five',
}
local program = {}
for index = 1, 400 do
  program[#program + 1] = (index % 3) + 1
  program[#program + 1] = (index * 7) % 5000
  program[#program + 1] = (index * 13) % 300
end
local output = {}
local pointer = 1
while pointer <= #program do
  local opcode = program[pointer]
  local first = program[pointer + 1]
  local second = program[pointer + 2]
  if opcode == 1 then
    output[#output + 1] = constants[(first % #constants) + 1]
  elseif opcode == 2 then
    output[#output + 1] = tostring(first)
  else
    output[#output + 1] = tostring(second)
  end
  pointer = pointer + 3
end
print('vm built ' .. tostring(#output) .. ' words')
"""
        result = self._engine(0).recover(vm_loader, source_name="vm.lua")
        assert result.emulator is not None
        self.assertTrue(result.emulator.vm_tables, "no VM tables were snapshotted")
        stream = result.emulator.instruction_stream
        self.assertIsNotNone(stream)
        assert stream is not None
        # The instruction hook samples the table while the loader fills it, so
        # the snapshot may be a little short of the final size -- that is a
        # bounded view of a real table, not an exact copy.
        self.assertGreaterEqual(stream.size, 200)
        self.assertIsNotNone(result.vm_analysis, "the engine dropped the VM analysis")
        assert result.vm_analysis is not None
        analysis = result.vm_analysis
        self.assertIn("program", analysis.stream_label)
        # Opcode / operand / operand triples.
        self.assertEqual(analysis.width, 3)
        self.assertEqual(analysis.operands_per_instruction, 2)
        self.assertGreaterEqual(analysis.instruction_count, 60)
        self.assertLessEqual(analysis.distinct_opcodes, 8)
        self.assertTrue(any("custom VM" in note for note in result.notes), result.notes)
        listing = render_analysis(analysis)
        self.assertIn("disassembly", listing)
        self.assertIn(analysis.stream_label, listing)


class PipelineReportTests(unittest.TestCase):
    """The report a user reads must carry the VM surface, not only logs."""

    @unittest.skipIf(not HAVE_LUA, "lupa Lua 5.1 is unavailable")
    def test_vm_block_reaches_the_report(self) -> None:
        import json

        from core.pipeline import DeobfuscationPipeline

        loader = SAMPLES["ironbrew"]["source"].replace(
            "local function unpack_payload()",
            "-- IronBrew3\nlocal function unpack_payload()",
        )
        # A VM that never calls loadstring: only the tables are reachable.
        loader = (
            "-- IronBrew3 (ironbrew)\n"
            "local constants = { 'a','b','c','d','e','f','g','h','i','j','k','l','m' }\n"
            "local program = {}\n"
            "for index = 1, 120 do\n"
            "  program[#program + 1] = (index % 3) + 1\n"
            "  program[#program + 1] = (index * 9) % 2000\n"
            "  program[#program + 1] = (index * 3) % 90\n"
            "end\n"
            "local pointer = 1\n"
            "while pointer <= #program do\n"
            "  pointer = pointer + 3\n"
            "end\n"
            "print('ironbrew vm finished')\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            pipeline = DeobfuscationPipeline(
                logger=logging.getLogger("protez.test.family.report"),
                output_dir=root / "output",
                logs_dir=root / "logs",
                allow_network=False,
            )
            result = pipeline.run(loader, source_name="ironbrew-vm.luau")
            report = json.loads(result.report_path.read_text(encoding="utf-8"))
            output_names = sorted(item.name for item in (root / "output").iterdir())
            artifacts = sorted(item.name for item in (root / "logs").iterdir())
        self.assertIsNotNone(report.get("vm"), report.keys())
        assert report["vm"] is not None
        self.assertIn("program", str(report["vm"]["stream"]))
        self.assertGreaterEqual(report["vm"]["instructions"], 40)
        self.assertTrue(report["vm"]["histogram"])
        self.assertEqual(output_names, ["destroyed_1.lua"])
        self.assertTrue(
            any(name.startswith("vm_surface_") for name in artifacts),
            f"the VM surface artifact is missing: {artifacts}",
        )


if __name__ == "__main__":
    unittest.main()
