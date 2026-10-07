# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Stamp published_date / updated_date into playbook.json from git history.

Run by the stamp-playbook-dates workflow after a push to main. For every
reachable playbook (core + supplemental):

* published_date: set ONCE, to the first commit that added the playbook
  directory, if the field is missing or empty. Never overwritten afterward, so
  the publication date is stable even as the playbook is edited.
* updated_date: always refreshed to the most recent commit touching the
  playbook directory.

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


def latest_commit_date(rel_dir: str) -> str:
    return _git_date(["-1", "--format=%aI", "--", rel_dir])


def stamp(meta_path: Path) -> bool:
    """Update dates in one playbook.json. Returns True if the file changed."""
    rel_dir = meta_path.parent.relative_to(REPO_ROOT).as_posix()
    published = first_commit_date(rel_dir)
    updated = latest_commit_date(rel_dir)
    if not published and not updated:
        return False  # no history (untracked / new in this same commit)

    meta = json.loads(meta_path.read_text(encoding="utf-8"))
    changed = False

    # Set published_date only if missing/empty; then it is immutable.
    if not meta.get("published_date") and published:
        meta["published_date"] = published
        changed = True

    # Always refresh updated_date to the latest commit.
    if updated and meta.get("updated_date") != updated:
        meta["updated_date"] = updated
        changed = True

    if changed:
        meta_path.write_text(
            json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8", newline="\n",
        )
    return changed


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
