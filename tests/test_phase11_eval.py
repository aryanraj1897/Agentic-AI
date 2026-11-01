import sys
import time
import pytest
from pathlib import Path

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.agents.graph import get_analysis_graph
from app.agents.state import AgentState
from app.services.evaluator import SystemEvaluator

def test_evaluation_metrics_benchmark_and_report_generation():
    eval_runner = SystemEvaluator()
    graph = get_analysis_graph()

    benchmark_runs = [
        {"dataset_path": "sample_data/sample.csv", "query": "Analyze employee departments and salaries"},
        {"dataset_path": "sample_data/sample.csv", "query": "Find highest salary department"},
        {"dataset_path": "sample_data/sample.csv", "query": "Show salary distribution summary"}
    ]

    for run_idx, run_info in enumerate(benchmark_runs):
        start_time = time.time()

        state: AgentState = {
            "dataset_path": run_info["dataset_path"],
            "dataset_id": f"eval_ds_{run_idx}",
            "user_query": run_info["query"],
            "retry_count": 0,
            "status": "started"
        }

        final_state = graph.invoke(state)
        duration = time.time() - start_time

        eval_runner.record_run(final_state, duration)

    metrics = eval_runner.generate_evaluation_report()

    # Assert evaluation metric thresholds
    assert metrics["total_runs"] == 3
    assert metrics["successful_analysis_rate"] >= 80.0
    assert metrics["code_execution_success_rate"] >= 80.0
    assert metrics["visualization_generation_success_rate"] >= 80.0
    assert metrics["report_generation_success_rate"] >= 80.0
    assert metrics["average_execution_time_seconds"] >= 0.0

    # Verify generated report files
    eval_json = Path(backend_dir.parent / "evaluation_report.json")
    docs_md = Path(backend_dir.parent / "docs" / "EVALUATION_REPORT.md")

    assert eval_json.exists()
    assert docs_md.exists()
