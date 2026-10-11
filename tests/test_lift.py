"""Tests for the partial lift (flattened state machine -> readable pseudo source).

Two layers are covered:

* ``core.lift`` itself, on a miniature state machine written by hand, so the
  expectations do not depend on a third party sample;
* the whole pipeline on a WRD-encoded file whose payload *is* that state
  machine (the encoding reuses :func:`tools.make_wrd_fixture.build_obfuscated`),
  which proves the lift runs end to end and writes ``pseudocode.lua``.
"""

from __future__ import annotations

import dataclasses
import sys
import tempfile
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import PipelineConfig, SandboxConfig  # noqa: E402
from core.deobfuscate import deobfuscate, deobfuscate_file  # noqa: E402
from core.lift import (  # noqa: E402
    find_dispatcher,
    lift,
    match_balanced,
    match_block,
    mask_lua,
    split_statements,
    tokenize,
)
from tools.make_wrd_fixture import build_obfuscated  # noqa: E402

#: A miniature *flattened* payload: a ``while <state>`` dispatch loop over four
#: states with single letter registers, a helper closure, a constant jump, a
#: conditional jump and a jump whose target is read out of a table register.
FLATTENED = """-- flattened payload (state machine with single letter registers)
local a={}
local b=0
local c=setmetatable
local d=120000
local function e(f)
  return f+1
end
while d do
  if d<900000 then
    if d<480000 then
      b=e(b)
      d=480000
    else
      d=d and 900000 or 1500000
    end
  else
    if d<2100000 then
      a["FZwOKLq0r7v3"]=2100000
      d=a["FZwOKLq0r7v3"]
    else
      d=nil
    end
  end
end
return b
"""

#: State values the payload actually visits (used as "observed" trace values).
OBSERVED = [120000, 480000, 900000, 2100000]

SAMPLE_DIR = ROOT / "samples" / "real"
REAL_SAMPLES = sorted(SAMPLE_DIR.glob("wrd_*.lua"))


def tokens(source: str):
    return tokenize(source, mask_lua(source))


class DispatcherDetection(unittest.TestCase):
    def test_find_dispatcher_locates_the_state_machine(self):
        found = find_dispatcher(FLATTENED)
        self.assertIsNotNone(found)
        self.assertEqual(found["variable"], "d")
        self.assertGreaterEqual(found["pivots"], 3)
        start, end = found["body_char_span"]
        self.assertLess(start, end)
        self.assertLessEqual(end, len(FLATTENED))
        # the reported start is the `while` keyword of the dispatch loop
        self.assertTrue(FLATTENED[found["start"]:].startswith("while d do"))

    def test_plain_code_has_no_dispatcher(self):
        plain = "local x = 1\nprint(x)\nreturn x\n"
        self.assertIsNone(find_dispatcher(plain))

    def test_dispatcher_is_stable(self):
        self.assertEqual(find_dispatcher(FLATTENED), find_dispatcher(FLATTENED))


class StatementScanner(unittest.TestCase):
    """Invariants of the hand written scanner (the luaparser oracle lives in the
    development notes; these checks keep the same guarantees in CI)."""

    def test_match_balanced_handles_nested_and_string_brackets(self):
        source = 'local t={a={1,2},b="}{"}\n'
        toks = tokens(source)
        open_index = next(i for i, t in enumerate(toks) if t.text == "{")
        after = match_balanced(toks, open_index, len(toks))
        # `after` is one past the closer, which is the table's `}`, not the one
        # hidden inside the string literal
        self.assertEqual(toks[after - 1].text, "}")
        self.assertEqual(toks[after - 1].end, source.index("\n"))

    def test_match_block_skips_loop_headers(self):
        source = "for i=1,10 do x=x+1 end\ny=2\n"
        toks = tokens(source)
        body = next(i for i, t in enumerate(toks) if t.text == "do") + 1
        after = match_block(toks, body, len(toks))
        # `end` closes the loop, `after` is the token past it
        self.assertEqual(toks[after - 1].text, "end")
        self.assertEqual(toks[after].text, "y")

    def test_split_statements_covers_the_dispatcher_body(self):
        toks = tokens(FLATTENED)
        start, end = find_dispatcher(FLATTENED)["token_span"]
        spans = split_statements(toks, start, end)
        # the whole body is one `if ... end` statement, nothing dropped
        self.assertEqual(len(spans), 1)
        self.assertEqual(spans[0][0], start)
        self.assertEqual(spans[0][1], end)
        self.assertEqual(toks[start].text, "if")
        self.assertEqual(toks[end - 1].text, "end")

    def test_split_statements_separates_wrd_style_assignments(self):
        # WRD emits statements without separators: `x="a"t=nil`
        source = 'x="a"t=nil z=x'
        toks = tokens(source)
        spans = split_statements(toks, 0, len(toks))
        pieces = [source[toks[a].start:toks[b - 1].end] for a, b in spans]
        self.assertEqual(pieces, ['x="a"', "t=nil", "z=x"])


class Lift(unittest.TestCase):
    def setUp(self):
        self.result = lift(FLATTENED, observed=OBSERVED)

    def test_lift_succeeds_and_finds_the_states(self):
        self.assertTrue(self.result.ok, self.result.reason)
        self.assertEqual(len(self.result.states), 4)
        stats = self.result.stats()
        self.assertEqual(stats["dynamic_jumps"], 1)
        self.assertEqual(stats["dynamic_jumps_resolved_by_trace"], 1)
        self.assertEqual(stats["literal_jumps"], 1)
        self.assertEqual(stats["conditional_jumps"], 1)
        self.assertGreaterEqual(stats["registers"], 5)

    def test_registers_are_renamed_to_vN(self):
        legend = self.result.registers
        self.assertEqual(legend.get("state"), "d")
        renamed = set(legend)
        self.assertIn("v1", renamed)
        # every single letter register got a vN name
        self.assertNotIn("a", renamed)
        self.assertNotIn("b", renamed)
        self.assertNotIn("d", renamed)
        for vN, original in legend.items():
            self.assertNotEqual(vN, original)

    def test_pseudocode_is_readable(self):
        text = self.result.pseudocode
        self.assertIn("-- v1", text)                 # legend
        self.assertIn("state=v3[", text)             # dynamic jump through a register
        self.assertIn("(dynamic; trace:", text)      # resolved by the observed values
        self.assertIn("state = nil", text)           # literal successor rendered
        self.assertIn("dispatcher: while state do ... end", text)
        self.assertNotIn("local d=120000", text)     # original letter names are gone

    def test_without_a_trace_the_dynamic_jump_stays_unresolved(self):
        plain = lift(FLATTENED)
        stats = plain.stats()
        self.assertTrue(plain.ok)
        self.assertEqual(stats["dynamic_jumps"], 1)
        self.assertEqual(stats["dynamic_jumps_resolved_by_trace"], 0)
        self.assertNotIn("(dynamic; trace:", plain.pseudocode)
        self.assertIn("(dynamic: target read from a register)", plain.pseudocode)

    def test_lift_is_deterministic(self):
        again = lift(FLATTENED, observed=OBSERVED)
        self.assertEqual(self.result.pseudocode, again.pseudocode)
        self.assertEqual(self.result.as_dict(), again.as_dict())

    def test_max_states_caps_the_report(self):
        payload = self.result.as_dict(max_states=2)
        self.assertEqual(len(payload["states"]), 2)


class FlattenedPipeline(unittest.TestCase):
    """The encoded fixture is static-decoded byte for byte; the lift follows."""

    def setUp(self):
        self.source = build_obfuscated(FLATTENED)
        self.config = PipelineConfig(
            sandbox=SandboxConfig(timeout=10, sample_runs=1, max_attempts=1),
            trace_on_failure=False,
        )

    def test_static_layer_returns_the_flattened_payload(self):
        started = time.time()
        result = deobfuscate(self.source, config=self.config, source_name="mini.lua")
        self.assertLess(time.time() - started, 60.0, "the pipeline must not hang")
        static_stage = next((s for s in result.stages if s.name == "static"), None)
        self.assertIsNotNone(static_stage)
        self.assertTrue(static_stage.ok, static_stage.detail)
        self.assertEqual(result.output.strip(), FLATTENED.strip())
        self.assertEqual(result.method, "dynamic")
        self.assertFalse(result.partial, "the flattened payload itself is fully recovered")

    def test_lift_stage_writes_pseudocode(self):
        with tempfile.TemporaryDirectory() as tmp:
            result = deobfuscate(
                self.source,
                config=self.config,
                source_name="mini.lua",
                workdir=Path(tmp),
            )
            stage = next((s for s in result.stages if s.name == "lift"), None)
            self.assertIsNotNone(stage, [s.name for s in result.stages])
            self.assertTrue(stage.ok, stage.detail)
            self.assertTrue(result.pseudocode)
            self.assertIn("state=nil", result.pseudocode.replace(" ", ""))
            self.assertEqual(result.lift.get("source"), "payload")
            self.assertIsNotNone(result.pseudocode_path)
            self.assertTrue(result.pseudocode_path.exists())
            self.assertIn("Excalibur partial lift", result.pseudocode_path.read_text(encoding="utf-8"))

    def test_lift_can_be_disabled(self):
        config = dataclasses.replace(self.config, lift=False)
        result = deobfuscate(self.source, config=config, source_name="mini.lua")
        self.assertFalse(any(s.name == "lift" for s in result.stages))
        self.assertIsNone(result.pseudocode)
        self.assertIsNone(result.pseudocode_path)


@unittest.skipUnless(REAL_SAMPLES, "real-world samples are not present (tools/fetch_samples.py)")
class RealSamples(unittest.TestCase):
    def test_lift_on_a_real_sample(self):
        path = REAL_SAMPLES[0]
        config = PipelineConfig(
            sandbox=SandboxConfig(timeout=20, sample_runs=1, max_attempts=2),
        )
        started = time.time()
        result = deobfuscate_file(path, config=config)
        self.assertLess(time.time() - started, 180.0)
        self.assertTrue(result.partial, "a virtualised sample stays partial by design")
        self.assertIsNotNone(result.lift)
        info = result.lift
        self.assertGreater(info["stats"]["states"], 20)
        self.assertGreater(len(result.pseudocode or ""), 5_000)
        self.assertIn("-- v1", result.pseudocode)


if __name__ == "__main__":
    unittest.main()
