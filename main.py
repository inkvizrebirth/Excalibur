from __future__ import annotations

import sys
import traceback

from core.version import VERSION


def _show_error(title: str, message: str) -> None:
    if sys.stderr is not None:
        print(message, file=sys.stderr)
    try:
        from tkinter import messagebox

        messagebox.showerror(title, message)
    except Exception:
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)


def _ui_import_check() -> int:
    try:
        from gui.app import ProtezApp  # noqa: F401
    except Exception:
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)
        return 1
    if sys.stdout is not None:
        print("Protez GUI modules: ready")
    return 0


def _health_check() -> int:
    try:
        from installer import ensure_installed

        ensure_installed()
    except Exception as exc:
        if sys.stderr is not None:
            print(f"Protez startup check failed: {exc}", file=sys.stderr)
        return 1
    if sys.stdout is not None:
        print(f"Protez {VERSION}: runtime ready")
    return 0


def main() -> int:
    if "--version" in sys.argv:
        if sys.stdout is not None:
            print(f"Protez {VERSION}")
        return 0
    if "--health-check" in sys.argv:
        return _health_check()
    if "--ui-import-check" in sys.argv:
        return _ui_import_check()

    try:
        from gui.bootstrap import BootstrapWindow

        bootstrap = BootstrapWindow()
        bootstrap.mainloop()
        ready = bootstrap.success
    except Exception as exc:
        _show_error("Protez startup", f"Could not open the startup repair window:\n{exc}")
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)
        return 1

    if not ready:
        return 1

    try:
        from gui.app import ProtezApp

        app = ProtezApp()
        app.mainloop()
    except ModuleNotFoundError as exc:
        detail = f"Could not start Protez: {exc}"
        if exc.name in {"tkinter", "_tkinter"}:
            detail += "\nThis Python installation is missing Tk support."
        _show_error("Protez", detail)
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)
        return 1
    except Exception as exc:
        _show_error("Protez", f"The GUI stopped unexpectedly:\n{exc}")
        if sys.stderr is not None:
            traceback.print_exc(file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
