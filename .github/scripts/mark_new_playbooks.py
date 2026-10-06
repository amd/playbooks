# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Mark the most-recently-published playbooks as "New".

Keeps the website's "What's New" section bounded: exactly the NEW_COUNT most
recently published playbooks get isNew=true, everything else gets isNew=false.
Run by the playbook-metadata workflow after dates are stamped, so a just-merged
playbook (which may not have a published_date yet) is still ranked newest.

Ranking (newest first):
* A missing/empty published_date is treated as newest — a playbook that was just
  merged but not yet date-stamped is, by definition, the newest thing.
* Then by published_date descending, tie-broken by updated_date then id so the
  set is deterministic.

Only published (published=true) core/supplemental playbooks are considered;
unpublished drafts never take a "New" slot. Authors/dates are not touched here.

Usage:
    python .github/scripts/mark_new_playbooks.py            # rewrite in place
    python .github/scripts/mark_new_playbooks.py --check    # fail if stale
"""

import argparse
import json
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent.parent
PLAYBOOKS_ROOT = REPO_ROOT / "playbooks"
CATEGORIES = ["core", "supplemental"]

# How many playbooks are shown as "New" at once. The website's What's New grid is
# 3-wide; never surface more than this.
NEW_COUNT = 3

# Sorts ahead of any real YYYY-MM-DD date, so a not-yet-stamped playbook ranks newest.
_NEWEST = "9999-99-99"


def _rank_key(meta: dict) -> tuple:
    pub = meta.get("published_date") or _NEWEST
    upd = meta.get("updated_date") or _NEWEST
    return (pub, upd, meta.get("id", ""))


def compute(metas: list[tuple[Path, dict]]) -> set[str]:
    """Return the set of playbook ids that should be isNew=true."""
    published = [(p, m) for (p, m) in metas if m.get("published")]
    published.sort(key=lambda pm: _rank_key(pm[1]), reverse=True)
    return {m.get("id") for (_p, m) in published[:NEW_COUNT]}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true",
                        help="Exit non-zero if any isNew flag is stale, without writing.")
    args = parser.parse_args()

    metas: list[tuple[Path, dict]] = []
    for category in CATEGORIES:
        for meta_path in sorted((PLAYBOOKS_ROOT / category).glob("*/playbook.json")):
            metas.append((meta_path, json.loads(meta_path.read_text(encoding="utf-8"))))

    new_ids = compute(metas)

    stale = []
    for meta_path, meta in metas:
        desired = meta.get("id") in new_ids
        if bool(meta.get("isNew")) == desired:
            continue
        rel = meta_path.relative_to(REPO_ROOT).as_posix()
        stale.append(rel)
        if not args.check:
            meta["isNew"] = desired
            meta_path.write_text(
                json.dumps(meta, indent=2, ensure_ascii=False) + "\n",
                encoding="utf-8", newline="\n",
            )
            print(f"{'set' if desired else 'cleared'} isNew: {rel}")

    if args.check and stale:
        print("ERROR: isNew flags are stale; run mark_new_playbooks.py:")
        for s in stale:
            print(f"  {s}")
        return 1
    if not args.check:
        print(f"Done. New playbooks ({len(new_ids)}): {', '.join(sorted(new_ids))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
