# logs/

Runtime artefacts live here (git-ignored). Each run creates

```
run_<timestamp>_<source-hash>/
    input.lua            the exact bytes that were analysed
    decoded.lua          static layer: pool decoded, resolver inlined, constants folded
    output.lua           recovered source (written only when a payload validated)
    report.json          stages, candidates, validation checks, notes (machine readable)
    summary.txt          the same, human readable
    trace_summary.txt    visited dispatch states when the trace fallback ran
    <runtime>_<policy>/  one directory per sandbox attempt
        input.lua  report.json  hook_log.txt
        dump_NNN.lua        chunks passed to load/loadstring
        concat_NNN.txt      results of table.concat calls
        char_fragments.txt  string.char fragments
        trace.txt           raw dispatch trace
```

`gui.log` collects GUI-level errors. Nothing here is required for a run to
succeed - delete the directory whenever you like.
