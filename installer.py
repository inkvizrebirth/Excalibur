from __future__ import annotations

import argparse
import hashlib
import importlib.metadata
import json
import logging
import os
import platform
import queue
import shutil
import subprocess
import sys
import threading
import time
import tarfile
import tempfile
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path, PurePosixPath
from typing import Any, BinaryIO

from core.runtime_paths import (
    DATA_ROOT,
    ENVLOG_PATH,
    HOOKS_PATH,
    IS_FROZEN,
    LICENSES_DIR,
    LOGS_DIR,
    OUTPUT_DIR,
    PACKAGED_TOOLS_DIR,
    RESOURCE_ROOT,
    TOOLS_DIR,
)
from core.version import VERSION

ROOT = RESOURCE_ROOT
REQUIREMENTS_FILE = ROOT / "requirements.txt"
MARKER_FILE = DATA_ROOT / ".installed"
SCHEMA_VERSION = 4
MIN_PYTHON = (3, 10)
NATIVE_HOST_LUAU_TAG = "0.740"
MAX_DOWNLOAD_BYTES = 128 * 1024 * 1024
DOWNLOAD_TIMEOUT_SECONDS = 45

DISTRIBUTIONS = (
    "customtkinter",
    "tkinterdnd2",
)

TOOL_NAMES = {
    "luau",
    "luau.exe",
    "luau-compile",
    "luau-compile.exe",
    "luau-analyze",
    "luau-analyze.exe",
}

ALLOWED_DOWNLOAD_HOSTS = {
    "api.github.com",
    "github.com",
    "raw.githubusercontent.com",
    "release-assets.githubusercontent.com",
    "objects.githubusercontent.com",
}

LOGGER = logging.getLogger("protez.installer")


class InstallationError(RuntimeError):
    pass


def configure_logging() -> None:
    logger = logging.getLogger("protez")
    logger.setLevel(logging.DEBUG)
    if logger.handlers:
        return
    formatter = logging.Formatter(
        "[%(asctime)s] %(levelname)s: %(message)s",
        datefmt="%H:%M:%S",
    )
    if IS_FROZEN:
        logger.propagate = False
        try:
            LOGS_DIR.mkdir(parents=True, exist_ok=True)
            handler = logging.FileHandler(LOGS_DIR / "startup.log", encoding="utf-8")
            handler.setFormatter(formatter)
            logger.addHandler(handler)
        except OSError:
            pass
        if sys.stderr is not None:
            stream_handler = logging.StreamHandler(sys.stderr)
            stream_handler.setFormatter(formatter)
            logger.addHandler(stream_handler)
        return
    logging.basicConfig(level=logging.INFO, format=formatter._fmt, datefmt="%H:%M:%S")


def check_python() -> None:
    if sys.version_info < MIN_PYTHON:
        required = ".".join(str(part) for part in MIN_PYTHON)
        current = platform.python_version()
        raise InstallationError(
            f"Python {required} or newer is required; found Python {current}."
        )


def ensure_directories() -> None:
    for path in (DATA_ROOT, LOGS_DIR, OUTPUT_DIR, TOOLS_DIR):
        path.mkdir(parents=True, exist_ok=True)
    if not IS_FROZEN:
        (ROOT / "assets/icons").mkdir(parents=True, exist_ok=True)


def _requirements_digest() -> str:
    try:
        content = REQUIREMENTS_FILE.read_bytes()
    except OSError as exc:
        raise InstallationError(f"Cannot read {REQUIREMENTS_FILE}: {exc}") from exc
    return hashlib.sha256(content).hexdigest()


def _native_host_binary_path() -> Path:
    suffix = ".exe" if platform.system().lower() == "windows" else ""
    return TOOLS_DIR / f"protez-native-host{suffix}"


def _native_host_source_digest() -> str:
    digest = hashlib.sha256(f"Luau:{NATIVE_HOST_LUAU_TAG}\n".encode("utf-8"))
    for relative_path in ("native/CMakeLists.txt", "native/host.cpp"):
        path = ROOT / relative_path
        try:
            content = path.read_bytes()
        except OSError as exc:
            raise InstallationError(f"Cannot read native host source {path}: {exc}") from exc
        digest.update(relative_path.encode("utf-8"))
        digest.update(b"\0")
        digest.update(content)
        digest.update(b"\0")
    return digest.hexdigest()


def _dependencies_available() -> bool:
    for distribution in DISTRIBUTIONS:
        try:
            importlib.metadata.version(distribution)
        except importlib.metadata.PackageNotFoundError:
            return False
    return True


def _marker_is_current() -> bool:
    try:
        marker = json.loads(MARKER_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return False
    if not isinstance(marker, dict):
        return False

    native_host_available = marker.get("native_host_available") is True
    suffix = ".exe" if platform.system().lower() == "windows" else ""
    cli_runtime_available = all(
        (TOOLS_DIR / f"{name}{suffix}").is_file()
        for name in ("luau", "luau-compile")
    )
    runtime_available = (
        _native_host_binary_path().is_file()
        if native_host_available
        else cli_runtime_available
    )
    return (
        marker.get("schema") == SCHEMA_VERSION
        and marker.get("app_version") == VERSION
        and marker.get("requirements_sha256") == _requirements_digest()
        and marker.get("native_host_source_sha256") == _native_host_source_digest()
        and isinstance(marker.get("native_host_available"), bool)
        and runtime_available
        and marker.get("dependencies_installed") is True
        and _dependencies_available()
    )


def _run_logged(
    command: list[str],
    *,
    label: str,
    cwd: Path,
    timeout_seconds: float,
) -> tuple[int, str]:
    LOGGER.info("Starting %s", label)
    LOGGER.info("Command: %s", subprocess.list2cmdline(command))
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    try:
        process = subprocess.Popen(
            command,
            cwd=cwd,
            stdin=subprocess.DEVNULL,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            bufsize=1,
            close_fds=True,
            creationflags=creationflags,
        )
    except OSError as exc:
        raise InstallationError(f"Could not start {label}: {exc}") from exc
    if process.stdout is None:
        process.kill()
        raise InstallationError(f"Could not capture output from {label}")

    lines: queue.Queue[str | None] = queue.Queue()

    def read_output() -> None:
        try:
            for line in process.stdout:
                lines.put(line.rstrip("\r\n"))
        finally:
            lines.put(None)

    reader = threading.Thread(target=read_output, name="protez-installer-output", daemon=True)
    reader.start()
    tail: list[str] = []
    reader_finished = False
    deadline = time.monotonic() + timeout_seconds
    while not reader_finished or process.poll() is None:
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            try:
                process.kill()
            except OSError:
                pass
            process.wait()
            reader.join(timeout=1.0)
            raise InstallationError(f"{label} exceeded the {timeout_seconds:.0f} second timeout")
        try:
            line = lines.get(timeout=min(0.15, remaining))
        except queue.Empty:
            continue
        if line is None:
            reader_finished = True
            continue
        if line:
            clipped_line = line[:2000]
            LOGGER.info("%s", clipped_line)
            tail.append(clipped_line)
            if len(tail) > 32:
                del tail[:-32]

    return process.wait(), "\n".join(tail)


def install_dependencies() -> None:
    command = [
        sys.executable,
        "-m",
        "pip",
        "install",
        "--disable-pip-version-check",
        "--retries",
        "2",
        "--timeout",
        "20",
        "-r",
        str(REQUIREMENTS_FILE),
    ]
    LOGGER.info("Installing Python dependencies from requirements.txt")
    last_code = 1
    last_output = ""
    for attempt in (1, 2):
        last_code, last_output = _run_logged(
            command,
            label=f"pip dependency install (attempt {attempt}/2)",
            cwd=ROOT,
            timeout_seconds=900,
        )
        if last_code == 0:
            LOGGER.info("Python dependencies installed")
            return
        if attempt == 1:
            LOGGER.warning("pip exited with code %s; repairing pip and retrying once", last_code)
            repair_code, repair_output = _run_logged(
                [sys.executable, "-m", "ensurepip", "--upgrade"],
                label="pip self-repair",
                cwd=ROOT,
                timeout_seconds=180,
            )
            if repair_code != 0:
                LOGGER.warning("ensurepip returned %s; retrying dependency installation", repair_code)
                if repair_output:
                    LOGGER.warning("ensurepip output: %s", repair_output)

    detail = f"\nRecent output:\n{last_output}" if last_output else ""
    raise InstallationError(
        f"Dependency installation failed twice (last exit code {last_code}). "
        "Check the connection and Python permissions, then choose Repair again."
        f"{detail}"
    )


def _check_download_url(url: str) -> None:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https" or parsed.hostname not in ALLOWED_DOWNLOAD_HOSTS:
        raise InstallationError(f"Refusing download from an untrusted URL: {url}")


def _download_file(
    url: str,
    destination: Path,
    *,
    sha256: str | None = None,
    max_bytes: int = MAX_DOWNLOAD_BYTES,
) -> None:
    _check_download_url(url)
    destination.parent.mkdir(parents=True, exist_ok=True)
    partial_path = destination.with_name(destination.name + ".part")
    digest = hashlib.sha256()
    total = 0
    request = urllib.request.Request(
        url,
        headers={"User-Agent": "ProtezInstaller/1.0", "Accept": "*/*"},
    )

    try:
        with urllib.request.urlopen(
            request, timeout=DOWNLOAD_TIMEOUT_SECONDS
        ) as response:
            _check_download_url(response.geturl())
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_bytes:
                raise InstallationError(
                    f"Download exceeds the {max_bytes // (1024 * 1024)} MB limit: {url}"
                )

            with partial_path.open("wb") as output:
                while True:
                    chunk = response.read(64 * 1024)
                    if not chunk:
                        break
                    total += len(chunk)
                    if total > max_bytes:
                        raise InstallationError(
                            f"Download exceeds the {max_bytes // (1024 * 1024)} MB limit: {url}"
                        )
                    digest.update(chunk)
                    output.write(chunk)

        if sha256 and digest.hexdigest().lower() != sha256.lower():
            raise InstallationError(f"SHA-256 checksum mismatch for {url}")
        os.replace(partial_path, destination)
    except (OSError, urllib.error.URLError, ValueError) as exc:
        raise InstallationError(f"Download failed for {url}: {exc}") from exc
    finally:
        partial_path.unlink(missing_ok=True)


def _platform_tokens() -> tuple[tuple[str, ...], tuple[str, ...]]:
    system = platform.system().lower()
    machine = platform.machine().lower()

    if system == "windows":
        platform_tokens = ("windows", "win32", "win64")
    elif system == "linux":
        platform_tokens = ("ubuntu", "linux")
    elif system == "darwin":
        platform_tokens = ("macos", "darwin", "mac")
    else:
        raise InstallationError(f"Luau binaries are not configured for {system!r}.")

    if machine in {"x86_64", "amd64", "x64"}:
        architecture_tokens = ("x86_64", "amd64", "x64")
    elif machine in {"aarch64", "arm64"}:
        architecture_tokens = ("aarch64", "arm64")
    else:
        architecture_tokens = ()

    return platform_tokens, architecture_tokens


def _select_release_asset(assets: list[dict[str, Any]]) -> dict[str, Any] | None:
    platform_tokens, architecture_tokens = _platform_tokens()
    candidates: list[tuple[int, dict[str, Any]]] = []
    known_architectures = ("x86_64", "amd64", "x64", "aarch64", "arm64")

    for asset in assets:
        name = str(asset.get("name", "")).lower()
        if not name.endswith((".zip", ".tar.gz", ".tgz")):
            continue
        if any(token in name for token in ("source", "symbols", "debug")):
            continue
        if not any(token in name for token in platform_tokens):
            continue

        named_architectures = [token for token in known_architectures if token in name]
        if named_architectures and architecture_tokens and not any(
            token in name for token in architecture_tokens
        ):
            continue
        if named_architectures and not architecture_tokens:
            continue

        score = 10 if name.startswith("luau") else 0
        if named_architectures:
            score += 20
        if name.endswith(".zip"):
            score += 2
        candidates.append((score, asset))

    if not candidates:
        return None
    candidates.sort(key=lambda candidate: candidate[0], reverse=True)
    return candidates[0][1]


def _read_latest_release() -> tuple[str, list[dict[str, Any]]]:
    url = "https://api.github.com/repos/luau-lang/luau/releases/latest"
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "ProtezInstaller/1.0",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        },
    )
    _check_download_url(url)
    try:
        with urllib.request.urlopen(
            request, timeout=DOWNLOAD_TIMEOUT_SECONDS
        ) as response:
            _check_download_url(response.geturl())
            data = json.load(response)
    except (OSError, urllib.error.URLError, json.JSONDecodeError) as exc:
        raise InstallationError(f"Could not query the official Luau releases: {exc}") from exc

    if not isinstance(data, dict) or not isinstance(data.get("assets"), list):
        raise InstallationError("GitHub returned an unexpected Luau release response.")
    return str(data.get("tag_name", "latest")), data["assets"]


def _safe_tool_name(member_name: str) -> str | None:
    basename = PurePosixPath(member_name.replace("\\", "/")).name.lower()
    return basename if basename in TOOL_NAMES else None


def _copy_tool(source: BinaryIO, filename: str, tools_dir: Path) -> None:
    destination = tools_dir / filename
    with destination.open("wb") as output:
        shutil.copyfileobj(source, output, length=64 * 1024)
    if platform.system().lower() != "windows":
        destination.chmod(0o755)


def _extract_zip(archive_path: Path, tools_dir: Path) -> list[str]:
    copied: list[str] = []
    with zipfile.ZipFile(archive_path) as archive:
        for member in archive.infolist():
            filename = _safe_tool_name(member.filename)
            if not filename or member.is_dir():
                continue
            mode = member.external_attr >> 16
            if mode and (mode & 0o170000) == 0o120000:
                continue
            with archive.open(member) as source:
                _copy_tool(source, filename, tools_dir)
            copied.append(filename)
    return copied


def _extract_tar(archive_path: Path, tools_dir: Path) -> list[str]:
    copied: list[str] = []
    with tarfile.open(archive_path, mode="r:*") as archive:
        for member in archive.getmembers():
            filename = _safe_tool_name(member.name)
            if not filename or not member.isfile():
                continue
            source = archive.extractfile(member)
            if source is None:
                continue
            with source:
                _copy_tool(source, filename, tools_dir)
            copied.append(filename)
    return copied


def _expected_tool_names() -> set[str]:
    suffix = ".exe" if platform.system().lower() == "windows" else ""
    return {f"luau{suffix}", f"luau-compile{suffix}", f"luau-analyze{suffix}"}


def download_luau_tools() -> tuple[list[str], list[str]]:
    tools_dir = TOOLS_DIR
    expected = _expected_tool_names()
    available = {name for name in expected if (tools_dir / name).is_file()}
    if available == expected:
        LOGGER.info("Luau command-line tools are already present")
        return sorted(available), []

    try:
        tag, assets = _read_latest_release()
        asset = _select_release_asset(assets)
        if asset is None:
            raise InstallationError(
                f"No Luau release archive matches {platform.system()} "
                f"{platform.machine()}."
            )
        url = str(asset.get("browser_download_url", ""))
        if not url:
            raise InstallationError("The matching Luau release asset has no download URL.")

        digest = asset.get("digest")
        checksum = None
        if isinstance(digest, str) and digest.startswith("sha256:"):
            checksum = digest.removeprefix("sha256:")

        with tempfile.TemporaryDirectory(prefix="protez-luau-", dir=tools_dir) as temp_dir:
            archive_path = Path(temp_dir) / str(asset.get("name", "luau-release.zip"))
            _download_file(url, archive_path, sha256=checksum)
            LOGGER.info("Downloaded Luau %s release asset: %s", tag, asset["name"])
            suffix = archive_path.name.lower()
            if suffix.endswith(".zip"):
                extracted = _extract_zip(archive_path, tools_dir)
            else:
                extracted = _extract_tar(archive_path, tools_dir)

        available.update(name for name in extracted if name in expected)
    except (InstallationError, OSError, tarfile.TarError, zipfile.BadZipFile) as exc:
        LOGGER.warning(
            "%s. Download the matching release manually from "
            "https://github.com/luau-lang/luau/releases and place the CLI tools in %s.",
            exc,
            tools_dir,
        )

    missing = sorted(expected - available)
    if missing:
        LOGGER.warning("Luau tools not found: %s", ", ".join(missing))
    else:
        LOGGER.info("Luau tools ready: %s", ", ".join(sorted(available)))
    return sorted(available), missing


def build_native_host() -> bool:
    tools_dir = TOOLS_DIR
    destination = _native_host_binary_path()
    cmake = shutil.which("cmake")
    if cmake is None:
        if destination.is_file():
            LOGGER.warning("CMake is unavailable; keeping the existing native host")
            return True
        LOGGER.warning(
            "CMake was not found; using the official Luau CLI fallback. "
            "Install CMake and a C++17 compiler, then rerun installer.py --force to enable VM tracing."
        )
        return False

    build_dir = tools_dir / "native-host-build"
    configure = [
        cmake,
        "-S",
        str(ROOT / "native"),
        "-B",
        str(build_dir),
        "-DCMAKE_BUILD_TYPE=Release",
    ]
    parallel_jobs = max(1, min(os.cpu_count() or 2, 4))
    build = [
        cmake,
        "--build",
        str(build_dir),
        "--config",
        "Release",
        "--target",
        "protez-native-host",
        "--parallel",
        str(parallel_jobs),
    ]

    for label, command in (("configure", configure), ("build", build)):
        try:
            return_code, output = _run_logged(
                command,
                label=f"native host CMake {label}",
                cwd=ROOT,
                timeout_seconds=1200,
            )
        except InstallationError as exc:
            LOGGER.warning("Native host %s did not complete: %s", label, exc)
            return destination.is_file()
        if return_code != 0:
            LOGGER.warning(
                "Native host %s failed (exit code %s); retaining CLI fallback%s",
                label,
                return_code,
                f":\n{output}" if output else "",
            )
            return destination.is_file()

    built_binary = build_dir / "host-bin" / destination.name
    if not built_binary.is_file():
        LOGGER.warning(
            "Native host build completed without producing %s; retaining CLI fallback",
            built_binary,
        )
        return destination.is_file()

    temporary_binary = destination.with_name(destination.name + ".tmp")
    try:
        shutil.copy2(built_binary, temporary_binary)
        if platform.system().lower() != "windows":
            temporary_binary.chmod(0o755)
        os.replace(temporary_binary, destination)
    except OSError as exc:
        temporary_binary.unlink(missing_ok=True)
        LOGGER.warning("Could not install native host: %s", exc)
        return destination.is_file()

    LOGGER.info("Instrumented Luau native host ready: %s", destination.name)
    return True


def _write_marker(
    available_tools: list[str],
    missing_tools: list[str],
    native_host_available: bool,
) -> None:
    marker = {
        "schema": SCHEMA_VERSION,
        "app_version": VERSION,
        "python_version": platform.python_version(),
        "requirements_sha256": _requirements_digest(),
        "dependencies_installed": True,
        "luau_tools_available": available_tools,
        "luau_tools_missing": missing_tools,
        "native_host_available": native_host_available,
        "native_host_luau_tag": NATIVE_HOST_LUAU_TAG,
        "native_host_source_sha256": _native_host_source_digest(),
    }
    temporary_marker = MARKER_FILE.with_name(MARKER_FILE.name + ".tmp")
    temporary_marker.write_text(
        json.dumps(marker, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    os.replace(temporary_marker, MARKER_FILE)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _repair_packaged_binary(packaged: Path, installed: Path, *, label: str, required: bool) -> None:
    if required and not packaged.is_file():
        raise InstallationError(f"Bundled {label} is missing from the executable resources")
    if packaged.is_file():
        try:
            needs_repair = (
                not installed.is_file()
                or installed.stat().st_size != packaged.stat().st_size
                or _sha256_file(installed) != _sha256_file(packaged)
            )
        except OSError:
            needs_repair = True
        if needs_repair:
            LOGGER.warning("Repairing missing or damaged %s from the built-in package", label)
            temporary = installed.with_name(installed.name + ".repair")
            try:
                shutil.copy2(packaged, temporary)
                if platform.system().lower() != "windows":
                    temporary.chmod(0o755)
                os.replace(temporary, installed)
            except OSError as exc:
                temporary.unlink(missing_ok=True)
                raise InstallationError(f"Could not repair the bundled {label}: {exc}") from exc
    elif not installed.is_file():
        raise InstallationError(f"The bundled {label} is missing and cannot be repaired offline")


def _run_version_check(binary: Path, *, expected: str, label: str) -> str:
    creationflags = getattr(subprocess, "CREATE_NO_WINDOW", 0) if os.name == "nt" else 0
    try:
        result = subprocess.run(
            [str(binary), "--version"],
            cwd=DATA_ROOT,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            text=True,
            encoding="utf-8",
            errors="replace",
            timeout=10,
            check=False,
            creationflags=creationflags,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise InstallationError(f"Could not validate the bundled {label}: {exc}") from exc
    output = (result.stdout or "").strip()
    if result.returncode != 0 or expected.lower() not in output.lower():
        raise InstallationError(
            f"The bundled {label} failed its health check (exit {result.returncode}): "
            f"{output or 'no diagnostic output'}"
        )
    LOGGER.info("%s check passed: %s", label.capitalize(), output)
    return output


def verify_frozen_runtime() -> None:
    if not IS_FROZEN:
        return
    ensure_directories()
    for required in (ENVLOG_PATH, HOOKS_PATH):
        if not required.is_file():
            raise InstallationError(f"Bundled runtime resource is missing: {required.name}")

    host_name = _native_host_binary_path().name
    host_path = _native_host_binary_path()
    _repair_packaged_binary(
        PACKAGED_TOOLS_DIR / host_name,
        host_path,
        label="native Luau host",
        required=True,
    )
    decompiler_name = "luau-decompiler.exe" if os.name == "nt" else "luau-decompiler"
    decompiler_path = TOOLS_DIR / decompiler_name
    _repair_packaged_binary(
        PACKAGED_TOOLS_DIR / decompiler_name,
        decompiler_path,
        label="offline Luau bytecode decompiler",
        required=True,
    )
    license_file = LICENSES_DIR / "luau-decompiler-mit.txt"
    if not license_file.is_file():
        raise InstallationError("The bundled bytecode decompiler license notice is missing")

    _run_version_check(host_path, expected="Protez native Luau host", label="Luau runtime")
    _run_version_check(decompiler_path, expected="luau-decompiler", label="bytecode decompiler")
    LOGGER.info("The executable includes its offline bytecode decompiler; no Rust install is required")


def ensure_installed(*, force: bool = False) -> None:
    configure_logging()
    if IS_FROZEN:
        LOGGER.info("Checking bundled Protez runtime")
        verify_frozen_runtime()
        return

    check_python()
    ensure_directories()

    if not force and _marker_is_current():
        LOGGER.info("Installation marker found; setup is already complete")
        return

    install_dependencies()
    available_tools, missing_tools = download_luau_tools()
    native_host_available = build_native_host()
    if not native_host_available:
        suffix = ".exe" if platform.system().lower() == "windows" else ""
        required_tools = {f"luau{suffix}", f"luau-compile{suffix}"}
        if not required_tools.issubset(available_tools):
            missing_runtime = ", ".join(sorted(required_tools - set(available_tools)))
            raise InstallationError(
                "No usable Luau runtime/compiler is available. "
                f"Missing: {missing_runtime}. Choose Repair again or check network access."
            )
    _write_marker(
        available_tools,
        missing_tools,
        native_host_available,
    )
    LOGGER.info("Protez prerequisites checked")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Install Protez prerequisites")
    parser.add_argument(
        "--force",
        action="store_true",
        help="reinstall/check dependencies and redownload missing resources",
    )
    arguments = parser.parse_args(argv)

    try:
        ensure_installed(force=arguments.force)
    except InstallationError as exc:
        LOGGER.error("%s", exc)
        return 1
    except Exception:
        LOGGER.exception("Unexpected installer error")
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
