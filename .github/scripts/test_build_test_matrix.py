#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for test selection (build_test_matrix.py --mode changed).

The dangerous failure is a FALSE NEGATIVE: an entry whose behaviour changed but
which is not queued. These tests exist so a future change cannot silently
reintroduce one.

Two kinds of case:

  Real-commit replay
      Rebuild both sides of a real historical commit (base = c^, head = c) in a
      throwaway git repo and assert what selection does. The current harness is
      grafted onto BOTH sides, so the harness path check sees no change and the
      test exercises content selection rather than the harness rule.

  Synthetic mutation
      Build a fixture from the working tree, commit it as the base, mutate one
      thing, and assert exactly which entries are queued.

Nothing here touches the source repository: every case runs in a temp git repo.

Usage:
    python3 .github/scripts/test_build_test_matrix.py
    python3 .github/scripts/test_build_test_matrix.py --quick   # skip replay
"""

import argparse
import json
import re
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from typing import Optional

# Selection output is parsed from stdout, so keep workflow-command noise out of it
os.environ.pop("GITHUB_ACTIONS", None)

REPO_ROOT = Path(__file__).resolve().parents[2]
HARNESS = (
    ".github/scripts/run_playbook_tests.py",
    ".github/scripts/build_test_matrix.py",
    ".github/workflows/test-playbooks.yml",
)


def git(*args, cwd, check=True):
    return subprocess.run(
        ["git", *args], cwd=cwd, capture_output=True, text=True, check=check
    )


def make_repo(path: Path) -> None:
    path.mkdir(parents=True, exist_ok=True)
    git("init", "-q", cwd=path)
    git("config", "user.email", "ci@example.invalid", cwd=path)
    git("config", "user.name", "ci", cwd=path)
    git("config", "commit.gpgsign", "false", cwd=path)


def graft_harness(dest: Path) -> None:
    """Copy the working tree's harness into dest so both sides match byte-for-byte."""
    for rel in HARNESS:
        target = dest / rel
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(REPO_ROOT / rel, target)


def populate_from_rev(dest: Path, rev: str) -> None:
    """Extract playbooks/ from a revision of the source repo into dest."""
    for stale in (dest / "playbooks",):
        if stale.exists():
            shutil.rmtree(stale)
    archive = subprocess.run(
        ["git", "archive", "--format=tar", rev, "--", "playbooks"],
        cwd=REPO_ROOT, capture_output=True, check=True,
    )
    subprocess.run(["tar", "-x", "-C", str(dest)], input=archive.stdout, check=True)


def populate_from_worktree(dest: Path) -> None:
    shutil.copytree(REPO_ROOT / "playbooks", dest / "playbooks", symlinks=True)


def select(fixture: Path, base: str = "HEAD") -> list[dict]:
    """Run the fixture's own copy of the builder and return selected entries."""
    proc = subprocess.run(
        [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "changed", "--base", base],
        cwd=fixture, capture_output=True, text=True,
    )
    if proc.returncode != 0:
        raise AssertionError(f"builder failed: {proc.stderr[-1500:]}")
    return json.loads(proc.stdout)


def full_count(fixture: Path) -> int:
    proc = subprocess.run(
        [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "all"],
        cwd=fixture, capture_output=True, text=True, check=True,
    )
    return len(json.loads(proc.stdout))


class FixtureCase(unittest.TestCase):
    """Base fixture: working-tree playbooks + current harness, committed."""

    @classmethod
    def setUpClass(cls):
        cls._tmp = tempfile.TemporaryDirectory(prefix="matrix-fixture-")
        cls.fx = Path(cls._tmp.name) / "repo"
        make_repo(cls.fx)
        populate_from_worktree(cls.fx)
        graft_harness(cls.fx)
        git("add", "-A", cwd=cls.fx)  # safe: throwaway repo, not the source tree
        git("commit", "-qm", "base", cwd=cls.fx)
        cls.base_sha = git("rev-parse", "HEAD", cwd=cls.fx).stdout.strip()
        cls.total = full_count(cls.fx)

    @classmethod
    def tearDownClass(cls):
        cls._tmp.cleanup()

    def tearDown(self):
        # Tests that commit must not redefine the base for their successors.
        # Scoped to the throwaway fixture repo, never the source tree.
        git("reset", "-q", "--hard", self.base_sha, cwd=self.fx, check=False)
        git("clean", "-qfd", cwd=self.fx, check=False)

    # ---------------------------------------------------------------- helpers
    def edit(self, rel, transform):
        p = self.fx / rel
        p.write_text(transform(p.read_text(encoding="utf-8")), encoding="utf-8")

    def a_playbook_readme(self):
        return next((self.fx / "playbooks" / "core").glob("*/README.md"))

    # ------------------------------------------------------------------ tests
    def test_clean_tree_selects_nothing(self):
        self.assertEqual(select(self.fx), [])

    def test_selection_is_deterministic(self):
        run = lambda: subprocess.run(
            [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "all",
             "--github-output", os.devnull],
            cwd=self.fx, capture_output=True, text=True, check=True).stdout
        self.assertEqual(run(), run())

    def test_prose_edit_selects_nothing(self):
        readme = self.a_playbook_readme()
        self.edit(readme.relative_to(self.fx), lambda c: c.replace("\n\n", "\n\nA typo fix.\n\n", 1))
        self.assertEqual(select(self.fx), [])

    def test_harness_change_forces_full_matrix(self):
        self.edit(".github/workflows/test-playbooks.yml", lambda c: c + "\n# touched\n")
        self.assertEqual(len(select(self.fx)), self.total)

    def test_runner_change_forces_full_matrix(self):
        """The defect that motivated this design: editing the extractor must not cancel."""
        self.edit(".github/scripts/run_playbook_tests.py", lambda c: c + "\n# touched\n")
        self.assertEqual(len(select(self.fx)), self.total)

    def test_extractor_semantics_change_is_visible(self):
        """Removing dedup changes what executes; it must not cancel out."""
        self.edit(
            ".github/scripts/run_playbook_tests.py",
            lambda c: c.replace(
                "    for t in tests:\n        if t.id not in seen_ids:", "    for t in []:\n        if t.id not in seen_ids:"
            ),
        )
        self.assertEqual(len(select(self.fx)), self.total)

    def test_excluded_harness_file_does_not_force_full_matrix(self):
        path = self.fx / ".github/scripts/translate_playbook.py"
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text("# translation tooling\n")
        git("add", "-A", cwd=self.fx)
        git("commit", "-qm", "add translate", cwd=self.fx)
        path.write_text("# translation tooling, edited\n")
        self.assertEqual(select(self.fx), [])

    def test_unparseable_readme_is_selected_not_skipped(self):
        """A signature that cannot be computed must never read as 'unchanged'."""
        readme = self.a_playbook_readme()
        pb = readme.parent.name
        self.edit(readme.relative_to(self.fx), lambda c: c + "\n<!-- @var:id=x device=nope value=\"1\" -->\n"
                  "<!-- @test:id=broken-probe -->\n```bash\necho ${x}\n```\n<!-- @test:end -->\n")
        got = select(self.fx)
        self.assertTrue(got, "entries with an unresolvable @var must be queued")
        self.assertTrue(all(e["playbook"] == pb for e in got))

    def test_oversized_matrix_fails_loudly(self):
        """More than 256 jobs must fail in the builder, not at Actions expansion."""
        pj = next((self.fx / "playbooks" / "core").glob("*/playbook.json"))
        meta = json.loads(pj.read_text())
        meta["tested_platforms"] = {f"dev{i}": ["linux", "windows"] for i in range(200)}
        pj.write_text(json.dumps(meta, indent=2))
        proc = subprocess.run(
            [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "all",
             "--github-output", os.devnull],
            cwd=self.fx, capture_output=True, text=True,
        )
        self.assertNotEqual(proc.returncode, 0)
        self.assertIn("256", proc.stderr)

    def test_new_device_is_selected_even_though_signature_matches(self):
        pj = next((self.fx / "playbooks" / "core").glob("*/playbook.json"))
        meta = json.loads(pj.read_text())
        meta["tested_platforms"]["newdev"] = ["linux"]
        pj.write_text(json.dumps(meta, indent=2))
        got = select(self.fx)
        self.assertEqual([(e["platform"], e["arch"]) for e in got], [("linux", "newdev")])

    def test_required_flag_flip_is_selected(self):
        pj = next((self.fx / "playbooks" / "core").glob("*/playbook.json"))
        meta = json.loads(pj.read_text())
        dev, plats = next(iter(meta["tested_platforms"].items()))
        meta.setdefault("required_platforms", {})[dev] = [
            p for p in meta.get("required_platforms", {}).get(dev, []) if p != plats[0]
        ]
        pj.write_text(json.dumps(meta, indent=2))
        got = select(self.fx)
        self.assertEqual(len(got), 1)
        self.assertFalse(got[0]["required"])

    def test_annotations_never_pollute_stdout(self):
        """stdout carries the matrix JSON; workflow commands must go to stderr."""
        env = {**os.environ, "GITHUB_ACTIONS": "true"}
        # --mode changed always annotates, so this exercises a non-empty annotation path
        proc = subprocess.run(
            [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "changed",
             "--base", "HEAD", "--github-output", os.devnull],
            cwd=self.fx, capture_output=True, text=True, env=env, check=True,
        )
        self.assertIn("::", proc.stderr, "expected annotations on stderr")
        json.loads(proc.stdout)  # raises if an annotation leaked into stdout
        self.assertNotIn("::", proc.stdout)

    def test_corrupt_playbook_json_does_not_drop_entries(self):
        """A playbook.json that stops parsing must not silently lose its entries.

        The head expansion skips the corrupt playbook, but its entries still
        exist in base and the directory remains, so they are recovered and run.
        """
        pj = next((self.fx / "playbooks" / "core").glob("*/playbook.json"))
        pb = pj.parent.name
        n_entries = len(json.loads(subprocess.run(
            [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "playbook",
             "--playbook-id", pb, "--github-output", os.devnull],
            cwd=self.fx, capture_output=True, text=True, check=True).stdout))
        pj.write_text("{ this is not json")
        got = select(self.fx)
        self.assertEqual({e["playbook"] for e in got}, {pb})
        self.assertEqual(len(got), n_entries)

    def test_vanished_entry_is_queued_when_playbook_remains(self):
        """Dropping a device from tested_platforms must still run the lost entry."""
        pj = next((self.fx / "playbooks" / "core").glob("*/playbook.json"))
        meta = json.loads(pj.read_text())
        dev = sorted(meta["tested_platforms"])[0]
        lost = meta["tested_platforms"].pop(dev)
        pj.write_text(json.dumps(meta, indent=2))
        got = select(self.fx)
        self.assertEqual({e["arch"] for e in got}, {dev})
        self.assertEqual(len(got), len(lost))

    def test_escaping_assets_symlink_forces_a_run(self):
        """Content behind an escaping symlink is unsigned, so it cannot be skipped."""
        pb = next((self.fx / "playbooks" / "core").glob("*/assets")).parent
        outside = self.fx / "shared_lib.py"
        outside.write_text("v = 1\n")
        (pb / "assets" / "lib.py").symlink_to("../../../../shared_lib.py")
        git("add", "-A", cwd=self.fx)
        git("commit", "-qm", "add escaping symlink", cwd=self.fx)
        outside.write_text("v = 2\n")
        got = select(self.fx)
        self.assertTrue(any(e["playbook"] == pb.name for e in got))

    def test_pycache_lookalike_directory_is_signed(self):
        """The build-artefact skip must match the directory, not a substring."""
        d = self.fx / ".github/scripts/__pycache__helpers"
        d.mkdir(parents=True, exist_ok=True)
        (d / "helper.py").write_text("# v1\n")
        git("add", "-A", cwd=self.fx)
        git("commit", "-qm", "add helper", cwd=self.fx)
        (d / "helper.py").write_text("# v2\n")
        self.assertEqual(len(select(self.fx)), self.total)

    def test_shared_dependency_assets_are_signed(self):
        """@require inlines dependency markdown, so its assets are in scope."""
        probe = self.fx / "playbooks/dependencies/assets/probe.py"
        probe.parent.mkdir(parents=True, exist_ok=True)
        probe.write_text("# v1\n")
        git("add", "-A", cwd=self.fx)
        git("commit", "-qm", "add shared asset", cwd=self.fx)
        probe.write_text("# v2\n")
        self.assertEqual(len(select(self.fx)), self.total)

    def test_timeout_change_selects_that_entry(self):
        """Execution-governing @test fields (not just code) must be signed.

        Bumps every timeout in one README so at least one reachable block is hit,
        and picks the first README where the change actually reaches an entry
        (some blocks are dedup-shadowed or scoped to an unprovisioned device).
        """
        import re as _re
        # Rewrite the timeout attribute inside @test tags only, never code that
        # happens to contain "timeout=", so the change isolates the signed field.
        pat = _re.compile(r"(<!-- @test:[^>]*timeout=)(\d+)")
        touched = False
        for readme in (self.fx / "playbooks").rglob("*/README.md"):
            c = readme.read_text(errors="ignore")
            if pat.search(c):
                touched = True
                readme.write_text(pat.sub(r"\g<1>99\2", c))
        self.assertTrue(touched, "no @test timeout= attribute in the tree")
        # Bumping every timeout guarantees a reachable block is hit; if the
        # field were unsigned this would select nothing and the test would fail.
        self.assertTrue(select(self.fx), "timeout attribute is not signed")

    def test_output_contract(self):
        """The workflow reads these three keys; detection_ok gates the test-gate."""
        out = self.fx / "out.txt"
        subprocess.run(
            [sys.executable, ".github/scripts/build_test_matrix.py", "--mode", "all",
             "--github-output", str(out)],
            cwd=self.fx, capture_output=True, text=True, check=True,
        )
        keys = dict(line.split("=", 1) for line in out.read_text().splitlines() if "=" in line)
        self.assertEqual(set(keys) & {"matrix", "has_entries", "detection_ok"},
                         {"matrix", "has_entries", "detection_ok"})
        self.assertEqual(keys["has_entries"], "true")
        self.assertEqual(keys["detection_ok"], "true")
        json.loads(keys["matrix"])

    def test_asset_change_selects_that_playbook_only(self):
        assets = sorted((self.fx / "playbooks" / "core").glob("*/assets/*"))
        asset = next(a for a in assets if a.is_file())
        pb = asset.parent.parent.name
        asset.write_bytes(asset.read_bytes() + b"\n")
        got = select(self.fx)
        self.assertTrue(got)
        self.assertEqual({e["playbook"] for e in got}, {pb})

    def test_dependency_test_change_selects_all_consumers(self):
        dep = self.fx / "playbooks/dependencies/pytorch.md"
        if not dep.exists():
            self.skipTest("pytorch.md dependency not present")
        import re as _re
        dep.write_text(_re.sub(r"(<!-- @test:[^>]+ -->\s*```\w*\n)", r"\1echo probe\n",
                               dep.read_text(), count=1))
        got = select(self.fx)
        consumers = {
            p.parts[-2] for p in (self.fx / "playbooks").rglob("*/README.md")
            if _re.search(r"@require:[a-z0-9-,]*\bpytorch\b", p.read_text(errors="ignore"))
        }
        self.assertTrue(got)
        self.assertEqual({e["playbook"] for e in got}, consumers)


class UnreachableBaseCase(unittest.TestCase):
    def test_missing_base_falls_back_to_full(self):
        """An unresolvable base sha must run everything, not nothing."""
        with tempfile.TemporaryDirectory(prefix="matrix-nobase-") as tmp:
            fx = Path(tmp) / "repo"
            make_repo(fx)
            populate_from_worktree(fx)
            graft_harness(fx)
            git("add", "-A", cwd=fx)
            git("commit", "-qm", "base", cwd=fx)
            missing = "0" * 40  # not an object in this repo
            self.assertEqual(len(select(fx, base=missing)), full_count(fx))


REPLAY_LIMIT = 14  # bounded for CI runtime; skipped commits are reported, never silent


def classify_commit(commit: str) -> Optional[str]:
    """Independently predict selection for a commit, without running the builder.

    Returns "inert" if nothing that can affect execution changed (so selection
    must be empty), "active" if a @test region changed (so selection must be
    non-empty), or None if the commit is out of scope / ambiguous.

    Deliberately derived from the diff rather than from the manifest, so the
    test does not simply restate the implementation.
    """
    files = subprocess.run(
        ["git", "show", "--name-only", "--format=", commit],
        cwd=REPO_ROOT, capture_output=True, text=True,
    ).stdout.split()
    files = [f for f in files if f]
    if not files or any(not f.startswith("playbooks/") for f in files):
        return None  # harness/website commits are covered by dedicated tests
    if any("/assets/" in f or f.endswith("playbook.json") for f in files):
        return None  # legitimately affects execution; magnitude not predictable here
    if any(not f.endswith(".md") for f in files):
        return None

    def blocks_of(text):
        return [(m.start(), m.end()) for m in re.finditer(
            r"<!-- @test:[^>]+ -->.*?<!-- @test:end -->", text, re.S)]

    def line_starts(text):
        """Char offset of each 1-based line, so a line number maps to a position."""
        offsets, pos = [0], 0
        for ln in text.split("\n"):
            pos += len(ln) + 1
            offsets.append(pos)
        return offsets

    touched_test_region = False
    for path in files:
        after = subprocess.run(["git", "show", f"{commit}:{path}"],
                               cwd=REPO_ROOT, capture_output=True, text=True)
        before = subprocess.run(["git", "show", f"{commit}^:{path}"],
                                cwd=REPO_ROOT, capture_output=True, text=True)
        if after.returncode != 0 or before.returncode != 0:
            return None  # added/deleted/renamed; out of scope
        sides = {"+": (blocks_of(after.stdout), line_starts(after.stdout)),
                 "-": (blocks_of(before.stdout), line_starts(before.stdout))}
        # -U0 drops context lines, so every body line belongs to the hunk counters
        diff = subprocess.run(["git", "show", "-U0", commit, "--", path],
                              cwd=REPO_ROOT, capture_output=True, text=True).stdout
        old_no = new_no = 0
        for line in diff.splitlines():
            if line.startswith("@@"):
                m = re.match(r"@@ -(\d+)(?:,\d+)? \+(\d+)(?:,\d+)? @@", line)
                if not m:
                    return None
                old_no, new_no = int(m.group(1)), int(m.group(2))
                continue
            if not (old_no or new_no) or line.startswith(("+++", "---")):
                continue  # file header, before the first hunk
            sign = line[:1]
            if sign not in "+-":
                continue  # e.g. "\ No newline at end of file"
            body = line[1:].strip()
            lineno = new_no if sign == "+" else old_no
            if sign == "+":
                new_no += 1
            else:
                old_no += 1
            if not body:
                continue
            # A directive added OR removed restructures extraction in ways that
            # are not locally predictable (it may wrap tests, or nothing at all).
            # Refuse to guess: those cases are covered by synthetic mutations.
            if body.startswith("<!-- @"):
                return None
            blocks, starts = sides[sign]
            if lineno < 1 or lineno >= len(starts):
                return None  # cannot locate the line; do not guess
            # The exact changed line, not the first textual match of its content
            if any(s <= starts[lineno - 1] < e for s, e in blocks):
                touched_test_region = True
    return "active" if touched_test_region else "inert"


class ReplayCase(unittest.TestCase):
    """Replay real commits with the current harness grafted onto both sides."""

    def _replay(self, commit):
        with tempfile.TemporaryDirectory(prefix="matrix-replay-") as tmp:
            fx = Path(tmp) / "repo"
            make_repo(fx)
            populate_from_rev(fx, f"{commit}^")
            graft_harness(fx)
            git("add", "-A", cwd=fx)
            git("commit", "-qm", f"base {commit}^", cwd=fx)
            populate_from_rev(fx, commit)
            graft_harness(fx)
            return select(fx), full_count(fx)

    def test_replay_real_commits(self):
        log = subprocess.run(["git", "log", "--format=%h", "-60"],
                             cwd=REPO_ROOT, capture_output=True, text=True).stdout.split()
        cases, skipped = [], 0
        for c in log:
            kind = classify_commit(c)
            if kind is None:
                skipped += 1
                continue
            cases.append((c, kind))
            if len(cases) >= REPLAY_LIMIT:
                break
        print(f"\n    replaying {len(cases)} commits ({skipped} out of scope, "
              f"limit={REPLAY_LIMIT})")
        # Advisory only: how many recent commits are classifiable depends on repo
        # cadence, and a required check must not fail on unrelated history.
        if len(cases) < 4:
            print(f"    WARNING: only {len(cases)} replayable commits in the last "
                  f"{len(log)}; replay signal is weak this run")
        for commit, kind in cases:
            with self.subTest(commit=commit, kind=kind):
                got, total = self._replay(commit)
                n = len(got)
                subject = subprocess.run(["git", "log", "-1", "--format=%s", commit],
                                         cwd=REPO_ROOT, capture_output=True, text=True).stdout.strip()
                print(f"    {commit} [{kind:6s}] {n:3d}/{total}  {subject[:44]}")
                if kind == "inert":
                    self.assertEqual(n, 0, f"{commit} touches no test region but selected {n}")
                else:
                    self.assertGreater(n, 0, f"{commit} changed a test region but selected 0")
                    self.assertLess(n, total, f"{commit} should not force the full matrix")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--quick", action="store_true", help="skip real-commit replay")
    args, rest = ap.parse_known_args()
    loader = unittest.TestLoader()
    suite = unittest.TestSuite([loader.loadTestsFromTestCase(FixtureCase),
                                loader.loadTestsFromTestCase(UnreachableBaseCase)])
    if not args.quick:
        suite.addTests(loader.loadTestsFromTestCase(ReplayCase))
    sys.exit(0 if unittest.TextTestRunner(verbosity=2).run(suite).wasSuccessful() else 1)
