import os
import yaml
import pandas as pd
from daemon_analysis_tools.data_processing import normalize_journal, normalize_publisher


def load_and_process_csv(file_path):
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
def save_answers_to_yaml(grouped_data, question_num_to_text, parent_folder="."):
    for (publisher, journal), group in grouped_data.groupby(
        ["Publisher Name", "journal"]
    ):
        publisher_dir = os.path.join(parent_folder, publisher)
        os.makedirs(publisher_dir, exist_ok=True)

        journal_file_name = normalize_journal(journal)

        journal_data = {}
        for question_num, question_text in question_num_to_text.items():
            question_text_clean = question_text.strip()
            answers = {}
            for idx, row in group.iterrows():
                respondent_id = f"Respondent {idx + 1}"
                answers[respondent_id] = row[question_text]
            journal_data[question_text_clean] = answers

        journal_file = os.path.join(publisher_dir, f"{journal_file_name}.yaml")

        try:
            with open(journal_file, "w") as file:
                yaml.dump(journal_data, file, sort_keys=False)
        except Exception as e:
            print(f"Exception: {e} for journal {journal}")
