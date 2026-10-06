from __future__ import annotations

import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from core.bytecode_decompiler import (
    BytecodeDecompilerError,
    LocalBytecodeDecompiler,
)


class LocalBytecodeDecompilerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.root = Path(self.temporary.name)
        self.tools = self.root / "tools"
        self.tools.mkdir()
        self.binary = self.tools / "luau-decompiler"
        self.binary.write_bytes(b"unit-test marker; never executed")
        self.binary.chmod(0o755)

    def tearDown(self) -> None:
        self.temporary.cleanup()

    def test_invokes_cli_with_documented_input_and_output_arguments(self) -> None:
        decompiler = LocalBytecodeDecompiler(tools_dir=self.tools)
        observed: dict[str, object] = {}

        def record_command(command: list[str], *, cwd: Path) -> str:
            observed["command"] = command
            observed["cwd"] = cwd
            output_path = Path(command[command.index("--output") + 1])
            output_path.write_text("local x = 1\nreturn x\n", encoding="utf-8")
            return "decompiled"

        with patch.object(decompiler, "_run", side_effect=record_command):
            source, binary = decompiler.decompile(b"compiled bytes", source_name="../sample.lbc")

        command = observed["command"]
        self.assertEqual(binary, self.binary.resolve())
        self.assertEqual(source, "local x = 1\nreturn x\n")
        self.assertEqual(command[0], str(self.binary.resolve()))
        self.assertEqual(command[2], "--output")
        self.assertEqual(len(command), 4)
        self.assertNotIn("--opmap-cache", command)
        self.assertEqual(Path(command[1]).name, "sample.lbc")
        self.assertEqual(Path(command[1]).parent, observed["cwd"])
        self.assertEqual(Path(command[3]).parent, observed["cwd"])

    def test_rejects_empty_input_and_input_over_the_size_limit(self) -> None:
        decompiler = LocalBytecodeDecompiler(tools_dir=self.tools)
        with self.assertRaisesRegex(BytecodeDecompilerError, "empty"):
            decompiler.decompile(b"")

        with patch("core.bytecode_decompiler.MAX_BYTECODE_BYTES", 2):
            with self.assertRaisesRegex(BytecodeDecompilerError, "input limit"):
                decompiler.decompile(b"123")

    def test_requires_a_local_executable(self) -> None:
        self.binary.unlink()
        decompiler = LocalBytecodeDecompiler(tools_dir=self.tools)
        with patch("core.bytecode_decompiler.shutil.which", return_value=None):
            with self.assertRaisesRegex(BytecodeDecompilerError, "No local"):
                decompiler.decompile(b"compiled bytes")

    def test_pinned_provenance_is_claimed_only_for_a_matching_frozen_bundle(self) -> None:
        packaged = self.root / "_MEIPASS" / "tools"
        packaged.mkdir(parents=True)
        packaged_binary = packaged / self.binary.name
        packaged_binary.write_bytes(self.binary.read_bytes())
        decompiler = LocalBytecodeDecompiler(tools_dir=self.tools)

        with (
            patch("core.bytecode_decompiler.IS_FROZEN", True),
            patch("core.bytecode_decompiler.PACKAGED_TOOLS_DIR", packaged),
        ):
            self.assertTrue(decompiler.is_bundled_binary(self.binary))
            self.binary.write_bytes(b"different executable")
            self.assertFalse(decompiler.is_bundled_binary(self.binary))

        with patch("core.bytecode_decompiler.IS_FROZEN", False):
            self.assertFalse(decompiler.is_bundled_binary(packaged_binary))


if __name__ == "__main__":
    unittest.main()
