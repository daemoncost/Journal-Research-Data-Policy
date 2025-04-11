import os
import tempfile
import unittest
from contextlib import redirect_stdout
from io import StringIO

import yaml

from daemon_analysis_tools.datamodels.question import Question

# Import the functions to be tested.
from daemon_analysis_tools.io.yaml_handler import (
    build_journal_dict,
    save_answers_to_yaml,
    save_yaml_file,
    load_answers_from_yaml,
    _load_questions_from_file,
    _build_question
)
from daemon_analysis_tools.services.discrepancy_resolver import resolve_discrepancy


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


def create_dummy_grouped_questions():
    # Publisher1 with one journal having two questions.
    q1 = DummyQuestion(
        question_id="Q1",
        text="What is your favorite color?",
        is_open=False,
        answers=[],
    )
    q1._add_answer("Blue", "I like blue")
    q1._add_answer("Blue", "Blue is calming")

    q2 = DummyQuestion(
        question_id="Q2",
        text="What is 2+2?",
        is_open=False,
        answers=[],
    )
    q2._add_answer("4", "Correct arithmetic")
    q2._add_answer("3", "Mistake")
    q2._add_answer("4", "Reiterated")

    publisher1 = {"JournalA": {1: q1, 2: q2}}

    # Publisher2 with one journal having one question.
    q3 = DummyQuestion(
        question_id="Q3",
        text="What is the capital of France?",
        is_open=False,
        answers=[],
    )
    q3._add_answer("Paris", "Correct")
    publisher2 = {"JournalB": {1: q3}}

    return {"Publisher1": publisher1, "Publisher2": publisher2}


class TestBuildJournalDict(unittest.TestCase):
    def setUp(self):
        # Create two dummy questions.
        # Question 1: no correct answer, two answers, no discrepancies.
        q1 = DummyQuestion(
            question_id="Q1",
            text="What is your favorite color?",
            is_open=False,
            answers=[
                DummyAnswer("Blue", "I like blue"),
                DummyAnswer("Blue", "Blue is calming"),
            ],
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
                DummyAnswer("4", "Reiterated"),
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
        # The function should catch the exception and
        # print a message containing "Exception:"
        assert "Exception:" in output or "already exists" in output


class TestSaveAnswersToYaml(unittest.TestCase):
    def setUp(self):
        # Create a temporary directory to save YAML files.
        self.temp_dir_obj = tempfile.TemporaryDirectory()
        self.temp_dir = self.temp_dir_obj.name
        self.grouped_questions = create_dummy_grouped_questions()

    def tearDown(self):
        self.temp_dir_obj.cleanup()

    def test_save_answers_to_yaml_creates_files(self):
        # Call the function.
        save_answers_to_yaml(self.grouped_questions, parent_folder=self.temp_dir)

        # Check that directories for each publisher are created.
        pub1_dir = os.path.join(self.temp_dir, "Publisher1")
        pub2_dir = os.path.join(self.temp_dir, "Publisher2")
        self.assertTrue(os.path.isdir(pub1_dir))
        self.assertTrue(os.path.isdir(pub2_dir))

        # Check that each journal file is created.
        journalA_file = os.path.join(pub1_dir, "JournalA.yaml")
        journalB_file = os.path.join(pub2_dir, "JournalB.yaml")
        self.assertTrue(os.path.isfile(journalA_file))
        self.assertTrue(os.path.isfile(journalB_file))

        # Load and verify content for JournalA.
        with open(journalA_file, "r") as f:
            journalA_data = yaml.safe_load(f)
        # Expecting two keys corresponding to question IDs "Q1" and "Q2".
        self.assertIn("Q1", journalA_data)
        self.assertIn("Q2", journalA_data)
        # Verify one field, e.g., text.
        self.assertEqual(journalA_data["Q1"]["text"], "What is your favorite color?")
        self.assertEqual(journalA_data["Q2"]["text"], "What is 2+2?")

        # Load and verify content for JournalB.
        with open(journalB_file, "r") as f:
            journalB_data = yaml.safe_load(f)
        self.assertIn("Q3", journalB_data)
        self.assertEqual(journalB_data["Q3"]["text"], "What is the capital of France?")

    def test_save_only_parameter(self):
        # Call the function with save_only for Publisher1.
        save_answers_to_yaml(
            self.grouped_questions,
            parent_folder=self.temp_dir,
            save_only=["Publisher1"],
        )

        pub1_dir = os.path.join(self.temp_dir, "Publisher1")
        pub2_dir = os.path.join(self.temp_dir, "Publisher2")
        self.assertTrue(os.path.isdir(pub1_dir))
        # Publisher2 should not be created.
        self.assertFalse(os.path.isdir(pub2_dir))

    def test_save_yaml_file_warning(self):
        # Test behavior when the YAML file already exists.
        # First, create a file manually.
        publisher_dir = os.path.join(self.temp_dir, "Publisher1")
        os.makedirs(publisher_dir, exist_ok=True)
        journal_file = os.path.join(publisher_dir, "JournalA.yaml")
        with open(journal_file, "w") as f:
            f.write("Existing content")

        # Capture printed output.
        with StringIO() as buf, redirect_stdout(buf):
            save_answers_to_yaml(
                self.grouped_questions,
                parent_folder=self.temp_dir,
                save_only=["Publisher1"],
            )
            output = buf.getvalue()
        # Check that the warning message indicates that the file already exists.
        self.assertIn("already exists", output)


class TestBuildJournalDictEndToEnd(unittest.TestCase):
    def test_end_to_end_build_journal_dict(self):
        # Create Question 1 (no discrepancy)
        q1 = Question(
            question_id="Q1", text="What is your favorite color?", is_open=False
        )
        q1._add_answer("Blue", "I like blue")
        q1._add_answer("Blue", "I prefer blue")
        # We resolve discrepancy to get the right answer assigned
        resolve_discrepancy(q1)

        # Create Question 2 (with discrepancy)
        q2 = Question(question_id="Q2", text="What is 2+2?", is_open=False)
        q2._add_answer("3", "My father told me so")
        q2._add_answer("4", "I learnt at school")
        q2._add_answer("5", "I feel like that")

        # Create Question 3 (with unresolved discrepancy)
        q3 = Question(question_id="Q3", text="Do you breath sometimes?", is_open=False)
        q3._add_answer("Yes", "We all do.")
        q3._add_answer("No", "Too expensive")

        # Set correct answer using resolve_discrepancy:
        resolve_discrepancy(q2, 1, "Correct arithmetic")

        # Assemble a journal dictionary mapping question numbers to questions.
        journal = {1: q1, 2: q2, 3: q3}

        # Build the journal dictionary for YAML dumping.
        result = build_journal_dict(journal)

        # Verify that the keys are the question IDs.
        self.assertIn("Q1", result)
        self.assertIn("Q2", result)
        self.assertIn("Q3", result)

        # Verify Question 1 details.
        q1_dict = result["Q1"]
        self.assertEqual(q1_dict["text"], "What is your favorite color?")
        self.assertEqual(q1_dict["N. encoders"], 2)
        self.assertFalse(q1_dict["has_discrepancies"])
        self.assertEqual(
            q1_dict["correct_answer"], {"text": "Blue", "explanation": "I like blue"}
        )
        self.assertIsNone(q1_dict["discrepancy_reason"])
        # Check one respondent's answer.
        self.assertEqual(q1_dict[0]["text"], "Blue")
        self.assertEqual(q1_dict[0]["explanation"], "I like blue")

        # Verify Question 2 details.
        q2_dict = result["Q2"]
        self.assertEqual(q2_dict["text"], "What is 2+2?")
        self.assertEqual(q2_dict["N. encoders"], 3)
        self.assertTrue(q2_dict["has_discrepancies"])
        # Correct answer details should be a dict with the proper text and explanation.
        self.assertIsInstance(q2_dict["correct_answer"], dict)
        self.assertEqual(q2_dict["correct_answer"]["text"], "4")
        self.assertEqual(q2_dict["correct_answer"]["explanation"], "I learnt at school")
        self.assertEqual(q2_dict["discrepancy_reason"], "Correct arithmetic")

        # Verify Question 3 details.
        q3_dict = result["Q3"]
        self.assertEqual(q3_dict["text"], "Do you breath sometimes?")
        self.assertEqual(q3_dict["N. encoders"], 2)
        self.assertTrue(q3_dict["has_discrepancies"])
        self.assertIsNone(q3_dict["correct_answer"])
        self.assertIsNone(q3_dict["discrepancy_reason"])


class TestYAMLHandlerFunctions(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.publisher = "TestPublisher"
        self.journal = "TestJournal"
        self.yaml_path = os.path.join(
            self.temp_dir.name, self.publisher, f"{self.journal}.yaml"
        )
        os.makedirs(os.path.dirname(self.yaml_path), exist_ok=True)

        self.yaml_content = {
            "Q1": {
                "text": "What is 2+2?",
                "correct_answer": 1,
                "has_discrepancies": False,
                1: {"text": "4", "explanation": "Correct"},
                2: {"text": "3", "explanation": "Incorrect"},
            }
        }

        with open(self.yaml_path, "w") as f:
            yaml.dump(self.yaml_content, f)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_build_question(self):

        question = _build_question("Q1", self.yaml_content["Q1"])
        self.assertEqual(question.text, "What is 2+2?")
        self.assertEqual(len(question.answers), 2)
        self.assertEqual(question.answers[0].text, "4")

    @unittest.mock.patch("daemon_analysis_tools.io.yaml_handler.Question.has_discrepancies", return_value=False)
    def test__load_questions_from_file(self, mock_has_disc):

        questions = _load_questions_from_file(
            self.yaml_path, self.publisher, self.journal
        )

        self.assertIn("Q1", questions)
        q = questions["Q1"]
        self.assertEqual(q.text, "What is 2+2?")
        self.assertEqual(len(q.answers), 2)
        self.assertIsNotNone(q.correct_answer)  # Optional: validate it was resolved



    @unittest.mock.patch("daemon_analysis_tools.io.yaml_handler.Question.has_discrepancies", return_value=False)
    def test_load_answers_from_yaml(self, mock_has_disc):

        result = load_answers_from_yaml(self.temp_dir.name)

        self.assertIn(self.publisher, result)
        self.assertIn(self.journal, result[self.publisher])
        self.assertIn("Q1", result[self.publisher][self.journal])
        self.assertIsNotNone(result[self.publisher][self.journal]["Q1"].correct_answer)

