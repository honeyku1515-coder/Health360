"""
Comprehensive Data Analysis & Statistical Modeling for Health360
Calculates descriptive statistics, epidemiological metrics, risk odds ratios,
and prepares structured analytical payloads for dashboards and reports.
"""

import sqlite3
import pandas as pd
import numpy as np
import json
import os

def run_comprehensive_analysis(db_path, output_dir):
    print("=" * 60)
    print("Running Health360 Comprehensive Statistical Analysis")
    print("=" * 60)
    
    os.makedirs(output_dir, exist_ok=True)
    conn = sqlite3.connect(db_path)
    
    df = pd.read_sql_query("SELECT * FROM patients_cleaned", conn)
    
    # 1. Overall Population Metrics (KPIs)
    kpis = {
        "total_patients": int(len(df)),
        "avg_age": float(round(df['Age'].mean(), 1)),
        "median_age": float(df['Age'].median()),
        "avg_bmi": float(round(df['BMI'].mean(), 1)),
        "avg_blood_pressure": float(round(df['Blood_Pressure'].mean(), 2)),
        "avg_cholesterol": float(round(df['Cholesterol_Level'].mean(), 1)),
        "avg_glucose": float(round(df['Glucose_Level'].mean(), 1)),
        "heart_disease_cases": int((df['Heart_Disease'] == 'Yes').sum()),
        "heart_disease_rate": float(round(100.0 * (df['Heart_Disease'] == 'Yes').mean(), 2)),
        "diabetes_cases": int((df['Diabetes'] == 'Yes').sum()),
        "diabetes_rate": float(round(100.0 * (df['Diabetes'] == 'Yes').mean(), 2)),
        "stroke_cases": int((df['Stroke_History'] == 'Yes').sum()),
        "stroke_rate": float(round(100.0 * (df['Stroke_History'] == 'Yes').mean(), 2)),
        "fatigue_cases": int((df['Fatigue'] == 'Yes').sum()),
        "fatigue_rate": float(round(100.0 * (df['Fatigue'] == 'Yes').mean(), 2)),
        "chest_pain_cases": int((df['Chest_Pain'] == 'Yes').sum()),
        "chest_pain_rate": float(round(100.0 * (df['Chest_Pain'] == 'Yes').mean(), 2)),
        "dizziness_cases": int((df['Dizziness'] == 'Yes').sum()),
        "dizziness_rate": float(round(100.0 * (df['Dizziness'] == 'Yes').mean(), 2)),
        "high_risk_cases": int(df['Is_High_Risk'].sum()),
        "high_risk_rate": float(round(100.0 * df['Is_High_Risk'].mean(), 2))
    }
    
    # 2. Age Group Segmentation Breakdown
    age_order = ['Teenager', 'Young Adult', 'Adult', 'Middle Age', 'Senior', 'Old']
    age_summary = []
    for grp in age_order:
        sub = df[df['Age_Group'] == grp]
        count = len(sub)
        pct = round(100.0 * count / len(df), 2)
        avg_bp = round(sub['Blood_Pressure'].mean(), 2)
        hd_rate = round(100.0 * (sub['Heart_Disease'] == 'Yes').mean(), 2)
        diab_rate = round(100.0 * (sub['Diabetes'] == 'Yes').mean(), 2)
        fatigue_rate = round(100.0 * (sub['Fatigue'] == 'Yes').mean(), 2)
        age_summary.append({
            "age_group": grp,
            "patient_count": count,
            "percentage": pct,
            "avg_blood_pressure": avg_bp,
            "heart_disease_rate": hd_rate,
            "diabetes_rate": diab_rate,
            "fatigue_rate": fatigue_rate
        })
        
    # 3. BMI Category vs Chronic Conditions
    bmi_order = ['Underweight', 'Normal', 'Overweight', 'Obese']
    bmi_summary = []
    for cat in bmi_order:
        sub = df[df['BMI_Category'] == cat]
        count = len(sub)
        pct = round(100.0 * count / len(df), 2)
        hd_cases = int((sub['Heart_Disease'] == 'Yes').sum())
        hd_rate = round(100.0 * hd_cases / count, 2) if count > 0 else 0
        diab_cases = int((sub['Diabetes'] == 'Yes').sum())
        diab_rate = round(100.0 * diab_cases / count, 2) if count > 0 else 0
        stroke_cases = int((sub['Stroke_History'] == 'Yes').sum())
        stroke_rate = round(100.0 * stroke_cases / count, 2) if count > 0 else 0
        bmi_summary.append({
            "bmi_category": cat,
            "patient_count": count,
            "percentage": pct,
            "heart_disease_cases": hd_cases,
            "heart_disease_rate": hd_rate,
            "diabetes_cases": diab_cases,
            "diabetes_rate": diab_rate,
            "stroke_rate": stroke_rate
        })

    # 4. Exercise Level Distribution
    ex_order = ['Sedentary', 'Moderate', 'Active']
    exercise_summary = []
    for ex in ex_order:
        sub = df[df['Exercise_Level'] == ex]
        count = len(sub)
        pct = round(100.0 * count / len(df), 2)
        hd_rate = round(100.0 * (sub['Heart_Disease'] == 'Yes').mean(), 2)
        exercise_summary.append({
            "exercise_level": ex,
            "patient_count": count,
            "percentage": pct,
            "heart_disease_rate": hd_rate
        })

    # 5. Alcohol & Smoking Consumption across Age Groups
    lifestyle_summary = []
    for grp in age_order:
        sub = df[df['Age_Group'] == grp]
        lifestyle_summary.append({
            "age_group": grp,
            "regular_smokers": int((sub['Smoking_Habit'] == 'Regular').sum()),
            "occasional_smokers": int((sub['Smoking_Habit'] == 'Occasional').sum()),
            "non_smokers": int((sub['Smoking_Habit'] == 'Non-Smoker').sum()),
            "high_alcohol": int((sub['Alcohol_Consumption'] == 'High').sum()),
            "moderate_alcohol": int((sub['Alcohol_Consumption'] == 'Moderate').sum()),
            "non_drinkers": int((sub['Alcohol_Consumption'].isin(['None', 'Non-Drinker'])).sum())
        })

    # 6. Heatmap Matrix: Heart Disease Rate (%) by BMI Category & Exercise Level
    heatmap_matrix = []
    for b_cat in bmi_order:
        row = {"bmi_category": b_cat}
        for ex in ex_order:
            sub = df[(df['BMI_Category'] == b_cat) & (df['Exercise_Level'] == ex)]
            rate = round(100.0 * (sub['Heart_Disease'] == 'Yes').mean(), 2) if len(sub) > 0 else 0.0
            row[ex] = rate
        heatmap_matrix.append(row)

    # 7. Fatigue Condition across Age Groups
    fatigue_summary = []
    for grp in age_order:
        sub = df[df['Age_Group'] == grp]
        fatigue_summary.append({
            "age_group": grp,
            "fatigue_yes": int((sub['Fatigue'] == 'Yes').sum()),
            "fatigue_no": int((sub['Fatigue'] == 'No').sum()),
            "prevalence_rate": round(100.0 * (sub['Fatigue'] == 'Yes').mean(), 2)
        })

    # 8. Tableau Calculated Fields Reference Dictionary
    tableau_calculations = [
        {
            "name": "Age Group",
            "formula": """IF [Age] >= 18 AND [Age] <= 30 THEN 'Teenager'
ELSEIF [Age] >= 31 AND [Age] <= 40 THEN 'Young Adult'
ELSEIF [Age] >= 41 AND [Age] <= 50 THEN 'Adult'
ELSEIF [Age] >= 51 AND [Age] <= 60 THEN 'Middle Age'
ELSEIF [Age] >= 61 AND [Age] <= 70 THEN 'Senior'
ELSE 'Old'
END""",
            "purpose": "Groups raw numerical patient age into demographic cohorts for stratified health comparison."
        },
        {
            "name": "BMI Category",
            "formula": """IF [BMI] < 18.5 THEN 'Underweight'
ELSEIF [BMI] < 25.0 THEN 'Normal'
ELSEIF [BMI] < 30.0 THEN 'Overweight'
ELSE 'Obese'
END""",
            "purpose": "Standardizes raw body mass index according to WHO classification thresholds."
        },
        {
            "name": "Heart Disease Prevalence Rate (%)",
            "formula": "SUM(IIF([Heart Disease] = 'Yes', 1, 0)) / COUNT([Patient ID]) * 100",
            "purpose": "Calculates the percentage of patients with diagnosed heart disease within any filtered cohort."
        },
        {
            "name": "Diabetes Prevalence Rate (%)",
            "formula": "SUM(IIF([Diabetes] = 'Yes', 1, 0)) / COUNT([Patient ID]) * 100",
            "purpose": "Calculates the percentage of patients with diabetes across demographic and clinical segments."
        },
        {
            "name": "High Risk Patient Flag",
            "formula": "IIF([Health Risk Score] >= 7.0 OR [Heart Disease] = 'Yes' OR [Stroke History] = 'Yes', 'High Risk', 'Standard Risk')",
            "purpose": "Identifies critical patient cohorts requiring urgent preventive intervention."
        }
    ]

    analysis_payload = {
        "kpis": kpis,
        "age_summary": age_summary,
        "bmi_summary": bmi_summary,
        "exercise_summary": exercise_summary,
        "lifestyle_summary": lifestyle_summary,
        "heatmap_matrix": heatmap_matrix,
        "fatigue_summary": fatigue_summary,
        "tableau_calculations": tableau_calculations
    }
    
    # Save payload to JSON
    json_path = os.path.join(output_dir, "analysis_results.json")
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(analysis_payload, f, indent=2)
    print(f"Analysis results saved to {json_path}")
    
    conn.close()
    return analysis_payload

if __name__ == "__main__":
    base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
    db_file = os.path.join(base_dir, "database", "healthcare.db")
    out_dir = os.path.join(base_dir, "data")
    run_comprehensive_analysis(db_file, out_dir)
