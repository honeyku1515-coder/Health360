"""
Data Cleaning & Preprocessing Pipeline for Health360
Cleans raw patient health records, handles missing data, resolves duplicates,
standardizes categories, and derives clinical calculation fields.
"""

import pandas as pd
import numpy as np
import os

def clean_healthcare_data(raw_data_path, cleaned_output_path):
    print(f"Loading raw dataset from {raw_data_path}...")
    df_raw = pd.read_csv(raw_data_path)
    initial_rows, initial_cols = df_raw.shape
    print(f"Initial raw shape: {initial_rows} rows x {initial_cols} columns")
    
    # 1. Deduplication
    duplicates = df_raw.duplicated(subset=['Patient_ID'], keep='first')
    num_duplicates = duplicates.sum()
    df_cleaned = df_raw.drop_duplicates(subset=['Patient_ID'], keep='first').copy()
    print(f"Deduplication: Removed {num_duplicates} duplicate records based on Patient_ID.")
    
    # 2. Category Standardization
    # Standardize Exercise_Level
    df_cleaned['Exercise_Level'] = df_cleaned['Exercise_Level'].astype(str).str.strip().str.title()
    # Ensure known valid categories
    valid_exercise = ['Sedentary', 'Moderate', 'Active']
    df_cleaned['Exercise_Level'] = df_cleaned['Exercise_Level'].apply(
        lambda x: x if x in valid_exercise else 'Moderate'
    )
    
    # Standardize Smoking_Habit
    df_cleaned['Smoking_Habit'] = df_cleaned['Smoking_Habit'].astype(str).str.strip().str.title()
    
    # Standardize Alcohol_Consumption
    df_cleaned['Alcohol_Consumption'] = df_cleaned['Alcohol_Consumption'].fillna('Non-Drinker').astype(str).str.strip().str.title()
    # Replace any literal 'None' or 'Nan' with 'Non-Drinker'
    df_cleaned['Alcohol_Consumption'] = df_cleaned['Alcohol_Consumption'].replace({'None': 'Non-Drinker', 'Nan': 'Non-Drinker'})
    
    # 3. Missing Value Imputation
    missing_before = df_cleaned.isnull().sum()
    missing_cols = missing_before[missing_before > 0]
    if not missing_cols.empty:
        print("Missing values detected before cleaning:")
        for col, count in missing_cols.items():
            print(f"  - {col}: {count} missing values")
            
    # Impute BMI using median
    if df_cleaned['BMI'].isnull().sum() > 0:
        median_bmi = df_cleaned['BMI'].median()
        df_cleaned['BMI'] = df_cleaned['BMI'].fillna(median_bmi)
        print(f"Imputed missing BMI with median value: {median_bmi:.1f}")
        
    # Impute Cholesterol using median
    if df_cleaned['Cholesterol_Level'].isnull().sum() > 0:
        median_chol = df_cleaned['Cholesterol_Level'].median()
        df_cleaned['Cholesterol_Level'] = df_cleaned['Cholesterol_Level'].fillna(median_chol)
        print(f"Imputed missing Cholesterol with median value: {median_chol:.0f}")
        
    # 4. Data Type Casts & Validation
    df_cleaned['Age'] = df_cleaned['Age'].astype(int)
    df_cleaned['BMI'] = df_cleaned['BMI'].astype(float).round(1)
    df_cleaned['Blood_Pressure'] = df_cleaned['Blood_Pressure'].astype(float).round(2)
    df_cleaned['Cholesterol_Level'] = df_cleaned['Cholesterol_Level'].astype(int)
    df_cleaned['Glucose_Level'] = df_cleaned['Glucose_Level'].astype(int)
    df_cleaned['Health_Risk_Score'] = df_cleaned['Health_Risk_Score'].astype(float).round(1)
    
    # 5. Feature Engineering / Calculated Fields
    
    # Age Group calculation logic as per Health360 project spec:
    # 18-30: Teenager
    # 31-40: Young Adult
    # 41-50: Adult
    # 51-60: Middle Age
    # 61-70: Senior
    # >70: Old
    def get_age_group(age):
        if 18 <= age <= 30:
            return 'Teenager'
        elif 31 <= age <= 40:
            return 'Young Adult'
        elif 41 <= age <= 50:
            return 'Adult'
        elif 51 <= age <= 60:
            return 'Middle Age'
        elif 61 <= age <= 70:
            return 'Senior'
        elif age > 70:
            return 'Old'
        return 'Unknown'
        
    df_cleaned['Age_Group'] = df_cleaned['Age'].apply(get_age_group)
    
    # BMI Category calculation:
    # < 18.5: Underweight
    # 18.5 - 24.9: Normal
    # 25.0 - 29.9: Overweight
    # >= 30.0: Obese
    def get_bmi_category(bmi):
        if bmi < 18.5:
            return 'Underweight'
        elif bmi < 25.0:
            return 'Normal'
        elif bmi < 30.0:
            return 'Overweight'
        else:
            return 'Obese'
            
    df_cleaned['BMI_Category'] = df_cleaned['BMI'].apply(get_bmi_category)
    
    # Blood Pressure Category
    def get_bp_category(bp):
        if bp < 120:
            return 'Normal'
        elif bp < 130:
            return 'Elevated'
        elif bp < 140:
            return 'Stage 1 Hypertension'
        else:
            return 'Stage 2 Hypertension'
            
    df_cleaned['BP_Category'] = df_cleaned['Blood_Pressure'].apply(get_bp_category)
    
    # High Risk Binary Flag
    df_cleaned['Is_High_Risk'] = (
        (df_cleaned['Health_Risk_Score'] >= 7.0) | 
        (df_cleaned['Heart_Disease'] == 'Yes') | 
        (df_cleaned['Stroke_History'] == 'Yes')
    ).astype(int)
    
    final_rows, final_cols = df_cleaned.shape
    print(f"\nFinal cleaned shape: {final_rows} rows x {final_cols} columns")
    print(f"Missing values remaining: {df_cleaned.isnull().sum().sum()}")
    
    # Save output
    os.makedirs(os.path.dirname(cleaned_output_path), exist_ok=True)
    df_cleaned.to_csv(cleaned_output_path, index=False)
    print(f"Cleaned dataset saved successfully to {cleaned_output_path}")
    
    return df_cleaned

if __name__ == "__main__":
    base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
    raw_path = os.path.join(base_dir, "data", "original_dataset.csv")
    cleaned_path = os.path.join(base_dir, "data", "cleaned_dataset.csv")
    clean_healthcare_data(raw_path, cleaned_path)
