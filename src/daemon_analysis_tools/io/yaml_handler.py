import os
from glob import glob
from typing import Dict, List, Optional

import yaml

from daemon_analysis_tools.datamodels.question import Question
from daemon_analysis_tools.io.yaml_base_handler import save_yaml_file
from daemon_analysis_tools.services.discrepancy_resolver import (
    resolve_discrepancy,
)


def build_journal_dict(journal: Dict[int, "Question"]) -> Dict:
    """Build a dictionary from a journal's questions for YAML dumping.

    :param journal: A dictionary mapping question numbers to Question objects.
    :return: A dictionary with question IDs as keys and their details as values.
    """
    journal_dict = {}
    for question_number, question in journal.items():
        answers = question.answers
        question_dict = {
            "text": question.text,
            "N. encoders": len(answers),
            "has_discrepancies": question.has_discrepancies(),
        }
        # Add each respondent's answer
        for respondent_number, answer in enumerate(answers):
            question_dict[respondent_number] = {
                "text": answer.text,
                "explanation": answer.explanation,
            }
        # Add correct answer details if available
        if question.correct_answer is None:
            question_dict["correct_answer"] = None
        else:
            question_dict["correct_answer"] = {
                "text": question.correct_answer.text,
                "explanation": question.correct_answer.explanation,
            }
        # Always include discrepancy reason (could be None)
        question_dict["discrepancy_reason"] = question.discrepancy_reason

        journal_dict[question.question_id] = question_dict
    return journal_dict


def save_answers_to_yaml(
    grouped_questions: Dict[str, Dict[str, Dict[int, "Question"]]],
    parent_folder: Optional[str] = ".",
    save_only: Optional[List[str]] = None,
) -> None:
    """Save answers to YAML files, grouping data by publisher and journal.

    Iterates over grouped questions and creates a YAML file for each journal.

    :param grouped_questions: A nested dictionary structured as: {publisher_name:
        {journal_name: {question_number: Question}}}.
    :param parent_folder: Parent directory for saving the YAML files.
    :param save_only: Optional list of publisher names to be processed.
    """
    for publisher_name, publisher in grouped_questions.items():
        if save_only is not None and publisher_name not in save_only:
            continue

        publisher_dir = os.path.join(parent_folder, publisher_name)
        os.makedirs(publisher_dir, exist_ok=True)

        for journal_name, journal in publisher.items():
            journal_file = os.path.join(publisher_dir, f"{journal_name}.yaml")
            journal_dict = build_journal_dict(journal)
            save_yaml_file(journal_file, journal_dict)


def load_answers_from_yaml(
    parent_folder: str = ".",
) -> Dict[str, Dict[str, Dict[str, Question]]]:
    """Load answers from YAML files and reconstruct grouped questions.

    Searches for YAML files in publisher/journal directories and reconstructs
    Question objects with answers and resolution metadata.

    :param parent_folder: Directory containing publisher folders with YAML files.
    :return: Nested dict: {publisher: {journal: {question_number: Question}}}
    """
    grouped_questions: Dict[str, Dict[str, Dict[str, Question]]] = {}
    publisher_dirs = sorted(glob(f"{parent_folder}/*"))

    print(publisher_dirs)

    for publisher_dir in publisher_dirs:
        publisher_name = os.path.basename(publisher_dir)
        journal_files = glob(os.path.join(publisher_dir, "*.yaml"))

        for journal_file in journal_files:
            journal_name = os.path.splitext(os.path.basename(journal_file))[0]
            questions = _load_questions_from_file(
                journal_file, publisher_name, journal_name
            )

            if questions:
                grouped_questions.setdefault(publisher_name, {})[
                    journal_name
                ] = questions

        if not grouped_questions.get(publisher_name):
            grouped_questions.pop(publisher_name, None)

    return grouped_questions


def _load_questions_from_file(
    file_path: str, publisher: str, journal: str
) -> Dict[str, Question]:
    """Helper to load and process questions from a single YAML file."""
    questions: Dict[str, Question] = {}

    with open(file_path, "r") as file:
        yaml_data = yaml.safe_load(file)

    for q_number, q_dict in yaml_data.items():
        question = _build_question(q_number, q_dict)
        correct_answer_id = q_dict["correct_answer"]
        has_discrepancies = q_dict["has_discrepancies"]
        discrepancy_reason = q_dict.get("discrepancy_reason")

        if has_discrepancies != question.has_discrepancies():
            print(
                f"{publisher}/{journal}/{q_number} Mismatch in discrepancy "
                + f"flags: {has_discrepancies}, {question.has_discrepancies()}"
            )

        if question.has_discrepancies():
            if correct_answer_id is None:
                print(
                    f"{publisher}/{journal}/{q_number} has inconsistencies: skipped"
                )
                continue
            if discrepancy_reason is None:
                print(
                    f"Missing discrepancy_reason for {q_number} "
                    + f"in {journal}/{publisher}"
                )
                continue
            if isinstance(correct_answer_id, dict):
                correct_answer_id = correct_answer_id["text"]
            try:
                resolve_discrepancy(
                    question,
                    correct_answer=correct_answer_id,
                    discrepancy_reason=discrepancy_reason,
                )
            except ValueError:
                print(
                    f"correct_answer_id = {correct_answer_id} in {q_number} of"
                    + f" {journal}/{publisher}"
                )
                raise
        else:
            resolve_discrepancy(question)

        assert question.get_final_answer() is not None
        questions[q_number] = question

    return questions


def _build_question(question_number: str, data: dict) -> Question:
    """Helper to initialize Question object and add its answers."""
    question = Question(
        question_id=question_number,
        text=data["text"],
        is_open=False,  # TODO: false is a placeholder fix
    )

    for answer_id, answer in data.items():
        if isinstance(answer_id, int):
            question._add_answer(answer["text"], answer["explanation"])

    return question
