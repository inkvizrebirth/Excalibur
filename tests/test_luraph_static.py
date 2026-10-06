from __future__ import annotations

import hashlib
import json
import lzma
import logging
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import zstandard

from core.luraph_static import (
    LuraphStaticError,
    decode_luraph_base85,
    inspect_luraph_container,
    unpack_luraph_static,
)
from core.pipeline import DeobfuscationPipeline
from core.protection import inspect_protection


def _encode_luraph_base85(data: bytes) -> str:
    """Build a small LPH Ascii85 literal for deterministic unit fixtures."""
    output: list[str] = []
    for offset in range(0, len(data), 4):
        chunk = data[offset : offset + 4].ljust(4, b"\0")
        if chunk == b"\0\0\0\0":
            output.append("z")
            continue
        value = int.from_bytes(chunk, "little")
        digits: list[str] = []
        for power in (85**4, 85**3, 85**2, 85, 1):
            digit, value = divmod(value, power)
            digits.append(chr(digit + 33))
        output.append("".join(digits))
    return "LPH&" + "".join(output)


def _long_literal(value: str) -> str:
    # A high-equals delimiter avoids collisions with characters in the Ascii85 body.
    return "[========[" + value + "]========]"


def _zstd_stream(value: bytes) -> bytes:
    return zstandard.ZstdCompressor(level=1).compress(value)


def _two_stream_source(
    vm_source: bytes,
    bytecode: bytes,
    *,
    reverse: bool = False,
    version_comment: bool = True,
) -> str:
    streams = [_zstd_stream(vm_source), _zstd_stream(bytecode)]
    if reverse:
        streams.reverse()
    comment = "-- protected using Luraph v14.7\n" if version_comment else ""
    first, second = (_long_literal(_encode_luraph_base85(stream)) for stream in streams)
    return comment + f"local streamA = {first}\nlocal streamB = {second}"


class LuraphStaticDecoderTests(unittest.TestCase):
    def setUp(self) -> None:
        self.vm_source = (
            b"local state = {}; function dispatch(...) while true do return state end end"
        )
        self.bytecode = b"custom-luraph-bytecode\x00\x01\xff"

    def test_base85_decoder_handles_zero_run_and_padding(self) -> None:
        raw = b"\0\0\0\0test!"
        encoded = _encode_luraph_base85(raw)
        decoded = decode_luraph_base85(encoded)
        self.assertEqual(decoded, raw + b"\0\0\0")

    def test_base85_decoder_rejects_invalid_character(self) -> None:
        with self.assertRaisesRegex(LuraphStaticError, "invalid character"):
            decode_luraph_base85("LPH&abc\n12345")

    def test_two_stream_zstandard_unpack_is_order_aware(self) -> None:
        for reverse in (False, True):
            with self.subTest(reverse=reverse):
                source = _two_stream_source(self.vm_source, self.bytecode, reverse=reverse)
                result = unpack_luraph_static(source)
                self.assertEqual(result.layout, "two-stream-zstandard")
                self.assertEqual(result.vm_source, self.vm_source)
                self.assertEqual(result.custom_bytecode, self.bytecode)
                self.assertEqual(len(result.compressed_stream_sizes), 2)

    def test_single_stream_zstandard_extracts_only_custom_bytecode(self) -> None:
        payload = _encode_luraph_base85(_zstd_stream(self.bytecode))
        source = "local packed = " + _long_literal(payload)
        info = inspect_luraph_container(source)
        self.assertTrue(info.detected)
        self.assertEqual(info.layout, "single-stream-zstandard")

        result = unpack_luraph_static(source)
        self.assertEqual(result.layout, "single-stream-zstandard")
        self.assertIsNone(result.vm_source)
        self.assertEqual(result.custom_bytecode, self.bytecode)

    def test_legacy_two_stream_range_layout_is_decoded_statistically(self) -> None:
        filters = [
            {
                "id": lzma.FILTER_LZMA1,
                "dict_size": 1 << 20,
                "lc": 3,
                "lp": 0,
                "pb": 0,
            }
        ]
        compressed_vm = lzma.compress(self.vm_source, format=lzma.FORMAT_RAW, filters=filters)
        compressed_bytecode = lzma.compress(self.bytecode, format=lzma.FORMAT_RAW, filters=filters)
        source = _two_stream_source_from_encoded(compressed_vm, compressed_bytecode)

        result = unpack_luraph_static(source)

        self.assertEqual(result.layout, "two-stream-range")
        self.assertEqual(result.vm_source, self.vm_source)
        self.assertEqual(result.custom_bytecode, self.bytecode)

    def test_luraph_container_detection_ignores_comments_and_short_strings(self) -> None:
        payload = _encode_luraph_base85(_zstd_stream(self.bytecode))
        source = (
            "-- [====[LPH&not a stream]====]\n"
            'local decoy = "[====[LPH&also-not-a-stream]====]"\n'
            "local real = [========[\n" + payload + "]========]"
        )
        info = inspect_luraph_container(source)
        self.assertTrue(info.detected)
        self.assertEqual(info.long_string_count, 1)
        self.assertEqual(info.valid_stream_count, 1)
        self.assertEqual(info.layout, "single-stream-zstandard")

    def test_protection_detection_supports_luraph_version_comment_without_obfuscator_word(
        self,
    ) -> None:
        source = _two_stream_source(self.vm_source, self.bytecode)
        profile = inspect_protection(source)
        self.assertIsNotNone(profile)
        assert profile is not None
        self.assertEqual(profile.version, "14.7")
        self.assertEqual(profile.valid_payload_streams, 2)
        self.assertEqual(profile.container_layout, "two-stream-zstandard")

    def test_headerless_container_is_still_detected(self) -> None:
        source = _two_stream_source(self.vm_source, self.bytecode, version_comment=False)
        profile = inspect_protection(source)
        self.assertIsNotNone(profile)
        assert profile is not None
        self.assertIsNone(profile.version)
        self.assertEqual(profile.valid_payload_streams, 2)

    def test_static_unpack_enforces_decoded_size_limit(self) -> None:
        payload = _encode_luraph_base85(_zstd_stream(b"x" * 1024))
        source = "local packed = " + _long_literal(payload)
        with self.assertRaisesRegex(LuraphStaticError, "safety limit"):
            unpack_luraph_static(source, max_output_bytes=64)

    def test_source_installer_checks_the_zstandard_runtime(self) -> None:
        import installer

        self.assertIn("zstandard", installer.DISTRIBUTIONS)

    def test_pipeline_writes_intermediate_artifacts_without_running_any_luau(self) -> None:
        source = _two_stream_source(self.vm_source, self.bytecode)
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            pipeline = DeobfuscationPipeline(
                logger=logging.getLogger("protez.test.luraph-static"),
                output_dir=output_dir,
                tools_dir=output_dir / "no-tools",
            )
            with (
                patch("core.pipeline.Sandbox", side_effect=AssertionError("sandbox must not run")),
                patch(
                    "core.pipeline._LuauCompiler",
                    side_effect=AssertionError("compiler must not run"),
                ),
                patch("core.pipeline.Tracer", side_effect=AssertionError("tracer must not run")),
            ):
                result = pipeline.run(source, source_name="public-v147-fixture.luau")

            report = json.loads(result.report_path.read_text(encoding="utf-8"))
            self.assertEqual(result.status, "partial")
            self.assertEqual(result.route, "static-protection-report")
            self.assertIsNone(result.sandbox_result)
            self.assertFalse(report["source_reconstructed"])
            self.assertFalse(report["payload_executed"])
            self.assertTrue(report["static_unpack"]["success"])
            self.assertFalse(report["static_unpack"]["wrapper_executed"])
            self.assertFalse(report["static_unpack"]["vm_interpreter_executed"])
            self.assertEqual(report["static_unpack"]["container_layout"], "two-stream-zstandard")

            vm_path = Path(report["outputs"]["luraph_vm_interpreter"])
            bytecode_path = Path(report["outputs"]["luraph_custom_bytecode"])
            self.assertEqual(vm_path.read_bytes(), self.vm_source)
            self.assertEqual(bytecode_path.read_bytes(), self.bytecode)
            self.assertEqual(
                report["static_unpack"]["custom_bytecode"]["sha256"],
                hashlib.sha256(self.bytecode).hexdigest(),
            )
            summary = result.output_path.read_text(encoding="utf-8")
            self.assertIn("ORIGINAL SOURCE NOT RECONSTRUCTED", summary)
            self.assertIn("not Luau bytecode", summary)
            self.assertIn("were not executed", summary)
            self.assertEqual(len(list(output_dir.iterdir())), 5)

    def test_pipeline_reports_unsupported_single_legacy_stream_as_partial(self) -> None:
        source = "-- Luraph Obfuscator v14.7\nlocal x = [====[LPH&" + "B" * 64 + "]====]"
        with tempfile.TemporaryDirectory() as temporary_directory:
            output_dir = Path(temporary_directory)
            pipeline = DeobfuscationPipeline(
                logger=logging.getLogger("protez.test.luraph-unsupported"),
                output_dir=output_dir,
                tools_dir=output_dir / "no-tools",
            )
            result = pipeline.run(source, source_name="unsupported.luau")
            report = json.loads(result.report_path.read_text(encoding="utf-8"))

            self.assertEqual(result.status, "partial")
            self.assertFalse(report["static_unpack"]["success"])
            self.assertFalse(report["payload_executed"])
            self.assertIsNone(report["outputs"]["luraph_custom_bytecode"])
            self.assertEqual(len(list(output_dir.iterdir())), 3)


def _two_stream_source_from_encoded(vm_stream: bytes, bytecode_stream: bytes) -> str:
    return (
        "-- protected using Luraph v14.7\nlocal streamA = "
        + _long_literal(_encode_luraph_base85(vm_stream))
        + "\nlocal streamB = "
        + _long_literal(_encode_luraph_base85(bytecode_stream))
    )


if __name__ == "__main__":
    unittest.main()
