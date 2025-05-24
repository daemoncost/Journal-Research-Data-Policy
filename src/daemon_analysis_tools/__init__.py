"""This module provides the main functions intended for public use."""

from daemon_analysis_tools.io.csv_handler import (
    load_and_process_csv,
    load_summary_table_from_csv,
    save_summary_table_to_csv,
)
from daemon_analysis_tools.io.yaml_handler import (
    load_answers_from_yaml,
    save_answers_to_yaml,
)
from daemon_analysis_tools.processing.grouper import group_questions_by_journal
from daemon_analysis_tools.processing.questions_summary import (
    create_answers_summary_with_metadata,
)
from daemon_analysis_tools.services.discrepancy_resolver import resolve_discrepancy

__all__ = [
    "load_and_process_csv",
    "group_questions_by_journal",
    "resolve_discrepancy",
    "save_answers_to_yaml",
    "load_answers_from_yaml",
    "create_answers_summary_with_metadata",
    "load_summary_table_from_csv",
    "save_summary_table_to_csv",
]
