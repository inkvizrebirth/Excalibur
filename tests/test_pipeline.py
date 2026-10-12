"""End-to-end tests for the deobfuscation pipeline.

Runs with either ``python -m unittest`` or ``pytest`` (the CI uses pytest for
nicer output, but nothing here depends on it).

Coverage:

* the acceptance fixture pair ``tests/wrd_v1_0_0.lua`` -> ``_clean.lua`` must be
  recovered **byte for byte** (the TZ acceptance criterion);
* the generated fixture is detected as WeAreDevs v1.0.0 with high confidence;
* the static layer decodes the pool, inlines the resolver and folds constants;
* a non-obfuscated script is not falsely claimed to be deobfuscated;
* truncated input fails gracefully (no exception, actionable reason);
* an infinite loop is killed by the sandbox watchdog;
* real-world samples (when fetched) are detected, statically decoded and the
  rewritten source stays behaviourally identical to the input.
"""

from __future__ import annotations

import sys
import time
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from core.config import PipelineConfig, SandboxConfig  # noqa: E402
from core.deobfuscate import deobfuscate, deobfuscate_file  # noqa: E402
from core.registry import detect_and_route  # noqa: E402
from core.sourceio import read_source  # noqa: E402
from core.wrd_detect import detect  # noqa: E402
from core.wrd_static import analyze  # noqa: E402

FIXTURE = ROOT / "tests" / "wrd_v1_0_0.lua"
CLEAN = ROOT / "tests" / "wrd_v1_0_0_clean.lua"
REAL_DIR = ROOT / "samples" / "real"

FAST = PipelineConfig(sandbox=SandboxConfig(timeout=20, sample_runs=2, max_attempts=4))


def _runtime_available() -> bool:
    """Is there a usable Lua runtime (lupa wheel or a vendored interpreter)?"""
    try:
        from core.runtime import runtime_ladder

        usable, _rejected = runtime_ladder(("lua51", "luajit21", "lua54"))
    except Exception:
        return False
    return bool(usable)


#: Tests that really execute Lua; the rest of the suite runs without a runtime so
#: a fresh clone (``python -m unittest``) stays green before ``pip install``.
needs_runtime = unittest.skipUnless(
    _runtime_available(),
    "needs a Lua runtime: pip install -r requirements.txt, or build lua/lua51",
)


class AcceptanceFixture(unittest.TestCase):
    """The fixture pair that encodes the TZ acceptance criterion."""

    def test_fixture_files_exist(self) -> None:
        self.assertTrue(FIXTURE.exists(), "run tools/make_wrd_fixture.py")
        self.assertTrue(CLEAN.exists())

    def test_detected_as_wrd_1_0_0(self) -> None:
        source = read_source(FIXTURE)
        detection = detect(source.text)
        self.assertTrue(detection.is_obfuscated)
        self.assertEqual(detection.format, "wrd")
        self.assertEqual(detection.version, "1.0.0")
        self.assertGreaterEqual(detection.confidence, 0.8)

    def test_static_layer_decodes_everything(self) -> None:
        source = read_source(FIXTURE)
        result = analyze(source.text)
        self.assertTrue(result.ok, result.reason)
        self.assertEqual(result.pool.entries, len([d for d in result.decoded if d is not None]))
        self.assertGreater(result.inlined_calls, 0)
        self.assertGreater(result.folded_expressions, 0)
        self.assertIn("loadstring", result.output)

    @needs_runtime
    def test_recovered_source_matches_clean_file(self) -> None:
        """The acceptance criterion: deobfuscated output == clean source."""
        clean = CLEAN.read_text(encoding="utf-8")
        result = deobfuscate_file(FIXTURE, config=FAST)
        self.assertTrue(result.success, result.summary_text())
        self.assertFalse(result.partial, "the payload should be the original source, not the layer")
        self.assertEqual(result.method, "dynamic")
        self.assertIsNotNone(result.output)
        self.assertEqual(result.output, clean)
        # and the round trip has to be exact at the byte level as well
        self.assertEqual(result.output.encode("utf-8"), clean.encode("utf-8"))

    @needs_runtime
    def test_output_artifacts_are_written(self) -> None:
        result = deobfuscate_file(FIXTURE, config=FAST)
        self.assertIsNotNone(result.output_path)
        self.assertTrue(result.output_path.exists())
        self.assertIsNotNone(result.decoded_path)
        self.assertTrue(result.decoded_path.exists())
        self.assertTrue(result.report_path.exists())
        self.assertTrue(result.summary_path.exists())
        self.assertEqual(result.output_path.read_text(encoding="utf-8"),
                         CLEAN.read_text(encoding="utf-8"))


class FormatHandling(unittest.TestCase):
    def test_plain_lua_is_not_claimed_to_be_deobfuscated(self) -> None:
        plain = "local t = {1, 2, 3}\nfor i, v in ipairs(t) do print(i, v) end\n"
        result = deobfuscate(plain, config=FAST)
        self.assertFalse(result.success)
        self.assertIsNone(result.output)
        self.assertFalse(result.detection["is_obfuscated"])

    def test_truncated_input_fails_gracefully(self) -> None:
        source = read_source(FIXTURE).text[:4000]  # cut the file in half
        result = deobfuscate(source, config=FAST)
        self.assertFalse(result.success)
        self.assertTrue(result.stages, "stages must still be reported")
        self.assertTrue(result.notes, "a failure must explain itself")
        self.assertTrue(result.report_path.exists())

    def test_unsupported_obfuscator_routes_to_placeholder(self) -> None:
        fake_luraph = "--[[ Luraph v14.2 ]] return function(...) return ... end\n"
        route = detect_and_route(fake_luraph)
        self.assertIsNotNone(route.deobfuscator)
        self.assertFalse(route.supported)
        self.assertIn("not supported", route.message.lower())

    def test_empty_input_is_handled(self) -> None:
        result = deobfuscate("", config=FAST)
        self.assertFalse(result.success)
        self.assertIsNotNone(result.report_path)


class SandboxSafety(unittest.TestCase):
    @needs_runtime
    def test_infinite_loop_is_killed(self) -> None:
        from core.sandbox import Sandbox

        config = SandboxConfig(timeout=2.0, sample_runs=1, max_attempts=1, max_instructions=2_000_000)
        source = "while true do end\n"
        started = time.time()
        result = Sandbox(config).run(source, source_name="infinite.lua")
        elapsed = time.time() - started
        self.assertLess(elapsed, 30, "the watchdog must stop the loop quickly")
        self.assertTrue(result.attempts)
        attempt = result.attempts[0]
        self.assertFalse(attempt.ran, "an infinite loop cannot have finished")
        self.assertTrue(attempt.timed_out or "TIMEOUT" in (attempt.error or "").upper(),
                        f"expected a timeout, got: {attempt.error}")

    @needs_runtime
    def test_loadstring_payload_is_captured(self) -> None:
        from core.sandbox import Sandbox

        payload = "print('captured payload')\n"
        source = (
            "local chunk = loadstring([==[\n" + payload + "]==])\n"
            "if chunk then chunk() end\n"
        )
        config = SandboxConfig(timeout=10, sample_runs=1, max_attempts=1)
        result = Sandbox(config).run(source, source_name="loadstring.lua")
        self.assertTrue(result.any_loads)
        dumps = result.all_dumps()
        self.assertTrue(dumps, "the loadstring argument must be dumped")
        self.assertEqual(dumps[0].read_text(encoding="utf-8"), payload)


class LuaModules(unittest.TestCase):
    """The Lua half has to load under a real interpreter."""

    def test_forwarder_modules_load(self) -> None:
        """The spec paths (core/roblox_stubs.lua, core/loadstring_hook.lua) work."""
        try:
            import lupa
        except ImportError:  # pragma: no cover - lupa is required in CI
            self.skipTest("lupa is not installed")

        runtime = lupa.LuaRuntime()
        expected = {
            "core/roblox_stubs.lua": "core/lua/roblox_stubs.lua",
            "core/loadstring_hook.lua": "core/lua/hooks.lua",
        }
        for relative, implementation in expected.items():
            with self.subTest(module=relative):
                module = runtime.execute(f'return dofile("{ROOT.as_posix()}/{relative}")')
                # the forwarder records where the real implementation lives
                self.assertTrue(str(module["implementation"]).replace("\\", "/").endswith(implementation),
                                module["implementation"])
                value = module["build"] if relative.endswith("roblox_stubs.lua") else module["make_loader"]
                self.assertTrue(callable(value))

    def test_sandbox_module_files_exist(self) -> None:
        for name in ("runner.lua", "hooks.lua", "roblox_stubs.lua", "lua51_compat.lua"):
            with self.subTest(module=name):
                self.assertTrue((ROOT / "core" / "lua" / name).exists(), name)


@unittest.skipUnless(REAL_DIR.is_dir() and any(REAL_DIR.glob("*.lua")),
                     "real samples are not fetched (python tools/fetch_samples.py)")
class RealSamples(unittest.TestCase):
    """Regression over real WeAreDevs v1.0.0 builds.

    These scripts interpret their payload inside a flattened state machine, so
    there is no ``loadstring`` payload to capture: the constant layer is what
    Excalibur can lift today.  The tests therefore assert the invariants we do
    guarantee - detection, full static decode, identical runtime behaviour of
    the rewritten source, and an honest "partial" verdict.
    """

    def _samples(self):
        return sorted(REAL_DIR.glob("*.lua"))

    def test_real_samples_detected_and_decoded(self) -> None:
        for path in self._samples():
            with self.subTest(sample=path.name):
                source = read_source(path)
                detection = detect(source.text)
                self.assertTrue(detection.is_obfuscated, path.name)
                self.assertEqual(detection.format, "wrd")
                result = analyze(source.text)
                self.assertTrue(result.ok, f"{path.name}: {result.reason}")
                decoded = [d for d in result.decoded if d is not None]
                self.assertGreater(len(decoded), 10, path.name)
                self.assertIsNotNone(result.output)

    @needs_runtime
    def test_real_sample_behaviour_is_preserved(self) -> None:
        """The rewritten source must behave exactly like the input."""
        from core.sandbox import Sandbox

        sandbox = Sandbox(SandboxConfig(timeout=20, sample_runs=1, max_attempts=1))
        for path in self._samples()[:2]:
            with self.subTest(sample=path.name):
                source = read_source(path).text
                rewritten = analyze(source).output
                self.assertIsNotNone(rewritten, path.name)
                before = sandbox.run(source, source_name=path.name + ".orig")
                after = sandbox.run(rewritten, source_name=path.name + ".decoded")
                self.assertTrue(before.attempts and after.attempts, path.name)
                a, b = before.attempts[0].report, after.attempts[0].report
                self.assertEqual(a.get("ran"), b.get("ran"), path.name)
                self.assertEqual(a.get("stats", {}).get("char_calls"),
                                 b.get("stats", {}).get("char_calls"), path.name)
                self.assertEqual(sorted(m["name"] for m in a.get("missed_globals", [])),
                                 sorted(m["name"] for m in b.get("missed_globals", [])), path.name)

    def test_real_samples_report_partial_not_success(self) -> None:
        path = self._samples()[0]
        result = deobfuscate_file(path, config=FAST)
        self.assertTrue(result.success, result.summary_text())
        self.assertTrue(result.partial, "flattened builds have no loadstring payload")
        self.assertEqual(result.method, "static")
        self.assertIn("virtualised", " ".join(result.notes).lower())


if __name__ == "__main__":
    unittest.main(verbosity=2)
