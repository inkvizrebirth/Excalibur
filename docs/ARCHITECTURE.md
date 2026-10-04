# Internal architecture

- `main.py` checks/install prerequisites before loading the CustomTkinter GUI.
- The GUI sends work to `core.pipeline` on a worker thread; log and progress events return through queues.
- `core.sandbox` runs the official Luau CLI in a separate process with a timeout and bounded output. `sandbox/envlog.luau` supplies mock Roblox globals and captures `loadstring`/`load` payloads through stdout markers.
- HTTP, filesystem APIs and scheduled tasks are disabled in the mock. A subprocess is not an OS security boundary; use a disposable account or VM for untrusted input.
- The MVP fast path verifies captured source with `luau-compile` and copies valid Luau to `output/`. VM tracing, lifting and structured code generation are not implemented yet.
