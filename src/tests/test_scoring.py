import unittest

from daemon_analysis_tools.scoring import (
    assign_score,
    calculate_scores,
    normalize_scores,
)


class TestScoring(unittest.TestCase):
    def test_assign_score(self):
        multiple_choice_scores = {
            1: {"Option A": 1, "Option B": 0},
        }
        self.assertEqual(assign_score(1, "Option A", multiple_choice_scores), 1)
        self.assertEqual(assign_score(1, "Option B", multiple_choice_scores), 0)
        self.assertEqual(assign_score(1, "Option C", multiple_choice_scores), 0)

    # Add more tests for calculate_scores and normalize_scores


if __name__ == "__main__":
    unittest.main()
