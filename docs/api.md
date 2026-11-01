# API Documentation

The Autonomous Data Analysis Agent exposes RESTful endpoints for managing datasets, executing analyses, tracking real-time status, and retrieving generated artifacts.

Base URL: `http://localhost:8000`

---

## 1. Health Endpoint

### `GET /api/health`
Checks backend operational status.

#### Response `200 OK`
```json
{
  "status": "ok",
  "service": "autonomous-data-analysis-agent"
}
```

---

## 2. Dataset Management Endpoints

### `POST /api/datasets/upload`
Uploads a CSV or Excel dataset file.

- **Content-Type**: `multipart/form-data`
- **Body Parameter**: `file` (Binary file, max 50 MB, `.csv`, `.xlsx`, `.xls`)

#### Response `200 OK`
```json
{
  "id": "e4a29a6b-91d1-41d9-9524-dfb7a42ec781",
  "filename": "sales_data.csv",
  "filepath": "uploads/e4a29a6b-91d1-41d9-9524-dfb7a42ec781_sales_data.csv",
  "rows": 1000,
  "columns": 6,
  "column_names": ["Date", "Region", "Category", "Sales", "Profit", "Quantity"],
  "upload_time": "2026-09-30T10:15:30.123456",
  "profile": {
    "num_rows": 1000,
    "num_cols": 6,
    "missing_values": {"Sales": 0},
    "duplicate_rows": 0
  }
}
```

---

### `GET /api/datasets`
Lists all uploaded datasets.

#### Response `200 OK`
```json
[
  {
    "id": "e4a29a6b-91d1-41d9-9524-dfb7a42ec781",
    "filename": "sales_data.csv",
    "rows": 1000,
    "columns": 6,
    "upload_time": "2026-09-30T10:15:30.123456"
  }
]
```

---

### `GET /api/datasets/{dataset_id}`
Retrieves metadata and initial profile for a specific dataset.

#### Response `200 OK`
Returns the dataset detail object.

#### Response `404 Not Found`
```json
{
  "detail": "Dataset not found"
}
```

---

### `DELETE /api/datasets/{dataset_id}`
Deletes dataset entry and associated uploaded file.

#### Response `200 OK`
```json
{
  "status": "success",
  "message": "Dataset e4a29a6b-91d1-41d9-9524-dfb7a42ec781 deleted"
}
```

---

## 3. Analysis Management Endpoints

### `POST /api/analysis` (and `POST /api/analyses`)
Triggers an autonomous data analysis run for an uploaded dataset.

#### Request Body
```json
{
  "dataset_id": "e4a29a6b-91d1-41d9-9524-dfb7a42ec781",
  "user_query": "Analyze total sales by region and identify monthly trends."
}
```

#### Response `200 OK`
```json
{
  "analysis_id": "8f3b21c4-72a3-4819-a912-1d54e389bc01",
  "status": "completed",
  "user_query": "Analyze total sales by region and identify monthly trends.",
  "intent": {
    "category": "trend_analysis"
  },
  "plan": {
    "steps": ["Load dataset", "Aggregate monthly sales", "Generate line chart"]
  },
  "generated_code": "import pandas as pd...",
  "execution_result": {
    "stdout": "Total Sales: $1,250,000"
  },
  "visualizations": [
    {
      "title": "Monthly Sales Trend",
      "filepath": "generated/charts/8f3b21c4_sales_trend.png"
    }
  ],
  "insights": {
    "key_findings": ["Sales peaked in Q4."]
  },
  "report": "# Executive Summary\n...",
  "created_at": "2026-09-30T10:16:00.000000"
}
```

---

### `GET /api/analyses`
Lists historical data analysis runs.

#### Response `200 OK`
```json
[
  {
    "id": "8f3b21c4-72a3-4819-a912-1d54e389bc01",
    "dataset_id": "e4a29a6b-91d1-41d9-9524-dfb7a42ec781",
    "user_query": "Analyze total sales by region",
    "status": "completed",
    "created_at": "2026-09-30T10:16:00.000000"
  }
]
```

---

### `GET /api/analyses/{analysis_id}`
Retrieves complete analysis details, step logs, code, charts, and report.

#### Response `200 OK`
Returns analysis detail object.

---

### `DELETE /api/analyses/{analysis_id}`
Deletes an analysis record and its generated files.

#### Response `200 OK`
```json
{
  "status": "success",
  "message": "Analysis 8f3b21c4-72a3-4819-a912-1d54e389bc01 deleted"
}
```
