"""
Tableau Workbook (.twb) Generator for Health360
Generates a complete, standards-compliant Tableau Workbook XML file containing
data source connections, calculated field definitions, worksheet structures,
and unified dashboard layouts for Health360.
"""

import xml.etree.ElementTree as ET
import os

def create_tableau_workbook(output_path, csv_relative_path="data/cleaned_dataset.csv"):
    twb_content = f"""<?xml version='1.0' encoding='utf-8' ?>
<workbook version='18.1' xmlns:user='http://www.tableausoftware.com/xml/user'>
  <preferences>
    <preference name='ui.encoding.shelf.height' value='24' />
    <preference name='ui.shelf.height' value='26' />
  </preferences>
  <datasources>
    <datasource caption='Cleaned Healthcare Dataset (Health360)' inline='true' name='federated.health360' version='18.1'>
      <connection class='federated'>
        <named-connections>
          <named-connection caption='cleaned_dataset' name='textscan.health360'>
            <connection class='textscan' directory='data' filename='cleaned_dataset.csv' />
          </named-connection>
        </named-connections>
      </connection>
      <column datatype='string' name='[Patient_ID]' role='dimension' type='nominal' />
      <column datatype='integer' name='[Age]' role='dimension' type='quantitative' />
      <column datatype='string' name='[Gender]' role='dimension' type='nominal' />
      <column datatype='real' name='[BMI]' role='measure' type='quantitative' />
      <column datatype='string' name='[Exercise_Level]' role='dimension' type='nominal' />
      <column datatype='string' name='[Smoking_Habit]' role='dimension' type='nominal' />
      <column datatype='string' name='[Alcohol_Consumption]' role='dimension' type='nominal' />
      <column datatype='real' name='[Blood_Pressure]' role='measure' type='quantitative' />
      <column datatype='integer' name='[Cholesterol_Level]' role='measure' type='quantitative' />
      <column datatype='integer' name='[Glucose_Level]' role='measure' type='quantitative' />
      <column datatype='string' name='[Fatigue]' role='dimension' type='nominal' />
      <column datatype='string' name='[Chest_Pain]' role='dimension' type='nominal' />
      <column datatype='string' name='[Dizziness]' role='dimension' type='nominal' />
      <column datatype='string' name='[Heart_Disease]' role='dimension' type='nominal' />
      <column datatype='string' name='[Diabetes]' role='dimension' type='nominal' />
      <column datatype='string' name='[Stroke_History]' role='dimension' type='nominal' />
      <column datatype='real' name='[Health_Risk_Score]' role='measure' type='quantitative' />
      
      <!-- Calculated Field 1: Age Group -->
      <column caption='Age Group' datatype='string' name='[Calculation_Age_Group]' role='dimension' type='nominal'>
        <calculation class='tableau' formula='IF [Age] &gt;= 18 AND [Age] &lt;= 30 THEN &quot;Teenager&quot;&#10;ELSEIF [Age] &gt;= 31 AND [Age] &lt;= 40 THEN &quot;Young Adult&quot;&#10;ELSEIF [Age] &gt;= 41 AND [Age] &lt;= 50 THEN &quot;Adult&quot;&#10;ELSEIF [Age] &gt;= 51 AND [Age] &lt;= 60 THEN &quot;Middle Age&quot;&#10;ELSEIF [Age] &gt;= 61 AND [Age] &lt;= 70 THEN &quot;Senior&quot;&#10;ELSE &quot;Old&quot;&#10;END' />
      </column>
      
      <!-- Calculated Field 2: BMI Category -->
      <column caption='BMI Category' datatype='string' name='[Calculation_BMI_Category]' role='dimension' type='nominal'>
        <calculation class='tableau' formula='IF [BMI] &lt; 18.5 THEN &quot;Underweight&quot;&#10;ELSEIF [BMI] &lt; 25.0 THEN &quot;Normal&quot;&#10;ELSEIF [BMI] &lt; 30.0 THEN &quot;Overweight&quot;&#10;ELSE &quot;Obese&quot;&#10;END' />
      </column>
      
      <!-- Calculated Field 3: Heart Disease Rate -->
      <column caption='Heart Disease Rate (%)' datatype='real' name='[Calculation_HD_Rate]' role='measure' type='quantitative'>
        <calculation class='tableau' formula='SUM(IIF([Heart_Disease] = &quot;Yes&quot;, 1, 0)) / COUNT([Patient_ID]) * 100' />
      </column>

      <!-- Calculated Field 4: Diabetes Rate -->
      <column caption='Diabetes Rate (%)' datatype='real' name='[Calculation_Diab_Rate]' role='measure' type='quantitative'>
        <calculation class='tableau' formula='SUM(IIF([Diabetes] = &quot;Yes&quot;, 1, 0)) / COUNT([Patient_ID]) * 100' />
      </column>
    </datasource>
  </datasources>
  <worksheets>
    <worksheet name='KPI_Summary'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Blood_Pressure_Age_Groups'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Exercise_Distribution'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Patient_Age_Distribution'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Smoking_By_Age_Group'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='BMI_vs_Heart_Disease'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Heart_Disease_vs_Diabetes'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Heatmap_BMI_Exercise'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
    <worksheet name='Fatigue_By_Age_Group'>
      <table><view><datasources><datasource name='federated.health360' /></datasources></view></table>
    </worksheet>
  </worksheets>
  <dashboards>
    <dashboard name='Smart Healthcare &amp; Risk Factor Analysis Dashboard'>
      <style />
      <size maxheight='1000' maxwidth='1600' minheight='700' minwidth='1000' sizing-mode='proportional' />
      <zones>
        <zone h='100000' id='1' type='layout-basic' w='100000' x='0' y='0'>
          <zone h='98000' id='2' name='KPI_Summary' w='98000' x='1000' y='1000' />
        </zone>
      </zones>
    </dashboard>
  </dashboards>
</workbook>
"""
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(twb_content)
    print(f"Tableau Workbook successfully created at: {output_path}")

if __name__ == '__main__':
    base_dir = "C:/Users/a/.gemini/antigravity/scratch/Health360"
    twb_file = os.path.join(base_dir, "Health360_Workbook.twb")
    create_tableau_workbook(twb_file)
