import yaml
from typing import Dict


def load_yaml(filepath: str):
    """
    Load a YAML file and return its contents as a dictionary.

    Parameters:
    - filepath (str): Path to the YAML file.

    Returns:
    - dict: Parsed YAML content.
    """
    with open(filepath, "r") as file:
        data = yaml.safe_load(file)
    return data


def save_yaml_file(file_path: str, data: Dict) -> None:
    """Save a dictionary to a YAML file.

    :param file_path: The file path where the YAML file will be saved.
    :param data: The dictionary to dump into the YAML file.
    """
    try:
        with open(file_path, "x") as file:
            yaml.dump(data, file, sort_keys=False)
    except FileExistsError:
        print(
            f"{file_path} already exists. No data was written to prevent overwriting "
            "files modified by users. "
            "Manually delete this file if necessary."
        )

    except Exception as e:
        print(f"Exception: {e} for file {file_path}")
