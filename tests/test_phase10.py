import sys
import pytest
from pathlib import Path
from fastapi.testclient import TestClient

# Add backend directory to sys.path
backend_dir = Path(__file__).resolve().parent.parent / "backend"
if str(backend_dir) not in sys.path:
    sys.path.insert(0, str(backend_dir))

from app.main import app
from app.agents.validator import validate_code, validate_code_node
from app.api.datasets import sanitize_filename, sanitize_id
from app.services.logger_service import sanitize_log_message

client = TestClient(app)

def test_malicious_python_code_rejection():
    malicious_scripts = [
        "import os\nos.system('rm -rf /')",
        "import subprocess\nsubprocess.run(['ls', '-la'])",
        "eval('1 + 1')",
        "exec('import sys')",
        "import socket\ns = socket.socket()",
        "import requests\nrequests.get('http://malicious.com')",
        "import urllib.request\nurllib.request.urlopen('http://malicious.com')",
        "import pathlib\np = pathlib.Path('/etc/passwd').read_text()",
        "open('/etc/passwd', 'r').read()",
        "open('../../secret.txt', 'r')",
        "__import__('os').system('whoami')"
    ]

    for script in malicious_scripts:
        res = validate_code(script)
        assert res["valid"] is False, f"Validator failed to block malicious code:\n{script}"
        assert len(res["errors"]) > 0

def test_oversized_file_upload_rejection():
    # Create 51 MB dummy payload (> 50 MB limit)
    oversized_data = b"a" * (51 * 1024 * 1024)
    files = {"file": ("huge.csv", oversized_data, "text/csv")}

    res = client.post("/api/datasets/upload", files=files)
    assert res.status_code == 413
    assert "exceeds maximum allowed limit" in res.json()["detail"]

def test_invalid_file_extension_rejection():
    files = {"file": ("malicious.exe", b"binary content", "application/octet-stream")}
    res = client.post("/api/datasets/upload", files=files)
    assert res.status_code == 400
    assert "Unsupported file format" in res.json()["detail"]

def test_path_traversal_filename_sanitization():
    unsafe_name = "../../etc/passwd"
    safe = sanitize_filename(unsafe_name)
    assert ".." not in safe
    assert "/" not in safe
    assert "\\" not in safe
    assert safe == "etc_passwd" or safe == "passwd"

def test_path_traversal_id_sanitization():
    with pytest.raises(Exception):
        sanitize_id("../../etc/passwd")

    with pytest.raises(Exception):
        sanitize_id("dataset_123/../../")

    clean = sanitize_id("dataset-123-abc_def")
    assert clean == "dataset-123-abc_def"

def test_dangerous_user_query_handling():
    long_query = "A" * 1500  # Exceeds 1000 char query limit
    res = client.post("/api/analysis/start", json={"dataset_id": "test_ds", "user_query": long_query})
    assert res.status_code == 400
    assert "exceeds maximum allowed length" in res.json()["detail"]

def test_api_secret_masking_in_logs():
    secret_text = "Failed call with OPENAI_API_KEY=sk-proj-1234567890abcdefghijklmnopqrstuvwxyz and Bearer eyJhbGciOiJIUzI1NiI1"
    clean_text = sanitize_log_message(secret_text)
    assert "sk-proj-1234567890abcdefghijklmnopqrstuvwxyz" not in clean_text
    assert "MASKED" in clean_text

def test_validator_node_state_security():
    state = {
        "generated_code": "import subprocess\nsubprocess.call(['whoami'])",
        "dataset_id": "phase10_sec_test",
        "retry_count": 0
    }
    node_res = validate_code_node(state)
    assert node_res["status"] == "validation_failed"
    assert node_res["validated_code"] is None
    assert "Security Validation Failed" in node_res["execution_error"]
