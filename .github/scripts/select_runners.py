#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Filter the maintained runner list and build a matrix.

This script is the single source of truth for the fleet across workflows. It is invoked from:

* ``Restart Runners`` -- with filters (``--name``/``--os``/``--group``) to pick
  the subset of machines to reboot.
* ``Runner Heartbeat`` -- with no filters (``--os any --group any``) to emit the
  full fleet as a matrix.

It reads the static fleet definition in ``.github/runners.json`` and filters it down to the requested set.
When machines are added or removed, edit ``.github/runners.json`` ONLY -- both workflows pick up the change automatically.

``runners.json`` is a JSON array of objects, one per runner::
    [
      { "name": "xsj-aimlab-halo-0", "os": "Windows", "group": "halo" },
      ...
    ]

Filtering ANDs three optional criteria:
* ``--name``   exact runner name (e.g. ``xsj-aimlab-halo-0``). Restarts one box.
* ``--os``     ``Windows`` or ``Linux`` (or ``any``). Matched against ``os``.
* ``--group``  a hardware group (``halo``, ``stx``, ``krk``, ``r9700``,
               ``rx9070xt``, ``rx7900xt``) or ``any``. Matched against ``group``.

So ``--os Windows --group halo`` selects the Windows Ryzen AI Max machines,
``--group any --os any`` (the cron default) selects the whole fleet, and
``--name xsj-aimlab-krk-02`` targets a single machine.

The result is written to ``GITHUB_OUTPUT`` as ``matrix`` (a JSON array of
``{"runner": "<name>"}`` objects consumed by ``strategy.matrix.include``) and
``has_entries`` (``true``/``false``). It also prints a human-readable summary
to the step log.
"""

from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Optional


# Location of the maintained fleet list, relative to the repo root.
RUNNERS_FILE = Path(".github/runners.json")


def load_runners() -> list[dict]:
    """Load and lightly validate the maintained runner list."""
    if not RUNNERS_FILE.exists():
        sys.stderr.write(f"Runner list not found at {RUNNERS_FILE}.\n")
        sys.exit(1)
    try:
        data = json.loads(RUNNERS_FILE.read_text(encoding="utf-8"))
    except json.JSONDecodeError as e:
        sys.stderr.write(f"{RUNNERS_FILE} is not valid JSON: {e}\n")
        sys.exit(1)
    if not isinstance(data, list):
        sys.stderr.write(f"{RUNNERS_FILE} must contain a JSON array.\n")
        sys.exit(1)
    for i, entry in enumerate(data):
        if not isinstance(entry, dict) or "name" not in entry or "os" not in entry:
            sys.stderr.write(
                f"{RUNNERS_FILE} entry #{i} must be an object with at least "
                f"'name' and 'os' keys. Got: {entry!r}\n"
            )
            sys.exit(1)
    return data


def matches(
    runner: dict,
    name: Optional[str],
    os_filter: Optional[str],
    group: Optional[str],
) -> bool:
    """Return True if ``runner`` satisfies all active filters."""
    if name:
        if runner.get("name") != name:
            return False

    if os_filter and os_filter.lower() != "any":
        if str(runner.get("os", "")).lower() != os_filter.lower():
            return False

    if group and group.lower() != "any":
        if str(runner.get("group", "")).lower() != group.lower():
            return False

    return True


def main() -> int:
    parser = argparse.ArgumentParser(description="Build a runner restart matrix.")
    parser.add_argument("--name", default="", help="Exact runner name, or empty")
    parser.add_argument("--os", dest="os_filter", default="any", help="Windows|Linux|any")
    parser.add_argument("--group", default="any", help="Hardware group, or any")
    args = parser.parse_args()

    runners = load_runners()

    selected = [
        r
        for r in runners
        if matches(r, args.name.strip() or None, args.os_filter, args.group)
    ]

    # Human-readable summary in the step log.
    print(f"Loaded {len(runners)} runner(s) from {RUNNERS_FILE}.")
    print(
        f"Filters -> name={args.name or 'any'}, os={args.os_filter}, "
        f"group={args.group}"
    )
    if args.name.strip() and not selected:
        print(
            f"WARNING: no runner named '{args.name.strip()}' in "
            f"{RUNNERS_FILE}. Check spelling / update the list."
        )
    if selected:
        print("Will restart:")
        for r in selected:
            print(f"  - {r['name']} ({r.get('os')}, group={r.get('group', 'n/a')})")
    else:
        print("No runners matched the selection.")

    matrix = [{"runner": r["name"]} for r in selected]

    gh_out = os.environ.get("GITHUB_OUTPUT")
    if gh_out:
        with open(gh_out, "a", encoding="utf-8") as fh:
            fh.write(f"matrix={json.dumps(matrix)}\n")
            fh.write(f"has_entries={'true' if matrix else 'false'}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
