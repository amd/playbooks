#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Regression tests for what orchestrai_trigger.py sends to the pipeline.

run_settings.acquire_timeout was written into PLAN_JSON, but the pipeline reads
its machine-acquire timeout only from the ACQUIRE_TIMEOUT build parameter, so the
setting was silently ignored and every run waited the pipeline's 2400 s default.
These tests pin that the value in orchestrai-config.yml is what the pipeline
actually receives.

Usage:
    python3 .github/tests/test_orchestrai_trigger.py
"""

import os
import sys
import unittest
import urllib.parse
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


def submitted_params(plan, platform="linux"):
    """Run submit() against a fake pipeline server and return the form it posted."""
    captured = {}

    class Response:
        headers = {"Location": "https://pipeline.example/queue/item/1/"}

        def __enter__(self):
            return self

        def __exit__(self, *exc):
            return False

    class Opener:
        def open(self, req, timeout=None):
            captured["body"] = req.data
            return Response()

    with mock.patch.object(trigger.urllib.request, "build_opener", lambda *a: Opener()):
        queue = trigger.submit(plan, {"builds": []}, platform,
                               {"url": "https://pipeline.example", "job": "pipeline"},
                               "user", "token")
    assert queue == "https://pipeline.example/queue/item/1/"
    return {k: v[0] for k, v in urllib.parse.parse_qs(captured["body"].decode()).items()}


def plan_with(acquire_timeout):
    return {"groups": [], "run_settings": {"max_duration": 240, "max_test_case_duration": 90,
                                           "acquire_timeout": acquire_timeout,
                                           "machines_per_hw_group": 1}}


class AcquireTimeoutReachesThePipeline(unittest.TestCase):

    def test_acquire_timeout_is_sent_as_the_build_parameter_in_seconds(self):
        self.assertEqual(submitted_params(plan_with(60))["ACQUIRE_TIMEOUT"], "3600")
        self.assertEqual(submitted_params(plan_with(45))["ACQUIRE_TIMEOUT"], "2700")

    def test_the_configured_value_is_what_the_pipeline_receives(self):
        """End to end from the shipped orchestrai-config.yml."""
        cfg = load_config()
        plan = trigger.make_plan(BATCH, "refs/heads/main", cfg, 1,
                                 "https://github.com/amd/playbooks", "main",
                                 "https://index.example")
        params = submitted_params(plan)
        self.assertEqual(params["ACQUIRE_TIMEOUT"],
                         str(cfg["run_settings"]["acquire_timeout"] * 60))
        self.assertEqual(params["ACQUIRE_TIMEOUT"], "3600")

    def test_the_other_parameters_are_unchanged(self):
        params = submitted_params(plan_with(60), platform="windows")
        self.assertEqual(set(params), {"PLAN_JSON", "BUILDS_JSON", "OS_IMAGE", "ACQUIRE_TIMEOUT"})
        self.assertEqual(params["OS_IMAGE"], "windows")


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

    def test_a_timeout_that_leaves_no_time_to_run_is_rejected(self):
        self.assertTrue(self.errors_for(acquire_timeout=240, max_duration=240))
        self.assertEqual(self.errors_for(acquire_timeout=239, max_duration=240), [])

    def test_no_overall_limit_means_no_comparison(self):
        self.assertEqual(self.errors_for(acquire_timeout=600, max_duration=0), [])


if __name__ == "__main__":
    unittest.main(verbosity=2)
