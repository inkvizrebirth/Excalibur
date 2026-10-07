# Changelog

## Unreleased

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
