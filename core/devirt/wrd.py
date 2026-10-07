"""WeAreDevs (WRD) obfuscator: static recovery of the string pool.

The ``wearedevs.net/obfuscator`` wrappers (the ``v1.0.0`` banner and the newer
``v8``/v2.4 builds) reduce the protected program to a hand-rolled Lua 5.1
interpreter plus **one literal table holding every string constant of the
program**.  That table is stored base64-encoded under a permuted alphabet and
shuffled with a triple reversal, and both steps are pure constants in the file:

* ``local E = { "OtaNr52shda3IMJlOW==", ... }`` -- the encoded pool;
* ``for _, m in ipairs({{1, 45}, {1, 29}, {30, 45}}) do while m[1] < m[2] do
  ... E[m[1]], E[m[2]], m[1], m[2] = E[m[2]], E[m[1]], m[1] + 1, m[2] - 1``
  -- reverse ``E[1..45]``, then ``E[1..29]``, then ``E[30..45]``;
* ``local I = { ["0"] = 14, y = 37, ... }`` -- single character to 6-bit value,
  i.e. the base64 alphabet as the obfuscator permuted it, followed by the
  standard 24-bit group assembly.

Nothing in that pipeline depends on the runtime, so the pool -- the library
names the interpreter binds, the loader's own error/tamper strings, and every
constant the protected program carries -- can be read back **without running
the script**.  Entries the loader still keeps encrypted behind a run-time key
are reported as data, never as recovered source.

The instruction stream itself is not in the pool: the loader assembles it into
a numeric table while it runs.  When the caller has a ``core.vm_dump`` capture
of that table (``vm_tables``), the words are reported next to the pool instead
of being invented here.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any, Iterable, Sequence

from core.deobfuscator import Token, _ExpressionParser, _UNKNOWN, tokenize

__all__ = [
    "Pool",
    "find_pool",
    "decode_entry",
    "decode_pool",
    "render_listing",
    "devirtualize",
]

#: A pool table is recognised from its shape, not from a name: the loader picks
#: fresh local names for it on every build.
_MIN_POOL_ENTRIES = 8
_MIN_ALPHABET_ENTRIES = 40
_ALPHABET_VALUES = range(64)
#: How much of the pool must read as text before it is presented as recovered.
_READABLE_TARGET = 0.6


@dataclass(frozen=True)
class Pool:
    """The WRD string pool as the loader stores it, plus what was applied."""

    strings: tuple[bytes, ...]
    alphabet: dict[bytes, int]
    shuffle: tuple[tuple[int, int], ...] = ()
    reversed_ranges: bool = False
    table_name: str = ""
    spans: tuple[tuple[int, int], ...] = ()
    notes: tuple[str, ...] = field(default_factory=tuple)

    @property
    def size(self) -> int:
        return len(self.strings)


def _fold(tokens: Sequence[Token], index: int) -> tuple[Any, int]:
    """Fold the constant expression starting at ``index`` (``None`` if not one)."""
    value, end = _ExpressionParser(list(tokens), index, {}).parse()
    return (None if value is _UNKNOWN else value), end


def _parse_table(tokens: Sequence[Token], open_index: int) -> tuple[list[Any], list[Any], int]:
    """``(key/value pairs, positional values, index after '}')`` for a table literal."""
    entries: list[Any] = []
    positional: list[Any] = []
    index = open_index + 1
    while index < len(tokens) and tokens[index].text != "}":
        token = tokens[index]
        if token.text in {",", ";"}:
            index += 1
            continue
        if token.text == "[":
            key, cursor = _fold(tokens, index + 1)
            while cursor < len(tokens) and tokens[cursor].text != "]":
                cursor += 1
            cursor += 1
            if cursor < len(tokens) and tokens[cursor].text == "=":
                value, cursor = _fold(tokens, cursor + 1)
            else:
                value = None
            entries.append((key, value))
            index = max(cursor, index + 1)
            continue
        if token.kind == "identifier" and index + 1 < len(tokens) and tokens[index + 1].text == "=":
            value, cursor = _fold(tokens, index + 2)
            entries.append((token.text.encode("latin-1"), value))
            index = max(cursor, index + 1)
            continue
        value, cursor = _fold(tokens, index)
        positional.append(value)
        index = cursor if cursor > index else index + 1
    return entries, positional, index + 1


def _is_string_pool(positional: Iterable[Any], minimum: int = _MIN_POOL_ENTRIES) -> bool:
    values = list(positional)
    if len(values) < minimum:
        return False
    strings = [value for value in values if isinstance(value, bytes)]
    return len(strings) >= len(values) * 0.9 and len(strings) >= minimum


def _as_alphabet(entries: Iterable[Any]) -> dict[bytes, int] | None:
    alphabet: dict[bytes, int] = {}
    for key, value in entries:
        if not isinstance(key, bytes) or len(key) != 1:
            return None
        if not isinstance(value, (int, float)) or isinstance(value, bool):
            return None
        number = int(value)
        if number not in _ALPHABET_VALUES:
            return None
        alphabet[key] = number
    if len(alphabet) < _MIN_ALPHABET_ENTRIES:
        return None
    return alphabet


def _as_shuffle(positional: Iterable[Any]) -> tuple[tuple[int, int], ...] | None:
    pairs: list[tuple[int, int]] = []
    for value in positional:
        values = getattr(value, "values", None)
        if values is None or len(values) != 2:
            return None
        try:
            low, high = (int(number) for number in values)
        except (TypeError, ValueError):
            return None
        if low < 1 or high < low:
            return None
        pairs.append((low, high))
    if not pairs:
        return None
    return tuple(pairs)


def _decode_group(values: Sequence[int]) -> bytes:
    """One base64 group (2, 3 or 4 six-bit values) big-endian, as the loader does."""
    if not values:
        return b""
    packed = 0
    for index, value in enumerate(values):
        packed += value * (64 ** (len(values) - 1 - index))
    bits = len(values) * 6
    return bytes((packed >> (bits - 8 * (index + 1))) & 0xFF for index in range(bits // 8))


def decode_entry(entry: bytes, alphabet: dict[bytes, int]) -> bytes:
    """Decode one pool entry.  Characters outside the alphabet are kept as-is."""
    out = bytearray()
    group: list[int] = []
    for byte in entry:
        character = bytes([byte])
        if character == b"=":
            out += _decode_group(group)
            group = []
            continue
        value = alphabet.get(character)
        if value is None:
            out += _decode_group(group)
            group = []
            out.append(byte)
            continue
        group.append(value)
        if len(group) == 4:
            out += _decode_group(group)
            group = []
    out += _decode_group(group)
    return bytes(out)


def decode_pool(pool: Pool) -> list[bytes]:
    """Every entry of the pool, decoded in the order the loader reads them."""
    strings = list(pool.strings)
    if pool.reversed_ranges:
        for low, high in pool.shuffle:
            strings[low - 1 : high] = strings[low - 1 : high][::-1]
    return [decode_entry(entry, pool.alphabet) for entry in strings]


def _readable(data: bytes) -> bool:
    if not data:
        return True
    return all(32 <= byte < 127 or byte in (9, 10, 13) for byte in data)


def _readable_ratio(chunks: Sequence[bytes]) -> float:
    if not chunks:
        return 0.0
    return sum(1 for chunk in chunks if _readable(chunk)) / len(chunks)


def _looks_like_identifier(data: bytes) -> bool:
    return bool(re.fullmatch(rb"[A-Za-z_][A-Za-z0-9_]{0,40}", data or b""))


def _check_shuffle(tokens: Sequence[Token], pairs_index: int) -> bool:
    """Whether the pairs list is followed by the swap loop the loader uses.

    The pool is only reordered when the loader's own reversal loop is present:
    a table of pairs on its own says nothing about the order of the pool.
    """
    window = [token.text for token in tokens[pairs_index : pairs_index + 160]]
    if "while" not in window:
        return False
    body = " ".join(window)
    return "[ " in body and "=[" not in body and "= " in body and body.count("[") >= 6


def find_pool(source: str) -> Pool | None:
    """Locate the encoded string pool, its alphabet and its shuffle in ``source``."""
    tokens = tokenize(source)
    if not tokens:
        return None
    strings: tuple[bytes, ...] | None = None
    alphabet: dict[bytes, int] | None = None
    shuffle: tuple[tuple[int, int], ...] = ()
    shuffle_supported = False
    notes: list[str] = []
    spans: list[tuple[int, int]] = []

    for index, token in enumerate(tokens):
        if token.text != "{":
            continue
        entries, positional, end = _parse_table(tokens, index)
        if strings is None and _is_string_pool(positional) and len(positional) >= _MIN_POOL_ENTRIES:
            strings = tuple(positional)
            spans.append((token.start, tokens[end - 1].end))
        if alphabet is None and entries:
            candidate = _as_alphabet(entries)
            if candidate is not None:
                alphabet = candidate
                spans.append((token.start, tokens[end - 1].end))
        if not shuffle and token.text == "{" and index >= 2 and tokens[index - 1].text == "(" \
                and tokens[index - 2].text == "ipairs":
            pairs = _as_shuffle(positional)
            if pairs is not None:
                shuffle = pairs
                shuffle_supported = _check_shuffle(tokens, index)
    if strings is None or alphabet is None:
        return None

    pool = Pool(strings=strings, alphabet=alphabet, shuffle=shuffle, reversed_ranges=shuffle_supported,
                table_name="", spans=tuple(spans), notes=tuple(notes))
    if shuffle:
        forward = decode_pool(pool)
        plain = Pool(strings=strings, alphabet=alphabet, shuffle=(), reversed_ranges=False,
                     spans=tuple(spans))
        if _readable_ratio(decode_pool(plain)) > _readable_ratio(forward):
            notes.append("the loader's swap loop was not applied: the pool reads better in table order")
            return Pool(strings=strings, alphabet=alphabet, shuffle=shuffle, reversed_ranges=False,
                        spans=tuple(spans), notes=tuple(notes))
    return pool


def _word_dump(values: Sequence[int], limit: int = 24) -> list[str]:
    lines = []
    for start in range(0, min(len(values), limit * 4), 4):
        group = values[start : start + 4]
        if len(group) < 4:
            break
        word = group[0] | (group[1] << 8) | (group[2] << 16) | (group[3] << 24)
        lines.append("  %08x  (bytes %s)" % (word, " ".join(str(value) for value in group)))
    return lines


def _instruction_table(vm_tables: Sequence[Any] | None) -> tuple[list[int], str]:
    """The loader's own instruction array from a runtime capture, if there is one."""
    best: list[int] = []
    label = ""
    for table in vm_tables or ():
        values = list(getattr(table, "values", ()) or ())
        if not values or not all(isinstance(value, (int, float)) and not isinstance(value, bool)
                                 for value in values):
            continue
        if len(values) > len(best):
            best = [int(value) for value in values]
            label = str(getattr(table, "label", "") or "capture")
    return best, label


def render_listing(pool: Pool, decoded: Sequence[bytes], vm_tables: Sequence[Any] | None = None) -> str:
    """A readable, non-executable report of the recovered pool."""
    lines = ["-- WRD/WeAreDevs string pool recovered statically.",
             "-- %d entries; %d read back as constants, %d stay encrypted (the loader"
             % (len(decoded), sum(1 for chunk in decoded if _readable(chunk) and chunk),
                sum(1 for chunk in decoded if not _readable(chunk) or not chunk)),
             "-- derives its per-script key at run time)."]
    if pool.reversed_ranges:
        ranges = ", ".join("%d..%d" % pair for pair in pool.shuffle)
        lines.append("-- the loader's triple reversal was applied: %s" % ranges)
    lines.append("")
    for index, chunk in enumerate(decoded, start=1):
        if _readable(chunk) and chunk:
            lines.append("[%3d] %s" % (index, chunk.decode("latin-1")))
        elif _readable(chunk):
            lines.append("[%3d] (empty)" % index)
        else:
            lines.append("[%3d] (data, %d bytes) %s" % (index, len(chunk), chunk.hex()))
    values, label = _instruction_table(vm_tables)
    if values:
        lines.append("")
        lines.append("-- the loader's instruction table, %d words captured at run time%s:"
                     % (len(values), " (%s)" % label if label else ""))
        lines += _word_dump(values)
    return "\n".join(lines)


def devirtualize(
    source: str,
    *,
    vm_tables: Sequence[Any] | None = None,
    family: str = "wearedevs",
    logger: Any = None,
    **_ignored: Any,
) -> dict[str, Any] | None:
    """Recover a WRD wrapper's string pool; never claim more than was decoded."""
    try:
        pool = find_pool(source)
    except Exception as exc:  # noqa: BLE001 - a broken pool must not fail a run
        if logger is not None:
            logger.debug("WRD pool scan failed: %s", exc)
        return None
    if pool is None:
        return None
    decoded = decode_pool(pool)
    readable = [chunk for chunk in decoded if _readable(chunk) and chunk]
    ratio = _readable_ratio(decoded)
    names = sum(1 for chunk in readable if _looks_like_identifier(chunk))
    notes = [
        "the pool holds the protected program's string constants: %d bytes decoded from %d entries"
        % (sum(len(chunk) for chunk in decoded), len(decoded)),
        "%d entries read back as text, %d bound library/API names among them"
        % (len(readable), names),
    ]
    if ratio < 1.0:
        notes.append("%d entries are still encrypted: the loader decrypts them with a key it builds"
                     " while it runs, so they are reported as data" % (len(decoded) - len(readable)))
    notes.extend(pool.notes)
    confidence = 0.55 + (0.15 if pool.alphabet else 0.0) + (0.15 if pool.reversed_ranges else 0.0) \
        + 0.15 * ratio
    return {
        "family": family,
        "method": "WRD/WeAreDevs static string-pool recovery",
        "source": None,
        "bytecode": None,
        "notes": notes,
        "partial": True,
        "confidence": min(confidence, 0.95),
        "listing": render_listing(pool, decoded, vm_tables),
        "opcode_names": {},
    }
