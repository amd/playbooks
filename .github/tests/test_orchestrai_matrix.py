# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

import orchestrai_matrix  # noqa: E402

CFG = {"batch_split": {
    "batches": ["linux/rx9070xt"], "budget_minutes": 240, "default_minutes": 15,
    "playbook_minutes": {"lm": 90, "slack": 62, "comfy": 55, "gaia": 32}}}
SMALL = [f"p{i}" for i in range(13)]


def batch(pbs):
    return {"platform": "linux", "arch": "rx9070xt", "tags": ["t"], "playbooks": list(pbs)}


class SplitLongBatches(unittest.TestCase):
    def run_split(self, bid, pbs, cfg=CFG):
        batches = {bid: batch(pbs)}
        matrix = [{"playbook": pb, "batch_id": bid} for pb in pbs]
        orchestrai_matrix.split_long_batches(matrix, batches, cfg)
        return matrix, batches

    def test_a_listed_batch_over_budget_is_split_to_fit(self):
        pbs = ["lm", "slack", "comfy", "gaia"] + SMALL   # ~434 min
        matrix, batches = self.run_split("linux/rx9070xt", pbs)
        self.assertEqual(sorted(batches), ["linux/rx9070xt", "linux/rx9070xt#2"])
        est = lambda pb: CFG["batch_split"]["playbook_minutes"].get(pb, 15)
        for b in batches.values():
            self.assertLessEqual(sum(map(est, b["playbooks"])), 240)
        self.assertEqual(sorted(pb for b in batches.values() for pb in b["playbooks"]),
                         sorted(pbs), "every playbook lands in exactly one part")
        for e in matrix:
            self.assertIn(e["playbook"], batches[e["batch_id"]]["playbooks"])

    def test_localized_batch_is_split_too(self):
        _, batches = self.run_split("localized/zh-CN/linux/rx9070xt", ["lm", "slack", "comfy", "gaia"] + SMALL)
        self.assertIn("localized/zh-CN/linux/rx9070xt#2", batches)

    def test_unlisted_or_short_batches_are_left_alone(self):
        _, batches = self.run_split("linux/rx7900xt", ["lm", "slack", "comfy", "gaia"] + SMALL)
        self.assertEqual(list(batches), ["linux/rx7900xt"])
        _, batches = self.run_split("linux/rx9070xt", ["lm", "slack"])
        self.assertEqual(list(batches), ["linux/rx9070xt"])

    def test_no_config_means_no_split(self):
        _, batches = self.run_split("linux/rx9070xt", ["lm", "slack", "comfy", "gaia"] + SMALL, cfg={})
        self.assertEqual(len(batches), 1)


if __name__ == "__main__":
    unittest.main()
