import os
from glob import glob
from typing import Dict, List, Optional

import yaml

from daemon_analysis_tools.datamodels.question import Question


# Function to save answers to YAML files grouped by question
def save_answers_to_yaml(
    grouped_questions: Dict,
    parent_folder: Optional[str] = ".",
    save_only: Optional[List[str]] = None,
) -> None:
    """
    Save answers to yaml file to facilitate discrepancy resolution.
    """

    for publisher_name, publisher in grouped_questions.items():
        if save_only is not None:
            if publisher_name not in save_only:
                continue

        publisher_dir = os.path.join(parent_folder, publisher_name)
        os.makedirs(publisher_dir, exist_ok=True)

        for journal_name, journal in publisher.items():
            journal_file = os.path.join(publisher_dir, f"{journal_name}.yaml")

            dict_to_dump = {}
            for question_number, question in journal.items():
                answers = question.answers
                # if len(answers) > 1:
                dict_to_dump[question_number] = {}
                dict_to_dump[question_number]["text"] = question.text
                dict_to_dump[question_number]["N. encoders"] = len(answers)
                dict_to_dump[question_number][
                    "has_discrepancies"
                ] = question.has_discrepancies()
                for respondent_number, answer in enumerate(answers):
                    dict_to_dump[question_number][respondent_number] = {
                        "text": answer.text,
                        "explanation": answer.explanation,
                    }
                # Add empty line to fill with the correct answer
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
                        f"{publisher_name}/{journal_name}.yaml already exists "
                        ". No data was written to prevent overwriting files "
                        "modified by users. Manually delete these files if "
                        "necessary."
                    )
                )
            except Exception as e:
                print(f"Exception: {e} for journal {journal_name}")


def load_answers_from_yaml(parent_folder: str = ".") -> Dict:
    grouped_questions = {}

    publisher_dirs = sorted(glob(f"{parent_folder}/*"))
    for publisher_dir in publisher_dirs:
        publisher_name = publisher_dir.split("/")[-1]

        grouped_questions[publisher_name] = {}
        journal_files = glob(f"{parent_folder}/{publisher_name}/*.yaml")

        for journal_file in journal_files:
            journal_name = journal_file.split("/")[-1].split(".")[0]
            grouped_questions[publisher_name][journal_name] = {}
            with open(journal_file, "r") as file:
                _d = yaml.safe_load(file)
                for question_number, question_dict in _d.items():
                    grouped_questions[publisher_name][journal_name][
                        question_number
                    ] = {}

                    question = Question(text=question_dict["text"])
                    correct_answer_id = question_dict["correct_answer"]
                    has_discrepancies = question_dict["has_discrepancies"]
                    discrepancy_reason = question_dict.get("discrepancy_reason", None)

                    if has_discrepancies:
                        if correct_answer_id is None:
                            print(
                                (
                                    f"{publisher_name}/{journal_name}/"
                                    f"{question_number}"
                                    " has inconsistencies: skipped"
                                )
                            )
                            del grouped_questions[publisher_name][journal_name][
                                question_number
                            ]
                        else:
                            assert isinstance(correct_answer_id, int), (
                                "`correct_answer` must be an integer "
                                "(the number of the correct respondent)"
                            )
                            answer = question_dict[correct_answer_id]

                            question.add_answer(answer["text"], answer["explanation"])
                            if discrepancy_reason is None:
                                Warning(
                                    f"You must provide `discrepancy_reason` "
                                    f"to resolve discrepancies."
                                    f"Question {question_number} in {journal_name}"
                                    f"{publisher_name}"
                                )
                                del grouped_questions[publisher_name][journal_name][
                                    question_number
                                ]
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

            if len(grouped_questions[publisher_name][journal_name]) == 0:
                del grouped_questions[publisher_name][journal_name]

        if len(grouped_questions[publisher_name]) == 0:
            del grouped_questions[publisher_name]

    return grouped_questions
