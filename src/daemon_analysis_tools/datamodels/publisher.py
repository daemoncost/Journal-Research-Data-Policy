from typing import Dict, List

import pandas as pd

from daemon_analysis_tools.datamodels.journal import Journal


class Publisher:
    """A class representing a publisher with associated journals."""

    def __init__(self, name: str) -> None:
        """
        Initialize a Publisher instance.

        :param name: The name of the publisher.
        """
        self.name: str = name
        self.journals: Dict[str, Journal] = {}

    def __repr__(self) -> str:
        """
        Return the string representation of the Publisher instance.

        :return: A string representation of the Publisher.
        """
        return f"Publisher(name={self.name}, num_journals={len(self.journals)})"

    @classmethod
    def from_questions(
        cls, publisher_name: str, journals_data: Dict[str, Dict[str, Any]]
    ) -> "Publisher":
        """
        Create a Publisher instance from a dictionary of questions grouped by journal.

        :param publisher_name: The name of the publisher.
        :param journals_data: A dictionary mapping each journal name to a dictionary of
            questions. Each key in the nested dictionary represents a question text and
            its value is an object with a ``get_final_answer()`` method.
        :return: A Publisher instance with its associated journals populated.
        """
        publisher = cls(publisher_name)

        for journal_name, questions in journals_data.items():
            # Create a dictionary with final answers by resolving questions.
            final_data: Dict[str, str] = {}
            for question_text, question in questions.items():
                answer = question.get_final_answer()
                if answer:
                    # Only the text is passed to Journal.
                    final_data[question_text] = answer.text
                else:
                    final_data[question_text] = "Unknown"

            # Instantiate the Journal using the final answers
            publisher.add_journal(journal_name, pd.Series(final_data))

        return publisher

    def add_journal(
        self, journal_name: str, journal_data: Union[pd.Series, Dict[str, Any]]
    ) -> None:
        """
        Add a journal to the publisher.

        :param journal_name: The name of the journal.
        :param journal_data: A pandas Series or dictionary containing the data for the
            journal.
        """
        if journal_name not in self.journals:
            self.journals[journal_name] = Journal(journal_name, journal_data)

    def get_journal(self, journal_name: str) -> Union[Journal, None]:
        """
        Retrieve a journal instance by its name.

        :param journal_name: The name of the journal.
        :return: An instance of the Journal class if found, otherwise None.
        """
        return self.journals.get(journal_name)

    def list_journals(self) -> List[str]:
        """
        List all journal names associated with this publisher.

        :return: A list of journal names.
        """
        return list(self.journals.keys())
