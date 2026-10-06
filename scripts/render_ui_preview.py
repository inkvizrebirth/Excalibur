"""Render preview images of the pixel interface.

The sandbox that builds Protez has no display server, so this script draws the
same palette, bitmap font and metrics the real window uses (``gui.theme``,
``gui.pixelfont``, ``gui.highlight``) into PNG files.  The result is a faithful
mock-up of the chrome, not a screenshot: Tk still renders the live window.

Usage::

    python scripts/render_ui_preview.py [output-directory]
"""

from __future__ import annotations

import struct
import sys
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from gui import highlight, theme  # noqa: E402
from gui.logo_art import _BORDER, _SWORD  # noqa: E402
from gui.pixelfont import (  # noqa: E402
    GLYPH_HEIGHT,
    GLYPH_WIDTH,
    LETTER_SPACING,
    text_pixels,
)

WIDTH = theme.DEFAULT_WIDTH
HEIGHT = theme.DEFAULT_HEIGHT


class Canvas:
    """Minimal RGB canvas with pixel-font text and rectangle helpers."""

    def __init__(self, width: int, height: int, background: str) -> None:
        self.width = width
        self.height = height
        self.pixels = [[_rgb(background)] * width for _ in range(height)]

    def rectangle(
        self,
        x: int,
        y: int,
        width: int,
        height: int,
        *,
        fill: str | None = None,
        outline: str | None = None,
    ) -> None:
        if fill is not None:
            colour = _rgb(fill)
            for row in range(max(0, y), min(self.height, y + height)):
                self.pixels[row][max(0, x) : min(self.width, x + width)] = [colour] * (
                    min(self.width, x + width) - max(0, x)
                )
        if outline is not None:
            colour = _rgb(outline)
            for column in range(max(0, x), min(self.width, x + width)):
                self._point(column, y, colour)
                self._point(column, y + height - 1, colour)
            for row in range(max(0, y), min(self.height, y + height)):
                self._point(x, row, colour)
                self._point(x + width - 1, row, colour)

    def text(self, x: int, y: int, text: str, colour: str, *, scale: int = 1) -> int:
        """Draw ``text`` and return the x position after it."""
        ink = _rgb(colour)
        cursor = x
        for character in text:
            if character == " ":
                cursor += 4 * scale
                continue
            rows = text_pixels(character, spacing=0)
            for row_index, row in enumerate(rows):
                for column, cell in enumerate(row):
                    if not cell:
                        continue
                    for dy in range(scale):
                        for dx in range(scale):
                            self._point(
                                cursor + column * scale + dx,
                                y + row_index * scale + dy,
                                ink,
                            )
            cursor += (GLYPH_WIDTH + LETTER_SPACING) * scale
        return cursor

    def emblem(self, x: int, y: int, size: int, ink: str, accent: str) -> None:
        cell = size / 16
        ink_rgb = _rgb(ink)
        accent_rgb = _rgb(accent)
        for row_index, row in enumerate(_SWORD):
            for column, character in enumerate(row):
                if character != "#":
                    continue
                self._fill_rect(
                    x + int(column * cell), y + int(row_index * cell), max(1, int(cell)), max(1, int(cell)), accent_rgb
                )
        for column, row_index in sorted(_BORDER):
            self._fill_rect(
                x + int(column * cell), y + int(row_index * cell), max(1, int(cell)), max(1, int(cell)), ink_rgb
            )

    def _fill_rect(self, x: int, y: int, width: int, height: int, colour: tuple[int, int, int]) -> None:
        for row in range(y, y + height):
            if 0 <= row < self.height:
                for column in range(x, x + width):
                    self._point(column, row, colour)

    def _point(self, x: int, y: int, colour: tuple[int, int, int]) -> None:
        if 0 <= x < self.width and 0 <= y < self.height:
            self.pixels[y][x] = colour

    def save(self, path: Path) -> None:
        raw = bytearray()
        for row in self.pixels:
            raw.append(0)
            for red, green, blue in row:
                raw.extend((red, green, blue))
        header = struct.pack(">IIBBBBB", self.width, self.height, 8, 2, 0, 0, 0)

        def chunk(tag: bytes, payload: bytes) -> bytes:
            return (
                struct.pack(">I", len(payload))
                + tag
                + payload
                + struct.pack(">I", zlib.crc32(tag + payload) & 0xFFFFFFFF)
            )

        path.write_bytes(
            b"\x89PNG\r\n\x1a\n"
            + chunk(b"IHDR", header)
            + chunk(b"IDAT", zlib.compress(bytes(raw), 9))
            + chunk(b"IEND", b"")
        )


def _rgb(colour: str) -> tuple[int, int, int]:
    value = colour.lstrip("#")
    return int(value[0:2], 16), int(value[2:4], 16), int(value[4:6], 16)


SAMPLE_SOURCE = (
    "-- IronBrew:^3 protected\n"
    "local payload = {27,76,117,97,81,0,1,4,8,4,8,0,9,0,0,0}\n"
    "local parts = {}\n"
    "for i = 1, #payload do parts[i] = string.char(payload[i]) end\n"
    "return loadstring(table.concat(parts))()\n"
)

RECOVERED = """-- Recovered from Lua 5.1 bytecode by Protez.
local recovered_chunk = function(list, factor)
    local total = 0
    for index = 1, #list do
        total = total + list[index] * factor
    end
    if total > 100 then
        return "big"
    end
    return total
end
"""

LOG_LINES = (
    ("19:52:04", "INFO", "Likely family: IronBrew v3 (confidence 0.85)"),
    ("19:52:04", "INFO", "Executor environment attached for profile Auto"),
    ("19:52:05", "INFO", "Embedded Lua 5.1 bytecode decompiled"),
    ("19:52:05", "WARNING", "Lifted listing is an approximation (register names)"),
    ("19:52:06", "INFO", "Recovered source written to output/destroyed_1.lua"),
)


def panel(canvas: Canvas, x: int, y: int, width: int, height: int) -> tuple[int, int]:
    canvas.rectangle(x, y, width, height, fill=theme.PANEL, outline=theme.BORDER)
    return x + theme.PANEL_PAD, y + theme.PANEL_PAD


def draw_code(canvas: Canvas, x: int, y: int, source: str, *, lines: int) -> None:
    """Draw highlighted source with per-line numbers."""
    source_lines = source.split("\n")
    spans_per_line = highlight.highlight_lines(source)
    cursor_y = y
    for index, line in enumerate(source_lines[:lines]):
        canvas.text(x, cursor_y, f"{index + 1:>3}", theme.MUTED, scale=1)
        cursor_x = x + (GLYPH_WIDTH + LETTER_SPACING) * 4 + 4
        position = 0
        for span in spans_per_line[index]:
            if span.start > position:
                cursor_x = canvas.text(
                    cursor_x, cursor_y, line[position : span.start], theme.TEXT
                )
            cursor_x = canvas.text(
                cursor_x,
                cursor_y,
                line[span.start : span.end],
                theme.SYNTAX_COLORS.get(span.tag, theme.TEXT),
            )
            position = span.end
        if position < len(line):
            canvas.text(cursor_x, cursor_y, line[position:], theme.TEXT)
        cursor_y += GLYPH_HEIGHT + 4


def render_main_window(path: Path) -> Path:
    canvas = Canvas(WIDTH, HEIGHT, theme.BG)

    # Title bar
    canvas.rectangle(8, 8, WIDTH - 16, 34, fill=theme.PANEL, outline=theme.BORDER)
    canvas.rectangle(8, 41, WIDTH - 16, 1, fill=theme.ACCENT)
    canvas.emblem(14, 14, 22, theme.BORDER_BRIGHT, theme.ACCENT)
    cursor = canvas.text(44, 14, "PROTEZ", theme.TEXT, scale=2)
    canvas.text(cursor + 6, 22, "v0.6.2  -  ROBLOX SCRIPT RECOVERY", theme.MUTED)
    canvas.rectangle(WIDTH - 56, 16, 20, 18, fill=theme.PANEL_RAISED, outline=theme.BORDER)
    canvas.text(WIDTH - 50, 22, "-", theme.MUTED)
    canvas.rectangle(WIDTH - 30, 16, 20, 18, fill=theme.PANEL_RAISED, outline=theme.BORDER)
    canvas.text(WIDTH - 24, 22, "X", theme.ERROR)

    # Source panel
    left, top = panel(canvas, 8, 50, WIDTH - 16, 214)
    canvas.text(left, top, "SOURCE", theme.ACCENT)
    canvas.text(left + 70, top, "PASTE / URL / DROP FILE / CTRL+ENTER", theme.MUTED)
    for index, (label, colour) in enumerate(
        (("CLEAR", theme.MUTED), ("PASTE", theme.CYAN), ("FILE", theme.CYAN))
    ):
        button_x = WIDTH - 8 - theme.PANEL_PAD - (index + 1) * 58
        canvas.rectangle(button_x, top - 3, 52, 16, fill=theme.PANEL_ALT, outline=theme.BORDER)
        canvas.text(button_x + 8, top + 1, label, colour)
    canvas.rectangle(left, top + 22, WIDTH - 16 - theme.PANEL_PAD * 2, 168, fill=theme.BG_SUNKEN, outline=theme.BORDER)
    for index, line in enumerate(SAMPLE_SOURCE.rstrip("\n").split("\n")[:7]):
        colour = theme.SYNTAX_COLORS["comment"] if line.startswith("--") else theme.TEXT_DIM
        canvas.text(left + 8, top + 28 + index * 18, _as_ascii(line)[:96], colour)

    # Options row
    row_y = 276
    canvas.text(10, row_y + 5, "INJECTOR", theme.MUTED)
    canvas.rectangle(78, row_y, 232, 22, fill=theme.PANEL, outline=theme.CYAN)
    canvas.text(86, row_y + 7, _as_ascii("Auto - all executors (recommended)")[:34], theme.TEXT)
    canvas.text(238, row_y + 7, "V", theme.CYAN)
    canvas.rectangle(322, row_y + 4, 13, 13, fill=theme.ACCENT, outline=theme.BORDER)
    canvas.text(340, row_y + 5, "FETCH REMOTE PAYLOADS", theme.TEXT_DIM)
    canvas.text(516, row_y + 5, "SCRIPT KEY", theme.MUTED)
    canvas.rectangle(586, row_y, 170, 22, fill=theme.BG_SUNKEN, outline=theme.BORDER)
    canvas.text(594, row_y + 7, "optional", theme.DISABLED)

    # Action row
    action_y = 312
    canvas.rectangle(8, action_y, 132, 44, fill=theme.ACCENT_SOFT, outline=theme.ACCENT)
    canvas.rectangle(9, action_y + 1, 130, 42, fill=theme.ACCENT)
    canvas.text(34, action_y + 12, "DESTROY", theme.BG, scale=2)
    canvas.rectangle(152, action_y + 8, WIDTH - 160, 12, fill=theme.PANEL_ALT, outline=theme.BORDER)
    filled = int((WIDTH - 164) * 0.72)
    for block in range(0, filled - 6, 10):
        canvas.rectangle(155 + block, action_y + 11, 7, 6, fill=theme.ACCENT)
    canvas.text(156, action_y + 26, "DECODE  -  layer 2 of 3", theme.TEXT_DIM)

    # Activity panel
    left, top = panel(canvas, 8, 366, WIDTH - 16, 224)
    canvas.text(left, top, "ACTIVITY", theme.ACCENT)
    canvas.rectangle(WIDTH - 8 - theme.PANEL_PAD - 96, top - 3, 96, 16, fill=theme.PANEL_ALT, outline=theme.BORDER)
    canvas.text(WIDTH - 8 - theme.PANEL_PAD - 88, top + 1, "OPEN RESULT", theme.ACCENT)
    canvas.rectangle(left, top + 22, WIDTH - 16 - theme.PANEL_PAD * 2, 208, fill=theme.BG_SUNKEN, outline=theme.BORDER)
    for index, (stamp, level, message) in enumerate(LOG_LINES):
        line_y = top + 30 + index * 24
        canvas.text(left + 8, line_y, stamp, theme.MUTED)
        colour = theme.LEVEL_COLORS[level]
        canvas.text(left + 66, line_y, level, colour)
        canvas.text(left + 132, line_y, _as_ascii(message)[:74], theme.TEXT_DIM)

    canvas.text(
        10,
        HEIGHT - 24,
        "PREVIEW ONLY - THE SOURCE BOX AND THE VIEWER USE THE SYSTEM MONOSPACE FONT AT RUNTIME",
        theme.MUTED,
    )
    canvas.rectangle(WIDTH - 18, HEIGHT - 16, 12, 12, outline=theme.BORDER_BRIGHT)
    canvas.save(path)
    return path


def render_viewer(path: Path) -> Path:
    canvas = Canvas(WIDTH, 432, theme.BG)
    canvas.rectangle(8, 8, WIDTH - 16, 26, fill=theme.PANEL, outline=theme.BORDER)
    canvas.rectangle(8, 33, WIDTH - 16, 1, fill=theme.ACCENT)
    canvas.text(16, 14, "PROTEZ VIEWER", theme.TEXT)
    canvas.text(WIDTH - 250, 14, "OUTPUT/DESTROYED_1.LUA", theme.MUTED)
    canvas.rectangle(WIDTH - 44, 11, 28, 18, fill=theme.PANEL_ALT, outline=theme.BORDER)
    canvas.text(WIDTH - 38, 16, "X", theme.ERROR)

    canvas.rectangle(8, 40, WIDTH - 16, 28, fill=theme.PANEL_ALT, outline=theme.BORDER)
    canvas.text(16, 48, "FAMILY", theme.MUTED)
    canvas.text(70, 48, "IRONBREW V3", theme.ACCENT)
    canvas.text(180, 48, "STATUS", theme.MUTED)
    canvas.text(232, 48, "PARTIAL RECOVERY", theme.WARN)
    canvas.text(370, 48, "FIND", theme.MUTED)
    canvas.rectangle(406, 44, 150, 20, fill=theme.BG_SUNKEN, outline=theme.BORDER)
    canvas.rectangle(566, 44, 54, 20, fill=theme.PANEL_RAISED, outline=theme.BORDER)
    canvas.text(576, 49, "NEXT", theme.CYAN)

    canvas.rectangle(8, 74, WIDTH - 16, 296, fill=theme.BG_SUNKEN, outline=theme.BORDER)
    draw_code(canvas, 16, 84, RECOVERED, lines=13)
    canvas.text(16, 378, "RECOVERED CODE - REGISTER NAMES ARE SYNTHETIC", theme.MUTED)
    canvas.text(
        16,
        396,
        "PREVIEW ONLY - THE VIEWER DRAWS CODE WITH THE SYSTEM MONOSPACE FONT AND THE SAME COLOURS",
        theme.MUTED,
    )
    canvas.save(path)
    return path


def _as_ascii(text: str) -> str:
    replacements = {"−": "-", "—": "-", "…": "...", "·": ".", "×": "x", "→": "->", "←": "<-"}
    return "".join(replacements.get(character, character) for character in text)


def main() -> int:
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else ROOT / "docs" / "preview"
    target.mkdir(parents=True, exist_ok=True)
    printed = [
        render_main_window(target / "ui-main-window.png"),
        render_viewer(target / "ui-viewer.png"),
    ]
    for path in printed:
        print(f"wrote {path.relative_to(ROOT)} ({path.stat().st_size:,} bytes)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
