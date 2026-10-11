"""The vendored Lua 5.1 interpreter (``lua/lua51.exe``) and the exe runtime path.

``lua/lua51.exe`` is committed (built bit for bit from the official Lua 5.1.5
sources, see ``lua/README.md`` and ``tools/build_lua.py``).  These tests keep
three promises:

* the committed binary is the pinned one (hash + PE header), so a corrupted or
  swapped file is caught before it ships inside the EXE;
* the runtime ladder *offers* it, and the preference rules (auto on Windows,
  ``EXCALIBUR_RUNTIME`` override, fall back to lupa) behave as documented;
* when an interpreter can actually run on this machine - Windows, or a native
  build made with ``python tools/build_lua.py --native lua/lua51`` - the
  acceptance fixture goes through *that* interpreter and still comes out byte
  identical.  A standalone interpreter is a different code path from lupa (it
  prints instead of returning values), so it needs its own coverage.
"""

from __future__ import annotations

import os
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import PipelineConfig, SandboxConfig  # noqa: E402
from core.deobfuscate import deobfuscate_file  # noqa: E402
from core.runtime import (  # noqa: E402
    RuntimeSpec,
    discover_runtimes,
    probe_runtime,
    resolve_prefer_exe,
)
from tools.build_lua import (  # noqa: E402
    BINARY,
    BINARY_SHA256,
    BINARY_SIZE,
    SOURCE,
    pe_info,
    sha256_file,
    verify,
)

FIXTURE = ROOT / "tests" / "wrd_v1_0_0.lua"
CLEAN = ROOT / "tests" / "wrd_v1_0_0_clean.lua"


def runnable_interpreter() -> RuntimeSpec | None:
    """The vendored interpreter if this host can execute it, else the first exe."""
    if BINARY.is_file():
        probed = probe_runtime(RuntimeSpec(name="lua51", kind="exe", detail=str(BINARY)))
        if probed is not None:
            return probed
    for name in ("lua51", "lua"):
        for spec in discover_runtimes((name,), prefer_exe=True):
            if spec.kind == "exe":
                return spec
    return None


RUNNABLE = runnable_interpreter()


class VendoredInterpreter(unittest.TestCase):
    """The file in ``lua/`` is the artefact ``tools/build_lua.py`` describes."""

    def test_binary_is_present(self) -> None:
        self.assertTrue(BINARY.is_file(), "lua/lua51.exe is part of the repository")

    def test_matches_the_pinned_manifest(self) -> None:
        report = verify()
        self.assertTrue(report["ok"], report)
        self.assertEqual(report["size"], BINARY_SIZE)
        self.assertEqual(sha256_file(BINARY), BINARY_SHA256)

    def test_is_a_windows_x86_64_console_binary(self) -> None:
        info = pe_info(BINARY.read_bytes())
        self.assertTrue(info["pe"], "not a PE file")
        self.assertEqual(info["machine"], "x86_64")
        self.assertEqual(info["subsystem"], 3, "console subsystem")
        self.assertTrue(info["pe32_plus"])

    def test_contains_the_lua_5_1_5_interpreter(self) -> None:
        data = BINARY.read_bytes()
        self.assertIn(b"Lua 5.1", data)
        self.assertIn(b"PUC-Rio", data)
        self.assertNotIn(b"lua51.dll", data, "the binary must be self contained")
        self.assertEqual(SOURCE["version"], "Lua 5.1.5")

    def test_builder_documents_the_same_hash(self) -> None:
        # the tool that rebuilds the file and the tests must never drift apart
        self.assertEqual(len(BINARY_SHA256), 64)
        self.assertGreater(BINARY_SIZE, 100_000)


class RuntimePreference(unittest.TestCase):
    """``resolve_prefer_exe`` decides lupa vs. standalone interpreters."""

    def setUp(self) -> None:
        self._saved = os.environ.pop("EXCALIBUR_RUNTIME", None)

    def tearDown(self) -> None:
        if self._saved is None:
            os.environ.pop("EXCALIBUR_RUNTIME", None)
        else:
            os.environ["EXCALIBUR_RUNTIME"] = self._saved

    def test_auto_follows_the_platform(self) -> None:
        # Windows ships lua/lua51.exe next to the EXE, POSIX hosts cannot run it
        expected = os.name == "nt"
        self.assertEqual(resolve_prefer_exe(), expected)
        self.assertEqual(resolve_prefer_exe(None), expected)

    def test_explicit_choice_wins_over_auto(self) -> None:
        self.assertTrue(resolve_prefer_exe(True))
        self.assertFalse(resolve_prefer_exe(False))

    def test_environment_override_wins_over_everything(self) -> None:
        os.environ["EXCALIBUR_RUNTIME"] = "exe"
        self.assertTrue(resolve_prefer_exe(False))
        os.environ["EXCALIBUR_RUNTIME"] = "lupa"
        self.assertFalse(resolve_prefer_exe(True))
        os.environ["EXCALIBUR_RUNTIME"] = "nonsense"
        self.assertEqual(resolve_prefer_exe(True), True)
        self.assertEqual(resolve_prefer_exe(False), False)


@unittest.skipUnless(RUNNABLE is not None,
                     "no interpreter this host can run (build one with "
                     "python tools/build_lua.py --native lua/lua51)")
class ExeRuntimePipeline(unittest.TestCase):
    """The acceptance fixture through a *standalone* interpreter, not lupa."""

    def test_acceptance_fixture_is_byte_identical(self) -> None:
        config = PipelineConfig(
            sandbox=SandboxConfig(timeout=30, sample_runs=2, max_attempts=3, prefer_exe=True),
            trace_on_failure=False,
        )
        result = deobfuscate_file(FIXTURE, config=config)
        clean = CLEAN.read_text(encoding="utf-8")
        self.assertTrue(result.success, result.summary_text())
        self.assertEqual(result.method, "dynamic")
        self.assertEqual(result.output, clean)
        self.assertEqual(result.output.encode("utf-8"), clean.encode("utf-8"))

    def test_the_interpreter_was_actually_used(self) -> None:
        config = PipelineConfig(
            sandbox=SandboxConfig(timeout=30, sample_runs=1, max_attempts=1, prefer_exe=True),
            trace_on_failure=False,
        )
        result = deobfuscate_file(FIXTURE, config=config)
        attempts = (result.sandbox or {}).get("attempts") or []
        self.assertTrue(attempts, "the sandbox did not run")
        self.assertTrue(
            any(attempt.get("runtime", {}).get("kind") == "exe" for attempt in attempts),
            f"lupa was used instead of the interpreter: {attempts}",
        )

    def test_an_infinite_loop_is_killed_by_the_interpreter(self) -> None:
        # the watchdog lives inside runner.lua; a standalone interpreter must
        # honour it just like lupa does (LuaJIT starves count hooks - see
        # core/lua/runner.lua, where the JIT is switched off for this reason)
        import shutil
        import tempfile

        from core.sandbox import Sandbox

        source = "--[[ v1.0.0 https://wearedevs.net/obfuscator ]]\nwhile true do local x = 1 end\n"
        workdir = Path(tempfile.mkdtemp(prefix="excalibur-spin-"))
        try:
            config = SandboxConfig(timeout=3, sample_runs=1, max_attempts=1, prefer_exe=True)
            started = __import__("time").time()
            result = Sandbox(config).run(source, source_name="spin.lua", workdir=workdir)
            self.assertLess(__import__("time").time() - started, 60.0)
            attempt = result.attempts[0]
            self.assertTrue(attempt.timed_out, attempt.summary())
        finally:
            shutil.rmtree(workdir, ignore_errors=True)


if __name__ == "__main__":
    unittest.main()
