<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Archived workflows: self-hosted device runners

These workflows ran playbook tests on self-hosted GitHub runners attached to
AMD devices. Those runners were retired; playbook tests now run on OrchestrAI
(`../test-playbooks-orchestrai.yml`). They are kept here for reference only.

GitHub runs only the workflow files directly in `.github/workflows/`, so
nothing in this directory runs. To bring one back, move it up a level; the
scripts it calls are in `../../scripts/archive/`.

| File | What it did |
|------|-------------|
| `test-playbooks-device-runners.yml` | `test-playbooks.yml` before the move: the PR, nightly and manual playbook tests on the device runners, and the nightly's `ci-test-failure` issues |
| `native-test-matrix.yml` | The reusable job that ran one matrix of playbook tests on the device runners |
| `monitor-runners.yml` | Weekly: listed the device runners and checked the heartbeat results |
| `restart-runners.yml` | Nightly, or by hand for chosen runners: restarted the device runners |
| `runner-heartbeat.yml` | Weekly: ran a heartbeat job on each runner in `runners.json` |
