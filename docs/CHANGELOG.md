# Changelog

## Unreleased

- **The executor surface is faithful where it matters most.**  Roblox locks the
  metatables of its instances: `getmetatable(instance)` answers with the string
  "The metatable is locked", and only the executor's own `getrawmetatable` sees
  the real table -- which is how payloads tell a live Roblox from a
  re-implementation, and how they hook `__namecall`.  Protez's instance proxies
  now behave the same way, its internal namecall dispatch reads the raw
  metatable, and `getrawmetatable(game).__namecall = hook` still reaches the
  payload's hook first (pinned by a test).
- **A remote body that cannot be fetched no longer takes the loader down.**  A
  failed fetch handed back an empty string, so `loadstring(game:HttpGet(url))()`
  produced nil and the loader died at its first call into the missing library --
  and everything the script would have decoded after that point was lost.  Both
  the HTTP bridge and `request` now return a placeholder chunk whose result
  tolerates indexing, calling, concatenation and length, so the script keeps
  running and keeps decoding its own protected payload.  (With the IronBrew1
  fixture the failure moves from the missing library into the payload's own
  decode loop.)
- The backend's traceback handler now reports up to 64 locals per frame (26 was
  not enough to see the variable that was actually nil) and the new
  `PROTEZ_EMU_CALL_LOG=<file>` records every environment-probing call a script
  makes -- `newproxy`, `getmetatable`, `hookfunction`, `getgenv` and friends --
  with its arguments and results, which is how a payload's expectations can be
  read straight off its last few calls.


- The Lua 5.1 lifter (the common path for WeAreDevs, IronBrew2/3, PSU, Nexus,
  MoonSec and every other bytecode family) now produces listings that actually
  parse, and no longer explode on obfuscated control flow:
  - **Instruction-level deduplication.**  Obfuscators overlap their branch
    regions on purpose; the lifter followed every path and re-emitted shared
    tails, turning a 9k-instruction dispatcher into a 250k-line listing full of
    half-open blocks.  Each instruction is now emitted once, and a path that
    reaches one already emitted ends with a short note.  MoonSec V3's recovered
    interpreter went from 250k unparseable lines to **11.8k lines that parse**
    (287 KB down from 3.4 MB, 0.2 s).
  - **Flat fallback.**  When a branch layout cannot be structured, the listing is
    re-emitted flat -- one instruction per line, control flow in comments --
    instead of leaving an unparseable structure behind.  Flat mode emits no
    blocks at all, including `return`/`break`.
  - **Structural verification.**  A listing is checked before it is handed on
    (unmatched `else`/`end`, `return` that does not end its block) and repaired
    or re-emitted flat, with a header line saying which happened.
  - Fixed three emissions that were syntactically invalid on their own:
    `SETGLOBAL` printed `"SomeName" = value` (the name is a string constant, and
    a name that is not an identifier belongs in `_G[...]`), a chunk with
    parameters or upvalues was printed as a bare `function(...) ... end`, and
    `...` was emitted inside functions that do not declare varargs (a stripped
    prototype can read varargs without carrying the flag).
  - A `_varargs` helper keeps `...` legal at every use site, the nested-prototype
    copy keeps the child's own nesting instead of flattening it, and the block
    scanner no longer copies the remaining listing per line (that made a 3 MB
    listing quadratic to scan).
- **MoonSec V3 without the offline tool.**  The shipped route needs an external
  devirtualizer and `unluac`; when they are absent the route now falls back to
  the portable backend, captures the interpreter chunk the wrapper dumps at run
  time, lifts it with Protez's own lifter, and uses that partial lift as the
  single result artifact (route `moonsec-v3-vm-lifter`, with a notice saying
  exactly what was and was not decoded).


- The portable backend now performs the **same work for every family**, instead
  of depending on what a loader happens to call:
  - The executor prelude, the table tagger and the VM dumper are set up *before*
    the step hook starts.  Charging Protez's own thousands of prelude statements
    to the hook's schedule left the VM dumper scanning its own tables while the
    payload ran; the backend also re-reporting its own executor-name list as an
    "instruction stream" — a confident dump that meant nothing.  Payload tables
    now carry `__protez_own` where they belong to Protez, the dumper skips
    tagged tables, and its scan schedule starts at the payload's first
    instruction.
  - The VM report refuses to confirm a stream it cannot justify: opcode and
    operand columns must have different shapes (repetitive opcodes, varied
    operands) before the dump is called an instruction stream, and otherwise the
    summary says plainly that no stream was confirmed and how many tables and
    constants were collected.
- Two host bridges inside the backend never worked: a Python callable crosses
  the `lupa` bridge as *userdata*, so the `type(fn) == 'function'` guards were
  always false.  That silently disabled the Luau lowering for chunks a loader
  builds at run time (`loadstring` of Luau source — v15-style wrappers) and the
  new position reporting.  Both now call through a tiny helper and are pinned by
  tests.
- Diagnostics that pay for themselves on every family:
  - `PROTEZ_EMU_TRACEBACK=1` runs the payload through `xpcall` with a handler
    that prints each frame *and its locals*, so a loader that catches its own
    error and later falls over on a `nil` register can be read directly from the
    backend's log.
  - `PROTEZ_EMU_POSITIONS=<file>` records where the script was (once per 200
    hook events and when the budget runs out), which is how the PSU fixture's
    extra-long tail was located even though it never trips the budget.
- `backend_terminates` caches its verdict for the rest of the recovery run: a
  loader that has to be killed inside the backend used to burn the full timeout
  on every layer, turning one slow fixture into a minute of wasted work.


- **Every fixture now ends as a readable script.**  The pipeline used to hand
  back minified wrappers unchanged: `format_luau` declines any input whose `if`
  is not a statement (every machine-made wrapper), and the single formatting path
  was gated on the Luau compiler, so `destroyed_N.lua` could be 16 lines of
  100 000 characters.  `core.formatter.break_statements` is the lexical fallback:
  it only inserts newlines, only where an expression provably cannot continue
  (`;`, `then`/`do`/`else`/`repeat`/`end`, a comma inside brackets, a statement
  keyword or a new assignment after a finished value), re-indents block bodies up
  to six levels and leaves every byte of program text alone.  Static-protection
  results now carry their report as a Lua comment block in front of the formatted
  wrapper preview, so the single result file stays loadable Lua.  All twelve
  `samples/real` fixtures land between 620 and 21 700 lines and re-parse as
  Lua/Luau; `dev/check_readability.py` proves it per result (line count, longest
  line of *code* ignoring data literals, token preservation, parse) and
  `tests/test_formatter.py` pins the breaker.
- Fixed three ways constant folding corrupted a recovered script.  Folding a
  span into a literal can fuse with its neighbours: `if c<(A+B)then` (minified
  Luau relies on the `)` that folding deletes) became the malformed number
  `256then`; `x-(A-B)` became the comment `x--5`, which swallowed the rest of the
  line and with it real `end`s; and dropping the parentheses of
  `([[MoonSec V3]]):gsub(...)` left a string where Lua needs a prefix expression.
  A replacement is now spaced or parenthesised exactly when the surrounding text
  requires it.
- The portable backend can no longer freeze the application.  A loader that
  catches the step-budget error inside its own `pcall` and keeps looping (the
  AztupBrew fixture did) runs forever inside one Lua call, where neither the
  instruction budget nor the pipeline deadline can reach it.  The backend now
  runs the script in a forked child first and only touches the loader in this
  process when that child returned; a child that has to be killed makes the run
  report the backend as skipped instead of hanging the GUI.  On the way the
  budget itself got harder to swallow: when it is spent, the step hook neuters
  every `pcall`/`xpcall`/`coroutine.resume` it can reach in the paused script
  (globals, upvalues and one level of their tables), so the next raise cannot be
  caught, and it re-escalates whenever the loader rebuilds its handlers.
- The expression parser no longer accepts a truncated span.  On an IronBrew3
  fixture it stopped parsing inside a function body (`105 or yz==((function()`)
  and the "fold" deleted the body's head; a span is now only trusted when its
  brackets balance and it starts and ends where an expression can.


- The portable backend now runs **Luau** source.  `core.devirt.luau_normalize`
  was written but never called, so every Luaph wrapper died on the first line
  with a Lua 5.1 syntax error; the backend probes with `loadstring` and lowers
  what does not compile: numeric separators (`0Xf5__e`), `!=`, compound
  assignment, `continue`, string interpolation, Luau's floor division (`a // b`
  -> `math.floor(a / b)`) and if-*expressions* (`z = if c then a else b` ->
  a one-shot closure, which keeps `false`/`nil` branches correct).  The
  `continue` pass no longer mistakes an if-expression for a block that needs an
  `end`.  With this, the Luraph v14.6 and v15.0 fixtures parse *and run*
  (previously both failed before executing a statement).
- The Lua bridge is byte-exact (`LuaRuntime(encoding="latin-1")`): a loader may
  hand the host raw binary (a dumped chunk, a packed table) without the run
  dying on `UnicodeDecodeError`.  MoonSec v3 now dumps its 131 KB interpreter
  chunk this way.
- `core.luau_compat` provides `string.pack`/`unpack`/`packsize` (Lua 5.3 format
  strings on `struct`) as real Lua functions, so an IronBrew3 wrapper's
  `string.pack and string.unpack` gate passes and the loader runs to completion.
- The executor prelude gained Luau's `buffer` and `vector` libraries plus
  `table.move`/`clone`, `math.noise`, `bit32.byteswap`, `coroutine.close` and
  `utf8` additions.  Luraph v15 builds its chunk inside `buffer` and its
  constants with `vector`; both used to stop the run at the first call.
- `core/lua51.py`: the structured lifter no longer explodes on an obfuscated
  jump table.  It refuses to re-enter a region it is already lifting and stops
  at a step budget with a line in the output that says so — the MoonSec v3
  interpreter chunk (112-instruction root, overlapping branch layouts) used to
  spend minutes of CPU and look like a hang; it now lifts in ~1.3 s.
- `core.devirt.wrd` (WeAreDevs/WRD string-pool recovery) is wired into the
  family registry ahead of the generic bytecode method and pinned by tests.
- Luraph **v14.7-v14.9** wrappers are now devirtualized the same way v15 is: the vendored MIT engine gained its v14 front end (repeat-dispatchers, prototype-as-argument-0 factories, initializer-scoped helpers, symbolic holes for not-yet-materialized tables), Protez routes a `v14.x` banner or a stripped v14 entry tail (`...}):t()(...)`) to it, and the payload root is picked engine-side because the runtime capture reports Luraph's anti-tamper prototype first. The shared lifter then walks the real dispatch loop with symbolic registers, rebuilds control flow, and runs the same naming/local-function/formatting passes as v15. A v14.7 container is one flat prototype namespace per VM — the entry prototype is only the program's main chunk — so the whole namespace is lifted: the entry plus every sibling prototype is emitted as a labelled `proto_<id>` function with its own opcode count, Luraph's anti-tamper-shaped prototypes (a deep register file and thousands of guard opcodes) are skipped and reported instead of being passed off as script code, and the emitted file is Luau-parser clean; the report, notice and log lines name the family that actually ran. Every pass that spawns a Luau parser now uses Protez's bounded `luau-ast` adapter instead of the vendor's unbounded subprocess call.
- Rebuilt the desktop interface in a pixel style: bitmap-font chrome, segmented progress blocks, a compact option row (executor profile, remote-payload switch, `script_key`) and an in-app result viewer with line numbers, Lua highlighting and search. The viewer opens automatically when a run finishes; intermediate artifacts are parked under `logs/` so `output/` keeps exactly one `destroyed_N.lua` per run.
- The default executor profile is now **Real**, a fictional executor with the full command surface (144 features). `core.executor_api` gives the sandbox a working file API (`writefile`, `appendfile`, `readfile`, `isfile`, `isfolder`, `makefolder`, `delfile`, `delfolder`, `listfiles`, `loadfile`, `getcustomasset`), HTTP tables (`request`/`http_request`/`HttpGet*`/`fetch`), `crypt` (base64/hex/HMAC/SHA-256 in pure Lua), identity and HWID functions, `hookfunction`/`hookmetamethod`/`newcclosure`, the `debug` helpers and a recorded input surface, so scripts that refuse to run outside a real injector boot normally. Files written by a script are mirrored into `logs/executor-workspace/` and reported.
- Namecall hooks work the way dumpers expect: `hookmetamethod(game, "__namecall", hook)` and the classic `getrawmetatable(game).__namecall = hook` / `__index` swap both see `game:HttpGet(...)` and friends with the real arguments, `getnamecallmethod()` is set during the hook, and a hook that errors falls back to the emulated call instead of killing the run.
- Payloads that only exist at runtime are now recovered: bodies pulled through `request`/`HttpGet` are captured (and reported with their URL and method), files a loader writes are picked up as recovery candidates (bytecode is decompiled), and the copy of them under `logs/executor-workspace/` mirrors what the loader had on disk. This covers "API защита" loaders whose body cannot be opened as a raw link and is only served to a running executor with the right request body.
- The recovery engine reports the richest portable-backend run (the loader, not the tiny deobfuscated layer), the remote cache is per-run (`logs/remote_cache`) instead of shared, and empty `loadstring` chunks are no longer recorded as captures.
- Added `core.injector_env`: executor profiles (Synapse X, Krnl, Fluxus, Solara, Delta, Wave, Xeno, Hydrogen, Swift, Script-Ware, WeAreDevs v2.4, mobile executors, ...) with marker globals, feature probes and a Roblox proxy surface. The same environment is synthesised both as a static evaluator table and as a Lua prelude, so scripts that bootstrap from `identifyexecutor`, `getgenv`, `syn.protect_gui`, `isfunction`-style probes or `game:GetService(...)` no longer die on the first nil.
- Added `core.remote_payloads` plus the two-pass HTTP prelude: loaders that fetch their payload from a private library (for example a Luarmor `api.luarmor.net` loader) are resolved by running the loader inside the portable backend with a bounded fetch bridge, and the native worker receives the captured responses on the second pass. Fetches are cached, size-limited and reported.
- Added the portable Lua 5.1 backend (`core.emulator`) for environments where the native worker or its isolation tools cannot start: capability-stripped in-process execution, instruction/time budgets, `loadstring`/`load` capture, `string.dump` capture and full fetch reporting.
- Wrote Protez's own recovery methods for the families where no usable open-source lifter exists (network access to upstream repositories is unavailable in the build sandbox, so bundling more third-party tools was not an option): encoded-blob recovery now turns `{104,101,108,108,111}` arrays, `string.char(...)` calls, escape runs, hex and base64 payloads back into **Lua source** as well as into bytecode (`core.families.scan_embedded_source`), and `core.vm_dump` + `core.vm_recover` read a loader's own VM at run time — instruction stream, stride, opcode histogram, constant pool and a bounded disassembly — with an honest note that opcode semantics need a per-family map. `docs/FAMILIES.md` states the detection evidence, recovery path and typical result for Luraph v14/v15, WeAreDevs v2.4, Wynfuscate v5, IronBrew3, Prometheus, Nexus v2.0, PSU v1.0, MoonSec, AztupBrew, Xen, Synapse and generic custom VMs, and `tests/test_family_samples.py` pins each of them with a synthetic sample.
- The portable backend now samples the loader's VM tables while it runs: a second step callback (chained with the instruction budget, so a script still cannot clear it) walks the call stack, snapshots large array-like tables with a growth-aware guard, and hands them to the host as bounded snapshots. Numeric and string tables have separate budgets so a constant pool can never starve the instruction stream, and the sampling is dense early and sparse later to stay cheap on long payloads.
- Expanded family coverage and reporting: Luraph v14/v15, MoonSec V2/V3, WeAreDevs v2.4, Wynfuscate v5, IronBrew 2/3, Prometheus, Nexus v2.0, PSU v1.0, AztupBrew, Xen, Synapse-protected payloads and a generic custom-VM detector, each with version extraction from the input. Unknown VMs still go through the layered engine.
- Added static Lua 5.1 bytecode recovery (`core.lua51`): chunk reader, disassembler and a control-flow lifter that now also finds chunks hidden in decimal/hex byte arrays — the shape IronBrew, WeAreDevs v2.4, PSU and Nexus loaders use — and emits one readable statement per line.
- Added the layered recovery engine (`core.engine`) that chains static decoding, remote payload resolution, embedded bytecode lifting, the portable backend and the native worker, with per-layer hashes in the report.
- Formatting now preserves the author's line breaks between statements instead of gluing them into one line, so the viewer shows real code rather than a wall of text; continuation lines (`=`/operators/`,`/open brackets) are still joined and block bodies are re-indented.
- Plain or already-readable scripts are returned as written: a constant/string decode is only adopted when the input is a machine-made blob, loses a real layer (escapes, hex, base64) or is a minified one-liner. Lifted bytecode listings are marked partial and are never re-flowed.
- `PipelineResult.status` now matches the written banner and the report's `partial` flag for engine runs, and lifted bytecode is only allowed to preempt a family route when it is real work (never a static echo).
- Dependencies: dropped the unused `customtkinter`, added `requirements-portable.txt` for the optional `lupa` runtime (installed best-effort by `installer.py`, bundled into the Windows build), and `core.pipeline` now also finds a developer build of the native host in `native/build/host-bin`.
- Every string the pixel font draws now has a real glyph (the window's minimise sign, em dashes and the ellipsis were falling back to `?`); a test walks `gui/` and fails if any label would render a placeholder.
- Added `scripts/render_ui_preview.py`, which renders the window chrome and the viewer with the real palette, bitmap font and syntax colours into `docs/preview/*.png`. The build sandbox has no display, so these are faithful mock-ups for review rather than screenshots.
- Added `core.devirt`: own devirtualizers per family (`bytecode_vm`, `nexus`, `table_vm`, `prometheus`, `luraph` + a registry).  Highlights: a Lua 5.1 chunk is rebuilt from the *runtime* table a loader filled (the door static passes cannot open), payloads split across `"…" .. "…"` runs are reassembled, VM opcodes are named from the loader's own dispatcher, pool constants are inlined into the disassembly, and Prometheus-style control-flow flattening is removed into straight-line code — but only when the state graph is fully known.
- VM dumps are written as `logs/vm_surface_<report>.txt` and, when nothing else was lifted, the result notice says so (`custom VM surface recovered: N instructions, M distinct opcodes, K constants`), so `output/` still holds exactly one `destroyed_N.lua`.
- Added `tests/test_vm_recovery.py` (snapshot parsing, stride detection, scoring, listing) and `tests/test_family_samples.py` (a synthetic protected sample per family, each asserting detection and one working recovery method, plus a pipeline test that the `vm` block reaches the report).
- Added tests for the injector environment (including Lua-side probes), the executor command surface and the XDumper-style `getgenv().loadstring` hook plus `setfenv` sandbox pattern (identity, file API, dumper-style namecall hooks, request/download capture), the portable backend, family detection, embedded bytecode scanning, the remote/Luarmor chain and an end-to-end API-protected loader whose payload only exists at runtime, output policy and the pixel-font/highlighter logic used by the interface.
- Preserve isolated Luraph `loadstring` captures as separate, hash-reported artifacts. A large captured body is promoted to source only after Luau validation and when it has no recognized VM signature or nested remote fetch; otherwise it remains a partial candidate.
- Mark syntactically valid MoonSec output partial when strict source lifting reports errors, the output contains an unluac diagnostic marker, or it loads more Lua over HTTP. Keep the candidate, static preview, bytecode, and partial reasons in the report.
- Expand the Windows family smoke run with pinned real Luraph v15 and MoonSec V3 samples. The smoke suite distinguishes recoverable local source from loader-only wrappers whose fetched payload is not embedded.

## 2026-10-06 — 0.6.2

- Report incomplete Luraph lifts when generated output still contains unresolved constants, missing VM values, closures, iterators, tail calls, or runtime helpers. Remove unused generated error stubs from candidate source.
- Build the native, Rust, and MoonSec Windows support tools in parallel, then package and publish only `Protez.exe`.

## 2026-10-06 — 0.6.1

- Fixed the sandbox runtime for the supported Luraph v15 VM layout by exposing a monotonic, side-effect-free `os.clock()` and reading trace locals without mutating the active Luau stack. The instruction hook no longer changes Luau's callback table while code is running. Windows AppContainer smoke recovery now produces syntax-checked source for the pinned Luraph v15 and MoonSec V3 samples.

## 2026-10-06 — 0.6.0

- Added family-specific readable-source recovery for supported Luraph v15 and MoonSec V3 VM layouts. Luraph v15 uses the pinned MIT lifter in Protez's isolated Luau runtime; MoonSec V3 statically maps supported handlers to Lua 5.1 bytecode and decompiles it with pinned `unluac-rs`. The pipeline validates recovered source as Luau, writes real bytecode/disassembly artifacts on partial runs, and reports that semantic equivalence is not established. This is version/family-aware coverage, not a universal VM deobfuscator.
- Bundled separate MoonSec and Lua bytecode helper executables and their licenses/source in the Windows build; source installations can build/download these tools when available. Bumped the application version to 0.6.0.
- Replaced the no-op dynamic loader capture with real bounded Luau compilation. `loadstring`/`load` return executable functions in the same Luau state; wrapper-invoked chunks are traced when they run. Roblox Engine APIs are not faked.
- Added Windows AppContainer/Job Object and Linux bubblewrap/prlimit isolation for dynamic source runs, with fail-closed behavior when the native worker or isolation tools are unavailable. Windows application no longer requests Administrator elevation.
- Pipeline runs collect Luau VM instruction traces alongside payload capture, trace nested loader candidates, and report trace paths, isolation backend, execution outcome, and captured chunk metadata. Unsupported protected variants receive explicit partial reports.
- Added bounded, local-only static extraction for recognized Luraph LPH LZ/Zstandard containers. The extracted custom bytecode is only lifted when it matches the supported Luraph v15 VM family; unsupported layouts/versions remain partial.
- Added the `zstandard` runtime dependency to the self-contained Windows package and deterministic tests for static stream decoding, size limits, and report output.

## 2026-10-05 — 0.4.0

- Added static Luau bytecode decompilation through the bundled offline `luau-decompiler` CLI; bytecode and recovered source are not executed. Reports record provenance only when a frozen build's active binary matches the packaged copy and document lossy recovery and the upstream-documented v3–v9 scope.
- Added bounded, token-preserving whitespace formatting for supported Luau source. The pipeline keeps formatted output only after a compile-only syntax check; unsupported syntax or a failed check leaves the candidate unchanged.
- Removed rounded UI corners and pixel-font loading. The compact desktop UI now uses crisp system and monospace fonts while preserving the sword icon, Paste/File, Browse fallback, optional drag-and-drop, queued logs, background processing, and UAC behavior.
- The Windows workflow builds the pinned offline decompiler and packages its MIT notice. GitHub Releases remain limited to `Protez.exe`; the installer stays a CI artifact.

## 2026-10-05 — 0.3.0

- Tightened the main desktop window and added a white pixel-sword application/window icon.
- Configured the Windows application to request Administrator approval at launch; static analysis remains available when elevated, while dynamic sandbox execution and tracing are skipped.
- Added static Luraph VM detection and a clearly labeled partial report with wrapper strings and a non-executable preview. The report explicitly states that the original source is not reconstructed.
- Kept the release upload limited to `Protez.exe`; the separate installer remains a CI artifact.

## 2026-10-05 — 0.2.0

- Added a bounded static Luau tokenizer/evaluator for constant strings, arithmetic, bitwise helpers, Base64, and table concatenation; unknown expressions are preserved rather than executed.
- Expanded the pipeline to explore locally captured payload layers with compile-only validation, candidate/depth/time caps, valid-source fallback, and a JSON analysis report. Full VM-handler lifting and source reconstruction remain out of scope.
- Added a timestamped startup/repair window and streamed prerequisite/build output to the UI through a logging queue.
- Added a Windows x64 build workflow for a self-contained `Protez.exe` and elevated, user-selectable `Protez-Setup.exe`. Setup verifies the embedded app checksum, supports repair/reinstall, and creates shortcuts; the installed app runs without elevation.
- Added Python-only unit tests for the static decoder and a packaged runtime health check.
- Refined the desktop UI into a compact `PROTEZ` window; removed secondary output/copy controls, fixed Windows pixel-font enumeration, and made successful results open automatically.
- Added safe text-only handling for direct code URLs and simple linked `loadstring`/`HttpGet` loaders, with public-host checks, redirect validation, byte/time limits, and URL-resolution regression tests.
- Improved readability, replaced outlined window controls, added a custom vector P-mark, rounded native window corners, a restrained animated gradient outline, and short open/close fade animations. The primary action now has an explicit click log and visible busy/error states.
- Fixed startup crash in the animated outline by relying on widget stacking order instead of calling the Canvas item-lowering method without an item ID.
- Updated the Windows release workflow to publish only the standalone `Protez.exe` asset; the setup executable remains out of Releases.

## 2026-10-04

- Reworked the desktop shell as a compact monochrome, pixel-font, frameless window with custom title-bar controls and manual resizing.
- Added an optional C++ Luau 0.740 host using `lua_singlestep`/`debugstep`, unoptimized/full-debug compilation, version-pinned VM internals for proto-relative PCs and opcode decoding, bounded VM memory, sampled local snapshots, and trace-event caps; the installer retains the official CLI fallback when a CMake/C++ build is unavailable.
- Routed sandbox and tracer runs through the native host when installed, while keeping payload capture and the existing mock/API trace transport.
- Clarified that full register recovery, control-flow lifting, and source reconstruction remain unimplemented.
- Added the repository scaffold, prerequisite installer, and desktop GUI shell.
- Added a Luau subprocess mock environment with payload capture and timeout/output limits.
- Added the valid-Luau fast path: compile-check captured source and write it to `output/`.
- Added streaming trace-event transport, 100 MB JSONL rotation, and native-hook capability detection; stock Luau currently yields sandbox/API events only.
