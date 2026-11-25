#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
Pull request runs for OrchestrAI CI changes
===========================================

build_test_matrix.py picks the entries whose tests a pull request changed. A
change to .github/orchestrai-config.yml or to the scripts that start and read
the OrchestrAI runs changes no test, so it picks nothing, yet it decides how
the entries run: the machines' tags, sites and OS image, PLAYBOOK_DEVICE, the
provisioning scripts and the run settings. A pull request's run
(test-playbooks-orchestrai.yml) uses the PR's own config and scripts, so it can
test such a change on hardware; this picks the entries to run for it.

  * The config: each entry, English and --locale, becomes the plan and builds
    orchestrai_trigger.py would send for it alone, once with the base
    revision's config and once with this checkout's. An entry runs when the two
    differ, or when it is new (a skip list no longer drops it). Names shown on
    the results (device_names) and pr_devices change what is reported or
    picked, not how an entry runs, so they select nothing. Both configs go
    through this checkout's scripts; a change to those is the next case.
  * The scripts (CONTROLLER_PATHS, minus NOT_CONTROLLER) and the workflow:
    every entry.

A change that reaches more than config_change_runs.max_entries entries runs a
sample instead (sample()): one entry per OS and device family where it reaches
every entry of that family, else one per device it reaches. A change to the
scripts therefore runs one playbook per OS on one APU and one Radeon GPU.

Usage:
    orchestrai_config_changes.py --base <sha> [--locale zh-CN]

Prints the selected entries as a sorted JSON list of [locale, playbook,
platform, device] ("" = English), as build_test_matrix.py --keys does.
Annotations go to stderr.
"""

import argparse
import contextlib
import fnmatch
import io
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

sys.path.insert(0, str(Path(__file__).parent))
import orchestrai_matrix as M  # noqa: E402
import orchestrai_trigger as T  # noqa: E402
import run_playbook_tests as R  # noqa: E402

REPO_ROOT = Path(__file__).resolve().parents[2]
CONFIG = ".github/orchestrai-config.yml"

# What starts the runs and reads their results on a pull request. A change to
# any of these reaches every entry.
CONTROLLER_PATHS = (
    ".github/scripts/orchestrai_*",
    ".github/workflows/test-playbooks-orchestrai.yml",
)
# Matched by CONTROLLER_PATHS, but a pull request's run does not use them.
NOT_CONTROLLER = frozenset({
    ".github/scripts/orchestrai_command.py",         # !orc, always from main
    ".github/scripts/orchestrai_config_changes.py",  # picks entries; unit tests
})

DEFAULT_MAX_ENTRIES = 8

# Placeholder values for what a run gets from its event, not from the config,
# so only the config differs between the two sides.
PLACEHOLDERS = {"git_ref": "<ref>", "repo": "<repo>", "sha": "<sha>", "rocm_index_url": "<index>"}


def annotate(level, message):
    """Report on stderr only; stdout is the selection."""
    prefix = f"::{level}::" if os.environ.get("GITHUB_ACTIONS") else ""
    print(f"{prefix}{message}", file=sys.stderr)


def entry_key(e):
    return (e.get("locale", ""), e["playbook"], e["platform"], e["arch"])


def label(key):
    locale, playbook, platform, device = key
    return f"{locale + '/' if locale else ''}{playbook} ({platform}/{device})"


def with_device_tags(cfg):
    """The config with the device -> broker tags the run uses. They are not
    committed (ORCHESTRAI_DEVICE_TAGS, as orchestrai_matrix.py reads it), and
    an entry whose device has none is left out of the matrix, so without them
    every device known to the config stands in with its own name."""
    cfg = dict(cfg)
    raw = os.environ.get("ORCHESTRAI_DEVICE_TAGS")
    if raw:
        try:
            cfg["device_to_tags"] = json.loads(raw)
        except json.JSONDecodeError:
            annotate("warning", "ORCHESTRAI_DEVICE_TAGS is not valid JSON; using the config's map")
    if not cfg.get("device_to_tags"):
        known = set(cfg.get("device_families") or {}) | set(cfg.get("device_to_gfx") or {})
        cfg["device_to_tags"] = {device: [device] for device in known}
    return cfg


def flatten(value, prefix=""):
    """{dotted path: JSON} of a nested dict, so a difference can be named."""
    if isinstance(value, dict) and value:
        out = {}
        for k, v in value.items():
            out.update(flatten(v, f"{prefix}.{k}" if prefix else str(k)))
        return out
    return {prefix: json.dumps(value, sort_keys=True)}


def run_settings(batch, cfg):
    """What orchestrai_trigger.py would send for a batch of one entry."""
    plan = T.make_plan(batch, PLACEHOLDERS["git_ref"], cfg,
                       (cfg.get("run_settings") or {}).get("default_machines_per_hw_group", 1),
                       PLACEHOLDERS["repo"], PLACEHOLDERS["sha"], PLACEHOLDERS["rocm_index_url"])
    builds, missing = T.make_builds(batch, cfg)
    (group,) = plan["groups"]
    return flatten({
        "machines": {k: batch.get(k) for k in ("platform", "arch", "gfx", "tags")},
        "group": {k: v for k, v in group.items() if k != "id"},
        "plan": {k: v for k, v in plan.items() if k != "groups"},
        "builds": builds,
        "missing": sorted(missing),
    })


def entry_runs(cfg, languages, root):
    """{key: (entry, settings)} for every entry the config runs, each built as
    a batch of its own: what it shares a machine with is not the change."""
    cfg = with_device_tags(cfg)
    out = {}
    for locale, playbooks in languages.items():
        for playbook in playbooks:
            with contextlib.redirect_stderr(io.StringIO()):
                matrix, batches = M.build([], cfg, languages={locale: [playbook]},
                                          root=root, cover_localized=False)
                for e in matrix:
                    out[entry_key(e)] = (e, run_settings(batches[e["batch_id"]], cfg))
    return out


def changed_entries(base_cfg, head_cfg, languages, root):
    """(head entries, keys of those that run differently with head_cfg).
    A base config that cannot be read or run reaches every entry."""
    head = entry_runs(head_cfg, languages, root)
    try:
        if not isinstance(base_cfg, dict):
            raise ValueError("it is not a mapping")
        base = entry_runs(base_cfg, languages, root)
    except Exception as exc:  # noqa: BLE001 - any doubt runs everything
        annotate("warning", f"Cannot apply the base revision's config ({type(exc).__name__}: "
                            f"{exc}); every entry may run differently")
        return head, set(head)
    # One notice per difference, naming what differs and not its values: the
    # broker tags are not public.
    by_reason = {}
    for key, (_, settings) in head.items():
        if key not in base:
            by_reason.setdefault("new entry", []).append(key)
            continue
        prior = base[key][1]
        paths = sorted(p for p in settings.keys() | prior.keys() if settings.get(p) != prior.get(p))
        if paths:
            by_reason.setdefault(", ".join(paths), []).append(key)
    for reason, keys in sorted(by_reason.items()):
        shown = ", ".join(label(k) for k in sorted(keys)[:10])
        more = f" and {len(keys) - 10} more" if len(keys) > 10 else ""
        annotate("notice", f"Config change ({reason}): {shown}{more}")
    return head, {k for keys in by_reason.values() for k in keys}


def sample(selected, everything, cfg):
    """The entries a broad change runs: for each OS and device family, one
    entry if the change reaches every entry of that family, else one on each
    device it reaches. The device is the family's first in pr_devices; the
    entry is English, on a canary playbook (config_change_runs) if one runs
    there, else the first playbook by name."""
    families = cfg.get("device_families") or {}
    order = cfg.get("pr_devices") or {}
    canaries = (cfg.get("config_change_runs") or {}).get("canary_playbooks") or []

    def family(key):
        return (key[2], families.get(key[3], key[3]))

    def device_rank(device):
        listed = order.get(families.get(device)) or []
        return (listed.index(device) if device in listed else len(listed), device)

    def preferred(key):
        locale, playbook = key[0], key[1]
        return (locale != "", canaries.index(playbook) if playbook in canaries else len(canaries),
                playbook, locale)

    picked = set()
    for fam in sorted({family(k) for k in selected}):
        reached = {k for k in selected if family(k) == fam}
        if reached == {k for k in everything if family(k) == fam}:
            device = min({k[3] for k in reached}, key=device_rank)
            picked.add(min((k for k in reached if k[3] == device), key=preferred))
        else:
            for device in {k[3] for k in reached}:
                picked.add(min((k for k in reached if k[3] == device), key=preferred))
    return picked


def select(base_cfg, head_cfg, languages, root, controller_changed=False):
    """Keys of the entries a pull request changing the config or the scripts runs."""
    head, changed = changed_entries(base_cfg, head_cfg, languages, root)
    if controller_changed:
        annotate("notice", "The OrchestrAI scripts or workflow changed; every entry may run differently")
        changed = set(head)
    limit = (head_cfg.get("config_change_runs") or {}).get("max_entries", DEFAULT_MAX_ENTRIES)
    if len(changed) > limit:
        picked = sample(changed, set(head), head_cfg)
        annotate("notice", f"The change reaches {len(changed)} entries, more than "
                           f"config_change_runs.max_entries ({limit}); running "
                           f"{len(picked)}: {', '.join(label(k) for k in sorted(picked))}")
        changed = picked
    return sorted(changed)


def controller_changes(base, root=REPO_ROOT):
    """The CONTROLLER_PATHS files that differ between base and this checkout."""
    out = subprocess.run(["git", "diff", "--name-only", base, "HEAD", "--",
                          ".github/scripts", ".github/workflows"],
                         cwd=root, capture_output=True, text=True, check=True).stdout
    return sorted(path for path in out.splitlines()
                  if any(fnmatch.fnmatch(path, pattern) for pattern in CONTROLLER_PATHS)
                  and path not in NOT_CONTROLLER)


def base_config(base, root=REPO_ROOT):
    """The base revision's config, or None when it has none or it cannot be read."""
    try:
        text = subprocess.run(["git", "show", f"{base}:{CONFIG}"], cwd=root,
                              capture_output=True, text=True, check=True).stdout
        return yaml.safe_load(text)
    except (subprocess.CalledProcessError, yaml.YAMLError) as exc:
        annotate("warning", f"Cannot read {CONFIG} at {base}: {exc}")
        return None


def main():
    ap = argparse.ArgumentParser(
        description="Pick the entries a change to the OrchestrAI config or scripts runs")
    ap.add_argument("--base", required=True, help="the revision the pull request branched off")
    ap.add_argument("--locale", default="", help="also select this locale's entries (zh-CN)")
    args = ap.parse_args()

    head_cfg = M.load_config(REPO_ROOT / CONFIG)
    languages = {"": R.list_playbook_ids(REPO_ROOT)}
    if args.locale:
        languages[args.locale] = R.list_localized_playbook_ids(REPO_ROOT, args.locale)
    try:
        scripts = controller_changes(args.base)
    except subprocess.CalledProcessError as exc:
        annotate("warning", f"Cannot compare the OrchestrAI scripts with {args.base}: "
                            f"{exc.stderr.strip()[:200]}")
        scripts = ["(unknown)"]
    for path in scripts:
        annotate("notice", f"Changed: {path}")
    keys = select(base_config(args.base), head_cfg, languages, REPO_ROOT,
                  controller_changed=bool(scripts))
    print(json.dumps([list(k) for k in keys]))


if __name__ == "__main__":
    main()
