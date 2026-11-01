import sys
import os
import json
import traceback
import subprocess
from pathlib import Path

def run_script(script_path: str, output_dir: str):
    script_path = Path(script_path).resolve()
    output_dir = Path(output_dir).resolve()
    output_dir.mkdir(parents=True, exist_ok=True)

    if not script_path.exists():
        print(json.dumps({
            "success": False,
            "stdout": "",
            "stderr": f"Script file '{script_path}' does not exist.",
            "results": {},
            "charts": []
        }))
        return

    # Change working directory to output_dir so charts are saved directly inside it
    current_cwd = os.getcwd()
    os.chdir(output_dir)

    stdout_capture = []
    stderr_capture = []
    success = False

    try:
        with open(script_path, "r", encoding="utf-8") as f:
            code_content = f.read()

        # Create global dictionary for execution
        exec_globals = {
            "__name__": "__main__",
            "__file__": str(script_path),
        }

        # Override sys.stdout / sys.stderr
        import io
        old_stdout = sys.stdout
        old_stderr = sys.stderr

        captured_stdout = io.StringIO()
        captured_stderr = io.StringIO()

        sys.stdout = captured_stdout
        sys.stderr = captured_stderr

        try:
            exec(code_content, exec_globals)
            success = True
        except Exception:
            captured_stderr.write(traceback.format_exc())
            success = False
        finally:
            sys.stdout = old_stdout
            sys.stderr = old_stderr

        stdout_str = captured_stdout.getvalue()
        stderr_str = captured_stderr.getvalue()

    finally:
        os.chdir(current_cwd)

    # Collect generated chart files (.png, .jpg, .svg)
    charts = []
    for ext in ["*.png", "*.jpg", "*.jpeg", "*.svg"]:
        for chart_file in output_dir.glob(ext):
            charts.append(str(chart_file.name))

    output = {
        "success": success,
        "stdout": stdout_str,
        "stderr": stderr_str,
        "results": {"execution_completed": success},
        "charts": sorted(charts)
    }

    print(json.dumps(output))

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(json.dumps({
            "success": False,
            "stdout": "",
            "stderr": "Usage: runner.py <script_path> <output_dir>",
            "results": {},
            "charts": []
        }))
        sys.exit(1)

    run_script(sys.argv[1], sys.argv[2])
