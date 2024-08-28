import unittest

from daemon_analysis_tools.file_handling import clean_journal_name


class TestFileHandling(unittest.TestCase):
    def test_clean_journal_name(self):
        self.assertEqual(clean_journal_name("Journal & Title."), "journal_and_title")
        self.assertEqual(
            clean_journal_name("Journal of Science"), "journal_of_science"
        )

    # Add more tests for save_answers_to_yaml


if __name__ == "__main__":
    unittest.main()
