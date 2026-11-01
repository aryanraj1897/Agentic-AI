import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from langgraph.graph import END
from app.agents.graph import route_after_execution, get_analysis_graph
from app.agents.repair import repair_code_node
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def test_route_after_execution_success():
    state: AgentState = {
        "execution_result": {"success": True, "stdout": "Success"},
        "execution_error": None,
        "retry_count": 0
    }
    assert route_after_execution(state) == "visualization"

def test_route_after_execution_failure_under_max_retries():
    state: AgentState = {
        "execution_result": {"success": False},
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 1
    }
    assert route_after_execution(state) == "repair"

def test_route_after_execution_max_retries_reached():
    state: AgentState = {
        "execution_result": {"success": False},
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 3
    }
    # Maximum 3 retries reached: must route to report node
    assert route_after_execution(state) == "report"

def test_repair_key_error():
    user_query = "Find average sales"
    dataset_profile = {"columns": ["sales", "revenue", "department"]}
    intent = {"required_columns": ["sales"]}
    plan = ["Calculate mean sales"]
    dataset_path = "sample_data/sample.csv"
    code = "import pandas as pd\ndf = pd.read_csv('sample.csv')\nprint(df['Sales'].mean())"
    error_msg = "KeyError: 'Sales'"

    repaired = llm_service.repair_code(
        user_query=user_query,
        dataset_profile=dataset_profile,
        intent=intent,
        plan=plan,
        dataset_path=dataset_path,
        code=code,
        error_msg=error_msg
    )

    assert "sales" in repaired.lower()
    assert "df['sales']" in repaired or 'df["sales"]' in repaired

def test_repair_type_error():
    user_query = "Sum total values"
    dataset_profile = {"columns": ["val1", "val2"]}
    intent = {"required_columns": ["val1", "val2"]}
    plan = ["Sum values"]
    dataset_path = "sample_data/sample.csv"
    code = "import pandas as pd\ndf = pd.read_csv('sample.csv')\nprint(df['val1'] + 'string')"
    error_msg = "TypeError: can only concatenate str (not 'int') to str"

    repaired = llm_service.repair_code(
        user_query=user_query,
        dataset_profile=dataset_profile,
        intent=intent,
        plan=plan,
        dataset_path=dataset_path,
        code=code,
        error_msg=error_msg
    )

    assert "TypeError" not in repaired
    assert "pd.read_csv" in repaired

def test_repair_missing_column():
    user_query = "Calculate profit"
    dataset_profile = {"columns": ["revenue", "expenses"]}
    intent = {"required_columns": ["revenue", "expenses"]}
    plan = ["Compute revenue minus expenses"]
    dataset_path = "sample_data/sample.csv"
    code = "import pandas as pd\ndf = pd.read_csv('sample.csv')\nprint(df['profit'].mean())"
    error_msg = "KeyError: 'profit'"

    repaired = llm_service.repair_code(
        user_query=user_query,
        dataset_profile=dataset_profile,
        intent=intent,
        plan=plan,
        dataset_path=dataset_path,
        code=code,
        error_msg=error_msg
    )

    assert "KeyError" not in repaired
    assert "pd.read_csv" in repaired

def test_repair_invalid_operation():
    user_query = "Analyze data"
    dataset_profile = {"columns": ["department", "salary"]}
    intent = {"required_columns": ["salary"]}
    plan = ["Summarize salary"]
    dataset_path = "sample_data/sample.csv"
    code = "import pandas as pd\ndf = pd.read_csv('sample.csv')\nprint(df['salary'].non_existent_method())"
    error_msg = "AttributeError: 'Series' object has no attribute 'non_existent_method'"

    repaired = llm_service.repair_code(
        user_query=user_query,
        dataset_profile=dataset_profile,
        intent=intent,
        plan=plan,
        dataset_path=dataset_path,
        code=code,
        error_msg=error_msg
    )

    assert "non_existent_method" not in repaired
    assert "pd.read_csv" in repaired

def test_repair_node_increments_retry_and_resets_validation():
    state: AgentState = {
        "user_query": "Test query",
        "dataset_profile": {"columns": ["sales"]},
        "intent": {},
        "analysis_plan": [],
        "dataset_path": "sample_data/sample.csv",
        "generated_code": "df['Sales'].mean()",
        "validated_code": "df['Sales'].mean()",
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 0,
        "status": "execution_failed"
    }

    res = repair_code_node(state)

    assert res["retry_count"] == 1
    assert res["validated_code"] is None  # MUST force re-validation!
    assert res["status"] == "code_repaired"
    assert res["generated_code"] is not None

def test_full_graph_execution_with_repair_loop():
    graph = get_analysis_graph()

    initial_state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "phase6_repair_test",
        "user_query": "Show monthly sales trends",
        "retry_count": 0,
        "status": "started"
    }

    final_state = graph.invoke(initial_state)

    assert final_state["status"] == "completed"
    assert final_state["execution_result"]["success"] is True
    assert final_state["retry_count"] <= 3
