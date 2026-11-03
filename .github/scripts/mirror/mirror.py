#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Keep the internal Artifactory mirror in step with artifacts.json.

Adapted from the Ryzen AI documentation mirror's mirror.py (its push and check).
A maintainer runs this, never CI. Reads are anonymous; push also needs an
Artifactory identity token in ARTIFACTORY_TOKEN. The mirror's base URL comes from
ARTIFACTORY_BASE, as for get.py.

    mirror.py check [--group G] [--upstream]
    mirror.py push [--group G] [--dest PATH]

check compares each pinned file with the mirror, and with Hugging Face when asked.
push uploads the entries the mirror lacks. A file Artifactory already stores under
another path is linked by checksum, with no transfer; anything else is downloaded from
its url, checked against its pinned SHA-256, and deployed with that checksum so
Artifactory checks it again. A file already on the mirror is never replaced.
"""
from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import tempfile
import urllib.error
import urllib.request
from pathlib import Path

from get import CURL, MANIFEST, download, load_manifest

BASE = os.environ.get("ARTIFACTORY_BASE", "").rstrip("/")
# Downloads are staged here one file at a time, then removed once deployed.
STAGING = Path(os.environ.get("MIRROR_STAGING", Path(tempfile.gettempdir()) / "playbooks-mirror"))


def mask(text: str) -> str:
    """Keep the internal host out of anything printed."""
    return text.replace(BASE, "$ARTIFACTORY_BASE") if BASE else text


def remote_sha256(dest: str) -> str | None:
    """SHA-256 Artifactory records for dest, or None when the mirror lacks it."""
    server, repo = BASE.split("/artifactory/", 1)
    url = f"{server}/artifactory/api/storage/{repo}/{dest}"
    try:
        with urllib.request.urlopen(url, timeout=60) as resp:
            return json.load(resp).get("checksums", {}).get("sha256", "")
    except urllib.error.HTTPError as exc:
        if exc.code == 404:
            return None
        raise


def upstream_sha256(url: str) -> str | None:
    """SHA-256 Hugging Face reports today for a resolve URL's LFS file, without downloading it."""
    if "huggingface.co/" not in url:
        return None
    # Pins download from a fixed commit; drift is a question about the current main.
    url = re.sub(r"/resolve/[0-9a-f]{40}/", "/resolve/main/", url)
    r = subprocess.run([CURL, "-sSI", "--connect-timeout", "10", url], capture_output=True, text=True)
    m = re.search(r'^x-linked-etag:\s*"?([0-9a-f]{64})"?', r.stdout, re.I | re.M)
    return m.group(1) if m else None


def selected(args) -> list:
    entries = load_manifest(Path(args.manifest)).values()
    return [e for e in entries if (not args.group or e.get("group") == args.group)
            and (not getattr(args, "dest", None) or e["dest"] == args.dest)]


def cmd_check(args) -> int:
    problems = 0
    for e in selected(args):
        have = remote_sha256(e["dest"])
        state = "missing" if have is None else "ok" if have == e["sha256"] else "DIFFERENT"
        if args.upstream and e.get("url"):
            up = upstream_sha256(e["url"])
            if up and up != e["sha256"]:
                state += ", upstream changed"
        problems += state != "ok"
        print(f"{state:28} {e['dest']}")
    return 1 if problems else 0


def deploy(path: Path | None, dest: str, sha256: str, token: str) -> bool:
    """PUT a file; Artifactory rejects it unless it matches the declared SHA-256.

    Without a path, deploy by checksum: Artifactory links dest to a binary it already
    stores under another path, so nothing is transferred.
    """
    body = ["-T", str(path)] if path else ["-X", "PUT", "-H", "X-Checksum-Deploy: true"]
    r = subprocess.run([CURL, "-sS", "-o", os.devnull, "-w", "%{http_code}", *body,
                        "-H", f"X-Checksum-Sha256: {sha256}", "-H", "@-", f"{BASE}/{dest}"],
                       input=f"Authorization: Bearer {token}\n", capture_output=True, text=True)
    if not r.stdout.startswith("2"):
        if path:
            print(f"deploying {dest} failed: HTTP {r.stdout} {mask(r.stderr.strip())}")
        return False
    return True


def cmd_push(args) -> int:
    token = os.environ.get("ARTIFACTORY_TOKEN", "")
    if not token:
        print("push needs an Artifactory identity token in ARTIFACTORY_TOKEN")
        return 1
    failed = 0
    for e in selected(args):
        have = remote_sha256(e["dest"])
        if have is not None:
            print(f"{'already there' if have == e['sha256'] else 'left as is (different file)'}: {e['dest']}")
            continue
        if deploy(None, e["dest"], e["sha256"], token) and remote_sha256(e["dest"]) == e["sha256"]:
            print(f"linked to the copy the mirror already stores: {e['dest']}", flush=True)
            continue
        staged = STAGING / e["dest"]
        print(f"downloading {e['dest']} ({e['size'] / 2**30:.1f} GiB)", flush=True)
        if not download(e["url"], staged, e["sha256"]):
            print(f"could not get a verified copy of {e['dest']}")
            failed += 1
            continue
        if deploy(staged, e["dest"], e["sha256"], token) and remote_sha256(e["dest"]) == e["sha256"]:
            staged.unlink()
            print(f"pushed: {e['dest']}", flush=True)
        else:
            print(f"NOT pushed, kept {staged} for a retry: {e['dest']}", flush=True)
            failed += 1
    return 1 if failed else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--manifest", default=str(MANIFEST), help=argparse.SUPPRESS)
    sub = parser.add_subparsers(dest="cmd", required=True)
    check = sub.add_parser("check", help="compare the pinned files with the mirror")
    check.add_argument("--group", help="only this artifacts.json group")
    check.add_argument("--upstream", action="store_true", help="also compare with Hugging Face")
    check.set_defaults(func=cmd_check)
    push = sub.add_parser("push", help="upload the pinned files the mirror lacks")
    push.add_argument("--group", help="only this artifacts.json group")
    push.add_argument("--dest", help="only this mirror path")
    push.set_defaults(func=cmd_push)
    args = parser.parse_args()
    if not BASE:
        print("ARTIFACTORY_BASE is not set")
        return 1
    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
