"""Luraph v14 route: family detection, payload-root ranking, engine swap.

The heavy end-to-end lift (``V14LiftOracleTests``) is opt-in because it needs
Protez's pinned Luau binaries:

    PROTEZ_V14_ORACLE=1 PROTEZ_LUAU_AST=/path/luau-ast PROTEZ_LUAU_EXE=/path/luau \
        pytest tests/test_luraph_v14_route.py
"""

from __future__ import annotations

import contextlib
import json
import os
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace

from core.luraph_devirtualizer import (
    VENDOR_CORE,
    _V14Route,
    _v14_root_candidates,
    luraph_family,
)

SAMPLE_DIR = Path(__file__).resolve().parents[1] / "samples"
V14_SAMPLE = SAMPLE_DIR / "luraph_v14_7_variant01.luau"


def _add_vendor_to_path() -> None:
    core_path = str(VENDOR_CORE)
    if core_path not in sys.path:
        sys.path.insert(0, core_path)


@contextlib.contextmanager
def _dump_file(text: str):
    with tempfile.TemporaryDirectory() as directory:
        path = Path(directory) / "protos.json"
        path.write_text(text, encoding="utf-8")
        yield path


class LuraphFamilyDetectionTests(unittest.TestCase):
    def test_banner_selects_the_v14_front_end(self) -> None:
        source = "-- This file was protected using Luraph Obfuscator v14.7 [https://lura.ph/]\nreturn({})"
        self.assertEqual(luraph_family(source), "luraph_v14")

    def test_banner_selects_the_v15_front_end(self) -> None:
        source = "-- Luraph Obfuscator v15.1 [https://lura.ph/]\nlocal t = ..."
        self.assertEqual(luraph_family(source), "luraph_v15")

    def test_stripped_banner_falls_back_to_the_v14_entry_shape(self) -> None:
        """v14 wrappers end with a method fetch on the table they returned."""
        structured = "return({t=function(z,z) return z end}):t()(...);\n"
        self.assertEqual(luraph_family(structured), "luraph_v14")
        # a mere `return(...)` tail is not enough to claim v14
        plain = "local a=1\nreturn(function() local t={} return t end)(...)  \n"
        self.assertEqual(luraph_family(plain), "luraph_v15")

    def test_stripped_banner_falls_back_to_the_v15_markers(self) -> None:
        source = "local f = function() return LPH_ENCSTR(1) end\nreturn f"
        self.assertEqual(luraph_family(source), "luraph_v15")

    def test_real_v14_samples_are_detected(self) -> None:
        for name in ("luraph_v14_7_variant01.luau", "luraph_v14_7_HEHE.lua"):
            path = SAMPLE_DIR / name
            if not path.is_file():  # samples are optional in a trimmed checkout
                continue
            with self.subTest(sample=name):
                self.assertEqual(luraph_family(path.read_text(errors="replace")), "luraph_v14")


def _capture(*prototypes: tuple[int, int, int]) -> dict:
    """A capture shaped like the harness dump: protos plus their opcode tables."""
    entries, tables = {}, {}
    for number, opcode_count, maxstack in prototypes:
        table = 1000 + number
        entries[str(number)] = {"H": {"t": table}, "K": maxstack, "D": {"t": 0}, "__seq": number}
        tables[str(table)] = {"arr": list(range(opcode_count)), "kv": []}
    return {"root_callee": None, "overrides": [], "protos": entries, "tables": tables}


class V14RootCandidateTests(unittest.TestCase):
    def test_program_root_is_ranked_before_later_prototypes(self) -> None:
        with _dump_file(json.dumps(_capture((1, 403, 35), (3, 80, 25), (7, 128, 30)))) as path:
            self.assertEqual(_v14_root_candidates(str(path)), [1, 3, 7])

    def test_anti_tamper_prototype_is_never_a_candidate(self) -> None:
        """The first proto the entry method calls is Luraph's anti-tamper blob:
        thousands of opcodes and a deep stack. It must not reach the lifter."""
        with _dump_file(json.dumps(_capture((2, 4943, 139), (1, 403, 35)))) as path:
            self.assertEqual(_v14_root_candidates(str(path)), [1])

    def test_tiny_helpers_are_not_offered_as_program_roots(self) -> None:
        with _dump_file(json.dumps(_capture((1, 12, 4), (2, 200, 30)))) as path:
            self.assertEqual(_v14_root_candidates(str(path)), [2])

    def test_best_candidate_becomes_the_dump_root(self) -> None:
        """The lifter walks the dump's own root first; it must be the program."""
        capture = _capture((2, 4943, 139), (1, 403, 35))
        capture["root_callee"] = 2  # the anti-tamper proto, as the capture reports it
        with _dump_file(json.dumps(capture)) as path:
            self.assertEqual(_v14_root_candidates(str(path)), [1])
            rewritten = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(rewritten["root_callee"], 1)

    def test_harness_ranked_roots_win_and_are_not_rewritten(self) -> None:
        capture = _capture((1, 403, 35), (4, 200, 30))
        capture["root_candidates"] = [4]
        capture["root_callee"] = 4
        with _dump_file(json.dumps(capture)) as path:
            self.assertEqual(_v14_root_candidates(str(path)), [4, 1])
            rewritten = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(rewritten["root_callee"], 4)

    def test_unreadable_dump_reports_no_candidates(self) -> None:
        with _dump_file("not json") as path:
            self.assertEqual(_v14_root_candidates(str(path)), [])
        self.assertEqual(_v14_root_candidates("/nonexistent/protos.json"), [])


class EngineRouteTests(unittest.TestCase):
    """The v14 route swaps the mapper and the lifter for the duration of a run."""

    def setUp(self) -> None:
        _add_vendor_to_path()
        import obfuscators.luraph_v15 as package
        from obfuscators.luraph_v15 import driver

        self.package = package
        self.driver = driver
        self.saved_lift = driver.lift
        self.saved_mapper = getattr(package, "vmmap", None)

    def tearDown(self) -> None:
        self.driver.lift = self.saved_lift
        self.package.vmmap = self.saved_mapper

    def test_route_forwards_the_v14_engine_and_restores_afterwards(self) -> None:
        calls: list[tuple] = []

        def shared_lift(*args):
            calls.append(args)
            return "lifted"

        self.driver.lift = shared_lift
        marker_mapper, marker_engine = object(), object()

        with _V14Route(self.driver, marker_mapper, plugin=object(), devirt=marker_engine):
            self.assertIs(self.package.vmmap, marker_mapper)
            result = self.driver.lift("job", "runner", "patched", "cfg", {}, "text", "p", "d", [])
            self.assertEqual(result, "lifted")
            self.assertEqual(len(calls[0]), 10)
            self.assertIs(calls[0][-1], marker_engine)  # the v14 lifter, not the v15 one

        self.assertIs(self.driver.lift, shared_lift)
        self.assertIs(self.package.vmmap, self.saved_mapper)

    def test_route_restores_even_when_the_run_raises(self) -> None:
        with self.assertRaises(RuntimeError):
            with _V14Route(self.driver, object(), plugin=object(), devirt=object()):
                raise RuntimeError("lifter exploded")
        self.assertIs(self.driver.lift, self.saved_lift)
        self.assertIs(self.package.vmmap, self.saved_mapper)

    def test_route_restores_the_candidate_ranking(self) -> None:
        import obfuscators.luraph_v14.devirt as v14_engine

        original = v14_engine._lift_candidates
        with _V14Route(self.driver, object(), plugin=object(), devirt=v14_engine):
            self.assertIs(v14_engine._lift_candidates, _v14_root_candidates)
        self.assertIs(v14_engine._lift_candidates, original)

    def test_route_lifts_every_prototype_and_restores_the_lifter(self) -> None:
        """A v14 container is one flat prototype namespace: the run must lift
        all of them, not just the ranked root, and the engine module must be
        left exactly as it was found."""

        import obfuscators.luraph_v14.devirt as v14_engine

        original = v14_engine.lift_program
        self.assertTrue(hasattr(v14_engine, "lift_program_all"),
                        "the v14 engine must ship the whole-container lifter")
        with _V14Route(self.driver, object(), plugin=object(), devirt=v14_engine):
            self.assertIs(v14_engine.lift_program, v14_engine.lift_program_all)
        self.assertIs(v14_engine.lift_program, original)

    def test_route_keeps_the_shared_lifter_for_engines_without_the_all_lifter(self) -> None:
        import obfuscators.luraph_v14.devirt as v14_engine

        class FakeEngine:
            _lift_candidates = staticmethod(lambda path: [])

            def lift_program(self, *args, **kwargs):  # pragma: no cover - sentinel
                return None

        engine = FakeEngine()
        with _V14Route(self.driver, object(), plugin=object(), devirt=engine):
            # the mapper hook is swapped, the lifter is not (this engine has no
            # whole-container lifter)
            self.assertNotIn("lift_program", engine.__dict__)
        self.assertNotIn("lift_program", engine.__dict__)
        self.assertTrue(v14_engine.lift_program.__name__ in {"lift_program", "lift_program_all"})


@unittest.skipUnless(
    os.environ.get("PROTEZ_V14_ORACLE") == "1",
    "set PROTEZ_V14_ORACLE=1 (and PROTEZ_LUAU_AST / PROTEZ_LUAU_EXE) for the end-to-end lift",
)
class V14LiftOracleTests(unittest.TestCase):
    """Runs the shipped engine over the reference v14.7 sample (no sandbox):
    the runtime capture, the payload-root ranking, the lift and the polishing
    passes, exactly as the pipeline drives them."""

    def setUp(self) -> None:
        self.ast_tool = Path(os.environ.get("PROTEZ_LUAU_AST", "/nonexistent"))
        self.luau_exe = Path(os.environ.get("PROTEZ_LUAU_EXE", "/nonexistent"))
        for tool in (self.ast_tool, self.luau_exe):
            if not tool.is_file():
                self.skipTest(f"missing pinned Luau tool: {tool}")
        if not V14_SAMPLE.is_file():
            self.skipTest("the v14 reference sample is not part of this checkout")
        os.environ["PROTEZ_LUAU_AST"] = str(self.ast_tool)
        _add_vendor_to_path()

    def test_the_payload_root_is_lifted_into_non_scaffolding_luau(self) -> None:
        harness = __import__("harness")
        from obfuscators.luraph_v15 import driver as shared_driver
        from core.luraph_devirtualizer import _Job, _import_vendor

        harness, driver, devirt, _backend, vmmap, plugin = _import_vendor("luraph_v14")
        luau_exe = str(self.luau_exe)
        saved_runner = harness.Runner

        class _LocalRunner:
            """The sandbox-free twin of Protez's runner (same harness call)."""

            def __init__(self, job):
                self.job = job
                self.bridge = None
                self.luau = luau_exe
                self.hpath = job.trace_path + ".harness.luau"

            def run(self, source, cfg, chunks=None):
                return harness.run_once(self.luau, source, cfg, self.hpath,
                                        self.job.args.timeout, self.job.args.keep_harness, chunks)

            def finish(self):
                return None

        harness.Runner = _LocalRunner
        try:
            with tempfile.TemporaryDirectory() as directory:
                target = Path(directory) / "lifted.luau"
                args = SimpleNamespace(
                    no_devirt=False, no_hooks=False, no_tidy=False, keep_preamble=False,
                    max_runs=3, devirt_rounds=8, no_fold=False, raw=None, timeout=300,
                    keep_harness=False, studio=False, port=0, studio_wait=0, budget=120,
                    executor="Protez Offline", input_text=None, cfg=[], strings=False,
                    debug=True, obfuscator="Luraph v14",
                )
                job = _Job(V14_SAMPLE, V14_SAMPLE.read_bytes().decode("latin-1"), target, args)
                with _V14Route(driver, vmmap, plugin, devirt):
                    output = driver.run(job)
                lifted = Path(output)
                text = lifted.read_text(encoding="utf-8")
                parsed = __import__("subprocess").run([str(self.ast_tool), str(lifted)],
                                                      capture_output=True)
        finally:
            harness.Runner = saved_runner

        self.assertEqual(parsed.returncode, 0, parsed.stderr.decode("utf-8", "replace")[:400])
        # every prototype of the container is lifted, not just the entry one
        self.assertGreaterEqual(text.count("\nlocal function proto_"), 40, text[:400])
        self.assertIn("(the entry proto)", text)
        # the anti-tamper proto is Luraph's own trap, never a lifted "script function"
        self.assertNotIn("local function proto_2(", text)
        # …and the lift carries the program's own symbols, not the trap's
        for marker in ("Vector3", "UDim2", "HttpService"):
            self.assertIn(marker, text)
        # the shared-runtime stubs are reported, so the residual scaffolding score
        # stays low; a lift that lost the payload to the anti-tamper proto scores
        # far higher (95+)
        self.assertLessEqual(devirt._scaffold_score(text), 120, text[:400])


if __name__ == "__main__":
    unittest.main()
