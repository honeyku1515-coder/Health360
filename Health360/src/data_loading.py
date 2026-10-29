"""
Database Ingestion & Management Module for Health360
Connects to SQLite database, executes schema DDL, imports raw and cleaned
datasets, verifies data integrity, and validates analytical views.
"""

import sqlite3
import pandas as pd
import os

def init_database(db_path, schema_path, raw_csv_path, cleaned_csv_path):
    print("=" * 60)
    print("Health360 Database Ingestion & Verification")
    print("=" * 60)
    
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # 1. Execute Schema DDL
    print(f"Reading schema from {schema_path}...")
    with open(schema_path, 'r', encoding='utf-8') as f:
        schema_sql = f.read()
    cursor.executescript(schema_sql)
    print("Schema DDL and analytical views created successfully.")
    
    # 2. Ingest Raw Dataset
    print(f"\nIngesting raw records from {raw_csv_path}...")
    df_raw = pd.read_csv(raw_csv_path)
    df_raw.to_sql('patients_raw', conn, if_exists='replace', index=False)
    cursor.execute("SELECT COUNT(*) FROM patients_raw")
    raw_count = cursor.fetchone()[0]
    print(f"-> Ingested {raw_count} raw records into table 'patients_raw'.")
    
    # 3. Ingest Cleaned Dataset
    print(f"\nIngesting cleaned records from {cleaned_csv_path}...")
    df_clean = pd.read_csv(cleaned_csv_path)
    df_clean.to_sql('patients_cleaned', conn, if_exists='replace', index=False)
    cursor.execute("SELECT COUNT(*) FROM patients_cleaned")
    clean_count = cursor.fetchone()[0]
    print(f"-> Ingested {clean_count} clean records into table 'patients_cleaned'.")
    
    # 4. Verification Queries
    print("\n--- KPI Summary Query Verification ---")
    kpi_df = pd.read_sql_query("SELECT * FROM vw_kpi_summary", conn)
    for col in kpi_df.columns:
        print(f"  {col}: {kpi_df[col].iloc[0]}")
        
    print("\n--- Blood Pressure Across Age Groups Verification ---")
    bp_df = pd.read_sql_query("SELECT * FROM vw_blood_pressure_by_age_group", conn)
    print(bp_df.to_string(index=False))
    
    print("\n--- Exercise Distribution Verification ---")
    ex_df = pd.read_sql_query("SELECT * FROM vw_exercise_distribution", conn)
    print(ex_df.to_string(index=False))
    
    conn.commit()
    conn.close()
    print("\nDatabase operations completed successfully.")
    return raw_count, clean_count

if __name__ == "__main__":
    base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
    db_file = os.path.join(base_dir, "database", "healthcare.db")
    schema_file = os.path.join(base_dir, "database", "schema.sql")
    raw_csv = os.path.join(base_dir, "data", "original_dataset.csv")
    clean_csv = os.path.join(base_dir, "data", "cleaned_dataset.csv")
    
    init_database(db_file, schema_file, raw_csv, clean_csv)
