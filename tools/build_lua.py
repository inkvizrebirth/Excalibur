"""Build (and verify) the vendored Windows Lua 5.1 interpreter.

``lua/lua51.exe`` is the interpreter WRD-era scripts were written for, and the
sandbox prefers it on Windows.  It is built from the **unmodified** Lua 5.1.5
release sources with the zig toolchain, which makes the build reproducible on
any host and leaves no MSVC/mingw installation as a prerequisite:

* ``lua-5.1.5.tar.gz`` - the official PUC-Rio release (md5
  ``2e115fe26e435e33b0d5c022e4490567``), mirrored inside the ``dyne/luabinaries``
  repository so that it can be fetched through the GitHub blob API;
* ``ziglang 0.13.0`` - a PyPI wheel that contains the whole compiler, so
  ``zig cc`` can cross compile to ``x86_64-windows-gnu`` without any toolchain
  packages;
* the COFF timestamp is zeroed after linking: the PE header otherwise records
  the build time and two builds of the same sources never match.

Usage::

    python tools/build_lua.py --check              # verify lua/lua51.exe (offline)
    python tools/build_lua.py --build              # rebuild it bit for bit
    python tools/build_lua.py --native /tmp/lua51  # same sources for this host,
                                                    # used to exercise the exe
                                                    # runtime on dev machines
    python tools/build_lua.py --check --json
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import platform
import shutil
import stat
import subprocess
import sys
import tarfile
import tempfile
import zipfile
from pathlib import Path
from typing import Dict, List, Optional

ROOT = Path(__file__).resolve().parent.parent
BINARY = ROOT / "lua" / "lua51.exe"

# --------------------------------------------------------------------- manifest
#: official Lua 5.1.5 sources, mirrored in a repository (fetched through the API)
SOURCE = {
    "name": "lua-5.1.5.tar.gz",
    "url": "https://api.github.com/repos/dyne/luabinaries/contents/lua-5.1.5.tar.gz",
    "blob": "78de4108ad071d4b98879f743caef3c6f1fb11d7",  # git blob sha1 of the file
    "sha256": "2640fc56a795f29d28ef15e13c34a47e223960b0240e8cb0a82d9b0738695333",
    "md5": "2e115fe26e435e33b0d5c022e4490567",
    "version": "Lua 5.1.5",
}

#: ziglang wheels (one per host) - the compiler is bundled, nothing to install
ZIG_VERSION = "0.13.0"
ZIG_WHEELS: Dict[str, dict] = {
    "manylinux_2_12_x86_64": {
        "filename": "ziglang-0.13.0-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64.whl",
        "url": "https://files.pythonhosted.org/packages/0c/b7/ecfdce6368cc3664d301f7f52db4fe1004aa7da7a12c4a9bf1de534ff6ab/"
               "ziglang-0.13.0-py3-none-manylinux_2_12_x86_64.manylinux2010_x86_64.musllinux_1_1_x86_64.whl",
        "sha256": "3ce0c9f16547e5d61b32e0d226926e9a2552ef4b91fccf7ab5ea1a623a77824b",
        "size": 80896325,
    },
    "win_amd64": {
        "filename": "ziglang-0.13.0-py3-none-win_amd64.whl",
        "url": "https://files.pythonhosted.org/packages/e0/0c/66f4710aedf5544e15779ff9c6e770322986e15daf9299b1a4df0be19e09/"
               "ziglang-0.13.0-py3-none-win_amd64.whl",
        "sha256": "b64b2aa936ebbfeecfbb2611df331a5474edebe1246b98c2f56d6ae4d58b71fc",
        "size": 80418705,
    },
    "macosx_12_0_x86_64": {
        "filename": "ziglang-0.13.0-py3-none-macosx_12_0_x86_64.whl",
        "url": "https://files.pythonhosted.org/packages/4b/38/4f2ef2b1d727d7317b08ef309e52d8c90089272b57d5d940c74524cc4315/"
               "ziglang-0.13.0-py3-none-macosx_12_0_x86_64.whl",
        "sha256": "d1b00173b8a5bfbaccb255240b8c091bd523c13743178bc248355ec6484fced7",
        "size": 83910175,
    },
    "macosx_12_0_arm64": {
        "filename": "ziglang-0.13.0-py3-none-macosx_12_0_arm64.whl",
        "url": "https://files.pythonhosted.org/packages/e6/14/3587387c715175ed5bb103c94c0df554fabac5bc97de153e9eec2fa905aa/"
               "ziglang-0.13.0-py3-none-macosx_12_0_arm64.whl",
        "sha256": "5408ad3a6cb342fb4e4e2351a3725adfcae82eaadebe85fdbbdad9c0ac8b1e24",
        "size": 81237662,
    },
}

#: the interpreter that ships in lua/ (x86_64, static, UCRT like Python 3.12)
BINARY_SHA256 = "9d3c0e13a79c845305a49b30ec9d7aadd6bc4962ef32f7f56aba7d239328d51c"
BINARY_SIZE = 297472

#: every translation unit of `lua` (lua.c is the interpreter, luac.c is left out)
SRCS: List[str] = [
    "lua.c", "lapi.c", "lauxlib.c", "lbaselib.c", "lcode.c", "ldblib.c", "ldebug.c",
    "ldo.c", "ldump.c", "lfunc.c", "lgc.c", "linit.c", "liolib.c", "llex.c",
    "lmathlib.c", "lmem.c", "loadlib.c", "lobject.c", "lopcodes.c", "loslib.c",
    "lparser.c", "lstate.c", "lstring.c", "lstrlib.c", "ltable.c", "ltablib.c",
    "ltm.c", "lundump.c", "lvm.c", "lzio.c",
]

#: io.popen is available on Windows too, matching the POSIX builds
DEFINES = ["-DLUA_USE_POPEN"]
DEFAULT_CACHE = ROOT / ".cache" / "lua-build"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with open(path, "rb") as handle:
        for chunk in iter(lambda: handle.read(1 << 20), b""):
            digest.update(chunk)
    return digest.hexdigest()


def zero_coff_timestamp(data: bytes) -> bytes:
    """Clear ``IMAGE_FILE_HEADER.TimeDateStamp`` so the build is reproducible."""
    if len(data) < 0x40 or data[:2] != b"MZ":
        return data
    pe = int.from_bytes(data[0x3C:0x40], "little")
    if pe + 12 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        return data
    out = bytearray(data)
    out[pe + 8:pe + 12] = b"\0\0\0\0"
    return bytes(out)


def pe_info(data: bytes) -> dict:
    """Machine/subsystem of a PE file (used by ``--check`` and the tests)."""
    info = {"pe": False, "machine": "", "subsystem": None, "size": len(data)}
    if len(data) < 0x40 or data[:2] != b"MZ":
        return info
    pe = int.from_bytes(data[0x3C:0x40], "little")
    if pe + 24 > len(data) or data[pe:pe + 4] != b"PE\0\0":
        return info
    info["pe"] = True
    info["machine"] = {0x8664: "x86_64", 0x14C: "i386", 0xAA64: "arm64"}.get(
        int.from_bytes(data[pe + 4:pe + 6], "little"), hex(int.from_bytes(data[pe + 4:pe + 6], "little"))
    )
    magic = int.from_bytes(data[pe + 24:pe + 26], "little")
    opt = pe + 24
    # Subsystem sits at the same offset in PE32 and PE32+ (ImageBase differs)
    info["subsystem"] = int.from_bytes(data[opt + 0x44:opt + 0x46], "little")
    info["pe32_plus"] = magic == 0x20B
    return info


# -------------------------------------------------------------------- downloads
def _download(url: str, *, timeout: int = 600) -> bytes:
    import urllib.request

    request = urllib.request.Request(url, headers={"User-Agent": "excalibur-build-lua"})
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch_source(cache: Path) -> Path:
    """Return the official ``lua-5.1.5.tar.gz`` (downloading it when needed)."""
    target = cache / SOURCE["name"]
    if target.exists() and sha256_file(target) == SOURCE["sha256"]:
        return target

    cache.mkdir(parents=True, exist_ok=True)
    data: Optional[bytes] = None
    # the contents API returns base64 for files below 1 MB - no raw host needed
    if shutil.which("gh"):
        try:
            result = subprocess.run(
                ["gh", "api", f"repos/dyne/luabinaries/git/blobs/{SOURCE['blob']}",
                 "--jq", ".content"],
                capture_output=True, text=True, timeout=180, check=True,
            )
            data = base64.b64decode("".join(result.stdout.split()))
        except Exception:  # pragma: no cover - depends on the network
            data = None
    if data is None:
        try:
            payload = json.loads(_download(SOURCE["url"], timeout=180))
            data = base64.b64decode("".join(payload["content"].split()))
        except Exception as exc:
            raise SystemExit(
                "cannot download the Lua sources; pass --tarball <lua-5.1.5.tar.gz> "
                f"or fix the network ({type(exc).__name__}: {exc})"
            ) from exc

    digest = sha256_bytes(data)
    if digest != SOURCE["sha256"]:
        raise SystemExit(f"source tarball hash mismatch: {digest} != {SOURCE['sha256']}")
    target.write_bytes(data)
    print(f"source   : {SOURCE['name']} ({len(data)} bytes, sha256 ok)")
    return target


def host_zig_tag() -> str:
    system, machine = platform.system().lower(), platform.machine().lower()
    if system == "windows":
        return "win_amd64"
    if system == "darwin":
        return "macosx_12_0_arm64" if machine in {"arm64", "aarch64"} else "macosx_12_0_x86_64"
    return "manylinux_2_12_x86_64"


def fetch_zig(cache: Path) -> Path:
    """Return the ``zig`` executable of the pinned compiler (downloaded if needed)."""
    tag = host_zig_tag()
    wheel = ZIG_WHEELS[tag]
    target_dir = cache / f"zig-{ZIG_VERSION}-{tag}"
    binary = target_dir / ("zig.exe" if os.name == "nt" else "zig")
    if binary.exists():
        return binary

    archive = cache / wheel["filename"]
    if not archive.exists() or sha256_file(archive) != wheel["sha256"]:
        cache.mkdir(parents=True, exist_ok=True)
        print(f"zig      : downloading {wheel['filename']} ({wheel['size'] // 1024} KiB)")
        data = _download(wheel["url"])
        digest = sha256_bytes(data)
        if digest != wheel["sha256"]:
            raise SystemExit(f"zig wheel hash mismatch: {digest} != {wheel['sha256']}")
        archive.write_bytes(data)

    target_dir.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(archive) as zf:
        zf.extractall(target_dir)
    found = next(target_dir.rglob("zig.exe" if os.name == "nt" else "zig"), None)
    if found is None:
        raise SystemExit("the zig wheel did not contain a compiler binary")
    found.chmod(found.stat().st_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    return found


def unpack_source(tarball: Path, workdir: Path) -> Path:
    with tarfile.open(tarball) as tf:
        tf.extractall(workdir)
    source_dir = workdir / "lua-5.1.5" / "src"
    if not source_dir.is_dir():
        raise SystemExit(f"unexpected tarball layout: no {source_dir}")
    return source_dir


# ----------------------------------------------------------------------- build
def compile_lua(zig: Path, source_dir: Path, out: Path, *, target: Optional[str]) -> Path:
    # the compiler runs with cwd=<source dir>, so the output path must be absolute
    out = Path(out).resolve()
    command = [str(zig), "cc", "-O2", "-static", "-s", *DEFINES]
    if target:
        command += ["-target", target]
    command += ["-o", str(out), *SRCS, "-lm"]
    out.parent.mkdir(parents=True, exist_ok=True)
    result = subprocess.run(command, cwd=source_dir, capture_output=True, text=True)
    if result.returncode != 0 or not out.exists():
        tail = (result.stderr or result.stdout or "").strip().splitlines()[-12:]
        raise SystemExit("compilation failed:\n  " + "\n  ".join(tail))
    out.write_bytes(zero_coff_timestamp(out.read_bytes()))
    try:
        out.chmod(out.stat().st_mode | stat.S_IXUSR)
    except OSError:  # pragma: no cover - exotic filesystems
        pass
    return out


def verify(path: Path = BINARY) -> dict:
    """Everything ``--check`` reports and the test suite asserts on."""
    report = {
        "path": str(path),
        "exists": path.is_file(),
        "size": path.stat().st_size if path.is_file() else 0,
        "sha256": sha256_file(path) if path.is_file() else "",
        "expected_sha256": BINARY_SHA256,
        "expected_size": BINARY_SIZE,
        "binary": SOURCE["version"],
    }
    data = path.read_bytes() if path.is_file() else b""
    report.update({f"pe_{key}": value for key, value in pe_info(data).items()})
    report["ok"] = bool(
        report["exists"]
        and report["sha256"] == BINARY_SHA256
        and report["size"] == BINARY_SIZE
        and report["pe_pe"]
        and report["pe_machine"] == "x86_64"
    )
    return report


def main(argv: Optional[List[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--check", action="store_true", help="verify lua/lua51.exe (default)")
    mode.add_argument("--build", action="store_true", help="rebuild lua/lua51.exe from source")
    mode.add_argument("--native", metavar="PATH",
                      help="build the same sources for this host into PATH")
    parser.add_argument("--tarball", metavar="PATH", help="use a local lua-5.1.5.tar.gz")
    parser.add_argument("--zig", metavar="PATH", help="use a local zig executable")
    parser.add_argument("--cache", metavar="DIR", default=str(DEFAULT_CACHE),
                        help="download cache (default: .cache/lua-build)")
    parser.add_argument("--out", metavar="PATH", help="output path (default: lua/lua51.exe)")
    parser.add_argument("--json", action="store_true", help="machine readable summary")
    args = parser.parse_args(argv)

    cache = Path(args.cache)

    if not args.build and not args.native:
        report = verify(Path(args.out) if args.out else BINARY)
        if args.json:
            print(json.dumps(report, indent=2))
            return 0 if report["ok"] else 1
        if not report["exists"]:
            print(f"{report['path']} is missing: run python tools/build_lua.py --build")
            return 1
        status = "ok" if report["ok"] else "MISMATCH"
        print(f"{report['path']}: {report['size']} bytes, sha256 {report['sha256'][:16]} "
              f"[{report['pe_machine']}, {report['binary']}] - {status}")
        if not report["ok"]:
            print(f"  expected sha256 {BINARY_SHA256} ({BINARY_SIZE} bytes)")
            return 1
        return 0

    tarball = Path(args.tarball) if args.tarball else fetch_source(cache)
    if sha256_file(tarball) != SOURCE["sha256"]:
        raise SystemExit(f"{tarball}: unexpected sha256 {sha256_file(tarball)}")
    zig = Path(args.zig) if args.zig else fetch_zig(cache)

    with tempfile.TemporaryDirectory(prefix="excalibur-lua-") as tmp:
        source_dir = unpack_source(tarball, Path(tmp))
        if args.native:
            out = Path(args.native)
            compile_lua(zig, source_dir, out, target=None)
            print(f"native   : {out} ({out.stat().st_size} bytes, sha256 {sha256_file(out)[:16]})")
            return 0

        out = Path(args.out) if args.out else BINARY
        compile_lua(zig, source_dir, out, target="x86_64-windows-gnu")

    report = verify(out)
    if args.json:
        print(json.dumps(report, indent=2))
    else:
        print(f"built    : {out} ({report['size']} bytes, sha256 {report['sha256']})")
        print(f"           {report['pe_machine']}, {report['binary']}")
        print("reproduced: bit for bit" if report["sha256"] == BINARY_SHA256
              else f"NOTE: differs from the pinned {BINARY_SHA256[:16]} (toolchain change?)")
    return 0 if report["ok"] else 1


if __name__ == "__main__":
    sys.exit(main())
