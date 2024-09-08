from typing import Dict, Optional
import os
import yaml
from glob import glob
import pandas as pd
from daemon_analysis_tools.data_processing import normalize_journal, normalize_publisher
from daemon_analysis_tools.data.question import Question


def load_and_process_csv(file_path: str) -> pd.DataFrame:
    data = pd.read_csv(file_path)
    try:
        data.drop(["Zeitstempel", "E-Mail-Adresse", "Punkte"], axis=1, inplace=True)
        data.drop([0, 1, 2], axis=0, inplace=True)
        print(f"Warning: E-mail addresses found in {file_path}.")
    except KeyError:
        pass
        # Already preprocessed to remove E-mail addresses

    data.rename(
        columns={
            (
                "Journal name or names, in case these replies apply "
                "to multiple journals (please separate the names by comma):"
            ): "journal"
        },
        inplace=True,
    )

    data["journal"] = data["journal"].str.split(r"\s*,\s*")
    data_duplicated = data.explode("journal").reset_index(drop=True)

    # Normalize the publisher names
    data_duplicated["Publisher Name"] = data_duplicated["Publisher Name"].apply(
        normalize_publisher
    )

    # Normalize the journal names
    # with open("../data/journal_normalizer.yaml", "r") as file:
    # normalizazion_dict = yaml.safe_load(file)
    data_duplicated["journal"] = data_duplicated["journal"].apply(normalize_journal)

    return data_duplicated


# Function to save answers to YAML files grouped by question
def save_answers_to_yaml(
    grouped_questions: Dict, parent_folder: Optional[str] = "."
) -> None:
    """
    Save answers to yaml file to facilitate discrepancy resolution.
    """

    for publisher_name, publisher in grouped_questions.items():

        publisher_dir = os.path.join(parent_folder, publisher_name)
        os.makedirs(publisher_dir, exist_ok=True)

        for journal_name, journal in publisher.items():
            journal_file = os.path.join(publisher_dir, f"{journal_name}.yaml")

            dict_to_dump = {}
            for question_number, question in journal.items():
                answers = question.answers
                if len(answers) > 1:
                    dict_to_dump[question_number] = {}
                    dict_to_dump[question_number]["text"] = question.text
                    dict_to_dump[question_number][
                        "has_discrepancies"
                    ] = question.has_discrepancies()
                    for respondent_number, answer in enumerate(answers):
                        dict_to_dump[question_number][respondent_number] = {
                            "text": answer.text,
                            "explanation": answer.explanation,
                        }
                    # Add empty line to fill with the correct answer
                    dict_to_dump[question_number]["correct_answer"] = None

            try:
                with open(journal_file, "x") as file:
                    yaml.dump(dict_to_dump, file, sort_keys=False)
            except FileExistsError:
                print(
                    (
                        f"{publisher_name}/{journal_name}.yaml already exists. "
                        "No data was written to prevent overwriting files modified "
                        "by users. Manually delete these files if necessary."
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

                    if has_discrepancies:
                        if correct_answer_id is None:
                            print(
                                (
                                    f"{publisher_name}/{journal_name}/{question_number}"
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
                            grouped_questions[publisher_name][journal_name][
                                question_number
                            ] = question
                    else:
                        answer = question_dict[0]
                        question.add_answer(answer["text"], answer["explanation"])
                        grouped_questions[publisher_name][journal_name][
                            question_number
                        ] = question

            if len(grouped_questions[publisher_name][journal_name]) == 0:
                del grouped_questions[publisher_name][journal_name]

        if len(grouped_questions[publisher_name]) == 0:
            del grouped_questions[publisher_name]

    return grouped_questions
