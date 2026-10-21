#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT
"""V2 selection/provisioning and verdict contract; no hardware or API calls."""

import copy
import base64
import io
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import tempfile
import signal
import subprocess
import threading
import time
from types import SimpleNamespace
import unittest
from contextlib import redirect_stdout
from urllib import error
from unittest import mock

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT / ".github/orchestrai"))
import orchestrai_v2 as v2
import orchestrai_v2_api as api


class V2Contract(unittest.TestCase):
    def setUp(self):
        self.cfg = v2.legacy.load_config(ROOT / ".github/orchestrai-config.yml")
        self.cfg["device_to_tags"] = {"halo": ["apu-halo"], "rx9070xt": ["radeon"]}
        self.cfg["provisioning"]["therock_url"] = "https://example.invalid/therock.tar.gz"
        self.cfg["provisioning"]["windows_driver"]["source"] = "driver-coordinate"
        self.cfg["provisioning"]["windows_driver"]["use"] = "internal"
        self.cfg["provisioning"]["linux_kernel_driver"]["source"] = "https://example.invalid/driver.deb"
        self.env = mock.patch.dict(os.environ, {
            "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://example.invalid/wheels/",
        }, clear=True)
        self.env.start()
        self.addCleanup(self.env.stop)
        self.batch = {"platform": "linux", "arch": "halo", "tags": ["apu-halo"],
                      "playbooks": ["ollama-getting-started", "gaia-agents"]}

    def request(self, **kwargs):
        return v2.request_for("linux/halo", kwargs.get("batch", self.batch), self.cfg,
                              "a" * 40, "playbooks-test", "catalog-id", "rp-publisher")

    def test_sessions_preserve_distinct_playbook_variables_and_external_sha(self):
        request = self.request()
        sessions = request["parameters"]["PLAN_JSON"]["sessions"]
        self.assertEqual([s["name"] for s in sessions],
                         ["playbook-ollama-getting-started", "playbook-gaia-agents"])
        for pb, session in zip(self.batch["playbooks"], sessions):
            self.assertEqual(session["machine_tags"], ["apu-halo"])
            self.assertEqual(session["variables"]["PLAYBOOK_ID"], pb)
            self.assertEqual(session["variables"]["PLAYBOOK_REPO"], v2.EXTERNAL_REPO)
            self.assertEqual(session["variables"]["PLAYBOOK_SHA"], "a" * 40)
            self.assertEqual(session["tests"], ["L4-sys/playbooks/linux/sys_func-playbook_runner"])
            self.assertNotIn("HF_TOKEN", session["variables"])
        self.assertEqual(request["parameters"]["PLAN_JSON"]["catalog_release_id"], "catalog-id")

    def test_radeon_retains_driver_then_therock_order(self):
        batch = {**self.batch, "arch": "rx9070xt", "playbooks": ["ollama-getting-started"]}
        scripts = self.request(batch=batch)["parameters"]["BUILDS_JSON"]["install_scripts"]
        self.assertEqual([s["script"] for s in scripts[:3]], [
            "InstallationScripts/common/install-kernel-headers.sh",
            "InstallationScripts/gfx/linux.sh",
            "InstallationScripts/gfx/linux-therock-tarball.sh",
        ])
        self.assertTrue(scripts[1]["reboot_after"])

    def test_windows_uses_windows_driver_and_explicit_image_override(self):
        with mock.patch.dict(os.environ, {"ORCHESTRAI_V2_WINDOWS_IMAGE": "windows/test-image"}):
            request = self.request(batch={**self.batch, "platform": "windows"})
        self.assertEqual(request["parameters"]["PLAN_JSON"]["sessions"][0]["os_image"], "windows/test-image")
        self.assertEqual(request["parameters"]["BUILDS_JSON"]["install_scripts"][0]["script"],
                         "InstallationScripts/gfx/windows.ps1")

    def test_public_driver_choice_reaches_the_actual_v2_plan(self):
        env = {"ORCHESTRAI_WINDOWS_DRIVER": "public",
               "ORCHESTRAI_WINDOWS_DRIVER_URL": "https://example.invalid/adrenalin.exe"}
        with mock.patch.dict(os.environ, env):
            cfg = v2.legacy.apply_env_overrides(copy.deepcopy(self.cfg))
        cfg["provisioning"]["windows_driver"]["source"] = ""
        batch = {**self.batch, "platform": "windows", "playbooks": ["ollama-getting-started"]}
        request = v2.request_for("windows/halo", batch, cfg, "a" * 40, "workspace", "", "")
        builds = request["parameters"]["BUILDS_JSON"]
        self.assertEqual(builds["install_scripts"][0], {
            "script": "InstallationScripts/gfx/windows-public-url.ps1", "reboot_after": True})
        self.assertEqual(builds["vars"]["driver_url"], env["ORCHESTRAI_WINDOWS_DRIVER_URL"])
        self.assertNotIn("driver_source", builds["vars"])
        self.assertNotIn("driver_copy", builds["vars"])

    def test_missing_public_driver_never_falls_back_to_the_internal_share(self):
        self.cfg["provisioning"]["windows_driver"]["use"] = "public"
        with self.assertRaisesRegex(ValueError, "ORCHESTRAI_WINDOWS_DRIVER_URL"):
            self.request(batch={**self.batch, "platform": "windows"})

    def test_public_driver_url_uses_the_same_safety_checks_as_external_playbooks(self):
        self.cfg["provisioning"]["windows_driver"]["use"] = "public"
        for url in ("http://example.invalid/setup.exe", "https://user:pass@example.invalid/setup.exe",
                    "https://example.invalid/broken\npath.exe", "https://[broken/setup.exe"):
            with self.subTest(url=url), self.assertRaisesRegex(ValueError, "HTTPS installer URL"):
                self.cfg["provisioning"]["windows_public_driver"]["url"] = url
                self.request(batch={**self.batch, "platform": "windows"})

    def test_public_driver_keeps_windows_therock_after_driver_reboot(self):
        prov = self.cfg["provisioning"]
        prov["windows_driver"]["use"] = "public"
        prov["windows_public_driver"]["url"] = "https://example.invalid/adrenalin.exe"
        prov["windows_therock_url"] = "https://example.invalid/therock-windows.tar.gz"
        batch = {**self.batch, "platform": "windows", "arch": "rx9070xt",
                 "playbooks": ["llama-factory-finetuning"]}
        builds = self.request(batch=batch)["parameters"]["BUILDS_JSON"]
        self.assertEqual([item["script"] for item in builds["install_scripts"][:2]], [
            "InstallationScripts/gfx/windows-public-url.ps1",
            "InstallationScripts/gfx/windows-therock-tarball.ps1"])
        self.assertTrue(builds["install_scripts"][0]["reboot_after"])

    def test_unknown_driver_is_rejected_before_plan_submission(self):
        self.cfg["provisioning"]["windows_driver"]["use"] = "typo"
        with self.assertRaisesRegex(ValueError, "internal or public"):
            self.request(batch={**self.batch, "platform": "windows"})

    def test_missing_provisioning_fails_before_submission(self):
        self.cfg["provisioning"]["therock_url"] = ""
        with self.assertRaisesRegex(ValueError, "ORCHESTRAI_THEROCK_URL"):
            self.request()

    def test_mutable_sha_is_rejected(self):
        with self.assertRaisesRegex(ValueError, "immutable"):
            v2.request_for("linux/halo", self.batch, self.cfg, "main", "workspace", "", "")

    def test_selection_reads_external_metadata_and_respects_requested_subset(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            for pb in ("ollama-getting-started", "gaia-agents"):
                path = source / "playbooks/core" / pb / "playbook.json"
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({"tested_platforms": {"halo": ["linux", "windows"]}}))
            cfg = copy.deepcopy(self.cfg)
            batches = v2.select(cfg, source, "ollama-getting-started,ollama-getting-started", "halo", "linux")
            self.assertEqual(list(batches), ["linux/halo"])
            self.assertEqual(batches["linux/halo"]["playbooks"], ["ollama-getting-started"])
            with self.assertRaisesRegex(ValueError, "absent from the external"):
                v2.select(cfg, source, "not-present", "halo", "linux")

    def test_blank_and_all_selection_preserve_existing_dispatch_semantics(self):
        with tempfile.TemporaryDirectory() as tmp:
            source = Path(tmp)
            cfg = copy.deepcopy(self.cfg)
            # This fixture checks metadata discovery, not production tag/extra-device policy.
            for key in ("extra_tags", "device_extra_tags", "extra_devices"):
                cfg[key] = {}
            for category, pb, platforms in (
                ("core", "ollama-getting-started", {"halo": ["linux", "windows"]}),
                ("supplemental", "gaia-agents", {"halo": ["linux"]}),
                ("core", "windows-only", {"halo": ["windows"]}),
            ):
                path = source / "playbooks" / category / pb / "playbook.json"
                path.parent.mkdir(parents=True)
                path.write_text(json.dumps({"tested_platforms": platforms}))
            for playbooks in ("", "all"):
                for devices in ("", "all", "halo"):
                    with self.subTest(playbooks=playbooks, devices=devices):
                        batches = v2.select(cfg, source, playbooks, devices, "linux")
                        self.assertEqual(set(batches), {"linux/halo"})
                        self.assertEqual(set(batches["linux/halo"]["playbooks"]),
                                         {"ollama-getting-started", "gaia-agents"})
            with self.assertRaisesRegex(ValueError, "No eligible configured hardware"):
                v2.select(cfg, source, "windows-only", "halo", "linux")
            with self.assertRaisesRegex(ValueError, "No eligible playbooks"):
                v2.select(cfg, source, "all", "rx9070xt", "linux")

    def test_workspace_uses_repository_configuration_with_explicit_override(self):
        env = {"ORCHESTRAI_V2_WORKSPACE": "production-workspace"}
        self.assertEqual(v2.resolve_workspace("", env), "production-workspace")
        self.assertEqual(v2.resolve_workspace("  ", env), "production-workspace")
        self.assertEqual(v2.resolve_workspace("other-workspace", env), "other-workspace")
        for value, settings in (("", {}), ("", {"ORCHESTRAI_V2_WORKSPACE": "Display Name"}),
                                ("bad/workspace", env)):
            with self.subTest(value=value, settings=settings), self.assertRaisesRegex(
                    ValueError, "ORCHESTRAI_V2_WORKSPACE"):
                v2.resolve_workspace(value, settings)

    def test_capacity_wait_and_reportportal_are_v2_managed(self):
        cp = self.request()["config"]["control_plane"]
        self.assertEqual(cp["require_capacity"], "queue")
        self.assertEqual(cp["auth"], "oidc")
        self.assertTrue(cp["cancel_on_exit"])
        self.assertNotIn("ci_api_url", cp)
        self.assertEqual(cp["result_publishers"][0]["credential"], "rp-publisher")

    def test_native_plan_has_no_external_publisher_or_reportportal_parameter(self):
        with mock.patch.dict(os.environ, {"ORCHESTRAI_V2_RP_CREDENTIAL": "old-credential"}):
            request = v2.request_for("linux/halo", self.batch, self.cfg,
                                     "a" * 40, "playbooks-test", "catalog-id", "")
        self.assertNotIn("result_publishers", request["config"]["control_plane"])
        self.assertNotIn("result_publishers", request["parameters"]["PLAN_JSON"]["run_settings"])
        self.assertNotIn("RP_PROJECT", request["parameters"])

    def prepare(self, root, export=False):
        args = SimpleNamespace(config="unused", source=str(root), playbooks="ollama-getting-started",
                               devices="halo", platform="linux", sha="a" * 40,
                               workspace="playbooks", catalog="", prepare_only=False,
                               publish_reportportal=export, requests=str(root / "requests"),
                               preview=str(root / "preview"))
        with mock.patch.object(v2.legacy, "load_config", return_value=self.cfg), \
                mock.patch.object(v2.legacy, "apply_env_overrides", side_effect=lambda x: x), \
                mock.patch.object(v2.legacy, "validate_config", return_value=[]), \
                mock.patch.object(v2, "select", return_value={"linux/halo": self.batch}), \
                mock.patch.object(api.Settings, "from_env"):
            v2.prepare(args)
        return json.loads((root / "requests/linux_halo.json").read_text())

    def test_prepare_native_ignores_existing_reportportal_variable(self):
        for credential in ("", "old-credential"):
            with self.subTest(credential=credential), tempfile.TemporaryDirectory() as tmp, \
                    mock.patch.dict(os.environ, {"ORCHESTRAI_V2_RP_CREDENTIAL": credential}):
                request = self.prepare(Path(tmp))
                self.assertNotIn("result_publishers", request["config"]["control_plane"])

    def test_explicit_export_requires_credential_and_remains_required(self):
        with tempfile.TemporaryDirectory() as tmp:
            with self.assertRaisesRegex(ValueError, "export was requested"):
                self.prepare(Path(tmp), export=True)
            with mock.patch.dict(os.environ, {"ORCHESTRAI_V2_RP_CREDENTIAL": "rp"}):
                request = self.prepare(Path(tmp), export=True)
            publisher = request["config"]["control_plane"]["result_publishers"][0]
            self.assertEqual(publisher["credential"], "rp")
            self.assertTrue(publisher["required"])

    def test_nested_metadata_does_not_reject_a_complete_pass(self):
        result = {"verdict": "success", "tests_summary": {
            "total": 17, "passed": 17, "failed": 0, "running": 0,
            "per_test": {"total": 1, "machines": 17, "passed": 1},
        }}
        self.assertEqual(v2.validate_result(result, 17), result)

    def test_nested_metadata_cannot_hide_bad_outcome_counters(self):
        for field in ("not_run", "interrupted", "cancelled", "unknown", "errors"):
            result = {"verdict": "success", "tests_summary": {
                "total": 1, "passed": 1, "per_test": {}, field: 1}}
            self.assertEqual(v2.validate_result(result, 1)["verdict"], "failure")
        for counts in ([], "not an object", {"total": -1, "passed": 1},
                       {"total": 1, "passed": 1, "not_run": True}):
            self.assertEqual(v2.validate_result({"verdict": "success", "tests_summary": counts}, 1)["verdict"],
                             "failure")

    def test_zero_missing_skipped_and_extra_verdicts_cannot_pass(self):
        for counts in ({}, {"total": 0, "passed": 0}, {"total": 2, "passed": 1, "skipped": 1},
                       {"total": 3, "passed": 3}, {"total": 2, "passed": 2, "errors": 1}):
            result = v2.validate_result({"verdict": "success", "tests_summary": counts}, 2)
            self.assertEqual(result["verdict"], "failure")
            self.assertEqual(result["status"], "tests-errored")

    def test_success_and_failure_verdicts_are_preserved(self):
        success = {"verdict": "success", "tests_summary": {"total": 2, "passed": 2}}
        failure = {"verdict": "failure", "status": "timeout"}
        self.assertEqual(v2.validate_result(success, 2), success)
        self.assertEqual(v2.validate_result(failure, 2), failure)

    def test_boolean_and_string_counts_cannot_pass(self):
        for counts in ({"total": 1, "passed": True}, {"total": 1, "passed": "1"}):
            self.assertEqual(v2.validate_result({"verdict": "success", "tests_summary": counts}, 1)["verdict"],
                             "failure")


class NativeReporting(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.plan = [{"batch_id": "linux/halo", "playbook_sha": "a" * 40, "playbook_count": 2},
                     {"batch_id": "windows/halo", "playbook_sha": "a" * 40, "playbook_count": 2}]
        self.args = SimpleNamespace(plan=str(self.root / "plan.json"), artifacts=str(self.root / "artifacts"))
        v2.write_json(self.args.plan, self.plan)
        self.result = {"batch_id": "linux/halo", "playbook_sha": "a" * 40, "expected": 2,
                       "status": "passed", "verdict": "success", "result_destination": "native",
                       "url": "https://example.invalid/#/runs/one", "pipeline_url": "https://jenkins.invalid/1/",
                       "tests": [{"path": "shared-adapter", "outcome": "passed"},
                                 {"path": "shared-adapter", "outcome": "passed"}]}
        self.output = redirect_stdout(io.StringIO())
        self.output.__enter__()
        self.addCleanup(self.output.__exit__, None, None, None)

    def save(self, result, folder):
        v2.write_json(Path(self.args.artifacts) / folder / "result.json", result)

    def test_aggregate_duplicate_adapter_paths_and_not_run_without_guessing_names(self):
        self.save(self.result, "linux")
        other = {**self.result, "batch_id": "windows/halo", "status": "failed", "verdict": "failure",
                 "tests": [{"path": "shared-adapter", "outcome": "failed"},
                           {"path": "shared-adapter", "outcome": "not_run"}]}
        self.save(other, "windows")
        report = v2.summary(self.args)
        self.assertIn("linux/halo | 2 | 2 | 0 | 0 | 0 | 0 | passed | success", report)
        self.assertIn("windows/halo | 2 | 0 | 1 | 1 | 0 | 0 | failed | failure", report)
        self.assertIn("V2 logs", report)
        self.assertIn("does not infer identity", report)
        self.assertNotIn("ReportPortal]", report)

    def test_missing_result_is_written_as_unknown_then_fails_reporting(self):
        self.save(self.result, "linux")
        step_summary = self.root / "step.md"
        with mock.patch.dict(os.environ, {"GITHUB_STEP_SUMMARY": str(step_summary)}):
            with self.assertRaisesRegex(ValueError, "artifacts are missing"):
                v2.summary(self.args)
        report = step_summary.read_text()
        self.assertIn("windows/halo | 2 | 0 | 0 | 0 | 0 | 2 | UNKNOWN | UNKNOWN", report)

    def test_reports_link_only_to_native_runs_not_executor(self):
        self.save(self.result, "linux")
        self.save({**self.result, "batch_id": "windows/halo"}, "windows")
        for report in (v2.result_report(self.result, "linux/halo"), v2.summary(self.args)):
            self.assertIn(self.result["url"], report)
            self.assertNotIn(self.result["pipeline_url"], report)
            self.assertNotIn("Jenkins", report)
        # Keep executor coordinates in diagnostic metadata, not rendered links.
        self.assertEqual(self.result["pipeline_url"], "https://jenkins.invalid/1/")

    def test_missing_native_link_does_not_fall_back_to_executor(self):
        result = {**self.result, "url": ""}
        self.save(result, "linux")
        self.save({**result, "batch_id": "windows/halo"}, "windows")
        report = v2.summary(self.args)
        self.assertIn("No V2 run link", report)
        for rendered in (report, v2.result_report(result, "linux/halo")):
            self.assertNotIn(result["pipeline_url"], rendered)

    def test_source_mismatch_and_duplicate_configuration_are_rejected(self):
        self.save({**self.result, "playbook_sha": "b" * 40}, "linux")
        with self.assertRaisesRegex(ValueError, "source mismatch"):
            v2.summary(self.args)
        self.save(self.result, "linux")
        self.save(self.result, "duplicate")
        with self.assertRaisesRegex(ValueError, "Duplicate"):
            v2.summary(self.args)

    def test_all_tests_passed_but_pipeline_failed_is_not_a_test_failure(self):
        result = {**self.result, "status": "failed", "verdict": "failure", "pipeline_status": "FAILURE"}
        report = v2.result_report(result, "linux/halo")
        self.assertIn("2 passed · 0 failed", report)
        self.assertIn("All returned test executions passed", report)
        self.assertIn("Executor/publishing status: **FAILURE**", report)
        self.assertEqual(result["verdict"], "failure")

    def test_links_and_cells_cannot_inject_markdown_html_or_credentials(self):
        for url in ("http://example.invalid", "https://user:secret@example.invalid", "https://bad.invalid:wrong",
                    "https://example.invalid\n::error::bad", "javascript:alert(1)"):
            self.assertEqual(v2.result_link(url, "V2"), "")
        self.assertNotIn(")evil", v2.result_link("https://example.invalid/)evil", "V2"))
        self.assertEqual(v2.cell("<x>|a\nb"), "&lt;x&gt;\\|a b")

    def test_both_dispatch_forms_default_to_reportportal_and_aggregate_after_failure(self):
        import yaml
        workflow = yaml.load((ROOT / ".github/workflows/test-playbooks-orchestrai-v2.yml").read_text(),
                             Loader=yaml.BaseLoader)
        bridge = yaml.load((ROOT / ".github/workflows/test-playbooks-orchestrai.yml").read_text(),
                           Loader=yaml.BaseLoader)
        for event in ("workflow_dispatch", "workflow_call"):
            self.assertEqual(workflow["on"][event]["inputs"]["publish_reportportal"]["default"], "true")
        self.assertEqual(bridge["on"]["workflow_dispatch"]["inputs"]["v2_publish_reportportal"]["default"], "true")
        self.assertIn("inputs.v2_publish_reportportal", bridge["jobs"]["v2"]["with"]["publish_reportportal"])
        self.assertIn("always()", workflow["jobs"]["results"]["if"])
        self.assertIn("execute", workflow["jobs"]["results"]["needs"])
        self.assertIn("results", workflow["jobs"]["gate"]["needs"])
        self.assertEqual(workflow["jobs"]["results"]["permissions"]["actions"], "read")

    def test_workspace_defaults_are_portable_and_public_nightly_is_unchanged(self):
        import yaml
        workflow = yaml.load((ROOT / ".github/workflows/test-playbooks-orchestrai-v2.yml").read_text(),
                             Loader=yaml.BaseLoader)
        bridge = yaml.load((ROOT / ".github/workflows/test-playbooks-orchestrai.yml").read_text(),
                           Loader=yaml.BaseLoader)
        for event in ("workflow_dispatch", "workflow_call"):
            self.assertEqual(workflow["on"][event]["inputs"]["workspace"]["default"], "")
        self.assertEqual(bridge["on"]["workflow_dispatch"]["inputs"]["v2_workspace"]["default"], "")
        self.assertEqual(workflow["env"]["ORCHESTRAI_V2_WORKSPACE"],
                         "${{ vars.ORCHESTRAI_V2_WORKSPACE }}")
        self.assertEqual(bridge["jobs"]["v2"]["uses"],
                         "./.github/workflows/test-playbooks-orchestrai-v2.yml")
        self.assertEqual(bridge["jobs"]["v2"]["permissions"]["id-token"], "write")
        self.assertEqual(workflow["jobs"]["execute"]["permissions"]["id-token"], "write")
        self.assertEqual(bridge["on"]["schedule"], [{"cron": "0 1 * * *"}])

    def test_v2_hardware_runs_use_the_standard_per_playbook_jobs(self):
        import yaml
        bridge = yaml.load((ROOT / ".github/workflows/test-playbooks-orchestrai.yml").read_text(),
                           Loader=yaml.BaseLoader)
        self.assertEqual(bridge["on"]["workflow_dispatch"]["inputs"]["use_v2"]["default"], "false")
        # Plan-only validation stays in the dedicated lane; hardware runs go
        # through Detect & Trigger -> per-playbook jobs -> Test Gate.
        self.assertIn("inputs.use_v2 && inputs.v2_prepare_only", bridge["jobs"]["v2"]["if"])
        for name in ("detect-and-trigger", "test-gate"):
            self.assertIn("!(github.event_name == 'workflow_dispatch' && inputs.use_v2 && inputs.v2_prepare_only)",
                          bridge["jobs"][name]["if"])
        self.assertEqual(bridge["jobs"]["detect-and-trigger"]["permissions"]["id-token"], "write")
        trigger = next(st for st in bridge["jobs"]["detect-and-trigger"]["steps"] if st.get("id") == "trigger")
        self.assertIn("inputs.use_v2", trigger["env"]["ORCHESTRAI_USE_V2"])
        self.assertEqual(bridge["jobs"]["v2"]["with"]["locale"], "")
        self.assertIn("inputs.windows_driver", bridge["jobs"]["v2"]["with"]["windows_driver"])

    def test_trigger_batches_returns_each_executor_build_url(self):
        polls = {"a": [{"status": "queued"}, {"status": "running", "pipeline_url": "https://j/b/1"}],
                 "b": [{"status": "error"}]}

        class FakeClient:
            def __init__(self, *_):
                pass

            def start(self, request, _body, _path):
                return request["batch_id"].split("/")[-1]

            def retry(self, _method, path, **_):
                return {"run": {"id": path.rsplit("/", 1)[-1], **polls[path.rsplit("/", 1)[-1]].pop(0)}}

        env = {"ORCHESTRAI_V2_CI_API_URL": "https://o/api/ci/v1", "ORCHESTRAI_V2_OIDC_AUDIENCE": "https://o",
               "ORCHESTRAI_V2_PORTAL_URL": "https://o"}
        with mock.patch.dict(os.environ, env), mock.patch.object(v2.api, "Client", FakeClient), \
                mock.patch.object(v2, "request_for", lambda bid, *_: {"batch_id": bid}), \
                mock.patch.object(v2.api, "start_body", lambda *_: {}), \
                mock.patch.object(v2.time, "sleep", lambda _: None):
            urls = v2.trigger_batches({"x/a": {}, "x/b": {}}, {}, "0" * 40, "ws", "", "/tmp")
        self.assertEqual(urls, {"x/a": "https://j/b/1/"})

    def test_verdict_takes_the_reportportal_launch_from_the_v2_publisher_log(self):
        sys.path.insert(0, str(ROOT / ".github/scripts"))
        import orchestrai_verdict
        log = ("[publish] reportportal project p (credential c): published: "
               "https://rp.example/ui/#p/launches/all/69554\n")
        with mock.patch.object(orchestrai_verdict, "fetch", lambda *_: log):
            self.assertEqual(orchestrai_verdict.rp_url_from_console("https://j/b/1/", "u", "t"),
                             "https://rp.example/ui/#p/launches/all/69554")

    def test_public_validation_runs_the_ported_suite_without_hardware_permissions(self):
        import yaml
        validation = yaml.load((ROOT / ".github/workflows/test-orchestrai-reporting.yml").read_text(),
                               Loader=yaml.BaseLoader)
        job = validation["jobs"]["reporting-tests"]
        self.assertEqual(validation["permissions"], {"contents": "read"})
        self.assertIn("test_orchestrai_v2.py", job["steps"][-1]["run"])

    def test_v2_only_files_do_not_change_the_unrelated_native_harness(self):
        import build_test_matrix as native
        signed = native.harness_files(ROOT)
        self.assertIn(".github/scripts/run_playbook_tests.py", signed)
        for path in (".github/orchestrai/orchestrai_v2.py",
                     ".github/orchestrai/orchestrai_v2_api.py",
                     ".github/orchestrai/V2.md", ".github/tests/test_orchestrai_v2.py"):
            self.assertNotIn(path, signed)
        self.assertNotIn("orchestrai_v2", (ROOT / ".github/workflows/test-playbooks.yml").read_text())


class FakeApi:
    def __init__(self):
        self.now = 0
        self.calls = []
        self.tokens = 0
        self.responses = []
        self.states = ["passed"]
        self.tests = [{"path": "adapter", "outcome": "passed"}]

    def sleep(self, seconds):
        self.now += seconds

    def token(self):
        self.tokens += 1
        segment = base64.urlsafe_b64encode(json.dumps({"exp": 1000 + self.now + 300}).encode()).decode().rstrip("=")
        return f"header.{segment}.signature-{self.tokens}"

    def call(self, method, url, headers, body=None):
        self.calls.append((method, url, dict(headers), copy.deepcopy(body)))
        if url.startswith("https://oidc.example.invalid/"):
            return 200, {"value": self.token()}
        if self.responses:
            answer = self.responses.pop(0)
            if isinstance(answer, Exception):
                raise answer
            return answer
        if method == "POST" and url.endswith("/runs"):
            return 201, {"run": {"id": "run-1", "status": "queued"}}
        if url.endswith("/cancel"):
            return 204, None
        if url.endswith("/tests"):
            return 200, {"tests": self.tests}
        state = self.states.pop(0) if len(self.states) > 1 else self.states[0]
        return 200, {"run": {"id": "run-1", "status": state, "tests_status": "passed",
                             "tests_summary": {"total": 1, "passed": 1}}}


class DirectApiContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = str(Path(self.tmp.name) / "state.json")
        self.fake = FakeApi()
        self.settings = api.Settings("https://ci.example.invalid/api/ci/v1", "https://portal.example.invalid",
                                     "https://portal.example.invalid", "playbooks",
                                     timeout=120, poll=1, start_timeout=20, cleanup_timeout=20)
        self.env = {"GITHUB_REPOSITORY": "amd/playbooks", "GITHUB_RUN_ID": "10",
                    "GITHUB_RUN_ATTEMPT": "1", "GITHUB_JOB": "execute",
                    "ACTIONS_ID_TOKEN_REQUEST_URL": "https://oidc.example.invalid/token?job=abc",
                    "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "runner-secret"}
        self.doc = {"batch_id": "linux/halo", "playbook_sha": "a" * 40, "config": {"control_plane": {
            "workspace": "playbooks", "result_publishers": [{"kind": "reportportal", "credential": "rp",
                "project": "ucicd_project_slim", "required": True,
                "attributes": {"github_run_id": "{GITHUB_RUN_ID}"}}]}},
            "parameters": {"PLAN_JSON": {"sessions": [{"name": "ollama", "tests": ["adapter"],
                "variables": {"PLAYBOOK_REPO": v2.EXTERNAL_REPO, "PLAYBOOK_SHA": "a" * 40}}]},
                "BUILDS_JSON": {"install_scripts": [{"script": "gfx/linux.sh"}], "vars": {"driver": "private"}},
                "MAX_DURATION": 240}}
        self.client = api.Client(self.settings, self.env, self.fake.call, clock=lambda: self.fake.now,
                                 wall_clock=lambda: 1000 + self.fake.now, sleep=self.fake.sleep)
        output = redirect_stdout(io.StringIO())
        output.__enter__()
        self.addCleanup(output.__exit__, None, None, None)

    def post_calls(self):
        return [c for c in self.fake.calls if c[0] == "POST" and c[1].endswith("/runs")]

    def test_end_to_end_oidc_submit_poll_results_and_safe_state(self):
        self.fake.states = ["queued", "running", "passed"]
        result = self.client.execute(self.doc, self.path)
        self.assertEqual(result["verdict"], "success")
        self.assertEqual(result["tests"], self.fake.tests)
        self.assertEqual(len(self.post_calls()), 1)
        _, _, headers, body = self.post_calls()[0]
        self.assertEqual(headers["X-OrchestrAI-Workspace"], "playbooks")
        self.assertIn("Idempotency-Key", headers)
        self.assertEqual(body["require_capacity"], "queue")
        self.assertEqual(body["builds_json"], self.doc["parameters"]["BUILDS_JSON"])
        plan = body["plan_document"]["document"]
        self.assertEqual(plan["sessions"][0]["variables"]["PLAYBOOK_SHA"], "a" * 40)
        self.assertEqual(plan["run_settings"]["max_duration"], 240)
        self.assertEqual(plan["run_settings"]["result_publishers"][0]["attributes"]["github_run_id"], "10")
        state = Path(self.path).read_text()
        self.assertTrue(json.loads(state)["finished"])
        for secret in ("runner-secret", "private", "Bearer", "signature"):
            self.assertNotIn(secret, state)
        self.assertEqual(Path(self.path).stat().st_mode & 0o777, 0o600)

    def test_native_only_submit_retains_results_without_external_exports(self):
        del self.doc["config"]["control_plane"]["result_publishers"]
        self.doc["parameters"]["PLAN_JSON"]["run_settings"] = {
            "result_publishers": [{"kind": "reportportal", "credential": "legacy"}]}
        result = self.client.execute(self.doc, self.path)
        self.assertEqual(result["verdict"], "success")
        settings = self.post_calls()[0][3]["plan_document"]["document"]["run_settings"]
        self.assertNotIn("result_publishers", settings)
        self.assertEqual(result["tests"], self.fake.tests)
        self.assertTrue(any(url.endswith("/tests") for _, url, _, _ in self.fake.calls))

    def test_lost_start_and_503_reuse_the_exact_body_and_key(self):
        self.fake.responses = [api.ApiError("lost reply", True), (503, {"error": {"code": "unavailable"}}),
                               (409, {"error": {"code": "idempotency_in_progress"}})]
        self.assertEqual(self.client.execute(self.doc, self.path)["verdict"], "success")
        calls = self.post_calls()
        self.assertEqual(len(calls), 4)
        self.assertEqual(len({c[2]["Idempotency-Key"] for c in calls}), 1)
        self.assertTrue(all(c[3] == calls[0][3] for c in calls))

    def test_permission_refusal_is_not_retried_or_cancelled(self):
        self.fake.responses = [(403, {"error": {"code": "no_matching_rule", "message": "private"}})]
        result = self.client.execute(self.doc, self.path)
        self.assertIn("no_matching_rule", result["error"])
        self.assertNotIn("private", result["error"])
        self.assertEqual(len(self.post_calls()), 1)
        self.assertFalse(any(c[1].endswith("/cancel") for c in self.fake.calls))

    def test_revoked_permission_after_lost_start_does_not_mark_run_finished(self):
        denial = (403, {"error": {"code": "no_matching_rule"}})
        self.fake.responses = [api.ApiError("lost start response", True), denial, denial]
        result = self.client.execute(self.doc, self.path)
        self.assertEqual(result["verdict"], "failure")
        self.assertFalse(json.loads(Path(self.path).read_text())["finished"])
        self.assertEqual(len(self.post_calls()), 3)
        self.assertEqual(len({c[2]["Idempotency-Key"] for c in self.post_calls()}), 1)

    def test_token_refresh_before_expiry_and_on_expired_response(self):
        first = self.client.bearer()
        self.fake.now += 245
        self.assertNotEqual(self.client.bearer(), first)
        self.fake.responses = [(401, {"error": {"code": "token_expired"}})]
        self.client.call("GET", "/runs/run-1")
        self.assertEqual(self.fake.tokens, 3)
        self.assertEqual(len([c for c in self.fake.calls if c[1].endswith("/runs/run-1")]), 2)

    def test_rate_limit_and_poll_outage_recover(self):
        self.fake.responses = [(429, {"error": {"code": "rate_limited"}}),
                               (201, {"run": {"id": "run-1"}}),
                               api.ApiError("transport failed", True), (502, None)]
        self.assertEqual(self.client.execute(self.doc, self.path)["verdict"], "success")

    def test_failed_test_result_is_preserved(self):
        self.fake.states = ["unstable"]
        self.fake.tests = [{"path": "adapter", "outcome": "failed", "error": "model allocation failed"}]
        result = self.client.execute(self.doc, self.path)
        self.assertEqual(result["verdict"], "failure")
        self.assertIn("model allocation failed", v2.result_report(result, "linux/halo"))

    def test_controller_rejects_green_summary_with_missing_or_wrong_actual_records(self):
        doc_path = Path(self.tmp.name) / "request.json"
        doc_path.write_text(json.dumps(self.doc))
        args = SimpleNamespace(request=str(doc_path), state=self.path,
                               results=str(Path(self.tmp.name) / "results"))
        for tests in ([], [{"path": "wrong-adapter", "outcome": "passed"}],
                      [{"path": "adapter", "outcome": "skipped"}],
                      [{"path": ["invalid"], "outcome": "passed"}]):
            result = {"run_id": "run-1", "verdict": "success", "status": "passed",
                      "tests_summary": {"total": 1, "passed": 1}, "tests": tests}
            with mock.patch.object(api.Settings, "from_env", return_value=self.settings), \
                    mock.patch.object(api, "Client") as client:
                client.return_value.execute.return_value = result
                with self.assertRaisesRegex(ValueError, "exact requested passed adapters"):
                    v2.execute(args)
            saved = json.loads((Path(args.results) / "result.json").read_text())
            self.assertEqual(saved["verdict"], "failure")
            self.assertEqual(saved["tests"], tests)

    def test_controller_accepts_exact_adapters_and_saves_external_identity(self):
        doc_path = Path(self.tmp.name) / "request.json"
        doc_path.write_text(json.dumps(self.doc))
        args = SimpleNamespace(request=str(doc_path), state=self.path,
                               results=str(Path(self.tmp.name) / "results"))
        self.doc["playbook_sha"] = "a" * 40
        doc_path.write_text(json.dumps(self.doc))
        result = {"run_id": "run-1", "verdict": "success", "status": "passed",
                  "tests_summary": {"total": 1, "passed": 1}, "tests": self.fake.tests}
        with mock.patch.object(api.Settings, "from_env", return_value=self.settings), \
                mock.patch.object(api, "Client") as client:
            client.return_value.execute.return_value = result
            v2.execute(args)
        identity = json.loads((Path(args.results) / "identity.json").read_text())
        self.assertEqual(identity["playbook_repo"], "https://github.com/amd/playbooks")
        self.assertEqual(identity["playbook_sha"], "a" * 40)

    def test_timeout_requests_cancellation_without_claiming_release(self):
        self.fake.states = ["running"]
        result = self.client.execute(self.doc, self.path)
        self.assertEqual(result["verdict"], "failure")
        self.assertIn("budget", result["error"])
        state = json.loads(Path(self.path).read_text())
        self.assertTrue(state["cancel_requested"])
        self.assertFalse(state["finished"])
        self.assertTrue(any(c[1].endswith("/cancel") for c in self.fake.calls))

    def test_interruption_during_start_replays_identity_then_cancels(self):
        self.fake.responses = [api.Interrupted("SIGINT during start")]
        result = self.client.execute(self.doc, self.path)
        self.assertEqual(result["status"], "cancelled")
        calls = self.post_calls()
        self.assertEqual(len(calls), 2)
        self.assertEqual(calls[0][2]["Idempotency-Key"], calls[1][2]["Idempotency-Key"])
        self.assertEqual(calls[0][3], calls[1][3])
        self.assertTrue(json.loads(Path(self.path).read_text())["cancel_requested"])

    def test_cleanup_recovers_unknown_start_and_is_repeatable(self):
        body = api.start_body(self.doc, self.env)
        state = self.client.identity(self.doc, body)
        state["attempted"] = True
        api.save_state(self.path, state)
        for _ in range(2):
            self.client.cancel(self.doc, body, self.path)
        self.assertEqual(len(self.post_calls()), 1)
        self.assertEqual(len([c for c in self.fake.calls if c[1].endswith("/cancel")]), 2)

    def test_cleanup_cannot_cancel_another_job_attempt_batch_or_endpoint(self):
        body = api.start_body(self.doc, self.env)
        state = self.client.identity(self.doc, body)
        state.update(attempted=True, run_id="run-1")
        for key in ("key", "workspace", "ci_api", "request_hash"):
            wrong = {**state, key: "another"}
            api.save_state(self.path, wrong)
            with self.assertRaisesRegex(api.ApiError, "different"):
                self.client.cancel(self.doc, body, self.path)
        self.assertEqual(self.fake.calls, [])

    def test_finished_or_missing_state_does_not_cancel_or_authenticate(self):
        self.client.cancel(self.doc, api.start_body(self.doc, self.env), self.path)
        state = self.client.identity(self.doc, api.start_body(self.doc, self.env))
        state.update(finished=True, run_id="run-1", attempted=True)
        api.save_state(self.path, state)
        self.client.cancel(self.doc, api.start_body(self.doc, self.env), self.path)
        self.assertEqual(self.fake.calls, [])

    def test_missing_oidc_and_endpoint_configuration_fail_before_start(self):
        with self.assertRaisesRegex(api.ApiError, "CI_API_URL"):
            api.Settings.from_env("playbooks", {})
        self.client.env = {}
        with self.assertRaisesRegex(api.ApiError, "id-token: write"):
            self.client.bearer()
        self.assertEqual(self.fake.calls, [])

    def test_url_validation_and_redirects_cannot_leak_bearers(self):
        for url in ("http://ci.example.invalid", "https://user:pass@ci.example.invalid", "https://ci.example.invalid?x=1"):
            with self.assertRaises(api.ApiError):
                api.https_url(url, "endpoint")
        self.assertIsNone(api.NoRedirect().redirect_request(None, None, 302, "redirect", {},
                                                          "https://untrusted.example.invalid"))

    def test_http_preserves_error_codes_and_discards_non_json_without_echo(self):
        response = error.HTTPError("https://ci.example.invalid", 403, "Forbidden", {},
                                   io.BytesIO(b'{"error":{"code":"no_matching_rule"},"request_id":"request-1"}'))
        opener = mock.Mock()
        opener.open.side_effect = response
        with mock.patch.object(api.request, "build_opener", return_value=opener):
            status, payload = api.http("GET", "https://ci.example.invalid", {})
        self.assertEqual(status, 403)
        self.assertEqual(api.code_of(payload), "no_matching_rule")

    def test_current_error_envelope_reports_exact_rejection_and_request_id(self):
        self.fake.responses = [(409, {"error": {"code": "credentials_missing",
            "message": "playbooks-reportportal cannot be used by Publish results"}, "request_id": "request-42"})]
        result = self.client.execute(self.doc, self.path)
        self.assertIn("credentials_missing", result["error"])
        self.assertIn("cannot be used by Publish results", result["error"])
        self.assertIn("request_id=request-42", result["error"])
        self.assertEqual(len(self.post_calls()), 1)

    def test_current_and_legacy_envelopes_and_plain_details_are_supported(self):
        for payload in ({"error": {"code": "conflict", "message": "reason"}},
                        {"detail": {"code": "conflict", "message": "reason"}},
                        {"code": "conflict", "message": "reason"}):
            self.assertEqual(api.code_of(payload), "conflict")
            self.assertIn("reason", self.client.diagnostic(409, payload))
        self.assertIn("legacy reason", self.client.diagnostic(409, {"detail": "legacy reason"}))
        self.assertEqual(api.code_of(None), "")

    def test_diagnostics_mask_tokens_provisioning_values_and_query_credentials(self):
        self.client.token = "signed-token"
        self.client.redactions += ["driver-private-coordinate"]
        payload = {"error": {"code": "invalid_request", "message":
            "runner-secret signed-token driver-private-coordinate https://example.invalid?token=secretvalue "
            "Bearer anothersecret\n::error::ignored"}, "request_id": "valid-42"}
        text = self.client.diagnostic(409, payload)
        for secret in ("runner-secret", "signed-token", "driver-private-coordinate", "secretvalue", "anothersecret"):
            self.assertNotIn(secret, text)
        self.assertNotIn("\n", text)
        self.assertIn("request_id=valid-42", text)

    def test_workflow_has_no_library_checkout_or_secret_requirement(self):
        workflow = (ROOT / ".github/workflows/test-playbooks-orchestrai-v2.yml").read_text()
        for old in ("ORCHESTRAI_V2_LIBRARY_TOKEN", "SSH_DEPLOY_KEY", "ci-actions-lib", "ci/requirements.txt"):
            self.assertNotIn(old, workflow)
        for new in ("ORCHESTRAI_V2_CI_API_URL", "ORCHESTRAI_V2_OIDC_AUDIENCE", "ORCHESTRAI_V2_PORTAL_URL"):
            self.assertIn(new, workflow)

    def test_body_read_disconnect_is_a_retryable_error(self):
        opener = mock.MagicMock()
        response = opener.open.return_value
        response.read.side_effect = ConnectionResetError("sensitive URL")
        with mock.patch.object(api.request, "build_opener", return_value=opener):
            with self.assertRaises(api.ApiError) as exc:
                api.http("GET", "https://ci.example.invalid", {})
        self.assertTrue(exc.exception.transient)
        self.assertNotIn("sensitive", str(exc.exception))

    def test_real_http_and_process_signal_cancel_the_saved_run(self):
        fake = self.fake
        started = threading.Event()
        calls = []

        class Handler(BaseHTTPRequestHandler):
            def log_message(self, *_args):
                pass

            def dispatch(self):
                raw = self.rfile.read(int(self.headers.get("Content-Length", 0)))
                body = json.loads(raw) if raw else None
                calls.append((self.command, self.path, dict(self.headers), body))
                if self.path.startswith("/token"):
                    payload = {"value": fake.token()}
                elif self.path.endswith("/cancel"):
                    payload = {"run": {"id": "run-1", "status": "cancelled"}}
                else:
                    started.set()
                    payload = {"run": {"id": "run-1", "status": "running"}}
                encoded = json.dumps(payload).encode()
                self.send_response(200)
                self.send_header("Content-Type", "application/json")
                self.send_header("Content-Length", str(len(encoded)))
                self.end_headers()
                self.wfile.write(encoded)

            do_GET = dispatch
            do_POST = dispatch

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        thread = threading.Thread(target=server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(server.server_close)
        self.addCleanup(server.shutdown)
        doc_path = Path(self.tmp.name) / "request.json"
        doc_path.write_text(json.dumps(self.doc))
        code = """
import json, os, sys
sys.path.insert(0, sys.argv[1])
import orchestrai_v2_api as api
doc = json.load(open(sys.argv[2]))
def local_http(method, url, headers, body=None):
    from urllib.parse import urlsplit
    parts = urlsplit(url)
    url = sys.argv[4] + parts.path + ('?' + parts.query if parts.query else '')
    return api.http(method, url, headers, body)
settings = api.Settings('https://ci.example.invalid/api/ci/v1', 'https://portal.example.invalid',
                       'https://portal.example.invalid', 'playbooks', poll=1)
result = api.Client(settings, dict(os.environ), transport=local_http).execute(doc, sys.argv[3])
print('RESULT=' + json.dumps(result))
"""
        process = subprocess.Popen([sys.executable, "-c", code, str(ROOT / ".github/orchestrai"),
                                    str(doc_path), self.path, f"http://127.0.0.1:{server.server_port}"],
                                   env={**os.environ, **self.env}, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                   text=True)
        try:
            self.assertTrue(started.wait(10), "child did not start its fake V2 run")
            deadline = time.monotonic() + 10
            while not Path(self.path).is_file() or not json.loads(Path(self.path).read_text()).get("run_id"):
                self.assertLess(time.monotonic(), deadline)
                time.sleep(0.01)
            process.send_signal(signal.SIGINT)
            stdout, stderr = process.communicate(timeout=10)
        finally:
            if process.poll() is None:
                process.kill()
                process.communicate()
        self.assertEqual(process.returncode, 0, stderr)
        self.assertIn('"status": "cancelled"', stdout)
        self.assertEqual(len([c for c in calls if c[0] == "POST" and c[1] == "/api/ci/v1/runs"]), 1)
        cancel = [c for c in calls if c[1].endswith("/cancel")]
        self.assertEqual(len(cancel), 1)
        self.assertEqual({k.lower(): v for k, v in cancel[0][2].items()}["x-orchestrai-workspace"], "playbooks")
        self.assertTrue(json.loads(Path(self.path).read_text())["cancel_requested"])


if __name__ == "__main__":
    unittest.main()
