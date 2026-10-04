from __future__ import annotations

import sys
import traceback


def main() -> int:
    try:
        from installer import ensure_installed

        ensure_installed()
    except Exception as exc:
        print(f"Protez setup failed: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1

    try:
        from gui.app import ProtezApp

        app = ProtezApp()
        app.mainloop()
    except ModuleNotFoundError as exc:
        print(f"Could not start Protez: {exc}", file=sys.stderr)
        if exc.name in {"tkinter", "_tkinter"}:
            print(
                "This Python installation is missing Tk support. "
                "On Debian/Ubuntu, install the python3-tk system package.",
                file=sys.stderr,
            )
        traceback.print_exc()
        return 1
    except Exception as exc:
        print(f"Protez GUI failed: {exc}", file=sys.stderr)
        traceback.print_exc()
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
