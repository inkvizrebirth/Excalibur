"""Generate ``assets/icon.ico`` (monochrome, no Pillow required).

The mark is deliberately simple: a black rounded square with a white blade and a
crossguard - readable at 16x16, strictly monochrome, matching the GUI palette.

    python tools/make_icon.py            # write assets/icon.ico
    python tools/make_icon.py --check    # verify it exists and is a valid ICO
"""

from __future__ import annotations

import argparse
import struct
import sys
from pathlib import Path
from typing import List, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "assets" / "icon.ico"
SIZES = (16, 32, 48, 64, 128)

BACKGROUND = (10, 10, 10, 255)
BLADE = (255, 255, 255, 255)
GUARD = (224, 224, 224, 255)
HILT = (138, 138, 138, 255)


def _blend(pixel: Tuple[int, int, int, int], colour: Tuple[int, int, int, int]) -> Tuple[int, int, int, int]:
    """Paint ``colour`` over ``pixel`` using the colour's own alpha."""
    alpha = colour[3] / 255.0
    return tuple(  # type: ignore[return-value]
        int(round(pixel[index] * (1 - alpha) + colour[index] * alpha)) for index in range(4)
    )


def _distance_to_segment(px: float, py: float, ax: float, ay: float, bx: float, by: float) -> float:
    dx, dy = bx - ax, by - ay
    length_squared = dx * dx + dy * dy
    if length_squared == 0:
        return ((px - ax) ** 2 + (py - ay) ** 2) ** 0.5
    t = max(0.0, min(1.0, ((px - ax) * dx + (py - ay) * dy) / length_squared))
    cx, cy = ax + t * dx, ay + t * dy
    return ((px - cx) ** 2 + (py - cy) ** 2) ** 0.5


def render(size: int) -> List[Tuple[int, int, int, int]]:
    """Draw the mark on a ``size x size`` RGBA canvas."""
    pixels = [BACKGROUND for _ in range(size * size)]
    unit = size / 16.0
    # anti-aliased lines: supersample 3x3 per pixel
    samples = 3
    for y in range(size):
        for x in range(size):
            hits_blade = hits_guard = hits_hilt = 0
            for sy in range(samples):
                for sx in range(samples):
                    px = x + (sx + 0.5) / samples
                    py = y + (sy + 0.5) / samples
                    # blade: diagonal from the lower left to the upper right
                    blade = _distance_to_segment(px, py, 3.4 * unit, 12.6 * unit, 12.0 * unit, 4.0 * unit)
                    guard = _distance_to_segment(px, py, 4.4 * unit, 10.0 * unit, 9.2 * unit, 10.0 * unit)
                    hilt = _distance_to_segment(px, py, 3.6 * unit, 11.4 * unit, 5.6 * unit, 13.4 * unit)
                    hits_blade += blade <= 0.95 * unit
                    hits_guard += guard <= 0.45 * unit
                    hits_hilt += hilt <= 0.55 * unit
            total = samples * samples
            pixel = BACKGROUND
            if hits_blade:
                pixel = _blend(pixel, (*BLADE[:3], int(255 * hits_blade / total)))
            if hits_guard:
                pixel = _blend(pixel, (*GUARD[:3], int(255 * hits_guard / total)))
            if hits_hilt:
                pixel = _blend(pixel, (*HILT[:3], int(255 * hits_hilt / total)))
            pixels[y * size + x] = pixel
    return pixels


def bmp_entry(size: int, pixels: Sequence[Tuple[int, int, int, int]]) -> bytes:
    """Encode one icon image as an uncompressed 32bpp BMP DIB."""
    header = struct.pack(
        "<IiiHHIIiiII",
        40,           # biSize
        size,         # biWidth
        size * 2,     # biHeight (colour + mask)
        1,            # biPlanes
        32,           # biBitCount
        0,            # biCompression
        0,            # biSizeImage
        0, 0, 0, 0,   # ppm / clr used / clr important
    )
    rows = []
    for y in range(size - 1, -1, -1):  # bottom-up
        row = bytearray()
        for x in range(size):
            red, green, blue, alpha = pixels[y * size + x]
            row += bytes((blue, green, red, alpha))
        rows.append(bytes(row))
    colour = b"".join(rows)
    mask_row = ((size + 31) // 32) * 4  # 1bpp AND mask, padded to 4 bytes
    mask = b"\x00" * (mask_row * size)
    return header + colour + mask


def build_ico(sizes: Sequence[int] = SIZES) -> bytes:
    images = [(size, bmp_entry(size, render(size))) for size in sizes]
    header = struct.pack("<HHH", 0, 1, len(images))
    directory = bytearray()
    offset = 6 + 16 * len(images)
    payload = bytearray()
    for size, data in images:
        dimension = 0 if size >= 256 else size
        directory += struct.pack("<BBBBHHII", dimension, dimension, 0, 0, 1, 32, len(data), offset)
        payload += data
        offset += len(data)
    return bytes(header + directory + payload)


def check() -> int:
    if not TARGET.exists():
        print(f"missing {TARGET.relative_to(ROOT)}: run python tools/make_icon.py")
        return 1
    data = TARGET.read_bytes()
    if len(data) < 6:
        print("icon is truncated")
        return 1
    reserved, kind, count = struct.unpack("<HHH", data[:6])
    if reserved != 0 or kind != 1 or count == 0:
        print(f"not a valid ICO (reserved={reserved} kind={kind} count={count})")
        return 1
    sizes = []
    for index in range(count):
        entry = data[6 + 16 * index : 6 + 16 * (index + 1)]
        width, height, _colors, _res, _planes, _bits, length, offset = struct.unpack("<BBBBHHII", entry)
        if offset + length > len(data):
            print(f"entry {index} points outside the file")
            return 1
        sizes.append(width or 256)
    print(f"{TARGET.relative_to(ROOT)}: {count} image(s) {sizes}, {len(data):,} bytes")
    return 0


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="generate the Excalibur icon")
    parser.add_argument("--check", action="store_true", help="verify the committed icon")
    args = parser.parse_args(argv)
    if args.check:
        return check()
    TARGET.parent.mkdir(parents=True, exist_ok=True)
    TARGET.write_bytes(build_ico())
    print(f"wrote {TARGET.relative_to(ROOT)} ({TARGET.stat().st_size:,} bytes)")
    return check()


if __name__ == "__main__":
    sys.exit(main())
