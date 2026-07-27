# Enterprise Recruitment Analytics & Executive Dashboard Platform Guide (`resume-parser-v2`)

> Phase 13 Platform providing operational, executive, department, and compliance dashboards with 12 core recruitment KPIs, multi-chart datasets, automated insights, workload forecasting, and multi-format export.

---

## 🏛️ Analytics Architecture

```
               All FacultyIQ Modules (Phases 1–12)
                              │
                              ▼
                [1. KPI Calculation Engine]              <-- 12 core recruitment metrics
                              │
                              ▼
                [2. Chart Data Generator Engine]         <-- Bar, Line, Pie, Radar, Heatmap
                              │
                              ▼
                [3. Insights Engine]                     <-- Hiring, Bottleneck, Department, Risk
                              │
                              ▼
                [4. Workload Forecast Engine]            <-- Application volume, Interview load
                              │
                              ▼
                [5. Export Engine (CSV/JSON)]
                              │
                              ▼
              Final AnalyticsDashboardReport JSON
```

---

## 🔌 API Endpoints

### 1. `GET /api/v1/analytics/dashboard`

Returns full analytics dashboard with KPIs, charts, insights, forecasts, and alerts.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/analytics/dashboard?dashboard_type=University+Dashboard'
```

### 2. `GET /api/v1/analytics/kpi`

Returns all 12 core recruitment KPI metrics.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/analytics/kpi'
```

### 3. `GET /api/v1/analytics/charts`

Returns structured JSON chart datasets for frontend rendering.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/analytics/charts'
```

### 4. `GET /api/v1/analytics/reports`

Returns exportable analytics report with full KPI, chart, insight, and forecast data.

```bash
curl -X 'GET' 'http://localhost:8000/api/v1/analytics/reports'
```

---

## 📊 12 Core Recruitment KPIs

| # | KPI Name | Unit | Sample Value |
|---|----------|------|-------------|
| 1 | Applications Received | count | 347 |
| 2 | Applications Processed | count | 312 |
| 3 | Average Match Score | % | 78.4 |
| 4 | Average AI Confidence | % | 91.2 |
| 5 | Hiring Success Rate | % | 64.3 |
| 6 | Interview Conversion Rate | % | 72.1 |
| 7 | Offer Acceptance Rate | % | 85.0 |
| 8 | Average Time To Hire | days | 42 |
| 9 | Applications Per Department | count | 28.9 |
| 10 | Faculty Distribution | count | 156 |
| 11 | Research Score Distribution | score | 74.6 |
| 12 | Teaching Score Distribution | score | 81.3 |

---

## 📈 Chart Types Supported

| Chart Type | Use Case |
|------------|----------|
| Bar | Applications by Department |
| Line | Hiring Trends (Monthly) |
| Pie | Faculty Distribution by Rank |
| Radar | Average Candidate Competency Profile |
| Heatmap | Department Hiring Activity Heatmap |
