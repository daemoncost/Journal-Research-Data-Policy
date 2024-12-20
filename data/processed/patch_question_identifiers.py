import shutil
from glob import glob

import yaml

question_number_to_question_id = {
    1: "rdp_exist",
    3: "data_sharing",
    4: "data_fair",
    2: "data_availability",
    5: "data_citability",
    7: "data_timing",
    8: "data_sharing_method",
    9: "data_licenses",
    10: "data_referee",
    11: "data_recommended",
    12: "data_required",
    13: "code_required",
    14: "code_reproducibility",
    15: "code_versioning",
    16: "code_quality",
    17: "code_autotest",
    18: "code_docs",
    19: "code_linting",
    20: "code_development",
}

all_pubs = glob("./all_answers/*")
for pub in all_pubs:
    all_journals = glob(pub + "/*.yaml")
    for j in all_journals:
        # create a backup copy of the original file
        j_backup = j + "_backup"
        shutil.copy(j, j_backup)
        y = yaml.safe_load(open(j))
        new_y = {question_number_to_question_id[i]: values for i, values in y.items()}
        with open(j, "w") as f:
            yaml.dump(new_y, f, sort_keys=False)
