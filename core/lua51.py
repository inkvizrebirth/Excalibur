"""Lua 5.1 bytecode reader, disassembler and readable-source recovery.

Obfuscators such as WeAreDevs v2.4, IronBrew2/3, PSU v1.0, Nexus v2.0,
AztupBrew and MoonSec V2 all keep the real script as Lua 5.1 bytecode behind a
string/array decoder.  Once that bytecode is recovered it still looks like
garbage to a human, so this module turns it into structured pseudocode:

* a strict reader for the standard ``\\x1bLua`` 5.1 container,
* a full 38-opcode disassembler with constant-pool rendering,
* a control-flow recovery pass (if/else, numeric for, generic for, while,
  repeat, break) that emits indented Lua with a symbolic register model.

Recovered code is an approximation: names, comments and some idioms cannot be
restored from stripped bytecode, and the output marks that boundary instead of
pretending to be a perfect decompilation.
"""

from __future__ import annotations

import re
import struct
from dataclasses import dataclass, field
from typing import Iterator, Sequence

__all__ = [
    "BytecodeError",
    "Constant",
    "Proto",
    "Chunk",
    "read_chunk",
    "is_lua51_bytecode",
    "looks_like_luau_bytecode",
    "disassemble",
    "decompile",
    "Lua51Scanner",
]

LUA51_SIGNATURE = b"\x1bLua"
LUAU_SIGNATURE_PREFIXES = (b"\x01\x02\x03", b"RSB1", b"RSB2")

#: Instructions one prototype may cost the structured walk before the lifter
#: stops structuring and says so in the output.  An obfuscated jump table has
#: overlapping branch layouts, and descending into them recursively used to
#: blow up combinatorially: a 112-instruction prototype took minutes of CPU and
#: looked like a hang.  The cap keeps lifting predictable.
_WALK_STEP_BUDGET = 200_000


class BytecodeError(ValueError):
    """The data is not a supported Lua 5.1 bytecode chunk."""


# ---------------------------------------------------------------------------
# Reader
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class Constant:
    kind: str  # nil | boolean | number | string
    value: object = None

    def render(self) -> str:
        if self.kind == "nil":
            return "nil"
        if self.kind == "boolean":
            return "true" if self.value else "false"
        if self.kind == "number":
            number = float(self.value)  # type: ignore[arg-type]
            if number == int(number) and abs(number) < 1e15:
                return str(int(number))
            return f"{number:.14g}"
        if self.kind == "string":
            return _quote(str(self.value))
        return "?"


def _quote(value: str) -> str:
    escaped = (
        value.replace("\\", "\\\\")
        .replace('"', '\\"')
        .replace("\r", "\\r")
        .replace("\n", "\\n")
        .replace("\t", "\\t")
    )
    # Keep the escaped text printable.
    escaped = "".join(character if character.isprintable() else f"\\{ord(character):03d}" for character in escaped)
    return f'"{escaped}"'


@dataclass
class Proto:
    source: str | None
    line_defined: int
    last_line_defined: int
    num_params: int
    is_vararg: int
    max_stack_size: int
    code: bytes
    constants: list[Constant]
    protos: list["Proto"]
    line_info: list[int]
    upvalue_names: list[str]
    upvalue_count: int = 0
    index: int = 0
    parent: "Proto | None" = None

    @property
    def instructions(self) -> Iterator["Instruction"]:
        for offset in range(0, len(self.code) - 3, 4):
            yield Instruction(struct.unpack_from("<I", self.code, offset)[0], offset)

    def constant_text(self, index: int) -> str:
        if not 0 <= index < len(self.constants):
            return f"K{index}"
        return self.constants[index].render()

    @property
    def name(self) -> str:
        if self.line_defined:
            return f"function@{self.line_defined}"
        return f"proto_{self.index}"

    @property
    def accepts_varargs(self) -> bool:
        return bool(self.is_vararg & 2)


@dataclass
class Chunk:
    version: int
    root: Proto
    proto_count: int = 0

    def protos(self) -> Iterator[Proto]:
        stack = [self.root]
        while stack:
            current = stack.pop()
            yield current
            stack.extend(reversed(current.protos))


class _Reader:
    def __init__(
        self,
        data: bytes,
        *,
        int_size: int = 4,
        size_t_size: int = 4,
        number_size: int = 8,
    ):
        self.data = data
        self.position = 0
        self.proto_index = 0
        self.int_size = int_size
        self.size_t_size = size_t_size
        self.number_size = number_size

    def bytes(self, count: int) -> bytes:
        if self.position + count > len(self.data):
            raise BytecodeError("bytecode ended earlier than its headers claimed")
        result = self.data[self.position : self.position + count]
        self.position += count
        return result

    def byte(self) -> int:
        return self.bytes(1)[0]

    def int(self) -> int:
        if self.int_size == 8:
            return struct.unpack("<q", self.bytes(8))[0]
        return struct.unpack("<i", self.bytes(self.int_size))[0]

    def size(self) -> int:
        if self.size_t_size == 8:
            return struct.unpack("<Q", self.bytes(8))[0]
        return struct.unpack("<I", self.bytes(self.size_t_size))[0]

    def number(self) -> float:
        if self.number_size == 4:
            return float(struct.unpack("<f", self.bytes(4))[0])
        return struct.unpack("<d", self.bytes(self.number_size))[0]

    def string(self) -> str | None:
        length = self.size()
        if length == 0:
            return None
        raw = self.bytes(length)
        return raw.rstrip(b"\x00").decode("utf-8", "replace")


def read_chunk(data: bytes) -> Chunk:
    """Parse a standard Lua 5.1 binary chunk."""
    if isinstance(data, str):
        data = data.encode("latin-1")
    if not data.startswith(LUA51_SIGNATURE):
        raise BytecodeError("not a Lua 5.1 bytecode chunk (missing \\x1bLua signature)")
    reader = _Reader(data)
    reader.bytes(4)
    version = reader.byte()
    if version != 0x51:
        raise BytecodeError(f"unsupported Lua bytecode version 0x{version:02x} (only 5.1 is supported)")
    reader.byte()  # format
    endianness = reader.byte()
    if endianness != 1:
        raise BytecodeError("big-endian Lua bytecode is not supported")
    int_size = reader.byte()
    size_t_size = reader.byte()
    instruction_size = reader.byte()
    number_size = reader.byte()
    reader.byte()  # integral (integer) number flag
    if int_size not in {4, 8} or size_t_size not in {4, 8} or instruction_size != 4 or number_size not in {4, 8}:
        raise BytecodeError(
            "unusual Lua 5.1 platform sizes "
            f"(int={int_size}, size_t={size_t_size}, instruction={instruction_size}, number={number_size})"
        )
    reader.int_size = int_size
    reader.size_t_size = size_t_size
    reader.number_size = number_size
    root = _read_proto(reader, None)
    return Chunk(version=version, root=root, proto_count=reader.proto_index)


def _read_proto(reader: _Reader, parent: Proto | None) -> Proto:
    source = reader.string()
    line_defined = reader.int()
    last_line_defined = reader.int()
    upvalue_count_declared = reader.byte()  # nups (Lua 5.1 keeps this in the header)
    num_params = reader.byte()
    is_vararg = reader.byte()
    max_stack_size = reader.byte()

    code_size = reader.int()
    if code_size < 0 or code_size > 8_000_000:
        raise BytecodeError("implausible instruction count in the bytecode chunk")
    code = reader.bytes(code_size * 4)

    constant_count = reader.int()
    if constant_count < 0 or constant_count > 2_000_000:
        raise BytecodeError("implausible constant count in the bytecode chunk")
    constants: list[Constant] = []
    for _ in range(constant_count):
        kind = reader.byte()
        if kind == 0:
            constants.append(Constant("nil"))
        elif kind == 1:
            constants.append(Constant("boolean", reader.byte() != 0))
        elif kind == 3:
            constants.append(Constant("number", reader.number()))
        elif kind == 4:
            constants.append(Constant("string", reader.string() or ""))
        else:
            raise BytecodeError(f"unknown constant type {kind}")

    proto_count = reader.int()
    if proto_count < 0 or proto_count > 500_000:
        raise BytecodeError("implausible nested prototype count")
    proto = Proto(
        source=source,
        upvalue_count=upvalue_count_declared,
        line_defined=line_defined,
        last_line_defined=last_line_defined,
        num_params=num_params,
        is_vararg=int(is_vararg),
        max_stack_size=max_stack_size,
        code=code,
        constants=constants,
        protos=[],
        line_info=[],
        upvalue_names=[],
        index=reader.proto_index,
        parent=parent,
    )
    reader.proto_index += 1
    for _ in range(proto_count):
        proto.protos.append(_read_proto(reader, proto))

    line_info_count = reader.int()
    if 0 < line_info_count <= 8_000_000:
        proto.line_info = list(struct.unpack(f"<{line_info_count}i", reader.bytes(line_info_count * 4)))
    else:
        reader.bytes(max(0, line_info_count) * 4)

    local_count = reader.int()
    if 0 < local_count <= 1_000_000:
        for _ in range(local_count):
            reader.string()
            reader.int()
            reader.int()
    upvalue_count = reader.int()
    if 0 < upvalue_count <= 100_000:
        proto.upvalue_names = [reader.string() or "" for _ in range(upvalue_count)]
    return proto


def is_lua51_bytecode(data: bytes | str) -> bool:
    if isinstance(data, str):
        data = data.encode("latin-1", "ignore")
    return bytes(data[:4]) == LUA51_SIGNATURE


def looks_like_luau_bytecode(data: bytes | str) -> bool:
    if isinstance(data, str):
        data = data.encode("latin-1", "ignore")
    head = bytes(data[:4])
    return any(head.startswith(prefix) for prefix in LUAU_SIGNATURE_PREFIXES) or head.startswith(b"\x1bLua")


# ---------------------------------------------------------------------------
# Disassembler
# ---------------------------------------------------------------------------

OPCODE_NAMES = (
    "MOVE", "LOADK", "LOADBOOL", "LOADNIL", "GETUPVAL", "GETGLOBAL", "GETTABLE",
    "SETGLOBAL", "SETUPVAL", "SETTABLE", "NEWTABLE", "SELF", "ADD", "SUB", "MUL",
    "DIV", "MOD", "POW", "UNM", "NOT", "LEN", "CONCAT", "JMP", "EQ", "LT", "LE",
    "TEST", "TESTSET", "CALL", "TAILCALL", "RETURN", "FORLOOP", "FORPREP",
    "TFORLOOP", "SETLIST", "CLOSE", "CLOSURE", "VARARG",
)
OPCODE_INDEX = {name: index for index, name in enumerate(OPCODE_NAMES)}

# Opcodes whose C argument is a constant-or-register (RK) operand.
_RK_OPCODES = {
    "GETTABLE", "SETTABLE", "SELF", "ADD", "SUB", "MUL", "DIV", "MOD", "POW",
    "EQ", "LT", "LE",
}


@dataclass(frozen=True)
class Instruction:
    raw: int
    offset: int

    @property
    def op(self) -> int:
        return self.raw & 0x3F

    @property
    def name(self) -> str:
        return OPCODE_NAMES[self.op] if self.op < len(OPCODE_NAMES) else f"OP_{self.op}"

    @property
    def a(self) -> int:
        return (self.raw >> 6) & 0xFF

    @property
    def c(self) -> int:
        return (self.raw >> 14) & 0x1FF

    @property
    def b(self) -> int:
        return (self.raw >> 23) & 0x1FF

    @property
    def bx(self) -> int:
        return self.raw >> 14

    @property
    def sbx(self) -> int:
        return self.bx - 131071

    @property
    def is_k(self) -> bool:
        return self.bx >= 256

    def text(self, proto: Proto) -> str:
        name = self.name
        if name == "LOADK":
            return f"LOADK {self._r(self.a)} {proto.constant_text(self.bx)}"
        if name == "GETGLOBAL":
            return f"GETGLOBAL {self._r(self.a)} {proto.constant_text(self.bx)}"
        if name == "SETGLOBAL":
            return f"SETGLOBAL {self._r(self.a)} {proto.constant_text(self.bx)}"
        if name in {"JMP", "FORLOOP", "FORPREP"}:
            return f"{name} {self._r(self.a)} -> {self.offset + 4 + self.sbx * 4}"
        if name == "CLOSURE":
            return f"CLOSURE {self._r(self.a)} proto_{self.bx}"
        if name in _RK_OPCODES:
            return f"{name} {self._r(self.a)} {self._rk(proto, self.b)} {self._rk(proto, self.c)}"
        if name in {"RETURN", "CALL", "TAILCALL", "SETLIST"}:
            return f"{name} {self._r(self.a)} b={self.b} c={self.c}"
        return f"{name} {self._r(self.a)} b={self.b} c={self.c}"

    def _r(self, register: int) -> str:
        return f"R{register}"

    def _rk(self, proto: Proto, value: int) -> str:
        if value & 0x100:
            return f"K[{proto.constant_text(value & 0xFF)}]"
        return f"R{value}"


def disassemble(proto: Proto, *, limit: int | None = None) -> str:
    lines: list[str] = []
    for index, instruction in enumerate(proto.instructions):
        if limit is not None and index >= limit:
            lines.append("-- ...")
            break
        lines.append(f"{instruction.offset // 4:6d}  {instruction.text(proto)}")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Decompiler
# ---------------------------------------------------------------------------

_MAX_EXPRESSION_LENGTH = 120


class _LoopInfo:
    """A recovered loop region."""

    def __init__(
        self,
        *,
        kind: str,
        header: int,
        body_start: int,
        body_end: int,
        tail: int,
        exit_offset: int,
        condition: str | None = None,
        for_clause: str | None = None,
    ):
        self.kind = kind  # while | while-true | repeat | numeric-for | generic-for
        self.header = header
        self.body_start = body_start
        self.body_end = body_end
        self.tail = tail
        self.exit_offset = exit_offset
        self.condition = condition
        self.for_clause = for_clause


_BLOCK_TERMINATORS = re.compile(r"^(end\b|else\b|elseif\b|until\b|when\b|}\b|\))")


class _FunctionLifter:
    """Turn one prototype into indented, structured pseudocode.

    The lifter keeps a symbolic register model: a register that is written once
    with a side-effect-free expression is inlined, while accumulators and loop
    variables keep their own name so the recovered code stays correct instead
    of collapsing into nonsense like ``0 + 1``.
    """

    def __init__(self, proto: Proto):
        self.proto = proto
        self.instructions: list[Instruction] = list(proto.instructions)
        self.index_by_offset: dict[int, int] = {
            instruction.offset: index for index, instruction in enumerate(self.instructions)
        }
        self.lines: list[str] = []
        self._return_indent: int | None = None
        self.indent = 0
        self.registers: dict[int, str] = {}
        self.write_counts: dict[int, int] = {}
        self.stable: dict[int, bool] = {}
        self.parameters = {index: f"p{index + 1}" for index in range(proto.num_params)}
        self.loops: dict[int, _LoopInfo] = {}
        self._active_loops: set[int] = set()
        # A structured walk that re-enters the region it is already inside can
        # never terminate: an overlapping branch layout (obfuscated jump table)
        # makes ``_branch_layout`` produce ranges that nest back into the
        # current one.  The set below remembers the active regions, and the
        # step budget is the backstop for regions that are merely enormous.
        self._active_ranges: set[tuple[int, int, int]] = set()
        self.walk_budget = _WALK_STEP_BUDGET
        self.budget_exhausted = False
        self._count_writes()
        self._find_loops()

    # ------------------------------------------------------------------
    # Analysis
    # ------------------------------------------------------------------
    def _count_writes(self) -> None:
        for instruction in self.instructions:
            target = self._write_register(instruction)
            if target is not None:
                self.write_counts[target] = self.write_counts.get(target, 0) + 1

    @staticmethod
    def _write_register(instruction: Instruction) -> int | None:
        name = instruction.name
        if name in {"MOVE", "LOADK", "LOADBOOL", "LOADNIL", "GETUPVAL", "GETGLOBAL", "GETTABLE",
                    "NEWTABLE", "SELF", "ADD", "SUB", "MUL", "DIV", "MOD", "POW", "UNM", "NOT",
                    "LEN", "CONCAT", "VARARG", "CLOSURE", "TESTSET"}:
            return instruction.a
        if name == "CALL":
            return instruction.a if instruction.c != 1 else None
        return None

    def _index(self, offset: int) -> int | None:
        return self.index_by_offset.get(offset)

    def _find_loops(self) -> None:
        generic_tails: set[int] = set()
        for index, instruction in enumerate(self.instructions):
            if instruction.name != "JMP" or instruction.sbx <= 0:
                continue
            target_index = self._index(instruction.offset + 4 + instruction.sbx * 4)
            if target_index is None or not 0 <= target_index < len(self.instructions):
                continue
            if self.instructions[target_index].name != "TFORLOOP":
                continue
            generic_tails.add(target_index + 1)
            self._register_generic_for(index, target_index)

        for index, instruction in enumerate(self.instructions):
            name = instruction.name
            if name == "JMP" and instruction.sbx < 0:
                if index in generic_tails:
                    continue
                target = instruction.offset + 4 + instruction.sbx * 4
                self._register_loop(target, tail_index=index, conditional=False)
            elif name in {"TEST", "TESTSET", "EQ", "LT", "LE"}:
                following = self.instructions[index + 1] if index + 1 < len(self.instructions) else None
                if following is not None and following.name == "JMP" and following.sbx < 0:
                    target = following.offset + 4 + following.sbx * 4
                    self._register_loop(target, tail_index=index + 1, conditional=True)
            elif name == "FORPREP":
                loop_index = index + 1 + instruction.sbx
                if 0 <= loop_index < len(self.instructions):
                    loop = self.instructions[loop_index]
                    if loop.name == "FORLOOP":
                        self.loops[instruction.offset] = _LoopInfo(
                            kind="numeric-for",
                            header=instruction.offset,
                            body_start=instruction.offset + 4,
                            body_end=loop.offset,
                            tail=loop.offset,
                            exit_offset=loop.offset + 4 + loop.sbx * 4,
                        )


    def _register_generic_for(self, setup_index: int, loop_index: int) -> None:
        """Recover a Lua 5.1 generic-for loop.

        Lua 5.1 stores no jump inside TFORLOOP: the setup jump targets it, the
        body follows the setup jump, and the back edge is the instruction after
        TFORLOOP.
        """
        setup = self.instructions[setup_index]
        loop_instruction = self.instructions[loop_index]
        body_start = setup.offset + 4
        tail_index = loop_index + 1
        tail = (
            self.instructions[tail_index].offset
            if tail_index < len(self.instructions)
            else loop_instruction.offset
        )
        exit_offset = tail + 4
        if tail_index < len(self.instructions):
            back = self.instructions[tail_index]
            if back.name == "JMP" and back.sbx < 0:
                exit_offset = back.offset + 4
        self.loops[setup.offset] = _LoopInfo(
            kind="generic-for",
            header=setup.offset,
            body_start=body_start,
            body_end=loop_instruction.offset,
            tail=tail,
            exit_offset=exit_offset,
        )

    def _register_loop(
        self,
        header_offset: int,
        *,
        tail_index: int,
        conditional: bool,
    ) -> None:
        if header_offset not in self.index_by_offset:
            return
        if header_offset >= self.instructions[tail_index].offset:
            return
        tail = self.instructions[tail_index]
        exit_offset = tail.offset + 4
        if conditional:
            # repeat ... until cond: the test sits at the tail of the region.
            condition_index = self._index(tail.offset - 4)
            start = self._index(header_offset)
            if start is None or condition_index is None:
                return
            self.loops.setdefault(
                header_offset,
                _LoopInfo(
                    kind="repeat",
                    header=header_offset,
                    body_start=header_offset,
                    body_end=tail.offset - 4,
                    tail=tail.offset,
                    exit_offset=exit_offset,
                ),
            )
            return

        # Unconditional back edge: a while loop, or an infinite loop.
        exit_guess = tail.offset + 4
        body_start = header_offset
        for candidate_index in range(self._index(header_offset) or 0, tail_index):
            candidate = self.instructions[candidate_index]
            if candidate.name in {"TEST", "TESTSET", "EQ", "LT", "LE"}:
                following = (
                    self.instructions[candidate_index + 1]
                    if candidate_index + 1 < len(self.instructions)
                    else None
                )
                if following is not None and following.name == "JMP" and following.sbx > 0:
                    jump_target = following.offset + 4 + following.sbx * 4
                    if jump_target == exit_guess:
                        condition_index = candidate_index
                        condition_text = self._condition_text(condition_index)
                        self.loops.setdefault(
                            header_offset,
                            _LoopInfo(
                                kind="while",
                                header=header_offset,
                                body_start=following.offset + 4,
                                body_end=tail.offset,
                                tail=tail.offset,
                                exit_offset=exit_guess,
                                condition=condition_text,
                            ),
                        )
                        return
                    if jump_target > exit_guess:
                        exit_guess = jump_target
        self.loops.setdefault(
            header_offset,
            _LoopInfo(
                kind="while-true",
                header=header_offset,
                body_start=body_start,
                body_end=tail.offset,
                tail=tail.offset,
                exit_offset=exit_guess,
            ),
        )

    # ------------------------------------------------------------------
    # Emission helpers
    # ------------------------------------------------------------------
    def _emit(self, text: str = "") -> None:
        stripped = text.strip()
        if stripped and not stripped.startswith("--"):
            if self._return_indent is not None:
                if self.indent == self._return_indent:
                    if stripped.startswith("return"):
                        # A fallthrough RETURN after an explicit one adds nothing.
                        return
                    if not _BLOCK_TERMINATORS.match(stripped):
                        # Statements after a return in the same block are dead.
                        return
                self._return_indent = None
            if stripped.startswith("return"):
                self._return_indent = self.indent
        elif not stripped:
            self._return_indent = None
        self.lines.append(("\t" * self.indent + text) if text else "")

    def _register_name(self, index: int) -> str:
        if index in self.parameters:
            return self.parameters[index]
        return f"v{index}"

    def _is_stable(self, register: int) -> bool:
        """True when the register can be inlined without changing behaviour."""
        if register in self.parameters:
            return False
        if self.write_counts.get(register, 0) != 1:
            return False
        return self.stable.get(register, False)

    def _expression(self, register: int) -> str:
        if self._is_stable(register):
            return self.registers[register]
        return self._register_name(register)

    def _assign(self, register: int, expression: str, *, stable: bool) -> None:
        self.registers[register] = expression
        self.stable[register] = stable
        if self.write_counts.get(register, 0) == 1 and stable:
            return  # inlined at use sites, no statement needed
        self._emit(f"{self._register_name(register)} = {expression}")

    def _value(self, instruction: Instruction, operand: int) -> str:
        if operand & 0x100:
            return self.proto.constant_text(operand & 0xFF)
        return self._expression(operand)

    def _rk_index(self, operand: int) -> int:
        return operand & 0xFF

    # ------------------------------------------------------------------
    # Control flow text helpers
    # ------------------------------------------------------------------
    def _condition_text(self, index: int) -> str:
        from core.lua51 import _INVERTED_COMPARISONS, _COMPARISONS  # type: ignore

        instruction = self.instructions[index]
        name = instruction.name
        if name in _COMPARISONS:
            left = self._value(instruction, instruction.b)
            right = self._value(instruction, instruction.c)
            operator = _COMPARISONS[name]
            # Lua 5.1: "if ((RK(B) op RK(C)) ~= A) then pc++" - A=0 keeps the
            # comparison as written, A=1 is its negation.
            condition = f"{left} {operator} {right}"
            return condition if instruction.a == 0 else f"not ({condition})"
        if name == "TESTSET":
            return self._expression(instruction.b) if instruction.c == 1 else f"not {self._expression(instruction.b)}"
        value = self._expression(instruction.a)
        return value if instruction.c == 1 else f"not {value}"

    def _skip_past_condition(self, index: int) -> int:
        return index + 2

    # ------------------------------------------------------------------
    # Main walk
    # ------------------------------------------------------------------
    def lift(self, *, as_chunk: bool = False) -> str:
        parameters = list(self.parameters.values())
        if self.proto.accepts_varargs:
            parameters.append("...")
        # The main prototype of a chunk has no parameters; emitting its body
        # directly keeps the result valid Luau instead of a stray
        # `function(...) ... end` block.
        # A chunk's body can be printed as plain statements; a dumped function
        # with named parameters needs the wrapper to stay valid Luau. Varargs
        # are legal at the top level, so they do not force a wrapper.
        named_parameters = [item for item in parameters if item != "..."]
        bare_chunk = bool(as_chunk and not named_parameters and not self.proto.upvalue_count)
        named_chunk = bool(as_chunk and named_parameters and not self.proto.upvalue_count)
        self._emit(f"-- {self.proto.name}: {len(self.instructions)} instructions, "
                   f"stack {self.proto.max_stack_size}, {self.proto.upvalue_count} upvalue(s)")
        if named_chunk:
            # A dumped function keeps its parameter list; binding it to a name
            # makes the listing valid Luau instead of a bare function statement.
            self._emit(f"local recovered_chunk = function({', '.join(parameters)})")
        elif not bare_chunk:
            self._emit(f"function({', '.join(parameters)})")
        self.indent = 0 if bare_chunk else 1
        for index in range(self.proto.num_params, self.proto.max_stack_size, 1):
            self.registers.pop(index, None)
        self._walk(0, len(self.instructions), loop=None)
        if not bare_chunk:
            self.indent = 0
            self._emit("end")
        if named_chunk:
            self._emit("")
            self._emit("-- call recovered_chunk(...) with the arguments the original received")
        return "\n".join(self.lines)

    def _walk(self, start: int, end: int, loop: _LoopInfo | None) -> None:
        if not 0 <= start < end:
            return
        key = (start, end, loop.header if loop is not None else -1)
        if key in self._active_ranges:
            # The same region is already being lifted further up the stack: the
            # jump table overlaps, so descending again would never terminate.
            self._emit(f"-- region L{self.instructions[start].offset // 4}-"
                       f"L{self.instructions[end - 1].offset // 4} is part of an "
                       f"overlapping branch layout (not repeated)")
            return
        self._active_ranges.add(key)
        try:
            self._walk_region(start, end, loop)
        finally:
            self._active_ranges.discard(key)

    def _walk_region(self, start: int, end: int, loop: _LoopInfo | None) -> None:
        index = start
        while 0 <= index < end:
            self.walk_budget -= 1
            if self.walk_budget <= 0:
                if not self.budget_exhausted:
                    self.budget_exhausted = True
                    remaining = len(self.instructions) - index
                    self._emit(f"-- lifting stopped at the step budget with "
                               f"{remaining} instruction(s) of this prototype left: "
                               f"the jump table is too irregular to structure")
                return
            instruction = self.instructions[index]
            offset = instruction.offset
            name = instruction.name

            loop_here = self.loops.get(offset)
            if loop_here is loop or (loop_here is not None and offset in self._active_loops):
                loop_here = None
            if loop_here is not None and loop_here.kind in {"numeric-for", "generic-for"}:
                self._emit_for_loop(loop_here)
                body_start = self._index(loop_here.body_start)
                body_end = self._index(loop_here.body_end)
                if body_start is not None and body_end is not None and body_start < body_end:
                    self._active_loops.add(loop_here.header)
                    self.indent += 1
                    self._walk(body_start, body_end, loop=loop_here)
                    self.indent -= 1
                    self._active_loops.discard(loop_here.header)
                self._emit("end")
                after = self._index(loop_here.tail)
                index = (after + 1) if after is not None else end
                continue

            if loop_here is not None and loop_here.kind in {"while", "while-true", "repeat"}:
                self._emit_loop(loop_here)
                body_start = self._index(loop_here.body_start)
                body_end = self._index(loop_here.body_end)
                if body_start is not None and body_end is not None and body_start < body_end:
                    self._active_loops.add(loop_here.header)
                    self.indent += 1
                    self._walk(body_start, body_end, loop=loop_here)
                    self.indent -= 1
                    self._active_loops.discard(loop_here.header)
                if loop_here.kind == "repeat":
                    condition = self._condition_text(self._index(loop_here.body_end) or index)
                    self._emit(f"until {self._unwrap_condition(condition)}")
                else:
                    self._emit("end")
                after = self._index(loop_here.tail)
                index = (after + 1) if after is not None else end
                continue

            if name in {"TEST", "TESTSET", "EQ", "LT", "LE"}:
                following = self.instructions[index + 1] if index + 1 < len(self.instructions) else None
                if following is not None and following.name == "JMP":
                    target = following.offset + 4 + following.sbx * 4
                    if target < offset:
                        # Back edge of an enclosing repeat loop.
                        if loop is not None and target == loop.header:
                            return
                        self._emit(f"-- loop back to L{target // 4}")
                        index += 2
                        continue
                    condition = self._unwrap_condition(self._condition_text(index))
                    if loop is not None and target == loop.exit_offset:
                        self._emit(f"if {condition} then break end")
                        index += 2
                        continue
                    target_index = self._index(target)
                    if target_index is None:
                        self._emit(f"-- conditional jump past the end of the function")
                        index += 2
                        continue
                    branches = self._branch_layout(index + 2, target_index, target)
                    self._emit(f"if {condition} then")
                    self.indent += 1
                    self._walk(branches[0], branches[1], loop=loop)
                    self.indent -= 1
                    if branches[2] is not None:
                        self._emit("else")
                        self.indent += 1
                        self._walk(branches[2], branches[3], loop=loop)
                        self.indent -= 1
                        index = branches[3]
                    else:
                        index = target_index
                    self._emit("end")
                    continue
                self._emit(f"-- {instruction.text(self.proto)}")
                index += 1
                continue

            if name == "JMP":
                target = offset + 4 + instruction.sbx * 4
                if instruction.sbx < 0:
                    if loop is not None and target == loop.header:
                        return
                    self._emit(f"-- jump back to L{target // 4}")
                    index += 1
                    continue
                if loop is not None and target == loop.exit_offset:
                    self._emit("break")
                    index += 1
                    continue
                self._emit(f"-- jump to L{target // 4}")
                index += 1
                continue

            if name == "FORPREP" or name == "FORLOOP":
                if loop is not None and offset == loop.tail:
                    return
                self._emit(f"-- {instruction.text(self.proto)}")
                index += 1
                continue

            if name == "TFORLOOP":
                if loop is not None and offset == loop.tail:
                    return
                self._emit("-- generic for loop")
                index += 1
                continue

            if name == "RETURN":
                values: list[str] = []
                if instruction.b == 0:
                    values = [self._expression(instruction.a), "..."]
                elif instruction.b > 1:
                    values = [
                        self._expression(register)
                        for register in range(instruction.a, instruction.a + instruction.b - 1)
                    ]
                self._emit("return" + (" " + ", ".join(values) if values else ""))
                index += 1
                continue

            if name in {"CALL", "TAILCALL"}:
                index = self._emit_call(index, instruction)
                continue

            if name == "CLOSURE":
                nested_index = instruction.bx
                if 0 <= nested_index < len(self.proto.protos):
                    nested = self.proto.protos[nested_index]
                    nested_lines = _FunctionLifter(nested).lift().splitlines()
                    header_line = next(
                        (line for line in nested_lines if line.strip().startswith("function(")),
                        "function(...)",
                    )
                    self._emit(f"{self._register_name(instruction.a)} = {header_line.strip()}")
                    body_start = nested_lines.index(header_line) + 1
                    for line in nested_lines[body_start:-1]:
                        self._emit(line.lstrip("\t"))
                    self._emit("end")
                    self.registers[instruction.a] = self._register_name(instruction.a)
                    self.stable[instruction.a] = False
                else:
                    self._emit(f"{self._register_name(instruction.a)} = nil -- missing prototype")
                index += 1
                continue

            if name == "SETGLOBAL":
                self._emit(f"{self.proto.constant_text(instruction.bx)} = {self._expression(instruction.a)}")
                index += 1
                continue

            if name == "SETUPVAL":
                upvalue = self._upvalue(instruction.b)
                self._emit(f"{upvalue} = {self._expression(instruction.a)}")
                index += 1
                continue

            if name == "SETTABLE":
                table = self._expression(instruction.a)
                key = self._value(instruction, instruction.b)
                value = self._value(instruction, instruction.c)
                self._emit(self._table_set_text(table, key, value))
                index += 1
                continue

            if name == "SETLIST":
                table = self._expression(instruction.a)
                count = instruction.b
                self._emit(f"-- {table} gets a list of {count} value(s) (SETLIST)")
                index += 1
                continue

            if name == "CLOSE":
                index += 1
                continue

            # Plain expression instructions.
            self._emit_expression(instruction)
            index += 1

    # ------------------------------------------------------------------
    # Statements
    # ------------------------------------------------------------------
    def _unwrap_condition(self, condition: str) -> str:
        if condition.startswith("not (") and condition.endswith(")"):
            inner = condition[5:-1]
            for operator, inverted in ((" == ", " ~= "), (" ~= ", " == "), (" < ", " >= "), (" <= ", " > ")):
                if operator in inner:
                    return inner.replace(operator, inverted, 1)
        return condition

    def _table_set_text(self, table: str, key: str, value: str) -> str:
        if key.startswith('"') and key.endswith('"'):
            name = key[1:-1]
            if name.isidentifier():
                return f"{table}.{name} = {value}"
        return f"{table}[{key}] = {value}"

    def _upvalue(self, index: int) -> str:
        names = self.proto.upvalue_names
        if 0 <= index < len(names) and names[index]:
            return names[index]
        return f"up{index + 1}"

    def _branch_layout(
        self,
        start: int,
        target_index: int,
        target_offset: int,
    ) -> tuple[int, int, int | None, int]:
        """Return (then_start, then_end, else_start, else_end) for an if statement.

        Lua compiles ``if c then A else B end`` as the condition, a jump to the
        else label, ``A``, a jump past ``B``, ``B`` and the shared exit.  A
        then-branch therefore ends one instruction before the else label.
        """
        then_end = target_index
        else_start: int | None = None
        else_end = target_index
        if target_index - 1 > start:
            candidate = self.instructions[target_index - 1]
            if candidate.name == "JMP" and candidate.sbx > 0:
                else_target = candidate.offset + 4 + candidate.sbx * 4
                else_index = self._index(else_target)
                if else_index is not None and else_target > target_offset and else_index > start:
                    then_end = target_index - 1
                    else_start = target_index
                    else_end = else_index
        return (start, then_end, else_start, else_end)

    def _emit_loop(self, loop: _LoopInfo) -> None:
        if loop.kind == "while":
            self._emit(f"while {self._unwrap_condition(loop.condition or 'true')} do")
        elif loop.kind == "repeat":
            self._emit("repeat")
        else:
            self._emit("while true do")

    def _emit_for_loop(self, loop: _LoopInfo) -> None:
        if loop.kind == "numeric-for":
            start_index = self._index(loop.header) or 0
            instruction = self.instructions[start_index]
            register = instruction.a
            start = self.registers.get(register, "?")
            limit = self.registers.get(register + 1, "?")
            step = self.registers.get(register + 2, "1")
            self._emit(
                f"for {self._register_name(register + 3)} = {start}, {limit}, {step} do"
            )
            for slot in range(register, register + 4):
                self.registers.pop(slot, None)
                self.stable[slot] = False
            return
        # generic for: iterator state lives in registers A, A+1, A+2
        tail_index = self._index(loop.body_end) or 0
        instruction = self.instructions[tail_index]
        function = self.registers.get(instruction.a, self._register_name(instruction.a))
        state = self.registers.get(instruction.a + 1, self._register_name(instruction.a + 1))
        control = self.registers.get(instruction.a + 2, self._register_name(instruction.a + 2))
        names = [self._register_name(instruction.a + 3 + index) for index in range(max(1, instruction.c))]
        looks_like_call = "(" in function and function.endswith(")")
        if looks_like_call:
            target = function
        elif function in {"next", "pairs"}:
            target = f"{function}({state})"
        else:
            target = f"{function}({state}, {control})"
        self._emit(f"for {', '.join(names)} in {target} do")

    def _emit_call(self, index: int, instruction: Instruction) -> int:
        register = instruction.a
        arguments: list[str] = []
        if instruction.b == 0:
            arguments = [self._expression(register + 1 + offset) for offset in range(0, 2)]
            arguments.append("...")
        else:
            arguments = [self._expression(slot) for slot in range(register + 1, register + instruction.b)]
        callee = self.registers.get(register)
        if callee is None:
            callee = self._register_name(register)
        # SELF-based method call: the callee register holds a ':method' binding.
        text = f"{callee}({', '.join(arguments)})"
        results = instruction.c
        if instruction.name == "TAILCALL":
            self._emit(f"return {text}")
            return index + 1
        if results == 0:
            self._emit(text)
            self.registers.pop(register, None)
            return index + 1
        if results == 1:
            self._emit(text)
            return index + 1
        self.registers[register] = text
        self.stable[register] = self.write_counts.get(register, 0) == 1
        if not self.stable[register]:
            self._emit(f"{self._register_name(register)} = {text}")
        return index + 1

    def _emit_expression(self, instruction: Instruction) -> None:
        name = instruction.name
        destination = instruction.a
        if name == "LOADK":
            self._assign(destination, self.proto.constant_text(instruction.bx), stable=True)
        elif name == "LOADBOOL":
            self._assign(destination, "true" if instruction.b else "false", stable=True)
        elif name == "LOADNIL":
            for register in range(destination, destination + instruction.b + 1):
                self._assign(register, "nil", stable=True)
        elif name == "MOVE":
            source = instruction.b
            self._assign(destination, self._expression(source), stable=self._is_stable(source))
        elif name == "GETGLOBAL":
            self._assign(destination, self.proto.constant_text(instruction.bx).strip('"'), stable=True)
        elif name == "GETUPVAL":
            self._assign(destination, self._upvalue(instruction.b), stable=False)
        elif name == "NEWTABLE":
            # A table constructor is a fresh value: never inline it.
            self._assign(destination, "{}", stable=False)
        elif name == "GETTABLE":
            table = self._expression(instruction.b)
            key = self._value(instruction, instruction.c)
            if key.startswith('"') and key.endswith('"') and key[1:-1].isidentifier():
                expression = f"{table}.{key[1:-1]}"
            else:
                expression = f"{table}[{key}]"
            stable = self._is_stable(instruction.b) or instruction.b in self.parameters
            self._assign(destination, expression, stable=stable)
        elif name == "SELF":
            source = instruction.b
            method = self._value(instruction, instruction.c)
            if method.startswith('"') and method.endswith('"'):
                method = method[1:-1]
            self.registers[destination + 1] = self._expression(source)
            self.stable[destination + 1] = self._is_stable(source)
            self._assign(destination, f"{self._expression(source)}:{method}", stable=False)
            self.stable[destination] = False
        elif name in {"ADD", "SUB", "MUL", "DIV", "MOD", "POW"}:
            operator = {"ADD": "+", "SUB": "-", "MUL": "*", "DIV": "/", "MOD": "%", "POW": "^"}[name]
            left = self._value(instruction, instruction.b)
            right = self._value(instruction, instruction.c)
            stable = self._operand_stable(instruction.b) and self._operand_stable(instruction.c)
            self._assign(destination, f"{left} {operator} {right}", stable=stable)
        elif name == "UNM":
            self._assign(destination, f"-{self._expression(instruction.b)}", stable=self._is_stable(instruction.b))
        elif name == "NOT":
            self._assign(destination, f"not {self._expression(instruction.b)}", stable=self._is_stable(instruction.b))
        elif name == "LEN":
            self._assign(destination, f"#{self._expression(instruction.b)}", stable=self._is_stable(instruction.b))
        elif name == "CONCAT":
            parts = [self._expression(register) for register in range(instruction.b, instruction.c + 1)]
            stable = all(self._is_stable(register) for register in range(instruction.b, instruction.c + 1))
            self._assign(destination, " .. ".join(parts), stable=stable)
        elif name == "VARARG":
            self._assign(destination, "..." if instruction.b == 0 else "select(...)", stable=False)
        else:
            self._emit(f"-- {instruction.text(self.proto)}")

    def _operand_stable(self, operand: int) -> bool:
        if operand & 0x100:
            return True
        return self._is_stable(operand)


_COMPARISONS = {"EQ": "==", "LT": "<", "LE": "<="}
_INVERTED_COMPARISONS = {"EQ": "~=", "LT": ">", "LE": ">"}


def decompile(data: bytes | str, *, include_disassembly: bool = False) -> str:
    """Return readable pseudocode for a Lua 5.1 bytecode chunk."""
    if isinstance(data, str):
        data = data.encode("latin-1", "ignore")
    chunk = read_chunk(bytes(data))
    header = [
        "-- Recovered from Lua 5.1 bytecode by Protez.",
        f"-- Prototypes: {chunk.proto_count}. Register names are synthetic (v0, v1, ...);",
        "-- stripped bytecode does not carry local names, so some idioms remain approximate.",
        "",
    ]
    body = _FunctionLifter(chunk.root).lift(as_chunk=True)
    if include_disassembly:
        header.append("--[[ Disassembly of the entry prototype:")
        header.append(disassemble(chunk.root, limit=400))
        header.append("]]")
        header.append("")
    return "\n".join(header) + body + "\n"


class Lua51Scanner:
    """Locate embedded Lua 5.1 chunks inside raw or text data."""

    def __init__(self, data: bytes | str):
        self.data = data.encode("latin-1", "ignore") if isinstance(data, str) else bytes(data)

    def find(self, *, minimum: int = 64) -> list[tuple[int, bytes]]:
        results: list[tuple[int, bytes]] = []
        start = 0
        while True:
            position = self.data.find(LUA51_SIGNATURE, start)
            if position < 0:
                break
            start = position + 1
            payload = self._extend(position)
            if len(payload) >= minimum:
                results.append((position, payload))
        return results

    def _extend(self, position: int) -> bytes:
        """Return the candidate chunk, trimmed at the first unreadable proto."""
        data = self.data
        end = len(data)
        # Try progressively longer prefixes; the first one that parses wins.
        best = data[position:end]
        if len(best) <= 512:
            return best
        for length in (end - position, 262_144, 65_536, 16_384, 4_096):
            candidate = data[position : position + length]
            try:
                read_chunk(candidate + b"")
            except BytecodeError:
                continue
            best = candidate
            break
        return best


def scan_and_decompile(data: bytes | str, *, minimum: int = 64) -> str | None:
    """Find the first embedded Lua 5.1 chunk and decompile it."""
    for _offset, payload in Lua51Scanner(data).find(minimum=minimum):
        try:
            return decompile(payload)
        except BytecodeError:
            continue
    return None
