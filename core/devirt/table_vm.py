"""Table-VM devirtualizer.

The second group -- Luraph, Wynfuscate, Prometheus' VM mode, Xen, Synapse,
Hyperion, Luau-VM style packers -- keeps the payload as its *own* instruction
format inside a table and interprets it.  There is no Lua chunk to recover, so
the honest work is:

* read the loader's dispatcher and name the opcodes it dispatches on, instead
  of printing raw numbers;
* inline the constant pool into the disassembly (``v1  ; K[12]="print"``);
* report the pool's own strings, and -- when the pool spells out a whole Lua
  source run by run -- hand that source back as the recovered payload.

The result stays a partial recovery, but it is a *readable* one: a human can
see what the VM loads, calls and branches on, and the opcode names come from
the obfuscator's own code rather than from a guess about the family.
"""

from __future__ import annotations

import re
from typing import Any, Iterable, Sequence

from core.devirt.common import pool_source

__all__ = [
    "devirtualize",
    "infer_opcode_names",
    "annotated_listing",
]

MAX_OPCODE = 4096
_BODY_WINDOW = 420

_CONDITION_HANDLER = re.compile(
    r"(?:if|elseif)\s+(?P<var>[A-Za-z_]\w*)\s*==\s*(?P<opcode>\d{1,4})\s+then",
    re.IGNORECASE,
)
_TABLE_HANDLER = re.compile(
    r"(?P<var>[A-Za-z_]\w*)\s*\[\s*(?P<opcode>\d{1,4})\s*\]\s*=\s*function",
    re.IGNORECASE,
)

# What a handler body *does* is a good enough name when nothing better exists.
# The order matters: the most specific operation wins over ``return``/``numeric``,
# which almost every handler contains.
_SEMANTICS: tuple[tuple[str, re.Pattern[str]], ...] = (
    ("arith", re.compile(r"[^\w.]\s*[+\-*/%^]\s*[^\w.]")),
    ("concat", re.compile(r"\.\.")),
    ("compare", re.compile(r"(?:~=|==|<=|>=|<|>)")),
    ("string", re.compile(r"\bstring\s*\.|:(?:sub|gsub|find|format|rep|byte|char)\b")),
    ("env", re.compile(r"\b(?:getfenv|setfenv|getupvalue|setupvalue)\b")),
    ("branch", re.compile(r"\b(?:while|repeat|goto|break)\b")),
    ("index", re.compile(r"[A-Za-z_)\]]\s*\[")),
    ("field", re.compile(r"\.[A-Za-z_]\w*")),
    ("call", re.compile(r"[A-Za-z_]\w*\s*[\(\{]")),
    ("closure", re.compile(r"\bfunction\b")),
    ("return", re.compile(r"\breturn\b")),
    ("numeric", re.compile(r"\d")),
)
_VAGUE = {"index", "field", "call", "numeric", "return"}
_TAIL_BOUNDARY = re.compile(
    r"(?m)\n[ \t]*(?:end\b|else\b|elseif\b|local\b|if\b|for\b|while\b|repeat\b|return\b"
    r"|function\b|--|[A-Za-z_]\w*[ \t]*[\[.])"
)


def _body_window(source: str, start: int) -> str:
    """The handler body starting at ``start``, cut before the next clause."""
    window = source[start : start + _BODY_WINDOW]
    boundary = _TAIL_BOUNDARY.search(window)
    return window[: boundary.start()] if boundary else window


def _handler_bodies(source: str) -> dict[int, str]:
    """Snippets of the loader's own dispatch code, keyed by opcode number.

    A dispatcher usually appears twice: once as ``if opcode == n then`` (a
    lookup) and once as ``handlers[n] = function(...)`` (the implementation).
    The implementation is what names the opcode, so it wins when the lookup
    would only say "index".
    """
    lookups: dict[int, str] = {}
    for match in _CONDITION_HANDLER.finditer(source):
        opcode = int(match.group("opcode"))
        if 0 <= opcode <= MAX_OPCODE and opcode not in lookups:
            lookups[opcode] = _body_window(source, match.end())
    implementations: dict[int, str] = {}
    for match in _TABLE_HANDLER.finditer(source):
        opcode = int(match.group("opcode"))
        if 0 <= opcode <= MAX_OPCODE and opcode not in implementations:
            implementations[opcode] = _body_window(source, match.end())
    bodies = dict(lookups)
    for opcode, body in implementations.items():
        if opcode not in bodies or _categorise(body) not in _VAGUE:
            bodies[opcode] = body
    return bodies


def _categorise(body: str) -> str:
    for name, pattern in _SEMANTICS:
        if pattern.search(body):
            return name
    return "op"


def infer_opcode_names(source: str, opcodes: Iterable[int]) -> dict[int, str]:
    """Name the opcodes a loader dispatches on, using its own handler bodies."""
    if not source:
        return {}
    bodies = _handler_bodies(source)
    if not bodies:
        return {}
    names: dict[int, str] = {}
    for opcode in sorted({int(value) for value in opcodes}):
        body = bodies.get(opcode)
        if body is None:
            continue
        names[opcode] = _categorise(body)
    return names


def _constant_renderer(pool: Any):
    if pool is None:
        return lambda value: None
    values = tuple(getattr(pool, "values", ()) or ())
    kind = getattr(pool, "kind", "")
    if kind == "numbers" or not values:
        return lambda value: None

    def render(value: int) -> str | None:
        if not 1 <= value <= len(values):
            return None
        constant = values[value - 1]
        if not isinstance(constant, str) or not constant:
            return None
        rendered = constant.replace("\\", "\\\\").replace("\n", "\\n")
        if len(rendered) > 28:
            rendered = rendered[:27] + "…"
        return f'K[{value}]="{rendered}"'

    return render


def annotated_listing(
    vm_tables: Sequence[Any],
    *,
    source: str = "",
    max_rows: int = 200,
) -> tuple[str, dict[int, str]]:
    """A disassembly with opcode names and pool constants filled in.

    Returns ``(text, opcode_names)``; ``text`` is empty when the tables hold no
    instruction stream.
    """
    from core.vm_dump import constant_pool, instruction_table
    from core.vm_recover import _pick_width

    stream = instruction_table(vm_tables)
    if stream is None:
        return "", {}
    values = stream.as_int_values()
    if not values:
        return "", {}
    # The runtime snapshot does not always know the stride (a table read by the
    # instruction hook has no width), so fall back to the same column analysis
    # the VM report uses.
    stride, _operands = _pick_width(values, stream.width if stream.width > 1 else None)
    if stride < 2:
        return "", {}
    pool = constant_pool(vm_tables)
    render_constant = _constant_renderer(pool)
    opcodes = values[0::stride]
    names = infer_opcode_names(source, opcodes)
    label = ", ".join(f"{opcode}->{name}" for opcode, name in sorted(names.items())[:12])
    lines = [
        "-- annotated disassembly (offset, opcode, operands, inlined constants)",
        f"-- stream: {stream.label}, stride {stride}"
        + (f", pool: {pool.label}" if pool is not None else ""),
    ]
    if names:
        lines.append(f"-- opcode names inferred from the loader's dispatcher: {label}")
    else:
        lines.append("-- the loader's dispatcher was not readable; opcodes stay numeric")
    rows = 0
    for offset in range(0, len(values) - stride + 1, stride):
        opcode = values[offset]
        name = names.get(opcode, f"op_{opcode}")
        operands = values[offset + 1 : offset + stride]
        rendered = [f"{value:>9}" for value in operands]
        annotations = [
            text for text in (render_constant(value) for value in operands) if text
        ]
        row = f"{offset // stride:06d}  {name:<9} " + " ".join(rendered)
        if annotations:
            row += "   ; " + ", ".join(annotations)
        lines.append(row)
        rows += 1
        if rows >= max_rows:
            lines.append(f"-- ... {len(values) // stride - rows} more instruction(s)")
            break
    return "\n".join(lines), names


def devirtualize(
    source: str,
    *,
    vm_tables: Sequence[Any] | None = None,
    vm_analysis: Any | None = None,
    family: str = "generic",
) -> dict[str, Any] | None:
    """Describe (and where possible lift) a custom table VM."""
    if not vm_tables and vm_analysis is None:
        return None
    notes: list[str] = []
    recovered: str | None = None
    confidence = 0.4
    if vm_tables:
        from core.vm_dump import constant_pool

        pool = constant_pool(vm_tables)
        spelled = pool_source(pool) if pool is not None else None
        if spelled:
            recovered = spelled
            confidence = 0.6
            notes.append(
                "the VM's constant pool spells out a complete Lua source; it was reassembled"
            )
    listing, names = ("", {})
    if vm_tables:
        listing, names = annotated_listing(vm_tables, source=source)
    if names:
        notes.append(
            "opcode names were read from the loader's own dispatcher "
            f"({len(names)} of them matched a handler)"
        )
    if recovered:
        notes.append(
            "the bytecode semantics of this VM were not lifted; the payload above came from its pool"
        )
    else:
        notes.append(
            "the VM ran inside the portable backend and its tables were read; lifting the "
            "opcodes to source needs a per-family opcode map"
        )
    return {
        "source": recovered,
        "bytecode": None,
        "method": "custom VM introspection (annotated disassembly)",
        "notes": tuple(notes),
        "confidence": confidence if recovered else 0.35,
        "partial": True,
        "listing": listing,
        "opcode_names": names,
    }
