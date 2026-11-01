import sys
import io
import json
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

def test_csv_upload_and_profiling():
    csv_content = (
        "id,name,age,salary,is_active\n"
        "1,Alice,30,90000.5,true\n"
        "2,Bob,35,75000.0,false\n"
        "3,Charlie,28,82000.0,true\n"
        "4,Diana,42,95000.0,true\n"
    )
    files = {"file": ("test_data.csv", csv_content.encode("utf-8"), "text/csv")}
    response = client.post("/api/datasets/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert "dataset_id" in data
    assert data["filename"] == "test_data.csv"
    assert data["rows"] == 4
    assert data["columns"] == 5

    dataset_id = data["dataset_id"]

    # Test GET metadata
    meta_resp = client.get(f"/api/datasets/{dataset_id}")
    assert meta_resp.status_code == 200
    assert meta_resp.json()["dataset_id"] == dataset_id

    # Test GET profile
    profile_resp = client.get(f"/api/datasets/{dataset_id}/profile")
    assert profile_resp.status_code == 200
    profile = profile_resp.json()
    assert profile["rows"] == 4
    assert profile["columns"] == 5
    assert "age" in profile["numeric_columns"] or "salary" in profile["numeric_columns"]

def test_excel_upload():
    df = pd.DataFrame({
        "product": ["Laptop", "Phone", "Tablet"],
        "price": [1200, 800, 500],
        "in_stock": [True, False, True]
    })
    excel_buffer = io.BytesIO()
    df.to_excel(excel_buffer, index=False, engine="openpyxl")
    excel_buffer.seek(0)

    files = {"file": ("test_excel.xlsx", excel_buffer.getvalue(), "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")}
    response = client.post("/api/datasets/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "test_excel.xlsx"
    assert data["rows"] == 3
    assert data["columns"] == 3

def test_json_upload():
    json_data = [
        {"user_id": 101, "role": "admin", "score": 98.5},
        {"user_id": 102, "role": "user", "score": 76.0},
        {"user_id": 103, "role": "user", "score": 88.0}
    ]
    files = {"file": ("data.json", json.dumps(json_data).encode("utf-8"), "application/json")}
    response = client.post("/api/datasets/upload", files=files)
    
    assert response.status_code == 201
    data = response.json()
    assert data["filename"] == "data.json"
    assert data["rows"] == 3
    assert data["columns"] == 3

def test_invalid_file_type():
    pdf_content = b"%PDF-1.4 Fake PDF Content"
    files = {"file": ("document.pdf", pdf_content, "application/pdf")}
    response = client.post("/api/datasets/upload", files=files)
    
    assert response.status_code == 400
    assert "Unsupported file format" in response.json()["detail"]

def test_empty_dataset_upload():
    empty_csv = ""
    files = {"file": ("empty.csv", empty_csv.encode("utf-8"), "text/csv")}
    response = client.post("/api/datasets/upload", files=files)
    
    assert response.status_code == 400

def test_missing_values_detection():
    csv_with_missing = (
        "id,name,score\n"
        "1,Alice,\n"
        "2,,85.0\n"
        "3,Charlie,90.0\n"
    )
    files = {"file": ("missing.csv", csv_with_missing.encode("utf-8"), "text/csv")}
    response = client.post("/api/datasets/upload", files=files)
    assert response.status_code == 201
    dataset_id = response.json()["dataset_id"]

    profile_resp = client.get(f"/api/datasets/{dataset_id}/profile")
    assert profile_resp.status_code == 200
    profile = profile_resp.json()
    
    assert profile["total_missing_values"] == 2
    assert profile["column_profiles"]["score"]["missing_count"] == 1
    assert profile["column_profiles"]["name"]["missing_count"] == 1

def test_duplicate_rows_detection():
    csv_with_duplicates = (
        "item,price\n"
        "Apple,1.5\n"
        "Banana,0.75\n"
        "Apple,1.5\n"
        "Apple,1.5\n"
    )
    files = {"file": ("duplicates.csv", csv_with_duplicates.encode("utf-8"), "text/csv")}
    response = client.post("/api/datasets/upload", files=files)
    assert response.status_code == 201
    dataset_id = response.json()["dataset_id"]

    profile_resp = client.get(f"/api/datasets/{dataset_id}/profile")
    assert profile_resp.status_code == 200
    profile = profile_resp.json()
    
    assert profile["duplicate_rows"] == 2
