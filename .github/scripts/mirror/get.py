#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Put a mirrored artifact where a prerequisite's own download would put it.

Adapted from the Ryzen AI documentation mirror's get.py. Prereq install scripts
call this before falling back to their normal download. The internal Artifactory
mirror's base URL comes from the ARTIFACTORY_BASE secret; reads are anonymous, and
the URL is a secret only to keep the internal host out of public logs. Without the
secret (e.g. a fork PR), or when the mirror does not carry the artifact or the
transfer fails, the artifact comes from its upstream URL instead.

    get.py fetch <mirror path> --to <file> [--upstream]

Exits 0 iff <file> is in place afterwards, so a caller can chain a fallback.
Every download is checked against the SHA-256 pinned in artifacts.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

MANIFEST = Path(__file__).with_name("artifacts.json")
CURL = "curl.exe" if os.name == "nt" else "curl"
# Resilient transfer: the corporate link can stall a single connection, so turn a
# stall into a retry and resume from the byte it stopped at.
CURL_FETCH = [CURL, "-sSfL", "--retry", "30", "--retry-all-errors", "--retry-delay", "2",
              "--speed-limit", "102400", "--speed-time", "15", "-C", "-"]


def record(artifact: str, outcome: str) -> None:
    """Append what was asked for and what happened, so a run can prove it used the mirror."""
    path = os.environ.get("PLAYBOOKS_MIRROR_LEDGER")
    if path:
        with open(path, "a", encoding="utf-8") as fh:
            fh.write(json.dumps({"artifact": artifact, "outcome": outcome}) + "\n")


def load_manifest(path: Path) -> dict:
    return {a["dest"]: a for a in json.loads(path.read_text(encoding="utf-8"))}


def head_status(url: str) -> str:
    """HTTP status of a HEAD request; settles a 404 before curl would retry it 30 times."""
    r = subprocess.run([CURL, "-sSL", "-o", os.devnull, "--head", "-w", "%{http_code}", url],
                       capture_output=True, text=True)
    return r.stdout.strip()


def sha256_of(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def download(url: str, dest: Path, sha256: str) -> bool:
    """Fetch url to dest via a .part file; keep it only if it is whole and matches sha256."""
    part = dest.with_name(dest.name + ".part")
    part.unlink(missing_ok=True)
    dest.parent.mkdir(parents=True, exist_ok=True)
    if subprocess.run(CURL_FETCH + ["-o", str(part), url]).returncode != 0:
        part.unlink(missing_ok=True)
        return False
    if sha256 and sha256_of(part) != sha256:
        print(f"checksum mismatch for {dest.name}; discarding it")
        part.unlink(missing_ok=True)
        return False
    part.replace(dest)
    return True


def cmd_fetch(args) -> int:
    dest = Path(args.to)
    if dest.exists():
        record(args.path, "present")
        print(f"{dest} is already in place")
        return 0
    entry = load_manifest(Path(args.manifest)).get(args.path, {})
    sha256 = entry.get("sha256", "")

    base = os.environ.get("ARTIFACTORY_BASE", "").rstrip("/")
    if not base:
        record(args.path, "no-secret")
        print("ARTIFACTORY_BASE is not set, so the mirror is unreachable")
    else:
        url = f"{base}/{args.path}"
        status = head_status(url)
        if status != "200":
            record(args.path, "absent")
            print(f"{args.path} is not on the mirror (HTTP {status})")
        elif download(url, dest, sha256):
            record(args.path, "downloaded")
            print(f"{dest.name} came from the internal mirror")
            return 0
        else:
            record(args.path, "failed")
            print(f"fetching {args.path} from the mirror failed")

    if args.upstream and entry.get("url"):
        print(f"falling back to upstream for {dest.name}")
        if download(entry["url"], dest, sha256):
            record(args.path, "upstream")
            return 0
        print(f"upstream download of {dest.name} failed")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=str(MANIFEST), help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd", required=True)
    fetch = sub.add_parser("fetch", help="put one mirrored file in place")
    fetch.add_argument("path", help="path in the mirror, as artifacts.json lists it under dest")
    fetch.add_argument("--to", required=True, help="where the file should end up")
    fetch.add_argument("--upstream", action="store_true",
                       help="when the mirror cannot serve it, download the artifacts.json url")
    fetch.set_defaults(func=cmd_fetch)
    args = parser.parse_args()
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
