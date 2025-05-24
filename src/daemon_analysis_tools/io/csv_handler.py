from pathlib import Path
from typing import Dict, Optional

import pandas as pd

from daemon_analysis_tools.datamodels.question import Question
from daemon_analysis_tools.io.utilities import (
    _create_table_from_grouped_questions,
    _merge_answers_metadata,
    _merge_single_layer,
    _read_double_layer_metadata,
    _read_single_layer_metadata,
)
from daemon_analysis_tools.processing.normalizer import (
    _normalize_journal,
    _normalize_publisher,
)


def _load_csv(path: Path | str) -> pd.DataFrame:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"[error] File not found: {path}")

    df = pd.read_csv(path)
    print(f"[info] CSV loaded ← {path}")
    return df


def _remove_sensitive_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Remove sensitive columns from the DataFrame.

    This function checks whether all e-mail addresses in the "E-Mail-Adresse" column are
    NaN. If any e-mail addresses are found, a warning is printed. It then drops the
    columns "Zeitstempel", "E-Mail-Adresse", and "Punkte", and removes the first three
    rows.

    :param data: The DataFrame from which sensitive columns should be removed.
    :type data: pd.DataFrame
    :return: The DataFrame with sensitive columns removed.
    :rtype: pd.DataFrame
    """
    try:
        emails_are_nan = data["E-Mail-Adresse"].isna().all()
        if not emails_are_nan:
            print("Warning: E-mail addresses found.")
        data.drop(["Zeitstempel", "E-Mail-Adresse", "Punkte"], axis=1, inplace=True)
        data.drop([0, 1, 2], axis=0, inplace=True)
    except KeyError:
        # The DataFrame has already been preprocessed to remove e-mail addresses.
        pass
    return data


def _rename_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Rename specific columns in the DataFrame for consistency.

    :param data: The DataFrame with original column names.
    :type data: pd.DataFrame
    :return: A DataFrame with renamed columns.
    :rtype: pd.DataFrame
    """
    rename_mapping = {
        (
            "Journal name or names, in case these replies apply to multiple journals "
            "(please separate the names by comma):"
        ): "journal"
    }
    return data.rename(columns=rename_mapping)


def _split_and_expand_journal_names(data: pd.DataFrame) -> pd.DataFrame:
    """Split journal names by commas and expand them into multiple rows.

    The 'journal' column is expected to contain comma-separated values. This function
    splits these values into lists and then expands the lists into separate rows.

    :param data: The DataFrame containing the 'journal' column.
    :type data: pd.DataFrame
    :return: A DataFrame with expanded journal names.
    :rtype: pd.DataFrame
    """
    data["journal"] = data["journal"].str.split(r"\s*,\s*")
    return data.explode("journal").reset_index(drop=True)


def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Normalize journal and publisher names in the DataFrame.

    If the 'Publisher Name' column is present, its values are normalized using the
    _normalize_publisher function. Likewise, the 'journal' column values are normalized
    using the _normalize_journal function.

    :param data: The DataFrame with columns to be normalized.
    :type data: pd.DataFrame
    :return: A DataFrame with normalized journal and publisher names.
    :rtype: pd.DataFrame
    """
    if "Publisher Name" in data.columns:
        data["Publisher Name"] = data["Publisher Name"].apply(_normalize_publisher)
    if "journal" in data.columns:
        data["journal"] = data["journal"].apply(_normalize_journal)
    return data


def _remove_unnamed_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Remove automatically generated unnamed columns from the DataFrame.

    :param data: The DataFrame from which to remove unnamed columns.
    :type data: pd.DataFrame
    :return: A DataFrame with unnamed columns removed.
    :rtype: pd.DataFrame
    """
    return data.loc[:, ~data.columns.str.contains("^Unnamed:")]


def load_and_process_csv(file_path: str) -> pd.DataFrame:
    """Load and process a CSV file step by step.

    This function executes several data processing steps:
      1. Load the CSV into a DataFrame.
      2. Remove sensitive columns.
      3. Rename specific columns.
      4. Split and expand journal names.
      5. Normalize journal and publisher names.
      6. Remove automatically generated unnamed columns.

    :param file_path: Path to the CSV file.
    :type file_path: str
    :return: A processed DataFrame.
    :rtype: pd.DataFrame
    """
    data = _load_csv(file_path)
    data = _remove_sensitive_columns(data)
    data = _rename_columns(data)
    data = _split_and_expand_journal_names(data)
    data = _normalize_columns(data)
    data = _remove_unnamed_columns(data)
    return data


def save_summary_table_to_csv(df: pd.DataFrame, path: Path | str) -> None:
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)

    if path.exists():
        response = (
            input(f"[warning] File '{path}' already exists. Overwrite? [y/N]: ")
            .strip()
            .lower()
        )
        if response not in {"y", "yes"}:
            print("[info] Aborted saving.")
            return

    df.to_csv(path, index=False)
    print(f"[info] CSV written → {path}")


def load_summary_table_from_csv(path: Path | str) -> pd.DataFrame:
    return _load_csv(path)
