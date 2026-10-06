"""Tests for the display-independent parts of the pixel interface."""

from __future__ import annotations

import unittest
from pathlib import Path

from gui import highlight
from gui.pixelfont import (
    GLYPH_HEIGHT,
    GLYPH_WIDTH,
    glyph,
    iter_characters,
    text_rows,
    text_size,
)


class PixelFontTests(unittest.TestCase):
    def test_every_glyph_is_well_formed(self) -> None:
        for character in iter_characters():
            with self.subTest(character=character):
                rows = glyph(character)
                self.assertEqual(len(rows), GLYPH_HEIGHT)
                for row in rows:
                    self.assertEqual(len(row), GLYPH_WIDTH)
                    self.assertTrue(set(row) <= {"#", "."})

    def test_unknown_characters_render_a_placeholder(self) -> None:
        self.assertEqual(glyph("\u2603"), glyph("?"))

    def test_lowercase_folds_to_uppercase(self) -> None:
        self.assertEqual(glyph("a"), glyph("A"))

    def test_text_size_scales(self) -> None:
        width, height = text_size("AB")
        self.assertEqual(height, GLYPH_HEIGHT)
        self.assertEqual(width, 2 * GLYPH_WIDTH + 1)

    def test_rows_are_rectangular(self) -> None:
        rows = text_rows("PROTEZ 1.0")
        widths = {len(row) for row in rows}
        self.assertEqual(len(widths), 1)


class HighlightTests(unittest.TestCase):
    def test_keywords_strings_numbers_and_comments(self) -> None:
        source = '-- note\nlocal greeting = "hi"\nlocal total = 2.5\nif total then end\n'
        lines = highlight.highlight_lines(source)
        tags = [span.tag for line in lines for span in line]
        self.assertIn(highlight.TAG_COMMENT, tags)
        self.assertIn(highlight.TAG_KEYWORD, tags)
        self.assertIn(highlight.TAG_STRING, tags)
        self.assertIn(highlight.TAG_NUMBER, tags)

    def test_executor_globals_are_tagged(self) -> None:
        source = "if syn and syn.protect_gui then print(identifyexecutor()) end"
        tags = {
            span.tag
            for line in highlight.highlight_lines(source)
            for span in line
        }
        self.assertIn(highlight.TAG_EXECUTOR, tags)

    def test_long_comments_and_strings_span_lines(self) -> None:
        source = "--[[ multi\nline comment ]]\nlocal s = [[long\nstring]]\nreturn s\n"
        lines = highlight.highlight_lines(source)
        self.assertEqual(lines[0][0].tag, highlight.TAG_COMMENT)
        self.assertEqual(lines[1][0].tag, highlight.TAG_COMMENT)
        self.assertEqual(lines[2][-1].tag, highlight.TAG_STRING)
        self.assertEqual(lines[3][0].tag, highlight.TAG_STRING)

    def test_spans_never_overlap_or_leave_the_line(self) -> None:
        source = 'local function f(a, b)\n  return a .. "x" -- tail\nend\n'
        for line, spans in zip(source.split("\n"), highlight.highlight_lines(source)):
            previous = 0
            for span in spans:
                with self.subTest(line=line, span=span):
                    self.assertLess(span.start, span.end)
                    self.assertLessEqual(span.end, len(line))
                    self.assertGreaterEqual(span.start, previous)
                previous = span.end

    def test_unterminated_string_does_not_crash(self) -> None:
        spans = highlight.highlight_lines('local value = "unterminated')
        self.assertTrue(any(span.tag == highlight.TAG_STRING for span in spans[0]))

    def test_summary_counts_tokens(self) -> None:
        counts = highlight.summarize("local a = 1 -- c\n")
        self.assertEqual(counts.get(highlight.TAG_KEYWORD), 1)
        self.assertEqual(counts.get(highlight.TAG_COMMENT), 1)


class PixelLabelCoverageTests(unittest.TestCase):
    """Every string drawn by the bitmap font must have a real glyph."""

    _PIXEL_WIDGETS = (
        "PixelLabel",
        "PixelButton",
        "PixelToggle",
        "PixelProgress",
        "PixelDropdown",
        "PixelEntry",
        "PixelTextArea",
        "PixelPanel",
    )

    def _label_strings(self) -> list[tuple[str, str]]:
        import ast

        found: list[tuple[str, str]] = []
        gui = Path(__file__).resolve().parent.parent / "gui"
        for path in sorted(gui.glob("*.py")):
            tree = ast.parse(path.read_text(encoding="utf-8"))
            for node in ast.walk(tree):
                if not isinstance(node, ast.Call):
                    continue
                name = getattr(node.func, "id", None) or getattr(node.func, "attr", None)
                if name not in self._PIXEL_WIDGETS:
                    continue
                for argument in node.args[1:]:
                    if isinstance(argument, ast.Constant) and isinstance(argument.value, str):
                        found.append((f"{path.name}:{node.lineno}", argument.value))
        return found

    def test_no_label_falls_back_to_the_placeholder_glyph(self) -> None:
        placeholder = glyph("?")
        labels = self._label_strings()
        self.assertTrue(labels, "no pixel-font labels were found in gui/")
        for location, label in labels:
            for character in label:
                if character == " ":
                    continue
                with self.subTest(label=label, character=character, location=location):
                    self.assertNotEqual(
                        glyph(character),
                        placeholder,
                        f"{location} renders {character!r} as the placeholder",
                    )

    def test_known_accents_and_symbols_render(self) -> None:
        for character in "\u2212\u2014\u2026\u2192\u2190\u25bc\u2713\u00b7":
            with self.subTest(character=character):
                self.assertNotEqual(glyph(character), glyph("?"))


if __name__ == "__main__":
    unittest.main()
