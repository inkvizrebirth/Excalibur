from __future__ import annotations

import tempfile
import unittest
from pathlib import Path

from core.emulator import LuaEmulator, classify_chunk, emulator_available

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


if __name__ == "__main__":
    unittest.main()
