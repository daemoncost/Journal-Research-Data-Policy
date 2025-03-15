import os
import tempfile
import unittest

import pandas as pd

# Import the functions to be tested.
from daemon_analysis_tools.io.csv_handler import (
    _load_csv,
    _normalize_columns,
    _remove_sensitive_columns,
    _remove_unnamed_columns,
    _rename_columns,
    _split_and_expand_journal_names,
    load_and_process_csv,
)


class TestCSVProcessing(unittest.TestCase):
    def setUp(self):
        # Create dummy CSV content with required columns.
        self.csv_content = (
            "Zeitstempel,E-Mail-Adresse,Punkte,"
            '"Journal name or names, in case these replies apply to '
            'multiple journals (please separate the names by comma):",'
            "Publisher Name,OtherColumn\n"
            '2023-01-01,,10,"Journal A, Journal B",Pub A,Value1\n'
            '2023-01-01,,10,"Journal A, Journal B",Pub A,Value2\n'
            '2023-01-01,,10,"Journal A, Journal B",Pub A,Value3\n'
            '2023-01-02,,15,"Journal C",Pub B,Value4\n'
            '2023-01-02,,15,"Journal C",Pub B,Value5\n'
            '2023-01-02,,15,"Journal C",Pub B,Value6\n'
        )
        # Create a temporary directory and file to hold the CSV.
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_file_path = os.path.join(self.temp_dir.name, "test.csv")
        with open(self.temp_file_path, "w") as f:
            f.write(self.csv_content)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_load_csv(self):
        df = _load_csv(self.temp_file_path)
        self.assertIsInstance(df, pd.DataFrame)
        # Our dummy CSV has 6 rows.
        self.assertEqual(df.shape[0], 6)

    def test_remove_sensitive_columns(self):
        df = _load_csv(self.temp_file_path)
        df = _remove_sensitive_columns(df)
        # The columns "Zeitstempel", "E-Mail-Adresse", "Punkte" should be removed.
        self.assertNotIn("Zeitstempel", df.columns)
        self.assertNotIn("E-Mail-Adresse", df.columns)
        self.assertNotIn("Punkte", df.columns)
        # The first three rows should have been dropped.
        self.assertEqual(df.shape[0], 3)

    def test_rename_columns(self):
        df = _load_csv(self.temp_file_path)
        df = _rename_columns(df)
        # The original long column name should now be renamed to "journal".
        self.assertIn("journal", df.columns)

    def test_split_and_expand_journal_names(self):
        df = _load_csv(self.temp_file_path)
        df = _rename_columns(df)
        df = _split_and_expand_journal_names(df)
        # First three rows have "Journal A, Journal B" → 3 rows become 6.
        # Next three rows have "Journal C" → remain 3 rows.
        # Total expected rows = 9.
        self.assertEqual(df.shape[0], 9)
        # All values in "journal" should be strings.
        self.assertTrue(all(df["journal"].apply(lambda x: isinstance(x, str))))

    def test_normalize_columns(self):
        from daemon_analysis_tools.processing import normalizer as norm_mod

        original_normalize_journal = norm_mod._normalize_journal
        original_normalize_publisher = norm_mod._normalize_publisher

        try:

            def dummy_normalize_journal(x):
                return x.lower()

            def dummy_normalize_publisher(x):
                return x.lower()

            norm_mod._normalize_journal = dummy_normalize_journal
            norm_mod._normalize_publisher = dummy_normalize_publisher

            df = _load_csv(self.temp_file_path)
            df = _rename_columns(df)
            df = _normalize_columns(df)
            # Check that the 'journal' column values are in lower-case.
            self.assertTrue(all(df["journal"].apply(lambda x: x == x.lower())))
            # Check that if "Publisher Name" is present, it is also normalized.
            if "Publisher Name" in df.columns:
                self.assertTrue(
                    all(df["Publisher Name"].apply(lambda x: x == x.lower()))
                )
        finally:
            norm_mod._normalize_journal = original_normalize_journal
            norm_mod._normalize_publisher = original_normalize_publisher

    def test_remove_unnamed_columns(self):
        # Create a simple DataFrame with an unnamed column.
        data = {"Unnamed: 0": [1, 2, 3], "A": [4, 5, 6]}
        df = pd.DataFrame(data)
        df_clean = _remove_unnamed_columns(df)
        self.assertNotIn("Unnamed: 0", df_clean.columns)
        self.assertIn("A", df_clean.columns)

    def test_load_and_process_csv_end_to_end(self):
        # End-to-end test: load and process the CSV file.
        df = load_and_process_csv(self.temp_file_path)
        # Check that sensitive columns have been removed.
        self.assertNotIn("Zeitstempel", df.columns)
        self.assertNotIn("E-Mail-Adresse", df.columns)
        self.assertNotIn("Punkte", df.columns)
        # Check that the long journal column has been renamed.
        self.assertIn("journal", df.columns)
        # Ensure that the 'journal' column contains strings.
        self.assertTrue(df["journal"].dtype == object)
        # Ensure that no automatically generated unnamed columns remain.
        self.assertFalse(any(df.columns.str.contains("^Unnamed:")))


if __name__ == "__main__":
    unittest.main()
