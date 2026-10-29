-- Health360: Comprehensive Healthcare Risk & Disease Analysis
-- Database Schema & Analytical Views

DROP TABLE IF EXISTS patients_raw;
DROP TABLE IF EXISTS patients_cleaned;

-- Raw patient ingestion table
CREATE TABLE patients_raw (
    Patient_ID VARCHAR(20),
    Age INT,
    Gender VARCHAR(10),
    BMI REAL,
    Exercise_Level VARCHAR(20),
    Smoking_Habit VARCHAR(20),
    Alcohol_Consumption VARCHAR(20),
    Blood_Pressure REAL,
    Cholesterol_Level REAL,
    Glucose_Level REAL,
    Fatigue VARCHAR(10),
    Chest_Pain VARCHAR(10),
    Dizziness VARCHAR(10),
    Heart_Disease VARCHAR(10),
    Diabetes VARCHAR(10),
    Stroke_History VARCHAR(10),
    Health_Risk_Score REAL
);

-- Cleaned & verified patient table
CREATE TABLE patients_cleaned (
    Patient_ID VARCHAR(20) PRIMARY KEY,
    Age INT NOT NULL,
    Gender VARCHAR(10) NOT NULL,
    BMI REAL NOT NULL,
    Exercise_Level VARCHAR(20) NOT NULL,
    Smoking_Habit VARCHAR(20) NOT NULL,
    Alcohol_Consumption VARCHAR(20) NOT NULL,
    Blood_Pressure REAL NOT NULL,
    Cholesterol_Level INT NOT NULL,
    Glucose_Level INT NOT NULL,
    Fatigue VARCHAR(10) NOT NULL,
    Chest_Pain VARCHAR(10) NOT NULL,
    Dizziness VARCHAR(10) NOT NULL,
    Heart_Disease VARCHAR(10) NOT NULL,
    Diabetes VARCHAR(10) NOT NULL,
    Stroke_History VARCHAR(10) NOT NULL,
    Health_Risk_Score REAL NOT NULL,
    Age_Group VARCHAR(20) NOT NULL,
    BMI_Category VARCHAR(20) NOT NULL,
    BP_Category VARCHAR(30) NOT NULL,
    Is_High_Risk INT NOT NULL
);

-- Indexes for rapid dashboard querying and filter performance
CREATE INDEX idx_patients_age_group ON patients_cleaned(Age_Group);
CREATE INDEX idx_patients_bmi_category ON patients_cleaned(BMI_Category);
CREATE INDEX idx_patients_exercise_level ON patients_cleaned(Exercise_Level);
CREATE INDEX idx_patients_heart_disease ON patients_cleaned(Heart_Disease);
CREATE INDEX idx_patients_diabetes ON patients_cleaned(Diabetes);
CREATE INDEX idx_patients_gender ON patients_cleaned(Gender);

-- VIEW 1: KPI Executive Summary
CREATE VIEW vw_kpi_summary AS
SELECT 
    COUNT(*) AS Total_Patients,
    ROUND(AVG(Age), 1) AS Avg_Age,
    ROUND(AVG(BMI), 1) AS Avg_BMI,
    ROUND(AVG(Blood_Pressure), 2) AS Avg_Blood_Pressure,
    SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) AS Heart_Disease_Cases,
    ROUND(100.0 * SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Heart_Disease_Rate,
    SUM(CASE WHEN Diabetes = 'Yes' THEN 1 ELSE 0 END) AS Diabetes_Cases,
    ROUND(100.0 * SUM(CASE WHEN Diabetes = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Diabetes_Rate,
    SUM(CASE WHEN Stroke_History = 'Yes' THEN 1 ELSE 0 END) AS Stroke_Cases,
    ROUND(100.0 * SUM(CASE WHEN Stroke_History = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Stroke_Rate,
    SUM(Is_High_Risk) AS High_Risk_Cases
FROM patients_cleaned;

-- VIEW 2: Blood Pressure Across Age Groups
CREATE VIEW vw_blood_pressure_by_age_group AS
SELECT 
    Age_Group,
    COUNT(*) AS Patient_Count,
    ROUND(AVG(Blood_Pressure), 2) AS Avg_Blood_Pressure
FROM patients_cleaned
GROUP BY Age_Group
ORDER BY 
    CASE Age_Group
        WHEN 'Teenager' THEN 1
        WHEN 'Young Adult' THEN 2
        WHEN 'Adult' THEN 3
        WHEN 'Middle Age' THEN 4
        WHEN 'Senior' THEN 5
        WHEN 'Old' THEN 6
        ELSE 7
    END;

-- VIEW 3: Exercise Level Distribution
CREATE VIEW vw_exercise_distribution AS
SELECT 
    Exercise_Level,
    COUNT(*) AS Count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients_cleaned), 2) AS Percentage
FROM patients_cleaned
GROUP BY Exercise_Level;

-- VIEW 4: Age Group Distribution
CREATE VIEW vw_age_group_distribution AS
SELECT 
    Age_Group,
    COUNT(*) AS Count,
    ROUND(100.0 * COUNT(*) / (SELECT COUNT(*) FROM patients_cleaned), 2) AS Percentage
FROM patients_cleaned
GROUP BY Age_Group
ORDER BY 
    CASE Age_Group
        WHEN 'Teenager' THEN 1
        WHEN 'Young Adult' THEN 2
        WHEN 'Adult' THEN 3
        WHEN 'Middle Age' THEN 4
        WHEN 'Senior' THEN 5
        WHEN 'Old' THEN 6
        ELSE 7
    END;

-- VIEW 5: Alcohol and Smoking Habits by Age Group
CREATE VIEW vw_smoking_alcohol_by_age_group AS
SELECT 
    Age_Group,
    SUM(CASE WHEN Smoking_Habit = 'Regular' THEN 1 ELSE 0 END) AS Regular_Smokers,
    SUM(CASE WHEN Smoking_Habit = 'Occasional' THEN 1 ELSE 0 END) AS Occasional_Smokers,
    SUM(CASE WHEN Smoking_Habit = 'Non-Smoker' THEN 1 ELSE 0 END) AS Non_Smokers,
    SUM(CASE WHEN Alcohol_Consumption = 'High' THEN 1 ELSE 0 END) AS High_Alcohol,
    SUM(CASE WHEN Alcohol_Consumption = 'Moderate' THEN 1 ELSE 0 END) AS Moderate_Alcohol,
    SUM(CASE WHEN Alcohol_Consumption IN ('None', 'Non-Drinker') THEN 1 ELSE 0 END) AS Non_Drinkers
FROM patients_cleaned
GROUP BY Age_Group;

-- VIEW 6: BMI Category vs Heart Disease Rate
CREATE VIEW vw_bmi_vs_heart_disease AS
SELECT 
    BMI_Category,
    COUNT(*) AS Total_Patients,
    SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) AS Heart_Disease_Cases,
    ROUND(100.0 * SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Heart_Disease_Rate
FROM patients_cleaned
GROUP BY BMI_Category;

-- VIEW 7: Heart Disease vs Diabetes Prevalence by BMI Category
CREATE VIEW vw_heart_disease_diabetes_by_bmi AS
SELECT 
    BMI_Category,
    COUNT(*) AS Total_Patients,
    ROUND(100.0 * SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Heart_Disease_Prevalence,
    ROUND(100.0 * SUM(CASE WHEN Diabetes = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Diabetes_Prevalence
FROM patients_cleaned
GROUP BY BMI_Category;

-- VIEW 8: Heatmap Data - Heart Disease Rate by BMI Category and Exercise Level
CREATE VIEW vw_heart_disease_by_bmi_exercise AS
SELECT 
    BMI_Category,
    Exercise_Level,
    COUNT(*) AS Patient_Count,
    SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) AS Heart_Disease_Count,
    ROUND(100.0 * SUM(CASE WHEN Heart_Disease = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Heart_Disease_Rate
FROM patients_cleaned
GROUP BY BMI_Category, Exercise_Level;

-- VIEW 9: Age Group Distribution by Fatigue Condition
CREATE VIEW vw_fatigue_by_age_group AS
SELECT 
    Age_Group,
    SUM(CASE WHEN Fatigue = 'Yes' THEN 1 ELSE 0 END) AS Fatigue_Yes,
    SUM(CASE WHEN Fatigue = 'No' THEN 1 ELSE 0 END) AS Fatigue_No,
    ROUND(100.0 * SUM(CASE WHEN Fatigue = 'Yes' THEN 1 ELSE 0 END) / COUNT(*), 2) AS Fatigue_Prevalence
FROM patients_cleaned
GROUP BY Age_Group;
