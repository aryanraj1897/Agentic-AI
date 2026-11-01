import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.agents.graph import get_analysis_graph
from app.agents.state import AgentState
from app.agents.visualization import visualization_node
from app.agents.insights import insights_node
from app.agents.report import report_node

client = TestClient(app)

def test_visualization_agent_chart_selection():
    state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_profile": {
            "filename": "sample.csv",
            "columns": ["department", "salary"],
            "numeric_columns": ["salary"],
            "categorical_columns": ["department"]
        },
        "intent": {
            "objective": "Compare department salaries",
            "tasks": ["compare_salaries"]
        },
        "execution_result": {"success": True, "stdout": "Salary analysis completed"}
    }

    res = visualization_node(state)
    assert res["status"] == "visualizations_generated"
    assert "charts" in res
    assert len(res["charts"]) > 0
    assert any("bar_chart" in c.get("type", "") for c in res["charts"])

def test_insights_agent_generation():
    state: AgentState = {
        "user_query": "Analyze employee salary distribution",
        "dataset_profile": {
            "columns": ["department", "salary"],
            "rows": 100
        },
        "execution_result": {
            "success": True,
            "stdout": "Department Mean Salary:\nEngineering: 95000\nSales: 75000"
        },
        "charts": [{"type": "bar_chart", "filename": "chart.png"}]
    }

    res = insights_node(state)
    assert res["status"] == "insights_generated"
    assert "insights" in res
    assert isinstance(res["insights"], list)
    assert len(res["insights"]) > 0

def test_report_agent_markdown_structure():
    state: AgentState = {
        "user_query": "Analyze sales performance and identify the best-performing products and regions.",
        "dataset_profile": {
            "filename": "sales.csv",
            "columns": ["product", "region", "sales"],
            "rows": 500,
            "missing_values": {"product": 0, "region": 0, "sales": 0},
            "duplicate_rows": 0
        },
        "intent": {
            "objective": "Identify top products and regions by sales",
            "tasks": ["top_products", "regional_sales"]
        },
        "analysis_plan": [{"step": 1, "action": "group_by_product"}],
        "execution_result": {
            "success": True,
            "stdout": "Top Product: Widget A ($50,000)\nTop Region: North ($120,000)"
        },
        "retry_count": 0,
        "charts": [{"type": "bar_chart", "filename": "top_products.png", "description": "Bar chart of sales"}],
        "insights": ["Widget A generated highest revenue.", "North region leads total sales."]
    }

    res = report_node(state)
    assert res["status"] == "completed"
    report_text = res.get("report", "")

    required_sections = [
        "# Executive Summary",
        "# Dataset Overview",
        "# Data Quality",
        "# Analysis Performed",
        "# Key Findings",
        "# Visualizations",
        "# Statistical Findings",
        "# Anomalies",
        "# Limitations",
        "# Recommendations"
    ]

    for section in required_sections:
        assert section in report_text, f"Missing required section '{section}' in generated report"

def test_failed_analysis_report_generation():
    state: AgentState = {
        "user_query": "Broken analysis query",
        "dataset_profile": {"filename": "corrupt.csv", "columns": ["id"], "rows": 10},
        "execution_result": {"success": False},
        "execution_error": "KeyError: 'non_existent'",
        "retry_count": 3
    }

    res = report_node(state)
    report_text = res.get("report", "")
    assert "ANALYSIS EXECUTION FAILED" in report_text
    assert "# Limitations" in report_text

def test_complete_phase7_end_to_end_sales_query():
    # 1. Upload dataset first
    csv_content = (
        "product,region,sales,date\n"
        "Widget A,North,1500,2024-01-01\n"
        "Widget B,South,2300,2024-01-02\n"
        "Widget A,East,1800,2024-01-03\n"
        "Widget C,North,3100,2024-01-04\n"
        "Widget B,North,2900,2024-01-05\n"
    )

    files = {"file": ("sales.csv", csv_content.encode("utf-8"), "text/csv")}
    upload_res = client.post("/api/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # 2. Run Analysis with query: "Analyze sales performance and identify the best-performing products and regions."
    query = "Analyze sales performance and identify the best-performing products and regions."
    analysis_req = {"dataset_id": dataset_id, "user_query": query}
    start_res = client.post("/api/analysis/start", json=analysis_req)
    assert start_res.status_code == 200

    data = start_res.json()
    assert "analysis_id" in data
    analysis_id = data["analysis_id"]

    # Verify state elements:
    assert data["generated_code"] is not None
    assert data["execution_result"] is not None
    assert data["execution_result"]["success"] is True
    assert len(data["charts"]) > 0
    assert len(data["insights"]) > 0
    assert data["report"] is not None

    # 3. Test Phase 7 API Endpoints
    # GET /api/analysis/{analysis_id}/results
    res_endpoint = client.get(f"/api/analysis/{analysis_id}/results")
    assert res_endpoint.status_code == 200
    res_json = res_endpoint.json()
    assert res_json["analysis_id"] == analysis_id
    assert "insights" in res_json

    # GET /api/analysis/{analysis_id}/charts
    charts_endpoint = client.get(f"/api/analysis/{analysis_id}/charts")
    assert charts_endpoint.status_code == 200
    charts_json = charts_endpoint.json()
    assert "charts" in charts_json
    assert len(charts_json["charts"]) > 0

    # GET /api/analysis/{analysis_id}/report
    report_endpoint = client.get(f"/api/analysis/{analysis_id}/report")
    assert report_endpoint.status_code == 200
    report_json = report_endpoint.json()
    assert "report" in report_json
    assert "# Executive Summary" in report_json["report"]
