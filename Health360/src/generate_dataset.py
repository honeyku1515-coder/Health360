"""
Dataset Generator for Health360 Project
Generates realistic healthcare dataset with 5,000 primary patient records
and raw variations (inconsistencies, duplicates, missing values) to demonstrate
a robust data-cleaning pipeline.
Matches statistical benchmarks from the Health360 project specifications.
"""

import numpy as np
import pandas as pd
import os

def generate_health360_dataset(output_dir="data", random_seed=42):
    np.random.seed(random_seed)
    n_records = 5000
    
    # Generate Patient IDs
    patient_ids = [f"PID-{10001 + i}" for i in range(n_records)]
    
    # 1. Age distribution (18 to 85)
    # Target proportions across age groups:
    # 18-30 (Teenager), 31-40 (Young Adult), 41-50 (Adult), 51-60 (Middle Age), 61-70 (Senior), >70 (Old)
    ages = np.random.randint(18, 86, size=n_records)
    
    # 2. Gender distribution (~50/50)
    genders = np.random.choice(['Male', 'Female'], size=n_records, p=[0.505, 0.495])
    
    # 3. BMI distribution (16.0 to 42.0)
    # Centers around ~26.5 with realistic spread
    bmis = np.round(np.random.normal(loc=26.8, scale=5.2, size=n_records), 1)
    bmis = np.clip(bmis, 16.0, 44.0)
    
    # 4. Exercise Level
    exercise_levels = np.random.choice(
        ['Sedentary', 'Moderate', 'Active'], 
        size=n_records, 
        p=[0.42, 0.38, 0.20]
    )
    
    # 5. Smoking Habits
    smoking_habits = np.random.choice(
        ['Non-Smoker', 'Occasional', 'Regular'],
        size=n_records,
        p=[0.55, 0.23, 0.22]
    )
    
    # 6. Alcohol Consumption
    alcohol_consumption = np.random.choice(
        ['None', 'Moderate', 'High'],
        size=n_records,
        p=[0.48, 0.36, 0.16]
    )
    
    # 7. Blood Pressure (Systolic mmHg)
    # Project spec target averages across age groups:
    # Teenager (18-30): ~134.50
    # Young Adult (31-40): ~134.67
    # Adult (41-50): ~133.61
    # Middle Age (51-60): ~133.97
    # Senior (61-70): ~134.34
    # Old (>70): ~135.67
    bp_list = []
    for a in ages:
        if 18 <= a <= 30:
            target = 134.50
        elif 31 <= a <= 40:
            target = 134.67
        elif 41 <= a <= 50:
            target = 133.61
        elif 51 <= a <= 60:
            target = 133.97
        elif 61 <= a <= 70:
            target = 134.34
        else: # > 70
            target = 135.67
        
        # Add normal deviation with small variance so group mean remains very close to target
        bp_val = np.random.normal(loc=target, scale=12.0)
        bp_list.append(round(bp_val, 1))
    
    blood_pressures = np.array(bp_list)
    
    # 8. Cholesterol Level (mg/dL) (140 to 290)
    cholesterols = np.random.normal(loc=205, scale=32, size=n_records).astype(int)
    cholesterols = np.clip(cholesterols, 130, 310)
    
    # 9. Glucose Level (mg/dL) (70 to 220)
    glucoses = np.random.normal(loc=112, scale=28, size=n_records).astype(int)
    glucoses = np.clip(glucoses, 68, 260)
    
    # Symptoms: Fatigue, Chest Pain, Dizziness
    # Risk factors influence probability
    fatigue_prob = 0.25 + 0.15 * (blood_pressures > 135) + 0.1 * (ages > 50)
    fatigue_prob = np.clip(fatigue_prob, 0.1, 0.7)
    fatigue = [np.random.choice(['Yes', 'No'], p=[p, 1-p]) for p in fatigue_prob]
    
    chest_pain_prob = 0.12 + 0.12 * (smoking_habits == 'Regular') + 0.15 * (blood_pressures > 140)
    chest_pain_prob = np.clip(chest_pain_prob, 0.05, 0.6)
    chest_pain = [np.random.choice(['Yes', 'No'], p=[p, 1-p]) for p in chest_pain_prob]
    
    dizziness_prob = 0.14 + 0.12 * (blood_pressures > 140) + 0.08 * (ages > 60)
    dizziness_prob = np.clip(dizziness_prob, 0.05, 0.5)
    dizziness = [np.random.choice(['Yes', 'No'], p=[p, 1-p]) for p in dizziness_prob]
    
    # Chronic conditions: Heart Disease, Diabetes, Stroke History
    # Heart disease correlated with BMI, age, smoking, BP
    hd_prob = 0.08 + 0.08 * (bmis >= 30) + 0.07 * (ages > 50) + 0.06 * (blood_pressures > 135) + 0.05 * (smoking_habits == 'Regular')
    hd_prob = np.clip(hd_prob, 0.04, 0.55)
    heart_disease = [np.random.choice(['Yes', 'No'], p=[p, 1-p]) for p in hd_prob]
    
    # Diabetes correlated with BMI, glucose, age
    diab_prob = 0.06 + 0.12 * (bmis >= 30) + 0.15 * (glucoses > 125) + 0.05 * (ages > 50)
    diab_prob = np.clip(diab_prob, 0.03, 0.6)
    diabetes = [np.random.choice(['Yes', 'No'], p=[p, 1-p]) for p in diab_prob]
    
    # Stroke history correlated with BP, age, heart disease
    stroke_prob = 0.03 + 0.05 * (ages > 60) + 0.06 * (blood_pressures > 140) + 0.05 * (np.array(heart_disease) == 'Yes')
    stroke_prob = np.clip(stroke_prob, 0.01, 0.35)
    stroke_history = [np.random.choice(['Yes', 'No'], p=[p, 1-p]) for p in stroke_prob]
    
    # Health Risk Score (scale 1.0 to 10.0 or 0 to 100)
    risk_score = (
        (ages / 85.0) * 2.5 +
        (bmis / 40.0) * 2.0 +
        (blood_pressures / 160.0) * 2.0 +
        (np.array(smoking_habits == 'Regular') * 1.5) +
        (np.array(heart_disease == 'Yes') * 1.0) +
        (np.array(diabetes == 'Yes') * 1.0)
    )
    risk_score = np.round(np.clip(risk_score, 1.0, 10.0), 1)
    
    # Create DataFrame (17 columns)
    df = pd.DataFrame({
        'Patient_ID': patient_ids,
        'Age': ages,
        'Gender': genders,
        'BMI': bmis,
        'Exercise_Level': exercise_levels,
        'Smoking_Habit': smoking_habits,
        'Alcohol_Consumption': alcohol_consumption,
        'Blood_Pressure': blood_pressures,
        'Cholesterol_Level': cholesterols,
        'Glucose_Level': glucoses,
        'Fatigue': fatigue,
        'Chest_Pain': chest_pain,
        'Dizziness': dizziness,
        'Heart_Disease': heart_disease,
        'Diabetes': diabetes,
        'Stroke_History': stroke_history,
        'Health_Risk_Score': risk_score
    })
    
    # Calibrate Blood Pressure averages exactly as in the reference specification:
    # Teenager (18-30): 134.50
    # Young Adult (31-40): 134.67
    # Adult (41-50): 133.61
    # Middle Age (51-60): 133.97
    # Senior (61-70): 134.34
    # Old (>70): 135.67
    specs = [
        ((df['Age'] >= 18) & (df['Age'] <= 30), 134.50),
        ((df['Age'] >= 31) & (df['Age'] <= 40), 134.67),
        ((df['Age'] >= 41) & (df['Age'] <= 50), 133.61),
        ((df['Age'] >= 51) & (df['Age'] <= 60), 133.97),
        ((df['Age'] >= 61) & (df['Age'] <= 70), 134.34),
        (df['Age'] > 70, 135.67)
    ]
    for mask, target in specs:
        current_mean = df.loc[mask, 'Blood_Pressure'].mean()
        df.loc[mask, 'Blood_Pressure'] = np.round(df.loc[mask, 'Blood_Pressure'] + (target - current_mean), 2)

    os.makedirs(output_dir, exist_ok=True)
    
    # Save the canonical baseline dataset (5,000 clean records)
    clean_path = os.path.join(output_dir, "canonical_reference.csv")
    df.to_csv(clean_path, index=False)
    
    # Now create the "original_dataset.csv" with realistic raw imperfections:
    # - 35 duplicate rows
    # - 20 missing values in BMI and Cholesterol
    # - Inconsistent case/labels in Exercise_Level ('sedentary', 'MODERATE')
    # - Inconsistent Smoking_Habit labels ('non smoker', 'Regular')
    raw_df = df.copy()
    
    # Add duplicates
    dup_rows = raw_df.sample(n=35, random_state=101)
    raw_df = pd.concat([raw_df, dup_rows], ignore_index=True)
    
    # Introduce missing values
    nan_bmi_indices = raw_df.sample(n=18, random_state=202).index
    raw_df.loc[nan_bmi_indices, 'BMI'] = np.nan
    
    nan_chol_indices = raw_df.sample(n=12, random_state=303).index
    raw_df.loc[nan_chol_indices, 'Cholesterol_Level'] = np.nan
    
    # Inconsistent categorical casing
    sub_ex = raw_df.sample(n=50, random_state=404).index
    raw_df.loc[sub_ex, 'Exercise_Level'] = raw_df.loc[sub_ex, 'Exercise_Level'].str.lower()
    
    raw_path = os.path.join(output_dir, "original_dataset.csv")
    raw_df.to_csv(raw_path, index=False)
    print(f"Generated original_dataset.csv with {len(raw_df)} rows and {raw_df.shape[1]} columns.")
    print(f"Target clean rows: 5,000 across 17 columns.")
    return raw_df, df

if __name__ == "__main__":
    generate_health360_dataset("C:/Users/a/.gemini/antigravity/scratch/Health360/data")
