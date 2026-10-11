# Excalibur

Autonomous **WeAreDevs (WRD) deobfuscator** for Lua scripts, packaged as a single
Windows executable with a minimalist monochrome GUI.

Paste (or drop) an obfuscated `*.lua` file, press **deobfuscate**, and Excalibur:

1. **detects** the obfuscator and its version from structural markers,
2. **lifts the static constant layer** - decodes the custom-base64 string pool,
   applies the shuffle, inlines the pool resolver and folds the constant
   arithmetic (`h(1000+5)` -> `"..."`, `812345-812342` -> `3`),
3. **runs the script in a sandbox** with a `loadstring`/`load`/`table.concat`
   hook and Roblox/executor stubs, following a runtime x policy ladder, and
   writes every chunk and concatenation the script builds to `logs/`,
4. **validates** every candidate by compiling it with a real Lua runtime and
   scoring it, then writes the winner next to a machine-readable report,
5. falls back to **dispatch-loop tracing** when the payload is virtualised, so a
   failed run still produces something actionable.

## Quick start

| | |
|---|---|
| **GUI** | `Excalibur.exe` (or `python main.py`) |
| **Console** | `Excalibur.exe --cli script.lua --out clean.lua` |
| **Detect only** | `Excalibur.exe --detect script.lua` |
| **First-run setup** | `Excalibur.exe --boot` |
| **Tests** | `python -m unittest discover -s tests` |

Everything is written under `logs/run_<timestamp>_<hash>/`:

```
output.lua        recovered source (only when a payload was validated)
decoded.lua       the rewritten constant layer (always, when the static stage ran)
pseudocode.lua    partial lift: state blocks, renamed registers, resolved jumps
report.json       every stage, candidate, validation check and note
summary.txt       the same, human readable
trace_summary.txt visited VM states (trace fallback)
lua51_codex/      per-attempt artefacts: input.lua, report.json, hook_log.txt,
                  dump_NNN.lua (loadstring arguments), concat_NNN.txt, trace.txt
```

## What it can and cannot do

| Input | Result |
|---|---|
| WRD builds that rebuild the payload with `loadstring`/`table.concat` | **full recovery**: the original source is captured, validated byte-for-byte |
| WRD v1.0.0 "flattened" builds (the payload is interpreted inside the obfuscator's own state machine) | **partial + lift**: the constant layer is decoded and rewritten, the state machine is traced, and `pseudocode.lua` renders every state block with registers renamed to `v1, v2, v3, ...` and the jumps resolved (see below) |
| Luraph / Moonsec / IronBrew | recognised and routed, implementation is a documented placeholder (`core/registry.py`) |

Excalibur never invents output: if nothing validates, it says so and leaves the
diagnostics it produced in `logs/`.

### Partial lift (flattened builds)

When the payload stays virtualised, the lift stage writes `pseudocode.lua` next
to the other artefacts: one block per state of the dispatch loop, the original
logic inside it, a register legend (`v1 = b`, `state = d`, ...) and one comment
per successor - `goto S12345`, `if v3 then ... end`, or
`goto v7["name"] (dynamic; trace: S_900000_2100000 in 1 visit(s))`. The values
recorded by the trace fallback are what resolve the computed jumps, so the file
is usually more complete than a purely static view. It is *not* recompilable
source: the dispatch tree and the state numbers are kept on purpose so the
result can be checked against the original.

```bat
python main.py --cli script.lua --out clean.lua --lift pseudo.lua
python main.py --cli script.lua --no-lift        :: skip the stage
```

## Build

```bat
python build.py doctor          :: what this machine can build
python build.py dev             :: run the GUI from source (uv, if installed)
python build.py wheels          :: collect wheels so the first run works offline
python build.py fetch-lua       :: verify lua/lua51.exe (--build rebuilds it)
python build.py exe             :: PyInstaller --onefile --windowed
python build.py all             :: wheels + exe
```

The build embeds `core/lua/*.lua`, `assets/`, and `lua/`, `vendor/`, `wheels/`
when they exist, checks the result against the 80 MB budget and prints a size
report. `.github/workflows/ci.yml` builds the EXE on `windows-latest` and uploads
it as an artifact.

### Autonomy / first run

* Everything writable lives in `%LOCALAPPDATA%\Excalibur` (`logs/`, `runtime/`),
  so the EXE itself can be read-only and can be copied anywhere.
* On the **first** run the bootstrap installs the optional Python dependencies
  into `%LOCALAPPDATA%\Excalibur\runtime\site-packages` - from the bundled
  `wheels/` folder when present (fully offline), otherwise from PyPI through the
  bundled `uv` (`vendor\uv.exe`) with `pip` as a fallback.
* Every later run reuses that folder and does **not** touch the network.
* Lua: `lupa` (a pip wheel that ships Lua 5.1, 5.4 and LuaJIT) is the default
  runtime. Drop `lua51.exe` into `lua/` to use an external interpreter instead.

## Layout

```
main.py              entry point (GUI default, --cli/--detect/--boot modes)
bootstrap.py         first-run setup, dependency cache, offline policy
build.py             PyInstaller + uv development helpers
core/
  deobfuscate.py     the pipeline (detect -> static -> dynamic -> trace -> lift)
  registry.py        obfuscator registry (WRD now, Luraph/Moonside placeholders)
  wrd_detect.py      structural detection, masking helpers
  wrd_static.py      pool/alphabet/shuffle decoding, resolver inlining, folding
  sandbox.py         runtime x policy ladder, artefact collection
  runtime.py         lupa / external interpreter discovery and execution
  pick_payload.py    candidate scoring (explainable, no hard-coded names)
  validate.py        compile + structural validation, dynamic vs static modes
  vm_trace.py        dispatch-loop instrumentation and trace summarisation
  lift.py            partial lift: state blocks, register renaming, jump recovery
  lua/               Lua side: runner, hooks (load/loadstring capture),
                     Roblox stubs (the spec's core/roblox_stubs.lua),
                     Lua 5.1 compatibility shims
lua/lua51.exe        vendored Windows Lua 5.1.5 interpreter (see lua/README.md)
gui/                 monochrome Tkinter UI (theme + app)
tests/               unit + end-to-end tests, acceptance fixture pair
tools/               fixture generator, sample fetcher, icon generator,
                     reproducible lua51.exe builder (build_lua.py)
docs/                architecture, real-world notes, roadmap
```

Anti-patterns the code base avoids on purpose: nothing keys off hard-coded
identifier names (`X`, `m`, `i`, ...) - detection and rewriting are structural;
the sandbox never uses `_G` as the environment (it builds a fresh table and sets
`env._G = env`); every stage runs in a worker thread in the GUI; and the WRD path
is driven by runtime dynamics plus verifiable static transforms rather than
static VM parsing.

## Documentation

* `docs/ARCHITECTURE.md` - how the stages fit together, threading, errors.
* `docs/REAL_WORLD_NOTES.md` - everything measured on real WRD v1.0.0 samples,
  including the formats and the traps.
* `docs/ROADMAP.md` - devirtualisation, new obfuscators, packaging next steps.
