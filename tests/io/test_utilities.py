import os
import tempfile
import unittest
from pathlib import Path

import pandas as pd
import yaml

from daemon_analysis_tools.io.utilities import (
    _read_yaml,
    _read_single_layer_metadata,
    _read_double_layer_metadata,
    _create_table_from_grouped_questions,
    _merge_single_layer,
    _normalize,
    _merge_answers_metadata,
    _fill_answer_metadata_fuzzy,
)
from daemon_analysis_tools.datamodels.question import Question


class DummyQuestion:
    def __init__(self, question_id, text, answers, correct_answer=None, discrepancy_reason=None):
        self.question_id = question_id
        self.text = text
        self.answers = answers
        self.correct_answer = correct_answer
        self.discrepancy_reason = discrepancy_reason

    def has_discrepancies(self):
        return self.discrepancy_reason is not None


class DummyAnswer:
    def __init__(self, text, explanation):
        self.text = text
        self.explanation = explanation


class TestUtilities(unittest.TestCase):

    def test_normalize(self):
        self.assertEqual(_normalize("  Hello. "), "hello")
        self.assertEqual(_normalize("Multiple   spaces"), "multiple spaces")
        self.assertIsNone(_normalize(None))
        self.assertIsNone(_normalize(123))

    def test_read_yaml_file_and_missing(self):
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
            yaml.dump({"foo": {"bar": 1}}, tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(_read_yaml(tmp_path), {"foo": {"bar": 1}})
            self.assertEqual(_read_yaml(None), {})
            self.assertEqual(_read_yaml("nonexistent.yaml"), {})
        finally:
            os.remove(tmp_path)

    def test_read_single_double_layer_metadata(self):
        content = {
            "q1": {"answer 1": {"score": 1.0}},
            "q2": {"answer 2": {"score": 0.5}},
        }
        with tempfile.NamedTemporaryFile("w", suffix=".yaml", delete=False) as tmp:
            yaml.dump(content, tmp)
            tmp_path = tmp.name
        try:
            self.assertEqual(_read_double_layer_metadata(tmp_path), content)
            self.assertEqual(_read_single_layer_metadata(tmp_path), content)
        finally:
            os.remove(tmp_path)

    def test_create_table_from_grouped_questions(self):
        q1 = DummyQuestion("q1", "Text 1", [DummyAnswer("Yes", "Reason")])
        q2 = DummyQuestion("q2", "Text 2", [], discrepancy_reason="Some reason", correct_answer=DummyAnswer("Yes", ""))
        grouped = {"Pub": {"Journal": {"q1": q1, "q2": q2}}}

        df = _create_table_from_grouped_questions(grouped)
        self.assertEqual(df.shape[0], 2)
        self.assertIn("final_answer", df.columns)
        self.assertEqual(df.loc[df["question_id"] == "q1", "final_answer"].values[0], None)
        self.assertEqual(df.loc[df["question_id"] == "q2", "final_answer"].values[0], "Yes")

    def test_merge_single_layer(self):
        df = pd.DataFrame({"journal": ["A", "B"]})
        metadata = {"A": {"score": 1.0}, "B": {"score": 2.0}}
        merged = _merge_single_layer(df, metadata, "journal")
        self.assertEqual(list(merged["score"]), [1.0, 2.0])

    def test_merge_answers_metadata_and_fuzzy(self):
        df = pd.DataFrame({
            "question_id": ["q1", "q1", "q1"],
            "final_answer": ["YES", "yes.", "No"],
        })
        meta = {
            "q1": {
                "yes": {"score": 1.0},
                "no": {"score": 0.0},
            }
        }
        merged = _merge_answers_metadata(df.copy(), meta)
        self.assertListEqual(sorted(merged["score"].dropna().tolist()), [0.0, 1.0, 1.0])

        # Now simulate typo with fuzzy fill
        df_typo = pd.DataFrame({
            "question_id": ["q1"],
            "final_answer": ["yess"]
        })
        df_merged = _merge_answers_metadata(df_typo.copy(), meta)
        filled = _fill_answer_metadata_fuzzy(df_merged, meta, threshold=80)
        self.assertEqual(filled["score"].iloc[0], 1.0)
