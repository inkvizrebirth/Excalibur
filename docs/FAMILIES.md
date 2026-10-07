# Obfuscator coverage: what Protez does per family

Protez does not ship a binary per obfuscator.  It combines four methods and
applies them in the order that recovers the most source:

1. **Static decoding** (`core.deobfuscator`) — constant folding, string-escape,
   hex and base64 layers, on the real Luau token stream.
2. **Encoded-blob recovery** (`core.families.scan_embedded_source`,
   `scan_embedded_bytecode`) — payloads hidden in `{104,101,108,108,111}`
   arrays, `string.char(...)` calls or escape runs, decoded back to source or
   to a Lua 5.1 chunk that `core.lua51` then lifts.
3. **Running the loader** (`core.emulator` + `core.injector_env` +
   `core.executor_api`) — a fictional `Real` executor runs the loader with a
   full command surface, so every payload handed to `loadstring`/`load`, drawn
   over HTTP, written to disk, or assembled inside a Lua-side VM is captured.
4. **VM introspection** (`core.vm_dump` + `core.vm_recover`) — for a loader
   that keeps its payload inside its own VM, the instruction stream, constant
   pool, opcode histogram and a bounded disassembly are recovered and reported.
5. **Own devirtualizers** (`core.devirt`) — one recovery method per family,
   applied before the VM surface is accepted as the final answer.

Open-source lifters are used where they exist and are legally bundleable
(the MoonSec V3 handler mapper and Lua-5.1 decompiler shipped in `tools/`); the
methods above are Protez's own and cover the rest.

## The own devirtualizers (`core.devirt`)

No lifter could be vendored for most of the named families, so each one has an
implemented method instead of a guess.  `core.devirt.devirtualize(family, …)`
runs the family's strategy and normalises the outcome (`source`, `bytecode`,
`method`, `notes`, `confidence`, `partial`).

| Family | Method | What it recovers |
| --- | --- | --- |
| Luraph v14/v15 | `core.devirt.luraph` | Static container unpack (`core.luraph_static`), a Lua 5.1 chunk if the custom stream turns out to be one, hidden source in the decoded streams, and a disassembly whose opcode names come from Luraph's **own** interpreter source |
| MoonSec V2/V3 | `core.devirt.bytecode_vm` | The Lua 5.1 chunk behind the VM — from the loader text, from a captured `loadstring`, or rebuilt from the table the loader filled at runtime |
| WeAreDevs v2.4 | `core.devirt.bytecode_vm` | Same bytecode reconstruction, including the runtime-table door |
| IronBrew 2/3 | `core.devirt.bytecode_vm` | Same, plus byte-table packings (1-based codes, 16/32-bit words, both endiannesses) |
| PSU v1.0 | `core.devirt.bytecode_vm` | Same |
| Nexus v2.0 | `core.devirt.nexus` | Reassembles payloads split across `"…" .. "…"` literal runs before decoding, then falls back to the bytecode method |
| Prometheus | `core.devirt.prometheus` | **Control-flow flattening removal:** the state-machine dispatcher is traced and re-ordered into straight-line code.  Conservative: a rewrite happens only when every branch is reachable through literal `state = n` transitions, no branch computes its state at runtime, and the loop cannot repeat |
| Wynfuscate v5 | `core.devirt.table_vm` | Annotated disassembly: opcode names read from the loader's dispatcher (`handlers[n] = function …`, `if opcode == n then …`), pool constants inlined (`K[12]="print"`), and the payload itself when the constant pool spells it out |
| Xen / Synapse / Hyperion / Luau VM | `core.devirt.table_vm` | Same annotated disassembly and pool reassembly |
| Generic / unknown VM | `core.devirt.bytecode_vm` → `table_vm` → `prometheus` | Whichever method applies first |

Two doors lead to a bytecode chunk, and the runtime one matters most: static
containers can be encrypted, but the loader still has to *build* the chunk
before running it, so `core.vm_dump` snapshots the table and
`core.devirt.common` rebuilds the bytes from it.  The same helper accepts
0–255 byte tables, 1-based codes and 16/32-bit word packings.

## Named families

| Family | Detection | Recovery path | Typical result |
| --- | --- | --- | --- |
| **Luraph v15.1** | `Luraph`/`LPH` marker, `-- Luraph Obfuscator v15.1` header, LPH container | Pinned v15 lifter when the layout matches; otherwise container extraction → portable backend → VM introspection | Full source for supported v15 layouts; `partial` with a VM surface and container artifacts otherwise |
| **Luraph v14.7** | `-- Luraph Obfuscator v14.7` header, LPH container | Pinned v14 lifter when the layout matches (runtime prototype capture → whole-namespace symbolic walk → structuring: entry prototype plus every sibling function, anti-tamper prototypes reported as skipped); otherwise container extraction, static decoding, portable backend, VM introspection | Full source for supported v14 layouts; `partial` with the VM surface and container artifacts otherwise |
| **WeAreDevs Obfuscator v2.4** | `WeAreDevs`/`wearedevs`/`wad_obfuscator`, numeric-loader shape | String/byte-array decode → `loadstring` capture → Lua 5.1 lifting when a chunk is used | Readable payload when it decodes to source; lifted pseudocode from a dumped chunk |
| **Wynfuscate v5** | `Wynfuscate`/`wyn` markers, `string.char(0x..)` structural hint | `string.char`/array decode, portable backend, VM introspection | Source or a chunk from the loader; VM surface when the payload stays inside the VM |
| **IronBrew3** | `IronBrew`/`IB3`, numeric loader with `getfenv` | Byte-array → chunk decode, `core.lua51` lifting, portable backend, VM introspection | Lifted Lua 5.1 pseudocode, or the VM surface plus a bounded disassembly |
| **Prometheus** | `Prometheus`/`levno-710`, escaped `\27Lua` header | Escaped-bytecode decode → decompiler; portable backend; VM introspection | Lifted pseudocode or a declared partial with the VM surface |
| **Nexus Obfuscator v2.0** | `Nexus Obfuscator`/`nexus_obfuscator`, `\27\76\117\97` header | Escaped-bytecode decode → decompiler; array decode; portable backend | Lifted pseudocode or the VM surface |
| **PSU Obfuscator v1.0** | `PSU`/`psu_obfuscator` markers | Array/`string.char`/base64 decode → source; portable backend | Readable source when the payload is source-shaped |
| **MoonSec V2/V3** | `MoonSec` markers | V3 handler mapping to Lua 5.1 bytecode plus the pinned `unluac-rs` decompiler; V2 static decoding and the portable backend | Source for the supported V3 serializer, explicit `partial` with bytecode/disassembly otherwise |
| **AztupBrew 2** | `AztupBrew`/`aztup` markers, numeric loader | Byte-array → chunk lifting plus the portable backend | Lifted pseudocode or the VM surface |
| **Xen Obfuscator** | `Xen Obfuscator`/`xen_obf` markers | Array decode, portable backend | Source or chunk from the loader |
| **Synapse-protected payloads** | `syn.protect`/`Synapse` markers | Portable backend (the executor surface answers `syn.*`), static decoding | The captured chunk, or the cleaned wrapper |
| **Generic custom VM / unknown** | structural probes: byte-by-byte string building, `string.dump`, `buffer.*`, numeric loader with `loadstring` | Array/bytecode scanning, portable backend, VM introspection | Whatever the layers recover; always labelled `partial` with the VM surface |

## What each result means

* **`complete`** — a readable source layer passed Luau validation and no
  protected signature survived; names and comments may still be synthetic.
* **`partial`** — real work happened (layers were removed, bytecode was lifted,
  a VM surface was read) but the output is an approximation; the report lists
  what is missing.
* The report (`logs/report_*.json`) carries `layers`, `remote_fetches`,
  `emulator` (captures, requests, downloads, workspace files) and `vm`
  (stream, opcode histogram, confidence, constants) so a partial result can be
  audited instead of guessed at.

## Fed by tests

`tests/test_family_samples.py` builds a synthetic protected sample for every
family in the table above and asserts detection **and** one working recovery
method per family, so a family that silently loses coverage fails the suite.
`tests/test_devirt.py` covers the own devirtualizers: container packing,
runtime-table reconstruction, concatenated-literal reassembly, opcode naming
from a dispatcher, pool reassembly, and the flattening removal with its
refusal cases (incomplete graph, computed state, loop that can repeat).
