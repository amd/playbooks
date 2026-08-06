#!/usr/bin/env python3
# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""
OrchestrAI matrix/batch builder
===============================

Turns a list of playbook IDs into:

  * matrix  - one entry per (playbook, platform, device) GitHub Actions test job
  * batches - same entries grouped by (platform/device[+extra-tags]); each batch
              becomes ONE OrchestrAI pipeline build that runs its playbooks on
              shared hardware.

Device/platform come from each playbook's playbooks/<cat>/<id>/playbook.json
(tested_platforms / required_platforms). All environment-specific policy
(device -> broker tags, extra tags, extra devices, skips) is read from
.github/orchestrai-config.yml so this script stays generic.

Usage:
    orchestrai_matrix.py --playbooks '["comfyui-image-gen", ...]' \
        [--config .github/orchestrai-config.yml] [--print]

Writes matrix=/batches=/has_entries= to $GITHUB_OUTPUT when set; --print also
dumps a human-readable summary + JSON to stdout (handy for dry runs).
"""

import argparse
import json
import os
import sys
from pathlib import Path

import yaml


def load_config(path):
    with open(path) as f:
        return yaml.safe_load(f)


def build(playbooks, cfg, devices=None, platforms=None):
    device_to_tags = cfg["device_to_tags"]
    device_to_gfx = cfg["device_to_gfx"]
    extra_tags = cfg.get("extra_tags", {})
    device_extra_tags = cfg.get("device_extra_tags", {})
    extra_tag_devices = cfg.get("extra_tag_devices", {})
    extra_devices = cfg.get("extra_devices", {})
    skip_devices = set(cfg.get("skip_devices", []))

    matrix = []

    def tags_for(playbook, device):
        """Return device-specific tags when configured, else playbook defaults."""
        overrides = device_extra_tags.get(playbook, {})
        return overrides.get(device, extra_tags.get(playbook, []))

    # 1) Declared platforms from each playbook's playbook.json
    for pb_id in playbooks:
        for cat in ("core", "supplemental"):
            pb_file = Path(f"playbooks/{cat}/{pb_id}/playbook.json")
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
                    extra = tags_for(pb_id, device)
                    batch_id = f"{platform}/{device}" + (
                        f"+{'_'.join(extra)}" if extra else ""
                    )
                    matrix.append({
                        "playbook": pb_id,
                        "platform": platform,
                        "arch": device,
                        "batch_id": batch_id,
                        "required": platform in required_platforms,
                    })
            break

    # 2) Extra (device, platforms) entries beyond playbook.json (always optional)
    for pb_id in playbooks:
        for spec in extra_devices.get(pb_id, []):
            device = spec["device"]
            for platform in spec["platforms"]:
                extra = tags_for(pb_id, device)
                entry = {
                    "playbook": pb_id,
                    "platform": platform,
                    "arch": device,
                    "batch_id": f"{platform}/{device}" + (
                        f"+{'_'.join(extra)}" if extra else ""
                    ),
                    "required": False,
                }
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

    # 5) Group into batches by batch_id
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
        if e["playbook"] not in batches[bid]["playbooks"]:
            batches[bid]["playbooks"].append(e["playbook"])

    return matrix, batches


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
    args = ap.parse_args()

    def parse_csv(s):
        s = (s or "").strip()
        if not s or s.lower() == "all":
            return None
        return {x.strip() for x in s.split(",") if x.strip()}

    devices = parse_csv(args.devices)
    platforms = parse_csv(args.platforms)

    raw = (args.playbooks or "").strip()
    playbooks = json.loads(raw) if raw and raw != "[]" else []

    if not playbooks:
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
        matrix, batches = build(playbooks, cfg, devices=devices, platforms=platforms)

    out = os.environ.get("GITHUB_OUTPUT")
    if out:
        with open(out, "a") as f:
            f.write(f"matrix={json.dumps(matrix)}\n")
            f.write(f"batches={json.dumps(batches)}\n")
            f.write(f"has_entries={'true' if matrix else 'false'}\n")

    print(f"Matrix: {len(matrix)} entries, Batches: {len(batches)}", file=sys.stderr)
    if args.do_print:
        for bid, b in batches.items():
            print(f"  {bid}: {', '.join(b['playbooks'])}  tags={b['tags']}",
                  file=sys.stderr)
        print(json.dumps({"matrix": matrix, "batches": batches}, indent=2))


if __name__ == "__main__":
    main()
