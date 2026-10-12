"""Exception hierarchy used across Excalibur."""

from __future__ import annotations


class ExcaliburError(Exception):
    """Base class for all Excalibur failures."""


class RuntimeUnavailable(ExcaliburError):
    """No usable Lua runtime could be found or started."""


class CompileError(ExcaliburError):
    """The obfuscated (or candidate) source could not be compiled by any runtime."""


class DetectionError(ExcaliburError):
    """Format detection failed in an unexpected way."""


class SandboxError(ExcaliburError):
    """The sandbox could not run the script (I/O, timeouts, engine failure)."""


class ValidationError(ExcaliburError):
    """A candidate payload did not pass validation."""
