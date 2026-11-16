# Copyright Advanced Micro Devices, Inc.
#
# SPDX-License-Identifier: MIT

"""Tests for splitting English and localized OrchestrAI matrices."""

import sys
import unittest
from pathlib import Path


SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from orchestrai_prepare_matrices import MatrixLimitError, prepare  # noqa: E402


class PrepareMatricesTests(unittest.TestCase):
    def test_combined_total_may_exceed_single_matrix_limit(self):
        result = prepare(
            [{"id": index} for index in range(206)],
            {"english": {"playbooks": ["example"]}},
            [{"id": index} for index in range(56)],
            {"localized/zh-CN": {"playbooks": ["example"]}},
        )

        self.assertEqual(len(result["english_matrix"]), 206)
        self.assertEqual(len(result["localized_matrix"]), 56)
        self.assertGreater(
            len(result["english_matrix"]) + len(result["localized_matrix"]),
            256,
        )
        self.assertTrue(result["has_entries"])

    def test_native_matrices_may_also_exceed_limit_in_total(self):
        result = prepare([{}] * 218, {}, [{}] * 56, {})

        self.assertEqual(len(result["english_matrix"]), 218)
        self.assertEqual(len(result["localized_matrix"]), 56)
        self.assertEqual(
            len(result["english_matrix"]) + len(result["localized_matrix"]),
            274,
        )

    def test_english_matrix_still_has_an_independent_limit(self):
        with self.assertRaisesRegex(MatrixLimitError, "English matrix has 257"):
            prepare([{}] * 257, {}, [], {})

    def test_localized_matrix_still_has_an_independent_limit(self):
        with self.assertRaisesRegex(MatrixLimitError, "Localized matrix has 257"):
            prepare([], {}, [{}] * 257, {})

    @staticmethod
    def entries(count, batches, prefix="b"):
        return [{"batch_id": f"{prefix}{index % batches}", "platform": "linux",
                 "arch": "stx", "playbook": f"p{index}"} for index in range(count)]

    def test_batch_jobs_bound_the_batches_not_the_playbooks(self):
        # 300 playbook entries in 14 batches: 14 Test jobs, a valid matrix.
        result = prepare(self.entries(300, 14), {}, [], {}, batch_jobs=True)
        self.assertEqual(len(result["batch_matrix"]), 14)

    def test_batch_jobs_reject_a_combined_batch_matrix_over_the_limit(self):
        # Each half is within the limit; together they are not.
        with self.assertRaisesRegex(MatrixLimitError, "Batch matrix has 258"):
            prepare(self.entries(129, 129, "en"), {}, self.entries(129, 129, "zh"), {},
                    batch_jobs=True)

    def test_colliding_batch_ids_are_rejected(self):
        with self.assertRaisesRegex(ValueError, "batch IDs collide: duplicate"):
            prepare([], {"duplicate": {}}, [], {"duplicate": {}})


if __name__ == "__main__":
    unittest.main()
