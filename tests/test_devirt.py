"""Own devirtualizers: container readers, per-family methods, registry, engine.

``core.devirt`` is where Protez stops relying on somebody else's lifter.  These
tests pin the behaviour each method promises:

* the byte containers (arrays, ``string.char`` runs, concatenated literals) are
  decoded and validated as real Lua 5.1 chunks;
* a chunk that only exists *at runtime*, inside a table the loader filled, is
  rebuilt from ``core.vm_dump`` snapshots (the door static passes cannot open);
* a custom table VM gets an annotated disassembly, with opcode names read from
  the loader's own dispatcher and pool constants inlined;
* a Prometheus-style dispatcher is re-ordered into straight-line code -- and
  left alone whenever the state graph is not fully known;
* the engine actually routes a family through its own method.
"""

from __future__ import annotations

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

from core.devirt import available_families, devirtualize, report_table  # noqa: E402
from core.devirt import bytecode_vm, nexus, prometheus, table_vm  # noqa: E402
from core.devirt.common import (  # noqa: E402
    chunk_from_values,
    find_lua51_chunk,
    lua_string_value,
    string_runs,
)
from core.engine import RecoveryEngine  # noqa: E402
from core.vm_dump import VmSnapshot  # noqa: E402

# The payload's three string constants survive bytecode lifting as literals,
# even though the concat() call itself becomes register pseudocode.
PAYLOAD_PIECES = ("family", "payload", "recovered")


class _PayloadAssertions:
    def assertPseudocode(self, source: object) -> None:  # noqa: N802 - unittest style
        text = str(source)
        for piece in PAYLOAD_PIECES:
            self.assertIn(f'"{piece}"', text)


def _dumped_chunk() -> bytes:
    """A real Lua 5.1 chunk (lupa dumps it), so nothing here is a fake header."""
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


class _ChunkFixture:
    """Builds one real Lua 5.1 chunk for the tests that need one."""

    def setUp(self) -> None:
        if not HAVE_LUA:
            self.skipTest("lupa is required to build a real Lua 5.1 chunk")
        self.chunk = _dumped_chunk()


class ContainerTests(_ChunkFixture, unittest.TestCase):
    def test_chunk_is_found_next_to_junk(self) -> None:
        wrapped = b"\x00junk\xff" + self.chunk + b"trailing\x00"
        found = find_lua51_chunk(wrapped)
        self.assertIsNotNone(found)
        self.assertTrue(found.startswith(b"\x1bLua"))

    def test_number_array_codes_are_understood(self) -> None:
        zero_based = chunk_from_values(list(self.chunk))
        one_based = chunk_from_values([byte + 1 for byte in self.chunk])
        self.assertIsNotNone(zero_based)
        self.assertIsNotNone(one_based)
        self.assertEqual(zero_based[:8], self.chunk[:8])
        self.assertEqual(one_based[:8], self.chunk[:8])

    def test_plain_numbers_are_not_mistaken_for_bytecode(self) -> None:
        self.assertIsNone(chunk_from_values([index % 7 for index in range(2000)]))

    def test_lua_literal_and_concat_run(self) -> None:
        self.assertEqual(lua_string_value(r'"\27\76\117\97"'), b"\x1bLua")
        payload = 'local s = "\\27\\76" .. "\\117\\97" .. "\\116\\104" .. "\\101"'
        self.assertEqual(string_runs(payload), [b"\x1bLuathe"])


class BytecodeVmTests(_PayloadAssertions, _ChunkFixture, unittest.TestCase):
    def test_static_array_loader_is_lifted(self) -> None:
        body = ", ".join(str(byte) for byte in self.chunk)
        loader = (
            "-- IronBrew3 style loader\n"
            "local bytes = { " + body + " }\n"
            "local parts = {}\n"
            "for index = 1, #bytes do parts[index] = string.char(bytes[index]) end\n"
            "local chunk = loadstring(table.concat(parts))\n"
            "if chunk then chunk() end\n"
        )
        result = bytecode_vm.devirtualize(loader, family="ironbrew")
        self.assertIsNotNone(result)
        self.assertPseudocode(result["source"])
        self.assertEqual(result["bytecode"][:4], b"\x1bLua")

    def test_runtime_table_is_lifted_when_static_passes_see_nothing(self) -> None:
        # The bytes are hidden from every text pass; only the table the loader
        # built at runtime knows the chunk.
        loader = "local program = build()\nrun(program)\n"
        snapshots = [VmSnapshot(kind="numbers", label="program", values=tuple(self.chunk))]
        result = bytecode_vm.devirtualize(loader, vm_tables=snapshots, family="moonsec")
        self.assertIsNotNone(result)
        self.assertPseudocode(result["source"])
        self.assertIn("program", " ".join(result["notes"]))

    def test_runtime_string_table_is_lifted(self) -> None:
        pieces = tuple(chr(byte) for byte in self.chunk)
        snapshots = [VmSnapshot(kind="strings", label="pool", values=pieces)]
        result = bytecode_vm.devirtualize("local t = build()", vm_tables=snapshots, family="psu")
        self.assertIsNotNone(result)
        self.assertPseudocode(result["source"])

    def test_nothing_to_lift_returns_none(self) -> None:
        self.assertIsNone(bytecode_vm.devirtualize("print('plain')", family="ironbrew"))

    def test_captured_bytecode_is_lifted(self) -> None:
        result = bytecode_vm.devirtualize(
            "local chunk = loadstring(payload)()",
            captured_source=self.chunk.decode("latin-1"),
            family="wearedevs",
        )
        self.assertIsNotNone(result)
        self.assertPseudocode(result["source"])


class NexusTests(_PayloadAssertions, _ChunkFixture, unittest.TestCase):
    def test_payload_split_across_literals_is_reassembled(self) -> None:
        pieces = [
            '"' + "".join(f"\\{byte:03d}" for byte in self.chunk[index : index + 12]) + '"'
            for index in range(0, len(self.chunk), 12)
        ]
        loader = "local s = " + " .. ".join(pieces) + "\nloadstring(s)()\n"
        result = nexus.devirtualize(loader)
        self.assertIsNotNone(result)
        self.assertPseudocode(result["source"])


class TableVmTests(unittest.TestCase):
    def test_opcode_names_come_from_the_dispatcher(self) -> None:
        loader = """
        local handlers = {}
        handlers[3] = function(a, b) return a + b end
        handlers[7] = function(a, b) return a .. b end
        handlers[9] = function(a) return a[1] end
        local program = { 3, 1, 2, 7, 3, 4, 9, 5, 0, 6 }
        while true do
            local opcode = program[pointer]
            if opcode == 3 then handler = handlers[3]
            elseif opcode == 7 then handler = handlers[7]
            elseif opcode == 9 then handler = handlers[9] end
        end
        """
        names = table_vm.infer_opcode_names(loader, [3, 7, 9, 11])
        self.assertEqual(names[3], "arith")
        self.assertEqual(names[7], "concat")
        self.assertIn(names[9], {"index", "field", "numeric"})
        self.assertNotIn(11, names)

    def test_annotated_listing_inlines_pool_constants(self) -> None:
        opcodes = (3, 7, 9, 6)
        values: list[int] = []
        for index in range(80):
            values.extend((opcodes[index % 4], (index * 7) % 97, (index * 13) % 89))
        snapshots = [
            VmSnapshot(kind="numbers", label="program", values=tuple(values)),
            VmSnapshot(kind="strings", label="constants", values=("print", "hello", "world")),
        ]
        listing, names = table_vm.annotated_listing(
            snapshots, source="if opcode == 3 then return a + b end"
        )
        self.assertIn("stride 3", listing)
        self.assertIn('K[2]="hello"', listing)
        self.assertEqual(names.get(3), "arith")

    def test_pool_that_spells_out_source_is_reassembled(self) -> None:
        source = (
            "local parts = { 'family', 'payload', 'recovered' }\n"
            "print(table.concat(parts, ' '))\n"
        )
        pieces = [line for line in source.splitlines() if line]
        snapshots = [
            VmSnapshot(kind="numbers", label="program", values=(1, 2, 3) * 30),
            VmSnapshot(kind="strings", label="constants", values=tuple(pieces)),
        ]
        result = table_vm.devirtualize("local vm = build()", vm_tables=snapshots, family="luraph")
        self.assertIsNotNone(result)
        for piece in PAYLOAD_PIECES:
            self.assertIn(piece, str(result["source"]))

    def test_summary_only_when_nothing_is_recoverable(self) -> None:
        snapshots = [
            VmSnapshot(kind="numbers", label="program", values=(1, 2) * 40),
            VmSnapshot(kind="strings", label="constants", values=("a", "b")),
        ]
        result = table_vm.devirtualize("local vm = build()", vm_tables=snapshots)
        self.assertIsNotNone(result)
        self.assertIsNone(result["source"])
        self.assertTrue(result["notes"])


class PrometheusTests(unittest.TestCase):
    FLAT = """-- protect_prometheus v2
local v = 1
while true do
    if v == 1 then
        local total = 0
        v = 2
    elseif v == 2 then
        print(total)
        break
    end
end
"""

    def test_dispatcher_is_replaced_by_straight_line_code(self) -> None:
        result = prometheus.deflatten(self.FLAT)
        self.assertIsNotNone(result)
        self.assertNotIn("while true do", str(result["source"]))
        self.assertNotIn("v = 2", str(result["source"]))
        self.assertIn("print(total)", str(result["source"]))
        self.assertTrue(prometheus.lua_blocks_balanced(str(result["source"])))

    def test_dispatcher_is_kept_when_the_graph_is_incomplete(self) -> None:
        incomplete = """local v = 1
while true do
    if v == 1 then
        v = 2
    elseif v == 2 then
        v = 3
    elseif v == 3 then
        v = 4
    end
end
"""
        self.assertIsNone(prometheus.deflatten(incomplete))

    def test_dispatcher_is_kept_when_a_state_is_computed(self) -> None:
        dynamic = """local v = 1
while true do
    if v == 1 then
        v = compute()
    elseif v == 2 then
        v = 3
    end
end
"""
        self.assertIsNone(prometheus.deflatten(dynamic))

    def test_dispatcher_is_kept_when_the_loop_can_repeat(self) -> None:
        cycle = """local v = 1
while true do
    if v == 1 then worker() v = 2
    elseif v == 2 then worker2() v = 1 end
end
"""
        self.assertIsNone(prometheus.deflatten(cycle))

    def test_ordinary_loops_are_untouched(self) -> None:
        plain = "local total = 0\nfor i = 1, 10 do total = total + i end\nprint(total)\n"
        self.assertIsNone(prometheus.deflatten(plain))


class RegistryTests(unittest.TestCase):
    def test_every_named_family_has_a_method(self) -> None:
        families = set(available_families())
        for key in (
            "luraph",
            "moonsec",
            "wearedevs",
            "ironbrew",
            "psu",
            "nexus",
            "prometheus",
            "wynfuscate",
            "xen",
            "synapse-protected",
            "hyperion",
            "generic-vm",
        ):
            self.assertIn(key, families)
        self.assertTrue(report_table())

    def test_registry_runs_the_family_method(self) -> None:
        result = devirtualize("prometheus", PrometheusTests.FLAT)
        self.assertIsNotNone(result)
        self.assertTrue(result.recovered)
        self.assertEqual(result.family, "prometheus")
        self.assertIn("flattening", result.method)
        self.assertFalse(result.partial)

    def test_registry_reports_a_vm_surface_without_pretending(self) -> None:
        snapshots = [
            VmSnapshot(kind="numbers", label="program", values=(1, 3, 5, 2) * 40),
            VmSnapshot(kind="strings", label="constants", values=("a", "b", "c")),
        ]
        result = devirtualize("wynfuscate", "local vm = build()", vm_tables=snapshots)
        self.assertIsNotNone(result)
        self.assertFalse(result.recovered)
        self.assertTrue(result.partial)
        self.assertTrue(result.notes)
        self.assertIn("recovered", result.as_dict())

    def test_unknown_family_falls_back_without_raising(self) -> None:
        self.assertIsNone(devirtualize("no-such-family", "print('hi')"))
        self.assertIsNotNone(devirtualize("no-such-family", PrometheusTests.FLAT))


class EngineIntegrationTests(_PayloadAssertions, _ChunkFixture, unittest.TestCase):
    def _engine(self, root: Path) -> RecoveryEngine:
        return RecoveryEngine(
            logger=logging.getLogger("devirt-test"),
            logs_dir=root / "logs",
            use_emulator=False,
            use_native=False,
            allow_network=False,
            max_seconds=10.0,
            max_layers=2,
        )

    def test_engine_routes_a_prometheus_script_through_its_own_method(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self._engine(root).recover(PrometheusTests.FLAT)
        self.assertNotIn("while true do", result.source)
        self.assertIn("print(total)", result.source)
        self.assertTrue(
            any("flattening" in note for note in result.notes),
            result.notes,
        )

    def test_engine_lifts_a_byte_array_loader_for_a_named_family(self) -> None:
        loader = (
            "-- IronBrew3 (ironbrew)\n"
            "local bytes = { "
            + ", ".join(str(byte) for byte in self.chunk)
            + " }\n"
            "local parts = {}\n"
            "for index = 1, #bytes do parts[index] = string.char(bytes[index]) end\n"
            "local chunk = loadstring(table.concat(parts))\n"
            "if chunk then chunk() end\n"
        )
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            result = self._engine(root).recover(loader)
        self.assertPseudocode(result.source)
        self.assertTrue(
            any("bytecode" in note.lower() for note in result.notes),
            result.notes,
        )


if __name__ == "__main__":
    unittest.main()
