import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend path to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.agents.state import AgentState
from app.agents.profiler import profile_dataset_node
from app.agents.intent import analyze_intent_node
from app.agents.planner import create_analysis_plan_node
from app.agents.graph import get_analysis_graph

client = TestClient(app)

def test_agent_state_creation():
    state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "test_ds_123",
        "user_query": "Analyze my sales data",
        "retry_count": 0,
        "status": "started"
    }
    assert state["dataset_id"] == "test_ds_123"
    assert state["user_query"] == "Analyze my sales data"
    assert state["retry_count"] == 0
    assert state["status"] == "started"

def test_individual_nodes_execution():
    # 1. Test profiler node
    initial_state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "test_ds_456",
        "user_query": "Summary of salary by department",
        "retry_count": 0,
        "status": "started"
    }

    profiler_res = profile_dataset_node(initial_state)
    assert profiler_res["status"] == "profiled"
    assert "dataset_profile" in profiler_res
    profile = profiler_res["dataset_profile"]
    assert profile["rows"] > 0

    # 2. Test intent node
    state_after_profile = {**initial_state, **profiler_res}
    intent_res = analyze_intent_node(state_after_profile)
    assert intent_res["status"] == "intent_analyzed"
    assert "intent" in intent_res
    assert "analysis_type" in intent_res["intent"]

    # 3. Test planner node
    state_after_intent = {**state_after_profile, **intent_res}
    planner_res = create_analysis_plan_node(state_after_intent)
    assert planner_res["status"] == "plan_created"
    assert "analysis_plan" in planner_res
    assert len(planner_res["analysis_plan"]) > 0

def test_graph_execution():
    graph = get_analysis_graph()

    initial_state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "graph_test_789",
        "user_query": "Find trends in my employee salaries",
        "retry_count": 0,
        "status": "started"
    }

    final_state = graph.invoke(initial_state)

    # Verify that dataset_profile, intent, and analysis_plan are populated
    assert "dataset_profile" in final_state and final_state["dataset_profile"] is not None
    assert "intent" in final_state and final_state["intent"] is not None
    assert "analysis_plan" in final_state and final_state["analysis_plan"] is not None
    assert final_state["status"] == "completed"

def test_analysis_api_endpoint():
    # First upload dataset to get a valid dataset_id
    csv_content = "id,product,sales\n1,Widget,500\n2,Gadget,800\n"
    files = {"file": ("sales_test.csv", csv_content.encode("utf-8"), "text/csv")}
    upload_res = client.post("/api/datasets/upload", files=files)
    assert upload_res.status_code == 201
    dataset_id = upload_res.json()["dataset_id"]

    # Call /api/analysis/start
    payload = {
        "dataset_id": dataset_id,
        "user_query": "Analyze top performing products by sales"
    }
    response = client.post("/api/analysis/start", json=payload)
    assert response.status_code == 200

    data = response.json()
    assert data["dataset_id"] == dataset_id
    assert "dataset_profile" in data
    assert "intent" in data
    assert "analysis_plan" in data
    assert data["status"] == "completed"
