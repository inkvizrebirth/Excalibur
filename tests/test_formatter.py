from __future__ import annotations

import unittest

from core.deobfuscator import tokenize
from core.formatter import MAX_FORMAT_SOURCE_CHARS, format_luau


class FormatterTests(unittest.TestCase):
    def test_formats_compact_control_flow_and_preserves_all_tokens(self) -> None:
        source = "local x=1; if x>0 then x=x+1 else x=0 end"

        formatted = format_luau(source)

        self.assertEqual(
            formatted,
            "local x = 1;\n"
            "if x > 0 then\n"
            "    x = x + 1\n"
            "else\n"
            "    x = 0\n"
            "end",
        )
        self.assertEqual(
            [(token.kind, token.text) for token in tokenize(source)],
            [(token.kind, token.text) for token in tokenize(formatted)],
        )

    def test_formats_nested_blocks_and_does_not_indent_after_semicolons(self) -> None:
        source = "function outer(x)local n=x+1;if n>2 then return n else return 0 end end"

        formatted = format_luau(source)

        self.assertIn("\n    local n = x + 1;\n", formatted)
        self.assertIn("\n        return n\n", formatted)
        self.assertTrue(formatted.endswith("\nend"))
        for line in formatted.splitlines():
            if line.strip():
                indentation = len(line) - len(line.lstrip(" "))
                self.assertEqual(indentation % 4, 0)

    def test_preserves_comments_and_string_literals(self) -> None:
        source = '-- header\nlocal msg="a  b\\ntext" -- inline\nreturn msg'
        formatted = format_luau(source)

        self.assertIn('-- header\n', formatted)
        self.assertIn('"a  b\\ntext" -- inline', formatted)
        self.assertEqual(
            format_luau("local x=1 -- trailing spaces  \nreturn x"),
            "local x = 1 -- trailing spaces  \nreturn x",
        )
        self.assertEqual(
            [(token.kind, token.text) for token in tokenize(source)],
            [(token.kind, token.text) for token in tokenize(formatted)],
        )

    def test_leaves_interpolation_if_expressions_and_typed_returns_untouched(self) -> None:
        samples = (
            'local text = `value {x}`',
            "local value=if ready then 1 else 2",
            "local function f(x: number): number return x end",
        )
        for source in samples:
            with self.subTest(source=source):
                self.assertEqual(format_luau(source), source)

    def test_skips_sources_above_the_tokenization_limit(self) -> None:
        source = "x" * (MAX_FORMAT_SOURCE_CHARS + 1)
        self.assertIs(format_luau(source), source)


if __name__ == "__main__":
    unittest.main()
