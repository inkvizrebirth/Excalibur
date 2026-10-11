# Architecture

```
                 +-------------------------------+
   input .lua -> |  core.deobfuscate.deobfuscate |
                 +-------------------------------+
                       |        |         |
      (1) route -------+        |         |
      core.registry /           |         |
      core.wrd_detect           |         |
                                |         |
      (2) static ---------------+         |
      core.wrd_static                     |
                                |         |
      (3) dynamic --------------+---------+
      core.sandbox -> core.runtime -> core/lua/runner.lua
                                |
      (4) trace ----------------+
      core.vm_trace
                                |
                       +--------+---------+
                       |  pick + validate |
                       |  pick_payload.py |
                       |  validate.py     |
                       +------------------+
                                |
                 logs/run_*/{output.lua, decoded.lua, report.json, summary.txt}
```

## Stages

**1. Routing** (`core/registry.py`, `core/wrd_detect.py`)

`detect()` is structural: the WRD banner (searched in a *comment-preserving*
mask, because the banner is a comment), the `return(function(...) ... end)(...)`
wrapper, the escaped-decimal string pool and the pool resolver. Every signal
adds confidence and a human-readable reason; the result carries
`is_obfuscated`, `format`, `version`, `confidence`, `features` and `warnings`.
`registry.detect_and_route()` maps the format to a `Deobfuscator` subclass; only
WRD is implemented, the others raise a documented "recognised, not supported"
error instead of pretending to work.

**2. Static layer** (`core/wrd_static.py`)

Text in, text out - never offsets into a stale buffer:

* locate the biggest escaped-decimal table (`local <name> = { "\068..." , ... }`),
* parse the custom alphabet table (`{ ["0"] = 0, ... }`, at least 40 entries),
* parse the shuffle ranges (`for _, v in ipairs({{1, 45}, ...})`),
* unescape + base64-decode + unshuffle every entry,
* find the resolver (`local function h(x) return j[x - 63015] end`, both the
  named and the anonymous form) and replace `h(<constant>)` with a literal,
* fold pure constant arithmetic with Lua 5.1 semantics (floor `%`, `^`, hex
  literals, unary runs) while respecting precedence and binding boundaries.

Both stages return `(count, text)`; `analyze()` chains them, so the second pass
always works on the text the first pass produced. The result carries the decoded
constants, the resolver description and the rewritten source.

**3. Dynamic layer** (`core/sandbox.py`, `core/runtime.py`, `core/lua/*.lua`)

The sandbox runs the input under a ladder of runtimes (`lua51`, `luajit21`,
`lua54`, or a vendored `lua/*.exe`) and environment policies
(`codex` -> `strict` -> `permissive`), stopping early when the caller's
`stop_when` predicate says a payload was captured. Each attempt gets its own
`logs/run_*/<engine>_<policy>/` directory containing the input, the report,
`hook_log.txt`, every `loadstring` argument (`dump_NNN.lua`), every
`table.concat` result (`concat_NNN.txt`), `char_fragments.txt` and a `trace.txt`
when tracing.

The Lua side is four files loaded with `loadfile`:

| file | role |
|---|---|
| `runner.lua` | reads the `EXCALIBUR` config table, builds the environment, installs the watchdog, `xpcall`s the chunk, writes the report |
| `hooks.lua` | `load`/`loadstring`/`table.concat`/`string.char` instrumentation, read/write counters, dump writers, trace state |
| `roblox_stubs.lua` | Roblox and executor API stubs (`Instance`, `Vector3`, `CFrame`, `Enum`, `game:GetService`, `task`, `typeof`, `http_request`, ...) with three policies and auto-vivifying tables |
| `lua51_compat.lua` | `getfenv`/`setfenv`/`loadstring`/`unpack`/`bit32`/`bit` shims for Lua 5.2+, deterministic `math.random` |

The sandbox never uses `_G` as the environment: it builds a fresh table, sets
`env._G = env`, and restricts `os`, `io` and `debug`. The watchdog is a
`debug.sethook` instruction counter plus a wall-clock check; `scripts must not
disable the watchdog` is enforced by shadowing `debug.sethook`.

**4. Trace fallback** (`core/vm_trace.py`)

When no payload validated, the dispatch loop returned by
`core.lift.find_dispatcher()` gets `__sandbox_trace_state(<state>)` injected at
the top of the body and the instrumented source is re-run (the heuristic
"most `if` statements" scan is only the fallback when no dispatcher is found).
The visited states are summarised (distinct count, hottest states, most frequent
transitions, repeated cycles) and written to `trace_summary.txt`.

**5. Partial lift** (`core/lift.py`)

The trace values feed the lift, which is a hand-written O(n) scanner - no ANTLR
in the production path (luaparser is 2-4 s per 13 KB and is used only as an
oracle during development). It tokenises the text once, finds the dispatch loop
(`while <state> do if <state> < <pivot> ...`), walks the pivot tree into state
blocks, and for each block:

* renders the body with every register renamed to `vN` (the state variable keeps
  the name `state`), using one shared map built from the whole file because the
  VM's helper closures share the dispatcher's scope;
* classifies the successors: constant (`state = 12345`), conditional
  (`state = state and A or B` and friends), literal (`true`/`false`/`nil`) and
  dynamic (`goto v7["name"]`, `state = v3[...]`);
* resolves the dynamic ones against the observed trace values, reporting the
  target block, the visit count and the confidence;
* inventories the VM's own helper functions, which are printed as an appendix.

The result is `logs/run_*/pseudocode.lua` plus `result.lift` (stats, states,
registers, successors) in `report.json`. The stage runs whenever a dispatch loop
is found in the chosen payload or in the constant-layer rewrite, including for
successful runs whose payload is itself flattened. `--no-lift` turns it off.

**6. Runtime ladder details**

`runtime.discover_runtimes()` groups candidate interpreters by name (`lua51.exe`,
`lua51`, `luajit`, ...) from `lua/` and `PATH`, probes each one, and keeps the
first that actually runs - so a Windows binary sitting next to a native one in
`lua/` never shadows a usable interpreter. `resolve_prefer_exe()` then decides
between the standalone interpreter and the lupa wheels: *auto* (the default)
prefers `lua/lua51.exe` on Windows and lupa elsewhere, and the
`EXCALIBUR_RUNTIME=exe|lupa` environment variable overrides both, as does
`main.py --runtime exe|lupa|auto`. A standalone interpreter is a different code
path from lupa (it prints values instead of returning them and enforces the
watchdog in a separate process), so `tests/test_lua_runtime.py` runs the
acceptance fixture through it wherever such an interpreter can run.

## Selection and validation

`pick_payload.py` scores every candidate with explainable points: Lua construct
density, printable ratio, `loadstring`/`concat` provenance, penalties for
escaped-decimal runs, constant-arithmetic density, binary control characters and
"identical to the input". Nothing is keyed on identifier names.

`validate.py` has two profiles:

* **dynamic** - the candidate claims to be the original source, so the WRD
  wrapper and a large escaped-decimal pool are failures;
* **static** - the candidate is the rewritten constant layer: keeping the
  wrapper is expected, what matters is that the pool is gone, the text is valid
  Lua and it differs from the input.

Both profiles compile the candidate with a real Lua runtime when one is
available; when none is, compilation is skipped (and reported as such) rather
than guessed. A successful run is only marked `partial` when the winner came
from the static layer, and the report says so explicitly.

## Threading and error model

* Every pipeline call is a pure function; nothing writes to module-level state.
* The GUI runs the pipeline in a worker thread and exchanges messages with the
  UI through a `queue.Queue` drained by `root.after(80 ms, ...)`; the window is
  built before any heavy import happens.
* The core raises `ExcaliburError` subclasses (`core/errors.py`) for expected
  failures and never lets an unexpected exception escape a stage: the pipeline
  records it as a stage note and keeps going, so a broken input still produces a
  report.

### File naming

The original task description names two sandbox files that this repository keeps
inside `core/lua/` instead, because the whole Lua side is one loadable bundle:

| name in the task description | where it lives here |
|---|---|
| `core/roblox_stubs.lua` | `core/lua/roblox_stubs.lua` |
| `core/loadstring_hook.lua` | the `load`/`loadstring` half of `core/lua/hooks.lua` (installed by `core/lua/runner.lua`) |

`core/lua/runner.lua` locates its siblings through the `base_dir` entry of the
`EXCALIBUR` config table, so the folder can be moved as a unit.

## Artefact layout

```
%LOCALAPPDATA%/Excalibur/                (dev: <repo>)
  state.json          last bootstrap state (installed packages, python tag)
  runtime/site-packages   first-run dependency cache
  logs/gui.log        GUI level errors
  logs/run_<stamp>_<hash>/
      input.lua decoded.lua output.lua report.json summary.txt trace_summary.txt
      <runtime>_<policy>/  ... per-attempt artefacts ...
```

## Extension points

* `core/registry.py` - add a `Deobfuscator` subclass and register it.
* `core/config.py` - runtimes, policies, timeouts, instruction budget, payload
  thresholds.
* `gui/theme.py` - the palette and fonts; swapping theme never touches widgets.
