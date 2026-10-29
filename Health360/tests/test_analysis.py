"""
Analysis & Statistical Calculation Tests for Health360
Validates calculated fields, age group segmentation, BMI categories,
and blood pressure benchmarks against project specifications.
"""

import unittest
import pandas as pd
import sqlite3
import os

class TestHealthcareAnalysis(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
        cls.clean_csv = os.path.join(cls.base_dir, "data", "cleaned_dataset.csv")
        cls.db_path = os.path.join(cls.base_dir, "database", "healthcare.db")
        cls.df = pd.read_csv(cls.clean_csv)

    def test_01_age_group_classification_logic(self):
        # Teenager: 18-30
        teenagers = self.df[self.df['Age_Group'] == 'Teenager']
        self.assertTrue(teenagers['Age'].between(18, 30).all(), "Teenagers must be aged 18 to 30.")

        # Young Adult: 31-40
        young_adults = self.df[self.df['Age_Group'] == 'Young Adult']
        self.assertTrue(young_adults['Age'].between(31, 40).all(), "Young Adults must be aged 31 to 40.")

        # Adult: 41-50
        adults = self.df[self.df['Age_Group'] == 'Adult']
        self.assertTrue(adults['Age'].between(41, 50).all(), "Adults must be aged 41 to 50.")

        # Middle Age: 51-60
        mid_age = self.df[self.df['Age_Group'] == 'Middle Age']
        self.assertTrue(mid_age['Age'].between(51, 60).all(), "Middle Age must be aged 51 to 60.")

        # Senior: 61-70
        seniors = self.df[self.df['Age_Group'] == 'Senior']
        self.assertTrue(seniors['Age'].between(61, 70).all(), "Seniors must be aged 61 to 70.")

        # Old: > 70
        old = self.df[self.df['Age_Group'] == 'Old']
        self.assertTrue((old['Age'] > 70).all(), "Old group must be strictly older than 70.")

    def test_02_bmi_category_thresholds(self):
        underweight = self.df[self.df['BMI_Category'] == 'Underweight']
        if len(underweight) > 0:
            self.assertTrue((underweight['BMI'] < 18.5).all(), "Underweight BMI < 18.5")

        normal = self.df[self.df['BMI_Category'] == 'Normal']
        self.assertTrue(normal['BMI'].between(18.5, 24.99).all(), "Normal BMI 18.5 - 24.9")

        overweight = self.df[self.df['BMI_Category'] == 'Overweight']
        self.assertTrue(overweight['BMI'].between(25.0, 29.99).all(), "Overweight BMI 25.0 - 29.9")

        obese = self.df[self.df['BMI_Category'] == 'Obese']
        self.assertTrue((obese['BMI'] >= 30.0).all(), "Obese BMI >= 30.0")

    def test_03_blood_pressure_benchmarks(self):
        # Benchmark verification from reference specifications:
        # Old: 135.67, Young Adult: 134.67, Teenager: 134.50, Senior: 134.34, Middle Age: 133.97, Adult: 133.61
        means = self.df.groupby('Age_Group')['Blood_Pressure'].mean().round(2)
        
        self.assertAlmostEqual(means['Old'], 135.67, places=1)
        self.assertAlmostEqual(means['Young Adult'], 134.67, places=1)
        self.assertAlmostEqual(means['Teenager'], 134.50, places=1)
        self.assertAlmostEqual(means['Senior'], 134.34, places=1)
        self.assertAlmostEqual(means['Middle Age'], 133.97, places=1)
        self.assertAlmostEqual(means['Adult'], 133.61, places=1)

    def test_04_database_analytical_views(self):
        conn = sqlite3.connect(self.db_path)
        
        # Test KPI view
        kpi_df = pd.read_sql_query("SELECT * FROM vw_kpi_summary", conn)
        self.assertEqual(len(kpi_df), 1)
        self.assertEqual(kpi_df['Total_Patients'].iloc[0], 5000)
        
        # Test BP view
        bp_df = pd.read_sql_query("SELECT * FROM vw_blood_pressure_by_age_group", conn)
        self.assertEqual(len(bp_df), 6)
        
        conn.close()

if __name__ == '__main__':
    unittest.main()
