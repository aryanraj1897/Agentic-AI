import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from langgraph.graph import END
from app.agents.graph import get_analysis_graph, route_after_execution
from app.agents.state import AgentState

def test_graph_successful_path():
    graph = get_analysis_graph()
    initial_state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "graph_success_test",
        "user_query": "Analyze employee departments and average salary",
        "retry_count": 0,
        "status": "started"
    }

    final_state = graph.invoke(initial_state)

    assert final_state["status"] == "completed"
    assert final_state["execution_result"]["success"] is True
    assert len(final_state.get("charts", [])) > 0
    assert len(final_state.get("insights", [])) > 0
    assert "# Executive Summary" in final_state.get("report", "")

def test_graph_router_error_path_under_max_retries():
    # Simulated execution error when retry_count < 3
    state: AgentState = {
        "execution_result": {"success": False, "stderr": "KeyError: 'Sales'"},
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 1
    }
    next_node = route_after_execution(state)
    assert next_node == "repair"

def test_graph_router_maximum_retry_path():
    # Simulated execution error when retry_count >= 3
    state: AgentState = {
        "execution_result": {"success": False, "stderr": "Persistent error"},
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 3
    }
    next_node = route_after_execution(state)
    # Maximum 3 retries reached: must route directly to 'report' (where report notes failure)
    assert next_node == "report"

def test_graph_failed_max_retries_end_to_end_report():
    from app.agents.report import report_node
    state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "graph_max_retry_test",
        "user_query": "Query forcing error",
        "retry_count": 3,  # Already at max retries
        "execution_error": "Simulated unrecoverable runtime crash",
        "execution_result": {"success": False},
        "status": "execution_failed"
    }

    res = report_node(state)
    assert "report" in res
    assert "ANALYSIS EXECUTION FAILED" in res["report"]
