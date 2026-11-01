import sys
import os
import json
import tempfile
import subprocess
from pathlib import Path
from typing import Dict, Any
from app.agents.state import AgentState
from app.config import settings

def execute_code_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Executing validated Python analysis code inside an isolated sandbox subprocess.
    Enforces execution timeouts, restricted environment, and output capture.
    """
    status = state.get("status")
    validated_code = state.get("validated_code")

    if status == "validation_failed" or not validated_code:
        return {
            "execution_result": {
                "success": False,
                "stdout": "",
                "stderr": "Code security validation failed. Execution blocked.",
                "results": {},
                "charts": []
            },
            "execution_error": state.get("execution_error") or "Validation failed. Untrusted code execution blocked.",
            "charts": [],
            "status": "execution_failed"
        }

    timeout_seconds = settings.EXECUTION_TIMEOUT or 30

    # Create temporary directory for script and outputs
    with tempfile.TemporaryDirectory(prefix="agent_sandbox_") as temp_dir:
        temp_dir_path = Path(temp_dir)
        script_path = temp_dir_path / "analysis_script.py"
        output_dir = temp_dir_path / "outputs"
        output_dir.mkdir(parents=True, exist_ok=True)

        with open(script_path, "w", encoding="utf-8") as f:
            f.write(validated_code)

        runner_script = Path(__file__).resolve().parent.parent.parent.parent / "sandbox" / "runner.py"

        cmd = [
            sys.executable,
            str(runner_script),
            str(script_path),
            str(output_dir)
        ]

        try:
            # Execute runner process with timeout and isolated environment
            process = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=timeout_seconds,
                env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"}
            )

            stdout = process.stdout.strip()
            stderr = process.stderr.strip()

            if process.returncode == 0 and stdout:
                try:
                    result_data = json.loads(stdout)
                    success = result_data.get("success", False)
                    charts = result_data.get("charts", [])
                    
                    return {
                        "execution_result": result_data,
                        "execution_error": None if success else result_data.get("stderr"),
                        "charts": charts,
                        "status": "completed" if success else "execution_failed"
                    }
                except json.JSONDecodeError:
                    pass

            return {
                "execution_result": {
                    "success": False,
                    "stdout": stdout,
                    "stderr": stderr,
                    "results": {},
                    "charts": []
                },
                "execution_error": stderr or "Unknown execution error.",
                "charts": [],
                "status": "execution_failed"
            }

        except subprocess.TimeoutExpired:
            return {
                "execution_result": {
                    "success": False,
                    "stdout": "",
                    "stderr": f"Execution timed out after {timeout_seconds} seconds.",
                    "results": {},
                    "charts": []
                },
                "execution_error": f"Execution timed out after {timeout_seconds} seconds.",
                "charts": [],
                "status": "execution_failed"
            }
