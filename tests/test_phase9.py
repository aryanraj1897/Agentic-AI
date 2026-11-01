import os
import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.db.database import init_db, SessionLocal
from app.db.repository import (
    save_dataset_db,
    create_analysis_db,
    update_analysis_db,
    add_analysis_step_db,
    add_generated_file_db,
    get_analysis_db,
    list_analyses_db,
    delete_analysis_db
)

client = TestClient(app)

def setup_module(module):
    """Ensure SQLite database tables are created."""
    init_db()

def test_sqlite_repository_direct_crud():
    db = SessionLocal()
    try:
        dataset_id = "test_ds_p9"
        filename = "sales_p9.csv"
        filepath = "sample_data/sample.csv"

        # 1. Save dataset
        dataset = save_dataset_db(db, dataset_id, filename, filepath, 100, 5, {"filename": filename})
        assert dataset.id == dataset_id
        assert dataset.rows == 100

        # 2. Create analysis
        analysis_id = "test_analysis_p9"
        analysis = create_analysis_db(db, analysis_id, dataset_id, "Analyze sales performance", "started")
        assert analysis.id == analysis_id
        assert analysis.status == "started"

        # 3. Add steps and generated files
        step = add_analysis_step_db(db, analysis_id, "code_generator", "completed")
        assert step.step_name == "code_generator"

        gen_file = add_generated_file_db(db, analysis_id, "chart", "charts/chart_bar.png")
        assert gen_file.file_type == "chart"

        # 4. Update analysis
        updated = update_analysis_db(
            db,
            analysis_id,
            status="completed",
            generated_code="import pandas as pd",
            execution_result={"success": True, "stdout": "Done"}
        )
        assert updated.status == "completed"
        assert updated.generated_code == "import pandas as pd"

        # 5. List analyses
        analyses_list = list_analyses_db(db)
        assert any(a.id == analysis_id for a in analyses_list)

        # 6. Delete analysis
        deleted = delete_analysis_db(db, analysis_id)
        assert deleted is True
        assert get_analysis_db(db, analysis_id) is None
    finally:
        db.close()

def test_phase9_api_endpoints_integration():
    # 1. Upload dataset via API
    csv_content = "product,sales\nWidget A,100\nWidget B,200\n"
    files = {"file": ("e-commerce.csv", csv_content.encode("utf-8"), "text/csv")}
    upload_res = client.post("/api/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # 2. Start analysis via API
    query = "Analyze revenue and top selling products"
    custom_analysis_id = "analysis_phase9_test"
    start_req = {
        "dataset_id": dataset_id,
        "user_query": query,
        "analysis_id": custom_analysis_id
    }
    start_res = client.post("/api/analysis/start", json=start_req)
    assert start_res.status_code == 200
    res_data = start_res.json()
    assert res_data["analysis_id"] == custom_analysis_id

    # 3. GET /api/analyses (List all saved analyses in SQLite)
    list_res = client.get("/api/analyses")
    assert list_res.status_code == 200
    analyses_list = list_res.json()
    assert isinstance(analyses_list, list)
    assert any(a["id"] == custom_analysis_id for a in analyses_list)

    # 4. GET /api/analyses/{analysis_id} (Retrieve single analysis state)
    single_res = client.get(f"/api/analyses/{custom_analysis_id}")
    assert single_res.status_code == 200
    single_data = single_res.json()
    assert single_data["id"] == custom_analysis_id
    assert single_data["user_query"] == query
    assert "report" in single_data
    assert "charts" in single_data

    # 5. Retrieve report via GET /api/analysis/{analysis_id}/report
    report_res = client.get(f"/api/analysis/{custom_analysis_id}/report")
    assert report_res.status_code == 200
    assert "report" in report_res.json()

    # 6. Retrieve charts via GET /api/analysis/{analysis_id}/charts
    charts_res = client.get(f"/api/analysis/{custom_analysis_id}/charts")
    assert charts_res.status_code == 200
    assert "charts" in charts_res.json()

    # 7. DELETE /api/analyses/{analysis_id}
    del_res = client.delete(f"/api/analyses/{custom_analysis_id}")
    assert del_res.status_code == 200
    assert del_res.json()["success"] is True

    # 8. Verify deletion from SQLite API list
    get_after_del = client.get(f"/api/analyses/{custom_analysis_id}")
    assert get_after_del.status_code == 404
