"""Custom-VM introspection for obfuscators that build a VM in Lua.

Every Lua-implemented obfuscator in the wild -- IronBrew 2/3, WeAreDevs v2.4,
Wynfuscate v5, Prometheus, Nexus v2.0, PSU v1.0, AztupBrew, Xen, the Luraph
v14/v15 wrappers -- shares one property: before it can run anything, it decodes
its packed payload into ordinary Lua tables (an instruction stream, a constant
pool, sometimes a prototype table).  Reimplementing each family's byte-level
codec from scratch is fragile; observing the tables the obfuscator builds for
itself is not.

This module therefore dumps those tables from a live run:

* :data:`VM_DUMP_LUA` walks the Lua call stack from inside the emulator's
  instruction hook and snapshots large array-like tables it can reach through
  locals and upvalues (with a table-identity guard and strict budgets),
* :func:`instruction_table` / :func:`constant_pool` pick the instruction stream
  and the constant pool out of the snapshots using structural scoring.

The dumper never mutates the script's state, never touches the network and
gives up after a fixed number of scans, so it is safe to leave installed for
every portable-backend run.
"""

from __future__ import annotations

import re
from dataclasses import dataclass
from typing import Any, Iterable, Sequence

__all__ = [
    "VM_DUMP_LUA",
    "VmSnapshot",
    "snapshot_from_bridge",
    "instruction_table",
    "constant_pool",
    "describe_snapshots",
    "MAX_SNAPSHOTS",
    "MAX_TABLE_VALUES",
    "MAX_PAYLOAD_BYTES",
]

MAX_SNAPSHOTS = 48
MAX_TABLE_VALUES = 200_000
MAX_PAYLOAD_BYTES = 4 * 1024 * 1024
MAX_STRING_VALUES = 4_096
MAX_STRING_BYTES = 64 * 1024

_NUMBER_SEPARATOR = ","
_STRING_SEPARATOR = "\x01"


# ---------------------------------------------------------------------------
# Lua side
# ---------------------------------------------------------------------------

VM_DUMP_LUA = r"""
-- ---------------------------------------------------------------------------
-- Custom-VM introspection: snapshot the tables an obfuscator builds for its
-- own virtual machine.  Installed as a *second* step callback so the
-- instruction-budget hook keeps running; every scan is bounded, and each
-- value read is defensive because the payload may be hostile.
-- ---------------------------------------------------------------------------
local __protez_vm_seen = {}
local __protez_vm_seen_count = 0
local __protez_vm_events = 0
local __protez_vm_scans = 0
local __protez_vm_reports = 0
-- Numeric and string tables get their own budgets: a constant pool can never
-- starve the instruction stream, which is the one we most want.
local __protez_vm_number_reports = 0
local __protez_vm_string_reports = 0
local __protez_vm_gate = 1

local function __protez_vm_size(value)
  local ok, count = pcall(function() return #value end)
  if not ok or type(count) ~= 'number' then return 0 end
  if count < 0 then return 0 end
  return math.floor(count)
end

-- Tables grow while a loader fills them, so the guard remembers how large a
-- table was when it was last looked at: the same table is revisited whenever
-- it has grown since, and skipped while it has not.
local function __protez_vm_has_seen(value)
  local size = __protez_vm_size(value)
  local previous = __protez_vm_seen[value]
  if previous ~= nil then
    return previous >= size
  end
  if __protez_vm_seen_count >= 2048 then return true end
  __protez_vm_seen_count = __protez_vm_seen_count + 1
  __protez_vm_seen[value] = size
  return false
end

local function __protez_vm_length(value)
  local ok, count = pcall(function() return #value end)
  if not ok or type(count) ~= 'number' then return nil end
  if count < 1 or count > 4000000 then return nil end
  return math.floor(count)
end

-- Classify an array-like table as 'numbers' / 'strings' / 'tables'.
local function __protez_vm_array_kind(value, minimum)
  local count = __protez_vm_length(value)
  if count == nil or count < (minimum or 24) then return nil, 0 end
  local step = 1
  if count > 64 then step = math.floor(count / 64) end
  local numbers, strings, tables, checked = 0, 0, 0, 0
  local index = 1
  while index <= count and checked < 64 do
    local item = value[index]
    if item == nil then return nil, 0 end
    local kind = type(item)
    if kind == 'number' then numbers = numbers + 1
    elseif kind == 'string' then strings = strings + 1
    elseif kind == 'table' then tables = tables + 1
    else return nil, 0 end
    checked = checked + 1
    index = index + step
  end
  if checked == 0 then return nil, 0 end
  if numbers >= checked * 0.8 then return 'numbers', count end
  if strings >= checked * 0.6 then return 'strings', count end
  if tables >= checked * 0.8 then return 'tables', count end
  return nil, 0
end

local function __protez_vm_has_separator(text)
  -- Lua 5.1 patterns cannot express NUL/0x01 classes reliably, so scan bytes.
  local limit = #text
  if limit > 4096 then limit = 4096 end
  for index = 1, limit do
    local byte = string.byte(text, index)
    if byte == 0 or byte == 1 then return true end
  end
  return false
end

local function __protez_vm_payload(values, count, kind, minimum)
  local parts = {}
  local sent = 0
  local index = 1
  while index <= count do
    local item = values[index]
    if kind == 'numbers' then
      if type(item) ~= 'number' then break end
      parts[#parts + 1] = tostring(item)
      if sent >= 200000 then break end
    else
      if type(item) ~= 'string' then break end
      if __protez_vm_has_separator(item) then return nil end
      parts[#parts + 1] = item
      if sent >= 4096 then break end
    end
    sent = sent + 1
    index = index + 1
  end
  if sent < (minimum or 24) then return nil end
  local separator = kind == 'numbers' and ',' or '\1'
  local payload = table.concat(parts, separator)
  if #payload > 4194304 then return nil end
  return payload, sent
end

local __protez_vm_reported = {}

local function __protez_vm_already_reported(label, size)
  -- Tables grow while the loader fills them: keep the biggest one seen.
  local previous = __protez_vm_reported[label]
  if previous ~= nil and previous >= size then return true end
  __protez_vm_reported[label] = size
  return false
end

-- Protez's own prelude tables are never the obfuscator's VM.
local function __protez_vm_is_runtime(label)
  local _, _, field = string.find(label, ':([%w_]+)$')
  if field == nil then return false end
  return string.sub(field, 1, 8) == '__protez'
end

local function __protez_vm_report_table(label, value, kind, count, width)
  if __protez_vm_reports >= 160 then return end
  if kind == 'numbers' then
    if __protez_vm_number_reports >= 64 then return end
  else
    if __protez_vm_string_reports >= 64 then return end
  end
  if __protez_vm_already_reported(label, count) then return end
  local minimum = kind == 'strings' and 6 or 24
  local payload, sent = __protez_vm_payload(value, count, kind, minimum)
  if payload == nil or sent == nil then return end
  local ok = pcall(__protez_vm_table, kind, label, payload, sent, width or 1)
  if ok then
    __protez_vm_reports = __protez_vm_reports + 1
    if kind == 'numbers' then
      __protez_vm_number_reports = __protez_vm_number_reports + 1
    else
      __protez_vm_string_reports = __protez_vm_string_reports + 1
    end
  end
end

-- A table of small numeric rows: flatten it into one instruction stream.
local function __protez_vm_report_rows(label, value, count)
  local rows = {}
  local width, total, rows_seen = 0, 0, 0
  local index = 1
  while index <= count and rows_seen < 4096 do
    local sub = value[index]
    if type(sub) ~= 'table' then break end
    local sub_count = __protez_vm_length(sub)
    if sub_count == nil or sub_count > 64 then break end
    local samples, position, numeric_row = 0, 1, true
    while position <= sub_count and samples < 8 do
      if type(sub[position]) ~= 'number' then
        numeric_row = false
        break
      end
      samples = samples + 1
      position = position + 1
    end
    if not numeric_row then break end
    if sub_count > width then width = sub_count end
    total = total + sub_count
    rows_seen = rows_seen + 1
    rows[rows_seen] = sub
    index = index + 1
  end
  if width < 2 or total < 96 then return end
  local flat = {}
  local position = 1
  for row = 1, rows_seen do
    local sub = rows[row]
    local sub_count = __protez_vm_length(sub)
    if sub_count == nil then break end
    for index_in_row = 1, sub_count do
      if position >= 200000 then break end
      flat[position] = sub[index_in_row]
      position = position + 1
    end
  end
  __protez_vm_report_table(label .. '/' .. width, flat, 'numbers', #flat, width)
end

local function __protez_vm_consider(label, value, depth)
  if type(value) ~= 'table' then return end
  if __protez_vm_reports >= 160 then return end
  if __protez_vm_is_runtime(label) then return end
  if __protez_vm_has_seen(value) then return end
  -- Constant pools are often short; instruction streams are not.
  local kind, count = __protez_vm_array_kind(value, 12)
  if kind == 'numbers' then
    if count < 24 then return end
    __protez_vm_report_table(label, value, 'numbers', count, 1)
    return
  end
  if kind == 'strings' then
    __protez_vm_report_table(label, value, 'strings', count, 1)
    return
  end
  if kind == 'tables' and (depth or 0) < 1 then
    __protez_vm_report_rows(label, value, count)
    return
  end
  if (depth or 0) < 1 then
    -- A wrapper table such as `vm = { code = ..., consts = ... }`.
    local visited = 0
    for key, sub in pairs(value) do
      if visited >= 24 or __protez_vm_reports >= 96 then break end
      visited = visited + 1
      if type(sub) == 'table' then
        __protez_vm_consider(label .. '.' .. tostring(key), sub, 1)
      end
    end
  end
end

local function __protez_vm_note(line)
  local log = rawget(_G, '__protez_vm_log')
  if type(log) ~= 'table' then
    log = {}
    rawset(_G, '__protez_vm_log', log)
  end
  if #log < 128 then log[#log + 1] = line end
end

local function __protez_vm_scan()
  if __protez_vm_scans >= 512 then return end
  __protez_vm_scans = __protez_vm_scans + 1
  -- Dense while the loader is still building its tables, sparse afterwards.
  if __protez_vm_scans == 160 then __protez_vm_gate = 8 end
  if __protez_vm_scans == 320 then __protez_vm_gate = 32 end
  local level = 1
  while level <= 12 do
    local info = debug.getinfo(level, 'fS')
    if info == nil then break end
    -- `what` is 'main' for a chunk and 'Lua' for a function: both can hold
    -- the obfuscator's own tables, so neither may be skipped.
    if (info.what == 'Lua' or info.what == 'main') and type(info.func) == 'function' then
      local where = ''
      if type(info.source) == 'string' then where = info.source end
      local upvalue_index = 1
      while upvalue_index <= 60 do
        local name, value = debug.getupvalue(info.func, upvalue_index)
        if name == nil then break end
        if type(value) == 'table' then
          __protez_vm_note('lvl ' .. level .. ' upvalue ' .. tostring(name) .. ' (' .. tostring(info.what) .. ')')
          __protez_vm_consider(where .. ':' .. tostring(name), value, 0)
        end
        upvalue_index = upvalue_index + 1
      end
      local local_index = 1
      while local_index <= 200 do
        local name, value = debug.getlocal(level, local_index)
        if name == nil then break end
        if type(value) == 'table' then
          __protez_vm_note('lvl ' .. level .. ' local ' .. tostring(name) .. ' (' .. tostring(info.what) .. ')')
          __protez_vm_consider(where .. ':' .. tostring(name), value, 0)
        end
        local_index = local_index + 1
      end
    end
    level = level + 1
  end
end

rawset(_G, '__protez_vm_step', function()
  __protez_vm_events = __protez_vm_events + 1
  if __protez_vm_events % __protez_vm_gate ~= 0 then return end
  -- A scan must never break the payload: any introspection error is swallowed.
  pcall(__protez_vm_scan)
end)

-- A manual sweep the host can trigger at the end of a run, when the payload's
-- top-level tables are all built.
rawset(_G, '__protez_vm_scan_now', function()
  pcall(__protez_vm_scan)
  return rawget(_G, '__protez_vm_log')
end)

-- Diagnostics: how much of the run the dumper actually observed.
rawset(_G, '__protez_vm_stats', function()
  return __protez_vm_events, __protez_vm_scans, __protez_vm_seen_count, __protez_vm_reports
end)
"""


# ---------------------------------------------------------------------------
# Python side
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class VmSnapshot:
    """A large array-like table observed inside a running obfuscator."""

    kind: str  # numbers | strings
    label: str
    values: tuple[Any, ...]
    width: int = 1

    @property
    def size(self) -> int:
        return len(self.values)

    @property
    def numeric(self) -> bool:
        return self.kind == "numbers"

    def as_int_values(self) -> tuple[int, ...]:
        numbers: list[int] = []
        for value in self.values:
            if isinstance(value, bool):
                numbers.append(int(value))
            elif isinstance(value, int):
                numbers.append(value)
            elif isinstance(value, float):
                numbers.append(int(value))
            else:
                return ()
        return tuple(numbers)

    def describe(self) -> str:
        return f"{self.kind} table {self.label!r} ({self.size} entries, width {self.width})"


def _parse_numbers(payload: str) -> tuple[int, ...]:
    numbers: list[int] = []
    for item in payload.split(_NUMBER_SEPARATOR):
        item = item.strip()
        if not item:
            continue
        try:
            numbers.append(int(float(item)))
        except ValueError:
            continue
    return tuple(numbers)


def snapshot_from_bridge(
    kind: object,
    label: object,
    payload: object,
    count: object = 0,
    width: object = 1,
) -> VmSnapshot | None:
    """Build a snapshot from the Lua ``__protez_vm_table`` bridge call."""
    kind_text = str(kind)
    label_text = str(label or "table")
    if not isinstance(payload, str):
        return None
    try:
        size = int(count)
    except (TypeError, ValueError):
        size = 0
    try:
        stride = max(1, int(width))
    except (TypeError, ValueError):
        stride = 1
    if len(payload) > MAX_PAYLOAD_BYTES:
        return None
    if kind_text == "numbers":
        values: tuple[Any, ...] = _parse_numbers(payload)[:MAX_TABLE_VALUES]
    elif kind_text == "strings":
        if not payload:
            return None
        values = tuple(payload.split(_STRING_SEPARATOR))[:MAX_STRING_VALUES]
    else:
        return None
    if not values:
        return None
    if size and len(values) > size:
        values = values[:size]
    return VmSnapshot(kind=kind_text, label=label_text, values=values, width=stride)


_INSTRUCTION_LABEL_HINTS = (
    "ins",
    "inst",
    "instruction",
    "instructions",
    "code",
    "bytecode",
    "program",
    "proto",
    "protos",
    "opcode",
    "opcodes",
    "ops",
    "bytes",
    "vm",
    "vmentry",
    "p",
    "c",
)

_STRING_LABEL_HINTS = (
    "const",
    "consts",
    "constant",
    "constants",
    "k",
    "str",
    "strings",
    "string",
    "pool",
    "data",
    "d",
)


def _label_tokens(label: str) -> set[str]:
    return {token for token in re.split(r"[^0-9a-z]+", str(label).lower()) if token}


def _hint_match(tokens: set[str], hints: tuple[str, ...]) -> bool:
    """Whole-token hints only: a stray letter inside a word is not evidence."""
    for hint in hints:
        if hint in tokens:
            return True
        if len(hint) >= 3 and any(token.startswith(hint) or token.endswith(hint) for token in tokens):
            return True
    return False


def _label_penalty(label: str) -> float:
    """Protez's own runtime tables are never the obfuscator's VM."""
    lowered = str(label).lower()
    if "__protez" in lowered or "protez_" in lowered:
        return 0.25
    return 1.0


def instruction_score(snapshot: VmSnapshot) -> float:
    """How much a numeric snapshot looks like a VM instruction stream.

    Instruction streams repeat their opcodes a lot, stay inside a small numeric
    range, and are long.  Random data (URLs, hashes split into numbers) does
    not have those properties.
    """
    if not snapshot.numeric:
        return 0.0
    values = snapshot.as_int_values()
    if len(values) < 64:
        return 0.0
    sample = values[:20_000]
    distinct = len(set(sample))
    if distinct == 0:
        return 0.0
    maximum = max(sample)
    minimum = min(sample)
    if minimum < 0 or maximum > 2**31:
        return 0.0
    repeats = 1.0 - (distinct / len(sample))
    small_range = 1.0 if maximum <= 2**20 else (0.5 if maximum <= 2**31 else 0.0)
    length_score = min(1.0, len(values) / 2_000.0)
    width_bonus = 0.15 if snapshot.width > 1 else 0.0
    label_bonus = 0.2 if _hint_match(_label_tokens(snapshot.label), _INSTRUCTION_LABEL_HINTS) else 0.0
    score = 0.35 * repeats + 0.3 * small_range + 0.2 * length_score + width_bonus + label_bonus
    score *= _label_penalty(snapshot.label)
    return round(min(1.0, score), 4)


def string_score(snapshot: VmSnapshot) -> float:
    if snapshot.numeric or not snapshot.values:
        return 0.0
    printable = 0
    for value in snapshot.values[:512]:
        text = str(value)
        if text and all(character.isprintable() or character in "\t " for character in text):
            printable += 1
    ratio = printable / min(len(snapshot.values), 512)
    label_bonus = 0.25 if _hint_match(_label_tokens(snapshot.label), _STRING_LABEL_HINTS) else 0.0
    score = (ratio * 0.8 + label_bonus) * _label_penalty(snapshot.label)
    return round(min(1.0, score), 4)


def instruction_table(snapshots: Sequence[VmSnapshot]) -> VmSnapshot | None:
    """Pick the most instruction-stream-like snapshot, if any."""
    best: tuple[float, VmSnapshot] | None = None
    for snapshot in snapshots:
        score = instruction_score(snapshot)
        if score <= 0:
            continue
        weighted = score * (1.0 + min(1.0, snapshot.size / 50_000.0))
        if best is None or weighted > best[0]:
            best = (weighted, snapshot)
    return best[1] if best else None


def constant_pool(snapshots: Sequence[VmSnapshot]) -> VmSnapshot | None:
    """Pick the most constant-pool-like snapshot.

    A pool is built *before* the VM runs, so among equally string-like tables
    the one seen first wins; the assembled output of the VM is usually a string
    table too, and it is always built later.
    """
    best: tuple[float, VmSnapshot] | None = None
    first_seen: dict[str, int] = {}
    for position, snapshot in enumerate(snapshots):
        first_seen.setdefault(snapshot.label, position)
    total = max(1, len(snapshots))
    for snapshot in snapshots:
        score = string_score(snapshot)
        if score <= 0:
            continue
        order = first_seen.get(snapshot.label, total)
        order_bonus = 0.2 * (1.0 - order / total)
        weighted = (score + order_bonus) * (1.0 + min(1.0, snapshot.size / 512.0))
        if best is None or weighted > best[0]:
            best = (weighted, snapshot)
    return best[1] if best else None


def numeric_tables(snapshots: Sequence[VmSnapshot]) -> tuple[VmSnapshot, ...]:
    return tuple(snapshot for snapshot in snapshots if snapshot.numeric and snapshot.size >= 64)


def describe_snapshots(snapshots: Sequence[VmSnapshot]) -> tuple[str, ...]:
    return tuple(snapshot.describe() for snapshot in snapshots)


def looks_like_vm_payload(source: str) -> bool:
    """Cheap structural probe: does this text look like a Lua-side VM?"""
    if not source or len(source) < 2_000:
        return False
    sample = source[:400_000]
    lowered = sample.lower()
    signals = 0
    if re.search(r"string\.byte\s*\(", sample):
        signals += 1
    if re.search(r"while\s+true\s+do|while\s+not\s+\w+\s+do", sample):
        signals += 1
    if re.search(r"(?m)^\s*local\s+\w+\s*=\s*\{", sample):
        signals += 1
    if "goto" in lowered or "%" in sample:
        signals += 1
    if re.search(r"\[[a-z]\s*\+\s*1\]\s*=|\[\s*\w+\s*\]\s*=\s*function", sample):
        signals += 1
    if sample.count("function") >= 16:
        signals += 1
    return signals >= 3
