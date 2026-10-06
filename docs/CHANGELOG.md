# Changelog

## Unreleased

- Added bounded, local-only static extraction for recognized Luraph LPH container layouts: Ascii85 framing with single/two-stream Zstandard or legacy two-stream raw LZMA1/range streams. Protez saves intermediate VM-interpreter/custom-bytecode artifacts and records sizes, hashes, and safety flags. This does not devirtualize the custom VM or reconstruct original Luau; unsupported variants remain explicitly partial. The wrapper, interpreter, and payload are never executed.
- Added the `zstandard` runtime dependency to the self-contained Windows package and deterministic tests for stream decoding, limits, report output, and the no-execution path.

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
