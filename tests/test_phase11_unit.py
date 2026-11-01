import os
import sys
import pytest
import pandas as pd
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.data.loader import load_dataset
from app.data.profiler import generate_profile
from app.agents.intent import analyze_intent_node
from app.agents.planner import create_analysis_plan_node
from app.agents.code_generator import generate_code_node
from app.agents.validator import validate_code, validate_code_node
from app.agents.executor import execute_code_node
from app.agents.repair import repair_code_node
from app.agents.visualization import visualization_node
from app.agents.insights import insights_node
from app.agents.report import report_node
from app.agents.state import AgentState
from app.services.llm_service import llm_service

# 1. Dataset Loader Unit Test
def test_unit_dataset_loader():
    csv_bytes = b"category,sales\nElectronics,5000\nApparel,3000\n"
    df = load_dataset(csv_bytes, "test.csv")
    assert isinstance(df, pd.DataFrame)
    assert len(df) == 2
    assert "category" in df.columns

# 2. Dataset Profiler Unit Test
def test_unit_dataset_profiler():
    df = pd.DataFrame({"product": ["A", "B", "A"], "revenue": [100.0, 200.0, 150.0]})
    profile = generate_profile(df, "ds_unit_1", "sales.csv", 1024, "CSV", "2026-09-30T00:00:00")
    assert profile["rows"] == 3
    assert profile["columns"] == 2
    assert "revenue" in profile["numeric_columns"]

# 3. Intent Analyzer Unit Test
def test_unit_intent_analyzer():
    state: AgentState = {
        "user_query": "Find top 10 products by revenue",
        "dataset_profile": {"column_profiles": {"product": {}, "revenue": {}}}
    }
    res = analyze_intent_node(state)
    assert res["status"] == "intent_analyzed"
    assert "intent" in res
    assert "objective" in res["intent"]

# 4. Planner Unit Test
def test_unit_planner():
    state: AgentState = {
        "intent": {"objective": "Top products", "tasks": ["top_products"], "required_columns": ["revenue"]}
    }
    res = create_analysis_plan_node(state)
    assert res["status"] == "plan_created"
    assert "analysis_plan" in res
    assert len(res["analysis_plan"]) > 0

# 5. Code Generator Unit Test
def test_unit_code_generator():
    state: AgentState = {
        "user_query": "Calculate mean revenue",
        "dataset_profile": {"column_profiles": {"revenue": {"type": "float64"}}, "numeric_columns": ["revenue"]},
        "intent": {"required_columns": ["revenue"]},
        "analysis_plan": [{"step": 1, "action": "compute_mean"}],
        "dataset_path": "sample_data/sample.csv"
    }
    res = generate_code_node(state)
    assert res["status"] == "code_generated"
    assert "pd.read_csv" in res["generated_code"]

# 6. Validator Unit Test
def test_unit_validator():
    valid_code = "import pandas as pd\ndf = pd.read_csv('sample.csv')"
    res = validate_code(valid_code)
    assert res["valid"] is True

    invalid_code = "import os\nos.system('dir')"
    res_inv = validate_code(invalid_code)
    assert res_inv["valid"] is False

# 7. Executor Unit Test
def test_unit_executor():
    state: AgentState = {
        "validated_code": "import pandas as pd\nprint('Execution Unit Test OK')",
        "status": "code_validated"
    }
    res = execute_code_node(state)
    assert res["status"] in ["completed", "executed"]
    assert res["execution_result"]["success"] is True
    assert "Execution Unit Test OK" in res["execution_result"]["stdout"]

# 8. Repair Agent Unit Test
def test_unit_repair_agent():
    state: AgentState = {
        "user_query": "Fix key error",
        "dataset_profile": {"columns": ["sales"]},
        "generated_code": "print(df['Sales'])",
        "execution_error": "KeyError: 'Sales'",
        "retry_count": 0
    }
    res = repair_code_node(state)
    assert res["retry_count"] == 1
    assert res["validated_code"] is None  # Forces re-validation
    assert res["status"] == "code_repaired"

# 9. Visualization Agent Unit Test
def test_unit_visualization_agent():
    state: AgentState = {
        "intent": {"objective": "Time series sales trend", "tasks": ["monthly_trend"]},
        "dataset_profile": {"columns": ["date", "sales"], "numeric_columns": ["sales"], "categorical_columns": ["date"]},
        "execution_result": {"success": True, "stdout": "Done"}
    }
    res = visualization_node(state)
    assert res["status"] == "visualizations_generated"
    assert len(res["charts"]) > 0

# 10. Insights Agent Unit Test
def test_unit_insights_agent():
    state: AgentState = {
        "user_query": "Summary insights",
        "dataset_profile": {"columns": ["sales", "profit"], "rows": 50},
        "execution_result": {"success": True, "stdout": "Total Sales: $100,000"}
    }
    res = insights_node(state)
    assert res["status"] == "insights_generated"
    assert len(res["insights"]) > 0

# 11. Report Agent Unit Test
def test_unit_report_agent():
    state: AgentState = {
        "user_query": "Final report",
        "dataset_profile": {"filename": "unit.csv", "columns": ["sales"], "rows": 10},
        "intent": {"objective": "Final Summary"},
        "analysis_plan": [],
        "execution_result": {"success": True, "stdout": "All metrics calculated"},
        "charts": [],
        "insights": ["Unit test insight"]
    }
    res = report_node(state)
    assert res["status"] == "completed"
    assert "# Executive Summary" in res["report"]
