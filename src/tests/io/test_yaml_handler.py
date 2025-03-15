import os
import tempfile
import unittest
import yaml
from io import StringIO
from contextlib import redirect_stdout

# Import the functions to be tested.
from daemon_analysis_tools.io.yaml_handler import save_yaml_file, build_journal_dict

# Create dummy classes to simulate the Question and Answer behavior.
class DummyAnswer:
    def __init__(self, text: str, explanation: str):
        self.text = text
        self.explanation = explanation

    def __repr__(self):
        return f"DummyAnswer(text={self.text}, explanation={self.explanation})"


class DummyQuestion:
    def __init__(
        self,
        question_id: str,
        text: str,
        is_open: bool,
        answers: list,
        correct_answer=None,
        discrepancy_reason: str = None,
        has_discrepancies_val: bool = False,
    ):
        self.question_id = question_id
        self.text = text
        self.is_open = is_open
        self.answers = answers  # list of DummyAnswer objects
        self.correct_answer = correct_answer  # either a DummyAnswer or None
        self.discrepancy_reason = discrepancy_reason
        self._has_discrepancies = has_discrepancies_val

    def has_discrepancies(self) -> bool:
        return self._has_discrepancies

    def _add_answer(self, answer_text: str, explanation: str = "") -> None:
        self.answers.append(DummyAnswer(answer_text, explanation))


class TestBuildJournalDict(unittest.TestCase):
    def setUp(self):
        # Create two dummy questions.
        # Question 1: no correct answer, two answers, no discrepancies.
        q1 = DummyQuestion(
            question_id="Q1",
            text="What is your favorite color?",
            is_open=False,
            answers=[DummyAnswer("Blue", "I like blue"), DummyAnswer("Blue", "Blue is calming")],
            correct_answer=None,
            discrepancy_reason=None,
            has_discrepancies_val=False,
        )

        # Question 2: with correct answer, three answers, discrepancies present.
        q2 = DummyQuestion(
            question_id="Q2",
            text="What is 2+2?",
            is_open=False,
            answers=[
                DummyAnswer("4", "Correct arithmetic"),
                DummyAnswer("3", "Mistake"),
                DummyAnswer("4", "Reiterated")
            ],
            correct_answer=DummyAnswer("4", "Correct arithmetic"),
            discrepancy_reason="Multiple responses detected",
            has_discrepancies_val=True,
        )
        # Journal dictionary mapping question number (int) to DummyQuestion.
        self.journal = {1: q1, 2: q2}

    def test_build_journal_dict_structure(self):
        result = build_journal_dict(self.journal)
        # Check that keys are the question IDs from the dummy questions.
        self.assertIn("Q1", result)
        self.assertIn("Q2", result)

        # Check that basic fields are dumped correctly.
        q1_dict = result["Q1"]
        self.assertEqual(q1_dict["text"], "What is your favorite color?")
        self.assertEqual(q1_dict["N. encoders"], 2)
        self.assertFalse(q1_dict["has_discrepancies"])
        # Check respondent answers for q1.
        self.assertIn(0, q1_dict)
        self.assertEqual(q1_dict[0]["text"], "Blue")
        self.assertEqual(q1_dict[0]["explanation"], "I like blue")
        self.assertEqual(q1_dict["correct_answer"], None)
        self.assertIsNone(q1_dict["discrepancy_reason"])

        q2_dict = result["Q2"]
        self.assertEqual(q2_dict["text"], "What is 2+2?")
        self.assertEqual(q2_dict["N. encoders"], 3)
        self.assertTrue(q2_dict["has_discrepancies"])
        # Check correct answer field.
        self.assertIsInstance(q2_dict["correct_answer"], dict)
        self.assertEqual(q2_dict["correct_answer"]["text"], "4")
        self.assertEqual(q2_dict["correct_answer"]["explanation"], "Correct arithmetic")
        self.assertEqual(q2_dict["discrepancy_reason"], "Multiple responses detected")

    def test_build_journal_dict_end_to_end(self):
        # End-to-end test: Build dict and then dump and load via YAML.
        journal_dict = build_journal_dict(self.journal)
        dumped_yaml = yaml.dump(journal_dict, sort_keys=False)
        loaded = yaml.safe_load(dumped_yaml)
        # Check that the loaded YAML has the same structure.
        self.assertEqual(loaded["Q1"]["text"], "What is your favorite color?")
        self.assertEqual(loaded["Q2"]["correct_answer"]["text"], "4")


class TestSaveYAMLFile(unittest.TestCase):
    def setUp(self):
        # Create a simple dictionary to dump.
        self.data = {"test": {"key": "value"}}
        # Create a temporary file path.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.file_path = os.path.join(self.temp_dir.name, "output.yaml")

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_save_yaml_file_success(self):
        # Save YAML file.
        save_yaml_file(self.file_path, self.data)
        # Check that file exists and content is correct.
        self.assertTrue(os.path.exists(self.file_path))
        with open(self.file_path, "r") as file:
            loaded_data = yaml.safe_load(file)
        self.assertEqual(loaded_data, self.data)

    def test_save_yaml_file_file_exists(self):
        # Create file beforehand.
        with open(self.file_path, "w") as f:
            f.write("Existing content")
        # Capture output.
        with StringIO() as buf, redirect_stdout(buf):
            save_yaml_file(self.file_path, self.data)
            output = buf.getvalue()
        # Check that warning message is printed.
        self.assertIn("already exists", output)

    def test_save_yaml_file_exception(self):
        # Test writing to a directory path, which should trigger an exception branch.
        with StringIO() as buf, redirect_stdout(buf):
            # Passing the directory path instead of a file path.
            save_yaml_file(str(self.temp_dir), self.data)
            output = buf.getvalue()
        # The function should catch the exception and print a message containing "Exception:"
        assert "Exception:" in output or "already exists" in output

