import re
import sys
from pathlib import Path
from typing import List

import pandas as pd

# Regular expression pattern for detecting emails
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")

# Directories to check for CSV files
DIRECTORIES = [Path("data/raw"), Path("data/processed")]


def check_for_emails_in_file(file_path: Path) -> bool:
    """
    Checks if a CSV file contains any email addresses.

    Args:
        file_path (Path): The path to the CSV file.

    Returns:
        bool: True if emails are found, False otherwise.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return False

    for column in df.select_dtypes(include=["object"]).columns:
        if df[column].str.contains(EMAIL_PATTERN, na=False).any():
            return True

    return False


def check_for_emails_in_directory(directories: List[Path]) -> bool:
    """
    Checks all CSV files in the given directories for email addresses.

    Args:
        directories (List[Path]): A list of directories to check.

    Returns:
        bool: True if emails are found, False otherwise.
    """
    files_with_emails = []
    files_without_emails = []

    for directory in directories:
        if not directory.is_dir():
            print(f"Directory does not exist: {directory}")
            continue

        for file_path in directory.glob("*.csv"):
            if check_for_emails_in_file(file_path):
                files_with_emails.append(file_path)
            else:
                files_without_emails.append(file_path)

    if files_without_emails:
        print("Files without detected emails:")
        for file_path in files_without_emails:
            print(f"  {file_path}")

    if files_with_emails:
        error_message = "Emails detected in the following files:\n" + "\n".join(
            map(str, files_with_emails)
        )
        print(error_message)
        return True  # Indicate that emails were found

    return False  # Indicate that no emails were found


def main() -> None:
    """
    Main function to execute the email detection in specified directories.
    """
    emails_found = check_for_emails_in_directory(DIRECTORIES)
    if emails_found:
        sys.exit(1)  # Exit with a non-zero status code to indicate failure


if __name__ == "__main__":
    main()
