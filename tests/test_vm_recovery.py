"""Unit tests for the VM-table dumper and the surface analysis."""

from __future__ import annotations

import unittest

from core.vm_dump import (
    VmSnapshot,
    constant_pool,
    instruction_score,
    instruction_table,
    looks_like_vm_payload,
    snapshot_from_bridge,
    string_score,
)
from core.vm_recover import analyse_vm, render_analysis, summary_line


def _stream(instructions: int, *, operands: int = 2) -> tuple[int, ...]:
    values: list[int] = []
    for index in range(instructions):
        values.append((index % 3) + 1)
        for operand in range(operands):
            values.append((index * (7 + operand * 3)) % 5_000)
    return tuple(values)


class SnapshotBridgeTests(unittest.TestCase):
    def test_numbers_are_parsed(self) -> None:
        snapshot = snapshot_from_bridge("numbers", "t:program", "1,2,3,4", 4, 2)
        assert snapshot is not None
        self.assertTrue(snapshot.numeric)
        self.assertEqual(snapshot.as_int_values(), (1, 2, 3, 4))
        self.assertEqual(snapshot.width, 2)

    def test_strings_are_parsed(self) -> None:
        snapshot = snapshot_from_bridge("strings", "t:pool", "print\x01value", 2)
        assert snapshot is not None
        self.assertFalse(snapshot.numeric)
        self.assertEqual(snapshot.values, ("print", "value"))

    def test_junk_is_rejected(self) -> None:
        self.assertIsNone(snapshot_from_bridge("numbers", "t", b"\x00\x01"))
        self.assertIsNone(snapshot_from_bridge("tables", "t", "1,2"))
        self.assertIsNone(snapshot_from_bridge("strings", "t", ""))


class ScoringTests(unittest.TestCase):
    def test_instruction_stream_scores_above_random_data(self) -> None:
        stream = VmSnapshot(kind="numbers", label="t:program", values=_stream(200), width=3)
        random_data = VmSnapshot(
            kind="numbers",
            label="t:data",
            values=tuple((index * 2654435761) % 2**31 for index in range(600)),
            width=1,
        )
        self.assertGreater(instruction_score(stream), instruction_score(random_data))

    def test_protez_tables_are_penalised(self) -> None:
        ours = VmSnapshot(kind="numbers", label="<python>:__protez_services", values=_stream(200), width=3)
        theirs = VmSnapshot(kind="numbers", label="<python>:program", values=_stream(200), width=3)
        self.assertLess(instruction_score(ours), instruction_score(theirs))

    def test_constant_pool_prefers_the_earlier_string_table(self) -> None:
        pool = VmSnapshot(kind="strings", label="t:constants", values=tuple(f"word{index}" for index in range(24)))
        output = VmSnapshot(kind="strings", label="t:output", values=tuple(f"line{index}" for index in range(120)))
        self.assertGreater(string_score(pool), 0)
        # The pool is built before the VM runs, so it is seen first; that beats
        # the assembled output even though the output table is much larger.
        self.assertEqual(constant_pool((pool, output)), pool)


class AnalysisTests(unittest.TestCase):
    def test_stride_and_opcodes_are_detected(self) -> None:
        snapshot = VmSnapshot(kind="numbers", label="t:program", values=_stream(120), width=1)
        analysis = analyse_vm([snapshot])
        assert analysis is not None
        self.assertEqual(analysis.width, 3)
        self.assertEqual(analysis.operands_per_instruction, 2)
        self.assertEqual(analysis.instruction_count, 120)
        self.assertEqual(analysis.distinct_opcodes, 3)
        self.assertGreater(analysis.confidence, 0.5)
        self.assertIn("disassembly", render_analysis(analysis))
        self.assertIn("custom VM surface", summary_line(analysis))

    def test_uniform_data_is_flagged_as_a_guess(self) -> None:
        snapshot = VmSnapshot(
            kind="numbers", label="t:blob", values=tuple(index % 7 for index in range(400)), width=1
        )
        analysis = analyse_vm([snapshot])
        assert analysis is not None
        self.assertTrue(any("guess" in note for note in analysis.notes), analysis.notes)

    def test_short_tables_are_ignored(self) -> None:
        self.assertIsNone(analyse_vm([VmSnapshot(kind="numbers", label="t:tiny", values=(1, 2, 3))]))
        self.assertIsNone(analyse_vm([]))

    def test_uniform_counter_data_is_not_a_strong_stream(self) -> None:
        flat = VmSnapshot(kind="numbers", label="t:flat", values=tuple(range(400)), width=1)
        analysis = analyse_vm([flat])
        if analysis is not None:
            self.assertTrue(any("guess" in note for note in analysis.notes), analysis.notes)

    def test_render_lists_constants(self) -> None:
        stream = VmSnapshot(kind="numbers", label="t:program", values=_stream(80), width=3)
        pool = VmSnapshot(kind="strings", label="t:constants", values=("print", "hello", "world"))
        analysis = analyse_vm([stream, pool])
        assert analysis is not None
        text = render_analysis(analysis)
        self.assertIn("t:constants", text)
        self.assertIn("'print'", text)


class PayloadProbeTests(unittest.TestCase):
    def test_vm_shaped_source_is_recognised(self) -> None:
        source = """
        local program = { 1, 2, 3, 4 }
        local function dispatch(opcode) return opcode end
        while true do
          local value = program[1]
          local byte = string.byte('x')
          dispatch(value + byte)
        end
        """ * 20
        self.assertTrue(looks_like_vm_payload(source))

    def test_plain_script_is_not_a_vm(self) -> None:
        self.assertFalse(looks_like_vm_payload("print('hello')\nlocal x = 1\n"))
        self.assertFalse(looks_like_vm_payload(""))


if __name__ == "__main__":
    unittest.main()
