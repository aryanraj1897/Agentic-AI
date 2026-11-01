# Security Architecture & Policies

Security is a primary design objective of the Autonomous Data Analysis Agent. Because the system autonomously generates and executes Python code based on user inputs, multiple layered defenses are built into the workflow to prevent unauthorized system access, code injection, resource exhaustion, or data leakage.

```
User Input ──> API Validation ──> AST Code Security Check ──> Restricted Sandbox Execution ──> Output Sanitization
```

---

## 1. Abstract Syntax Tree (AST) Validation

Before any generated Python script is permitted to execute, it passes through static AST security auditing (`backend/app/agents/validator.py`).

### Blocked Operations & Imports
- **Shell & OS Commands**: `os.system`, `subprocess`, `popen`, `shutil.rmtree`, `platform`
- **Dynamic Code Execution**: `eval`, `exec`, `compile`, `__import__`, `globals()`, `locals()`
- **Network Access**: `socket`, `requests`, `urllib`, `http.client`, `aiohttp`, `ftplib`
- **Arbitrary Filesystem Access**: `open()` outside allowed target dataset path, `pathlib.Path` directory traversal (`..`)

### Whitelisted Data Science Libraries
- `pandas`
- `numpy`
- `matplotlib`
- `seaborn`
- `scipy`
- `sklearn`

If AST validation detects un-whitelisted modules or dangerous nodes, execution is immediately aborted, `valid` is set to `False`, and error feedback is returned to the self-healing repair agent.

---

## 2. Containerized Sandbox Execution

Execution occurs inside an isolated environment separated from the FastAPI backend service.

### Docker Sandbox Guarantees
- **Non-Root User**: Code runs under unprivileged `sandboxuser` (`UID 1000`).
- **Read-Only Root Filesystem**: The base image is mounted read-only; output write operations are confined strictly to `/tmp` or designated output directories.
- **Ephemeral Container Lifetime**: Each execution takes place in a fresh ephemeral container instance destroyed upon exit.

---

## 3. Network Isolation

- **Zero Outbound Connectivity**: Sandbox containers run with `--net=none` to prevent data exfiltration, socket connections, or external API calls.
- **No Inbound Open Ports**: The sandbox environment exposes no listening ports.

---

## 4. Resource Limits & Hard Caps

To mitigate Denial-of-Service (DoS) vectors and CPU/memory exhaustion:
- **Execution Timeout**: Capped at `EXECUTION_TIMEOUT` (default: 30 seconds). Subprocesses/containers exceeding timeout are forcibly terminated with `SIGKILL`.
- **Memory Limit**: Docker containers are constrained to `512MB` maximum RAM usage.
- **CPU Limits**: CPU usage is capped at `1.0` core equivalent per execution.
- **File Upload Limits**: Dataset file uploads enforce `MAX_FILE_SIZE_MB` (default: 50 MB) and restrict extensions strictly to `.csv`, `.xlsx`, and `.xls`.

---

## 5. Retry System & Bounded Healing Loop

- Code repair attempts are constrained by `MAX_RETRIES` (default: 3).
- Every repaired code iteration must re-pass AST validation before re-execution.
- If maximum retries are exceeded, the state machine gracefully terminates execution and generates a report detailing the exact failure cause.

---

## 6. Log Sanitization & Sensitive Data Redaction

- Loggers automatically strip API keys (`sk-...`, `AIzaSy...`, `Bearer ...`) from tracebacks, step state logs, and error messages before writing logs to stdout or disk (`backend/app/services/logger_service.py`).
