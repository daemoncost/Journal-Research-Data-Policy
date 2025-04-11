import io
import sys
import unittest
from unittest.mock import patch

from daemon_analysis_tools.datamodels.question import Answer, Question


# A dummy jaccard_similarity for testing open questions.
def dummy_jaccard_similarity(answer_texts):
    # For testing purposes, if there are two different answers, return > 0.55,
    # otherwise < 0.55.
    if len(set(answer_texts)) > 1:
        return 0.6
    return 0.5


class TestAnswer(unittest.TestCase):
    def test_answer_initialization_default_explanation(self):
        ans = Answer("Test answer")
        self.assertEqual(ans.text, "Test answer")
        self.assertEqual(ans.explanation, "")

    def test_answer_initialization_with_explanation(self):
        ans = Answer("Test answer", "Detailed explanation")
        self.assertEqual(ans.text, "Test answer")
        self.assertEqual(ans.explanation, "Detailed explanation")

    def test_answer_repr(self):
        ans = Answer("Test answer", "Some explanation")
        rep = repr(ans)
        self.assertIn("Test answer", rep)
        self.assertIn("Some explanation", rep)


class TestQuestion(unittest.TestCase):
    def setUp(self):
        # Create a basic Question for tests.
        self.question = Question(
            question_id="Q1", text="What is the answer?", is_open=False
        )

    def test_question_initialization(self):
        self.assertEqual(self.question.question_id, "Q1")
        self.assertEqual(self.question.text, "What is the answer?")
        self.assertFalse(self.question.is_open)
        self.assertEqual(len(self.question.answers), 0)
        self.assertIsNone(self.question.correct_answer)
        self.assertIsNone(self.question.correct_answer_encoder_id)
        self.assertIsNone(self.question.discrepancy_reason)

    def test_add_answer(self):
        self.question._add_answer("Answer 1", "Explanation 1")
        self.assertEqual(len(self.question.answers), 1)
        self.assertEqual(self.question.answers[0].text, "Answer 1")
        self.assertEqual(self.question.answers[0].explanation, "Explanation 1")

    def test_has_discrepancies_non_open(self):
        # For non open question: two different answers -> discrepancy True.
        self.question._add_answer("A")
        self.question._add_answer("B")
        self.assertTrue(self.question.has_discrepancies())
        # For non open question: two identical answers -> discrepancy False.
        q2 = Question(question_id="Q2", text="Test?", is_open=False)
        q2._add_answer("A")
        q2._add_answer("A")
        self.assertFalse(q2.has_discrepancies())

    @patch(
        "daemon_analysis_tools.datamodels.question.jaccard_similarity",
        side_effect=dummy_jaccard_similarity,
    )
    def test_has_discrepancies_open(self, mock_jaccard):
        open_question = Question(question_id="Q3", text="Open question?", is_open=True)

        # One answer → expected to return True (insufficient for similarity comparison)
        open_question._add_answer("Answer")
        self.assertTrue(open_question.has_discrepancies())

        # Two answers → dummy similarity = 0.6 > 0.55 → returns False
        open_question = Question(question_id="Q4", text="Open question?", is_open=True)
        open_question._add_answer("Answer1")
        open_question._add_answer("Answer2")
        self.assertFalse(open_question.has_discrepancies())

    def test_get_final_answer_raises(self):
        q = Question(question_id="Q10", text="Test question", is_open=False)
        with self.assertRaises(ValueError):
            q.get_final_answer()

    def test_print_qa(self):
        q = Question(question_id="Q11", text="Print test?", is_open=False)
        q._add_answer("A", "Explanation A")
        # Capture printed output.
        captured_output = io.StringIO()
        sys.stdout = captured_output
        q.print_qa()
        sys.stdout = sys.__stdout__
        output = captured_output.getvalue()
        self.assertIn("Print test?", output)
        self.assertIn("Answer: A", output)
        self.assertIn("Explanation: Explanation A", output)

    def test_question_repr(self):
        rep = repr(self.question)
        self.assertIn("Q1", rep)
        self.assertIn("What is the answer?", rep)
        self.assertIn("is_open", rep)
