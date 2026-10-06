"""Tiny 5x7 bitmap font used by the pixel-styled interface.

The interface draws its own chrome, so labels are rendered from a hand-made
bitmap font instead of a system typeface.  Everything in this module is pure
Python (no Tk import), which keeps the glyph table testable on its own.
"""

from __future__ import annotations

from typing import Iterable, Sequence

GLYPH_WIDTH = 5
GLYPH_HEIGHT = 7
LETTER_SPACING = 1
WORD_SPACING = 4

# Each glyph is seven rows of five cells; '#' is ink, '.' is empty.
_GLYPHS: dict[str, str] = {
    "A": ".###./#...#/#...#/#####/#...#/#...#/#...#",
    "B": "####./#...#/#...#/####./#...#/#...#/####.",
    "C": ".###./#...#/#..../#..../#..../#...#/.###.",
    "D": "####./#...#/#...#/#...#/#...#/#...#/####.",
    "E": "#####/#..../#..../####./#..../#..../#####",
    "F": "#####/#..../#..../####./#..../#..../#....",
    "G": ".###./#...#/#..../#.###/#...#/#...#/.###.",
    "H": "#...#/#...#/#...#/#####/#...#/#...#/#...#",
    "I": ".###./..#../..#../..#../..#../..#../.###.",
    "J": "..###/...#./...#./...#./...#./#..#./.##..",
    "K": "#...#/#..#./#.#../##.../#.#../#..#./#...#",
    "L": "#..../#..../#..../#..../#..../#..../#####",
    "M": "#...#/##.##/#.#.#/#...#/#...#/#...#/#...#",
    "N": "#...#/##..#/#.#.#/#..##/#...#/#...#/#...#",
    "O": ".###./#...#/#...#/#...#/#...#/#...#/.###.",
    "P": "####./#...#/#...#/####./#..../#..../#....",
    "Q": ".###./#...#/#...#/#...#/#.#.#/#..#./.##.#",
    "R": "####./#...#/#...#/####./#.#../#..#./#...#",
    "S": ".####/#..../#..../.###./....#/....#/####.",
    "T": "#####/..#../..#../..#../..#../..#../..#..",
    "U": "#...#/#...#/#...#/#...#/#...#/#...#/.###.",
    "V": "#...#/#...#/#...#/#...#/#...#/.#.#./..#..",
    "W": "#...#/#...#/#...#/#.#.#/#.#.#/##.##/#...#",
    "X": "#...#/#...#/.#.#./..#../.#.#./#...#/#...#",
    "Y": "#...#/#...#/.#.#./..#../..#../..#../..#..",
    "Z": "#####/....#/...#./..#../.#.../#..../#####",
    "0": ".###./#...#/#..##/#.#.#/##..#/#...#/.###.",
    "1": "..#../.##../..#../..#../..#../..#../.###.",
    "2": ".###./#...#/....#/...#./..#../.#.../#####",
    "3": "####./....#/....#/.###./....#/....#/####.",
    "4": "...#./..##./.#.#./#..#./#####/...#./...#.",
    "5": "#####/#..../####./....#/....#/#...#/.###.",
    "6": "..##./.#.../#..../####./#...#/#...#/.###.",
    "7": "#####/....#/...#./..#../.#.../.#.../.#...",
    "8": ".###./#...#/#...#/.###./#...#/#...#/.###.",
    "9": ".###./#...#/#...#/.####/....#/...#./.##..",
    ".": "...../...../...../...../...../...../..#..",
    ",": "...../...../...../...../...../..#../.#...",
    ":": "...../..#../...../...../...../..#../.....",
    ";": "...../..#../...../...../...../..#../.#...",
    "!": "..#../..#../..#../..#../..#../...../..#..",
    "?": ".###./#...#/....#/...#./..#../...../..#..",
    "-": "...../...../...../#####/...../...../.....",
    "+": "...../..#../..#../#####/..#../..#../.....",
    "=": "...../...../#####/...../#####/...../.....",
    "/": "....#/....#/...#./..#../.#.../#..../#....",
    "\\": "#..../#..../.#.../..#../...#./....#/....#",
    "(": "...#./..#../.#.../.#.../.#.../..#../...#.",
    ")": ".#.../..#../...#./...#./...#./..#../.#...",
    "[": ".###./.#.../.#.../.#.../.#.../.#.../.###.",
    "]": ".###./...#./...#./...#./...#./...#./.###.",
    "<": "...#./..#../.#.../#..../.#.../..#../...#.",
    ">": ".#.../..#../...#./....#/...#./..#../.#...",
    "_": "...../...../...../...../...../...../#####",
    "#": ".#.#./.#.#./#####/.#.#./#####/.#.#./.#.#.",
    "%": "##..#/##..#/...#./..#../.#.../#..##/#..##",
    "*": "...../#.#.#/.###./#####/.###./#.#.#/.....",
    "'": "..#../..#../...../...../...../...../.....",
    '"': ".#.#./.#.#./...../...../...../...../.....",
    "|": "..#../..#../..#../..#../..#../..#../..#..",
    "~": "...../...../.##.#/#..#./...../...../.....",
    "$": "..#../.####/#.#../.###./..#.#/####./..#..",
    "&": ".##../#..#./#.#../.#.../#.#.#/#..#./.##.#",
    "^": "..#../.#.#./#...#/...../...../...../.....",
    "@": ".###./#...#/#.###/#.#.#/#.###/#..../.###.",
    "·": "...../...../...../..#../...../...../.....",
    "×": "...../#...#/.#.#./..#../.#.#./#...#/.....",
    "▸": "#..../##.../###../####./###../##.../#....",
    "◂": "....#/...##/..###/.####/..###/...##/....#",
    "✓": "...../....#/...#./#.#../###../.#.../.....",
    "●": "...../.###./#####/#####/#####/.###./.....",
    "○": "...../.###./#...#/#...#/#...#/.###./.....",
    "▲": "...../..#../.###./#####/...../...../.....",
    "▼": "...../...../...../#####/.###./..#../.....",
    "■": "...../.###./.###./.###./.###./.###./.....",
    "□": "...../.###./#...#/#...#/#...#/.###./.....",
    "←": "...../..#../.#.../#####/.#.../..#../.....",
    "→": "...../..#../...#./#####/...#./..#../.....",
    "↑": "...../..#../.###./#.#.#/..#../..#../.....",
    "↓": "...../..#../..#../#.#.#/.###./..#../.....",
}


def glyph(char: str) -> tuple[str, ...]:
    """Return the seven rows of ``char`` (lowercase folds to uppercase)."""
    if char == " ":
        return tuple("." * GLYPH_WIDTH for _ in range(GLYPH_HEIGHT))
    key = char.upper()
    raw = _GLYPHS.get(key) or _GLYPHS.get(char)
    if raw is None:
        raw = _GLYPHS["?"]
    rows = raw.split("/")
    if len(rows) != GLYPH_HEIGHT or any(len(row) != GLYPH_WIDTH for row in rows):
        raise AssertionError(f"glyph {char!r} is malformed")
    return tuple(rows)


def text_pixels(text: str, *, spacing: int = LETTER_SPACING) -> list[list[bool]]:
    """Render ``text`` to a matrix of booleans (True = ink)."""
    if not text:
        return [[] for _ in range(GLYPH_HEIGHT)]
    rows: list[list[bool]] = [[] for _ in range(GLYPH_HEIGHT)]
    for index, char in enumerate(text):
        if char == " ":
            for row in rows:
                row.extend([False] * WORD_SPACING)
            continue
        if index:
            for row in rows:
                row.extend([False] * spacing)
        for row_index, row in enumerate(glyph(char)):
            rows[row_index].extend(cell == "#" for cell in row)
    return rows


def text_size(text: str, *, scale: int = 1, spacing: int = LETTER_SPACING) -> tuple[int, int]:
    """Pixel size of ``text`` at ``scale``."""
    pixels = text_pixels(text, spacing=spacing)
    width = max((len(row) for row in pixels), default=0)
    return width * scale, GLYPH_HEIGHT * scale


def text_rows(text: str, *, ink: str = "#", empty: str = " ") -> list[str]:
    """ASCII-art rendering, handy for tests and terminal previews."""
    return [
        "".join(ink if cell else empty for cell in row)
        for row in text_pixels(text)
    ]


def color_rows(
    text: str,
    *,
    ink: str,
    background: str,
    scale: int = 1,
) -> list[list[str]]:
    """Per-pixel colour matrix for a Tk ``PhotoImage.put`` call."""
    pixels = text_pixels(text)
    rows: list[list[str]] = []
    for row in pixels:
        expanded: list[str] = []
        for cell in row:
            expanded.extend([ink if cell else background] * scale)
        for _ in range(scale):
            rows.append(list(expanded))
    return rows


def photo_data(rows: Sequence[Sequence[str]]) -> str:
    """Serialise a colour matrix into the ``PhotoImage.put`` data string."""
    return " ".join("{" + " ".join(row) + "}" for row in rows)


def iter_characters() -> Iterable[str]:
    """Every glyph the font can draw (used by the self-test)."""
    return tuple(_GLYPHS)
