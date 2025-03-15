<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
<<<<<<< HEAD
=======
import importlib.resources as pkg_resources
>>>>>>> 50d9aad... Update docs and type hints in grouper.py
from typing import Dict, Optional

import pandas as pd
import yaml

from daemon_analysis_tools.datamodels.question import Question


def _load_question_types(path: str) -> Dict[int, Dict]:
    """
    Load question metadata from a YAML file.

<<<<<<< HEAD
<<<<<<< HEAD
    Reads a YAML file and returns a dictionary mapping question numbers to a boolean
    value indicating whether the question is open.

    :return: Dictionary where keys are question numbers and values are True if the
=======
    Reads a YAML file and returns a dictionary mapping question numbers to a boolean 
    value indicating whether the question is open.

    :return: Dictionary where keys are question numbers and values are True if the 
>>>>>>> a41e68c... Move metadata outside of the package
        question is open, False otherwise.
=======
    Reads a YAML file and returns a dictionary mapping question numbers to question metadata.

    :return: Dictionary where keys are question numbers and values are dictionary with metadata.
>>>>>>> cd1b961... updated yaml saver
    """
    with open(path, "r") as file:
        question_metadata = yaml.safe_load(file)

    return question_metadata


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


<<<<<<< HEAD
def _initialize_question(
    grouped_questions: Dict[str, Dict[str, Dict[int, Question]]],
    publisher: str,
    journal: str,
    q_num: int,
    column: str,
    open_or_not: bool,
    question_id: str,
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
=======
    grouped_questions: dict, publisher: str, journal: str, q_num: int, column: str
):
    """
    Initialize a Question object in the grouped_questions dictionary if not already
    present.
>>>>>>> bb5b81c... Run pre-commit
    """

    if q_num not in grouped_questions[publisher][journal]:
        open_or_not = open_or_not
        question_id = question_id
        question = Question(text = column, is_open=open_or_not,question_id=question_id )
        grouped_questions[publisher][journal][q_num] = question

<<<<<<< HEAD

=======
>>>>>>> d3d7633... added more tests and fixed grouper
def _process_group(
    group: pd.DataFrame,
    question_metadata_dict: dict,
) -> Dict[int, Question]:
    """
    Process a single group of data (journal) and extract questions and answers.

    Iterates over each column in the DataFrame and, if the column is identified as a
    question, initializes a corresponding Question object (if needed) and adds each
    answer along with its explanation to the question.

    :param group: A DataFrame representing a group of data for a specific journal.
    :param question_metadata_dict: Dictionary mapping question numbers to their metadata (e.g., identifier and type).

    """
    questions_dict = {}
    for i, column in enumerate(group.columns): 
        if _is_question_column(column):
            q_num = int(column.split(".")[0])
            explanation_col = _get_explanation_column(group, i)
            question_id = question_metadata_dict[q_num]['identifier']
            open_or_not = question_metadata_dict[q_num]['type']=='open'
            if q_num not in questions_dict:
                question = Question(text=column, is_open=open_or_not, question_id=question_id)
                questions_dict[q_num] = question

            for idx, answer in enumerate(group[column]):
                explanation = (
                    group[explanation_col].iloc[idx]
                    if explanation_col is not None and explanation_col in group.columns
                    else ""
                )
                questions_dict[q_num]._add_answer(
                    answer, explanation
                )
    return questions_dict


def group_questions_by_journal(
    data: pd.DataFrame,
    question_metadata_file: str,
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

    question_metadata_dict = _load_question_types(question_metadata_file)
    for (publisher, journal), group in grouped_data:
        grouped_questions.setdefault(publisher, {}).setdefault(journal, {})
        grouped_questions[publisher][journal] = _process_group(group, question_metadata_dict)

    return grouped_questions
