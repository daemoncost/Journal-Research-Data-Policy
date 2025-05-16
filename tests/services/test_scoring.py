import os
import unittest

from daemon_analysis_tools.datamodels.question import Question
from daemon_analysis_tools.io.yaml_base_handler import load_yaml
from daemon_analysis_tools.services.scoring import (
    _get_maximum_possible_score,
    _get_question_type_lookup,
    get_journal_score,
    get_question_score,
)


class TestScoring(unittest.TestCase):
    def setUp(self):
        base_dir = os.path.dirname(os.path.abspath(__file__))
        data_dir = os.path.join(base_dir, "..", "..", "data", "metadata")

        self.question_type = load_yaml(os.path.join(data_dir, "question_type.yaml"))
        self.multiple_choice_scores = load_yaml(
            os.path.join(data_dir, "question_metadata_score.yaml")
        )

        # Create a dummy Question with one answer.
        self.question = Question(
            question_id="rdp_exist",
            text="1. Existence of research data policy",
            is_open=False,
        )
        self.question._add_answer("research data policy (rdp) exists.", "Explanation A")
        self.question._set_correct_answer(self.question.answers[0])

        # Create a dummy Journal with one question.
        self.journal = {"rdp_exist": self.question}

    def test_get_maximum_possible_score(self):
        max_score = _get_maximum_possible_score(self.multiple_choice_scores)

        self.assertEqual(max_score, 19.0)

    def test_get_question_score(self):
        question_number_lookup = _get_question_type_lookup(self.multiple_choice_scores)

        score = get_question_score(
            self.question.question_id,
            self.question,
            self.multiple_choice_scores,
            self.question_type,
            question_number_lookup,
        )

        self.assertEqual(score, 1.0)

    def test_get_journal_score(self):
        score = get_journal_score(self.journal)

        self.assertAlmostEqual(score, 1.0 / 19.0)


if __name__ == "__main__":
    unittest.main()
