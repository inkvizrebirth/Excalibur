"""Analysis of custom-VM tables recovered from a running obfuscator.

``core.vm_dump`` snapshots the big array-like tables a Lua-implemented
obfuscator builds for itself.  Those snapshots are raw numbers; this module
turns them into something a human can read and the pipeline can report:

* the instruction stream and its stride (opcode + operands per instruction),
* an opcode histogram, which tells the two common layours apart -- a real VM
  dispatches a small set of opcodes over and over, while encrypted data has a
  flat histogram,
* a bounded disassembly listing (offset, opcode, operands),
* a confidence value, so a partial result never looks like a full lift.

This is not a decompiler and does not pretend to be one: recovering the
*semantics* of an unknown VM needs a per-family opcode map.  What it gives is
the machine-readable VM surface -- which instructions and constants exist --
and a human-readable dump, which is what a partial Luraph/IronBrew/Prometheus
result can honestly offer.
"""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from typing import Iterable, Sequence

from core.vm_dump import VmSnapshot, constant_pool, instruction_table

__all__ = [
    "VmAnalysis",
    "analyse_vm",
    "render_analysis",
    "summary_line",
]

MAX_OPERANDS = 6
DEFAULT_LISTING_LINES = 160
_LISTING_LINE_INSTRUCTIONS = 4


@dataclass(frozen=True)
class VmAnalysis:
    stream_label: str
    pool_label: str
    instruction_count: int
    width: int
    operands_per_instruction: int
    distinct_opcodes: int
    opcode_min: int
    opcode_max: int
    histogram: tuple[tuple[int, int], ...]
    confidence: float
    listing: str = ""
    notes: tuple[str, ...] = ()
    constants: tuple[str, ...] = field(default_factory=tuple)

    @property
    def opcode_span(self) -> int:
        return self.opcode_max - self.opcode_min + 1

    def as_dict(self) -> dict[str, object]:
        return {
            "stream": self.stream_label,
            "pool": self.pool_label,
            "instructions": self.instruction_count,
            "width": self.width,
            "operands_per_instruction": self.operands_per_instruction,
            "distinct_opcodes": self.distinct_opcodes,
            "opcode_min": self.opcode_min,
            "opcode_max": self.opcode_max,
            "histogram": [{"opcode": opcode, "count": count} for opcode, count in self.histogram],
            "confidence": round(self.confidence, 3),
            "notes": list(self.notes),
            "constants": list(self.constants[:64]),
        }


def _column_stats(values: Sequence[int], stride: int) -> tuple[float, float, int]:
    """Return ``(opcode_variety, operand_variety, distinct_opcodes)``."""
    opcodes = values[0::stride]
    if not opcodes:
        return 1.0, 1.0, 0
    opcode_variety = len(set(opcodes)) / len(opcodes)
    operand_varieties: list[float] = []
    for offset in range(1, stride):
        column = values[offset::stride]
        if column:
            operand_varieties.append(len(set(column)) / len(column))
    operand_variety = (
        sum(operand_varieties) / len(operand_varieties) if operand_varieties else opcode_variety
    )
    return opcode_variety, operand_variety, len(set(opcodes))


def _pick_width(values: Sequence[int], explicit: int | None) -> tuple[int, int]:
    """Return ``(stride, operands_per_instruction)`` for an instruction stream.

    A stream is a flat array of numbers: one opcode followed by its operands.
    The right stride is the one where the first column is *much* less varied
    than the columns after it -- that is what an opcode column looks like, while
    a wrong stride just shifts the same pattern around.
    """
    if explicit and explicit >= 2:
        return explicit, max(1, explicit - 1)
    best: tuple[float, int] | None = None
    for stride in (2, 3, 4, 5, 6, 7):
        if len(values) < stride * 8:
            continue
        opcode_variety, operand_variety, distinct = _column_stats(values, stride)
        if distinct < 2:
            continue
        separation = operand_variety - opcode_variety
        span = max(values[0::stride]) - min(values[0::stride]) + 1
        small_range = 0.1 if span <= 512 else 0.0
        # Longer strides need real evidence, so they carry a small penalty.
        score = separation * 3.0 + small_range - 0.02 * (stride - 2)
        if best is None or score > best[0]:
            best = (score, stride)
    stride = best[1] if best else 1
    return stride, max(1, stride - 1)


def _listing(
    values: Sequence[int],
    *,
    stride: int,
    max_lines: int,
) -> str:
    lines: list[str] = []
    instructions: list[str] = []
    operands = max(1, stride - 1)
    for offset in range(0, len(values) - stride + 1, stride):
        opcode = values[offset]
        args = values[offset + 1 : offset + 1 + min(operands, MAX_OPERANDS)]
        text = f"{offset // stride:06d}  {opcode:>10}  " + " ".join(
            f"{value:>10}" for value in args
        )
        instructions.append(text)
        if len(instructions) == _LISTING_LINE_INSTRUCTIONS:
            lines.append("    ".join(instructions))
            instructions = []
            if len(lines) >= max_lines:
                break
    if instructions and len(lines) < max_lines:
        lines.append("    ".join(instructions))
    return "\n".join(lines)


def analyse_vm(
    tables: Sequence[VmSnapshot],
    *,
    width_hint: int | None = None,
    max_listing_lines: int = DEFAULT_LISTING_LINES,
) -> VmAnalysis | None:
    """Turn snapshots into a readable VM description, or ``None``."""
    stream = instruction_table(tables)
    if stream is None:
        return None
    values = stream.as_int_values()
    if not values:
        return None
    stride, operands = _pick_width(values, width_hint or (stream.width if stream.width > 1 else None))
    if stride < 2:
        # Not enough structure to call this an instruction stream.
        return None
    opcode_variety, operand_variety, _ = _column_stats(values, stride)
    opcode_column = values[stride - stride :: stride]
    histogram = Counter(opcode_column)
    top = tuple(histogram.most_common(16))
    distinct = len(histogram)
    span = max(opcode_column) - min(opcode_column) + 1
    repeat_ratio = 1.0 - (distinct / max(1, len(opcode_column)))
    confidence = 0.35 + 0.35 * repeat_ratio + (0.2 if span <= 512 else 0.05)
    if len(opcode_column) >= 256:
        confidence += 0.1
    confidence = round(min(0.95, confidence), 3)

    notes: list[str] = []
    if stride > 2:
        notes.append(f"each instruction occupies {stride} entries (opcode + {operands} operands)")
    else:
        notes.append("instructions are single-entry: opcode only, operands live elsewhere")
    if span > 512:
        notes.append(f"opcode values span {span} -- the first column may not be the opcode")
    if repeat_ratio < 0.5:
        notes.append("little opcode repetition: this may be data rather than an instruction stream")
    if operand_variety <= opcode_variety * 1.15:
        # A real opcode column stands out from its operands; equal variety means
        # we are probably looking at uniform data.
        notes.append(
            "operand columns are as uniform as the first column: the stride is a guess"
        )
        confidence = round(max(0.2, confidence - 0.25), 3)

    pool = constant_pool(tables)
    constants: tuple[str, ...] = ()
    if pool is not None and not pool.numeric:
        constants = tuple(str(value) for value in pool.values[:512])

    return VmAnalysis(
        stream_label=stream.label,
        pool_label=pool.label if pool is not None else "",
        instruction_count=len(values) // stride,
        width=stride,
        operands_per_instruction=operands,
        distinct_opcodes=distinct,
        opcode_min=min(opcode_column),
        opcode_max=max(opcode_column),
        histogram=top,
        confidence=confidence,
        listing=_listing(values, stride=stride, max_lines=max_listing_lines),
        notes=tuple(notes),
        constants=constants,
    )


def _escaped(text: str, limit: int = 60) -> str:
    rendered = text.replace("\\", "\\\\").replace("\n", "\\n").replace("\r", "\\r")
    if len(rendered) > limit:
        rendered = rendered[: limit - 1] + "…"
    return rendered


def render_analysis(analysis: VmAnalysis, *, max_constants: int = 48) -> str:
    """A text block for the report: what the VM looks like from the outside."""
    header = [
        "-- " + "=" * 70,
        "-- Custom VM surface recovered by running the loader",
        f"-- stream      : {analysis.stream_label}",
        f"-- instructions: {analysis.instruction_count:,} (stride {analysis.width}, "
        f"{analysis.operands_per_instruction} operand(s) each)",
        f"-- opcodes     : {analysis.distinct_opcodes} distinct in [{analysis.opcode_min}, "
        f"{analysis.opcode_max}], confidence {analysis.confidence:.2f}",
    ]
    if analysis.pool_label:
        header.append(f"-- constants   : {len(analysis.constants)} string(s) from {analysis.pool_label}")
    header.append("-- " + "=" * 70)
    for note in analysis.notes:
        header.append(f"-- note: {note}")
    body = ["-- disassembly (offset, opcode, operands)", analysis.listing]
    if analysis.constants:
        body.append("")
        body.append("-- constant pool")
        for index, value in enumerate(analysis.constants[:max_constants], start=1):
            body.append(f"--   {index:04d}  {_escaped(value)!r}")
        if len(analysis.constants) > max_constants:
            body.append(f"--   ... {len(analysis.constants) - max_constants} more")
    return "\n".join(header + body)


def summary_line(analysis: VmAnalysis) -> str:
    return (
        f"custom VM surface recovered: {analysis.instruction_count:,} instructions, "
        f"{analysis.distinct_opcodes} distinct opcodes, {len(analysis.constants)} constants"
    )
