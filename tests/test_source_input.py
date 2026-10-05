from __future__ import annotations

import logging
import unittest
from unittest.mock import Mock, patch

from core.source_input import (
    SourceInputError,
    _assert_public_http_url,
    _normalise_code_url,
    fetch_code_url,
    resolve_source_input,
)


class _Headers(dict):
    def __init__(self, *args, charset: str | None = None, **kwargs):
        super().__init__(*args, **kwargs)
        self._charset = charset

    def get_content_charset(self):
        return self._charset

    def get_content_type(self):
        return self.get("Content-Type", "").split(";", 1)[0]


class _Response:
    def __init__(self, body: bytes, *, url: str, content_type: str = "text/plain", charset=None):
        self._body = body
        self._url = url
        self.headers = _Headers({"Content-Type": content_type}, charset=charset)

    def __enter__(self):
        return self

    def __exit__(self, *_args):
        return None

    def geturl(self):
        return self._url

    def read(self, size: int = -1):
        if not self._body:
            return b""
        if size < 0:
            size = len(self._body)
        block, self._body = self._body[:size], self._body[size:]
        return block


class SourceInputTests(unittest.TestCase):
    def test_leaves_direct_luau_source_unchanged(self) -> None:
        source = 'local message = "hello"\nprint(message)'
        result = resolve_source_input(source)
        self.assertEqual(result.source, source)
        self.assertEqual(result.fetched_urls, ())

    def test_fetches_a_plain_code_link(self) -> None:
        fetcher = Mock(return_value="print('from link')")
        result = resolve_source_input(
            "https://raw.githubusercontent.com/example/repo/main/main.luau",
            source_name="pasted input",
            fetcher=fetcher,
        )
        fetcher.assert_called_once_with(
            "https://raw.githubusercontent.com/example/repo/main/main.luau"
        )
        self.assertEqual(result.source, "print('from link')")
        self.assertEqual(result.source_name, "main.luau")
        self.assertEqual(len(result.fetched_urls), 1)

    def test_converts_github_blob_links_to_raw_links(self) -> None:
        self.assertEqual(
            _normalise_code_url(
                "https://github.com/team/project/blob/main/src/file.luau?raw=1#readme"
            ),
            "https://raw.githubusercontent.com/team/project/main/src/file.luau?raw=1",
        )

    def test_converts_pastebin_page_links_to_raw_links(self) -> None:
        self.assertEqual(
            _normalise_code_url("https://www.pastebin.com/AbC123#view"),
            "https://pastebin.com/raw/AbC123",
        )

    def test_follows_a_simple_loadstring_httpget_wrapper(self) -> None:
        wrapper = 'loadstring(game:HttpGet("https://pastebin.com/AbC123"))()'
        fetcher = Mock(return_value="local answer = 42")
        result = resolve_source_input(wrapper, fetcher=fetcher)
        fetcher.assert_called_once_with("https://pastebin.com/raw/AbC123")
        self.assertEqual(result.source, "local answer = 42")
        self.assertEqual(result.source_name, "AbC123")

    def test_finds_a_loader_url_built_from_constant_strings(self) -> None:
        wrapper = 'loadstring(game:HttpGet("https://" .. "pastebin.com/raw/AbC123"))()'
        fetcher = Mock(return_value="print('decoded link')")
        result = resolve_source_input(wrapper, fetcher=fetcher)
        fetcher.assert_called_once_with("https://pastebin.com/raw/AbC123")
        self.assertEqual(result.source, "print('decoded link')")

    def test_follows_nested_remote_loader_links_with_a_cap(self) -> None:
        fetcher = Mock(
            side_effect=[
                'loadstring(game:HttpGet("https://pastebin.com/Second"))()',
                "print('final source')",
            ]
        )
        result = resolve_source_input(
            "https://pastebin.com/First",
            fetcher=fetcher,
            logger=logging.getLogger("source-input-test"),
        )
        self.assertEqual(result.source, "print('final source')")
        self.assertEqual(fetcher.call_count, 2)
        self.assertEqual(result.source_name, "Second")

    def test_understands_escaped_loader_urls(self) -> None:
        wrapper = r'loadstring(game:HttpGet("https:\/\/pastebin.com\/raw\/AbC"))()'
        fetcher = Mock(return_value="print('ok')")
        result = resolve_source_input(wrapper, fetcher=fetcher)
        fetcher.assert_called_once_with("https://pastebin.com/raw/AbC")
        self.assertEqual(result.source, "print('ok')")

    def test_requires_a_single_unambiguous_loader_url(self) -> None:
        wrapper = (
            'loadstring(game:HttpGet("https://pastebin.com/one"))() '
            '-- https://pastebin.com/two'
        )
        with self.assertRaisesRegex(SourceInputError, "more than one code link"):
            resolve_source_input(wrapper, fetcher=Mock())

    def test_does_not_fetch_unrelated_urls_in_source_comments(self) -> None:
        source = '-- example: https://example.invalid/file.lua\nprint("safe")'
        result = resolve_source_input(source, fetcher=Mock())
        self.assertEqual(result.source, source)

    def test_blocks_private_and_non_http_targets(self) -> None:
        for url in (
            "http://127.0.0.1/script.lua",
            "http://localhost/script.lua",
            "file:///tmp/script.lua",
        ):
            with self.subTest(url=url), self.assertRaises(SourceInputError):
                _assert_public_http_url(url)

    def test_fetches_utf8_text_with_bounded_reads(self) -> None:
        body = "local value = 'здравствуйте'".encode("utf-8")
        response = _Response(body, url="https://raw.example.net/script.lua", charset="utf-8")
        opener = Mock()
        opener.open.return_value = response
        with patch("core.source_input._assert_public_http_url"):
            text = fetch_code_url("https://raw.example.net/script.lua", opener=opener)
        self.assertEqual(text, "local value = 'здравствуйте'")
        opener.open.assert_called_once()

    def test_rejects_html_and_oversized_responses(self) -> None:
        html_response = _Response(
            b"<!doctype html><html><body>not code</body></html>",
            url="https://example.net/script.lua",
            content_type="text/html",
        )
        opener = Mock()
        opener.open.return_value = html_response
        with patch("core.source_input._assert_public_http_url"), self.assertRaisesRegex(
            SourceInputError, "web page"
        ):
            fetch_code_url("https://example.net/script.lua", opener=opener)

        large_response = _Response(
            b"0123456789",
            url="https://example.net/script.lua",
        )
        opener.open.return_value = large_response
        with patch("core.source_input._assert_public_http_url"), self.assertRaisesRegex(
            SourceInputError, "larger than"
        ):
            fetch_code_url("https://example.net/script.lua", max_bytes=8, opener=opener)


if __name__ == "__main__":
    unittest.main()
