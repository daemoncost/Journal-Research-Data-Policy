import re


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
        "journal_of_the_american_chemical_society_-_jacs": "jacs",
        "journal_of_chemical_physics_c": "the_journal_of_physical_chemistry_c",
        "journal_of_the_american_society_for_mass_spectroscopy": (
            "journal_of_the_" "american_society_for_mass_spectrometry"
        ),
        "acs_esandt_engineering": "acs_es_and_t_engineering",
        "applied_materials_and_interfaces": "acs_applied_materials_and_interfaces",
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
