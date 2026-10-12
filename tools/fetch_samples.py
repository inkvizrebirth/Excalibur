"""Fetch the real-world samples used by the regression tests.

The repo ships one generated fixture pair (``tests/wrd_v1_0_0*.lua``).  Real
WeAreDevs builds are third-party files, so they are *not* committed: this script
downloads them from their public repositories, verifies the sha1 and stores them
under ``samples/real/`` (git-ignored).  The regression tests use them when they
are present and skip otherwise.

    python tools/fetch_samples.py            # fetch what is missing
    python tools/fetch_samples.py --list     # show the manifest
    python tools/fetch_samples.py --force    # re-download everything
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.request
from pathlib import Path
from typing import Dict, List, Sequence

ROOT = Path(__file__).resolve().parent.parent
TARGET = ROOT / "samples" / "real"

#: url + sha1 for every sample the tests know about.
SAMPLES: List[Dict[str, str]] = [
    {
        "name": "wrd_aspect.lua",
        "url": "https://raw.githubusercontent.com/neosnappp/aspect-dumper-full-fixed/main/aspect/core/io/obfuscated.lua",
        "api": "https://api.github.com/repos/neosnappp/aspect-dumper-full-fixed/contents/aspect/core/io/obfuscated.lua",
        "sha1": "67f8d8cd11b47b8399dbd3936388ce2c9fbd3efc",
        "bytes": "17312",
        "note": "17 KB hub script, one dispatch loop, pool of 45 entries",
    },
    {
        "name": "wrd_fog.lua",
        "url": "https://raw.githubusercontent.com/mknhghv/bf/main/fog.lua",
        "api": "https://api.github.com/repos/mknhghv/bf/contents/fog.lua",
        "sha1": "dd27a885004e86eaaf859ec5adc5757cde4af6ce",
        "bytes": "18955",
        "note": "19 KB, pool of 54 entries, binary string constants",
    },
    {
        "name": "wrd_ka.lua",
        "url": "https://raw.githubusercontent.com/SleepyCattStar/CattStarTemp/main/ka.lua",
        "api": "https://api.github.com/repos/SleepyCattStar/CattStarTemp/contents/ka.lua",
        "sha1": "d6b1c7d47540cd94460302463949c718b54208ae",
        "bytes": "32336",
        "note": "32 KB, pool of 116 entries, three dispatch loops",
    },
]


def sha1(data: bytes) -> str:
    return hashlib.sha1(data).hexdigest()


def _download(url: str, timeout: int) -> bytes:
    request = urllib.request.Request(
        url,
        headers={
            "User-Agent": "Excalibur/1.0 sample fetcher",
            # the contents API returns the raw file when asked for it
            "Accept": "application/vnd.github.raw, text/plain, */*",
        },
    )
    with urllib.request.urlopen(request, timeout=timeout) as response:
        return response.read()


def fetch(sample: Dict[str, str], *, force: bool = False, timeout: int = 60) -> Path:
    TARGET.mkdir(parents=True, exist_ok=True)
    target = TARGET / sample["name"]
    if target.exists() and not force:
        data = target.read_bytes()
        expected = sample.get("sha1") or ""
        if not expected or sha1(data)[:8] == expected[:8]:
            print(f"have   {sample['name']} ({len(data):,} bytes)")
            return target
        print(f"stale  {sample['name']} - re-downloading")
    data = b""
    errors = []
    for url in [sample["url"], sample.get("api", "")]:
        if not url:
            continue
        try:
            data = _download(url, timeout)
            break
        except Exception as exc:  # try the next mirror
            errors.append(f"{url}: {exc}")
    if not data:
        print(f"failed {sample['name']}: " + " | ".join(errors))
        raise SystemExit(1)
    target.write_bytes(data)
    digest = sha1(data)
    expected = sample.get("sha1") or ""
    status = "ok" if (not expected or digest[:8] == expected[:8]) else "SHA1 MISMATCH"
    print(f"fetched {sample['name']} ({len(data):,} bytes, sha1 {digest[:12]}) {status}")
    if expected and digest[:8] != expected[:8]:
        raise SystemExit(f"{sample['name']} does not match the recorded sha1")
    return target


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="fetch the real-world WRD samples")
    parser.add_argument("--force", action="store_true", help="re-download even when present")
    parser.add_argument("--list", action="store_true", help="print the manifest and exit")
    args = parser.parse_args(argv)

    if args.list:
        print(json.dumps(SAMPLES, indent=2))
        return 0
    for sample in SAMPLES:
        fetch(sample, force=args.force)
    print(f"\nsamples are in {TARGET.relative_to(ROOT)} (git-ignored)")
    print("the regression tests pick them up automatically on the next run")
    return 0


if __name__ == "__main__":
    sys.exit(main())
