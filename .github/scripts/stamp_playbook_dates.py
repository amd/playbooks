# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Stamp published_date into playbook.json from git history.

Run by the playbook-metadata workflow after a push to main. For every reachable
playbook (core + supplemental), published_date is set ONCE, to the first commit
that added the playbook directory, if the field is missing or empty. It is never
overwritten afterward, so the publication date is stable even as the playbook is
edited.

There is deliberately no "last updated" counterpart. One used to be refreshed on
every commit touching the directory, which meant a repo-wide sweep — or the
metadata bot's own commit — re-dated every playbook at once and advertised a
freshness none of them had earned. The honest freshness signal on this site is
"last validated", which comes from CI actually running the playbook on hardware.

Dates are YYYY-MM-DD (author date). Authors are hand-maintained metadata and are
never touched here. Requires a full-history checkout (fetch-depth: 0).

Usage:
    python .github/scripts/stamp_playbook_dates.py            # rewrite in place
    python .github/scripts/stamp_playbook_dates.py --check    # fail if stale
"""

import argparse
import json
import subprocess
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLAYBOOKS_ROOT = REPO_ROOT / "playbooks"
CATEGORIES = ["core", "supplemental"]


def _git_date(args: list[str]) -> str:
    """Return the YYYY-MM-DD author date from a git log invocation, or ''."""
    out = subprocess.run(
        ["git", "log", *args],
        cwd=REPO_ROOT, capture_output=True, text=True, encoding="utf-8",
    ).stdout.strip().splitlines()
    return out[-1][:10] if out else ""


def first_commit_date(rel_dir: str) -> str:
    # --diff-filter=A: the commit that ADDED the dir; last line = earliest.
    return _git_date(["--diff-filter=A", "--format=%aI", "--", rel_dir])


def stamp(meta_path: Path) -> bool:
    """Stamp published_date in one playbook.json. Returns True if it changed."""
    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    if meta.get("published_date"):
        return False  # immutable once set

    rel_dir = meta_path.parent.relative_to(REPO_ROOT).as_posix()
    published = first_commit_date(rel_dir)
    if not published:
        return False  # no history (untracked / added in this same commit)

    meta["published_date"] = published
    meta_path.write_text(
        json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8", newline="\n",
    )
    return True


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if any file would change, without writing.")
    args = parser.parse_args()

    metas = []
    for category in CATEGORIES:
        metas.extend(sorted((PLAYBOOKS_ROOT / category).glob("*/playbook.json")))

    stale = []
    for meta_path in metas:
        rel = meta_path.relative_to(REPO_ROOT).as_posix()
        if args.check:
            # dry-run: detect change without persisting
            before = meta_path.read_text(encoding="utf-8")
            if stamp(meta_path):
                stale.append(rel)
                meta_path.write_text(before, encoding="utf-8", newline="\n")  # restore
        else:
            if stamp(meta_path):
                print(f"stamped {rel}")

    if args.check and stale:
        print("ERROR: playbook dates are stale; run stamp_playbook_dates.py:")
        for s in stale:
            print(f"  {s}")
        return 1
    if not args.check:
        print(f"Done. Checked {len(metas)} playbooks.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
