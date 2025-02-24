import pandas as pd

from daemon_analysis_tools.processing.normalizer import (
    _normalize_journal,
    _normalize_publisher,
)


def _load_csv(file_path: str) -> pd.DataFrame:
    """Loads a CSV file into a Pandas DataFrame."""
    return pd.read_csv(file_path)


def _remove_sensitive_columns(data: pd.DataFrame) -> pd.DataFrame:
    try:
        emails_are_nan = data["E-Mail-Adresse"].isna().all()
        if not emails_are_nan:
            print("Warning: E-mail addresses found.")
        data.drop(["Zeitstempel", "E-Mail-Adresse", "Punkte"], axis=1, inplace=True)
        data.drop([0, 1, 2], axis=0, inplace=True)
    except KeyError:
        pass
        # Already preprocessed to remove E-mail addresses
    return data


def _rename_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Renames specific columns for consistency."""
    rename_mapping = {
        "Journal name or names, in case these replies apply "
        "to multiple journals (please separate the names by comma):": "journal"
    }
    return data.rename(columns=rename_mapping)


def _split_and_expand_journal_names(data: pd.DataFrame) -> pd.DataFrame:
    """Splits journal names by commas and expands them into multiple rows."""
    data["journal"] = data["journal"].str.split(r"\s*,\s*")
    return data.explode("journal").reset_index(drop=True)


def _normalize_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Normalizes journal and publisher names."""
    if "Publisher Name" in data.columns:
        data["Publisher Name"] = data["Publisher Name"].apply(_normalize_publisher)

    if "journal" in data.columns:
        data["journal"] = data["journal"].apply(_normalize_journal)

    return data


def _remove_unnamed_columns(data: pd.DataFrame) -> pd.DataFrame:
    """Removes automatically generated unnamed columns."""
    return data.loc[:, ~data.columns.str.contains("^Unnamed:")]


def load_and_process_csv(file_path: str) -> pd.DataFrame:
    """Loads and processes a CSV file step by step."""
    data = _load_csv(file_path)
    data = _remove_sensitive_columns(data)
    data = _rename_columns(data)
    data = _split_and_expand_journal_names(data)
    data = _normalize_columns(data)
    data = _remove_unnamed_columns(data)
    return data
