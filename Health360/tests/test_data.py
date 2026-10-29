"""
Data Pipeline & Integrity Tests for Health360
Tests dataset loading, schema verification, missing value elimination,
and duplicate detection.
"""

import unittest
import pandas as pd
import sqlite3
import os

class TestHealthcareDataPipeline(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
        cls.raw_csv = os.path.join(cls.base_dir, "data", "original_dataset.csv")
        cls.clean_csv = os.path.join(cls.base_dir, "data", "cleaned_dataset.csv")
        cls.db_path = os.path.join(cls.base_dir, "database", "healthcare.db")

    def test_01_raw_dataset_exists_and_loaded(self):
        self.assertTrue(os.path.exists(self.raw_csv), "Raw dataset file must exist.")
        df_raw = pd.read_csv(self.raw_csv)
        self.assertGreater(len(df_raw), 5000, "Raw dataset should contain initial records including duplicates.")
        self.assertEqual(df_raw.shape[1], 17, "Raw dataset must have 17 core columns.")

    def test_02_cleaned_dataset_record_count(self):
        self.assertTrue(os.path.exists(self.clean_csv), "Cleaned dataset file must exist.")
        df_clean = pd.read_csv(self.clean_csv)
        self.assertEqual(len(df_clean), 5000, "Cleaned dataset must have exactly 5,000 records.")

    def test_03_cleaned_dataset_no_missing_values(self):
        df_clean = pd.read_csv(self.clean_csv)
        total_nulls = df_clean.isnull().sum().sum()
        self.assertEqual(total_nulls, 0, f"Cleaned dataset should have 0 missing values, found {total_nulls}.")

    def test_04_no_duplicate_patient_ids(self):
        df_clean = pd.read_csv(self.clean_csv)
        duplicates = df_clean.duplicated(subset=['Patient_ID']).sum()
        self.assertEqual(duplicates, 0, "Cleaned dataset must have unique Patient_IDs.")

    def test_05_database_tables_and_record_counts(self):
        self.assertTrue(os.path.exists(self.db_path), "SQLite database must exist.")
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM patients_cleaned")
        clean_count = cursor.fetchone()[0]
        self.assertEqual(clean_count, 5000, "Table 'patients_cleaned' must contain 5,000 records.")
        
        cursor.execute("SELECT COUNT(*) FROM patients_raw")
        raw_count = cursor.fetchone()[0]
        self.assertGreater(raw_count, 5000, "Table 'patients_raw' must contain raw ingestion count.")
        
        conn.close()

if __name__ == '__main__':
    unittest.main()
