# `lua/lua51.exe` - the vendored Lua 5.1 interpreter

```
file    : lua51.exe
target  : Windows, x86_64, console (PE32+), statically linked, no lua51.dll
size    : 297,472 bytes
sha256  : 9d3c0e13a79c845305a49b30ec9d7aadd6bc4962ef32f7f56aba7d239328d51c
version : Lua 5.1.5 (Copyright (C) 1994-2012 Lua.org, PUC-Rio)
license : MIT - http://www.lua.org/license.html
```

WRD-era Roblox scripts target Lua 5.1 (executors shipped 5.1 / LuaJIT), so the
sandbox prefers this interpreter over the bundled lupa runtime **on Windows**;
everywhere else it stays with lupa (a Windows binary cannot run on Linux/macOS).
`EXCALIBUR_RUNTIME=exe|lupa` and `python main.py --runtime exe|lupa|auto`
override the choice. The interpreter is optional: without it nothing breaks,
`build.py exe` simply packages fewer bytes.

## Provenance

Unmodified **official Lua 5.1.5 sources**, cross-compiled here with the pinned
zig toolchain - no Windows machine, MSVC or mingw installation is involved:

| input | pinned by |
|---|---|
| `lua-5.1.5.tar.gz` (PUC-Rio release) | sha256 `2640fc56a795f29d28ef15e13c34a47e223960b0240e8cb0a82d9b0738695333` (md5 `2e115fe26e435e33b0d5c022e4490567`), mirrored in `dyne/luabinaries` because the GitHub blob API can serve it |
| `ziglang 0.13.0` wheel | sha256 `3ce0c9f16547e5d61b32e0d226926e9a2552ef4b91fccf7ab5ea1a623a77824b` (`manylinux_2_12_x86_64`); the Windows/macOS wheels are pinned too |

```bat
:: the exact command, run from lua-5.1.5/src (the source list is in tools/build_lua.py)
zig cc -target x86_64-windows-gnu -O2 -static -s -DLUA_USE_POPEN -o lua51.exe ^
    lua.c lapi.c lauxlib.c lbaselib.c lcode.c ldblib.c ldebug.c ldo.c ldump.c ^
    lfunc.c lgc.c linit.c liolib.c llex.c lmathlib.c lmem.c loadlib.c lobject.c ^
    lopcodes.c loslib.c lparser.c lstate.c lstring.c lstrlib.c ltable.c ltablib.c ^
    ltm.c lundump.c lvm.c lzio.c -lm
```

Two build details matter:

* **the COFF timestamp is zeroed** after linking (`IMAGE_FILE_HEADER.TimeDateStamp`).
  Without that the PE header carries the build time and two builds of identical
  sources never hash the same; with it, the build is reproducible bit for bit.
* `-DLUA_USE_POPEN` keeps `io.popen` available, matching the POSIX builds (the
  sandbox replaces `io` anyway).

The result imports only `KERNEL32.dll` and the Universal CRT
(`api-ms-win-crt-*`) - the UCRT is the same requirement the bundled Python 3.12
has, so the target machine already provides it.

## Verify, rebuild, or build a native twin

```bat
python tools/build_lua.py --check              :: hash + PE checks, works offline
python tools/build_lua.py --build              :: rebuild, must match the hash above
python tools/build_lua.py --native lua/lua51   :: same sources for this host -
                                               :: lets Linux/macOS dev machines
                                               :: exercise the exe runtime path
python build.py fetch-lua [--build]            :: the same through build.py
```

`tests/test_lua_runtime.py` asserts the committed hash, the PE headers and - when
an interpreter can run on the machine (`lua/lua51.exe` on Windows, or the native
twin) - that the acceptance fixture still comes out byte identical through it.
`tools/build_lua.py --build` is the check that the recipe above is still enough
to reproduce the committed file.
