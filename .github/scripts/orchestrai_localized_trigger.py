#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Localized adapter for the canonical OrchestrAI pipeline trigger.

The canonical module owns validation, provisioning, authentication, retries,
submission, and queue polling. This adapter only merges the localized config
overlay and adds ``PLAYBOOK_LOCALE`` plus ``PLAYBOOK_LOCALIZED_ONLY`` to each
generated test group.
"""

from __future__ import annotations

import sys

import yaml

import orchestrai_trigger as canonical


_canonical_make_plan = canonical.make_plan


def load_config(path):
    with open(path, encoding="utf-8") as f:
        overlay = yaml.safe_load(f)
    base_path = overlay.pop("base_config", None)
    if not base_path:
        return overlay
    with open(base_path, encoding="utf-8") as f:
        config = yaml.safe_load(f)
    config.update(overlay)
    return config


def make_plan(batch, git_ref, cfg, machines_per_hw_group, repo, sha, rocm_index_url, hf_token=""):
    plan = _canonical_make_plan(batch, git_ref, cfg, machines_per_hw_group, repo, sha, rocm_index_url, hf_token)
    locale = batch.get("locale")
    if not locale:
        raise ValueError("Localized OrchestrAI batch is missing locale")
    localized_only_by_playbook = batch.get("localized_only", {})
    for group in plan["groups"]:
        playbook_id = group["variables"]["PLAYBOOK_ID"]
        localized_only = localized_only_by_playbook.get(playbook_id, True)
        if not isinstance(localized_only, bool):
            raise ValueError(f"Localized OrchestrAI batch has non-boolean localized_only for {playbook_id!r}")
        group["variables"]["PLAYBOOK_LOCALE"] = locale
        group["variables"]["PLAYBOOK_LOCALIZED_ONLY"] = str(localized_only).lower()
    return plan


def main():
    if not any(
        argument == "--config" or argument.startswith("--config=")
        for argument in sys.argv[1:]
    ):
        sys.argv.extend([
            "--config",
            ".github/orchestrai-localized-config.yml",
        ])

    canonical.load_config = load_config
    canonical.make_plan = make_plan
    canonical.main()


if __name__ == "__main__":
    main()
