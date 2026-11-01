import sys
import pytest
import pandas as pd
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app

client = TestClient(app)

# 1. Sales Analysis E2E Test
def test_e2e_sales_analysis():
    sales_csv = "product,region,sales,units\nWidget A,North,15000,100\nWidget B,South,25000,200\nWidget A,East,18000,150\n"
    files = {"file": ("sales_e2e.csv", sales_csv.encode("utf-8"), "text/csv")}
    up = client.post("/api/datasets/upload", files=files)
    assert up.status_code == 201
    ds_id = up.json()["dataset_id"]

    start = client.post("/api/analysis/start", json={"dataset_id": ds_id, "user_query": "Analyze top products by total sales"})
    assert start.status_code == 200
    res = start.json()
    assert res["execution_result"]["success"] is True
    assert len(res["charts"]) > 0
    assert "# Executive Summary" in res["report"]

# 2. Customer Churn E2E Test
def test_e2e_customer_churn_analysis():
    churn_csv = "customer_id,tenure,monthly_charges,churned\nC101,12,65.5,0\nC102,2,89.0,1\nC103,24,45.0,0\nC104,1,95.0,1\n"
    files = {"file": ("churn_e2e.csv", churn_csv.encode("utf-8"), "text/csv")}
    up = client.post("/api/datasets/upload", files=files)
    assert up.status_code == 201
    ds_id = up.json()["dataset_id"]

    start = client.post("/api/analysis/start", json={"dataset_id": ds_id, "user_query": "Analyze customer churn rates by monthly charges"})
    assert start.status_code == 200
    res = start.json()
    assert res["execution_result"]["success"] is True

# 3. E-Commerce Analysis E2E Test
def test_e2e_ecommerce_analysis():
    ecom_csv = "order_id,category,quantity,price,discount\nO1,Electronics,2,499.99,0.1\nO2,Clothing,5,29.99,0.0\nO3,Electronics,1,899.99,0.05\n"
    files = {"file": ("ecommerce_e2e.csv", ecom_csv.encode("utf-8"), "text/csv")}
    up = client.post("/api/datasets/upload", files=files)
    assert up.status_code == 201
    ds_id = up.json()["dataset_id"]

    start = client.post("/api/analysis/start", json={"dataset_id": ds_id, "user_query": "Calculate category revenue and average discounts"})
    assert start.status_code == 200
    res = start.json()
    assert res["execution_result"]["success"] is True

# 4. Missing Values Dataset E2E Test
def test_e2e_missing_values_analysis():
    missing_csv = "id,value1,value2\n1,100,50\n2,,60\n3,300,\n4,400,80\n"
    files = {"file": ("missing_data.csv", missing_csv.encode("utf-8"), "text/csv")}
    up = client.post("/api/datasets/upload", files=files)
    assert up.status_code == 201
    ds_id = up.json()["dataset_id"]

    start = client.post("/api/analysis/start", json={"dataset_id": ds_id, "user_query": "Analyze missing values and compute mean metrics"})
    assert start.status_code == 200
    res = start.json()
    assert res["execution_result"]["success"] is True

# 5. Duplicate Records Dataset E2E Test
def test_e2e_duplicate_records_analysis():
    dup_csv = "name,department,salary\nAlice,Engineering,90000\nBob,Sales,70000\nAlice,Engineering,90000\nBob,Sales,70000\n"
    files = {"file": ("duplicates.csv", dup_csv.encode("utf-8"), "text/csv")}
    up = client.post("/api/datasets/upload", files=files)
    assert up.status_code == 201
    ds_id = up.json()["dataset_id"]

    start = client.post("/api/analysis/start", json={"dataset_id": ds_id, "user_query": "Identify duplicate records and summarize salary"})
    assert start.status_code == 200
    res = start.json()
    assert res["execution_result"]["success"] is True

# 6. Invalid Query Handling E2E Test
def test_e2e_invalid_query_handling():
    # Empty query or oversized query
    res = client.post("/api/analysis/start", json={"dataset_id": "ds_dummy", "user_query": ""})
    assert res.status_code == 400

# 7. Code Failure Handling E2E Test
def test_e2e_code_failure_handling():
    # Malicious script execution attempt blocked at validator
    from app.agents.validator import validate_code
    res = validate_code("import subprocess\nsubprocess.run(['ls'])")
    assert res["valid"] is False

# 8. Code Repair Self-Healing Recovery E2E Test
def test_e2e_code_repair_self_healing():
    from app.agents.repair import repair_code_node
    from app.agents.state import AgentState

    state: AgentState = {
        "user_query": "Analyze sales",
        "dataset_profile": {"columns": ["sales", "region"]},
        "generated_code": "import pandas as pd\ndf = pd.read_csv('sample.csv')\nprint(df['Sales'].mean())",
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 0
    }
    res = repair_code_node(state)
    assert res["retry_count"] == 1
    assert res["validated_code"] is None  # Re-validates repaired code
    assert "sales" in res["generated_code"].lower()
