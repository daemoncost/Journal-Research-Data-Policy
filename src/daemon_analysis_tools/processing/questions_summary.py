from pathlib import Path
from typing import Dict, Optional, Union

import pandas as pd

from daemon_analysis_tools.datamodels.question import Question
from daemon_analysis_tools.io.utilities import (
    _create_table_from_grouped_questions,
    _merge_answers_metadata,
    _merge_single_layer,
    _read_double_layer_metadata,
    _read_single_layer_metadata,
)


def create_answers_summary_with_metadata(
    grouped_question: Dict[str, Dict[str, Dict[str, Question]]],
    publishers_metadata_yaml: Optional[Union[str, Path]] = None,
    journals_metadata_yaml: Optional[Union[str, Path]] = None,
    questions_metadata_yaml: Optional[Union[str, Path]] = None,
    answers_metadata_yaml: Optional[Union[str, Path]] = None,
) -> pd.DataFrame:
    """
    Build a summary table, enrich with optional metadata, and write to CSV.

    Parameters
    ----------
    grouped_question
        Nested dict as returned by `load_answers_from_yaml`.
    csv_file_path
        Destination CSV.
    publishers_metadata_yaml, journals_metadata_yaml, questions_metadata_yaml
        Single-layer YAMLs (`key: {prop: value}`).
    answers_metadata_yaml
        Double-layer YAML (`question_id: {answer_text: {prop: value}}`).
    """
    # 1. core table
    df = _create_table_from_grouped_questions(grouped_question)

    # 2. metadata enrichment (order: pub → journal → question → answer)
    df = _merge_single_layer(
        df, _read_single_layer_metadata(publishers_metadata_yaml), "publisher"
    )
    df = _merge_single_layer(
        df, _read_single_layer_metadata(journals_metadata_yaml), "journal"
    )
    df = _merge_single_layer(
        df, _read_single_layer_metadata(questions_metadata_yaml), "question_id"
    )
    df = _merge_answers_metadata(df, _read_double_layer_metadata(answers_metadata_yaml))

    # 3. return
    return df
