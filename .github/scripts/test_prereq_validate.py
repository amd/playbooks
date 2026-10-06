#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for prereq_validate.py.

Covers:
- @require scoping across @os:/@device: blocks (including the @os:end vs
  @os:<name> parsing hazard that would otherwise swallow requires after an
  end tag).
- The validate -> install -> re-validate loop's five outcomes: OK, INSTALLED,
  FAILED, MISSING_NO_INSTALL, unchecked.
"""

import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "prereq_validate", Path(__file__).with_name("prereq_validate.py")
)
pv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pv)

# Mirrors the shape of n8n-automation-gpt-oss: an @os-scoped require, a
# device-scoped model declared with the CI-only @prereq tag, and tags that
# follow an @os:end tag. The prose line is deliberately included: it must not
# be parsed as a dependency.
FIXTURE = """\
<!-- @require = dependency docs rendered on the website; @prereq = CI-only -->
<!-- @device:rx7900xt,rx9070xt,r9700 -->
<!-- @require:driver -->
<!-- @device:end -->

<!-- @os:windows -->
<!-- @require:lemonade,nodejs -->
<!-- @os:end -->

<!-- @os:linux -->
<!-- @require:lemonade,podman -->
<!-- @os:end -->

<!-- @device:halo,halo_box -->
<!-- @prereq:lemonade-models-gpt-oss-120b -->
<!-- @device:end -->
"""

# The regex the website uses to find @require tags (route.ts). @prereq must be
# invisible to it, otherwise this PR would change rendered output.
WEBSITE_REQUIRE_RE = re.compile(r"<!-- @require:([a-z0-9,-]+) -->")


class ScopingTests(unittest.TestCase):
    def test_linux_halo_includes_model_after_os_end(self):
        # The model require sits after an @os:end tag; it must not be swallowed.
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "halo")
        self.assertEqual(deps, ["lemonade", "podman", "lemonade-models-gpt-oss-120b"])

    def test_windows_halo_uses_windows_os_block(self):
        deps = pv.extract_scoped_requires(FIXTURE, "windows", "halo")
        self.assertEqual(deps, ["lemonade", "nodejs", "lemonade-models-gpt-oss-120b"])

    def test_non_halo_device_excludes_model(self):
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "stx")
        self.assertNotIn("lemonade-models-gpt-oss-120b", deps)
        self.assertIn("podman", deps)

    def test_driver_only_for_its_devices(self):
        self.assertIn("driver", pv.extract_scoped_requires(FIXTURE, "linux", "r9700"))
        self.assertNotIn("driver", pv.extract_scoped_requires(FIXTURE, "linux", "halo"))


class PrereqTagTests(unittest.TestCase):
    """@prereq must behave exactly like @require for validation purposes while
    staying invisible to the website."""

    def test_prereq_deps_are_collected(self):
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "halo")
        self.assertIn("lemonade-models-gpt-oss-120b", deps)

    def test_prereq_respects_device_scope(self):
        # Same device scoping rules as @require: stx is not in @device:halo,halo_box.
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "stx")
        self.assertNotIn("lemonade-models-gpt-oss-120b", deps)

    def test_prereq_respects_os_scope(self):
        content = (
            "<!-- @os:windows -->\n"
            "<!-- @prereq:winonly -->\n"
            "<!-- @os:end -->\n"
        )
        self.assertIn("winonly", pv.extract_scoped_requires(content, "windows", None))
        self.assertNotIn("winonly", pv.extract_scoped_requires(content, "linux", None))

    def test_require_and_prereq_are_unioned(self):
        content = "<!-- @require:a -->\n<!-- @prereq:b -->\n"
        self.assertEqual(pv.extract_scoped_requires(content, "linux", None), ["a", "b"])

    def test_explanatory_comment_is_not_parsed_as_a_dependency(self):
        # The prose line in FIXTURE mentions both tag names without a colon;
        # it must not contribute a bogus dep id.
        deps = pv.extract_scoped_requires(FIXTURE, "linux", "halo")
        self.assertEqual(deps, ["lemonade", "podman", "lemonade-models-gpt-oss-120b"])

    def test_prereq_is_invisible_to_the_website_require_regex(self):
        # This is the guarantee that keeps rendered output identical to main.
        self.assertEqual(WEBSITE_REQUIRE_RE.findall("<!-- @prereq:some-dep -->"), [])
        self.assertEqual(
            WEBSITE_REQUIRE_RE.findall(FIXTURE),
            ["driver", "lemonade,nodejs", "lemonade,podman"],
        )


class LoopTests(unittest.TestCase):
    def test_ok_when_validate_passes(self):
        spec = {"validate": {"linux": {"cmd": "true", "expect_rc": 0}}}
        r = pv.check_dependency("d", spec, "linux")
        self.assertEqual(r["status"], "OK")
        self.assertFalse(r["install_ran"])

    def test_installed_when_install_heals(self):
        # Use a private temp dir and a not-yet-created path inside it, so the
        # first validate fails and the install `touch` is what makes it pass.
        with tempfile.TemporaryDirectory() as tmp:
            flag = os.path.join(tmp, "heal-flag")
            spec = {
                "validate": {"linux": {"cmd": f"test -f {flag}", "expect_rc": 0}},
                "install": {"linux": {"cmd": f"touch {flag}", "timeout": 5}},
            }
            r = pv.check_dependency("d", spec, "linux")
            self.assertEqual(r["status"], "INSTALLED")
            self.assertTrue(r["install_ran"])

    def test_failed_when_install_does_not_heal(self):
        spec = {
            "validate": {"linux": {"cmd": "false", "expect_rc": 0}},
            "install": {"linux": {"cmd": "true", "timeout": 5}},
        }
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "FAILED")

    def test_missing_no_install(self):
        spec = {"validate": {"linux": {"cmd": "false", "expect_rc": 0}}}
        self.assertEqual(
            pv.check_dependency("d", spec, "linux")["status"], "MISSING_NO_INSTALL"
        )

    def test_optional_miss_warns_not_fails(self):
        # An optional dep whose validate fails and has no install must not be a
        # hard failure (status not in the unresolved set).
        spec = {"optional": True, "validate": {"linux": {"cmd": "false", "expect_rc": 0}}}
        self.assertEqual(
            pv.check_dependency("d", spec, "linux")["status"], "MISSING_OPTIONAL"
        )

    def test_unchecked_when_no_validate_for_platform(self):
        spec = {"validate": {"windows": {"cmd": "true", "expect_rc": 0}}}
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "unchecked")


class ScriptStepTests(unittest.TestCase):
    """A step may name a script under prereqs/ instead of an inline cmd."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self._saved = pv.PREREQ_SCRIPTS_DIR
        pv.PREREQ_SCRIPTS_DIR = Path(self._tmp.name)

    def tearDown(self):
        pv.PREREQ_SCRIPTS_DIR = self._saved
        self._tmp.cleanup()

    def _script(self, name, body):
        (Path(self._tmp.name) / name).write_text(body, encoding="utf-8")

    def test_script_validate_ok(self):
        self._script("d.validate.sh", "exit 0\n")
        spec = {"validate": {"linux": {"script": "d.validate.sh", "expect_rc": 0}}}
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "OK")

    def test_script_install_heals(self):
        flag = Path(self._tmp.name) / "installed"
        self._script("d.validate.sh", f'test -f "{flag}"\n')
        self._script("d.install.sh", f'touch "{flag}"\n')
        spec = {
            "validate": {"linux": {"script": "d.validate.sh", "expect_rc": 0}},
            "install": {"linux": {"script": "d.install.sh", "timeout": 5}},
        }
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "INSTALLED")

    def test_missing_script_fails_the_check_without_crashing(self):
        spec = {"validate": {"linux": {"script": "absent.validate.sh", "expect_rc": 0}}}
        self.assertEqual(pv.check_dependency("d", spec, "linux")["status"], "MISSING_NO_INSTALL")

    def test_windows_script_uses_powershell_file(self):
        args = pv._step_args({"script": "d.install.ps1"}, "windows")
        self.assertEqual(args[:6], ["powershell", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", args[5]])
        self.assertTrue(args[5].endswith("d.install.ps1"))


class MirrorGetTests(unittest.TestCase):
    """mirror/get.py: mirror first, verified, with an upstream fallback; exit 0 iff the file is in place."""

    GET = Path(__file__).with_name("mirror") / "get.py"

    @classmethod
    def setUpClass(cls):
        import functools, http.server, threading
        cls._root = tempfile.TemporaryDirectory()
        root = Path(cls._root.name)
        (root / "mirror/models").mkdir(parents=True)
        (root / "upstream").mkdir()
        cls.good = b"model-bytes"
        (root / "mirror/models/served.bin").write_bytes(cls.good)
        (root / "mirror/models/corrupt.bin").write_bytes(b"tampered")
        (root / "upstream/served.bin").write_bytes(cls.good)
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=str(root))
        handler.log_message = lambda *a: None
        cls._srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls._srv.serve_forever, daemon=True).start()
        port = cls._srv.server_address[1]
        cls.base = f"http://127.0.0.1:{port}/mirror"
        cls.upstream = f"http://127.0.0.1:{port}/upstream/served.bin"
        sha = __import__("hashlib").sha256(cls.good).hexdigest()
        cls.manifest = root / "artifacts.json"
        cls.manifest.write_text(json.dumps([
            {"dest": d, "url": cls.upstream, "size": len(cls.good), "sha256": sha}
            for d in ("models/served.bin", "models/corrupt.bin", "models/absent.bin")
        ]))

    @classmethod
    def tearDownClass(cls):
        cls._srv.shutdown()
        cls._root.cleanup()

    def _get(self, path, upstream=False, base=None):
        out = tempfile.TemporaryDirectory()
        self.addCleanup(out.cleanup)
        dest = Path(out.name) / "sub" / "file.bin"
        ledger = Path(out.name) / "ledger.jsonl"
        env = dict(os.environ, PLAYBOOKS_MIRROR_LEDGER=str(ledger))
        env.pop("ARTIFACTORY_BASE", None)
        if base is not None:
            env["ARTIFACTORY_BASE"] = base
        cmd = [sys.executable, str(self.GET), "--manifest", str(self.manifest), "fetch", path, "--to", str(dest)]
        rc = subprocess.run(cmd + (["--upstream"] if upstream else []), env=env,
                            capture_output=True, text=True).returncode
        outcomes = [json.loads(l)["outcome"] for l in ledger.read_text().splitlines()] if ledger.exists() else []
        return rc, dest, outcomes

    def test_served_by_mirror(self):
        rc, dest, outcomes = self._get("models/served.bin", base=self.base)
        self.assertEqual((rc, dest.read_bytes(), outcomes), (0, self.good, ["downloaded"]))

    def test_no_secret_falls_back_to_upstream(self):
        rc, dest, outcomes = self._get("models/served.bin", upstream=True)
        self.assertEqual((rc, dest.read_bytes(), outcomes), (0, self.good, ["no-secret", "upstream"]))

    def test_mirror_miss_falls_back_to_upstream(self):
        rc, dest, outcomes = self._get("models/absent.bin", upstream=True, base=self.base)
        self.assertEqual((rc, dest.read_bytes(), outcomes), (0, self.good, ["absent", "upstream"]))

    def test_corrupt_mirror_copy_is_rejected(self):
        rc, dest, outcomes = self._get("models/corrupt.bin", base=self.base)
        self.assertEqual((rc, dest.exists(), outcomes), (1, False, ["failed"]))
        self.assertFalse(dest.with_name(dest.name + ".part").exists())

    def test_present_file_is_left_alone(self):
        out = tempfile.TemporaryDirectory()
        self.addCleanup(out.cleanup)
        dest = Path(out.name) / "file.bin"
        dest.write_bytes(b"already here")
        env = dict(os.environ, ARTIFACTORY_BASE="http://127.0.0.1:9")  # nothing listens here
        rc = subprocess.run([sys.executable, str(self.GET), "--manifest", str(self.manifest), "fetch",
                             "models/served.bin", "--to", str(dest)], env=env, capture_output=True).returncode
        self.assertEqual((rc, dest.read_bytes()), (0, b"already here"))

    def test_manifest_entries_are_well_formed(self):
        entries = json.loads((self.GET.parent / "artifacts.json").read_text(encoding="utf-8"))
        bad = [e.get("dest") for e in entries
               if not (e.get("dest") and not e["dest"].startswith("/") and e.get("url", "").startswith("https://")
                       and isinstance(e.get("size"), int) and re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", "")))]
        self.assertEqual(bad, [])
        self.assertEqual(len({e["dest"] for e in entries}), len(entries))


class RegistryIntegrityTests(unittest.TestCase):
    """Catch a broken step reference here, before it breaks prereq validation on every runner."""

    REGISTRY = Path(__file__).resolve().parents[2] / "playbooks" / "dependencies" / "registry.json"
    EXT = {"linux": ".sh", "windows": ".ps1"}

    def _steps(self):
        deps = json.loads(self.REGISTRY.read_text(encoding="utf-8"))["dependencies"]
        for dep_id, spec in deps.items():
            for kind in ("validate", "install"):
                for platform, step in (spec.get(kind) or {}).items():
                    yield dep_id, kind, platform, step

    def test_each_step_is_exactly_one_of_cmd_or_script(self):
        bad = [f"{d}.{k}.{p}" for d, k, p, s in self._steps() if ("cmd" in s) == ("script" in s)]
        self.assertEqual(bad, [])

    def test_scripts_exist_and_follow_naming(self):
        bad = []
        for d, k, p, s in self._steps():
            if "script" in s:
                expected = f"{d}.{k}{self.EXT[p]}"
                if s["script"] != expected or not (pv.PREREQ_SCRIPTS_DIR / expected).is_file():
                    bad.append(f"{d}.{k}.{p} -> {s['script']} (expected {expected}, present)")
        self.assertEqual(bad, [])

    def test_no_orphan_scripts(self):
        referenced = {s["script"] for _, _, _, s in self._steps() if "script" in s}
        on_disk = {
            f.name for f in pv.PREREQ_SCRIPTS_DIR.iterdir()
            if re.search(r"\.(validate|install)\.(sh|ps1)$", f.name)
        }
        self.assertEqual(sorted(on_disk - referenced), [])


if __name__ == "__main__":
    unittest.main()
