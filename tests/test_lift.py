"""Partial lift tests: statement scanning, register renaming, pseudo-source.

The lift turns a payload that is still virtualised (a ``while state do`` binary
search over state numbers) into a readable listing: one section per state, the
registers renamed to ``v1, v2, ...``, and every jump described.  Two sources of
truth are used here:

* ``tests/wrd_flat_mini.lua`` - a hand-written flattened payload (four states, one
  constant jump, one two-way jump, one register target, one loop exit, one helper).
  Small enough that every expectation can be written down by hand.
* the real samples in ``samples/real`` (fetched by ``tools/fetch_samples.py``,
  skipped when missing) - there the expectations are invariants, not values.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import PipelineConfig, SandboxConfig  # noqa: E402
from core.deobfuscate import deobfuscate, deobfuscate_file  # noqa: E402
from core.lift import (  # noqa: E402
    _declared_names,
    _extract_successors,
    _simplify_successors,
    find_dispatcher,
    lift,
    mask_lua,
    match_balanced,
    match_block,
    split_statements,
    tokenize,
)

MINI = Path(__file__).with_name("wrd_flat_mini.lua")
SAMPLE_DIR = ROOT / "samples" / "real"
REAL_SAMPLES = sorted(SAMPLE_DIR.glob("wrd_*.lua"))

# the trace of the mini payload: 120000 -> 480000 -> 900000 -> 1500000 -> 2100000
MINI_TRACE = ["120000", "480000", "900000", "1500000", "2100000"]

#: names a payload must never have renamed (they are globals, not registers)
GLOBAL_NAMES = {
    "setmetatable", "getmetatable", "print", "string", "table", "math", "type",
    "tostring", "tonumber", "pairs", "ipairs", "pcall", "select", "error", "assert",
    "loadstring", "unpack", "rawget", "rawset", "_G", "getfenv", "setfenv", "newproxy",
}


class ScannerTests(unittest.TestCase):
    """The token scanner is the lift's only parser: it has to bracket-balance."""

    def test_match_balanced_handles_nesting_and_strings(self):
        source = 'f({a={1,2}}, g[ "]" ], "x,(y)") + 1'
        tokens = tokenize(source, mask_lua(source))
        open_index = next(i for i, token in enumerate(tokens)
                          if token.kind == "punct" and token.text == "(")
        close = match_balanced(tokens, open_index, len(tokens))
        self.assertEqual(tokens[close - 1].text, ")")  # index past the closer
        self.assertEqual(tokens[close].text, "+")

    def test_match_block_skips_for_header_keywords(self):
        source = "for i = 1, 10 do local x = 1 end after()"
        tokens = tokenize(source, mask_lua(source))
        do_index = next(i for i, token in enumerate(tokens)
                        if token.kind == "keyword" and token.text == "do")
        close = match_block(tokens, do_index + 1, len(tokens))
        self.assertEqual(tokens[close - 1].text, "end")
        self.assertEqual(tokens[close].text, "after")

    def test_split_statements_covers_every_token_without_overlap(self):
        source = MINI.read_text(encoding="utf-8")
        tokens = tokenize(source, mask_lua(source))
        spans = split_statements(tokens, 0, len(tokens))
        self.assertTrue(spans)
        previous_end = 0
        for start, end in spans:
            self.assertLessEqual(previous_end, start)
            self.assertLess(start, end)
            previous_end = end
        self.assertLessEqual(previous_end, len(tokens))

    def test_declared_names_finds_locals_parameters_and_loop_variables(self):
        source = "local a, b = 1, 2\nlocal function c(d) return d end\nfor e = 1, 3 do end\nf = 1\n"
        tokens = tokenize(source, mask_lua(source))
        declared = _declared_names(tokens)
        self.assertEqual(sorted(set(declared)), ["a", "b", "c", "d", "e"])
        self.assertNotIn("f", declared)

    def test_empty_and_plain_sources_do_not_raise(self):
        for source in ("", "print('hi')\n", "local x = 1\n"):
            self.assertIsNone(find_dispatcher(source))
            result = lift(source)
            self.assertFalse(result.ok)
            self.assertTrue(result.reason)


class DispatcherTests(unittest.TestCase):
    def setUp(self):
        self.payload = MINI.read_text(encoding="utf-8")
        self.found = find_dispatcher(self.payload)

    def test_find_dispatcher_locates_state_machine(self):
        self.assertIsNotNone(self.found)
        self.assertEqual(self.found["variable"], "d")
        self.assertGreaterEqual(self.found["pivots"], 3)
        start, end = self.found["token_span"]
        self.assertLess(start, end)
        self.assertIn("while", self.payload[self.found["start"]:self.found["start"] + 8])

    def test_find_dispatcher_rejects_a_plain_while_loop(self):
        self.assertIsNone(find_dispatcher("local i = 0\nwhile i < 10 do i = i + 1 end\n"))


class SuccessorTests(unittest.TestCase):
    """Jumps are described from the block's own statements, not from guesses."""

    def _successors(self, body: str, variable: str = "state"):
        # the harness declares locals before the body: register reads may pick up
        # values from either direction, like they do inside a real state block
        source = f"local state = 1\n{body}\n"
        tokens = tokenize(source, mask_lua(source))
        successors = _simplify_successors(_extract_successors(tokens, 0, len(tokens), variable), variable)
        # `local state = 1` is the harness' own initial state, not a jump
        return [s for s in successors if not (s.kind == "constant" and s.target == "1" and not s.condition)]

    def test_constant_target(self):
        [successor] = self._successors("state = 480000")
        self.assertEqual(successor.kind, "constant")
        self.assertEqual(successor.target, "480000")

    def test_register_holding_a_constant_is_resolved(self):
        [successor] = self._successors("local target = 2100000\nstate = target")
        self.assertEqual(successor.kind, "constant")
        self.assertEqual(successor.target, "2100000")

    def test_register_assigned_before_the_jump_is_resolved(self):
        [successor] = self._successors("local target = nil\ntarget = 4711\nstate = target")
        self.assertEqual(successor.kind, "constant")
        self.assertEqual(successor.target, "4711")

    def test_two_statement_conditional_resolves_both_branches(self):
        [successor] = self._successors("local cond = true\nstate = cond and 900000\nstate = state or 1500000")
        self.assertEqual(successor.kind, "conditional")
        self.assertEqual(successor.target, "900000")
        self.assertEqual(successor.raw, "1500000")
        self.assertEqual(successor.condition, "cond")

    def test_two_statement_conditional_with_unknown_registers(self):
        [successor] = self._successors("local cond = true\nstate = cond and t1\nstate = state or t2")
        self.assertEqual(successor.kind, "register-jump")
        self.assertEqual((successor.target, successor.raw), ("t1", "t2"))
        self.assertEqual(successor.condition, "cond")

    def test_single_statement_conditional(self):
        [successor] = self._successors("local cond = true\nstate = cond and 11 or 22")
        self.assertEqual(successor.kind, "conditional")
        self.assertEqual((successor.target, successor.raw), ("11", "22"))

    def test_table_target_stays_dynamic(self):
        [successor] = self._successors('state = jump["FZwOKLq0r7v3"]')
        self.assertEqual(successor.kind, "dynamic")
        self.assertEqual(successor.target, 'jump["FZwOKLq0r7v3"]')

    def test_exit_is_a_literal(self):
        [successor] = self._successors("state = nil")
        self.assertEqual(successor.kind, "literal")
        self.assertEqual(successor.target, "nil")

    def test_the_pair_is_one_jump_not_two(self):
        successors = self._successors("local cond = true\nstate = cond and 900000\nstate = state or 1500000")
        self.assertEqual(len(successors), 1)


class MiniLiftTests(unittest.TestCase):
    def setUp(self):
        self.payload = MINI.read_text(encoding="utf-8")
        self.result = lift(self.payload, observed=MINI_TRACE)

    def test_lift_reports_ok_with_states_and_helpers(self):
        self.assertTrue(self.result.ok, self.result.reason)
        stats = self.result.stats()
        self.assertEqual(stats["states"], 4)
        self.assertEqual(stats["dynamic_jumps"], 1)
        self.assertEqual(stats["conditional_jumps"], 1)
        self.assertEqual(stats["literal_jumps"], 1)
        self.assertEqual(stats["closures"], 2)  # the wrapper and the helper
        self.assertGreaterEqual(stats["registers"], 5)

    def test_registers_are_renamed_and_globals_are_not(self):
        aliases = self.result.registers
        self.assertEqual(aliases["state"], "d")
        self.assertEqual(sorted(aliases.values()), ["a", "b", "c", "d", "e", "f"])
        # setmetatable is a global: it must never be given an alias
        self.assertFalse(GLOBAL_NAMES & set(aliases.values()))
        for alias in aliases:
            self.assertRegex(alias, r"^(v\d+|state)$")

    def test_pseudocode_is_readable(self):
        text = self.result.pseudocode
        self.assertIn("-- control flow (state -> successor)", text)
        self.assertIn("register legend", text)
        self.assertIn("dispatcher: while state do ... end  -  4 states", text)
        # the renamed registers really are used in the listing
        self.assertIn("v1 = v2(v1)", text)  # b = e(b)
        self.assertNotIn("b = e(b)", text)
        # the appendix keeps globals verbatim and renames only the locals
        self.assertIn("local v4 = setmetatable", text)
        # four state sections, guards speak the new names
        self.assertEqual(text.count("-- ==== state "), 4)
        self.assertIn("-- guard: state < 900000 & state < 480000", text)
        self.assertIn("-- goto S_480000_900000", text)

    def test_no_register_is_left_under_its_original_name(self):
        listing = self.result.pseudocode
        mask = mask_lua(listing)
        names = {token.text for token in tokenize(listing, mask) if token.kind == "name"}
        self.assertFalse(names & set(self.result.registers.values()))

    def test_dynamic_jump_is_resolved_by_the_trace(self):
        stats = self.result.stats()
        self.assertEqual(stats["dynamic_jumps_resolved_by_trace"], 1)
        self.assertIn('(dynamic; trace -> S_from2100000, 1 visit(s))', self.result.pseudocode)

    def test_without_a_trace_the_dynamic_jump_stays_open(self):
        plain = lift(self.payload)
        self.assertTrue(plain.ok, plain.reason)
        self.assertEqual(plain.stats()["dynamic_jumps_resolved_by_trace"], 0)
        self.assertIn('v3["FZwOKLq0r7v3"] (dynamic)', plain.pseudocode)

    def test_lift_is_deterministic(self):
        again = lift(self.payload, observed=MINI_TRACE)
        self.assertEqual(again.pseudocode, self.result.pseudocode)
        self.assertEqual(again.registers, self.result.registers)

    def test_as_dict_is_json_safe(self):
        import json

        payload = self.result.as_dict()
        json.dumps(payload)
        self.assertEqual(payload["stats"]["states"], 4)
        self.assertEqual(payload["dispatcher"]["variable"], "d")


class LiftPipelineTests(unittest.TestCase):
    """The lift is part of the pipeline, not only a library call."""

    def _config(self, workdir: Path, *, lift_enabled: bool = True) -> PipelineConfig:
        return PipelineConfig(
            sandbox=SandboxConfig(timeout=10, sample_runs=1, max_attempts=1, workdir=workdir),
            lift=lift_enabled,
        )

    def test_a_bare_flattened_script_gets_a_listing(self):
        """No constant layer, no payload: the input *is* the state machine."""
        with TemporaryDirectory() as tmp:
            result = deobfuscate(MINI.read_text(encoding="utf-8"),
                                 config=self._config(Path(tmp) / "run"))
            self.assertIsNotNone(result.lift, result.stages and result.stages[-1].detail)
            self.assertTrue(result.lift["ok"], result.lift.get("reason"))
            self.assertEqual(result.lift["stats"]["states"], 4)
            self.assertEqual(result.lift["source"], "input")
            self.assertIsNotNone(result.pseudocode_path)
            self.assertTrue(result.pseudocode_path.is_file())
            written = result.pseudocode_path.read_text(encoding="utf-8")
            self.assertIn("-- control flow (state -> successor)", written)
            self.assertIn("v1 = v2(v1)", written)
            # nothing was deobfuscated, and the result says so instead of pretending
            self.assertFalse(result.success)
            self.assertFalse(result.partial)
            self.assertTrue(result.report_path.is_file())
            self.assertTrue(result.summary_path.is_file())

    def test_wrd_shaped_input_goes_through_the_constant_layer(self):
        """Built from the same payload, the WRD wrapper hides the code in a string."""
        from tools.make_wrd_fixture import build_obfuscated

        payload = MINI.read_text(encoding="utf-8")
        with TemporaryDirectory() as tmp:
            obfuscated = Path(tmp) / "mini_obfuscated.lua"
            obfuscated.write_text(build_obfuscated(payload), encoding="utf-8")
            result = deobfuscate_file(obfuscated, config=self._config(Path(tmp) / "run"))
            self.assertTrue(result.success)
            self.assertTrue(result.partial, "the constant layer is not the original source")
            self.assertNotEqual(result.output, payload)
            self.assertTrue(result.output_path and result.output_path.is_file())
            self.assertTrue(result.stages and result.stages[0].name == "static" and result.stages[0].ok)

    def test_lift_can_be_switched_off(self):
        with TemporaryDirectory() as tmp:
            result = deobfuscate(MINI.read_text(encoding="utf-8"),
                                 config=self._config(Path(tmp) / "run", lift_enabled=False))
            self.assertIsNone(result.lift)
            self.assertIsNone(result.pseudocode)
            self.assertIsNone(result.pseudocode_path)
            self.assertFalse(any(stage.name == "lift" for stage in result.stages))


@unittest.skipUnless(REAL_SAMPLES, f"no real samples in {SAMPLE_DIR} (run tools/fetch_samples.py)")
class RealSampleLiftTests(unittest.TestCase):
    """Invariants over the three real WRD payloads, not hardcoded layouts."""

    @classmethod
    def setUpClass(cls):
        from core.wrd_static import analyze

        cls.sources = {}
        for path in REAL_SAMPLES:
            rewritten = analyze(path.read_text(encoding="utf-8", errors="replace"),
                                inline=True, fold=True)
            cls.sources[path.name] = rewritten.output or ""

    def test_every_sample_has_a_dispatcher(self):
        for name, source in self.sources.items():
            with self.subTest(sample=name):
                self.assertIsNotNone(find_dispatcher(source), name)

    def test_lift_invariants(self):
        for name, source in self.sources.items():
            with self.subTest(sample=name):
                result = lift(source)
                self.assertTrue(result.ok, f"{name}: {result.reason}")
                stats = result.stats()
                self.assertGreaterEqual(stats["states"], 10)
                self.assertGreaterEqual(stats["registers"], 10)
                self.assertGreaterEqual(stats["closures"], 5)
                self.assertFalse(GLOBAL_NAMES & set(result.registers.values()),
                                 f"{name}: a global was renamed")
                self.assertIn("dispatcher: while state do ... end", result.pseudocode)
                self.assertGreater(len(result.pseudocode), 5_000)

    def test_no_register_is_left_under_its_original_name(self):
        for name, source in self.sources.items():
            with self.subTest(sample=name):
                result = lift(source)
                listing = result.pseudocode
                mask = mask_lua(listing)
                names = {token.text for token in tokenize(listing, mask) if token.kind == "name"}
                # a couple of globals may stay (they are not registers), but no
                # register alias may still be spelled with its original letter
                self.assertFalse(names & set(result.registers.values()), name)

    def test_every_jump_is_described(self):
        for name, source in self.sources.items():
            with self.subTest(sample=name):
                result = lift(source)
                known = {"constant", "conditional", "dynamic", "register-jump", "literal", "unknown"}
                for block in result.states:
                    for successor in block.successors:
                        self.assertIn(successor.kind, known)
                        self.assertTrue(successor.render().startswith(("goto", "if", "state")))


if __name__ == "__main__":
    unittest.main()
