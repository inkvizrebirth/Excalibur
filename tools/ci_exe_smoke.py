"""CI helper: the offline acceptance run through the *packaged* EXE.

The EXE is a PyInstaller one-file build, so the interesting failure mode is not
"does the algorithm work" (the unit tests cover that) but "does the bundle still
work when it is unpacked into ``%TEMP%`` with no console": the interpreter inside
the bundle has to be found, the Lua child processes have to be started from the
unpacked directory and the results have to survive the frozen ``sys._MEIPASS``
layout.

A ``--windowed`` build has no console at all, which is why its output is
mirrored into ``%LOCALAPPDATA%/Excalibur/logs/exe.log`` (see
``main.py::_setup_stdio``).  This helper:

* runs the acceptance commands through a console build of the same sources
  (visible stdout/stderr, so a failure is diagnosable);
* runs the windowed build at least once to prove it starts;
* compares the recovered sources byte for byte with the clean fixture;
* prints a compact summary and, on failure, emits a ``::error`` annotation with
  the exit code, the output tails and the app log - Actions job logs are handy
  for a human but annotations are what a script (or the agent) can read back.

    python tools/ci_exe_smoke.py --exe dist/ExcaliburCLI.exe
    python tools/ci_exe_smoke.py --exe dist/ExcaliburCLI.exe --windowed dist/Excalibur.exe
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

FIXTURE = ROOT / "tests" / "wrd_v1_0_0.lua"
CLEAN = ROOT / "tests" / "wrd_v1_0_0_clean.lua"
#: A bare flattened payload: the lift has something to describe even when the
#: constant layer and the sandbox produce nothing.
FLAT = ROOT / "tests" / "wrd_flat_mini.lua"

#: How much of a stream is quoted in an annotation (annotations are short).
TAIL = 500


def _escape(message: str) -> str:
    return message.replace("%", "%25").replace("\r", "").replace("\n", "%0A")


def annotate(title: str, message: str) -> None:
    print(f"::error title={title}::{_escape(message)[:6000]}")


def tail(text: str, limit: int = TAIL) -> str:
    text = (text or "").strip()
    if not text:
        return "(empty)"
    return text if len(text) <= limit else "..." + text[-limit:]


def app_log_path() -> Optional[Path]:
    """The file a windowed build mirrors its console output into."""
    try:
        from core import paths

        return paths.app_data_dir() / "logs" / "exe.log"
    except Exception:
        return None


def app_log_tail(limit: int = 1500) -> str:
    path = app_log_path()
    if path is None or not path.is_file():
        return "(no exe.log)"
    try:
        return tail(path.read_text(encoding="utf-8", errors="replace"), limit)
    except Exception as exc:  # pragma: no cover - unreadable log
        return f"(cannot read {path}: {exc})"


class Smoke:
    """Run the acceptance commands and keep every result for the summary."""

    def __init__(self, exe: Path, *, offline: bool = True, timeout: float = 300.0) -> None:
        self.exe = exe
        self.offline = offline
        self.timeout = timeout
        self.results: List[dict] = []
        self.failures: List[dict] = []

    # ------------------------------------------------------------------ running
    def run(self, label: str, arguments: Sequence[str], *, expect: int = 0) -> dict:
        command = [str(self.exe), *arguments]
        if self.offline:
            command.insert(1, "--offline")
        started = time.time()
        record: dict = {"label": label, "command": command, "exit": None, "stdout": "", "stderr": ""}
        try:
            completed = subprocess.run(
                command,
                capture_output=True,
                text=True,
                timeout=self.timeout,
                cwd=str(ROOT),
            )
            record.update(
                exit=completed.returncode,
                stdout=completed.stdout or "",
                stderr=completed.stderr or "",
            )
        except subprocess.TimeoutExpired as exc:
            record.update(exit="timeout", stdout=exc.stdout or "", stderr=exc.stderr or "")
        except Exception as exc:
            record.update(exit=f"error: {type(exc).__name__}: {exc}")
        record["elapsed_ms"] = int((time.time() - started) * 1000)
        ok = record["exit"] == expect
        record["ok"] = ok
        self.results.append(record)
        if not ok:
            record["expected"] = expect
            self.failures.append(record)
        line = (f"  {label}: exit={record['exit']} in {record['elapsed_ms']} ms "
                f"stdout={tail(record['stdout'], 120)}")
        print(line, flush=True)
        return record

    # ------------------------------------------------------------------ checks
    def compare(self, label: str, produced: Path, expected: Path = CLEAN) -> bool:
        """Byte-for-byte comparison - the acceptance criterion itself."""
        record: dict = {"label": label, "produced": str(produced)}
        try:
            got = produced.read_bytes()
        except Exception as exc:
            record.update(ok=False, detail=f"cannot read {produced}: {exc}")
            self.failures.append(record)
            print(f"  {label}: MISSING ({exc})", flush=True)
            return False
        want = expected.read_bytes()
        ok = got == want
        detail = "identical" if ok else f"{len(got)} bytes vs {len(want)} expected"
        if not ok:
            # the classic false alarm: a checkout that converted the fixtures to
            # CRLF (git's core.autocrlf is true on the Windows runners) - call it
            # out by name instead of leaving a byte count to guess from
            crlf = b"\r\n"
            got_crlf, want_crlf = got.count(crlf), want.count(crlf)
            if got.replace(crlf, b"\n") == want.replace(crlf, b"\n"):
                detail += ("; the two differ only by line endings - "
                           + str(got_crlf) + " CRLF in the produced file, "
                           + str(want_crlf) + " in the expected one "
                           "(check .gitattributes / core.autocrlf)")
            else:
                shared = 0
                for left, right in zip(got, want):
                    if left != right:
                        break
                    shared += 1
                detail += f"; first difference at byte {shared}: {got[shared:shared + 32]!r} vs {want[shared:shared + 32]!r}"
        record.update(ok=ok, bytes=len(got), detail=detail)
        self.results.append(record)
        if not ok:
            self.failures.append(record)
        print(f"  {label}: {'identical' if ok else 'DIFFERS'} ({len(got)} bytes)", flush=True)
        return ok

    # ------------------------------------------------------------------ report
    def summary(self) -> str:
        lines = [f"exe smoke: {self.exe.name}", f"  exe       : {self.exe}"]
        for record in self.results:
            if "command" in record:
                lines.append(f"  {record['label']:<22} exit={record['exit']} "
                             f"ok={record.get('ok')} {record['elapsed_ms']} ms")
            else:
                lines.append(f"  {record['label']:<22} ok={record.get('ok')} {record.get('detail', '')}")
        lines.append(f"  app log   : {app_log_path()}")
        lines.append("  problems  : " + (str(len(self.failures)) if self.failures else "none"))
        return "\n".join(lines)

    def failure_report(self) -> str:
        chunks: List[str] = []
        for record in self.failures:
            if "command" in record:
                heading = (f"{record['label']}: exit={record['exit']} "
                           f"(expected {record.get('expected')})\n  $ {' '.join(record['command'])}")
                chunks.append(f"{heading}\n  stdout: {tail(record['stdout'])}\n  stderr: {tail(record['stderr'])}")
            else:
                chunks.append(f"{record['label']}: {record.get('detail')} ({record.get('produced')})")
        doctor = next((r for r in self.results if r["label"] == "doctor"), None)
        if doctor is not None:
            chunks.append("doctor:\n" + tail("\n".join(
                line for line in doctor["stdout"].splitlines() if line.strip()), 1500))
        chunks.append("app log tail:\n" + app_log_tail())
        return "\n".join(chunks)


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--exe", required=True, metavar="PATH",
                        help="console build of the EXE used for the acceptance commands")
    parser.add_argument("--windowed", metavar="PATH",
                        help="windowed build: only asserted to start")
    parser.add_argument("--out-dir", default=".exe-smoke", metavar="DIR")
    parser.add_argument("--timeout", type=float, default=300.0)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args(argv)

    exe = Path(args.exe).resolve()
    out_dir = Path(args.out_dir)
    out_dir.mkdir(parents=True, exist_ok=True)
    started = time.time()

    if not exe.is_file():
        message = f"the EXE was not built: {exe}"
        print(message)
        annotate("exe smoke", message)
        return 1

    smoke = Smoke(exe, timeout=args.timeout)
    smoke.run("version", ["--version"])
    # the inventory explains *why* a later check failed (bundled interpreter, paths)
    smoke.run("doctor", ["--doctor"])
    smoke.run("detect", ["--detect", str(FIXTURE)])

    auto_out = out_dir / "recovered.lua"
    smoke.run("cli (bundled runtime)", ["--cli", str(FIXTURE), "--out", str(auto_out), "--quiet"])
    smoke.compare("bundled runtime output", auto_out)

    exe_out = out_dir / "recovered_exe.lua"
    smoke.run("cli (--runtime exe)", ["--runtime", "exe", "--cli", str(FIXTURE),
                                      "--out", str(exe_out), "--quiet"])
    smoke.compare("exe runtime output", exe_out)

    # A bare flattened payload has no payload to recover, so the CLI reports
    # "no payload" (exit 1) - the listing is the deliverable of this mode.
    pseudo = out_dir / "pseudocode.lua"
    smoke.run("cli (partial lift)", ["--cli", str(FLAT), "--lift", str(pseudo), "--quiet"],
              expect=1)
    if pseudo.is_file():
        text = pseudo.read_text(encoding="utf-8", errors="replace")
        ok = "control flow (state -> successor)" in text
        smoke.results.append({"label": "lift listing", "ok": ok,
                              "detail": f"{len(text)} chars" if ok else "no state listing"})
        print(f"  lift listing: {'ok' if ok else 'MISSING'} ({len(text)} chars)", flush=True)
        if not ok:
            smoke.failures.append(smoke.results[-1])
    else:
        smoke.failures.append({"label": "lift listing", "ok": False, "detail": f"not written: {pseudo}"})

    if args.windowed:
        windowed = Path(args.windowed).resolve()
        if windowed.is_file():
            smoke.run("windowed starts", ["--version"], expect=0)
        else:
            smoke.failures.append({"label": "windowed build", "ok": False,
                                   "detail": f"missing: {windowed}"})

    elapsed = int((time.time() - started) * 1000)
    print(smoke.summary(), flush=True)
    payload = {
        "exe": str(exe),
        "windowed": str(args.windowed) if args.windowed else None,
        "ok": not smoke.failures,
        "checks": len(smoke.results),
        "elapsed_ms": elapsed,
        "results": smoke.results,
    }
    if args.json:
        print(json.dumps(payload, ensure_ascii=False))

    if not smoke.failures:
        return 0

    annotate("exe smoke", smoke.failure_report())
    print(f"\nFAILED: {len(smoke.failures)} check(s) - see the annotation above", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
