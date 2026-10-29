"""
Health360 Flask Application
Full-stack interactive analytical dashboard and storytelling application.
Provides REST APIs for real-time multi-dimensional patient cohort filtering,
KPI recalculation, chart updates, and data exploration.
"""

from flask import Flask, render_template, jsonify, request, send_from_directory
import sqlite3
import pandas as pd
import numpy as np
import os

app = Flask(__name__, 
            template_folder=os.path.join(os.path.dirname(__file__), 'templates'),
            static_folder=os.path.join(os.path.dirname(__file__), 'static'))

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, 'database', 'healthcare.db')

def get_db_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def home():
    """Render the main Health360 analytics dashboard."""
    return render_template('index.html')

@app.route('/story')
def story():
    """Render the guided Health360 analytical story."""
    return render_template('story.html')

@app.route('/visualizations/<path:filename>')
def serve_visualizations(filename):
    """Serve generated visualization images."""
    viz_dir = os.path.join(BASE_DIR, 'visualizations')
    return send_from_directory(viz_dir, filename)

@app.route('/api/metadata')
def api_metadata():
    """Returns available filter options and categories."""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT DISTINCT Age_Group, BMI_Category, Exercise_Level, Gender, Smoking_Habit, Alcohol_Consumption FROM patients_cleaned", conn)
    conn.close()
    
    return jsonify({
        "age_groups": ['All', 'Teenager', 'Young Adult', 'Adult', 'Middle Age', 'Senior', 'Old'],
        "bmi_categories": ['All', 'Underweight', 'Normal', 'Overweight', 'Obese'],
        "exercise_levels": ['All', 'Sedentary', 'Moderate', 'Active'],
        "genders": ['All', 'Male', 'Female'],
        "smoking_habits": ['All', 'Non-Smoker', 'Occasional', 'Regular'],
        "alcohol_consumption": ['All', 'Non-Drinker', 'Moderate', 'High'],
        "diseases": ['All', 'Heart Disease', 'Diabetes', 'Stroke History']
    })

@app.route('/api/analytics', methods=['GET'])
def api_analytics():
    """
    Dynamic analytics endpoint that processes active query filters
    and returns updated KPIs, charts, and sample patient records.
    """
    age_group = request.args.get('age_group', 'All')
    bmi_category = request.args.get('bmi_category', 'All')
    exercise_level = request.args.get('exercise_level', 'All')
    gender = request.args.get('gender', 'All')
    smoking = request.args.get('smoking', 'All')
    heart_disease = request.args.get('heart_disease', 'All')
    diabetes = request.args.get('diabetes', 'All')
    
    query = "SELECT * FROM patients_cleaned WHERE 1=1"
    params = []
    
    if age_group != 'All':
        query += " AND Age_Group = ?"
        params.append(age_group)
    if bmi_category != 'All':
        query += " AND BMI_Category = ?"
        params.append(bmi_category)
    if exercise_level != 'All':
        query += " AND Exercise_Level = ?"
        params.append(exercise_level)
    if gender != 'All':
        query += " AND Gender = ?"
        params.append(gender)
    if smoking != 'All':
        query += " AND Smoking_Habit = ?"
        params.append(smoking)
    if heart_disease != 'All':
        query += " AND Heart_Disease = ?"
        params.append(heart_disease)
    if diabetes != 'All':
        query += " AND Diabetes = ?"
        params.append(diabetes)
        
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    
    total_records = len(df)
    
    if total_records == 0:
        return jsonify({
            "empty": True,
            "total_records": 0,
            "kpis": {},
            "charts": {},
            "sample_table": []
        })
        
    # Recalculate KPIs
    kpis = {
        "total_patients": total_records,
        "avg_age": round(float(df['Age'].mean()), 1),
        "avg_bmi": round(float(df['BMI'].mean()), 1),
        "avg_blood_pressure": round(float(df['Blood_Pressure'].mean()), 2),
        "heart_disease_cases": int((df['Heart_Disease'] == 'Yes').sum()),
        "heart_disease_rate": round(float(100.0 * (df['Heart_Disease'] == 'Yes').mean()), 2),
        "diabetes_cases": int((df['Diabetes'] == 'Yes').sum()),
        "diabetes_rate": round(float(100.0 * (df['Diabetes'] == 'Yes').mean()), 2),
        "stroke_cases": int((df['Stroke_History'] == 'Yes').sum()),
        "stroke_rate": round(float(100.0 * (df['Stroke_History'] == 'Yes').mean()), 2),
        "high_risk_cases": int(df['Is_High_Risk'].sum()),
        "high_risk_rate": round(float(100.0 * df['Is_High_Risk'].mean()), 2)
    }
    
    # 1. Blood Pressure Across Age Groups
    age_order = ['Teenager', 'Young Adult', 'Adult', 'Middle Age', 'Senior', 'Old']
    bp_data = df.groupby('Age_Group')['Blood_Pressure'].mean().to_dict()
    bp_chart = {
        "labels": [grp for grp in age_order if grp in bp_data],
        "values": [round(float(bp_data[grp]), 2) for grp in age_order if grp in bp_data]
    }
    
    # 2. Exercise Level Distribution
    ex_order = ['Sedentary', 'Moderate', 'Active']
    ex_counts = df['Exercise_Level'].value_counts().to_dict()
    exercise_chart = {
        "labels": [ex for ex in ex_order if ex in ex_counts],
        "values": [int(ex_counts[ex]) for ex in ex_order if ex in ex_counts]
    }
    
    # 3. Patient Distribution by Age Group
    age_counts = df['Age_Group'].value_counts().to_dict()
    age_dist_chart = {
        "labels": [grp for grp in age_order if grp in age_counts],
        "values": [int(age_counts[grp]) for grp in age_order if grp in age_counts]
    }
    
    # 4. Alcohol and Smoking across Age Groups
    lifestyle_chart = {
        "labels": [grp for grp in age_order if grp in age_counts],
        "regular_smokers": [],
        "occasional_smokers": [],
        "non_smokers": []
    }
    for grp in lifestyle_chart["labels"]:
        sub = df[df['Age_Group'] == grp]
        lifestyle_chart["regular_smokers"].append(int((sub['Smoking_Habit'] == 'Regular').sum()))
        lifestyle_chart["occasional_smokers"].append(int((sub['Smoking_Habit'] == 'Occasional').sum()))
        lifestyle_chart["non_smokers"].append(int((sub['Smoking_Habit'] == 'Non-Smoker').sum()))
        
    # 5. BMI Category vs Heart Disease Rate
    bmi_order = ['Underweight', 'Normal', 'Overweight', 'Obese']
    bmi_hd_dict = df.groupby('BMI_Category')['Heart_Disease'].apply(lambda x: (x == 'Yes').mean() * 100).to_dict()
    bmi_hd_chart = {
        "labels": [b for b in bmi_order if b in bmi_hd_dict],
        "values": [round(float(bmi_hd_dict[b]), 2) for b in bmi_order if b in bmi_hd_dict]
    }
    
    # 6. Heart Disease vs Diabetes Prevalence by BMI
    hd_by_bmi = df.groupby('BMI_Category')['Heart_Disease'].apply(lambda x: (x == 'Yes').mean() * 100).to_dict()
    diab_by_bmi = df.groupby('BMI_Category')['Diabetes'].apply(lambda x: (x == 'Yes').mean() * 100).to_dict()
    active_bmis = [b for b in bmi_order if b in hd_by_bmi or b in diab_by_bmi]
    bmi_comparison_chart = {
        "labels": active_bmis,
        "heart_disease_rates": [round(float(hd_by_bmi.get(b, 0)), 2) for b in active_bmis],
        "diabetes_rates": [round(float(diab_by_bmi.get(b, 0)), 2) for b in active_bmis]
    }
    
    # 7. Heatmap: Heart Disease Rate by BMI Category & Exercise Level
    heatmap_data = []
    for b in bmi_order:
        row = {"bmi_category": b}
        for ex in ex_order:
            sub = df[(df['BMI_Category'] == b) & (df['Exercise_Level'] == ex)]
            rate = round(float((sub['Heart_Disease'] == 'Yes').mean() * 100), 1) if len(sub) > 0 else 0.0
            row[ex] = rate
        heatmap_data.append(row)
        
    # 8. Fatigue by Age Group
    fatigue_chart = {
        "labels": [grp for grp in age_order if grp in age_counts],
        "fatigue_yes": [],
        "fatigue_no": []
    }
    for grp in fatigue_chart["labels"]:
        sub = df[df['Age_Group'] == grp]
        fatigue_chart["fatigue_yes"].append(int((sub['Fatigue'] == 'Yes').sum()))
        fatigue_chart["fatigue_no"].append(int((sub['Fatigue'] == 'No').sum()))
        
    # Sample Table (first 15 rows)
    sample_records = df[['Patient_ID', 'Age', 'Gender', 'BMI', 'BMI_Category', 
                         'Exercise_Level', 'Blood_Pressure', 'Cholesterol_Level', 
                         'Glucose_Level', 'Heart_Disease', 'Diabetes', 'Health_Risk_Score']].head(15).to_dict(orient='records')

    return jsonify({
        "empty": False,
        "total_records": total_records,
        "kpis": kpis,
        "charts": {
            "blood_pressure": bp_chart,
            "exercise": exercise_chart,
            "age_distribution": age_dist_chart,
            "lifestyle": lifestyle_chart,
            "bmi_heart_disease": bmi_hd_chart,
            "bmi_comparison": bmi_comparison_chart,
            "heatmap": heatmap_data,
            "fatigue": fatigue_chart
        },
        "sample_table": sample_records
    })

if __name__ == '__main__':
    # Run development server
    app.run(host='127.0.0.1', port=5000, debug=False)
