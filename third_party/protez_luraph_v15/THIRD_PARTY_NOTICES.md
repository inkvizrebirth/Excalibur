# Third-party notices

The Python devirtualizer (the shared lifter back end plus the Luraph v14 and
v15 front ends) and its offline Luau environment are adapted from
`caomod2077/Deobfuscator-Luraph-V15` (formerly `imnotherfav/deobfuscator-luraph-v15`),
commit `5a1ac583b69451f56dd735d2a1de6ab7a513432b`. That repository declares the
MIT License; its license text is included in `LICENSE`. Protez changes the
runtime runner to use Protez's isolated Luau worker, uses the pinned Luau AST
CLI for every front end and pass that spawns a parser, and drives the payload
root selection for captured v14 prototype graphs itself (the runtime capture
reports the anti-tamper prototype first). Protez also adds the v14 front end's
whole-namespace lift (`obfuscators/luraph_v14/devirt.py: lift_program_all`):
upstream lifts the single ranked root of each VM, which for a v14 container
reaches only the program's main chunk and drops every sibling function, so
Protez walks and labels every prototype of the namespace and reports the ones
it skips (anti-tamper shapes, unsupported layouts, failed walks).

The Luau runtime and AST parser are built from `luau-lang/luau` tag `0.740`,
also under the MIT License. The license text is included at
`third_party/luau-mit.txt` in the Protez source tree and in the packaged
application's `licenses` directory.
