"""Runtime configuration.

Everything that the GUI or CLI may want to tune lives here so that the core
modules stay free of globals and remain testable.
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional

from . import paths

#: Environment policies tried by the sandbox, best first.
DEFAULT_POLICIES: tuple[str, ...] = ("codex", "strict", "permissive")

#: Preferred Lua runtimes, best fidelity first.
#: WRD targets Lua 5.1 semantics, so 5.1/LuaJIT come first; Lua 5.4 is last
#: because it is the only *PUC* Lua that can compile the multi-hundred-kilobyte
#: obfuscated one-liners produced by WRD (see docs/REAL_WORLD_NOTES.md).
DEFAULT_RUNTIMES: tuple[str, ...] = ("lua51", "luajit21", "lua54")


@dataclass
class SandboxConfig:
    """Knobs for a single sandboxed execution."""

    timeout: float = 30.0
    """Wall-clock budget *inside* Lua, enforced by an instruction-count hook."""

    max_instructions: int = 400_000_000
    """Hard instruction budget; guards against scripts without clock progress."""

    policies: tuple[str, ...] = DEFAULT_POLICIES
    runtimes: tuple[str, ...] = DEFAULT_RUNTIMES
    allow_unsafe: bool = False
    """When True the sandbox exposes real io/os/require (never for untrusted input)."""

    deterministic_random: bool = True
    random_seed: int = 123456789
    keep_artifacts: bool = True
    """Keep the per-attempt artefact directories in ``logs/``."""

    max_attempts: int = 6
    """Cap on (runtime, policy) pairs tried by the ladder.  WRD v1.0.0 needs the
    first two or three attempts, so a small cap keeps a failed run bounded."""

    workdir: Optional[Path] = None
    sample_runs: int = 1
    """How many policies to try.  ``1`` = first policy only (fastest)."""

    def resolved_workdir(self) -> Path:
        return paths.ensure_dir(self.workdir or paths.logs_dir())


@dataclass
class PipelineConfig:
    """Knobs for the whole deobfuscation pipeline (see :mod:`core.deobfuscate`)."""

    sandbox: SandboxConfig = field(default_factory=SandboxConfig)
    prefer_static: bool = True
    """Try the static string-layer decoder first (fast, deterministic)."""

    run_dynamic: bool = True
    """Run the script in the Lua sandbox to capture runtime-built payloads."""

    trace_on_failure: bool = True
    """Instrument dispatch loops and re-run when nothing else produced a payload."""

    min_payload_chars: int = 80
    """Candidates shorter than this are ignored."""

    extra_roblox_source: Optional[str] = None
    """Optional path with extra Lua stubs injected into the sandbox."""

    def resolved_workdir(self) -> Path:
        return self.sandbox.resolved_workdir()


def default_logs_dir() -> Path:
    override = os.environ.get("EXCALIBUR_LOGS")
    return Path(override) if override else paths.logs_dir()


__all__ = [
    "DEFAULT_POLICIES",
    "DEFAULT_RUNTIMES",
    "PipelineConfig",
    "SandboxConfig",
    "default_logs_dir",
]
