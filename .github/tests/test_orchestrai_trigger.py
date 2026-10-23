#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for orchestrai_trigger.py: Control Plane submission, the
reporting switch (reportportal | api), config validation and scheduling policy.

Usage:
    python3 .github/tests/test_orchestrai_trigger.py
"""

import contextlib
import io
import json
import os
import sys
import unittest
from unittest import mock

import yaml

HERE = os.path.dirname(os.path.abspath(__file__))
GITHUB_DIR = os.path.dirname(HERE)
SCRIPTS_DIR = os.path.join(GITHUB_DIR, "scripts")
CONFIG = os.path.join(GITHUB_DIR, "orchestrai-config.yml")
sys.path.insert(0, SCRIPTS_DIR)

import orchestrai_trigger as trigger  # noqa: E402

BATCH = {"platform": "linux", "arch": "stx", "gfx": "gfx1150",
         "tags": ["apu_stx"], "playbooks": ["gaia-agents"]}


def load_config():
    with open(CONFIG) as f:
        return yaml.safe_load(f)


CP_ENV = {"ORCHESTRAI_V2_CI_API_URL": "https://cp.example/api/ci/v1",
          "ORCHESTRAI_V2_OIDC_AUDIENCE": "https://cp.example",
          "ORCHESTRAI_V2_PORTAL_URL": "https://cp.example", "ORCHESTRAI_V2_WORKSPACE": "ws",
          "ACTIONS_ID_TOKEN_REQUEST_URL": "https://oidc.example/token?x=1",
          "ACTIONS_ID_TOKEN_REQUEST_TOKEN": "req", "GITHUB_REPOSITORY": "amd/playbooks",
          "GITHUB_RUN_ID": "77", "GITHUB_RUN_ATTEMPT": "1"}


class FakeApi:
    """Stands in for http_json: the OIDC endpoint plus scripted CI API answers."""

    def __init__(self, *answers):
        self.answers, self.calls = list(answers), []

    def __call__(self, method, url, headers, body=None):
        if url.startswith("https://oidc.example/"):
            return 200, {"value": "oidc-jwt"}
        self.calls.append((method, url, headers, body))
        answer = self.answers.pop(0)
        if isinstance(answer, Exception):
            raise answer
        return answer


class ControlPlaneApi(unittest.TestCase):

    def setUp(self):
        patches = [mock.patch.dict(os.environ, CP_ENV, clear=True),
                   mock.patch.object(trigger.time, "sleep"),
                   contextlib.redirect_stdout(io.StringIO()),
                   contextlib.redirect_stderr(io.StringIO())]
        for p in patches:
            p.__enter__()
            self.addCleanup(p.__exit__, None, None, None)
        self.cp = trigger.control_plane()
        self.plan = trigger.make_plan(dict(BATCH, playbooks=["gaia-agents", "cvml"]), "refs/heads/main",
                                      load_config(), 1, "https://github.com/amd/playbooks", "a" * 40,
                                      "https://index.example")

    def start(self, fake, publisher="rp-cred", platform="linux"):
        with mock.patch.object(trigger, "http_json", fake):
            return trigger.start_run(self.cp, f"{platform}/stx", self.plan, {"install_scripts": []},
                                     platform, publisher, "a" * 40)

    def test_start_sends_one_session_per_playbook_with_oidc_and_workspace(self):
        fake = FakeApi((201, {"run": {"id": "r1"}}))
        self.assertEqual(self.start(fake), "r1")
        method, url, headers, body = fake.calls[0]
        self.assertEqual((method, url), ("POST", "https://cp.example/api/ci/v1/runs"))
        self.assertEqual(headers["Authorization"], "Bearer oidc-jwt")
        self.assertEqual(headers["X-OrchestrAI-Workspace"], "ws")
        sessions = body["plan_document"]["document"]["sessions"]
        self.assertEqual([s["name"] for s in sessions], ["playbook-gaia-agents", "playbook-cvml"])
        self.assertEqual({s["variables"]["PLAYBOOK_SHA"] for s in sessions}, {"a" * 40})
        self.assertEqual(sessions[0]["machine_tags"], ["apu_stx"])
        self.assertEqual(body["require_capacity"], "queue")

    def test_reportportal_publisher_is_required_and_api_mode_has_none(self):
        fake = FakeApi((201, {"run": {"id": "r1"}}), (201, {"run": {"id": "r2"}}))
        self.start(fake)
        self.start(fake, publisher="")
        rp = fake.calls[0][3]["plan_document"]["document"]["run_settings"]["result_publishers"][0]
        self.assertEqual((rp["credential"], rp["required"], rp["attributes"]["github_run_id"]),
                         ("rp-cred", True, "77"))
        self.assertNotIn("result_publishers", fake.calls[1][3]["plan_document"]["document"]["run_settings"])

    def test_windows_image_override(self):
        fake = FakeApi((201, {"run": {"id": "r1"}}))
        with mock.patch.dict(os.environ, {"ORCHESTRAI_V2_WINDOWS_IMAGE": "windows/win11-x"}):
            self.start(fake, platform="windows")
        self.assertEqual(fake.calls[0][3]["plan_document"]["document"]["run_settings"]["os_image"],
                         "windows/win11-x")

    def test_lost_start_is_retried_with_the_same_idempotency_key(self):
        fake = FakeApi(OSError("reset"), (503, None), (201, {"run": {"id": "r1"}}))
        self.assertEqual(self.start(fake), "r1")
        keys = {c[2]["Idempotency-Key"] for c in fake.calls}
        self.assertEqual(len(fake.calls), 3)
        self.assertEqual(len(keys), 1)

    def test_a_refusal_is_not_retried_and_reports_code_and_request_id(self):
        fake = FakeApi((403, {"error": {"code": "no_matching_rule", "message": "no rule"},
                              "request_id": "abc"}))
        with self.assertRaisesRegex(ValueError, "403 no_matching_rule: no rule.*request_id=abc"):
            self.start(fake)
        self.assertEqual(len(fake.calls), 1)

    def test_only_a_build_url_is_handed_on_and_errors_carry_their_reason(self):
        fake = FakeApi((200, {"run": {"id": "a", "status": "queued", "pipeline_url": "https://j/queue/item/7/"}}),
                       (200, {"run": {"id": "b", "status": "error", "error": "no image"}}),
                       (200, {"run": {"id": "a", "status": "running", "pipeline_url": "https://j/job/p/9"}}))
        err = io.StringIO()
        with mock.patch.object(trigger, "http_json", fake), contextlib.redirect_stderr(err):
            urls = trigger.await_builds(self.cp, {"x/a": "a", "x/b": "b"})
        self.assertEqual(urls, {"x/a": "https://j/job/p/9/"})
        self.assertIn("run b ended error without a build: no image", err.getvalue())


class ReportingSwitch(unittest.TestCase):
    """reportportal adds the required ReportPortal publisher; api does not."""

    def run_main(self, reporting, credential="playbooks-reportportal"):
        env = {**CP_ENV, "BATCHES_JSON": json.dumps({"linux/stx": BATCH}),
               "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://index.example",
               "ORCHESTRAI_THEROCK_URL": "https://therock.example/t.tar.gz",
               "ORCHESTRAI_PLAYBOOK_SHA": "a" * 40,
               "ORCHESTRAI_REPORTING": reporting, "ORCHESTRAI_V2_RP_CREDENTIAL": credential}
        start = mock.Mock(return_value="r1")
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["trigger", "--config", CONFIG]), \
                mock.patch.object(trigger, "start_run", start), \
                mock.patch.object(trigger, "await_builds", return_value={"linux/stx": "https://j/1/"}), \
                contextlib.redirect_stderr(io.StringIO()):
            trigger.main()
        return start.call_args.args[5]

    def test_reportportal_is_the_default_and_exports(self):
        self.assertEqual(self.run_main(""), "playbooks-reportportal")
        self.assertEqual(self.run_main("reportportal"), "playbooks-reportportal")

    def test_api_keeps_results_in_orchestrai(self):
        self.assertEqual(self.run_main("api"), "")

    def test_reportportal_without_its_credential_fails_before_submitting(self):
        with self.assertRaises(SystemExit):
            self.run_main("reportportal", credential="")
        with self.assertRaises(SystemExit):
            self.run_main("both")


class MachinesPerBatch(unittest.TestCase):
    """A batch never asks for more machines than it has playbooks."""

    def run_main(self, mphg, batches):
        env = {**CP_ENV, "BATCHES_JSON": json.dumps(batches), "MACHINES_PER_HW_GROUP": str(mphg),
               "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://index.example",
               "ORCHESTRAI_THEROCK_URL": "https://therock.example/t.tar.gz",
               "ORCHESTRAI_PLAYBOOK_SHA": "a" * 40, "ORCHESTRAI_REPORTING": "api"}
        start, err = mock.Mock(return_value="r1"), io.StringIO()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["trigger", "--config", CONFIG]), \
                mock.patch.object(trigger, "start_run", start), \
                mock.patch.object(trigger, "await_builds",
                                  side_effect=lambda _cp, runs, *_: {b: "https://j/1/" for b in runs}), \
                contextlib.redirect_stderr(err):
            trigger.main()
        requested = {c.args[1]: c.args[2]["run_settings"]["machines_per_hw_group"]
                     for c in start.call_args_list}
        return requested, err.getvalue()

    def test_machines_are_capped_at_the_playbook_count(self):
        one = dict(BATCH, playbooks=["gaia-agents"])
        five = dict(BATCH, playbooks=["gaia-agents", "lemonade-getting-started", "ollama-getting-started", "open-webui-chat", "lmstudio-rocm-llms"])
        requested, log = self.run_main(2, {"linux/one": one, "linux/five": five})
        self.assertEqual(requested, {"linux/one": 1, "linux/five": 2})
        self.assertIn("2 batch(es), 3 machine(s) requested (machines_per_hw_group=2)", log)

    def test_the_default_is_one_machine_per_batch(self):
        requested, log = self.run_main(1, {"linux/stx": BATCH})
        self.assertEqual(requested, {"linux/stx": 1})
        self.assertIn("1 batch(es), 1 machine(s) requested", log)


class WorkflowWiring(unittest.TestCase):
    """Same jobs as before; Detect & Trigger and !orc can request OIDC tokens."""

    def load(self, name):
        with open(os.path.join(GITHUB_DIR, "workflows", name)) as f:
            return yaml.load(f, Loader=yaml.BaseLoader)

    def test_jobs_reporting_input_and_oidc_permission(self):
        wf = self.load("test-playbooks-orchestrai.yml")
        self.assertEqual(list(wf["jobs"]), ["detect-and-trigger", "test-playbooks",
                                            "test-localized-playbooks", "test-gate"])
        reporting = wf["on"]["workflow_dispatch"]["inputs"]["reporting"]
        self.assertEqual((reporting["default"], reporting["options"]), ("reportportal", ["reportportal", "api"]))
        self.assertEqual(wf["jobs"]["detect-and-trigger"]["permissions"]["id-token"], "write")
        step = next(s for s in wf["jobs"]["detect-and-trigger"]["steps"] if s.get("id") == "trigger")
        self.assertIn("inputs.reporting", step["env"]["ORCHESTRAI_REPORTING"])
        self.assertEqual(self.load("orchestrai-pr-command.yml")["jobs"]["command"]["permissions"]["id-token"],
                         "write")


class AcquireTimeoutValidation(unittest.TestCase):

    def errors_for(self, **run_settings):
        cfg = load_config()
        cfg["run_settings"].update(run_settings)
        return [e for e in trigger.validate_config(cfg, {"b": BATCH}) if "acquire_timeout" in e]

    def test_the_shipped_config_is_valid(self):
        self.assertEqual(self.errors_for(), [])

    def test_non_positive_or_non_integer_values_are_rejected(self):
        for bad in (0, -5, "60", True, 60.5, None):
            self.assertTrue(self.errors_for(acquire_timeout=bad), bad)

    def test_a_wait_longer_than_the_build_limit_is_allowed(self):
        # The Control Plane waits for machines before the build starts, so the
        # wait no longer comes out of max_duration.
        self.assertEqual(self.errors_for(acquire_timeout=360, max_duration=240), [])

    def test_the_shipped_wait_is_six_hours_and_jobs_outlast_it(self):
        cfg = load_config()
        self.assertEqual(cfg["run_settings"]["acquire_timeout"], 360)
        need = (cfg["run_settings"]["acquire_timeout"] * 60 + trigger.BUILD_WAIT_MARGIN) / 60
        for name, job in (("test-playbooks-orchestrai.yml", "detect-and-trigger"),
                          ("orchestrai-pr-command.yml", "command")):
            with open(os.path.join(GITHUB_DIR, "workflows", name)) as f:
                limit = int(yaml.safe_load(f)["jobs"][job]["timeout-minutes"])
            self.assertGreater(limit, need, name)

    def test_main_waits_for_builds_as_long_as_the_control_plane_queues(self):
        env = {**CP_ENV, "BATCHES_JSON": json.dumps({"linux/stx": BATCH}),
               "ORCHESTRAI_ROCM_MULTI_ARCH_INDEX_URL": "https://index.example",
               "ORCHESTRAI_THEROCK_URL": "https://therock.example/t.tar.gz",
               "ORCHESTRAI_PLAYBOOK_SHA": "a" * 40, "ORCHESTRAI_REPORTING": "api"}
        wait = mock.Mock(return_value={"linux/stx": "https://j/1/"})
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["trigger", "--config", CONFIG]), \
                mock.patch.object(trigger, "start_run", return_value="r1"), \
                mock.patch.object(trigger, "await_builds", wait), \
                contextlib.redirect_stderr(io.StringIO()):
            trigger.main()
        self.assertEqual(wait.call_args.args[2], 360 * 60 + trigger.BUILD_WAIT_MARGIN)

    def test_no_overall_limit_means_no_comparison(self):
        self.assertEqual(self.errors_for(acquire_timeout=600, max_duration=0), [])


class SchedulingPolicy(unittest.TestCase):

    def test_fixed_qwen_agent_playbooks_skip_stx_and_pin_krk_to_64gb(self):
        from orchestrai_matrix import build

        cfg = load_config()
        cfg["device_to_tags"] = {
            device: [f"fixture-{device}"] for device in cfg["device_to_gfx"]
        }
        affected = ("github-slack-development-digest", "openhands-getting-started")
        baseline_cfg = load_config()
        baseline_cfg["device_to_tags"] = cfg["device_to_tags"]
        for playbook in affected:
            baseline_cfg["skip_playbook_devices"].pop(playbook, None)

        old_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(GITHUB_DIR))
            matrix, batches = build([*affected, "ollama-getting-started"], cfg)
            baseline, _ = build([*affected, "ollama-getting-started"], baseline_cfg)
        finally:
            os.chdir(old_cwd)

        def combinations(entries):
            return {(e["playbook"], e["platform"], e["arch"]) for e in entries}

        excluded = {(pb, os_name, "stx") for pb in affected
                    for os_name in ("linux", "windows")}
        self.assertEqual(combinations(matrix), combinations(baseline) - excluded)
        self.assertTrue(excluded <= combinations(baseline))
        for platform in ("linux", "windows"):
            self.assertEqual(batches[f"{platform}/stx"]["playbooks"],
                             ["ollama-getting-started"])
            self.assertEqual(batches[f"{platform}/krk+ram_64gb"]["playbooks"],
                             list(affected))


class OpenHandsProvisioning(unittest.TestCase):

    def test_windows_openhands_enables_wsl_without_installer_coordinates(self):
        """The Docker Desktop installer is the dependency's own business: this
        repository neither requires nor forwards its location."""
        cfg = {
            "provisioning": {
                "windows_install_scripts": [],
                "windows_driver": {"source": "driver", "copy": "direct"},
            },
            "extra_install_scripts": load_config()["extra_install_scripts"],
        }
        batch = {
            "platform": "windows",
            "arch": "halo",
            "playbooks": ["openhands-getting-started"],
        }
        builds, missing = trigger.make_builds(batch, cfg)
        self.assertEqual(missing, [])
        self.assertEqual(
            builds["install_scripts"],
            [{
                "script": "InstallationScripts/gfx/windows-wsl.ps1",
                "reboot_after": True,
            }],
        )
        self.assertEqual(builds["vars"], {"driver_source": "driver", "driver_copy": "direct"})

    def test_installer_repository_variables_are_not_read(self):
        cfg = {"pipeline": {}, "provisioning": {}}
        env = {
            "ORCHESTRAI_DOCKER_DESKTOP_INSTALLER_URL": "https://example.invalid/docker.exe",
            "ORCHESTRAI_DOCKER_DESKTOP_INSTALLER_SHA256": "b" * 64,
        }
        with mock.patch.dict(os.environ, env, clear=False):
            trigger.apply_env_overrides(cfg)
        self.assertFalse([k for k in cfg["provisioning"] if "docker" in k])

    def test_linux_openhands_does_not_run_windows_wsl_provisioning(self):
        cfg = {
            "device_families": {"stx": "ryzen_apu"},
            "provisioning": {
                "linux_install_scripts": [],
                "therock_url": "https://example.invalid/therock.tar.gz",
            },
            "extra_install_scripts": load_config()["extra_install_scripts"],
        }
        batch = {
            "platform": "linux",
            "arch": "stx",
            "playbooks": ["openhands-getting-started"],
        }
        builds, missing = trigger.make_builds(batch, cfg)
        self.assertEqual(missing, [])
        self.assertEqual(builds["install_scripts"], [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
