import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.state import AgentState
from app.agents.graph import get_analysis_graph
from app.services.llm_service import llm_service

def test_llm_service_intent_and_columns():
    profile = {
        "filename": "sales.csv",
        "numeric_columns": ["revenue", "quantity"],
        "categorical_columns": ["product", "region"],
        "date_columns": ["order_date"],
        "column_profiles": {
            "product": {"sample_values": ["Widget", "Gadget"]},
            "revenue": {"sample_values": [500.0, 1200.0]},
            "region": {"sample_values": ["North", "South"]},
            "order_date": {"sample_values": ["2024-01-15", "2024-02-01"]}
        }
    }

    intent = llm_service.analyze_intent("Find the top 10 products by revenue", profile)
    assert "required_columns" in intent
    assert any(c in profile["column_profiles"] for c in intent["required_columns"])

def test_phase4_graph_queries():
    graph = get_analysis_graph()

    queries = [
        "Find the top 10 products by revenue.",
        "Show monthly sales trends.",
        "Analyze regional performance."
    ]

    for q in queries:
        initial_state: AgentState = {
            "dataset_path": "sample_data/sample.csv",
            "dataset_id": "test_phase4_ds",
            "user_query": q,
            "retry_count": 0,
            "status": "started"
        }

        final_state = graph.invoke(initial_state)

        assert final_state["status"] == "completed"
        assert "generated_code" in final_state and len(final_state["generated_code"]) > 0
        assert "dataset_profile" in final_state
        assert "intent" in final_state
        assert "analysis_plan" in final_state

        # Check code contains pandas and dataset path or columns
        code = final_state["generated_code"]
        assert "pd.read_csv" in code or "pandas" in code
        print(f"\n--- Code Generated for '{q}' ---\n{code}")
