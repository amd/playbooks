# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Summarize a Translate Playbooks diff into a human-readable PR body section.

Reads the list of changed file paths (one per line) on stdin — the output of
`git diff --name-only` restricted to `auto-translations/` — and prints a markdown
summary of WHAT changed: how many locales, how many prose files (README /
platform.md) vs title/description files (playbook.json) vs rescored-only
manifests, and which playbooks were touched.

This exists because the auto-opened translation PR previously carried a bland
one-line body; the reviewer had to open hundreds of files to see what a run
actually did. The classification here is pure path parsing on the diff.

Usage:
    git diff --name-only <base>...HEAD -- auto-translations \\
        | python .github/scripts/summarize_translation_diff.py
"""

import sys

PROSE_FILES = {"README.md", "platform.md"}


def summarize(paths: list[str]) -> str:
    locales: set[str] = set()
    prose: set[str] = set()          # "<locale>/<playbook-or-dep>/<file>"
    titles: set[str] = set()         # playbook.json (title/description)
    manifest_locales: set[str] = set()
    content_locales: set[str] = set()  # locales with a real prose/title/dep change
    playbooks: set[str] = set()
    deps_touched = False
    other = 0

    for raw in paths:
        p = raw.strip()
        if not p or not p.startswith("auto-translations/"):
            continue
        rel = p[len("auto-translations/"):]
        parts = rel.split("/")
        # Top-level, non-locale files like _quality_report.json/.md.
        if parts[0].startswith("_"):
            continue
        locale = parts[0]
        locales.add(locale)
        base = parts[-1]

        if base == "translation_accuracy.json":
            manifest_locales.add(locale)
            continue
        content_locales.add(locale)
        # <locale>/dependencies/<file>
        if len(parts) >= 2 and parts[1] == "dependencies":
            deps_touched = True
            if base in PROSE_FILES:
                prose.add(rel)
            continue
        # <locale>/<category>/<playbook>/<file>
        if len(parts) >= 4 and parts[1] in ("core", "supplemental"):
            playbooks.add(parts[2])
            if base in PROSE_FILES:
                prose.add(rel)
            elif base == "playbook.json":
                titles.add(rel)
            else:
                other += 1
            continue
        other += 1

    lines = ["### What changed", ""]
    if locales:
        shown = ", ".join(sorted(locales))
        lines.append(f"- **Locales:** {len(locales)} ({shown})")
    if prose:
        lines.append(f"- **Prose (README / platform.md):** {len(prose)} file(s)")
    else:
        lines.append("- **Prose (README / platform.md):** none")
    if titles:
        lines.append(
            f"- **Titles & descriptions (playbook.json):** {len(titles)} file(s)"
        )
    if deps_touched:
        lines.append("- **Shared dependency content:** updated")
    # Locales whose manifest changed but had no prose/title/dep change: a pure
    # quality re-score (e.g. a judge-model bump), not a content change.
    rescore_only = manifest_locales - content_locales
    if rescore_only:
        lines.append(
            f"- **Quality re-score only (no content change):** {len(rescore_only)} locale(s)"
        )
    if other:
        lines.append(f"- **Other files:** {other}")

    if playbooks:
        lines += [
            "",
            f"### Playbooks touched ({len(playbooks)})",
            "",
            ", ".join(sorted(playbooks)),
        ]
    return "\n".join(lines)


def main() -> int:
    print(summarize(sys.stdin.read().splitlines()))
    return 0


if __name__ == "__main__":
    sys.exit(main())
