import os
import tempfile
import unittest
import pandas as pd
import yaml

from daemon_analysis_tools.processing.grouper import (
    _load_question_types,
    _is_question_column,
    _get_explanation_column,
    _process_group,
    group_questions_by_journal,
)
from daemon_analysis_tools.datamodels.question import Question


class TestJournalDictFunctions(unittest.TestCase):
    def setUp(self):
        # Create dummy YAML content for question metadata.
        self.question_metadata = {
            1: {"identifier": "Q1ID", "type": "multiple_choice"},
            2: {"identifier": "Q2ID", "type": "open"}
        }
        # Write temporary YAML file.
        self.temp_yaml = tempfile.NamedTemporaryFile(mode="w+", delete=False, suffix=".yaml")
        yaml.dump(self.question_metadata, self.temp_yaml)
        self.temp_yaml.close()

    def tearDown(self):
        os.unlink(self.temp_yaml.name)

    def test_load_question_types(self):
        metadata = _load_question_types(self.temp_yaml.name)
        self.assertEqual(metadata, self.question_metadata)

    def test_is_question_column(self):
        self.assertTrue(_is_question_column("1. Existence of research data policy"))
        self.assertFalse(_is_question_column("Publisher Name"))
    
    def test_get_explanation_column(self):
        # Create a dummy DataFrame with a question column followed by an explanation column.
        df = pd.DataFrame({
            "1. Existence of research data policy": ["Ans1", "Ans2"],
            "Please add the text from the RDP that supports your answer below:": ["Exp1", "Exp2"],
            "Other": [1, 2]
        })
        # For index 0 (the question column), explanation column should be the second column.
        explanation = _get_explanation_column(df, 0)
        self.assertEqual(explanation, "Please add the text from the RDP that supports your answer below:")

    def test_process_group(self):
        # Create a dummy DataFrame simulating a journal group.
        # Two question columns: "1. ..." and "2. ..." with corresponding explanation columns.
        df = pd.DataFrame({
            "1. Existence of research data policy": ["Answer1", "Answer1_dup"],
            "Please add the text from the RDP that supports your answer below:": ["Exp1", "Exp1_dup"],
            "2. Some open question": ["Answer2", "Answer2_dup"],
            "Please add the text from the RDP that supports your answer below:.1": ["Exp2", "Exp2_dup"],
        })
        questions_dict = _process_group(df, self.question_metadata)
        # Verify that both questions (keys 1 and 2) are in the result.
        self.assertIn(1, questions_dict)
        self.assertIn(2, questions_dict)
        # Check question 1 details.
        q1 = questions_dict[1]
        self.assertEqual(q1.text, "1. Existence of research data policy")
        self.assertEqual(len(q1.answers), 2)
        # Check question 2 details.
        q2 = questions_dict[2]
        self.assertEqual(q2.text, "2. Some open question")
        self.assertEqual(len(q2.answers), 2)

    def test_group_questions_by_journal(self):
        # Create a dummy DataFrame with columns for Publisher, journal, and question data.
        df = pd.DataFrame({
            "Publisher Name": ["PubA", "PubA", "PubB"],
            "journal": ["Journal1", "Journal1", "Journal2"],
            "1. Existence of research data policy": ["Answer1", "Answer1_dup", "Answer3"],
            "Please add the text from the RDP that supports your answer below:": ["Exp1", "Exp1_dup", "Exp3"],
            "2. Some open question": ["Answer2", "Answer2_dup", "Answer4"],
            "Please add the text from the RDP that supports your answer below:.1": ["Exp2", "Exp2_dup", "Exp4"],
        })
        grouped = group_questions_by_journal(df, self.temp_yaml.name)
        # Check that publishers exist.
        self.assertIn("PubA", grouped)
        self.assertIn("PubB", grouped)
        # For PubA, Journal1 should have questions 1 and 2.
        pubA_journal1 = grouped["PubA"]["Journal1"]
        self.assertIn(1, pubA_journal1)
        self.assertIn(2, pubA_journal1)
        self.assertEqual(pubA_journal1[1].text, "1. Existence of research data policy")
        self.assertEqual(len(pubA_journal1[1].answers), 2)
        self.assertEqual(pubA_journal1[2].text, "2. Some open question")
        self.assertEqual(len(pubA_journal1[2].answers), 2)
        # For PubB, Journal2 should have questions 1 and 2 with one row each.
        pubB_journal2 = grouped["PubB"]["Journal2"]
        self.assertIn(1, pubB_journal2)
        self.assertIn(2, pubB_journal2)
        self.assertEqual(pubB_journal2[1].text, "1. Existence of research data policy")
        self.assertEqual(len(pubB_journal2[1].answers), 1)
        self.assertEqual(pubB_journal2[2].text, "2. Some open question")
        self.assertEqual(len(pubB_journal2[2].answers), 1)


if __name__ == "__main__":
    unittest.main()
