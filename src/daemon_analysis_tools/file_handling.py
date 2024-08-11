import os
import yaml
import re

# Function to clean journal names for file naming
def clean_journal_name(journal_name):
    journal_name = journal_name.replace("&", "and")
    journal_name = re.sub(r'[.?]', '', journal_name)
    journal_name = journal_name.replace(" ", "_")
    journal_name = journal_name.lower()
    return journal_name

# Function to normalize publisher names
def normalize_publisher(name):
    normalization_dict = {
        "acs": "ACS",
        "acs ": "ACS",
        "aip publishing": "AIP",
        "american chemical society (acs)": "ACS",
        "american physical society (aps)": "APS",
        "bentham science publishers": "Bentham Science",
        "edp sciences": "EDP Sciences",
        "elsevier": "Elsevier",
        "frontiers": "Frontiers",
        "ieee": "IEEE",
        "iop": "IOP",
        "iop publishing": "IOP",
        "iucr": "IUCr",
        "mdpi": "MDPI",
        "mdpi all mdpi have the same instructions for authors": "MDPI",
        "mdpi all mdpi have the same  instructions for authors": "MDPI",
        "optica publishing group": "Optica",
        "royal society of chemistry": "RSC",
        "royal society of chemistry (rsc)": "RSC",
        "springer nature": "Springer Nature",
        "taylor & francis": "Taylor & Francis",
        "taylor and francis": "Taylor & Francis",
        "wiley": "Wiley"
    }
    name = name.strip().lower()
    return normalization_dict.get(name, name)

# Function to save answers to YAML files grouped by question
def save_answers_to_yaml(grouped_data, question_num_to_text, parent_folder='.'):
    for (publisher, journal), group in grouped_data.groupby(['Publisher Name', 'journal']):
        publisher_dir = os.path.join(parent_folder, publisher)
        os.makedirs(publisher_dir, exist_ok=True)
        
        journal_file_name = clean_journal_name(journal)
        
        journal_data = {}
        for question_num, question_text in question_num_to_text.items():
            question_text_clean = question_text.strip()
            answers = {}
            for idx, row in group.iterrows():
                respondent_id = f'Respondent {idx + 1}'
                answers[respondent_id] = row[question_text]
            journal_data[question_text_clean] = answers
        
        journal_file = os.path.join(publisher_dir, f'{journal_file_name}.yaml')

        try:
            with open(journal_file, 'w') as file:
                yaml.dump(journal_data, file, sort_keys=False)
        except Exception as e:
            print(f'Exception: {e} for journal {journal}')

