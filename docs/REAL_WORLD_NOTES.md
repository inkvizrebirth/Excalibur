# Real-world notes: WeAreDevs v1.0.0

Everything below was measured on real files, not inferred. Sample hashes are in
`tools/fetch_samples.py` (the files themselves are third-party and are fetched,
never committed).

| sample | bytes | sha1 | pool | alphabet | shuffles | resolver |
|---|---|---|---|---|---|---|
| `wrd_aspect.lua` | 17,312 | `67f8d8cd` | 45 | 64 chars | 1-45, 1-15, 16-45 | `h(x) = j[x - 63015]` |
| `wrd_fog.lua` | 18,955 | `dd27a885` | 54 | 64 chars | 1-54, 1-8, 9-54 | `x(k) = j[k - 36336]` |
| `wrd_ka.lua` | 32,336 | `d6b1c7d4` | 116 | 64 chars | 1-116, 1-82, 83-116 | `n(v) = j[v + 51631]` |
| petrix hub | 2,168,191 | - | 10,084 | 64 chars | 1-10084, 1-9671, 9672-10084 | `g(x) = j[x - 42384]` |

All of them carry the banner `--[[ v1.0.0 https://wearedevs.net/obfuscator ]]`.

## File shape

```
--[[ v1.0.0 https://wearedevs.net/obfuscator ]]
return(function(...)
  local u = { "\068\052\075\106...", ... }      -- escaped-decimal string pool
  local a = { ["0"]=0, ["1"]=1, ... }           -- the custom base64 alphabet
  local j = {}                                   -- decoded entries, unshuffled
  local function h(x) return j[x - <offset>] end -- the pool resolver
  ...                                            -- decoders + anti-tamper checks
  while <state> do ... end                       -- the dispatch loop
end)(...)
```

## Facts that matter when implementing

* **The pool is escaped decimals** (`"\068\052..."`), four or more `\ddd`
  escapes per literal; that pattern is the single most reliable static signal.
* **Base64 uses a custom alphabet**: the 64 characters are stored in a
  `{char = value}` table in the file, so a standard base64 table will not decode
  it. `core.wrd_static.decode_custom_base64` takes the table.
* **The decoded entries are shuffled.** The shuffle table is applied in three
  ranges (`{{1, N}, {1, M}, {M+1, N}}`), applied in order; the second range
  overlaps the first on purpose. Applying only the first range decodes the first
  ~95 % correctly and silently corrupts the tail - a trap worth remembering.
* **Indices are offset**, e.g. `h(63015)` is entry 0, so the resolver offset must
  be subtracted (or added) before indexing. `analyze()` records the exact
  expression it used.
* **Decoded pool contents are the script's vocabulary**: library names
  (`setmetatable`, `tonumber`, `unpack`, `pcall`, `concat`, `floor`, `byte`,
  `gmatch`, `char`, `len`, `random`, `gsub`, `remove`, `print`), metamethods
  (`__len`, `__gc`, `__index`, `__metatable`), string constants (`":"`,
  `"(%d*):"`, `"Tamper Detected!"`) and randomised identifiers
  (`4AU4rzT4DNdDKo`, `mB4H5dFS6IaS`, ...) that appear verbatim in the code.
* **Environment reads use those randomised names**: running a sample under a
  logging stub showed exactly the pool entries being read as globals
  (`4AU4rzT4DNdDKo` x19, then one read each of four more), i.e. the payload's
  globals were renamed to pool entries. Every missed global is a pool entry -
  that is a useful invariant for future tracer work.
* **`loadstring` is never called in these builds.** Instrumenting `load` and
  `loadstring` across four wild samples and every policy/runtime combination
  produced `loads = 0`. The payload is not rebuilt as text; it is interpreted by
  the obfuscator's own state machine. This is why a `loadstring` hook alone is
  not enough, and why the pipeline reports those files as *partial*.
* **`string.char` is used heavily** (399 calls for the 17 KB sample, 410 for the
  generated fixture) to assemble strings one character at a time; the captured
  fragments are what `char_fragments.txt` records.
* **Tracing works**: injecting a state logger into the dispatch loop recorded
  3,339 / 4,066 / 4,862 distinct states for the three samples, with a clear
  transition structure - the raw material for a devirtualiser.

## Runtime behaviour

* **Lua 5.1 is the faithful target** (Roblox-era semantics: `tostring(1.0)` is
  `"1"`, floor modulo, no integer subtype). `lupa.lua51` runs all three small
  samples.
* **Large files need Lua 5.4**: the 2 MB sample fails to compile under PUC 5.1,
  5.2, 5.3 and LuaJIT (`control structure too long near 'end'`) and only
  compiles under 5.4. The sandbox therefore tries runtimes in order and records
  which one rejected the input and why.
* Lua 5.4 changes observable behaviour for these scripts: the same sample that
  calls `string.char` 399 times under 5.1 calls it 143 times under 5.4 - the
  numeric formatting differences change the decoded strings. Prefer 5.1 for
  semantics, use 5.4 to get past the compiler limit.
* A trivial 2 MB run consumes the whole instruction budget without ever calling
  `loadstring`, which is the expected outcome for a flattened script.

## The static rewrite is behaviour preserving

For all three small samples, running the *original* and the *rewritten* source
under the same stub produced identical results:

```
aspect  original: ran=True instr=800000 chars=399 reads=23 misses=5
        decoded : ran=True instr=800000 chars=399 reads=23 misses=5   (identical)
fog     original: ran=True instr=1200000 chars=432 reads=76  misses=6
        decoded : ran=True instr=1200000 chars=432 reads=76  misses=6   (identical)
```

This is asserted by `tests/test_pipeline.py::RealSamples`, so a regression in the
folder/decoder fails the suite.

## Traps that cost time

* **Folding across a binding boundary.** `H and-459339+1691705` must fold to
  `H and 1232366`, never to `(H and -459339)+1691705`. Complete parenthesised
  groups are atomic; a right neighbour in `*/%^` refuses the fold unless atomic.
* **Signature detection vs the comment mask.** The WRD banner lives in a
  comment, so a comment-stripping mask hides it. `mask_strings()` blanks string
  literals but keeps comments; the banner is matched against *that* mask so a
  URL inside a plain string cannot forge a signature.
* **A pool literal escaping pass** (writing every byte as `\ddd`) keeps the
  generated file pure ASCII, which makes byte-exact round trips independent of
  the surrounding tooling's encoding choices.
* **Multi-pass folding must not re-match stale text.** Stages take text and
  return `(count, new_text)`; the pipeline chains them instead of applying
  patches to a buffer that was rendered earlier.
* **`analyze()` returns `output = None` when `ok = False`**, so callers must
  read `reason` before touching the text.
