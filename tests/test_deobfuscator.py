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

    def test_propagates_immutable_constants_and_decoder_aliases(self) -> None:
        source = 'local code = 65; local chr = string.char; local value = chr(code); return value'
        result = deobfuscate_source(source)
        self.assertEqual(
            result.source,
            'local code = 65; local chr = string.char; local value = "A"; return "A"',
        )
        self.assertTrue(any("immutable local/API propagation" in item for item in result.transformations))

    def test_propagation_respects_writes_shadowing_and_lexical_scopes(self) -> None:
        reassigned = 'local value = 1; value = 2; return value'
        shadowed = 'local value = 1; do local value = 2; print(value) end; return value'
        scoped = 'do local value = 1; print(value) end; return value'
        self.assertEqual(deobfuscate_source(reassigned).source, reassigned)
        self.assertEqual(deobfuscate_source(shadowed).source, shadowed)
        self.assertEqual(
            deobfuscate_source(scoped).source,
            'do local value = 1; print(1) end; return value',
        )

    def test_folds_read_only_numeric_and_keyed_tables(self) -> None:
        source = 'local bytes = {[1] = 72, [2] = 105}; return string.char(bytes[1], bytes[2])'
        self.assertEqual(deobfuscate_source(source).source, 'local bytes = {[1] = 72, [2] = 105}; return "Hi"')
        table_concat = 'local values = {"H", "i"}; return table.concat(values)'
        self.assertEqual(deobfuscate_source(table_concat).source, 'local values = {"H", "i"}; return "Hi"')
        fields = 'local record = {message = "ready"}; return record.message'
        self.assertEqual(deobfuscate_source(fields).source, 'local record = {message = "ready"}; return "ready"')

    def test_expands_multi_return_byte_and_unpack_only_in_final_call_argument(self) -> None:
        byte_range = 'local value = string.char(string.byte("OK", 1, 2))'
        self.assertEqual(deobfuscate_source(byte_range).source, 'local value = "OK"')
        unpack = 'local bytes = {79, 75}; local value = string.char(table.unpack(bytes))'
        self.assertEqual(
            deobfuscate_source(unpack).source,
            'local bytes = {79, 75}; local value = "OK"',
        )
        multiple = 'local first, second = string.byte("OK", 1, 2)'
        self.assertEqual(deobfuscate_source(multiple).source, multiple)

    def test_decodes_more_local_encodings_and_math(self) -> None:
        base64 = 'local decode = crypt.base64decode; local value = decode("SGk")'
        self.assertEqual(deobfuscate_source(base64).source, 'local decode = crypt.base64decode; local value = "Hi"')
        formatted = 'local value = string.format("%02X-%s", 65, "A")'
        self.assertEqual(deobfuscate_source(formatted).source, 'local value = "41-A"')
        bitwise = 'local value = bit32.bxor(65, 1)'
        self.assertEqual(deobfuscate_source(bitwise).source, 'local value = 64')
        numeric = 'local value = math.floor(math.pi * 2)'
        self.assertEqual(deobfuscate_source(numeric).source, 'local value = 6')

    def test_folds_constant_short_circuit_without_evaluating_dead_branch(self) -> None:
        source = 'local no = false and dynamic(); local yes = true or dynamic()'
        self.assertEqual(deobfuscate_source(source).source, 'local no = false; local yes = true')

    def test_preserves_call_parentheses_when_propagating_arguments(self) -> None:
        source = 'local value = 7; print(value); return (value)'
        self.assertEqual(deobfuscate_source(source).source, 'local value = 7; print(7); return (7)')

    def test_does_not_propagate_through_luau_if_expressions(self) -> None:
        source = 'local value = if flag then 1 else 2; return value'
        self.assertEqual(deobfuscate_source(source).source, source)


if __name__ == "__main__":
    unittest.main()
