"""Luau lowering: numerals, floor division, if-expressions, interpolation.

Every obfuscator in the Luraph family emits Luau, and the portable backend is
Lua 5.1: without these passes a wrapper that an executor would run happily dies
on the first line with a syntax error.  The tests compile the lowered text with
the same Lua 5.1 the backend uses, so "it looks right" is never enough.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

try:
    from lupa import lua51

    HAVE_LUA = True
except Exception:  # noqa: BLE001
    HAVE_LUA = False

from core.deobfuscator import tokenize  # noqa: E402
from core.devirt.luau_normalize import (  # noqa: E402
    UnsupportedLuauSyntax,
    luau_only_features,
    normalize_luau,
)


class _Compiles(unittest.TestCase):
    """Compile the lowered source the way the backend does."""

    def setUp(self) -> None:
        if not HAVE_LUA:
            self.skipTest("lupa is required to compile the lowered source")
        self.runtime = lua51.LuaRuntime(unpack_returned_tuples=True, encoding="latin-1")

    def assertCompiles(self, source: str) -> None:  # noqa: N802 - unittest style
        outcome = self.runtime.eval("loadstring")(source)
        if isinstance(outcome, tuple):
            function, error = (outcome + (None, None))[:2]
        else:
            function, error = outcome, None
        self.assertIsNotNone(function, f"lowered source does not compile: {error}")

    def lower(self, source: str) -> str:
        return normalize_luau(source).source


class NumeralTests(_Compiles):
    def test_separators_are_removed_and_hex_stays_exact(self) -> None:
        lowered = self.lower("local a = 0Xf5__e\nlocal b = 1_000\nlocal c = 0b1010")
        self.assertCompiles(lowered)
        self.assertNotIn("_", lowered.split("local a = ")[1].split("\n")[0])
        self.assertIn("0Xf5e", lowered)

    def test_features_are_reported(self) -> None:
        self.assertIn("numeric_separators", luau_only_features("local a = 1_000"))


class FloorDivisionTests(_Compiles):
    def test_operator_becomes_math_floor(self) -> None:
        lowered = self.lower("local q = a // b")
        self.assertCompiles(lowered)
        self.assertIn("math.floor", lowered)

    def test_chain_nests_left_to_right(self) -> None:
        lowered = self.lower("local q = a // b // c")
        self.assertCompiles(lowered)
        self.assertEqual(lowered.count("math.floor"), 2)

    def test_index_operands_keep_their_spans(self) -> None:
        lowered = self.lower("N[j[J]] = N[b[J]] // x[J];")
        self.assertCompiles(lowered)
        self.assertIn("math.floor", lowered)


class IfExpressionTests(_Compiles):
    def test_simple_expression_becomes_a_closure(self) -> None:
        lowered = self.lower("local z = if c then a else b")
        self.assertCompiles(lowered)
        self.assertIn("return a", lowered)
        self.assertIn("return b", lowered)

    def test_elseif_chain_keeps_every_branch(self) -> None:
        lowered = self.lower("local z = if c then a elseif d then b else e;")
        self.assertCompiles(lowered)
        self.assertIn("elseif d then return b", lowered)

    def test_nested_expression_in_a_branch(self) -> None:
        lowered = self.lower("local r = if a then if b then 1 else 2 else 3;")
        self.assertCompiles(lowered)
        self.assertEqual(lowered.count("(function()"), 2)

    def test_statement_ifs_are_left_alone(self) -> None:
        source = "if x then if y then z = 1 else z = 2 end end"
        self.assertEqual(self.lower(source), source)

    def test_false_and_nil_branches_survive(self) -> None:
        # ``(c and a) or b`` would lose these, which is why a closure is used.
        lowered = self.lower("local z = if c then false else nil")
        self.assertCompiles(lowered)
        runtime = lua51.LuaRuntime(unpack_returned_tuples=True, encoding="latin-1")
        expression = lowered.split("=", 1)[1].strip().rstrip(";")
        value = runtime.eval(f"(function() local z = {expression} return z end)()")
        self.assertIsNone(value)


class InterpolatedStringTests(_Compiles):
    def test_interpolation_becomes_concatenation(self) -> None:
        lowered = self.lower('local text = `hp: {health}/100`')
        self.assertCompiles(lowered)
        self.assertIn("tostring(health)", lowered)
        self.assertIn("hp: ", lowered)

    def test_tokenizer_keeps_the_whole_literal_as_one_token(self) -> None:
        tokens = tokenize("local t = `a {b} c`")
        self.assertEqual([token.kind for token in tokens].count("string"), 1)


class ContinueTests(_Compiles):
    def test_continue_inside_a_while_loop_is_lowered(self) -> None:
        lowered = self.lower("while a do if b then continue end work() end")
        self.assertCompiles(lowered)
        self.assertNotIn("continue", lowered)

    def test_if_expression_does_not_break_block_tracking(self) -> None:
        # The if-expression has no ``end``; counting it as a block used to make
        # the continue pass report "unterminated 'if' block" on valid Luau.
        lowered = self.lower(
            "while true do\n"
            "  local z = if j[i[z]] then D[z] else t[z];\n"
            "  if z then continue end\n"
            "end"
        )
        self.assertCompiles(lowered)


class UnsupportedSyntaxTests(unittest.TestCase):
    def test_if_expression_without_else_is_reported(self) -> None:
        with self.assertRaises(UnsupportedLuauSyntax):
            normalize_luau("local z = if c then a")


if __name__ == "__main__":
    unittest.main()
