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
   pool, opcode histogram and a bounded disassembly are recovered and reported,
   with an honest note that opcode semantics need a per-family opcode map.

Open-source lifters are used where they exist and are legally bundleable
(the MoonSec V3 handler mapper and Lua-5.1 decompiler shipped in `tools/`); the
methods above are Protez's own and cover the rest.

## Named families

| Family | Detection | Recovery path | Typical result |
| --- | --- | --- | --- |
| **Luraph v15.1** | `Luraph`/`LPH` marker, `-- Luraph Obfuscator v15.1` header, LPH container | Pinned v15 lifter when the layout matches; otherwise container extraction → portable backend → VM introspection | Full source for supported v15 layouts; `partial` with a VM surface and container artifacts otherwise |
| **Luraph v14.7** | `-- Luraph Obfuscator v14.7` header, LPH container | Container extraction, static decoding, portable backend, VM introspection | `partial`: the VM surface and any captured chunk, never a claimed full lift |
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
