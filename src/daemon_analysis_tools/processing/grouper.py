import importlib.resources as pkg_resources

import pandas as pd
import yaml

from daemon_analysis_tools.datamodels.question import Question


def _load_question_types() -> dict:
    """
    Reads a YAML file located inside a package (config/question.yaml)
    and returns a dictionary mapping question numbers to their types.

    :return: Dictionary where keys are question numbers (int), values are `True` if
        open, `False` otherwise.
    """
    with pkg_resources.open_text(
        "daemon_analysis_tools.metadata", "question_type.yaml"
    ) as file:
        question_types = yaml.safe_load(file)

    return {int(q_num): (q_type == "open") for q_num, q_type in question_types.items()}


def _is_question_column(column: str) -> bool:
    """Checks if a column name starts with an integer (indicating a question)."""
    return column.split(".")[0].isdigit()


def _get_explanation_column(data: pd.DataFrame, index: int) -> str:
    """Finds the explanation column corresponding to a question column."""
    next_column = data.columns[index + 1] if index + 1 < len(data.columns) else None
    if (
        next_column
        and "Please add the text from the RDP that supports your answer below:"
        in next_column
    ):
        return next_column
    return None


def _initialize_question(
    grouped_questions: dict, publisher: str, journal: str, q_num: int, column: str
):
    """
    Initializes a Question object in the grouped_questions dictionary if not already
    present.
    """
    question_types_dict = _load_question_types()
    if q_num not in grouped_questions[publisher][journal]:
        question = Question(column)
        question.is_open = question_types_dict[q_num]
        grouped_questions[publisher][journal][q_num] = question


def _process_group(
    group: pd.DataFrame,
    grouped_questions: dict,
    publisher: str,
    journal: str,
    data: pd.DataFrame,
):
    """Processes a single group (journal) and extracts questions and answers."""
    for i, column in enumerate(data.columns):
        if _is_question_column(column):
            q_num = int(column.split(".")[0])
            explanation_col = _get_explanation_column(data, i)

            _initialize_question(grouped_questions, publisher, journal, q_num, column)

            for idx, answer in enumerate(group[column]):
                explanation = (
                    group[explanation_col].iloc[idx]
                    if explanation_col in group.columns
                    else ""
                )
                grouped_questions[publisher][journal][q_num]._add_answer(
                    answer, explanation
                )


def group_questions_by_journal(data: pd.DataFrame) -> dict:
    """Groups questions by publisher and journal."""
    grouped_data = data.groupby(["Publisher Name", "journal"])
    grouped_questions = {}

    for (publisher, journal), group in grouped_data:
        grouped_questions.setdefault(publisher, {}).setdefault(journal, {})
        _process_group(group, grouped_questions, publisher, journal, data)

    return grouped_questions
