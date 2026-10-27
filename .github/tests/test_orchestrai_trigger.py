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

    def test_a_device_can_run_its_playbooks_as_another(self):
        cfg = dict(load_config(), device_runs_as={"grgh": "halo"})
        def device(arch):
            plan = trigger.make_plan(dict(BATCH, arch=arch, tags=["t"]), "refs/heads/main", cfg, 1,
                                     "https://github.com/amd/playbooks", "a" * 40, "https://index.example")
            return {(g["variables"]["PLAYBOOK_DEVICE"], tuple(g["maas_tags"])) for g in plan["groups"]}
        self.assertEqual(device("grgh"), {("halo", ("t",))})  # machines still chosen by grgh's tags
        self.assertEqual(device("stx"), {("stx", ("t",))})
        self.assertEqual(load_config()["device_runs_as"], {"grgh": "halo"})

    def test_a_device_image_reaches_only_that_device_and_platform(self):
        cfg = dict(load_config(), device_os_images={"grgh": {"windows": "windows/custom-x"}})
        def sessions(arch, platform):
            plan = trigger.make_plan(dict(BATCH, arch=arch, platform=platform), "refs/heads/main", cfg, 1,
                                     "https://github.com/amd/playbooks", "a" * 40, "https://index.example")
            fake = FakeApi((201, {"run": {"id": "r1"}}))
            with mock.patch.object(trigger, "http_json", fake):
                trigger.start_run(self.cp, f"{platform}/{arch}", plan, {}, platform, "", "a" * 40)
            return {s["os_image"] for s in fake.calls[0][3]["plan_document"]["document"]["sessions"]}
        self.assertEqual(sessions("grgh", "windows"), {"windows/custom-x"})
        self.assertEqual(sessions("grgh", "linux"), {"ubuntu"})
        self.assertEqual(sessions("stx", "windows"), {"windows"})

    def test_device_sites_reach_every_session_of_that_device_only(self):
        cfg = load_config()
        # Every configured device stays in Markham.
        self.assertTrue(cfg["device_site_ids"])
        self.assertEqual({tuple(v) for v in cfg["device_site_ids"].values()},
                         {("maas-mkm-mnb", "maas-mkm-cs")})
        cfg["device_site_ids"] = {"krk": ["maas-mkm-mnb", "maas-mkm-cs"]}  # stx: any site
        krk = trigger.make_plan(dict(BATCH, arch="krk", playbooks=["gaia-agents", "cvml"]), "refs/heads/main",
                                cfg, 1, "https://github.com/amd/playbooks", "a" * 40, "https://index.example")
        self.assertEqual({tuple(g["site_ids"]) for g in krk["groups"]}, {("maas-mkm-mnb", "maas-mkm-cs")})
        stx = trigger.make_plan(BATCH, "refs/heads/main", cfg, 1, "https://github.com/amd/playbooks",
                                "a" * 40, "https://index.example")
        self.assertNotIn("site_ids", stx["groups"][0])
        fake = FakeApi((201, {"run": {"id": "r1"}}), (201, {"run": {"id": "r2"}}))
        with mock.patch.object(trigger, "http_json", fake):
            trigger.start_run(self.cp, "linux/krk", krk, {}, "linux", "", "a" * 40)
            trigger.start_run(self.cp, "linux/stx", stx, {}, "linux", "", "a" * 40)
        sessions = [c[3]["plan_document"]["document"]["sessions"] for c in fake.calls]
        self.assertEqual({tuple(s["site_ids"]) for s in sessions[0]}, {("maas-mkm-mnb", "maas-mkm-cs")})
        self.assertNotIn("site_ids", sessions[1][0])

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
            urls = trigger.await_builds(self.cp, {"x/a": "a", "x/b": "b"}, 3600)
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
                mock.patch.object(trigger, "await_builds", side_effect=AssertionError("Detect must not wait")), \
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
        self.wait = mock.Mock()
        with mock.patch.dict(os.environ, env, clear=True), \
                mock.patch.object(sys, "argv", ["trigger", "--config", CONFIG]), \
                mock.patch.object(trigger, "start_run", start), \
                mock.patch.object(trigger, "await_builds", self.wait), \
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

    def test_detect_and_trigger_does_not_wait_for_builds(self):
        # Each Test job waits for its own batch (--await-build).
        self.run_main(1, {"linux/stx": BATCH})
        self.wait.assert_not_called()


class AwaitBuild(unittest.TestCase):
    """--await-build: one Test job waits for its own batch's build."""

    def run_it(self, run_id, found):
        out = io.StringIO()
        with mock.patch.dict(os.environ, {**CP_ENV, "RUN_ID": run_id, "BATCH_ID": "linux/stx",
                                          "GITHUB_OUTPUT": os.devnull}), \
                mock.patch.object(trigger, "await_builds", return_value=found) as wait, \
                mock.patch.object(trigger, "acquire_timeout_minutes", return_value=360), \
                mock.patch("builtins.open", mock.mock_open()) as opened, \
                contextlib.redirect_stderr(out):
            trigger.await_build_main(CONFIG)
        written = "".join(c.args[0] for c in opened().write.call_args_list)
        return wait, written, out.getvalue()

    def test_writes_the_build_url_for_this_batch_only(self):
        wait, written, _ = self.run_it("r1", {"linux/stx": "https://j/job/p/9/"})
        self.assertEqual(wait.call_args.args[1], {"linux/stx": "r1"})
        # As long as the Control Plane keeps the run queued, plus the margin.
        self.assertEqual(wait.call_args.args[2], 360 * 60 + trigger.BUILD_WAIT_MARGIN)
        self.assertEqual(written, "build_url=https://j/job/p/9/\n")

    def test_no_build_leaves_the_url_unset_for_not_run(self):
        _, written, _ = self.run_it("r1", {})
        self.assertEqual(written, "")

    def test_a_batch_that_never_started_says_so(self):
        wait, written, err = self.run_it("", {})
        wait.assert_not_called()
        self.assertIn("failed to start", err)

    def test_acquire_timeout_is_read_from_the_config_without_yaml(self):
        self.assertEqual(trigger.acquire_timeout_minutes(CONFIG),
                         load_config()["run_settings"]["acquire_timeout"])


class WorkflowWiring(unittest.TestCase):

    def test_localized_playbooks_run_only_when_a_locale_is_requested(self):
        with open(os.path.join(GITHUB_DIR, "workflows", "test-playbooks-orchestrai.yml")) as f:
            text = f.read()
        wf = yaml.load(text, Loader=yaml.BaseLoader)
        self.assertEqual(wf["on"]["workflow_dispatch"]["inputs"]["locale"]["default"], "")
        # No implicit zh-CN for the nightly (schedule has no inputs) or a blank dispatch.
        self.assertNotIn("inputs.locale || 'zh-CN'", text)
        self.assertIn("LOCALIZED='[]'", text)

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

    def test_every_test_job_waits_for_its_own_batch(self):
        for name, job in (("test-playbooks-orchestrai.yml", "test-playbooks"),
                          ("orchestrai-test-matrix.yml", "test-playbooks"),
                          ("orchestrai-pr-command.yml", "test-playbooks")):
            steps = self.load(name)["jobs"][job]["steps"]
            ids = [s.get("id") for s in steps]
            self.assertLess(ids.index("build"), ids.index("wait"), name)
            self.assertIn("--await-build", steps[ids.index("build")]["run"])
            self.assertIn("steps.build.outputs.build_url", steps[ids.index("wait")]["env"]["STARTED_BUILD_URL"])
            self.assertEqual(self.load(name)["jobs"][job]["permissions"]["id-token"], "write", name)


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

    def test_test_jobs_outlast_the_machine_wait_and_the_build(self):
        # Each Test job waits for its batch's build (acquire_timeout + margin),
        # then for the build itself (4.5 h: 1080 polls x 15 s).
        need = (load_config()["run_settings"]["acquire_timeout"] + trigger.BUILD_WAIT_MARGIN / 60
                + 1080 * 15 / 60)
        for name, job in (("test-playbooks-orchestrai.yml", "test-playbooks"),
                          ("orchestrai-pr-command.yml", "test-playbooks"),
                          ("orchestrai-test-matrix.yml", "test-playbooks")):
            with open(os.path.join(GITHUB_DIR, "workflows", name)) as f:
                limit = int(yaml.safe_load(f)["jobs"][job]["timeout-minutes"])
            self.assertGreater(limit, need, name)

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
            # KRK's untagged playbooks run on its 64 GB machine (superset_tags).
            self.assertEqual(batches[f"{platform}/krk+ram_64gb"]["playbooks"],
                             [*affected, "ollama-getting-started"])
            self.assertNotIn(f"{platform}/krk", batches)


class FoldIntoCapacityBatch(unittest.TestCase):
    """A device with a ram_128gb batch runs its untagged playbooks there too."""

    MIXED = ["deepseek-v4-flash-ds4", "lmstudio-rocm-llms", "ollama-getting-started",
             "cvml"]

    def build(self, playbooks=None, **overrides):
        from orchestrai_matrix import build
        cfg = load_config()
        cfg["device_to_tags"] = {device: [f"fixture-{device}"] for device in cfg["device_to_gfx"]}
        cfg.update(overrides)
        old_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(GITHUB_DIR))
            return build(playbooks or self.MIXED, cfg, devices={"halo"}, platforms={"linux"})
        finally:
            os.chdir(old_cwd)

    def test_untagged_halo_playbooks_join_the_128gb_batch(self):
        matrix, batches = self.build()
        self.assertEqual(sorted(batches), ["linux/halo+ram_128gb"])
        self.assertEqual(sorted(batches["linux/halo+ram_128gb"]["playbooks"]), sorted(self.MIXED))
        self.assertIn("ram_128gb", batches["linux/halo+ram_128gb"]["tags"])
        # Every Test job waits on the batch its playbook now runs in.
        self.assertEqual({e["batch_id"] for e in matrix}, {"linux/halo+ram_128gb"})

    def test_without_superset_tags_the_batches_stay_separate(self):
        matrix, batches = self.build(superset_tags=[])
        self.assertEqual(sorted(batches), ["linux/halo", "linux/halo+ram_128gb"])
        self.assertEqual({e["batch_id"] for e in matrix}, set(batches))

    def test_untagged_only_runs_keep_their_own_batch(self):
        _, batches = self.build(["ollama-getting-started", "cvml"])
        self.assertEqual(sorted(batches), ["linux/halo"])

    def test_two_capacity_batches_on_one_device_are_not_guessed_between(self):
        _, batches = self.build(device_extra_tags={
            **load_config()["device_extra_tags"],
            "lmstudio-rocm-llms": {"halo": ["ram_64gb"]}},
            extra_tag_devices={"ram_128gb": ["halo"], "ram_64gb": ["halo"]})
        self.assertEqual(sorted(batches),
                         ["linux/halo", "linux/halo+ram_128gb", "linux/halo+ram_64gb"])

    def test_localized_batches_fold_the_same_way(self):
        from orchestrai_matrix import build
        cfg = load_config()
        cfg["device_to_tags"] = {device: [f"fixture-{device}"] for device in cfg["device_to_gfx"]}
        old_cwd = os.getcwd()
        try:
            os.chdir(os.path.dirname(GITHUB_DIR))
            matrix, batches = build(["lmstudio-rocm-llms", "comfyui-image-gen"], cfg,
                                    devices={"halo"}, platforms={"linux"}, locale="zh-CN")
        finally:
            os.chdir(old_cwd)
        if not batches:
            self.skipTest("no zh-CN playbooks for this selection")
        self.assertEqual(sorted(batches), ["localized/zh-CN/linux/halo+ram_128gb"])
        self.assertEqual({e["batch_id"] for e in matrix}, set(batches))


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
