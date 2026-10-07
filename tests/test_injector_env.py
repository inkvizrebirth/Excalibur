from __future__ import annotations

import unittest

from core.injector_env import (
    DEFAULT_PROFILE_KEY,
    EXECUTOR_PROFILES,
    build_http_stub_prelude,
    build_lua_prelude,
    build_static_environment,
    detect_executor_keys,
    get_profile,
    profile_choices,
    static_call,
)

try:  # the portable backend is optional
    from lupa import lua51
except Exception:  # noqa: BLE001
    lua51 = None


class ProfileTests(unittest.TestCase):
    def test_default_profile_is_universal(self) -> None:
        profile = get_profile(None)
        self.assertEqual(profile.key, DEFAULT_PROFILE_KEY)
        self.assertTrue(profile.universal)

    def test_unknown_profile_falls_back_to_default(self) -> None:
        self.assertEqual(get_profile("does-not-exist").key, DEFAULT_PROFILE_KEY)

    def test_profile_choices_cover_the_named_executors(self) -> None:
        keys = dict(profile_choices())
        expected = {
            "universal",
            "synapse",
            "krnl",
            "fluxus",
            "solara",
            "delta",
            "wave",
            "xeno",
            "hydrogen",
            "swift",
            "scriptware",
            "wearedevs",
            "plain",
        }
        self.assertTrue(expected.issubset(set(keys)))

    def test_every_profile_has_a_label_and_features(self) -> None:
        for profile in EXECUTOR_PROFILES:
            with self.subTest(profile=profile.key):
                self.assertTrue(profile.label)
                self.assertTrue(profile.executor_name)
                self.assertTrue(profile.features)


class DetectionTests(unittest.TestCase):
    def test_detects_referenced_executor_names(self) -> None:
        source = "if syn and syn.protect_gui then end\nprint(KRNL_LOADED, fluxus)"
        keys = detect_executor_keys(source)
        self.assertIn("synapse", keys)
        self.assertIn("krnl", keys)
        self.assertIn("fluxus", keys)

    def test_ignores_plain_scripts(self) -> None:
        self.assertEqual(detect_executor_keys("local value = 1\nprint(value)"), ())

    def test_rejects_non_text(self) -> None:
        with self.assertRaises(TypeError):
            detect_executor_keys(b"print(1)")  # type: ignore[arg-type]


class StaticEnvironmentTests(unittest.TestCase):
    def test_default_profile_is_the_real_executor(self) -> None:
        profile = get_profile(None)
        self.assertEqual(profile.key, "real")
        self.assertEqual(profile.executor_name, "Real")
        handled, value = static_call("identifyexecutor", [])
        self.assertTrue(handled)
        self.assertEqual(value, b"Real")
        handled, value = static_call("getfpscap", [])
        self.assertTrue(handled)
        self.assertEqual(value, 60)
        handled, first = static_call("gethwid", [])
        handled_again, second = static_call("gethwid", [])
        self.assertTrue(handled and handled_again)
        self.assertEqual(first, second)

    def test_static_environment_matches_the_profile(self) -> None:
        environment = build_static_environment()
        self.assertEqual(environment["identifyexecutor"](), b"Real")
        self.assertEqual(environment["getexecutorname"](), b"Real")
        self.assertIs(environment["isfile"]("dump.lua"), False)
        self.assertEqual(environment["getthreadidentity"](), 8)
        self.assertEqual(environment["getfpscap"](), 60)

    def test_identifyexecutor_folds_to_the_profile_name(self) -> None:
        profile = get_profile("krnl")
        handled, value = static_call("identifyexecutor", [], profile=profile)
        self.assertTrue(handled)
        self.assertEqual(value, b"Krnl")

    def test_feature_probes_answer_deterministically(self) -> None:
        handled, value = static_call("checkcaller", [])
        self.assertTrue(handled)
        self.assertTrue(value)
        handled, value = static_call("getthreadidentity", [])
        self.assertEqual((handled, value), (True, 8))

    def test_unknown_function_is_not_handled(self) -> None:
        handled, value = static_call("some_random_library_call", [])
        self.assertFalse(handled)
        self.assertIsNone(value)

    def test_static_environment_carries_script_key(self) -> None:
        environment = build_static_environment(script_key="KEY-1")
        self.assertEqual(environment["script_key"], "KEY-1")


class PreludeTests(unittest.TestCase):
    def test_universal_prelude_has_no_placeholders(self) -> None:
        for key in ("universal", "krnl", "plain"):
            with self.subTest(profile=key):
                prelude = build_lua_prelude(get_profile(key))
                self.assertNotIn("@@", prelude)
                self.assertIn("__protez_profile", prelude)

    def test_prelude_exposes_the_requested_executor(self) -> None:
        prelude = build_lua_prelude(get_profile("solara"))
        self.assertIn('"Solara"', prelude)
        self.assertIn("getgenv", prelude)

    def test_robots_surface_can_be_disabled(self) -> None:
        prelude = build_lua_prelude(get_profile("universal"), roblox=False)
        self.assertNotIn("GetService", prelude)

    def test_script_key_is_injected(self) -> None:
        prelude = build_lua_prelude(get_profile("universal"), script_key="abc")
        self.assertIn('script_key = "abc"', prelude)

    def test_http_stub_prelude_contains_responses(self) -> None:
        stub = build_http_stub_prelude({"https://cdn/payload.lua": "print(1)"})
        self.assertIn("https://cdn/payload.lua", stub)
        self.assertIn("__protez_http_bridge", stub)


@unittest.skipIf(lua51 is None, "lupa Lua 5.1 is unavailable")
class PreludeRuntimeTests(unittest.TestCase):
    def _run(self, script: str, *, profile: str = "universal", responses=None) -> None:
        prelude = build_lua_prelude(get_profile(profile))
        stub = build_http_stub_prelude(responses or {})
        runtime = lua51.LuaRuntime()
        runtime.execute(prelude + "\n" + stub + "\n" + script)

    def test_executor_surface_survives_injector_probes(self) -> None:
        self._run(
            """
            assert(identifyexecutor() == "Synapse X", "executor name")
            assert(isfunction(print), "isfunction")
            assert(type(syn) == "table", "syn table")
            assert(type(syn.protect_gui) == "function", "syn.protect_gui")
            assert(KRNL_LOADED ~= nil and fluxus ~= nil, "marker globals")
            assert(getthreadidentity() == 8, "thread identity")
            assert(checkcaller() == true, "checkcaller")
            """
        )

    def test_getgenv_writes_are_visible_globally(self) -> None:
        self._run(
            """
            getgenv().Shared = { count = 1 }
            Shared.count = Shared.count + 1
            local environment = getgenv()
            assert(environment.Shared.count == 2, "getgenv write-through")
            assert(shared == environment, "shared aliases the environment")
            """
        )

    def test_roblox_proxies_do_not_raise(self) -> None:
        self._run(
            """
            local players = game:GetService("Players")
            local player = players.LocalPlayer
            assert(type(player.Name) == "string", "player name")
            local part = Instance.new("Part")
            part.Name = "hello"
            assert(part.IsA(part, "BasePart") == true, "IsA proxy")
            local connection = game:GetService("RunService").Heartbeat:Connect(function() end)
            assert(type(connection.Disconnect) == "function", "connection")
            """
        )

    def test_luau_library_gaps_are_filled(self) -> None:
        self._run(
            """
            assert(bit32.bxor(0x5A, 0x0F) == 85, "bxor")
            assert(bit32.band(0xF0, 0x3C) == 48, "band")
            assert(bit32.lshift(1, 8) == 256, "lshift")
            assert(string.split("a,b,c", ",")[2] == "b", "split")
            assert(math.round(2.4) == 2, "round")
            assert(math.clamp(9, 1, 3) == 3, "clamp")
            assert(table.create(2, 7)[1] == 7, "table.create")
            assert(utf8.char(104, 105) == "hi", "utf8.char")
            """
        )

    def test_http_bridge_serves_canned_payloads(self) -> None:
        self._run(
            """
            local body = game:HttpGet("https://cdn.example/payload.lua")
            assert(body == "return 7", "game:HttpGet bridge")
            local response = request({ Url = "https://cdn.example/payload.lua" })
            assert(response.Body == "return 7", "request bridge")
            assert(response.StatusCode == 200, "status code")
            """,
            responses={"https://cdn.example/payload.lua": "return 7"},
        )

    def test_plain_profile_keeps_the_scaffolding_but_hides_the_executor(self) -> None:
        self._run(
            """
            assert(type(getgenv) == "function", "getgenv")
            assert(type(game) == "table", "game table")
            """,
            profile="plain",
        )


if __name__ == "__main__":
    unittest.main()
