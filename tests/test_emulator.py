from __future__ import annotations

import tempfile
import os
import time
import unittest
import unittest.mock
from pathlib import Path

from core.emulator import (
    LuaEmulator,
    backend_terminates,
    classify_chunk,
    emulator_available,
)

try:
    from lupa import lua51  # noqa: F401

    HAVE_LUA = True
except Exception:  # noqa: BLE001
    HAVE_LUA = False

PAYLOAD_URL = "https://cdn.example/payload.lua"
NESTED_SOURCE = 'print("nested layer")'


def bridge(url: object, method: object = "GET") -> str:
    return NESTED_SOURCE if str(url) == PAYLOAD_URL else ""


class ChunkClassificationTests(unittest.TestCase):
    def test_recognises_source_and_binary(self) -> None:
        self.assertEqual(classify_chunk("print(1)"), "lua-source")
        self.assertEqual(classify_chunk("\x1bLuaQ\x00\x01\x04\x08"), "lua51-bytecode")
        self.assertEqual(classify_chunk(""), "empty")


@unittest.skipIf(not HAVE_LUA, "lupa Lua 5.1 is unavailable")
class EmulatorTests(unittest.TestCase):
    def test_captures_loadstring_payloads(self) -> None:
        loader = f"""
        local body = game:HttpGet("{PAYLOAD_URL}")
        local chunk = loadstring(body)
        if chunk then chunk() end
        print("done")
        """
        result = LuaEmulator(profile="universal", http_bridge=bridge).run(loader)
        self.assertEqual(result.status, "completed", result.error)
        kinds = [capture.kind for capture in result.captures]
        self.assertIn("loadstring", kinds)
        captured = [capture for capture in result.captures if capture.kind == "loadstring"]
        self.assertEqual(captured[0].text, NESTED_SOURCE)
        self.assertIn(PAYLOAD_URL, result.fetches)

    def test_injector_probes_do_not_abort_the_run(self) -> None:
        loader = """
        local executor = identifyexecutor()
        local environment = getgenv()
        environment.loaded = true
        if syn and syn.protect_gui then syn.protect_gui({}) end
        if isfunction(writefile) then writefile("cache/test", "1") end
        print(executor, type(game:GetService("Players")))
        """
        result = LuaEmulator(profile="universal").run(loader)
        self.assertEqual(result.status, "completed", result.error)
        prints = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any("Synapse X" in text for text in prints))

    def test_instruction_budget_stops_runaway_loops(self) -> None:
        result = LuaEmulator(profile="universal", max_instructions=1).run("while true do end")
        self.assertEqual(result.status, "limit")
        self.assertIsNotNone(result.error)

    def test_process_globals_are_absent_and_files_stay_in_the_workspace(self) -> None:
        loader = """
        assert(io == nil, "io should be removed")
        assert(os == nil or os.execute == nil, "os.execute should be removed")
        assert(package == nil, "package should be removed")
        writefile("probe/probe.lua", "return 'workspace'")
        assert(isfile("probe/probe.lua"), "workspace writes should work")
        assert(readfile("probe/probe.lua") == "return 'workspace'")
        assert(loadfile("probe/probe.lua")() == "workspace")
        assert(escape == nil, "no escape hatch should exist")
        print("sandbox ok")
        """
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            result = LuaEmulator(profile="real", workspace_dir=workspace).run(loader)
            self.assertEqual(result.status, "completed", result.error)
            written = sorted(item.relative_to(workspace) for item in workspace.rglob("*"))
            self.assertEqual([str(item) for item in written], ["probe", "probe/probe.lua"])

    def test_paths_cannot_escape_the_workspace(self) -> None:
        from core.executor_api import normalise_workspace_path

        self.assertEqual(normalise_workspace_path("../../etc/passwd"), "etc/passwd")
        self.assertEqual(normalise_workspace_path("/etc/passwd"), "etc/passwd")
        self.assertEqual(normalise_workspace_path("..\\..\\windows\\system32"), "windows/system32")

    def test_written_lua_payload_is_captured(self) -> None:
        loader = r"""
        local payload = "print('dumped payload')\n"
        writefile("dumped.lua", payload)
        """
        with tempfile.TemporaryDirectory() as temporary:
            result = LuaEmulator(
                profile="real", workspace_dir=Path(temporary) / "workspace"
            ).run(loader)
        self.assertEqual(result.status, "completed", result.error)
        written = result.written_captures
        self.assertTrue(written, "a written Lua file must be captured")
        self.assertEqual(written[0].chunk_name, "dumped.lua")
        self.assertIn("dumped payload", written[0].text)

    def test_real_executor_identity_is_reported(self) -> None:
        loader = """
        print(identifyexecutor())
        print(getexecutorname())
        print(getthreadidentity())
        print(type(writefile), type(readfile), type(listfiles), type(isfolder))
        print(game.PlaceId > 0, game.JobId ~= "")
        """
        result = LuaEmulator(profile=None).run(loader)
        self.assertEqual(result.status, "completed", result.error)
        prints = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertEqual(prints[0], "Real")
        self.assertEqual(prints[1], "Real")
        self.assertEqual(prints[2], "8")
        self.assertEqual(prints[3].split(), ["function"] * 4)
        self.assertEqual(prints[4].split(), ["true", "true"])

    def test_instance_metatables_are_locked_like_roblox(self) -> None:
        """`getmetatable(instance)` is a string; `getrawmetatable` is the table.

        Payloads use exactly that difference to tell a live Roblox from a
        re-implementation, and they hook `__namecall` through the raw one.
        """

        loader = """
        print("meta=" .. type(getmetatable(game)) .. ":" .. tostring(getmetatable(game)))
        local raw = getrawmetatable(game)
        print("raw=" .. type(raw) .. ":" .. type(raw and raw.__namecall))
        local captured = {}
        raw.__namecall = function(self, ...)
          captured[#captured + 1] = select("#", ...)
          return "hooked"
        end
        print("call=" .. tostring(game:HttpGet("https://example.test/x")))
        print("seen=" .. tostring(#captured))
        """
        result = LuaEmulator(profile="real").run(loader)
        self.assertEqual(result.status, "completed", result.error)
        printed = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any(text.startswith("meta=string") for text in printed), printed)
        self.assertIn("The metatable is locked", " ".join(printed))
        self.assertTrue(any(text.startswith("raw=table:function") for text in printed), printed)
        # The payload's own hook is what runs, exactly like on Roblox.
        self.assertTrue(any(text == "call=hooked" for text in printed), printed)
        self.assertTrue(any(text == "seen=1" for text in printed), printed)

    def test_dumpers_capture_httpget_results(self) -> None:
        """Both namecall hooking idioms a dumper uses must see the call."""
        hookmetamethod_style = f"""
        local captured = {{}}
        local oldNamecall
        oldNamecall = hookmetamethod(game, "__namecall", newcclosure(function(self, ...)
          local method = getnamecallmethod()
          local result = oldNamecall(self, ...)
          if method == "HttpGet" then captured[#captured + 1] = result end
          return result
        end))
        game:HttpGet("{PAYLOAD_URL}")
        print("captured=" .. tostring(#captured) .. ":" .. tostring(captured[1]))
        """
        rawmetatable_style = f"""
        local captured = {{}}
        local mt = getrawmetatable(game)
        local oldNamecall = mt.__namecall
        setreadonly(mt, false)
        mt.__namecall = newcclosure(function(self, ...)
          local result = oldNamecall(self, ...)
          captured[#captured + 1] = tostring(getnamecallmethod()) .. "=" .. tostring(result)
          return result
        end)
        setreadonly(mt, true)
        game:HttpGet("{PAYLOAD_URL}")
        print("raw=" .. tostring(captured[1]))
        """
        for source in (hookmetamethod_style, rawmetatable_style):
            with self.subTest(source=source.strip().splitlines()[0]):
                result = LuaEmulator(profile="real", http_bridge=bridge).run(source)
                self.assertEqual(result.status, "completed", result.error)
                prints = [capture.text for capture in result.captures if capture.kind == "print"]
                self.assertTrue(prints, result.notes)
                self.assertIn(NESTED_SOURCE, prints[-1], prints)

    def test_requests_and_downloads_are_reported(self) -> None:
        loader = f"""
        local response = request({{
          Url = "{PAYLOAD_URL}",
          Method = "POST",
          Headers = {{ ["Authorization"] = "KEY" }},
          Body = '{{"script_key":"KEY"}}',
        }})
        writefile("dump/body.lua", response.Body)
        """
        with tempfile.TemporaryDirectory() as temporary:
            result = LuaEmulator(
                profile="real",
                workspace_dir=Path(temporary) / "workspace",
                request_bridge=lambda options: {
                    "StatusCode": 200,
                    "StatusMessage": "OK",
                    "Headers": {},
                    "Body": NESTED_SOURCE,
                    "Success": True,
                },
            ).run(loader)
        self.assertEqual(result.status, "completed", result.error)
        self.assertEqual([capture.chunk_name for capture in result.request_calls], [PAYLOAD_URL])
        self.assertIn("POST", result.request_calls[0].text)
        self.assertIn("Authorization", result.request_calls[0].text)
        self.assertEqual([capture.chunk_name for capture in result.downloaded_payloads], [PAYLOAD_URL])
        self.assertEqual(result.downloaded_payloads[0].text, NESTED_SOURCE)
        self.assertEqual(result.written_files, ("dump/body.lua",))

    def test_dumper_sandbox_pattern_reaches_the_target(self) -> None:
        """XDumper-style: hook ``genv.loadstring`` and sandbox the input."""
        dumper = f"""
        local genv = getgenv()
        local captured = {{}}
        local realLoadstring = genv.loadstring
        genv.loadstring = newcclosure(function(chunk, chunk_name)
          if type(chunk) == "string" and #chunk > 8 then
            captured[#captured + 1] = chunk
            writefile("XDumper/" .. tostring(#captured) .. "_chunk.lua", chunk)
          end
          return realLoadstring(chunk, chunk_name)
        end)
        local function runSandboxed(source)
          local env = {{}}
          setmetatable(env, {{
            __index = genv,
            __newindex = function(_, key, value) genv[key] = value end,
          }})
          local chunk = realLoadstring(source, "=XDumperInput")
          if not chunk then return false, "load failed" end
          setfenv(chunk, env)
          return pcall(chunk)
        end
        local ok, value = runSandboxed([[
          local body = game:HttpGet("{PAYLOAD_URL}")
          loadstring(body)()
          return "sandbox returned"
        ]])
        print("sandbox=" .. tostring(ok) .. ":" .. tostring(value) .. " captured=" .. tostring(#captured))
        """
        with tempfile.TemporaryDirectory() as temporary:
            result = LuaEmulator(
                profile="real",
                workspace_dir=Path(temporary) / "workspace",
                http_bridge=bridge,
            ).run(dumper)
        self.assertEqual(result.status, "completed", result.error)
        prints = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertIn("sandbox=true:sandbox returned captured=1", prints)
        self.assertEqual(result.written_files, ("XDumper/1_chunk.lua",))
        self.assertEqual(
            [capture.chunk_name for capture in result.downloaded_payloads], [PAYLOAD_URL]
        )
        inner = [capture for capture in result.captures if capture.kind == "loadstring"]
        self.assertTrue(any(capture.text == NESTED_SOURCE for capture in inner), result.captures)

    def test_binary_payloads_are_flagged(self) -> None:
        loader = """
        local bytes = {27, 76, 117, 97, 81, 0, 1, 4, 8}
        local buffer = {}
        for index = 1, #bytes do buffer[index] = string.char(bytes[index]) end
        loadstring(table.concat(buffer))
        """
        result = LuaEmulator(profile="universal").run(loader)
        captured = [capture for capture in result.captures if capture.kind == "loadstring"]
        self.assertTrue(captured)
        self.assertTrue(captured[0].binary)
        self.assertTrue(captured[0].text.startswith("\x1b"))

    def test_unavailable_runtime_is_reported_not_raised(self) -> None:
        result = LuaEmulator(profile="universal").run("print(1)")
        self.assertIn(result.status, {"completed", "unavailable"})
        if result.status == "unavailable":
            self.assertTrue(result.error)


class AvailabilityTests(unittest.TestCase):
    def test_availability_helper_matches_import(self) -> None:
        self.assertEqual(emulator_available(), HAVE_LUA)



class LuauSourceTests(unittest.TestCase):
    """A loader written in Luau must run on the Lua 5.1 backend."""

    def test_luau_only_syntax_runs_end_to_end(self) -> None:
        loader = """
        local total = 0
        for index = 1, 3 do
          local step = if index % 2 == 0 then 1_0 else 2_0
          total += step
        end
        print("total", total // 3)
        """
        result = LuaEmulator(profile="universal").run(loader)
        self.assertEqual(result.status, "completed", result.error)
        printed = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any("16" in text for text in printed), printed)
        self.assertTrue(any("Luau syntax lowered" in note for note in result.notes), result.notes)


class BackendProbeTests(unittest.TestCase):
    """A loader that swallows the step budget must not freeze the host.

    ``while true do pcall(...) end`` keeps running after the budget error is
    caught, and the interpreter cannot be interrupted from inside the same Lua
    state.  The probe runs the script in a disposable child first and reports
    whether it returned, so the engine can skip a hopeless run instead of
    hanging the application.
    """

    def setUp(self) -> None:
        if os.name == "nt" or not hasattr(os, "fork"):
            self.skipTest("process isolation needs fork")
        if not emulator_available():
            self.skipTest("lupa is required for the portable backend")

    def test_a_script_that_returns_is_reported_as_runnable(self) -> None:
        verdict = backend_terminates(
            "local t = {} for i = 1, 3 do t[i] = i * 2 end print(#t)\n",
            timeout_seconds=10.0,
        )
        self.assertIs(verdict, True)

    def test_a_budget_swallowing_loop_does_not_run_forever(self) -> None:
        # The escalation has to neuter the loader's own pcall, otherwise the
        # budget error is caught and the loop retries until the host dies.
        verdict = backend_terminates(
            "while true do pcall(function() local x = 1 end) end\n",
            timeout_seconds=10.0,
            max_instructions=200,
        )
        self.assertIs(verdict, True)

    def test_a_child_that_never_returns_is_killed_and_reported(self) -> None:
        import core.emulator as emulator_module

        def hang(self, source):  # noqa: ANN001 - test double
            time.sleep(60)
            raise AssertionError("the probe should have killed this child")

        original_slack = emulator_module.PROBE_SLACK_SECONDS
        emulator_module.PROBE_SLACK_SECONDS = 0.0
        with unittest.mock.patch.object(emulator_module.LuaEmulator, "run", hang):
            try:
                verdict = backend_terminates("print('hi')\n", timeout_seconds=0.3)
            finally:
                emulator_module.PROBE_SLACK_SECONDS = original_slack
        self.assertIs(verdict, False)


class HostBridgeTests(unittest.TestCase):
    """Host callbacks cross the lupa bridge as *userdata*, not functions.

    A ``type(fn) == 'function'`` guard therefore disables the bridge silently:
    it did, and the Luau lowering inside the backend never ran once.  These
    tests pin the bridge and the helpers that use it.
    """

    def setUp(self) -> None:
        if not HAVE_LUA:
            self.skipTest("lupa is required for the portable backend")

    def test_luau_loaded_at_runtime_is_lowered_and_runs(self) -> None:
        loader = (
            "local chunk = 'local step = if true then 4_2 else 0\\nreturn step'\n"
            "local fn = loadstring(chunk)\n"
            "print('step', fn())\n"
        )
        result = LuaEmulator(profile="universal").run(loader)
        self.assertEqual(result.status, "completed", result.error)
        printed = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any("42" in text for text in printed), printed)

    def test_protez_own_tables_are_tagged_before_the_payload_runs(self) -> None:
        # The VM dumper skips tagged tables: without the tag it reported the
        # executor-name list as an instruction stream.
        loader = "print(rawget(rawget(_G, '__protez_globals'), '__protez_own'))\n"
        result = LuaEmulator(profile="universal").run(loader)
        self.assertEqual(result.status, "completed", result.error)
        printed = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any("true" in text for text in printed), printed)


class BoundedRunTests(unittest.TestCase):
    """A loader that cannot be stopped must not stop the application.

    The backend is run in a forked child under a hard wall-clock deadline, and
    the child spools what it observed: a run that has to be killed still yields
    its evidence, and the parent still performs the host-side work (fetches,
    requests) itself.
    """

    def setUp(self) -> None:
        if not HAVE_LUA:
            self.skipTest("lupa is required for the portable backend")
        if os.name == "nt" or not hasattr(os, "fork"):
            self.skipTest("process isolation is unavailable on this platform")

    def test_a_finished_run_returns_its_full_result(self) -> None:
        from core.emulator import LuaEmulator, run_bounded

        loader = "print('bounded ok')\n"
        result = run_bounded(LuaEmulator(timeout_seconds=10), loader, wall_seconds=20)
        self.assertEqual(result.status, "completed", result.error)
        printed = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any("bounded ok" in text for text in printed), printed)

    def test_a_run_that_cannot_be_stopped_is_killed_and_keeps_its_evidence(self) -> None:
        from core.emulator import LuaEmulator, run_bounded

        # A loader that catches the step stop and keeps looping inside one call:
        # only the process-level stop ends it.
        loader = (
            "print('first')\n"
            "local fn = string.dump(function() return 1 end)\n"
            "while true do\n"
            "  local ok = pcall(function() while true do end end)\n"
            "  _ = ok\n"
            "end\n"
        )
        started = time.monotonic()
        result = run_bounded(
            LuaEmulator(timeout_seconds=30, max_instructions=10**9), loader, wall_seconds=4
        )
        elapsed = time.monotonic() - started
        self.assertLess(elapsed, 12.0, "the wall-clock deadline must bound the run")
        self.assertEqual(result.status, "limit")
        self.assertIn("wall-clock", str(result.error))
        printed = [capture.text for capture in result.captures if capture.kind == "print"]
        self.assertTrue(any("first" in text for text in printed), printed)

    def test_the_parent_performs_bridge_calls_of_a_forked_run(self) -> None:
        from core.emulator import LuaEmulator, run_bounded

        calls: list[str] = []

        def bridge(url, method="GET"):
            calls.append(str(url))
            return "print('remote body')\n"

        loader = (
            "local body = game:HttpGet('https://example.test/library')\n"
            "print('body', body)\n"
        )
        result = run_bounded(
            LuaEmulator(timeout_seconds=10, http_bridge=bridge), loader, wall_seconds=20
        )
        self.assertEqual(result.status, "completed", result.error)
        # The call happened in *this* process: the caller can see it.
        self.assertEqual(calls, ["https://example.test/library"])
        self.assertTrue(any("remote body" in capture.text for capture in result.captures), result.captures)


if __name__ == "__main__":
    unittest.main()
