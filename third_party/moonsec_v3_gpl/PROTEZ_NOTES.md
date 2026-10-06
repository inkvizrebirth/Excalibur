# Protez integration notes

This separate command-line helper is adapted from
`tupsutumppu/MoonsecDeobfuscator`, commit
`2afe5d8a97333433de33b99efe0f9d420f7b9e6f`, under the included GPL-3.0
license. It maps MoonSec V3 VM handlers back to standard Lua 5.1 bytecode.
Protez invokes it as a separate process and keeps this component's license
and source separate from the main application.

The NLua dependency and runtime evaluation of key expressions were removed.
The helper evaluates numeric expressions and a small whitelist of pure
`math` calls from the parsed AST. Unsupported calls fail with a diagnostic;
the input script is never executed to obtain a key. Bytecode counts, string
lengths, and prototype nesting are bounded before allocation or recursion.

The resulting standard Lua 5.1 chunk is passed to the separate MIT-licensed
`unluac-rs` CLI. Its source recovery is approximate: comments and original
local names are unavailable in the VM bytecode, and Protez validates only
that generated output parses as Luau. It does not claim semantic equivalence.
