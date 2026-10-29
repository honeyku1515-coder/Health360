"""
Visualizations Generator for Health360
Renders high-resolution publication-quality medical analytics charts
matching the exact specifications and aesthetic of the Tableau Health360 dashboard.
"""

import os
os.environ['MPLCONFIGDIR'] = "C:/Users/a/.gemini/antigravity/scratch/Health360/.mplcache"
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np

# Set styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#cccccc'
plt.rcParams['axes.linewidth'] = 0.8

def generate_all_visualizations(cleaned_csv_path, output_dir):
    os.makedirs(output_dir, exist_ok=True)
    df = pd.read_csv(cleaned_csv_path)
    
    age_order = ['Teenager', 'Young Adult', 'Adult', 'Middle Age', 'Senior', 'Old']
    bmi_order = ['Underweight', 'Normal', 'Overweight', 'Obese']
    exercise_order = ['Sedentary', 'Moderate', 'Active']
    
    # Palette definition matching the Tableau warm/professional healthcare theme
    colors_main = ['#3498db', '#e74c3c', '#2ecc71', '#f39c12', '#9b59b6', '#1abc9c']
    
    print("Generating 9 Core Visualizations...")
    
    # -------------------------------------------------------------
    # 1. KPI Patient Health & Disease Overview Card Graphic
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(10, 4.5), dpi=300)
    ax.axis('off')
    
    total_patients = len(df)
    avg_age = df['Age'].mean()
    avg_bmi = df['BMI'].mean()
    avg_bp = df['Blood_Pressure'].mean()
    hd_rate = (df['Heart_Disease'] == 'Yes').mean() * 100
    diab_rate = (df['Diabetes'] == 'Yes').mean() * 100
    stroke_rate = (df['Stroke_History'] == 'Yes').mean() * 100
    
    kpis = [
        ("Total Cohort", f"{total_patients:,}", "Verified Records", "#2980b9"),
        ("Average Age", f"{avg_age:.1f} yrs", "Median: 52 yrs", "#8e44ad"),
        ("Mean Systolic BP", f"{avg_bp:.2f} mmHg", "Stage 1 Range", "#c0392b"),
        ("Heart Disease", f"{hd_rate:.1f}%", f"{(df['Heart_Disease']=='Yes').sum()} Cases", "#d35400"),
        ("Diabetes Rate", f"{diab_rate:.1f}%", f"{(df['Diabetes']=='Yes').sum()} Cases", "#16a085"),
        ("Stroke History", f"{stroke_rate:.1f}%", f"{(df['Stroke_History']=='Yes').sum()} Cases", "#7f8c8d")
    ]
    
    for i, (title, val, sub, col) in enumerate(kpis):
        x = 0.05 + (i % 3) * 0.32
        y = 0.55 if i < 3 else 0.10
        rect = plt.Rectangle((x, y), 0.28, 0.38, facecolor='#f8f9fa', edgecolor=col, linewidth=2, transform=ax.transAxes)
        ax.add_patch(rect)
        ax.text(x + 0.14, y + 0.26, title, fontsize=11, fontweight='bold', color='#555555', ha='center', transform=ax.transAxes)
        ax.text(x + 0.14, y + 0.13, val, fontsize=18, fontweight='heavy', color=col, ha='center', transform=ax.transAxes)
        ax.text(x + 0.14, y + 0.04, sub, fontsize=9, fontstyle='italic', color='#777777', ha='center', transform=ax.transAxes)
        
    ax.set_title("Health360: Executive KPI Summary - Patient Cohort & Clinical Overview", fontsize=13, fontweight='bold', pad=15, color='#2c3e50')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz1_kpi_overview.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 2. Bar Chart — Average Blood Pressure Across Age Groups
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8, 5), dpi=300)
    bp_data = df.groupby('Age_Group')['Blood_Pressure'].mean().reindex(age_order)
    
    bars = ax.bar(bp_data.index, bp_data.values, color='#e67e22', edgecolor='#b96317', width=0.55, zorder=3)
    ax.set_ylim(125, 140)
    ax.axhline(130, color='#e74c3c', linestyle='--', linewidth=1.2, label='Stage 1 HTN Threshold (130 mmHg)', zorder=2)
    ax.set_title("Average Blood Pressure Across Age Groups", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    ax.set_xlabel("Age Group", fontsize=10, fontweight='bold', labelpad=8)
    ax.set_ylabel("Systolic Blood Pressure (mmHg)", fontsize=10, fontweight='bold', labelpad=8)
    ax.legend(loc='lower right', frameon=True)
    ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=1)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold', color='#2c3e50')
                    
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz2_blood_pressure_age_groups.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 3. Grouped Bar Chart — Alcohol and Smoking Consumption Across Age Groups
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(9, 5), dpi=300)
    lifestyle_df = df.groupby(['Age_Group', 'Smoking_Habit']).size().unstack().reindex(age_order)
    lifestyle_df = lifestyle_df[['Non-Smoker', 'Occasional', 'Regular']]
    
    lifestyle_df.plot(kind='bar', ax=ax, colormap='Blues', edgecolor='#333333', linewidth=0.6, width=0.75, zorder=3)
    ax.set_title("Smoking Habit Distribution Across Patient Age Groups", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    ax.set_xlabel("Age Group", fontsize=10, fontweight='bold', labelpad=8)
    ax.set_ylabel("Patient Count", fontsize=10, fontweight='bold', labelpad=8)
    ax.legend(title="Smoking Status", frameon=True)
    ax.grid(axis='y', linestyle=':', alpha=0.6, zorder=1)
    plt.xticks(rotation=0)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz3_smoking_alcohol_age_groups.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 4. Donut Chart — Exercise Level Distribution
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 5), dpi=300)
    ex_counts = df['Exercise_Level'].value_counts().reindex(exercise_order)
    donut_colors = ['#e74c3c', '#f39c12', '#2ecc71']
    
    wedges, texts, autotexts = ax.pie(
        ex_counts, 
        labels=ex_counts.index, 
        autopct='%1.1f%%', 
        startangle=140, 
        colors=donut_colors,
        pctdistance=0.75,
        wedgeprops=dict(width=0.45, edgecolor='white', linewidth=2)
    )
    plt.setp(autotexts, size=10, weight="bold", color="white")
    plt.setp(texts, size=10, weight="bold")
    ax.set_title("Exercise Level Distribution in Population Cohort", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz4_exercise_distribution_donut.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 5. Pie Chart — Patient Distribution by Age Group
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(6.5, 5), dpi=300)
    age_counts = df['Age_Group'].value_counts().reindex(age_order)
    pie_colors = ['#3498db', '#e67e22', '#2ecc71', '#9b59b6', '#e74c3c', '#1abc9c']
    
    wedges, texts, autotexts = ax.pie(
        age_counts, 
        labels=age_counts.index, 
        autopct='%1.1f%%', 
        startangle=90, 
        colors=pie_colors,
        pctdistance=0.7,
        wedgeprops=dict(edgecolor='white', linewidth=1.5)
    )
    plt.setp(autotexts, size=9, weight="bold", color="white")
    plt.setp(texts, size=9, weight="bold")
    ax.set_title("Patient Demographics: Cohort Share by Age Group", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz5_age_distribution_pie.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 6. Grouped Bar Chart — Heart Disease vs Diabetes Prevalence by BMI Category
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    rates_by_bmi = df.groupby('BMI_Category').agg(
        HD_Rate=('Heart_Disease', lambda x: (x == 'Yes').mean() * 100),
        Diab_Rate=('Diabetes', lambda x: (x == 'Yes').mean() * 100)
    ).reindex(bmi_order)
    
    x = np.arange(len(bmi_order))
    width = 0.35
    
    rects1 = ax.bar(x - width/2, rates_by_bmi['HD_Rate'], width, label='Heart Disease (%)', color='#e74c3c', edgecolor='#b03a2e')
    rects2 = ax.bar(x + width/2, rates_by_bmi['Diab_Rate'], width, label='Diabetes (%)', color='#3498db', edgecolor='#2471a3')
    
    ax.set_title("Prevalence of Heart Disease vs. Diabetes across BMI Categories", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    ax.set_xticks(x)
    ax.set_xticklabels(bmi_order, fontweight='bold')
    ax.set_ylabel("Prevalence Rate (%)", fontsize=10, fontweight='bold', labelpad=8)
    ax.legend(frameon=True)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    
    for rect in list(rects1) + list(rects2):
        h = rect.get_height()
        ax.annotate(f"{h:.1f}%",
                    xy=(rect.get_x() + rect.get_width() / 2, h),
                    xytext=(0, 3), textcoords="offset points",
                    ha='center', va='bottom', fontsize=8, fontweight='bold')
                    
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz6_heart_disease_vs_diabetes_bmi.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 7. Bar Chart — BMI Category vs Heart Disease Rate
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    hd_bmi = df.groupby('BMI_Category')['Heart_Disease'].apply(lambda x: (x == 'Yes').mean() * 100).reindex(bmi_order)
    
    bars = ax.bar(hd_bmi.index, hd_bmi.values, color='#9b59b6', edgecolor='#76448a', width=0.5)
    ax.set_title("Heart Disease Incidence Rate Across BMI Categories", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    ax.set_xlabel("BMI Category (WHO Classification)", fontsize=10, fontweight='bold', labelpad=8)
    ax.set_ylabel("Heart Disease Rate (%)", fontsize=10, fontweight='bold', labelpad=8)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    
    for bar in bars:
        h = bar.get_height()
        ax.annotate(f"{h:.2f}%",
                    xy=(bar.get_x() + bar.get_width() / 2, h),
                    xytext=(0, 4), textcoords="offset points",
                    ha='center', va='bottom', fontsize=9, fontweight='bold')
                    
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz7_bmi_vs_heart_disease_rate.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 8. Heat Map — Heart Disease by BMI Category and Exercise Level
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(7.5, 5), dpi=300)
    heat_df = df.pivot_table(
        index='BMI_Category', 
        columns='Exercise_Level', 
        values='Heart_Disease', 
        aggfunc=lambda x: (x == 'Yes').mean() * 100
    ).reindex(index=bmi_order, columns=exercise_order)
    
    sns.heatmap(heat_df, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': 'Heart Disease Rate (%)'}, linewidths=1.5, linecolor='white', ax=ax)
    ax.set_title("Heatmap: Heart Disease Rate (%) by BMI & Exercise Level", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    ax.set_xlabel("Exercise Level", fontsize=10, fontweight='bold', labelpad=8)
    ax.set_ylabel("BMI Category", fontsize=10, fontweight='bold', labelpad=8)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz8_heatmap_bmi_exercise.png"))
    plt.close()
    
    # -------------------------------------------------------------
    # 9. Bar Chart — Age Group Distribution by Fatigue Condition
    # -------------------------------------------------------------
    fig, ax = plt.subplots(figsize=(8.5, 5), dpi=300)
    fatigue_data = df.groupby(['Age_Group', 'Fatigue']).size().unstack().reindex(age_order)
    
    fatigue_data[['No', 'Yes']].plot(kind='bar', stacked=True, color=['#95a5a6', '#e74c3c'], edgecolor='white', ax=ax, width=0.6)
    ax.set_title("Fatigue Symptom Prevalence Across Patient Age Groups", fontsize=12, fontweight='bold', pad=12, color='#2c3e50')
    ax.set_xlabel("Age Group", fontsize=10, fontweight='bold', labelpad=8)
    ax.set_ylabel("Number of Patients", fontsize=10, fontweight='bold', labelpad=8)
    ax.legend(title="Reports Fatigue?", frameon=True)
    ax.grid(axis='y', linestyle=':', alpha=0.6)
    plt.xticks(rotation=0)
    plt.tight_layout()
    fig.savefig(os.path.join(output_dir, "viz9_fatigue_by_age_group.png"))
    plt.close()
    
    print(f"All 9 visualizations generated and saved in: {output_dir}")

if __name__ == "__main__":
    base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
    cleaned_csv = os.path.join(base_dir, "data", "cleaned_dataset.csv")
    out_dir = os.path.join(base_dir, "visualizations")
    generate_all_visualizations(cleaned_csv, out_dir)
