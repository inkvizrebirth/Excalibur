from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))


def main() -> int:
    from core.version import VERSION
    parser = argparse.ArgumentParser(description="Write integrity metadata for the Protez installer")
    parser.add_argument("executable", type=Path)
    parser.add_argument("destination", type=Path)
    args = parser.parse_args()

    digest = hashlib.sha256()
    size = 0
    with args.executable.open("rb") as source:
        for block in iter(lambda: source.read(1024 * 1024), b""):
            digest.update(block)
            size += len(block)
    manifest = {"version": VERSION, "size_bytes": size, "sha256": digest.hexdigest()}
    args.destination.parent.mkdir(parents=True, exist_ok=True)
    args.destination.write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
