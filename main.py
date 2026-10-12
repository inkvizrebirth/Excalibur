"""Excalibur entry point - used by the EXE and for source checkouts.

Usage::

    Excalibur.exe                     launch the GUI
    Excalibur.exe script.lua          launch the GUI with the file loaded
    Excalibur.exe --cli script.lua    deobfuscate on the console (CI friendly)
    Excalibur.exe --detect script.lua print the format report and exit
    Excalibur.exe --boot              run the first-run setup and exit
    Excalibur.exe --version           print the version and exit

Nothing heavy is imported before the window exists: the GUI must appear in
under three seconds even on a cold start.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import List, Optional

__version__ = "1.0.0"


def _print(text: str = "", **kwargs) -> None:
    try:
        print(text, **kwargs)
    except Exception:  # pragma: no cover - exotic consoles
        pass


def _console_log_path() -> Optional[Path]:
    """Where a windowed build sends the text that has no console to go to."""
    try:
        from core import paths

        return paths.app_data_dir() / "logs" / "exe.log"
    except Exception:  # pragma: no cover - paths is tiny, this is belt and braces
        return None


def _setup_stdio() -> Optional[Path]:
    """Give ``sys.stdout``/``sys.stderr`` somewhere to live.

    A ``--windowed`` PyInstaller build has no console, so Python starts with both
    set to ``None``: ``print`` becomes a silent no-op and a traceback is lost.  The
    packaged EXE is therefore run as ``Excalibur.exe --cli input.lua --out ...``
    with *nothing* to inspect on failure.  Mirroring the streams into
    ``%LOCALAPPDATA%/Excalibur/logs/exe.log`` keeps the diagnostics, and pointing
    the real file descriptors there means the Lua child processes log too.
    """
    if sys.stdout is not None and sys.stderr is not None:
        return None
    log_path = _console_log_path()
    if log_path is None:
        return None
    try:
        log_path.parent.mkdir(parents=True, exist_ok=True)
        stream = open(log_path, "a", encoding="utf-8", errors="replace", buffering=1)
        os.dup2(stream.fileno(), 1)
        os.dup2(stream.fileno(), 2)
    except Exception:
        return log_path
    if sys.stdout is None:
        sys.stdout = stream
    if sys.stderr is None:
        sys.stderr = stream
    return log_path


def _log_crash(exc: BaseException) -> None:
    """Record an unexpected exception where the user (and CI) can read it."""
    import traceback

    try:
        sys.stderr.write("Excalibur crashed: " + "".join(
            traceback.format_exception(type(exc), exc, exc.__traceback__)))
        sys.stderr.flush()
    except Exception:  # pragma: no cover
        pass


def run_cli(args: argparse.Namespace) -> int:
    """Head-less deobfuscation (also what the CI smoke test uses)."""
    from core.config import PipelineConfig, SandboxConfig
    from core.deobfuscate import deobfuscate_file

    path = Path(args.cli)
    if not path.exists():
        _print(f"no such file: {path}")
        return 2

    def progress(stage: str, message: str) -> None:
        if not args.quiet:
            _print(f"[{stage}] {message}")

    config = PipelineConfig(
        sandbox=SandboxConfig(
            timeout=args.timeout,
            prefer_exe={"auto": None, "exe": True, "lupa": False}[args.runtime],
        ),
        prefer_static=not args.no_static,
        run_dynamic=not args.no_dynamic,
        trace_on_failure=not args.no_trace,
        lift=not args.no_lift,
    )
    result = deobfuscate_file(path, config=config, progress=progress)

    if args.json:
        _print(json.dumps(result.as_dict(), indent=2, ensure_ascii=False))
    else:
        _print(result.summary_text())
    if args.out:
        stdout_path = Path(args.out)
        try:
            from core.sourceio import write_source

            write_source(stdout_path, result.output or "", encoding="utf-8")
            _print(f"written: {stdout_path}")
        except Exception as exc:
            _print(f"cannot write {stdout_path}: {exc}")
            return 1
    elif result.output_path:
        _print(f"output : {result.output_path}")
    if args.lift and result.pseudocode:
        from core.sourceio import write_source

        target = Path(args.lift)
        write_source(target, result.pseudocode, encoding="utf-8")
        _print(f"pseudo : {target}")
    elif result.pseudocode_path:
        _print(f"pseudo : {result.pseudocode_path}")
    return 0 if result.success else 1


def run_detect(path: Path) -> int:
    from core.registry import detect_and_route
    from core.sourceio import read_source

    source = read_source(path)
    route = detect_and_route(source.text)
    _print(f"route      : {route.message}")
    _print(f"format     : {route.detection.format}")
    _print(f"version    : {route.detection.version or 'unknown'}")
    _print(f"confidence : {route.detection.confidence:.0%}")
    _print(f"reason     : {route.detection.reason}")
    for key, value in sorted(route.detection.features.items()):
        _print(f"  {key}: {value}")
    for warning in route.detection.warnings:
        _print(f"  warning: {warning}")
    return 0 if route.detection.is_obfuscated else 1


def run_doctor(*, offline: bool = False) -> int:
    """Print where everything lives and whether it works.

    The packaged EXE runs inside a PyInstaller ``_MEIPASS`` directory with no
    console, so "why is the bundled interpreter not used?" is otherwise very hard
    to answer - for the user *and* for CI.  ``--doctor`` answers it in one screen:
    paths, the bootstrap report, every discovered runtime with its probe result,
    and the reason a runtime was rejected.
    """
    import platform

    from core import paths

    _print(f"Excalibur {__version__} doctor")
    _print(f"python      : {platform.python_version()} ({platform.system()} {platform.machine()})")
    _print(f"frozen      : {paths.is_frozen()}")
    _print(f"resources   : {paths.resource_root()}")
    _print(f"lua dir     : {paths.lua_dir()}")
    _print(f"app data    : {paths.app_data_dir()}")
    _print(f"logs        : {paths.logs_dir()}")
    for name in ("lua51.exe", "lua54.exe", "lua51", "luajit.exe"):
        candidate = paths.lua_dir() / name
        _print(f"  {name:<12}: {'yes' if candidate.is_file() else 'no'}"
               + (f" ({candidate.stat().st_size} bytes)" if candidate.is_file() else ""))

    try:
        import bootstrap

        report = bootstrap.ensure_environment(allow_download=not offline)
        _print("bootstrap   : " + ("ok" if report.ok else "problems"))
        for key in sorted(report.detail):
            _print(f"  {key:<16}: {report.detail[key]}")
        for note in report.notes:
            _print(f"  note: {note}")
    except Exception as exc:
        _print(f"bootstrap   : failed: {type(exc).__name__}: {exc}")

    try:
        from core.config import DEFAULT_RUNTIMES
        from core.runtime import discover_runtimes, resolve_prefer_exe

        _print(f"prefer exe  : {resolve_prefer_exe()}")
        specs = discover_runtimes(DEFAULT_RUNTIMES)
        if not specs:
            _print("runtimes    : none usable")
        for spec in specs:
            _print(f"runtime     : {spec.label} -> {spec.detail} {spec.version}")
    except Exception as exc:
        _print(f"runtimes    : probe failed: {type(exc).__name__}: {exc}")
        return 1
    return 0 if specs else 1


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="Excalibur", description="WeAreDevs deobfuscator")
    parser.add_argument("--version", action="store_true", help="print the version and exit")
    parser.add_argument("--cli", metavar="FILE", help="deobfuscate FILE without opening the GUI")
    parser.add_argument("--detect", metavar="FILE", help="print the detection report for FILE")
    parser.add_argument("--out", metavar="FILE", help="write the deobfuscated source to FILE (with --cli)")
    parser.add_argument("--json", action="store_true", help="machine readable report (with --cli)")
    parser.add_argument("--quiet", action="store_true", help="do not print progress")
    parser.add_argument("--timeout", type=float, default=30.0, help="sandbox wall clock budget (seconds)")
    parser.add_argument("--no-static", action="store_true", help="skip the static constant layer stage")
    parser.add_argument("--no-dynamic", action="store_true", help="skip the sandbox stage")
    parser.add_argument("--no-trace", action="store_true", help="skip the trace fallback")
    parser.add_argument("--runtime", choices=("auto", "exe", "lupa"), default="auto",
                        help="which Lua runtime the sandbox uses (default: auto - the bundled "
                             "lua/lua51.exe on Windows, lupa elsewhere)")
    parser.add_argument("--lift", metavar="FILE", help="write the partial lift (pseudo source) to FILE")
    parser.add_argument("--no-lift", action="store_true", help="skip the partial lift stage")
    parser.add_argument("--doctor", action="store_true",
                        help="print paths, the bootstrap report and the usable Lua runtimes")
    parser.add_argument("--boot", action="store_true", help="run the first-run setup and exit")
    parser.add_argument("--offline", action="store_true", help="never allow the bootstrap to use the network")
    parser.add_argument("--skip-bootstrap", action="store_true", help="do not run the first-run setup")
    parser.add_argument("--no-bootstrap", action="store_true", help=argparse.SUPPRESS)
    parser.add_argument("--light", action="store_true", help="start with the light monochrome palette")
    parser.add_argument("--theme", choices=("dark", "light"), help="force a palette")
    parser.add_argument("file", nargs="?", help="Lua file to open in the GUI")
    return parser


def main(argv: Optional[List[str]] = None) -> int:
    argv = list(sys.argv[1:] if argv is None else argv)
    args = build_parser().parse_args(argv)

    if args.version:
        _print(f"Excalibur {__version__}")
        return 0

    # ---- first run setup -------------------------------------------------
    if args.boot:
        import bootstrap

        report = bootstrap.ensure_environment(allow_download=not args.offline)
        _print(report.text(), end="")
        return 0 if report.ok else 1

    skip = args.skip_bootstrap or args.no_bootstrap or "--skip-bootstrap" in argv
    if not skip:
        try:
            import bootstrap

            report = bootstrap.ensure_environment(allow_download=not args.offline)
            bootstrap.add_site_packages()
            if args.cli or args.detect:
                _print(report.text(), end="")
            if not report.ok:
                for note in report.notes:
                    _print(f"bootstrap: {note}")
        except Exception as exc:  # never let setup break the app
            _print(f"bootstrap skipped: {type(exc).__name__}: {exc}")

    # ---- console modes ---------------------------------------------------
    if args.doctor:
        return run_doctor(offline=args.offline)
    if args.detect:
        return run_detect(Path(args.detect))
    if args.cli:
        return run_cli(args)

    # ---- GUI -------------------------------------------------------------
    try:
        from gui.app import launch
    except Exception as exc:  # pragma: no cover - broken install
        _print(f"cannot start the GUI: {type(exc).__name__}: {exc}")
        return 5
    return launch(argv, file=args.file)


if __name__ == "__main__":
    _setup_stdio()
    try:
        _code = main()
    except SystemExit:
        raise
    except BaseException as _exc:  # a windowed build must not vanish silently
        _log_crash(_exc)
        _code = 70
    raise SystemExit(_code)
