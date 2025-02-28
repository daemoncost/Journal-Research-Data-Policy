import unittest

from daemon_analysis_tools.data_processing import normalize_journal


class TestDataProcessing(unittest.TestCase):
    def test_normalize_journal_known(self):
        # Define a list of test cases as (input, expected_output) tuples.
        test_cases = [
            (
                "accounts_of_materials_research_-_acc_mater_res",
                "accounts_of_materials_research",
            ),
            (
                "acs_applied_materials_and_interfaces_-_acs_appl_mater_interfaces",
                "applied_materials_and_interfaces",
            ),
            (
                "environmental_science_and_technology_-_environ_sci_technol",
                "environmental_science_and_technology",
            ),
            (
                "the_journal_of_physical_chemistry_c_-_j_phys_chem_c",
                "the_journal_of_physical_chemistry_c",
            ),
            (
                "https//publishingaiporg/resources/researchers/"
                "open-science/research-data-policy/",
                None,
            ),
            ("dalton-transactions", "dalton_transactions"),
            ("nanoscale-advances", "nanoscale_advances"),
            ("nature_eniergy", "nature_energy"),
            ("chemistry_-_a_european_journal", "chemistry_a_european_journal"),
            ("ce/paper", "ce-papers"),
            ("ce/papers", "ce-papers"),
            ("journal_of_the_american_chemical_society_-_jacs", "jacs"),
            ("journal_of_chemical_physics_c", "the_journal_of_physical_chemistry_c"),
            (
                "journal_of_the_american_society_for_mass_spectroscopy",
                "journal_of_the_american_society_for_mass_spectrometry",
            ),
            ("acs_esandt_engineering", "acs_es_and_t_engineering"),
            (
                "applied_materials_and_interfaces",
                "acs_applied_materials_and_interfaces",
            ),
            (
                "applied_catalysis_b_environmental",
                "applied_catalysis_b_environment_and_energy",
            ),
            (
                "acs_applied_materials_and_interfaces",
                "applied_materials_and_interfaces",
            ),
        ]
        for input_val, expected in test_cases:
            with self.subTest(journal=input_val):
                self.assertEqual(normalize_journal(input_val), expected)

    def test_normalize_journal_default(self):
        # Test that a journal name not in the normalization_dict is returned as is.
        self.assertEqual(normalize_journal("unknown_journal"), "unknown_journal")

    def test_load_and_process_data(self):
        # Add test cases to check if the data is loaded and processed correctly
        pass


if __name__ == "__main__":
    unittest.main()
