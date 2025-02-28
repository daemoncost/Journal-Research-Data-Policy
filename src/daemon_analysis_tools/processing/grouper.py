import importlib.resources as pkg_resources
from typing import Dict, Optional

import pandas as pd
import yaml

from daemon_analysis_tools.datamodels.question import Question


def _load_question_types() -> Dict[int, bool]:
    """
    Load question types from a YAML file.

    Reads a YAML file located inside the package "daemon_analysis_tools.metadata"
    (file: "question_type.yaml") and returns a dictionary mapping question numbers
    to a boolean value indicating whether the question is open.

    :return: Dictionary where keys are question numbers and values are True if
             the question is open, False otherwise.
    """
    with pkg_resources.open_text(
        "daemon_analysis_tools.metadata", "question_type.yaml"
    ) as file:
        question_types = yaml.safe_load(file)

    return {int(q_num): (q_type == "open") for q_num, q_type in question_types.items()}


def _is_question_column(column: str) -> bool:
    """
    Determine if a column name indicates a question by checking if it starts with an
    integer.

    :param column: The column name.
    :return: True if the column name starts with an integer, False otherwise.
    """
    return column.split(".")[0].isdigit()


def _get_explanation_column(data: pd.DataFrame, index: int) -> Optional[str]:
    """
    Find the explanation column corresponding to a question column.

    Checks if the column immediately following the given index in the DataFrame's
    columns contains a specific prompt text. If found, returns the column name;
    otherwise, None.

    :param data: The DataFrame containing the columns.
    :param index: The index of the question column.
    :return: The explanation column name if it matches the criteria, otherwise None.
    """
    next_column = data.columns[index + 1] if index + 1 < len(data.columns) else None
    if (
        next_column
        and "Please add the text from the RDP that supports your answer below:"
        in next_column
    ):
        return next_column
    return None


def _initialize_question(
    grouped_questions: Dict[str, Dict[str, Dict[int, Question]]],
    publisher: str,
    journal: str,
    q_num: int,
    column: str,
) -> None:
    """
    Initialize a Question object in the grouped_questions dictionary if not already
    present.

    The function loads question types from configuration and, if a question identified
    by q_num does not already exist for the specified publisher and journal, creates a
    new Question instance with its 'is_open' property set accordingly.

    :param grouped_questions: Nested dictionary structured as:
                              {publisher: {journal: {question_number: Question}}}.
    :param publisher: The publisher name.
    :param journal: The journal name.
    :param q_num: The question number.
    :param column: The column name containing the question text.
    """
    question_types_dict = _load_question_types()
    if q_num not in grouped_questions[publisher][journal]:
        question = Question(column)
        question.is_open = question_types_dict[q_num]
        grouped_questions[publisher][journal][q_num] = question


def _process_group(
    group: pd.DataFrame,
    grouped_questions: Dict[str, Dict[str, Dict[int, Question]]],
    publisher: str,
    journal: str,
    data: pd.DataFrame,
) -> None:
    """
    Process a single group of data (journal) and extract questions and answers.

    Iterates over each column in the DataFrame and, if the column is identified as a
    question, initializes a corresponding Question object (if needed) and adds each
    answer along with its explanation to the question.

    :param group: A DataFrame representing a group of data for a specific journal.
    :param grouped_questions: Nested dictionary to store questions, structured as:
                              {publisher: {journal: {question_number: Question}}}.
    :param publisher: The publisher name.
    :param journal: The journal name.
    :param data: The complete DataFrame containing all columns.
    """
    for i, column in enumerate(data.columns):
        if _is_question_column(column):
            q_num = int(column.split(".")[0])
            explanation_col = _get_explanation_column(data, i)
            _initialize_question(grouped_questions, publisher, journal, q_num, column)

            for idx, answer in enumerate(group[column]):
                explanation = (
                    group[explanation_col].iloc[idx]
                    if explanation_col is not None and explanation_col in group.columns
                    else ""
                )
                grouped_questions[publisher][journal][q_num]._add_answer(
                    answer, explanation
                )


def group_questions_by_journal(
    data: pd.DataFrame,
) -> Dict[str, Dict[str, Dict[int, Question]]]:
    """
    Group questions by publisher and journal.

    Groups the provided DataFrame by "Publisher Name" and "journal" columns,
    then processes each group to extract questions and associated answers into a nested
    dictionary.

    :param data: A DataFrame containing columns for publisher, journal, and questions.
    :return: A nested dictionary structured as:
             {publisher: {journal: {question_number: Question}}}.
    """
    grouped_data = data.groupby(["Publisher Name", "journal"])
    grouped_questions: Dict[str, Dict[str, Dict[int, Question]]] = {}

    for (publisher, journal), group in grouped_data:
        grouped_questions.setdefault(publisher, {}).setdefault(journal, {})
        _process_group(group, grouped_questions, publisher, journal, data)

    return grouped_questions
