# Third-party notices

The Python devirtualizer and its offline Luau environment are adapted from
`imnotherfav/deobfuscator-luraph-v15`, commit
`5a1ac583b69451f56dd735d2a1de6ab7a513432b`. That repository declares the MIT
License; its license text is included in `LICENSE`. Protez changes the runtime
runner to use Protez's isolated Luau worker and uses the pinned Luau AST CLI.

The Luau runtime and AST parser are built from `luau-lang/luau` tag `0.740`,
also under the MIT License. The license text is included at
`third_party/luau-mit.txt` in the Protez source tree and in the packaged
application's `licenses` directory.
