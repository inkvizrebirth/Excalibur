# samples/

Real-world WeAreDevs builds used by the regression tests.

They are **third-party files and are not committed**; fetch them with

```
python tools/fetch_samples.py
```

which verifies the recorded sha1 and stores them in `samples/real/`:

| file | bytes | sha1 | source repository |
|---|---|---|---|
| `wrd_aspect.lua` | 17,312 | `67f8d8cd` | `neosnappp/aspect-dumper-full-fixed` (`aspect/core/io/obfuscated.lua`) |
| `wrd_fog.lua` | 18,955 | `dd27a885` | `mknhghv/bf` (`fog.lua`) |
| `wrd_ka.lua` | 32,336 | `d6b1c7d4` | `SleepyCattStar/CattStarTemp` (`ka.lua`) |

The tests skip themselves when the folder is empty, so a checkout without
network access still runs the full unit suite and the acceptance fixture pair.

What these files are: WRD v1.0.0 output whose payload is interpreted by the
obfuscator's own state machine (no `loadstring`), which is why the pipeline
reports them as *partial*. See `docs/REAL_WORLD_NOTES.md`.
