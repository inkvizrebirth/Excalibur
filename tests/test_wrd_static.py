"""Unit tests for the static constant layer (:mod:`core.wrd_static`).

The constant folder is the part of the pipeline with the subtlest failure modes:
folding an expression across a binding boundary silently changes program
behaviour (``H and-459339+1691705`` is ``H and (...+...)``, not ``(H and -459339)+...``),
and gluing tokens together produces code that does not even lex
(``for i=1,3 do`` -> ``1do``).  Every case below is a regression for a bug that
was actually observed while reverse-engineering real WRD v1.0.0 files.
"""

from __future__ import annotations

import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.wrd_static import (  # noqa: E402
    _fold_constants,
    analyze,
    decode_custom_base64,
    escape_lua_string,
    evaluate_constant,
    inline_resolver_calls,
    unescape_lua_string,
)

#: The alphabet and offset used by the generated fixture (tools/make_wrd_fixture.py).
ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
OFFSET = 1000


def _load_generator():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "make_wrd_fixture", ROOT / "tools" / "make_wrd_fixture.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)  # type: ignore[union-attr]
    return module


_generator = _load_generator()
TINY_DECODED = ["hello ", "world", "!"]

TINY_WRD_SOURCE = (
    "local u={" + ",".join(
        '"' + _generator.escape_bytes(_generator.encode_entry(piece.encode(), ALPHABET).encode("latin-1")) + '"'
        for piece in TINY_DECODED
    ) + "}\n"
    "local a={" + ",".join(f'["{char}"]={index}' for index, char in enumerate(ALPHABET)) + "}\n"
    "local j={}\n"
    "local function h(x)return j[x-1000]end\n"
    "print(h(1001))\n"
)


#: (source, expected after folding).  ``None`` as the expected value means the
#: expression must stay *untouched* - folding it would change semantics.
FOLD_CASES = [
    # --- must fold -------------------------------------------------------
    ("local a=1+2", "local a=3"),
    ("x=2+3*4", "x=14"),
    ("t[1+2]", "t[3]"),
    ("f(1+2)", "f(3)"),
    ("a*(1+2)", "a*3"),
    ("10%3-1", "0"),
    ("return -1+2", "return 1"),
    ("H and-459339+1691705", "H and 1232366"),
    ("for u=-9378+9379,#z,-673266-(-673267)do", "for u=1,#z,1 do"),
    ("while i<8220092-37153 do", "while i<8182939 do"),
    ("i=o+G*(-581593+581657)^((653875+-653872)-m)", "i=o+G*64^(3-m)"),
    ("local u=q(U/(619307+-553371))", "local u=q(U/65936)"),
    ("j=6331556+-5703242", "j=628314"),
    # --- must NOT fold ---------------------------------------------------
    ("x-1+2", None),
    ("f(2)+3", None),
    ("a*1+2", None),
    ("y=a*-1+2", None),
    ("2^3^x", None),
    ("1e5+2", None),
    ("0x10+1", None),
    ("local do_ = 1 + 2", "local do_ = 3"),   # keyword prefixes must not confuse us
]


class FoldConstants(unittest.TestCase):
    def test_fold_cases(self) -> None:
        for source, expected in FOLD_CASES:
            with self.subTest(source=source):
                _count, text = _fold_constants(source)
                if expected is None:
                    self.assertEqual(text, source)
                else:
                    self.assertEqual(text, expected)

    def test_folding_is_always_compilable_and_stable(self) -> None:
        """Folding twice must be a no-op (idempotence) and keep the text valid."""
        for source, _expected in FOLD_CASES:
            with self.subTest(source=source):
                _count, once = _fold_constants(source)
                _count2, twice = _fold_constants(once)
                self.assertEqual(once, twice)

    def test_multi_pass_folds_full_chain(self) -> None:
        _count, text = _fold_constants("local x = (1+2)+(3*4)")
        self.assertEqual(text, "local x = 15")


class Helpers(unittest.TestCase):
    def test_unescape_and_escape_round_trip(self) -> None:
        for value in ("plain", "with\\000nul", "\x01\x02\xff binary", 'quote" and \\slash'):
            escaped = escape_lua_string(value)
            self.assertTrue(all(ord(c) < 127 for c in escaped), escaped)
            self.assertEqual(unescape_lua_string(escaped), value)

    def test_escape_uses_ascii_only(self) -> None:
        escaped = escape_lua_string("caf\u00e9 \u0402\u0403")
        self.assertTrue(all(ord(c) < 127 for c in escaped))
        self.assertNotIn("\u00e9", escaped)

    def test_evaluate_constant_lua_semantics(self) -> None:
        cases = {
            "1+2*3": 7,
            "10%3": 1,
            "-10%3": 2,          # Lua 5.1 floor modulo, not C fmod
            "2^10": 1024,
            "0x10": 16,
            ".5+0.25": 0.75,
        }
        for expression, expected in cases.items():
            with self.subTest(expression=expression):
                self.assertEqual(evaluate_constant(expression), expected)
        for expression in ("os.time()", "print(1)", "a+1", "1..2"):
            with self.subTest(expression=expression):
                self.assertIsNone(evaluate_constant(expression))


class CustomBase64(unittest.TestCase):
    #: the alphabet WRD uses (a rotation of the RFC 4648 one)
    ALPHABET = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz+/"
    #: the RFC 4648 alphabet, for vectors that must match standard base64
    STANDARD = "ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/"

    def setUp(self) -> None:
        self.table = {char: index for index, char in enumerate(self.ALPHABET)}
        self.standard = {char: index for index, char in enumerate(self.STANDARD)}

    def test_known_vectors(self) -> None:
        self.assertEqual(decode_custom_base64("", self.standard), b"")
        self.assertEqual(decode_custom_base64("MA==", self.standard), b"0")
        self.assertEqual(decode_custom_base64("MDE=", self.standard), b"01")
        self.assertEqual(decode_custom_base64("MDEy", self.standard), b"012")

    def test_round_trip_against_generator_encoding(self) -> None:
        import importlib.util

        spec = importlib.util.spec_from_file_location(
            "make_wrd_fixture", ROOT / "tools" / "make_wrd_fixture.py")
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)  # type: ignore[union-attr]
        for data in (b"x", b"xy", b"xyz", bytes(range(64)), b"robot script" * 7):
            encoded = module.encode_entry(data, self.ALPHABET)
            self.assertEqual(decode_custom_base64(encoded, self.table), data)


class ResolverInlining(unittest.TestCase):
    """The inliner works on the *text* of a resolver call, offset included."""

    def _source(self, body: str) -> str:
        return TINY_WRD_SOURCE.replace("print(h(1001))", body)

    def test_constant_call_is_replaced(self) -> None:
        source = self._source("print(h(1001),h(1002),h(1003))")
        from core.wrd_detect import mask_lua

        resolver = {"name": "h", "param": "x", "pool": "j", "offset": OFFSET, "op": "-"}
        count, text = inline_resolver_calls(source, mask_lua(source), resolver, TINY_DECODED)
        self.assertEqual(count, 3)
        for value in TINY_DECODED:
            self.assertIn(escape_lua_string(value), text)

    def test_out_of_range_index_is_left_alone(self) -> None:
        source = self._source("print(h(999999))")
        from core.wrd_detect import mask_lua

        resolver = {"name": "h", "param": "x", "pool": "j", "offset": OFFSET, "op": "-"}
        count, text = inline_resolver_calls(source, mask_lua(source), resolver, TINY_DECODED)
        self.assertEqual(count, 0)
        self.assertEqual(text, source)


class AnalyzeSmoke(unittest.TestCase):
    def test_reports_a_reason_instead_of_raising(self) -> None:
        for broken in ("", "print('hi')", 'local u={"\\065\\066\\067\\068"}'):
            with self.subTest(broken=broken[:20]):
                result = analyze(broken)
                self.assertFalse(result.ok)
                self.assertTrue(result.reason)

    def test_full_analysis_of_a_minimal_build(self) -> None:
        result = analyze(TINY_WRD_SOURCE)
        self.assertTrue(result.ok, result.reason)
        self.assertEqual(len(result.decoded), len(TINY_DECODED))
        self.assertEqual(result.resolver["name"], "h")
        self.assertGreater(result.inlined_calls, 0)
        self.assertIsNotNone(result.output)

    def test_disabled_rewrite_still_decodes(self) -> None:
        result = analyze(TINY_WRD_SOURCE, inline=False, fold=False)
        self.assertTrue(result.ok, result.reason)
        self.assertIsNone(result.output)
        self.assertEqual(result.inlined_calls, 0)


if __name__ == "__main__":
    unittest.main(verbosity=2)
