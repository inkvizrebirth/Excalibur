from __future__ import annotations

import unittest

from core.deobfuscator import MAX_SOURCE_BYTES, deobfuscate_source


class DeobfuscatorTests(unittest.TestCase):
    def test_decodes_nested_string_and_bit32_calls(self) -> None:
        source = 'local payload = string.char(72, 105) .. string.char(bit32.bxor(75, 42))'
        result = deobfuscate_source(source)
        self.assertEqual(result.source, 'local payload = "Hia"')
        self.assertTrue(result.changed)

    def test_decodes_base64_and_table_concat(self) -> None:
        source = 'local payload = table.concat({"SG", "k="})'
        result = deobfuscate_source(source)
        self.assertEqual(result.source, 'local payload = "SGk="')
        decoded = deobfuscate_source('local payload = base64.decode("SGk=")')
        self.assertEqual(decoded.source, 'local payload = "Hi"')

    def test_handles_lua_string_sub_zero_and_negative_indices(self) -> None:
        zero_start = deobfuscate_source('local value = string.sub("abc", 0, 1)')
        negative_range = deobfuscate_source('local value = string.sub("abc", -2, -1)')
        self.assertEqual(zero_start.source, 'local value = "a"')
        self.assertEqual(negative_range.source, 'local value = "bc"')

    def test_handles_roblox_httpservice_base64_form_statically(self) -> None:
        source = 'local payload = game:GetService("HttpService"):Base64Decode("SGk=")'
        result = deobfuscate_source(source)
        self.assertEqual(result.source, 'local payload = "Hi"')

    def test_folds_arithmetic_without_touching_comments(self) -> None:
        source = '-- string.char(65)\nlocal n = 1 + 2 * 3'
        result = deobfuscate_source(source)
        self.assertEqual(result.source, '-- string.char(65)\nlocal n = 7')

    def test_canonicalizes_escaped_literals_and_preserves_unicode(self) -> None:
        result = deobfuscate_source('local text = "\\x41" .. " snowman: ☃"')
        self.assertEqual(result.source, 'local text = "A snowman: ☃"')

    def test_refuses_to_fold_table_identity_or_undefined_length(self) -> None:
        for source in (
            'local equal = {} == {}',
            'local length = #{nil, 1}',
        ):
            with self.subTest(source=source):
                self.assertEqual(deobfuscate_source(source).source, source)

    def test_refuses_to_fold_multi_return_string_byte_ranges(self) -> None:
        source = 'local first, second = string.byte("AB", 1, 2)'
        self.assertEqual(deobfuscate_source(source).source, source)

    def test_refuses_to_fold_dynamic_calls(self) -> None:
        source = 'local payload = decodeWithRuntime(key, blob)'
        result = deobfuscate_source(source)
        self.assertEqual(result.source, source)
        self.assertFalse(result.changed)

    def test_preserves_binary_operators_after_unknown_expressions(self) -> None:
        for source in (
            'local value = (secret + 7) * 2',
            'local value = secret - 7',
            'local value = secret ~ 7',
        ):
            with self.subTest(source=source):
                self.assertEqual(deobfuscate_source(source).source, source)

    def test_folds_unary_operators_with_lua_precedence(self) -> None:
        self.assertEqual(deobfuscate_source('local x = -7').source, 'local x = -7')
        self.assertEqual(deobfuscate_source('local x = ~7').source, 'local x = -8')
        self.assertEqual(deobfuscate_source('local x = not 1 == 2').source, 'local x = true')
        self.assertEqual(deobfuscate_source('local x = -2 ^ 2').source, 'local x = -4')

    def test_bounds_source_and_folded_string_sizes(self) -> None:
        with self.assertRaises(ValueError):
            deobfuscate_source(" " * (MAX_SOURCE_BYTES + 1))
        oversized = 'local value = string.rep("x", 40000)'
        self.assertEqual(deobfuscate_source(oversized).source, oversized)


if __name__ == "__main__":
    unittest.main()
