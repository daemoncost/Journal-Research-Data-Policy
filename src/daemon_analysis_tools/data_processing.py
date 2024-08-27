import pandas as pd


def load_and_process_data(file_path):
    data = pd.read_csv(file_path)
    try:
        data.drop(["Zeitstempel", "E-Mail-Adresse", "Punkte"], axis=1, inplace=True)
        data.drop([0, 1, 2], axis=0, inplace=True)
        print(f'Warning: E-mail addresses found in {file_path}.')
    except KeyError:
        pass
        # Already preprocessed to remove E-mail addresses

    keys = data.keys()
    keys = [
        key
        for key in keys
        if "Please add the text from the RDP that supports your answer below:" in key
    ]
    data.drop(keys, axis=1, inplace=True)

    data.rename(
        columns={
            "Journal name or names, in case these replies apply to multiple journals (please separate the names by comma):": "journal"
        },
        inplace=True,
    )

    data["journal"] = data["journal"].str.split("\s*,\s*")
    data_duplicated = data.explode("journal").reset_index(drop=True)

    # Normalize the publisher names
    data_duplicated["Publisher Name"] = data_duplicated["Publisher Name"].apply(
        normalize_publisher
    )

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
        "wiley": "Wiley",
    }
    name = name.strip().lower()
    return normalization_dict.get(name, name)
