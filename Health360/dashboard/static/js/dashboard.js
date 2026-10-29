/**
 * Health360 Interactive Dashboard Logic
 * Manages Chart.js instances, real-time AJAX API filtering,
 * KPI counter animation, and data synchronization.
 */

// Global Chart references for dynamic updates
let chartInstances = {};

document.addEventListener('DOMContentLoaded', () => {
    initFilters();
    fetchAnalyticsData();
    
    // Register change listeners for all filters
    const filterSelectors = [
        'filter-age-group', 'filter-bmi-category', 
        'filter-exercise-level', 'filter-gender', 
        'filter-smoking', 'filter-heart-disease', 'filter-diabetes'
    ];
    
    filterSelectors.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('change', () => fetchAnalyticsData());
        }
    });
    
    const resetBtn = document.getElementById('btn-reset-filters');
    if (resetBtn) {
        resetBtn.addEventListener('click', resetAllFilters);
    }
});

function initFilters() {
    fetch('/api/metadata')
        .then(res => res.json())
        .then(meta => {
            populateSelect('filter-age-group', meta.age_groups);
            populateSelect('filter-bmi-category', meta.bmi_categories);
            populateSelect('filter-exercise-level', meta.exercise_levels);
            populateSelect('filter-gender', meta.genders);
            populateSelect('filter-smoking', meta.smoking_habits);
        })
        .catch(err => console.error("Error loading filter metadata:", err));
}

function populateSelect(elemId, options) {
    const select = document.getElementById(elemId);
    if (!select) return;
    const currentVal = select.value;
    select.innerHTML = '';
    options.forEach(opt => {
        const el = document.createElement('option');
        el.value = opt;
        el.textContent = opt;
        select.appendChild(el);
    });
    if (currentVal && options.includes(currentVal)) {
        select.value = currentVal;
    }
}

function resetAllFilters() {
    const filterSelectors = [
        'filter-age-group', 'filter-bmi-category', 
        'filter-exercise-level', 'filter-gender', 
        'filter-smoking', 'filter-heart-disease', 'filter-diabetes'
    ];
    filterSelectors.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = 'All';
    });
    fetchAnalyticsData();
}

function getFilterParams() {
    const params = new URLSearchParams();
    const mappings = {
        'filter-age-group': 'age_group',
        'filter-bmi-category': 'bmi_category',
        'filter-exercise-level': 'exercise_level',
        'filter-gender': 'gender',
        'filter-smoking': 'smoking',
        'filter-heart-disease': 'heart_disease',
        'filter-diabetes': 'diabetes'
    };
    for (const [id, param] of Object.entries(mappings)) {
        const el = document.getElementById(id);
        if (el && el.value !== 'All') {
            params.append(param, el.value);
        }
    }
    return params.toString();
}

function fetchAnalyticsData() {
    const queryStr = getFilterParams();
    const url = `/api/analytics?${queryStr}`;
    
    fetch(url)
        .then(res => res.json())
        .then(data => {
            if (data.empty) {
                alert("No patients match the selected filter criteria. Please broaden your selection.");
                return;
            }
            updateKPIs(data.kpis);
            renderCharts(data.charts);
            renderSampleTable(data.sample_table);
        })
        .catch(err => console.error("Error fetching analytics data:", err));
}

function updateKPIs(kpis) {
    document.getElementById('kpi-total-patients').textContent = kpis.total_patients.toLocaleString();
    document.getElementById('kpi-avg-age').textContent = `${kpis.avg_age} yrs`;
    document.getElementById('kpi-avg-bmi').textContent = `${kpis.avg_bmi} kg/m²`;
    document.getElementById('kpi-avg-bp').textContent = `${kpis.avg_blood_pressure} mmHg`;
    document.getElementById('kpi-heart-disease').textContent = `${kpis.heart_disease_rate}%`;
    document.getElementById('kpi-heart-disease-sub').textContent = `${kpis.heart_disease_cases.toLocaleString()} Confirmed Cases`;
    document.getElementById('kpi-diabetes').textContent = `${kpis.diabetes_rate}%`;
    document.getElementById('kpi-diabetes-sub').textContent = `${kpis.diabetes_cases.toLocaleString()} Confirmed Cases`;
}

function renderCharts(charts) {
    // 1. Average Blood Pressure Across Age Groups
    renderChart('chart-bp-age', {
        type: 'bar',
        data: {
            labels: charts.blood_pressure.labels,
            datasets: [{
                label: 'Mean Systolic BP (mmHg)',
                data: charts.blood_pressure.values,
                backgroundColor: '#e67e22',
                borderColor: '#b96317',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { min: 125, max: 140, title: { display: true, text: 'Systolic BP (mmHg)' } }
            }
        }
    });

    // 2. Exercise Level Distribution (Donut Chart)
    renderChart('chart-exercise-donut', {
        type: 'doughnut',
        data: {
            labels: charts.exercise.labels,
            datasets: [{
                data: charts.exercise.values,
                backgroundColor: ['#e74c3c', '#f39c12', '#2ecc71'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // 3. Patient Distribution by Age Group (Pie Chart)
    renderChart('chart-age-pie', {
        type: 'pie',
        data: {
            labels: charts.age_distribution.labels,
            datasets: [{
                data: charts.age_distribution.values,
                backgroundColor: ['#3498db', '#e67e22', '#2ecc71', '#9b59b6', '#e74c3c', '#1abc9c'],
                borderWidth: 2,
                borderColor: '#ffffff'
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            plugins: {
                legend: { position: 'bottom' }
            }
        }
    });

    // 4. Smoking Habits by Age Group
    renderChart('chart-smoking-grouped', {
        type: 'bar',
        data: {
            labels: charts.lifestyle.labels,
            datasets: [
                { label: 'Non-Smoker', data: charts.lifestyle.non_smokers, backgroundColor: '#2ecc71' },
                { label: 'Occasional', data: charts.lifestyle.occasional_smokers, backgroundColor: '#f1c40f' },
                { label: 'Regular', data: charts.lifestyle.regular_smokers, backgroundColor: '#e74c3c' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: false },
                y: { title: { display: true, text: 'Patient Count' } }
            }
        }
    });

    // 5. BMI Category vs Heart Disease Rate
    renderChart('chart-bmi-hd', {
        type: 'bar',
        data: {
            labels: charts.bmi_heart_disease.labels,
            datasets: [{
                label: 'Heart Disease Rate (%)',
                data: charts.bmi_heart_disease.values,
                backgroundColor: '#9b59b6',
                borderColor: '#76448a',
                borderWidth: 1,
                borderRadius: 4
            }]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Prevalence Rate (%)' } }
            }
        }
    });

    // 6. Heart Disease vs Diabetes Prevalence
    renderChart('chart-bmi-comparison', {
        type: 'bar',
        data: {
            labels: charts.bmi_comparison.labels,
            datasets: [
                { label: 'Heart Disease (%)', data: charts.bmi_comparison.heart_disease_rates, backgroundColor: '#e74c3c' },
                { label: 'Diabetes (%)', data: charts.bmi_comparison.diabetes_rates, backgroundColor: '#3498db' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                y: { beginAtZero: true, title: { display: true, text: 'Prevalence Rate (%)' } }
            }
        }
    });

    // 7. Fatigue by Age Group
    renderChart('chart-fatigue-bar', {
        type: 'bar',
        data: {
            labels: charts.fatigue.labels,
            datasets: [
                { label: 'Fatigue: No', data: charts.fatigue.fatigue_no, backgroundColor: '#95a5a6' },
                { label: 'Fatigue: Yes', data: charts.fatigue.fatigue_yes, backgroundColor: '#e74c3c' }
            ]
        },
        options: {
            responsive: true,
            maintainAspectRatio: false,
            scales: {
                x: { stacked: true },
                y: { stacked: true, title: { display: true, text: 'Patient Count' } }
            }
        }
    });

    // Render Heatmap Table
    renderHeatmapTable(charts.heatmap);
}

function renderChart(canvasId, config) {
    const canvas = document.getElementById(canvasId);
    if (!canvas) return;
    
    if (chartInstances[canvasId]) {
        chartInstances[canvasId].destroy();
    }
    
    chartInstances[canvasId] = new Chart(canvas.getContext('2d'), config);
}

function renderHeatmapTable(data) {
    const tbody = document.getElementById('heatmap-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    data.forEach(row => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: 600; text-align: left;">${row.bmi_category}</td>
            <td style="background-color: ${getHeatColor(row.Sedentary)}">${row.Sedentary}%</td>
            <td style="background-color: ${getHeatColor(row.Moderate)}">${row.Moderate}%</td>
            <td style="background-color: ${getHeatColor(row.Active)}">${row.Active}%</td>
        `;
        tbody.appendChild(tr);
    });
}

function getHeatColor(val) {
    // Color ramp from pale yellow to deep orange/red
    if (val < 10) return 'rgba(254, 240, 217, 0.7)';
    if (val < 15) return 'rgba(253, 204, 138, 0.7)';
    if (val < 20) return 'rgba(252, 141, 89, 0.7)';
    return 'rgba(227, 74, 51, 0.8)';
}

function renderSampleTable(records) {
    const tbody = document.getElementById('sample-table-tbody');
    if (!tbody) return;
    tbody.innerHTML = '';
    
    records.forEach(pt => {
        const tr = document.createElement('tr');
        tr.innerHTML = `
            <td style="font-weight: 600;">${pt.Patient_ID}</td>
            <td>${pt.Age}</td>
            <td>${pt.Gender}</td>
            <td>${pt.BMI} (${pt.BMI_Category})</td>
            <td>${pt.Exercise_Level}</td>
            <td>${pt.Blood_Pressure}</td>
            <td>${pt.Cholesterol_Level}</td>
            <td>${pt.Glucose_Level}</td>
            <td><span class="badge ${pt.Heart_Disease === 'Yes' ? 'yes' : 'no'}">${pt.Heart_Disease}</span></td>
            <td><span class="badge ${pt.Diabetes === 'Yes' ? 'yes' : 'no'}">${pt.Diabetes}</span></td>
            <td><strong>${pt.Health_Risk_Score}</strong></td>
        `;
        tbody.appendChild(tr);
    });
}
