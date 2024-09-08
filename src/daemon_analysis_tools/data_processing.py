import re
import pandas as pd
from daemon_analysis_tools.data.question import Question


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


def clean_question_text(question_text):
    return question_text.strip()


# Normalize text
def normalize_text(text):
    replacements = {"not available": "na", "no text": "na", "n/a": "na", "na": "na"}
    if isinstance(text, str):
        text = text.strip().lower()
        return replacements.get(text, text)
    return text


# Normalize series
def normalize_series(series):
    return series.apply(normalize_text)


# Normalize publisher names
def normalize_publisher(name):
    normalization_dict = {
        "acs": "ACS",
        "aip publishing": "AIP",
        "aip": "AIP",
        "american chemical society (acs)": "ACS",
        "aps": "APS",
        "american physical society (aps)": "APS",
        "bentham science publishers": "Bentham Science",
        "bentham science": "Bentham Science",
        "edp sciences": "EDP Sciences",
        "elsevier": "Elsevier",
        "keai      *no clear link to elsevier policies": "Elsevier",
        "frontiers": "Frontiers",
        "ieee": "IEEE",
        "iop": "IOP",
        "iop publishing": "IOP",
        "iucr": "IUCr",
        "mdpi": "MDPI",
        "mdpi all mdpi have the same instructions for authors": "MDPI",
        "mdpi all mdpi have the same  instructions for authors": "MDPI",
        "optica publishing group": "Optica",
        "optica": "Optica",
        "pleiades publishing": "Pleiades Publishing",
        "rsc": "RSC",
        "royal society of chemistry": "RSC",
        "royal society of chemistry (rsc)": "RSC",
        "springer nature": "Springer Nature",
        "taylor & francis": "Taylor & Francis",
        "taylor and francis": "Taylor & Francis",
        "wiley": "Wiley",
    }
    name = name.strip().lower()
    return normalization_dict.get(name, name)


# Normalize journal names
def normalize_journal(name):
    name = clean_journal_name(name)
    normalization_dict = {
        (
            "accounts_of_materials_research_-_acc_mater_res"
        ): "accounts_of_materials_research",
        (
            "acs_applied_materials_and_interfaces_-_" "acs_appl_mater_interfaces"
        ): "applied_materials_and_interfaces",
        (
            "environmental_science_and_technology_-_environ_sci_technol"
        ): "environmental_science_and_technology",
        (
            "the_journal_of_physical_chemistry_c_-_j_phys_chem_c"
        ): "the_journal_of_physical_chemistry_c",
        (
            "https//publishingaiporg/resources/researchers/"
            "open-science/research-data-policy/"
        ): None,
        "dalton-transactions": "dalton_transactions",
        "nanoscale-advances": "nanoscale_advances",
        "nature_eniergy": "nature_energy",
        "chemistry_-_a_european_journal": "chemistry_a_european_journal",
        "ce/paper": "ce-papers",
        "ce/papers": "ce-papers",
    }
    return normalization_dict.get(name, name)


# Function to clean journal names for file naming
def clean_journal_name(journal_name):
    # journal_name = journal_name.split("-")[0]
    journal_name = journal_name.strip()
    journal_name = re.sub(r"\n", "", journal_name)
    journal_name = journal_name.replace("&", "and")
    journal_name = re.sub(r"[.?:]", "", journal_name)
    journal_name = journal_name.replace(" ", "_")
    journal_name = journal_name.lower()
    return journal_name


def group_questions_by_journal(data):
    grouped_data = data.groupby(["Publisher Name", "journal"])
    grouped_questions = {}

    for (publisher_name, journal_name), group in grouped_data:
        if publisher_name not in grouped_questions:
            grouped_questions[publisher_name] = {}

        if journal_name not in grouped_questions[publisher_name]:
            grouped_questions[publisher_name][journal_name] = {}

        for i, column in enumerate(data.columns):
            if column.split(".")[
                0
            ].isdigit():  # Check if the column label starts with an integer
                q_num = int(column.split(".")[0])

                # Check for the presence of an explanation column
                next_column = data.columns[i + 1] if i + 1 < len(data.columns) else None
                explanation_col = None
                if (
                    next_column
                    and (
                        "Please add the text from the RDP "
                        "that supports your answer below:"
                    )
                    in next_column
                ):
                    explanation_col = next_column

                if q_num not in grouped_questions[publisher_name][journal_name]:
                    grouped_questions[publisher_name][journal_name][q_num] = Question(
                        column
                    )

                for idx, answer in enumerate(group[column]):
                    explanation = (
                        group[explanation_col].iloc[idx]
                        if explanation_col in group.columns
                        else ""
                    )
                    grouped_questions[publisher_name][journal_name][q_num].add_answer(
                        answer, explanation
                    )

    return grouped_questions
