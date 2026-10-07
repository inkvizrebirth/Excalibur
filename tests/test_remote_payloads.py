from __future__ import annotations

import json
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.pipeline import DeobfuscationPipeline
from core.remote_payloads import (
    PayloadFetcher,
    RemotePayloadError,
    extract_script_key,
    extract_urls,
    is_luarmor,
    luarmor_payload_url,
    luarmor_signature,
)

LOADER_ID = "d41d8cd98f00b204e9800998ecf8427e"
LOADER_URL = luarmor_payload_url(LOADER_ID)
PAYLOAD_URL = "https://cdn.example/library/payload.lua"
PAYLOAD_BODY = 'print("recovered from a private library")\nprint("recovered from an api-protected loader")'

LUARMOR_LOADER = f"""-- Luarmor protected
script_key = "KEY-123"
local ok, err = pcall(function()
  return loadstring(game:HttpGet("{LOADER_URL}"))()
end)
"""

STAGE_ONE = f"""
local script_key = script_key or "KEY-123"
local body = game:HttpGet("{PAYLOAD_URL}")
return loadstring(body)()
"""

# A script whose body lives behind a web API: the raw link answers with HTML
# (or nothing) in a browser, and only the loader -- running inside the executor
# with the right request body -- receives the payload. The loader also parks a
# copy of what it decoded in the executor workspace with ``writefile``.
PAYLOAD_MARKER = "recovered from an api-protected loader"

# ``api защита``: the script body lives behind a web API. The raw link cannot be
# opened in a browser, and the URL is assembled at runtime, so the only way to
# reach the payload is to actually run the loader inside an executor -- with its
# ``request`` call, its file API and its identity functions.
API_PAYLOAD = f"""-- protected library payload
local parts = {{ "recovered", "from", "an", "api-protected", "loader" }}
local message = table.concat(parts, " ")
print(message)
"""

API_LOADER = f"""-- api защита: the payload is only served to a running loader
script_key = "KEY-123"
local executor = identifyexecutor and identifyexecutor() or "unknown"
assert(type(writefile) == "function", "no file api")
local scheme = "https"
local host = table.concat({{ "cdn", "example" }}, ".")
local url = scheme .. "://" .. host .. "/library/" .. ("pay" .. "load.lua")
local response = request({{
  Url = url,
  Method = "POST",
  Headers = {{ ["Authorization"] = "KEY-123", ["Content-Type"] = "application/json" }},
  Body = '{{"script_key":"KEY-123"}}',
}})
local payload = response.Body
makefolder("dump")
writefile("dump/payload.lua", payload)
appendfile("dump/_log.txt", executor .. "\\n")
local chunk = loadstring(payload)
if chunk then chunk() end
"""




class SignatureTests(unittest.TestCase):
    def test_luarmor_loader_is_recognised_without_running_it(self) -> None:
        self.assertTrue(is_luarmor(LUARMOR_LOADER))
        signature = luarmor_signature(LUARMOR_LOADER)
        self.assertIsNotNone(signature)
        assert signature is not None
        self.assertEqual(signature["vendor"], "Luarmor")
        self.assertEqual(signature["loader_id"], LOADER_ID)
        self.assertEqual(signature["loader_url"], LOADER_URL)
        self.assertEqual(signature["script_key"], "KEY-123")
        self.assertFalse(signature["needs_runtime_key"])

    def test_script_key_and_urls_are_extracted(self) -> None:
        self.assertEqual(extract_script_key(LUARMOR_LOADER), "KEY-123")
        urls = extract_urls(LUARMOR_LOADER)
        self.assertIn(LOADER_URL, urls)

    def test_plain_scripts_have_no_signature(self) -> None:
        self.assertIsNone(luarmor_signature("print('hello')"))
        self.assertFalse(is_luarmor("print('hello')"))


class FetcherTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.cache = Path(self.temporary.name)
        self.calls: list[str] = []

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def _fetcher(self, bodies: dict[str, str]) -> PayloadFetcher:
        fetcher = PayloadFetcher(
            enabled=True,
            logger=logging.getLogger("protez.test.fetcher"),
            cache_dir=self.cache,
        )

        def download(url, *, use_roblox_headers=None):
            self.calls.append(url)
            if url not in bodies:
                raise RemotePayloadError(f"no canned body for {url}")
            return bodies[url]

        fetcher._download = download  # type: ignore[method-assign]
        return fetcher

    def test_fetch_records_and_caches(self) -> None:
        fetcher = self._fetcher({PAYLOAD_URL: PAYLOAD_BODY})
        first = fetcher.fetch(PAYLOAD_URL)
        second = fetcher.fetch(PAYLOAD_URL)

        self.assertEqual(first, PAYLOAD_BODY)
        self.assertEqual(second, PAYLOAD_BODY)
        self.assertEqual(self.calls, [PAYLOAD_URL], "second read must come from the cache")
        statuses = [record.status for record in fetcher.records]
        self.assertEqual(statuses, ["fetched", "cached"])
        self.assertEqual(fetcher.responses[PAYLOAD_URL], PAYLOAD_BODY)

    def test_disabled_fetcher_refuses_to_fetch(self) -> None:
        fetcher = PayloadFetcher(enabled=False, logger=logging.getLogger("protez.test.fetcher"))
        with self.assertRaises(RemotePayloadError):
            fetcher.fetch(PAYLOAD_URL)

    def test_fetch_limit_is_enforced(self) -> None:
        fetcher = self._fetcher({PAYLOAD_URL: PAYLOAD_BODY, "https://cdn.example/other.lua": "x"})
        fetcher.max_fetches = 1  # type: ignore[misc]
        fetcher.fetch(PAYLOAD_URL)
        with self.assertRaises(RemotePayloadError):
            fetcher.fetch("https://cdn.example/other.lua")

    def test_request_bridge_serves_api_payloads(self) -> None:
        fetcher = self._fetcher({PAYLOAD_URL: PAYLOAD_BODY})
        response = fetcher.request_bridge(
            {"Url": PAYLOAD_URL, "Method": "POST", "Body": '{"script_key":"KEY-123"}'}
        )
        self.assertEqual(response["StatusCode"], 200)
        self.assertEqual(response["Body"], PAYLOAD_BODY)
        self.assertTrue(response["Success"])
        self.assertEqual(self.calls, [PAYLOAD_URL])

        missing = fetcher.request_bridge({"Url": "https://cdn.example/gone.lua"})
        self.assertFalse(missing["Success"])
        self.assertEqual(missing["Body"], "")
        self.assertFalse(fetcher.request_bridge({"Url": "not-a-url"})["Success"])

    def test_bridge_serves_roblox_style_calls(self) -> None:
        fetcher = self._fetcher({PAYLOAD_URL: PAYLOAD_BODY})
        # game:HttpGet(url) passes the instance table first.
        self.assertEqual(fetcher.bridge(object(), PAYLOAD_URL), PAYLOAD_BODY)
        self.assertEqual(fetcher.bridge("not a url"), "")

    def test_failed_downloads_are_recorded_not_raised(self) -> None:
        fetcher = self._fetcher({})
        self.assertEqual(fetcher.bridge(PAYLOAD_URL), "")
        self.assertEqual(fetcher.records[-1].status, "failed")


class PipelineRemoteTests(unittest.TestCase):
    """The loader chain must resolve private-library payloads through the bridge."""

    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.output = self.root / "output"
        self.logs = self.root / "logs"
        self.cache = self.root / "cache"

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_two_stage_library_chain_is_recovered(self) -> None:
        bodies = {LOADER_URL: STAGE_ONE, PAYLOAD_URL: PAYLOAD_BODY}

        def download(self, url, *, use_roblox_headers=None):
            if url not in bodies:
                raise RemotePayloadError(f"no canned body for {url}")
            return bodies[url]

        pipeline = DeobfuscationPipeline(
            logger=logging.getLogger("protez.test.remote"),
            output_dir=self.output,
            logs_dir=self.logs,
            allow_network=True,
        )
        with (
            patch.object(PayloadFetcher, "_download", download),
            patch.object(PayloadFetcher, "cache_dir", self.cache, create=True),
        ):
            result = pipeline.run(LUARMOR_LOADER, source_name="luarmor.luau")

        body = result.output_path.read_text(encoding="utf-8")
        self.assertIn("recovered from a private library", body)
        self.assertEqual([item.name for item in self.output.iterdir()], ["destroyed_1.lua"])

        report = json.loads(result.report_path.read_text(encoding="utf-8"))
        fetched = {entry["url"] for entry in report["remote_fetches"]}
        self.assertIn(PAYLOAD_URL, fetched)

    def test_api_protected_loader_is_recovered(self) -> None:
        """A payload the loader only receives (and writes) at runtime."""

        calls: list[str] = []

        def download(self, url, *, use_roblox_headers=None):
            calls.append(url)
            if url == PAYLOAD_URL:
                return API_PAYLOAD
            raise RemotePayloadError(f"no canned body for {url}")

        pipeline = DeobfuscationPipeline(
            logger=logging.getLogger("protez.test.remote.api"),
            output_dir=self.output,
            logs_dir=self.logs,
            allow_network=True,
        )
        with (
            patch.object(PayloadFetcher, "_download", download),
            patch.object(PayloadFetcher, "cache_dir", self.cache, create=True),
        ):
            result = pipeline.run(API_LOADER, source_name="api-protected.luau")

        body = result.output_path.read_text(encoding="utf-8")
        # The payload itself, not the loader that fetched it.
        self.assertIn('table.concat(parts, " ")', body)
        self.assertIn("api-protected", body)
        self.assertNotIn("script_key", body)
        self.assertEqual([item.name for item in self.output.iterdir()], ["destroyed_1.lua"])
        self.assertEqual(calls, [PAYLOAD_URL], "the payload may only be fetched at runtime")

        report = json.loads(result.report_path.read_text(encoding="utf-8"))
        self.assertEqual(report["route"], "recovery engine")
        self.assertEqual(
            {entry["url"] for entry in report["remote_fetches"]},
            {PAYLOAD_URL},
        )
        emulator = report["emulator"]
        self.assertIsNotNone(emulator)
        assert emulator is not None
        self.assertEqual(emulator["status"], "completed", emulator["error"])
        self.assertTrue(emulator["requests"] >= 1)
        self.assertTrue(
            any(item["path"] == "dump/payload.lua" for item in emulator["workspace_files"]),
            emulator["workspace_files"],
        )
        # The mirrored workspace keeps what the loader wrote, next to the report.
        mirrored = self.logs / "executor-workspace" / "dump" / "payload.lua"
        self.assertTrue(mirrored.is_file(), sorted(str(item) for item in self.logs.rglob("*")))
        self.assertIn("recovered", mirrored.read_text(encoding="utf-8"))
        self.assertTrue((self.logs / "executor-workspace" / "dump" / "_log.txt").is_file())

    def test_offline_run_still_produces_output(self) -> None:
        pipeline = DeobfuscationPipeline(
            logger=logging.getLogger("protez.test.remote.offline"),
            output_dir=self.output,
            logs_dir=self.logs,
            allow_network=False,
        )
        result = pipeline.run(LUARMOR_LOADER, source_name="luarmor-offline.luau")
        self.assertTrue(result.output_path.is_file())
        self.assertEqual([item.name for item in self.output.iterdir()], ["destroyed_1.lua"])


if __name__ == "__main__":
    unittest.main()
