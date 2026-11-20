#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI matrix/batch builder
===============================

Turns a list of playbook IDs into:

  * matrix  - one entry per (playbook, language, platform, device)
  * batches - same entries grouped by (platform/device[+extra-tags]); each batch
              becomes ONE OrchestrAI pipeline build that runs its playbooks on
              shared hardware, English and localized alike.

Device/platform come from each playbook's playbooks/<cat>/<id>/playbook.json
(tested_platforms / required_platforms). All environment-specific policy
(device -> broker tags, extra tags, extra devices, skips) is read from
.github/orchestrai-config.yml so this script stays generic.

A batch's members are keys (orchestrai_keys.py): "<id>" for English and
"<locale>/<id>" for a localized playbook. A localized entry that would execute
exactly what its English entry in the same run executes (only the prose was
translated) is not run again on that machine; its matrix entry gets
covered_by and its batch lists it under "covered", so the results report it
with the English result.

Usage:
    orchestrai_matrix.py --playbooks '["comfyui-image-gen", ...]' \
        [--locale zh-CN [--localized-playbooks '["comfyui-image-gen", ...]']] \
        [--config .github/orchestrai-config.yml] [--print]

With --locale alone, --playbooks are that locale's (one language, as
!localized-orc runs). With --localized-playbooks too, --playbooks are English
and both languages share the batches.

Writes matrix=/batches=/has_entries= (and english_matrix=/localized_matrix=)
to $GITHUB_OUTPUT when set; --print also dumps a human-readable summary + JSON
to stdout (handy for dry runs).
"""

import argparse
import contextlib
import dataclasses
import io
import json
import os
import sys
import tempfile
from pathlib import Path

import yaml

import run_playbook_tests as runner
from orchestrai_keys import member_key
from run_playbook_tests import load_merged_metadata

# TestBlock fields that do not change what a test executes on one device and
# OS: where it sits in the README, whether readers see it, its CI time limit,
# and the @os/@device tags it was selected by.
NOT_EXECUTED = runner.SIGNATURE_EXCLUDED | {"timeout", "platform", "device"}


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def _execution(tests, assets):
    """What a test run executes: its tests' commands and the playbook's assets."""
    payload = [{k: v for k, v in dataclasses.asdict(t).items() if k not in NOT_EXECUTED}
               for t in tests]
    return json.dumps([payload, assets], sort_keys=True)


def english_execution(playbook, platform, device, root):
    path = runner.find_playbook_path(playbook, repo_root=root)
    if path is None:
        return None
    with contextlib.redirect_stdout(io.StringIO()):
        tests = runner.extract_tests(path / "README.md", platform, device, repo_root=root)
    assets = runner.assets_digest(path / "assets")
    return None if assets is None else _execution(tests, assets)


def localized_execution(playbook, locale, localized_only, platform, device, root):
    with tempfile.TemporaryDirectory(prefix="orchestrai-localized-") as tmp:
        with contextlib.redirect_stdout(io.StringIO()):
            path = runner.materialize_localized_playbook(
                locale, playbook, Path(tmp) / playbook, localized_only, repo_root=root)
            tests = runner.extract_tests(path / "README.md", platform, device, repo_root=root,
                                         locale=locale, localized_only=localized_only)
        assets = runner.assets_digest(path / "assets")
    return None if assets is None else _execution(tests, assets)


def runs_same_tests(entry, device, root):
    """True when a localized entry would execute exactly what its English
    entry does on the same device and OS: the same tests in the same order,
    with the same commands, setup, working directory and playbook assets.
    Only the prose differs, so running it again on the same machine tells
    nothing new. Anything that cannot be compared is run."""
    try:
        english = english_execution(entry["playbook"], entry["platform"], device, root)
        localized = localized_execution(entry["playbook"], entry["locale"],
                                        entry["localized_only"], entry["platform"], device, root)
    except Exception as exc:  # noqa: BLE001 - any doubt runs the test
        print(f"::notice::could not compare {entry['key']} with English ({exc}); running it",
              file=sys.stderr)
        return False
    return english is not None and english == localized


def build(playbooks, cfg, devices=None, platforms=None, locale="", localized_playbooks=None,
          root=None):
    """Matrix entries and batches for English and localized playbooks.

    Without localized_playbooks, `playbooks` are in `locale` ("" = English):
    one language, as !orc and !localized-orc run. With them, `playbooks` are
    English and `localized_playbooks` are in `locale`; both share batches, so
    a device and OS is one OrchestrAI run on one machine for every language.
    """
    root = Path(root) if root else Path.cwd()
    if localized_playbooks and not locale:
        raise ValueError("localized playbooks need a locale")
    sources = ([(locale, playbooks)] if localized_playbooks is None
               else [("", playbooks), (locale, localized_playbooks)])
    device_to_tags = cfg["device_to_tags"]
    device_to_gfx = cfg["device_to_gfx"]
    extra_tags = cfg.get("extra_tags", {})
    device_extra_tags = cfg.get("device_extra_tags", {})
    extra_tag_devices = cfg.get("extra_tag_devices", {})
    extra_devices = cfg.get("extra_devices", {})
    skip_devices = set(cfg.get("skip_devices", []))
    skip_playbook_devices = cfg.get("skip_playbook_devices", {}) or {}
    runs_as = cfg.get("device_runs_as") or {}

    matrix = []

    def tags_for(playbook, device):
        """Return device-specific tags when configured, else playbook defaults."""
        overrides = device_extra_tags.get(playbook, {})
        return overrides.get(device, extra_tags.get(playbook, []))

    def batch_id_for(platform, device, extra):
        # No locale in it: every language of a device and OS shares the batch.
        return f"{platform}/{device}" + (f"+{'_'.join(extra)}" if extra else "")

    def make_entry(pb_id, platform, device, required, src_locale, localized_only):
        entry = {
            "playbook": pb_id,
            "platform": platform,
            "arch": device,
            "batch_id": batch_id_for(platform, device, tags_for(pb_id, device)),
            "required": required,
            "key": member_key(pb_id, src_locale),
        }
        if src_locale:
            entry.update({"locale": src_locale, "localized_only": localized_only})
        return entry

    for src_locale, src_playbooks in sources:
        localized_only_by_playbook = {}
        # 1) Declared platforms from each playbook's playbook.json
        for pb_id in src_playbooks:
            for cat in ("core", "supplemental"):
                if src_locale:
                    pb_dir = root / "localized-playbooks" / src_locale / cat / pb_id
                    if not pb_dir.is_dir():
                        continue
                    # The playbooks under test are in the working directory, which
                    # for !orc is the PR head and not this script's checkout.
                    meta = load_merged_metadata(src_locale, cat, pb_id, root)
                    localized_only_by_playbook[pb_id] = meta["localized_only"]
                else:
                    pb_file = root / "playbooks" / cat / pb_id / "playbook.json"
                    if not pb_file.exists():
                        continue
                    meta = json.loads(pb_file.read_text())
                tested = meta.get("tested_platforms", {})
                if not tested:
                    break
                required = meta.get("required_platforms", {})
                for device, platform_list in tested.items():
                    required_platforms = set(required.get(device, []))
                    for platform in platform_list:
                        matrix.append(make_entry(pb_id, platform, device,
                                                 platform in required_platforms,
                                                 src_locale, meta.get("localized_only")))
                break

        # 2) Extra (device, platforms) entries beyond playbook.json (always optional)
        for pb_id in src_playbooks:
            for spec in extra_devices.get(pb_id, []):
                device = spec["device"]
                for platform in spec["platforms"]:
                    entry = make_entry(pb_id, platform, device, False, src_locale,
                                       localized_only_by_playbook.get(pb_id, True))
                    if entry not in matrix:
                        matrix.append(entry)

    # 2b) Narrow to the devices / platforms the run explicitly asked for
    #     (workflow_dispatch device/platform inputs). None/empty = no filter.
    if devices:
        matrix = [e for e in matrix if e["arch"] in devices]
    if platforms:
        matrix = [e for e in matrix if e["platform"] in platforms]

    # 3) Skip offline/unsupported devices
    matrix = [e for e in matrix if e["arch"] not in skip_devices]

    # 3b) Skip a specific playbook on a specific device. Unlike skip_devices
    #     (the device is unusable for everything), this is for a device that is
    #     fine in general but cannot run one playbook -- e.g. a playbook pinned
    #     to a model too large for that SKU's memory. Announce each drop: a
    #     silently missing combination is indistinguishable from one that was
    #     never declared.
    dropped = [
        (e["playbook"], e["arch"])
        for e in matrix
        if e["arch"] in skip_playbook_devices.get(e["playbook"], [])
    ]
    for pb_id, device in sorted(set(dropped)):
        print(f"::notice::skipping playbook '{pb_id}' on device '{device}' "
              f"(skip_playbook_devices in orchestrai-config.yml)", file=sys.stderr)
    matrix = [
        e for e in matrix
        if e["arch"] not in skip_playbook_devices.get(e["playbook"], [])
    ]

    # 4) Drop batches that request an extra tag the device can't satisfy
    #    (e.g. ram_128gb on a non-128GB device — broker could never match it).
    def device_satisfies_extras(e):
        for tag in tags_for(e["playbook"], e["arch"]):
            allowed = extra_tag_devices.get(tag)
            if allowed is not None and e["arch"] not in allowed:
                return False
        return True

    matrix = [e for e in matrix if device_satisfies_extras(e)]

    # 4b) Drop entries whose device has no broker-tag mapping. Falling back to the
    #     raw device name as a tag (the old behavior) builds a batch the MAAS
    #     broker can never satisfy — it would queue and time out hours later.
    #     Skip + warn instead, so a device declared in playbook.json but not yet
    #     wired into the fleet doesn't hang the run or block the other devices.
    unmapped = sorted({e["arch"] for e in matrix if e["arch"] not in device_to_tags})
    if unmapped:
        print(f"::warning::skipping device(s) with no device_to_tags mapping in "
              f"orchestrai-config.yml: {', '.join(unmapped)} "
              f"(add device_to_tags + device_to_gfx entries to enable)", file=sys.stderr)
        matrix = [e for e in matrix if e["arch"] in device_to_tags]

    # 4c) A localized entry whose English entry runs on the same device and OS
    #     in this run, executing exactly the same tests, is not run a second
    #     time on that machine: it reports the English result (covered_by).
    #     The device is the one the runner extracts for (device_runs_as).
    english = {(e["playbook"], e["platform"], e["arch"]) for e in matrix if not e.get("locale")}
    for e in matrix:
        if (e.get("locale") and (e["playbook"], e["platform"], e["arch"]) in english
                and runs_same_tests(e, runs_as.get(e["arch"], e["arch"]), root)):
            e["covered_by"] = member_key(e["playbook"])

    # 5) Group into batches by batch_id. Members are keys, English before
    #    localized: the matrix lists English first.
    batches = {}
    for e in matrix:
        bid = e["batch_id"]
        if bid not in batches:
            tags = sorted(
                device_to_tags.get(e["arch"], [e["arch"]])
                + tags_for(e["playbook"], e["arch"])
            )
            batches[bid] = {
                "platform": e["platform"],
                "arch": e["arch"],
                "gfx": device_to_gfx.get(e["arch"], e["arch"]),
                "tags": tags,
                "playbooks": [],
            }
        batch = batches[bid]
        if e.get("covered_by"):
            batch.setdefault("covered", {})[e["key"]] = e["covered_by"]
            continue
        if e["key"] not in batch["playbooks"]:
            batch["playbooks"].append(e["key"])
        if e.get("locale"):
            batch.setdefault("localized_only", {})[e["key"]] = e["localized_only"]

    # 6) A machine with more of a capacity (ram_128gb) also runs the device's
    #    untagged playbooks, so fold the untagged batch into it: one machine for
    #    the device instead of two. Only superset_tags qualify, and only when
    #    the device has exactly one such batch on that platform.
    fold_into_capacity_batches(matrix, batches, cfg, batch_id_for, tags_for)

    return matrix, batches


def fold_into_capacity_batches(matrix, batches, cfg, batch_id_for, tags_for):
    superset = set(cfg.get("superset_tags") or [])
    if not superset:
        return
    extras = {}  # batch id -> its extra tags
    for e in matrix:
        extras.setdefault(e["batch_id"], tuple(tags_for(e["playbook"], e["arch"])))
    targets = {}  # (platform, device) -> capacity batch ids
    for bid, b in batches.items():
        if extras.get(bid) and set(extras[bid]) <= superset:
            targets.setdefault((b["platform"], b["arch"]), []).append(bid)
    moved = {}
    for (platform, device), found in targets.items():
        base = batch_id_for(platform, device, [])
        if len(found) != 1 or base not in batches:
            continue
        target = batches[found[0]]
        for key in batches[base]["playbooks"]:
            if key not in target["playbooks"]:
                target["playbooks"].append(key)
        target["playbooks"].sort(key=lambda key: "/" in key)  # English first, as in step 5
        for field in ("localized_only", "covered"):
            if batches[base].get(field):
                target.setdefault(field, {}).update(batches[base][field])
        del batches[base]
        moved[base] = found[0]
    for e in matrix:
        e["batch_id"] = moved.get(e["batch_id"], e["batch_id"])


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--playbooks", default=os.environ.get("PLAYBOOKS", ""),
                    help='JSON array of playbook IDs')
    ap.add_argument("--config", default=".github/orchestrai-config.yml")
    ap.add_argument("--devices", default=os.environ.get("DEVICES", ""),
                    help='comma-separated device list (empty/"all" = every device)')
    ap.add_argument("--platforms", default=os.environ.get("PLATFORMS", ""),
                    help='comma-separated platform list (empty/"all" = linux+windows)')
    ap.add_argument("--print", action="store_true", dest="do_print")
    ap.add_argument(
        "--locale",
        default=os.environ.get("LOCALE", ""),
        help="Locale under localized-playbooks; empty selects canonical English",
    )
    ap.add_argument(
        "--localized-playbooks",
        default=os.environ.get("LOCALIZED_PLAYBOOKS"),
        help="JSON array of --locale playbook IDs to batch with the English --playbooks",
    )
    args = ap.parse_args()

    def parse_csv(s):
        s = (s or "").strip()
        if not s or s.lower() == "all":
            return None
        return {x.strip() for x in s.split(",") if x.strip()}

    def parse_ids(raw):
        raw = (raw or "").strip()
        return json.loads(raw) if raw and raw != "[]" else []

    devices = parse_csv(args.devices)
    platforms = parse_csv(args.platforms)

    playbooks = parse_ids(args.playbooks)
    localized = None if args.localized_playbooks is None else parse_ids(args.localized_playbooks)

    if not playbooks and not localized:
        matrix, batches = [], {}
    else:
        cfg = load_config(args.config)
        # Internal MAAS broker tags are not committed to this (public) repo; they
        # come from the ORCHESTRAI_DEVICE_TAGS variable (a JSON device->tags map).
        dt = os.environ.get("ORCHESTRAI_DEVICE_TAGS")
        if dt:
            try:
                cfg["device_to_tags"] = json.loads(dt)
            except json.JSONDecodeError:
                print("::warning::ORCHESTRAI_DEVICE_TAGS is not valid JSON — falling back to config",
                      file=sys.stderr)
        matrix, batches = build(playbooks, cfg, devices=devices, platforms=platforms,
                                locale=args.locale, localized_playbooks=localized)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"matrix={json.dumps(matrix)}\n")
            f.write(f"english_matrix={json.dumps([e for e in matrix if not e.get('locale')])}\n")
            f.write(f"localized_matrix={json.dumps([e for e in matrix if e.get('locale')])}\n")
            f.write(f"batches={json.dumps(batches)}\n")
            f.write(f"has_entries={'true' if matrix else 'false'}\n")

    covered = [e for e in matrix if e.get("covered_by")]
    print(f"Matrix: {len(matrix)} entries, Batches: {len(batches)}", file=sys.stderr)
    if covered:
        print(f"Not run again: {len(covered)} localized entries execute exactly what their "
              f"English entry in the same batch does", file=sys.stderr)
    if args.do_print:
        for bid, b in batches.items():
            print(f"  {bid}: {', '.join(b['playbooks'])}  tags={b['tags']}"
                  + (f"  same as English: {', '.join(b['covered'])}" if b.get("covered") else ""),
                  file=sys.stderr)
        print(json.dumps({"matrix": matrix, "batches": batches}, indent=2))


if __name__ == "__main__":
    main()
