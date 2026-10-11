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

When no payload validated, the most dispatch-like `while` loop(s) get
`__sandbox_trace_state(<state>)` injected at the top of the body and the
instrumented source is re-run. The visited states are summarised (distinct
count, hottest states, most frequent transitions, repeated cycles) and written
to `trace_summary.txt`. This is the input a devirtualiser needs; the module does
not claim to reconstruct the source.

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
