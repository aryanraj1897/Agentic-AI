import sys
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.validator import validate_code, validate_code_node
from app.agents.executor import execute_code_node
from app.agents.graph import get_analysis_graph
from app.agents.state import AgentState

def test_valid_pandas_code_validation():
    code = """
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

df = pd.read_csv("sample.csv")
print(df.describe())
plt.figure()
plt.savefig("chart.png")
"""
    res = validate_code(code)
    assert res["valid"] is True
    assert len(res["errors"]) == 0

def test_forbidden_os_system():
    code = """
import os
os.system("echo Hacked")
"""
    res = validate_code(code)
    assert res["valid"] is False
    assert any("os" in err or "system" in err for err in res["errors"])

def test_forbidden_subprocess():
    code = """
import subprocess
subprocess.run(["ls", "-la"])
"""
    res = validate_code(code)
    assert res["valid"] is False
    assert any("subprocess" in err for err in res["errors"])

def test_forbidden_eval():
    code = """
x = eval("1 + 1")
"""
    res = validate_code(code)
    assert res["valid"] is False
    assert any("eval" in err for err in res["errors"])

def test_forbidden_exec():
    code = """
exec("import sys")
"""
    res = validate_code(code)
    assert res["valid"] is False
    assert any("exec" in err for err in res["errors"])

def test_invalid_imports():
    code = """
import socket
import urllib.request
s = socket.socket()
"""
    res = validate_code(code)
    assert res["valid"] is False
    assert any("socket" in err or "urllib" in err for err in res["errors"])

def test_timeout_execution_handling():
    # Code with an infinite loop
    infinite_loop_code = """
import time
while True:
    time.sleep(0.1)
"""
    val_res = validate_code(infinite_loop_code)
    # Import 'time' is not in allowed list so validator blocks it
    assert val_res["valid"] is False

    # State with simulated timed out script
    state: AgentState = {
        "validated_code": "import pandas as pd\nwhile True:\n    pass",
        "status": "code_validated"
    }
    # Temporarily set EXECUTION_TIMEOUT to 2 seconds for fast test
    from app.config import settings
    original_timeout = settings.EXECUTION_TIMEOUT
    settings.EXECUTION_TIMEOUT = 2

    try:
        exec_res = execute_code_node(state)
        assert exec_res["status"] == "execution_failed"
        assert "timed out" in exec_res["execution_error"].lower()
    finally:
        settings.EXECUTION_TIMEOUT = original_timeout

def test_successful_analysis_execution():
    graph = get_analysis_graph()

    initial_state: AgentState = {
        "dataset_path": "sample_data/sample.csv",
        "dataset_id": "phase5_test_ds",
        "user_query": "Analyze employee salary distribution across departments",
        "retry_count": 0,
        "status": "started"
    }

    final_state = graph.invoke(initial_state)

    assert final_state["status"] == "completed"
    assert "execution_result" in final_state
    assert final_state["execution_result"]["success"] is True
    assert "Dataset Loaded" in final_state["execution_result"]["stdout"]
    assert len(final_state["charts"]) > 0 or "analysis_chart.png" in final_state["execution_result"]["charts"]
