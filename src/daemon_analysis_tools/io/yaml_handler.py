<<<<<<< HEAD
import os
from glob import glob
from typing import Dict, List, Optional

import yaml

from daemon_analysis_tools.datamodels.question import Question


def save_answers_to_yaml(
    grouped_questions: Dict[str, Dict[str, Dict[str, Question]]],
    parent_folder: Optional[str] = ".",
    save_only: Optional[List[str]] = None,
) -> None:
    """
    Save answers to YAML files, grouping data by publisher and journal.

    This function iterates over the provided grouped questions and creates a YAML
    file for each journal. The YAML file contains question details including text,
    the number of respondents, answer texts with explanations, discrepancy flags,
    and the resolved correct answer (if available).

    :param grouped_questions: A nested dictionary structured as:
        {publisher_name: {journal_name: {question_number: Question}}}.
    :param parent_folder: The parent directory where YAML files will be saved.
        Defaults to the current directory.
    :param save_only: An optional list of publisher names to be processed.
        If provided, only publishers whose names are in this list will be saved.
    :raises Exception: Propagates exceptions encountered during file writing,
        except for FileExistsError which is handled gracefully.
    """
    for publisher_name, publisher in grouped_questions.items():
        if save_only is not None and publisher_name not in save_only:
            continue

        publisher_dir = os.path.join(parent_folder, publisher_name)
        os.makedirs(publisher_dir, exist_ok=True)

        for journal_name, journal in publisher.items():
            journal_file = os.path.join(publisher_dir, f"{journal_name}.yaml")
            dict_to_dump: Dict = {}

            for question_number, question in journal.items():
                answers = question.answers
                dict_to_dump[question_number] = {
                    "text": question.text,
                    "N. encoders": len(answers),
                    "has_discrepancies": question.has_discrepancies(),
                }
                for respondent_number, answer in enumerate(answers):
                    dict_to_dump[question_number][respondent_number] = {
                        "text": answer.text,
                        "explanation": answer.explanation,
                    }
                if question.correct_answer is None:
                    dict_to_dump[question_number]["correct_answer"] = None
                else:
                    dict_to_dump[question_number]["correct_answer"] = {
                        "text": question.correct_answer.text,
                        "explanation": question.correct_answer.explanation,
                    }
                dict_to_dump[question_number][
                    "discrepancy_reason"
                ] = question.discrepancy_reason

            try:
                with open(journal_file, "x") as file:
                    yaml.dump(dict_to_dump, file, sort_keys=False)
            except FileExistsError:
                print(
                    (
                        f"{publisher_name}/{journal_name}.yaml already exists. "
                        "No data was written to prevent overwriting files modified by "
                        "users. Manually delete these files if necessary."
                    )
                )
            except Exception as e:
                print(f"Exception: {e} for journal {journal_name}")


def load_answers_from_yaml(
    parent_folder: str = ".",
) -> Dict[str, Dict[str, Dict[str, Question]]]:
    """
    Load answers from YAML files and reconstruct grouped questions.

    The function searches for publisher directories under the provided parent folder,
    loads each YAML file corresponding to a journal, and reconstructs the Question
    objects with their associated answers and discrepancy resolutions.

    :param parent_folder: The directory containing publisher folders with YAML files.
                          Defaults to the current directory.
    :return: A nested dictionary structured as:
             {publisher_name: {journal_name: {question_number: Question}}}.
    """
    grouped_questions: Dict[str, Dict[str, Dict[str, Question]]] = {}

    publisher_dirs: List[str] = sorted(glob(f"{parent_folder}/*"))
    for publisher_dir in publisher_dirs:
        publisher_name = publisher_dir.split("/")[-1]
        grouped_questions[publisher_name] = {}
        journal_files: List[str] = glob(f"{parent_folder}/{publisher_name}/*.yaml")

        for journal_file in journal_files:
            journal_name = os.path.splitext(os.path.basename(journal_file))[0]
            grouped_questions[publisher_name][journal_name] = {}

            with open(journal_file, "r") as file:
                yaml_data = yaml.safe_load(file)
                for question_number, question_dict in yaml_data.items():
                    # Initialize the question for reconstruction.
                    question = Question(text=question_dict["text"])
                    correct_answer_id = question_dict["correct_answer"]
                    has_discrepancies = question_dict["has_discrepancies"]
                    discrepancy_reason = question_dict.get("discrepancy_reason", None)

                    if has_discrepancies:
                        if correct_answer_id is None:
                            print(
                                (
                                    f"{publisher_name}/{journal_name}/{question_number}"
                                    " has inconsistencies: skipped"
                                )
                            )
                            # Skip the question if discrepancy resolution info is
                            # missing.
                            continue
                        else:
                            assert isinstance(correct_answer_id, int), (
                                "`correct_answer` must be an integer "
                                "(the number of the correct respondent)"
                            )
                            answer = question_dict[correct_answer_id]
                            question.add_answer(answer["text"], answer["explanation"])
                            if discrepancy_reason is None:
                                print(
                                    (
                                        "You must provide `discrepancy_reason` to "
                                        "resolve discrepancies. "
                                        f"Question {question_number} in "
                                        f"{journal_name}/{publisher_name}"
                                    )
                                )
                                continue
                            else:
                                question.resolve_discrepancy(
                                    correct_answer=0,
                                    discrepancy_reason=discrepancy_reason,
                                )
                                assert question.get_final_answer() is not None
                                grouped_questions[publisher_name][journal_name][
                                    question_number
                                ] = question
                    else:
                        answer = question_dict[0]
                        question.add_answer(answer["text"], answer["explanation"])
                        question.resolve_discrepancy(correct_answer=0)
                        assert question.get_final_answer() is not None
                        grouped_questions[publisher_name][journal_name][
                            question_number
                        ] = question

            # Remove journal if no questions were successfully loaded.
            if not grouped_questions[publisher_name][journal_name]:
                del grouped_questions[publisher_name][journal_name]

        # Remove publisher if no journals were successfully loaded.
        if not grouped_questions[publisher_name]:
            del grouped_questions[publisher_name]

    return grouped_questions
