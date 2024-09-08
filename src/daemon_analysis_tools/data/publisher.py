from typing import List, Dict
from daemon_analysis_tools.data.journal import Journal
import pandas as pd


class Publisher:
    def __init__(self, name: str) -> None:
        """
        Initialize a Publisher instance.

        :param name: The name of the publisher.
        """
        self.name = name
        self.journals = {}

    def __repr__(self):
        return (
            f"""Publisher(name={self.name}, 
          num_journals={len(self.journals)}"""
            #   journals=["""
            # + "|".join([journal for journal in self.journals])
            # + "]"
        )

    @classmethod
    def from_questions(cls, publisher_name: str, journals_data: Dict):
        """
        Class method to create a Publisher instance from dict of questions.

        :param publisher_name: The name of the publisher.
        :param journals_data: A dictionary where each journal name maps to its grouped
                              questions.
        :return: A Publisher instance with its associated journals.
        """
        publisher = cls(publisher_name)

        for journal_name, questions in journals_data.items():
            # Create a dictionary with final answers by resolving questions
            final_data = {}
            for question_text, question in questions.items():
                answer = question.get_final_answer()
                if answer:
                    final_data[question_text] = (
                        answer.text
                    )  # We are only passing the text to Journal
                    # final_data["explanation"] = answer.explanation
                else:
                    final_data[question_text] = "Unknown"

            # Instantiate the Journal using the final answers
            publisher.add_journal(journal_name, pd.Series(final_data))

        return publisher

    def add_journal(self, journal_name: str, journal_data: pd.DataFrame) -> None:
        """
        Add a journal to the publisher.

        :param journal_name: The name of the journal.
        :param journal_data: A dictionary or pandas Series containing the data
                             for the journal.
        """
        if journal_name not in self.journals:
            self.journals[journal_name] = Journal(journal_name, journal_data)

    def get_journal(self, journal_name: str) -> Journal:
        """
        Get a journal instance by name.

        :param journal_name: The name of the journal.
        :return: An instance of the Journal class.
        """
        return self.journals.get(journal_name)

    def list_journals(self) -> List:
        """
        List all journals associated with this publisher.

        :return: A list of journal names.
        """
        return list(self.journals.keys())
