# Changelog

## Unreleased

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
