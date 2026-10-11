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
* Monochrome Tkinter GUI, thread-safe, worker-based.
* First-run bootstrap with an offline-capable dependency cache.
* PyInstaller packaging helper with an 80 MB budget check; CI for Linux tests
  and a Windows EXE build.
* Acceptance fixture pair (`tests/wrd_v1_0_0*.lua`) with byte-exact recovery.

## Next: devirtualisation of flattened builds

The remaining hard problem for WRD v1.0.0 (and every wild sample measured so
far): the payload is interpreted inside the obfuscator's own state machine, so
there is no text to capture. The trace stage already records the visited states
and register writes; the next steps are:

1. **Lift the dispatch table.** Each `if <state> == <constant> ... end` branch is
   a basic block; the constants are folded pool values, so the branch table can
   be recovered statically once the constant layer is rewritten.
2. **Recover the register model.** The VM stores its state in a table (locals +
   pool entries). Instrument reads and writes per state to rebuild the data flow
   for one state at a time.
3. **Emit structured code.** Translate each basic block into Lua, then run the
   existing validation chain (`validate_payload`) plus an *equivalence* check:
   run the original and the reconstruction under the same stubs and compare the
   observable trace (instruction counts, char calls, missed globals) - the
   harness for that comparison already exists in `tests/test_pipeline.py`.
4. **Loop reconstruction.** Trace cycles become `while`/`for`; the trace summary
   already reports repeated short cycles and transition counts.

Until that lands, Excalibur stays honest: those files are reported as partial,
with `decoded.lua` (runnable, constant layer removed) plus the trace.

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
