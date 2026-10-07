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
- mirror/get.py: verified fetches with an upstream fallback, and seeding a
  dependency's mirrored files into Lemonade, LM Studio and Ollama stores.
"""

import functools
import hashlib
import http.server
import importlib.util
import json
import os
import re
import subprocess
import sys
import tempfile
import threading
import unittest
import unittest.mock
from pathlib import Path

_SPEC = importlib.util.spec_from_file_location(
    "prereq_validate", Path(__file__).with_name("prereq_validate.py")
)
pv = importlib.util.module_from_spec(_SPEC)
_SPEC.loader.exec_module(pv)
_GET_SPEC = importlib.util.spec_from_file_location("mirror_get", pv.MIRROR_GET)
mirror_get = importlib.util.module_from_spec(_GET_SPEC)
_GET_SPEC.loader.exec_module(mirror_get)

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

def _sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    """Static files for the mirror fakes, without a log line per request."""

    def log_message(self, *args):
        pass


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

    def _fake_seeder(self, tmp, body):
        fake = Path(tmp) / "get.py"
        fake.write_text(body, encoding="utf-8")
        saved = pv.MIRROR_GET
        pv.MIRROR_GET = fake
        self.addCleanup(setattr, pv, "MIRROR_GET", saved)

    def test_mirror_seed_heals_without_running_the_install(self):
        with tempfile.TemporaryDirectory() as tmp:
            flag = Path(tmp) / "seeded"
            self._fake_seeder(tmp, f"import pathlib; pathlib.Path({str(flag)!r}).touch()\n")
            spec = {
                "validate": {"linux": {"cmd": f"test -f {flag}", "expect_rc": 0}},
                "install": {"linux": {"mirror": "g", "cmd": "false", "timeout": 5}},
            }
            r = pv.check_dependency("d", spec, "linux")
            self.assertEqual((r["status"], r["mirror_rc"], "install_rc" in r), ("INSTALLED", 0, False))

    def test_a_full_seed_waits_for_the_tool_to_notice_its_files(self):
        with tempfile.TemporaryDirectory() as tmp:
            self._fake_seeder(tmp, "")
            self.addCleanup(setattr, pv, "SEED_SETTLE_SECONDS", pv.SEED_SETTLE_SECONDS)
            pv.SEED_SETTLE_SECONDS = 0
            calls = Path(tmp) / "calls"  # validate passes on its third check after the seed
            check = f'n=$(cat {calls} 2>/dev/null || echo 0); echo $((n+1)) > {calls}; [ "$n" -ge 3 ]'
            spec = {
                "validate": {"linux": {"cmd": check, "expect_rc": 0}},
                "install": {"linux": {"mirror": "g", "cmd": "false", "timeout": 5}},
            }
            r = pv.check_dependency("d", spec, "linux")
            self.assertEqual((r["status"], "install_rc" in r), ("INSTALLED", False))

    def test_windows_install_picks_up_path_entries_the_installer_added(self):
        with tempfile.TemporaryDirectory() as tmp:
            gh_path = Path(tmp) / "github_path"
            saved = pv._registry_path_entries
            pv._registry_path_entries = lambda: [r"C:\old", r"C:\new\bin", r"C:\new\bin"]
            self.addCleanup(setattr, pv, "_registry_path_entries", saved)
            with unittest.mock.patch.dict(os.environ, {"PATH": r"C:\old", "GITHUB_PATH": str(gh_path)}), \
                    unittest.mock.patch.object(os, "pathsep", ";"):
                pv._refresh_windows_path()
                self.assertEqual(os.environ["PATH"].split(";"), [r"C:\new\bin", r"C:\old"])
            self.assertEqual(gh_path.read_text().splitlines(), [r"C:\new\bin"])

    def test_path_is_refreshed_between_a_windows_install_and_its_revalidate(self):
        calls = []
        patches = {"_run": lambda step, platform, timeout: calls.append("install") or 0,
                   "_validate": lambda spec, platform: calls.append("validate") or len(calls) > 2,
                   "_refresh_windows_path": lambda: calls.append("refresh")}
        for name, fake in patches.items():
            self.addCleanup(setattr, pv, name, getattr(pv, name))
            setattr(pv, name, fake)
        spec = {"validate": {"windows": {"cmd": "x"}}, "install": {"windows": {"cmd": "y"}}}
        self.assertEqual(pv.check_dependency("d", spec, "windows")["status"], "INSTALLED")
        self.assertEqual(calls, ["validate", "install", "refresh", "validate"])

    def test_install_still_runs_when_seeding_falls_short(self):
        with tempfile.TemporaryDirectory() as tmp:
            flag = Path(tmp) / "installed"
            self._fake_seeder(tmp, "raise SystemExit(1)\n")
            spec = {
                "validate": {"linux": {"cmd": f"test -f {flag}", "expect_rc": 0}},
                "install": {"linux": {"mirror": "g", "cmd": f"touch {flag}", "timeout": 5}},
            }
            r = pv.check_dependency("d", spec, "linux")
            self.assertEqual((r["status"], r["mirror_rc"], r["install_rc"]), ("INSTALLED", 1, 0))


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
        cls._root = tempfile.TemporaryDirectory()
        root = Path(cls._root.name)
        (root / "mirror/models").mkdir(parents=True)
        (root / "upstream").mkdir()
        cls.good = b"model-bytes"
        (root / "mirror/models/served.bin").write_bytes(cls.good)
        (root / "mirror/models/corrupt.bin").write_bytes(b"tampered")
        (root / "upstream/served.bin").write_bytes(cls.good)
        handler = functools.partial(_QuietHandler, directory=str(root))
        cls._srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls._srv.serve_forever, daemon=True).start()
        port = cls._srv.server_address[1]
        cls.base = f"http://127.0.0.1:{port}/mirror"
        cls.upstream = f"http://127.0.0.1:{port}/upstream/served.bin"
        sha = _sha256(cls.good)
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
        outcomes = [json.loads(line)["outcome"] for line in ledger.read_text().splitlines()] if ledger.exists() else []
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
               if not (e.get("group") and e.get("dest") and not e["dest"].startswith("/")
                       and e.get("url", "").startswith("https://")
                       and isinstance(e.get("size"), int) and re.fullmatch(r"[0-9a-f]{64}", e.get("sha256", "")))]
        self.assertEqual(bad, [])
        self.assertEqual(len({e["dest"] for e in entries}), len(entries))


class MirrorSeedTests(unittest.TestCase):
    """mirror/get.py seed: a dependency's mirrored files land where its tool's own install looks."""

    GET = MirrorGetTests.GET
    FILES = {  # Ollama's manifest is listed before its blob on purpose: seed must reorder them.
        "models/lemonade/org/repo/model.gguf": b"gguf-bytes",
        "models/lemonade/org/repo/stale.gguf": b"old-bytes",
        "models/lmstudio/user/repo/model.gguf": b"lms-bytes",
        "models/Ollama/m/manifests/registry.ollama.ai/library/m/tag": b"{}",
        "models/Ollama/m/blobs/sha256-0a": b"blob",
    }

    @classmethod
    def setUpClass(cls):
        cls._root = tempfile.TemporaryDirectory()
        root = Path(cls._root.name)
        for rel, data in cls.FILES.items():
            (root / "mirror" / rel).parent.mkdir(parents=True, exist_ok=True)
            (root / "mirror" / rel).write_bytes(data)
        # A fake Hugging Face API: org/repo is at commit c0ffee, where stale.gguf has since changed.
        api = root / "hf/api/models/org/repo"
        (api / "revision").mkdir(parents=True)
        (api / "revision/main").write_text(json.dumps({"sha": "c0ffee"}))
        (api / "tree").mkdir()
        (api / "tree/c0ffee").write_text(json.dumps([
            {"path": "model.gguf", "lfs": {"oid": _sha256(b"gguf-bytes")}},
            {"path": "stale.gguf", "lfs": {"oid": _sha256(b"new-bytes")}},
        ]))
        handler = functools.partial(_QuietHandler, directory=str(root))
        cls._srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), handler)
        threading.Thread(target=cls._srv.serve_forever, daemon=True).start()
        port = cls._srv.server_address[1]
        cls.base, cls.hf = f"http://127.0.0.1:{port}/mirror", f"http://127.0.0.1:{port}/hf"
        tool = {"lemonade": "lemonade", "lmstudio": "lmstudio", "Ollama": "ollama"}
        cls.manifest = root / "artifacts.json"
        # Only LM Studio falls back upstream; its fixture upstream serves the same bytes.
        cls.manifest.write_text(json.dumps([
            {"group": f"{tool[rel.split('/')[1]]}-models-x", "dest": rel,
             "url": f"{cls.base}/{rel}" if "/lmstudio/" in rel else "https://example.invalid/",
             "size": len(data), "sha256": _sha256(data)} for rel, data in cls.FILES.items()
        ]))

    @classmethod
    def tearDownClass(cls):
        cls._srv.shutdown()
        cls._root.cleanup()

    def _seed(self, group, secret=True):
        out = tempfile.TemporaryDirectory()
        self.addCleanup(out.cleanup)
        store, ledger = Path(out.name) / "store", Path(out.name) / "ledger.jsonl"
        env = dict(os.environ, PLAYBOOKS_MIRROR_LEDGER=str(ledger), PLAYBOOKS_MIRROR_STORE=str(store),
                   HF_ENDPOINT=self.hf)
        for var in ("ARTIFACTORY_BASE", "HF_TOKEN"):
            env.pop(var, None)
        if secret:
            env["ARTIFACTORY_BASE"] = self.base
        rc = subprocess.run([sys.executable, str(self.GET), "--manifest", str(self.manifest), "seed", group],
                            env=env, capture_output=True, text=True).returncode
        lines = ledger.read_text().splitlines() if ledger.exists() else []
        return rc, store, [(json.loads(line)["artifact"], json.loads(line)["outcome"]) for line in lines]

    def test_lemonade_seeds_the_current_snapshot_and_leaves_changed_files_to_the_pull(self):
        rc, store, ledger = self._seed("lemonade-models-x")
        snapshot = store / "models--org--repo" / "snapshots" / "c0ffee"
        self.assertEqual((snapshot / "model.gguf").read_bytes(), b"gguf-bytes")
        self.assertFalse((snapshot / "stale.gguf").exists())
        self.assertEqual((rc, [o for _, o in ledger]), (1, ["stale", "downloaded"]))

    def test_lmstudio_seeds_the_user_repo_folder(self):
        rc, store, ledger = self._seed("lmstudio-models-x")
        self.assertEqual((rc, (store / "user/repo/model.gguf").read_bytes()), (0, b"lms-bytes"))

    def test_ollama_places_the_manifest_after_its_blobs(self):
        rc, store, ledger = self._seed("ollama-models-x")
        self.assertEqual(rc, 0)
        self.assertEqual((store / "blobs/sha256-0a").read_bytes(), b"blob")
        self.assertTrue((store / "manifests/registry.ollama.ai/library/m/tag").is_file())
        self.assertEqual([a.split("/")[3] for a, _ in ledger], ["blobs", "manifests"])

    def test_unreachable_mirror_is_tried_once_per_group(self):
        saved = self.base
        self.base = "http://127.0.0.1:9"  # nothing listens here
        try:
            rc, store, ledger = self._seed("ollama-models-x")
        finally:
            self.base = saved
        self.assertEqual((rc, [o for _, o in ledger]), (1, ["unreachable", "skipped"]))

    def test_no_secret_leaves_the_store_untouched(self):
        rc, store, ledger = self._seed("ollama-models-x", secret=False)
        self.assertEqual((rc, store.exists(), ledger), (1, False, []))

    def test_lmstudio_falls_back_to_the_pinned_upstream_without_the_mirror(self):
        rc, store, ledger = self._seed("lmstudio-models-x", secret=False)
        self.assertEqual((rc, (store / "user/repo/model.gguf").read_bytes()), (0, b"lms-bytes"))
        self.assertEqual([o for _, o in ledger], ["no-secret", "upstream"])

    def test_unknown_group_fails(self):
        self.assertEqual(self._seed("comfyui")[0], 1)


class _FakeArtifactory(http.server.BaseHTTPRequestHandler):
    """Storage API reads, token-gated PUTs that verify X-Checksum-Sha256, and an upstream file."""

    store: dict = {}
    upstream: dict = {}
    token = "t0ken"

    def log_message(self, *args):
        pass

    def _reply(self, code, body=b""):
        self.send_response(code)
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def do_GET(self):
        if self.path.startswith("/artifactory/api/storage/repo/"):
            key = self.path[len("/artifactory/api/storage/repo/"):]
            if key in self.store:
                return self._reply(200, json.dumps({"checksums": {"sha256": _sha256(self.store[key])}}).encode())
            return self._reply(404)
        if self.path in self.upstream:
            return self._reply(200, self.upstream[self.path])
        self._reply(404)

    def do_HEAD(self):
        self._reply(404)

    def do_PUT(self):
        body = self.rfile.read(int(self.headers.get("Content-Length") or 0))
        if self.headers.get("Authorization") != f"Bearer {self.token}":
            return self._reply(401)
        if self.headers.get("X-Checksum-Deploy") == "true":
            body = next((b for b in self.store.values() if _sha256(b) == self.headers.get("X-Checksum-Sha256")), None)
            if body is None:
                return self._reply(404)
        if self.headers.get("X-Checksum-Sha256") != _sha256(body):
            return self._reply(409)
        self.store[self.path[len("/artifactory/repo/"):]] = body
        self._reply(201)


class MirrorToolTests(unittest.TestCase):
    """mirror/mirror.py: push uploads only what the mirror lacks, verified twice; check reports drift."""

    TOOL = Path(__file__).with_name("mirror") / "mirror.py"

    @classmethod
    def setUpClass(cls):
        cls._srv = http.server.ThreadingHTTPServer(("127.0.0.1", 0), _FakeArtifactory)
        threading.Thread(target=cls._srv.serve_forever, daemon=True).start()
        port = cls._srv.server_address[1]
        cls.base = f"http://127.0.0.1:{port}/artifactory/repo"
        _FakeArtifactory.upstream.update({"/up/new.bin": b"new-bytes", "/up/bad.bin": b"tampered"})
        cls._tmp = tempfile.TemporaryDirectory()
        cls.manifest = Path(cls._tmp.name) / "artifacts.json"
        cls.manifest.write_text(json.dumps([
            {"group": "g", "dest": "models/new.bin", "url": f"http://127.0.0.1:{port}/up/new.bin",
             "size": 9, "sha256": _sha256(b"new-bytes")},
            {"group": "g", "dest": "models/kept.bin", "url": f"http://127.0.0.1:{port}/up/new.bin",
             "size": 9, "sha256": _sha256(b"new-bytes")},
            {"group": "bad", "dest": "models/bad.bin", "url": f"http://127.0.0.1:{port}/up/bad.bin",
             "size": 9, "sha256": _sha256(b"good-bytes")},
            {"group": "link", "dest": "models/link.bin", "url": f"http://127.0.0.1:{port}/up/absent.bin",
             "size": 19, "sha256": _sha256(b"someone else's file")},
        ]))

    @classmethod
    def tearDownClass(cls):
        cls._srv.shutdown()
        cls._tmp.cleanup()

    def setUp(self):
        _FakeArtifactory.store.clear()
        _FakeArtifactory.store["models/kept.bin"] = b"someone else's file"

    def _run(self, *args, token=True):
        env = dict(os.environ, ARTIFACTORY_BASE=self.base, MIRROR_STAGING=str(Path(self._tmp.name) / "staging"))
        env.pop("ARTIFACTORY_TOKEN", None)
        if token:
            env["ARTIFACTORY_TOKEN"] = _FakeArtifactory.token
        r = subprocess.run([sys.executable, str(self.TOOL), "--manifest", str(self.manifest), *args],
                           env=env, capture_output=True, text=True)
        return r.returncode, r.stdout

    def test_push_uploads_what_is_missing_and_never_replaces(self):
        rc, out = self._run("push", "--group", "g")
        self.assertEqual(rc, 0, out)
        self.assertEqual(_FakeArtifactory.store["models/new.bin"], b"new-bytes")
        self.assertEqual(_FakeArtifactory.store["models/kept.bin"], b"someone else's file")

    def test_push_refuses_an_upstream_copy_that_does_not_match_the_pin(self):
        rc, _ = self._run("push", "--group", "bad")
        self.assertEqual((rc, "models/bad.bin" in _FakeArtifactory.store), (1, False))

    def test_push_links_a_file_the_mirror_already_stores_without_downloading_it(self):
        rc, out = self._run("push", "--group", "link")  # its url 404s, so only a link can succeed
        self.assertEqual((rc, _FakeArtifactory.store.get("models/link.bin")), (0, b"someone else's file"), out)

    def test_push_needs_a_token(self):
        self.assertEqual(self._run("push", "--group", "g", token=False)[0], 1)
        self.assertNotIn("models/new.bin", _FakeArtifactory.store)

    def test_check_reports_missing_and_different_files(self):
        rc, out = self._run("check", "--group", "g")
        self.assertEqual(rc, 1)
        self.assertRegex(out, r"missing\s+models/new\.bin")
        self.assertRegex(out, r"DIFFERENT\s+models/kept\.bin")


class RegistryIntegrityTests(unittest.TestCase):
    """Catch a broken step reference here, before it breaks prereq validation on every runner."""

    ROOT = Path(__file__).resolve().parents[2]
    EXT = {"linux": ".sh", "windows": ".ps1"}

    def _registries(self):
        """English as "", then each locale's own registry under its locale name."""
        yield "", self.ROOT / "playbooks" / "dependencies" / "registry.json"
        for path in sorted(self.ROOT.glob("localized-playbooks/*/dependencies/registry.json")):
            yield path.parts[-3], path

    def _steps(self):
        for locale, path in self._registries():
            for dep_id, spec in json.loads(path.read_text(encoding="utf-8"))["dependencies"].items():
                for kind in ("validate", "install"):
                    for platform, step in (spec.get(kind) or {}).items():
                        yield (f"{locale}/{dep_id}" if locale else dep_id), kind, platform, step

    def test_each_step_is_exactly_one_of_cmd_or_script(self):
        bad = [f"{d}.{k}.{p}" for d, k, p, s in self._steps() if ("cmd" in s) == ("script" in s)]
        self.assertEqual(bad, [])

    def test_scripts_exist_and_follow_naming(self):
        bad = []
        for d, k, p, s in self._steps():
            if "script" in s:
                expected = f"{d.rsplit('/', 1)[-1]}.{k}{self.EXT[p]}"
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

    def _groups(self):
        return {e["group"] for e in json.loads(mirror_get.MANIFEST.read_text(encoding="utf-8"))}

    def test_mirror_groups_are_named_after_their_install(self):
        groups = self._groups()
        bad = [f"{d}.{k}.{p}" for d, k, p, s in self._steps()
               if "mirror" in s and (k != "install" or s["mirror"] != d or s["mirror"] not in groups)]
        self.assertEqual(bad, [])

    def test_every_seedable_group_is_used(self):
        used = {s["mirror"] for _, _, _, s in self._steps() if "mirror" in s}
        seedable = {g for g in self._groups() if mirror_get.tool_of(g)}
        self.assertEqual(sorted(seedable - used), [])


class LocaleTests(unittest.TestCase):
    """A localized run checks the localized README against English steps plus the locale's own."""

    def setUp(self):
        self._tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self._tmp.cleanup)
        self.root = Path(self._tmp.name)
        def write(rel, data):
            (self.root / rel).parent.mkdir(parents=True, exist_ok=True)
            (self.root / rel).write_text(data if isinstance(data, str) else json.dumps(data), encoding="utf-8")
        write("playbooks/dependencies/registry.json", {"dependencies": {
            "lemonade": {"name": "Lemonade", "validate": {"linux": {"cmd": "en-check"}}, "install": {"linux": {"cmd": "en-install"}}}}})
        write("localized-playbooks/xx-YY/dependencies/registry.json", {"dependencies": {
            "lemonade": {"name": "Lemonade (xx)", "file": "lemonade.md"},
            "local-model": {"name": "Local", "validate": {"linux": {"cmd": "xx-check"}}}}})
        write("playbooks/core/demo/README.md", "<!-- @require:lemonade -->\n")
        write("localized-playbooks/xx-YY/core/demo/README.md", "<!-- @require:lemonade -->\n<!-- @prereq:local-model -->\n")

    def test_a_locale_keeps_english_steps_and_adds_its_own(self):
        deps = pv.load_registry(self.root, "xx-YY")
        self.assertEqual(deps["lemonade"]["name"], "Lemonade (xx)")
        self.assertEqual(deps["lemonade"]["validate"]["linux"]["cmd"], "en-check")
        self.assertEqual(deps["lemonade"]["install"]["linux"]["cmd"], "en-install")
        self.assertEqual(deps["local-model"]["validate"]["linux"]["cmd"], "xx-check")
        self.assertNotIn("local-model", pv.load_registry(self.root))

    def test_a_locale_reads_its_own_readme(self):
        readme = pv.find_playbook_path("demo", self.root, "xx-YY") / "README.md"
        self.assertEqual(pv.extract_scoped_requires(readme.read_text(), "linux", None), ["lemonade", "local-model"])
        self.assertEqual(pv.find_playbook_path("demo", self.root), self.root / "playbooks/core/demo")

    def test_a_locale_prefixed_group_seeds_into_its_tool(self):
        self.assertIs(mirror_get.tool_of("zh-CN/lemonade-models-x"), mirror_get.TOOLS["lemonade"])
        self.assertIs(mirror_get.tool_of("lmstudio-models-x"), mirror_get.TOOLS["lmstudio"])
        self.assertIsNone(mirror_get.tool_of("hf:Qwen/Qwen3.5-4B"))


if __name__ == "__main__":
    unittest.main()
