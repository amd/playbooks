<!--
Copyright Advanced Micro Devices, Inc.

SPDX-License-Identifier: MIT
-->

# Archived scripts: self-hosted device runners

Kept for reference only, with the workflows in `../../workflows/archive/`.
Playbook tests now run on OrchestrAI, and nothing calls these files.

| File | What it did |
|------|-------------|
| `select_runners.py` | Picked device runners from `runners.json` for the runner workflows |
| `runners.json` | The device runner fleet: each runner's labels and device. It used to be `.github/runners.json`; `select_runners.py` still reads that path |

A change in this directory does not count as a change to the test runner, so it
does not make a pull request test every playbook (`build_test_matrix.py`).
