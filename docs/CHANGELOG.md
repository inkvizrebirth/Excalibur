# Changelog

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

## 2026-10-04

- Reworked the desktop shell as a compact monochrome, pixel-font, frameless window with custom title-bar controls and manual resizing.
- Added an optional C++ Luau 0.740 host using `lua_singlestep`/`debugstep`, unoptimized/full-debug compilation, version-pinned VM internals for proto-relative PCs and opcode decoding, bounded VM memory, sampled local snapshots, and trace-event caps; the installer retains the official CLI fallback when a CMake/C++ build is unavailable.
- Routed sandbox and tracer runs through the native host when installed, while keeping payload capture and the existing mock/API trace transport.
- Clarified that full register recovery, control-flow lifting, and source reconstruction remain unimplemented.
- Added the repository scaffold, prerequisite installer, and desktop GUI shell.
- Added a Luau subprocess mock environment with payload capture and timeout/output limits.
- Added the valid-Luau fast path: compile-check captured source and write it to `output/`.
- Added streaming trace-event transport, 100 MB JSONL rotation, and native-hook capability detection; stock Luau currently yields sandbox/API events only.
