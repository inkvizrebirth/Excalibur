"""Excalibur — universal deobfuscator for WeAreDevs (and friends) Lua scripts.

Package layout
--------------
``core``    detection, static decoding, sandboxed execution, validation
``gui``     monochrome ttkbootstrap/Tk interface
``tools``   build helpers, sample generators, runtime fetching

The public entry point of the library is :func:`core.deobfuscate.deobfuscate`.
"""

from __future__ import annotations

__all__ = ["__version__"]

__version__ = "1.0.0"
