import argparse
import re
import shutil
from pathlib import Path

import pandas as pd

# Regular expression pattern for detecting emails
EMAIL_PATTERN = re.compile(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}")


def create_backup(file_path: Path) -> Path:
    """
    Creates a backup of the specified file.

    Args:
        file_path (Path): The path to the file to back up.

    Returns:
        Path: The path to the backup file.

    Raises:
        FileExistsError: If the backup file already exists.
    """
    backup_path = file_path.with_suffix(file_path.suffix + ".bu")

    if backup_path.exists():
        raise FileExistsError(f"Backup file already exists: {backup_path}")

    shutil.copyfile(file_path, backup_path)
    print(f"Backup created: {backup_path}")
    return backup_path


def remove_emails_from_file(file_path: Path) -> None:
    """
    Removes emails from a CSV file and saves the result if any emails are found.

    Args:
        file_path (Path): The path to the CSV file.
    """
    try:
        df = pd.read_csv(file_path)
    except Exception as e:
        print(f"Error reading file {file_path}: {e}")
        return

    # Check if any emails are present in the file
    emails_detected = False
    for column in df.select_dtypes(include=["object"]).columns:
        if df[column].str.contains(EMAIL_PATTERN, na=False).any():
            emails_detected = True
            df[column] = df[column].replace(EMAIL_PATTERN, "", regex=True)

    if not emails_detected:
        print(f"No emails detected in file {file_path}. Skipping.")
        return

    create_backup(file_path)  # Create a backup before modifying the file

    try:
        df.to_csv(file_path, index=False)
        print(f"Emails removed from file {file_path}")
    except Exception as e:
        print(f"Error saving file {file_path}: {e}")


def remove_emails_from_directory(directory: Path) -> None:
    """
    Removes emails from all CSV files in a directory, skipping backup files.

    Args:
        directory (Path): The path to the directory containing CSV files.
    """
    if not directory.is_dir():
        print(f"The specified directory does not exist: {directory}")
        return

    for file_path in directory.glob("*.csv"):
        # Skip backup files
        if file_path.suffix == ".bu":
            continue

        remove_emails_from_file(file_path)


def parse_arguments() -> argparse.Namespace:
    """
    Parses command-line arguments.

    Returns:
        argparse.Namespace: The parsed arguments.
    """
    parser = argparse.ArgumentParser(
        description="Remove emails from a file or directory."
    )
    parser.add_argument("-f", "--file", type=Path, help="Path to the CSV file")
    parser.add_argument(
        "-d",
        "--directory",
        type=Path,
        help="Path to the directory containing CSV files",
    )
    return parser.parse_args()


def main() -> None:
    """
    Main function to execute the email removal process based on command-line arguments.
    """
    args = parse_arguments()

    if args.file:
        try:
            remove_emails_from_file(args.file)
        except FileExistsError as e:
            print(e)
    elif args.directory:
        remove_emails_from_directory(args.directory)
    else:
        print("Please specify either a file with -f or a directory with -d")


if __name__ == "__main__":
    main()
