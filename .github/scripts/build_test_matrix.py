#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Test Matrix Builder
===================

Builds the CI test matrix for test-playbooks.yml.

Modes:
    --mode all                              every entry (nightly cron)
    --mode playbook --playbook-id <id>      one playbook (workflow_dispatch)
    --mode changed --base <sha>             only entries whose tests changed (pull_request)

How --mode changed works:
    1. Materialise the base revision (git archive) into a temp tree.
    2. Harness check: if any file that governs how tests execute differs between
       base and head, run the FULL matrix. This is deny-by-default over
       .github/scripts/ and test-playbooks.yml, minus HARNESS_EXCLUDED.
    3. Otherwise the extractor is identical on both sides, so compute a per-entry
       signature with THIS checkout's extractor against each tree and diff them.
       An entry runs if it is new, its matrix identity changed, its signature
       changed, or either signature could not be computed.

    Applying one extractor to both trees is only safe because step 2 already
    forced the full matrix on any extractor change; that is what prevents a
    semantic change from cancelling out. Every failure to establish a trustworthy
    base (missing sha, archive error) falls back to the full matrix.
"""

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
import run_playbook_tests as R  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
ARCHIVE_TIMEOUT = 120

# GitHub Actions refuses a matrix above 256 jobs; fail here with a clear message
# rather than at workflow-expansion time
MATRIX_JOB_LIMIT = 256

# Files that govern how tests execute. Deny-by-default: anything added under
# these prefixes is covered without anyone remembering. Editing any of them
# forces the full matrix, so signatures never have to model harness behaviour.
HARNESS_PREFIXES = (".github/scripts/", ".github/workflows/test-playbooks.yml")

# Files under those prefixes that provably cannot change a playbook test verdict.
# Omitting one only costs a needless full run; wrongly adding one hides a real
# change, so each entry is justified by test-playbooks.yml not depending on it.
HARNESS_EXCLUDED = frozenset({
    ".github/scripts/translate_playbook.py",       # translation tooling
    ".github/scripts/disclaimers.json",            # translation tooling
    ".github/scripts/glossary.json",               # translation tooling
    ".github/scripts/check_copyright.py",          # check-copyright.yml
    ".github/scripts/validate_playbooks.py",       # validate-playbooks.yml
    ".github/scripts/fetch_github_issues.py",      # fetch-github-issues.yml
    ".github/scripts/select_runners.py",           # not referenced by test-playbooks.yml
    ".github/scripts/create_failure_issues.py",    # if: failure() on main, post-verdict
    ".github/scripts/test_build_test_matrix.py",   # separate selector-tests job
    ".github/scripts/gen_issue_template_playbooks.py",  # validate-playbooks.yml
    ".github/scripts/orchestrai_matrix.py",        # OrchestrAI workflows
    ".github/scripts/orchestrai_report.py",        # OrchestrAI workflows
    ".github/scripts/orchestrai_trigger.py",       # OrchestrAI workflows
    ".github/scripts/orchestrai_verdict.py",       # OrchestrAI workflows
})

def annotate(level: str, message: str) -> None:
    """Report on stderr only; stdout is reserved for the matrix JSON."""
    prefix = f"::{level}::" if os.environ.get("GITHUB_ACTIONS") else ""
    print(f"{prefix}{message}", file=sys.stderr)


def harness_files(root: Path) -> dict[str, bytes]:
    """Map relpath -> content hash for every execution-governing file in root."""
    out: dict[str, bytes] = {}
    for prefix in HARNESS_PREFIXES:
        target = root / prefix
        paths = []
        if target.is_dir():
            paths = [p for p in target.rglob("*") if p.is_file()]
        elif target.is_file():
            paths = [target]
        for path in paths:
            rel = str(path.relative_to(root)).replace(os.sep, "/")
            if "__pycache__" in path.relative_to(root).parts or rel.endswith(".pyc"):
                continue
            if rel in HARNESS_EXCLUDED:
                continue
            mode = b"\x01" if os.access(path, os.X_OK) else b"\x00"
            content = path.read_bytes().replace(b"\r\n", b"\n")
            out[rel] = mode + hashlib.sha256(content).digest()
    return out


def harness_changed(base_tree: Path) -> bool:
    return harness_files(REPO_ROOT) != harness_files(base_tree)


def materialise_base(base: str, dest: Path, include_localized: bool = False) -> bool:
    """Extract the base revision's playbooks and .github into dest."""
    try:
        paths = ["playbooks", ".github"]
        if include_localized:
            paths.append("localized-playbooks")
        archive = subprocess.run(
            ["git", "archive", "--format=tar", base, "--", *paths],
            cwd=REPO_ROOT, capture_output=True, check=True,
            stdin=subprocess.DEVNULL, timeout=ARCHIVE_TIMEOUT,
        )
    except subprocess.TimeoutExpired:
        annotate("warning", f"git archive {base} timed out after {ARCHIVE_TIMEOUT}s")
        return False
    except subprocess.CalledProcessError as exc:
        annotate("warning", f"git archive {base} failed: {exc.stderr.decode()[:200]}")
        return False
    try:
        with tarfile.open(fileobj=io.BytesIO(archive.stdout)) as tar:
            tar.extractall(dest, filter="data")
    except Exception as exc:
        annotate("warning", f"cannot extract base {base}: {type(exc).__name__}: {exc}")
        return False
    return True


def select_changed(base_tree: Path) -> list[dict]:
    """Entries not provably unchanged between base_tree and this checkout."""
    head = R.build_matrix_entries(REPO_ROOT)
    if harness_changed(base_tree):
        annotate("notice", "Test harness changed; running the full matrix")
        return head

    base_keys = {
        (e["playbook"], e["platform"], e["arch"]): e
        for e in R.build_matrix_entries(base_tree)
    }
    selected, skipped = [], 0
    for entry in head:
        key = (entry["playbook"], entry["platform"], entry["arch"])
        label = f"{key[0]} ({key[1]}/{key[2]})"
        prior = base_keys.get(key)
        if prior is None:
            annotate("notice", f"New matrix entry {label}")
        elif prior != entry:
            annotate("notice", f"Matrix metadata changed for {label}")
        else:
            head_sig = R.entry_signature(REPO_ROOT, *key)
            base_sig = R.entry_signature(base_tree, *key)
            if head_sig is None or base_sig is None:
                annotate("warning", f"Cannot prove {label} unchanged; running it")
            elif head_sig != base_sig:
                annotate("notice", f"Tests changed for {label}")
            else:
                skipped += 1
                continue
        selected.append(entry)

    # An entry that vanished while its playbook still exists is still runnable
    head_keys = {(e["playbook"], e["platform"], e["arch"]) for e in head}
    live = set(R.list_playbook_ids(REPO_ROOT))
    for key, prior in base_keys.items():
        if key not in head_keys and key[0] in live:
            annotate("warning", f"Entry vanished from {key[0]} ({key[1]}/{key[2]}) "
                                "but the playbook still exists; running it")
            selected.append(prior)

    annotate("notice", f"Selected {len(selected)} entries; skipped {skipped} unchanged")
    return selected


def tree_digest(path: Path) -> str:
    """Hash a localized content subtree for conservative change detection."""
    if not path.is_dir():
        return ""
    digest = hashlib.sha256()
    for child in sorted(p for p in path.rglob("*") if p.is_file()):
        digest.update(str(child.relative_to(path)).replace(os.sep, "/").encode())
        digest.update(hashlib.sha256(child.read_bytes()).digest())
    return digest.hexdigest()


def select_localized_changed(base_tree: Path, locale: str, head: list[dict]) -> list[dict]:
    """Select localized entries whose overlay, metadata, or dependencies changed."""
    if harness_changed(base_tree):
        annotate("notice", "Test harness changed; running the full localized matrix")
        return head

    head_dependencies = REPO_ROOT / "localized-playbooks" / locale / "dependencies"
    base_dependencies = base_tree / "localized-playbooks" / locale / "dependencies"
    if tree_digest(head_dependencies) != tree_digest(base_dependencies):
        annotate("notice", "Localized dependencies changed; running the full matrix")
        return head

    english_dependencies_changed = tree_digest(
        REPO_ROOT / "playbooks" / "dependencies"
    ) != tree_digest(base_tree / "playbooks" / "dependencies")

    try:
        base_entries = R.build_localized_matrix_entries(base_tree, locale)
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        annotate("warning", f"Cannot expand localized base metadata: {exc}; running all")
        return head

    base_by_key = {
        (e["playbook"], e["platform"], e["arch"]): e for e in base_entries
    }
    selected = []
    for entry in head:
        key = (entry["playbook"], entry["platform"], entry["arch"])
        prior = base_by_key.get(key)
        changed = prior != entry
        for category in ("core", "supplemental"):
            rel = Path("localized-playbooks") / locale / category / entry["playbook"]
            if tree_digest(REPO_ROOT / rel) != tree_digest(base_tree / rel):
                changed = True
                break
            if not entry.get("localized_only", True):
                english_rel = Path("playbooks") / category / entry["playbook"]
                if tree_digest(REPO_ROOT / english_rel) != tree_digest(
                    base_tree / english_rel
                ):
                    changed = True
                    break
        if not entry.get("localized_only", True) and english_dependencies_changed:
            changed = True
        if changed:
            selected.append(entry)
    annotate(
        "notice",
        f"Selected {len(selected)} localized entries; skipped {len(head) - len(selected)} unchanged",
    )
    return selected


def main() -> None:
    parser = argparse.ArgumentParser(description="Build the playbook CI test matrix")
    parser.add_argument("--mode", required=True, choices=["all", "playbook", "changed"])
    parser.add_argument("--playbook-id", help="Playbook id for --mode playbook")
    parser.add_argument("--base", help="Base revision for --mode changed")
    parser.add_argument(
        "--locale",
        default="",
        help="Build the matrix for this localized-playbooks locale instead of English",
    )
    parser.add_argument("--github-output", type=Path)
    parser.add_argument(
        "--allow-empty",
        action="store_true",
        help="Return an empty matrix instead of failing when a filter matches nothing",
    )
    args = parser.parse_args()

    try:
        entries = (
            R.build_localized_matrix_entries(REPO_ROOT, args.locale)
            if args.locale
            else R.build_matrix_entries(REPO_ROOT)
        )
    except (OSError, ValueError, json.JSONDecodeError) as exc:
        print(f"FATAL: cannot build test matrix: {exc}", file=sys.stderr)
        sys.exit(1)
    if not entries and not args.allow_empty:
        print("FATAL: this checkout lists no matrix entries", file=sys.stderr)
        sys.exit(1)

    if args.mode == "playbook":
        if not args.playbook_id:
            parser.error("--mode playbook requires --playbook-id")
        entries = [e for e in entries if e["playbook"] == args.playbook_id]
        if not entries and not args.allow_empty:
            print(f"FATAL: no matrix entries for playbook '{args.playbook_id}'", file=sys.stderr)
            sys.exit(1)
    elif args.mode == "changed":
        if not args.base:
            parser.error("--mode changed requires --base")
        with tempfile.TemporaryDirectory(prefix="base-tree-") as tmp:
            base_tree = Path(tmp)
            if materialise_base(args.base, base_tree, include_localized=bool(args.locale)):
                entries = (
                    select_localized_changed(base_tree, args.locale, entries)
                    if args.locale
                    else select_changed(base_tree)
                )
            else:
                annotate("warning", f"No trustworthy base {args.base}; running the full matrix")

    # Fail here rather than let Actions reject the oversized matrix with a vague error
    if len(entries) > MATRIX_JOB_LIMIT:
        print(f"FATAL: {len(entries)} entries exceeds the GitHub Actions matrix cap "
              f"of {MATRIX_JOB_LIMIT}; split the workflow", file=sys.stderr)
        sys.exit(1)

    matrix = json.dumps(entries)
    output_path = args.github_output or (
        Path(os.environ["GITHUB_OUTPUT"]) if os.environ.get("GITHUB_OUTPUT") else None
    )
    if output_path:
        with output_path.open("a", encoding="utf-8") as handle:
            handle.write(f"matrix={matrix}\n")
            handle.write(f"has_entries={'true' if entries else 'false'}\n")
            handle.write("detection_ok=true\n")
    print(matrix)


if __name__ == "__main__":
    main()
