# Changelog

## 2026-10-04

- Reworked the desktop shell as a compact monochrome, pixel-font, frameless window with custom title-bar controls and manual resizing.
- Added an optional C++ Luau 0.740 host using `lua_singlestep`/`debugstep`, unoptimized/full-debug compilation, version-pinned VM internals for proto-relative PCs and opcode decoding, bounded VM memory, sampled local snapshots, and trace-event caps; the installer retains the official CLI fallback when a CMake/C++ build is unavailable.
- Routed sandbox and tracer runs through the native host when installed, while keeping payload capture and the existing mock/API trace transport.
- Clarified that full register recovery, control-flow lifting, and source reconstruction remain unimplemented.

- Added repository scaffold, prerequisite installer and desktop GUI shell.
- Added a Luau subprocess mock environment with payload capture and timeout/output limits.
- Added the valid-Luau fast path: compile-check captured source and write it to `output/`.
- Added streaming trace-event transport, 100 MB JSONL rotation, and native-hook capability detection; stock Luau currently yields sandbox/API events only.
