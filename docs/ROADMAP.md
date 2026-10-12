# Roadmap

Ordered by value per unit of work. Everything in "done" is covered by tests.

## Done

* WRD v1.0.0 detection (structural, comment-aware banner matching, version).
* Static constant-layer lifting: pool, custom base64 alphabet, shuffle ranges,
  resolver inlining, Lua 5.1-correct constant folding - verified behaviour
  preserving on three wild samples.
* Sandbox: runtime x policy ladder, `loadstring`/`load`/`concat`/`char` hooks,
  Roblox + executor stubs with three permissiveness policies, instruction and
  wall-clock watchdog, per-attempt artefact directories.
* Payload scoring, two validation profiles, honest `partial` verdict.
* Dispatch-loop tracing with a readable summary.
* **Partial lift**: the flattened state machine is rendered as readable
  `pseudocode.lua` (state blocks, registers renamed to `v1, v2, v3, ...`,
  constant/conditional/literal/dynamic successors, helper inventory). Dynamic
  jumps are resolved from the recorded trace values. Verified statement for
  statement against a luaparser oracle on three wild samples (255/255 blocks)
  and unit tested on a miniature flattened payload.
* **Vendored `lua/lua51.exe`** (official Lua 5.1.5, built reproducibly with a
  pinned zig toolchain - see `lua/README.md`), preferred by the sandbox on
  Windows, with lupa as the always-available fallback.
* Monochrome Tkinter GUI, thread-safe, worker-based.
* First-run bootstrap with an offline-capable dependency cache.
* PyInstaller packaging helper with an 80 MB budget check; CI for Linux tests
  and a Windows EXE build.
* Acceptance fixture pair (`tests/wrd_v1_0_0*.lua`) with byte-exact recovery.

## Next: devirtualisation, part two

The dispatch table is already recovered (see the partial lift above): states,
bodies, registers and successors are readable, and the trace resolves most
computed jumps. What is still missing is *structured* code, i.e. turning the
state graph back into `if`/`while`/function calls that run without the
dispatcher. Measured on the wild samples: aspect 72 states / 38 dynamic jumps
(28 resolved by trace), fog 77 / 45 (36), ka 106 / 61 (39).

1. **Register data flow.** The lift renames variables but does not yet track
   types or lifetimes; the appendix lists the VM's helper closures, whose input
   conventions (`h( v49 )` -> `return v20[v49-(63015)]`) have to be folded into
   the call sites.
2. **Emulate the states offline.** Run the machine *without* the obfuscator by
   interpreting the rendered blocks in Python (the state bodies are plain Lua),
   then compare the observable behaviour with the original under the same stubs -
   the harness for that comparison already exists in `tests/test_pipeline.py`.
3. **Loop and branch reconstruction.** Cycles become `while`/`for`, the binary
   search over state numbers becomes real conditions. A useful intermediate
   artefact would be a single-block-decision listing (`state -> condition ->
   next`), which the trace already provides for the visited path.
4. **String/table reconstruction.** Pool tables are numbered registers; naming
   them after the constants they hold would remove most of the remaining noise.

Until that lands, Excalibur stays honest: those files are reported as partial,
with `decoded.lua` (runnable, constant layer removed), `pseudocode.lua` (the
lifted states) and `trace_summary.txt`.

## Next: more obfuscators

`core/registry.py` already routes them. Each placeholder documents what is
needed; the sandbox and payload/validation layers are format-agnostic and can be
reused as-is.

* **Luraph** - per-build VM with its own instruction set; needs a bytecode lifter
  plus the dynamic trace stage (already built).
* **Moonsec v3** - string pool comparable to WRD's; the decoder pattern in
  `core/wrd_static.py` is the template, the alphabet/shuffle parsing has to be
  generalised.
* **IronBrew 2** - Lua 5.1 bytecode; needs a `luac`-level disassembler.

## Smaller items

* Readability of the lift: the observed transitions are followed for 87-98% of
  the jumps (see `docs/REAL_WORLD_NOTES.md`), the rest point at values computed
  from registers the static pass cannot see. A second trace pass that dumps the
  *operands* of every dynamic jump (`u[expr]`) would close most of the gap.
* Lift output as runnable source: the listing is annotated pseudo-source, not a
  program. Emitting `goto`-based Lua 5.2 code (or a `while`+`if` chain) would let
  the user run the recovered logic.
* Lua 5.1 vendoring: `build.py fetch-lua` currently prints the recipe. Building
  Lua 5.1 from source on the CI runner and shipping `lua/lua51.exe` would remove
  the `lupa` dependency for the sandbox path and make the semantics exact.
* Richer Roblox stubs: `ObjectValue`/`ProximityPrompt`/`UserInputService` method
  surfaces, `Enum` members generated from a data table.
* Payload diffing in the GUI: show the original vs. recovered source and the
  constant table side by side.
* Report schema versioning (`report.json` is already the contract the GUI and CI
  read).
* Optional update check (opt-in, off by default) and a signed build.
