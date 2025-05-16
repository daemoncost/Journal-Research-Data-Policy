import unittest
from io import StringIO
from unittest.mock import patch

from daemon_analysis_tools.datamodels.question import Question
from daemon_analysis_tools.services.discrepancy_resolver import (
    _prompt_for_resolution,
    _select_correct_answer,
    resolve_discrepancy,
)


class TestSelectCorrectAnswer(unittest.TestCase):
    def setUp(self):
        # Create a dummy Question with three answers.
        self.question = Question(
            question_id="Q1", text="Sample question?", is_open=False
        )
        self.question._add_answer("Answer A", "Explanation A")
        self.question._add_answer("Answer B", "Explanation B")
        self.question._add_answer("Answer C", "Explanation C")

    def test_select_correct_answer_by_string(self):
        # When providing a correct answer as string.
        selected, idx = _select_correct_answer(self.question, "Answer B")
        self.assertEqual(selected.text, "Answer B")
        self.assertEqual(idx, 1)

    def test_select_correct_answer_by_index(self):
        # When providing a correct answer as index.
        selected, idx = _select_correct_answer(self.question, 2)
        self.assertEqual(selected.text, "Answer C")
        self.assertEqual(idx, 2)

    def test_select_correct_answer_not_found_string(self):
        # Providing an answer text that doesn't exist should raise ValueError.
        with self.assertRaises(ValueError):
            _select_correct_answer(self.question, "Nonexistent Answer")

    def test_select_correct_answer_invalid_index(self):
        # Providing an out-of-range index should raise ValueError.
        with self.assertRaises(ValueError):
            _select_correct_answer(self.question, 10)


class TestPromptForResolution(unittest.TestCase):
    def setUp(self):
        # Create a dummy Question with two answers.
        self.question = Question(
            question_id="Q2", text="Another question?", is_open=False
        )
        self.question._add_answer("First Answer", "First Explanation")
        self.question._add_answer("Second Answer", "Second Explanation")

    @patch("builtins.input", side_effect=["1", "Reason for choosing second answer"])
    def test_prompt_for_resolution(self, mock_input):
        # Capture printed output if needed.
        with patch("sys.stdout", new=StringIO()):
            index, reason = _prompt_for_resolution(self.question)
        self.assertEqual(index, 1)
        self.assertEqual(reason, "Reason for choosing second answer")


class TestResolveDiscrepancy(unittest.TestCase):
    def setUp(self):
        # Create a dummy Question with discrepancies.
        self.question = Question(
            question_id="Q3", text="Discrepant question?", is_open=False
        )
        self.question._add_answer("Opt1", "Expl1")
        self.question._add_answer("Opt2", "Expl2")
        self.question._add_answer("Opt3", "Expl3")

    def test_resolve_discrepancy_non_interactive_string(self):
        # Simulate discrepancies: assume question.has_discrepancies() returns True.
        # We don't override it here since our dummy Question
        # implementation can be used as is.
        # Provide correct_answer as string and a discrepancy reason.
        resolve_discrepancy(
            self.question,
            correct_answer="Opt2",
            discrepancy_reason="Matches policy",
            interactive=False,
        )
        self.assertIsNotNone(self.question.correct_answer)
        self.assertEqual(self.question.correct_answer.text, "Opt2")
        self.assertEqual(self.question.correct_answer_encoder_id, 1)
        self.assertEqual(self.question.discrepancy_reason, "Matches policy")

    def test_resolve_discrepancy_non_interactive_index(self):
        # Provide correct_answer as an integer.
        resolve_discrepancy(
            self.question,
            correct_answer=2,
            discrepancy_reason="Index selected",
            interactive=False,
        )
        self.assertIsNotNone(self.question.correct_answer)
        self.assertEqual(self.question.correct_answer.text, "Opt3")
        self.assertEqual(self.question.correct_answer_encoder_id, 2)
        self.assertEqual(self.question.discrepancy_reason, "Index selected")

    @patch("builtins.input", side_effect=["0", "Reason provided interactively"])
    def test_resolve_discrepancy_interactive(self, mock_input):
        # Test interactive mode when correct_answer is not provided.
        # We first force the question to have discrepancies.
        resolve_discrepancy(self.question, interactive=True)
        # With our dummy inputs, the correct index should be 0.
        self.assertIsNotNone(self.question.correct_answer)
        self.assertEqual(self.question.correct_answer.text, "Opt1")
        self.assertEqual(self.question.correct_answer_encoder_id, 0)
        self.assertEqual(
            self.question.discrepancy_reason, "Reason provided interactively"
        )

    def test_resolve_discrepancy_no_discrepancy(self):
        # For a question with no discrepancies, override has_discrepancies.
        self.question.has_discrepancies = lambda: False
        self.question.correct_answer = None
        resolve_discrepancy(
            self.question,
            correct_answer=0,
            discrepancy_reason="None needed",
            interactive=False,
        )
        self.assertIsNotNone(self.question.correct_answer)
        self.assertEqual(self.question.correct_answer.text, "Opt1")
        # In our implementation, when there are no discrepancies,
        # encoder_id is not set, so it remains None.
        self.assertIsNone(self.question.correct_answer_encoder_id)

    def test_resolve_discrepancy_missing_reason(self):
        # If discrepancy_reason is not provided, it should raise a ValueError.
        with self.assertRaises(ValueError):
            resolve_discrepancy(
                self.question,
                correct_answer="Opt1",
                discrepancy_reason=None,
                interactive=False,
            )


if __name__ == "__main__":
    unittest.main()
