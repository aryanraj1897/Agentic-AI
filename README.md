# Autonomous Data Analysis Agent

An end-to-end, LLM-powered multi-agent framework built with LangGraph, FastAPI, and React. The system autonomously transforms raw tabular datasets (CSV/Excel) into comprehensive analytical reports, statistical summaries, interactive visualizations, and data insights—all safely executed inside an isolated code execution environment with automatic AST security validation and self-healing error repair.

---

## Overview

The Autonomous Data Analysis Agent acts as an AI-powered data scientist. Users simply upload a dataset and ask a high-level question in plain natural language (e.g., *"Analyze sales trends and customer retention patterns across regions"*). The agent autonomously profiles the data, formulates an analysis plan, generates Python pandas/numpy scripts, validates code safety, executes in a secure sandbox, repairs errors if execution fails, creates visualizations, synthesizes statistical insights, and compiles an executive Markdown report.

---

## Problem Statement

Traditional data analysis requires extensive manual code authoring, data cleaning, chart creation, and interpretation. While basic LLM code generation can produce python snippets, raw execution carries severe risks:
1. **Security Vulnerabilities**: Arbitrary code execution can lead to system takeover, file destruction, or data exfiltration.
2. **Brittle Execution**: Code generated in a single prompt often fails due to unexpected column types, missing values, or API mismatches.
3. **Lack of End-to-End Automation**: Disconnected scripts require manual assembly into cohesive business reports.

The Autonomous Data Analysis Agent solves these challenges by combining static AST verification, isolated sandbox execution, autonomous state machine error recovery, and end-to-end report generation.

---

## Features

- 📊 **Automated Dataset Profiling**: Instant extraction of schemas, data types, missing value ratios, duplicate counts, and summary statistics.
- 🎯 **Natural Language Intent Recognition**: Maps user queries into analytical goals (e.g., trend analysis, distribution, correlation, aggregation).
- 🧠 **LangGraph Orchestration**: Stateful graph controlling execution flow, state persistence, and dynamic error branching.
- 🔒 **AST Code Security Validation**: Static Python AST analyzer blocking unauthorized calls (`os.system`, `eval`, `exec`, `subprocess`, socket operations).
- 🐳 **Isolated Sandbox Execution**: Runs generated Python scripts in restricted environments with 30-second timeouts and memory caps.
- 🛠️ **Autonomous Self-Healing Repair**: Catches execution failures and automatically regenerates corrected Python code with traceback feedback loops.
- 📈 **Smart Chart Generation**: Automatic selection of optimal chart types (line, bar, scatter, histogram, boxplot, heatmap) using `matplotlib` & `seaborn`.
- 📝 **Fact-Grounded Insights**: Synthesizes structured insights grounded strictly on computed data results (no hallucinated claims).
- 📑 **Comprehensive Markdown Reports**: Assembles complete executive reports with inline chart embeds, methodology details, and summary tables.
- 💾 **SQLite Persistence & History**: Track datasets, previous analyses, step logs, and generated artifacts across sessions.
- 🎨 **Modern React Dashboard**: Built with Vite and Tailwind CSS for interactive progress tracking, visualization previews, and report rendering.

---

## Architecture

The system uses a decoupled frontend/backend architecture with an embedded LangGraph state engine:

```
┌─────────────────────────────────────────────────────────────────────────┐
│                             React Frontend                              │
│             (Vite + Tailwind CSS + Interactive Dashboard)               │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │ HTTP / REST
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                            FastAPI Backend                              │
│           (Upload Manager, REST API, SQLite Storage Engine)            │
└────────────────延──────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                         LangGraph State Engine                          │
│             (Stateful Agent Nodes & Route Decision Matrix)              │
└────────────────────────────────────┬────────────────────────────────────┘
                                     │
                                     ▼
┌─────────────────────────────────────────────────────────────────────────┐
│                   Isolated Code Execution Sandbox                       │
│        (AST Security Validator + Docker/Restricted Process Sandbox)     │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## LangGraph Workflow

The workflow follows a state machine graph:

```
START ──> PROFILE ──> INTENT ──> PLANNER ──> CODE ──> VALIDATE ──> EXECUTE
                                                                     │
                                              ┌──────────────────────┴──────────────────────┐
                                              │                                             │
                                        Success Path                                   Error Path
                                              │                                             │
                                              ▼                                             ▼
                                        VISUALIZATION                                     REPAIR
                                              │                                             │
                                              ▼                                             │ (Retry < 3)
                                          INSIGHTS <────────────────────────────────────────┘ (Re-enters VALIDATE)
                                              │
                                              ▼
                                           REPORT ──> END
```

---

## Agent Architecture

| Node Name | Agent / Function | Purpose |
| :--- | :--- | :--- |
| **`PROFILE`** | Dataset Profiler | Extracts row/col metrics, column types, missing counts, and numerical stats. |
| **`INTENT`** | Intent Analyzer | Classifies query into target analytical domain. |
| **`PLANNER`** | Analysis Planner | Deconstructs analytical goal into actionable data processing steps. |
| **`CODE`** | Code Generator | Writes self-contained Python script using pandas, numpy, matplotlib, seaborn. |
| **`VALIDATE`** | Code Validator | Inspects AST tree to block disallowed packages and system calls. |
| **`EXECUTE`** | Sandbox Executor | Runs code safely under timeout and memory constraints. |
| **`REPAIR`** | Repair Agent | Autonomously fixes broken code using LLM traceback feedback. |
| **`VISUALIZATION`**| Visualization Agent | Selects chart types and renders PNG chart artifacts. |
| **`INSIGHTS`** | Insight Agent | Synthesizes numerical findings and data quality notes into facts. |
| **`REPORT`** | Report Agent | Compiles final Markdown report document. |

---

## Tech Stack

- **Backend**: Python 3.11, FastAPI, Uvicorn, SQLAlchemy, SQLite, Pydantic
- **AI & Orchestration**: LangGraph, LangChain, OpenAI GPT-4o
- **Data & Graphics**: Pandas, NumPy, Matplotlib, Seaborn, SciPy, Scikit-Learn
- **Frontend**: React 18, Vite, Tailwind CSS, Lucide React
- **DevOps & Containerization**: Docker, Docker Compose, Pytest

---

## Folder Structure

```
autonomous-data-analysis-agent/
├── backend/
│   ├── app/
│   │   ├── agents/          # LangGraph nodes (profiler, planner, validator, repair, etc.)
│   │   ├── api/             # FastAPI REST endpoints (datasets, analysis)
│   │   ├── core/            # Configuration & security settings
│   │   ├── db/              # SQLAlchemy models & repository layer
│   │   ├── services/        # LLM service, logger, & evaluation metrics engine
│   │   └── main.py          # FastAPI application entrypoint
│   ├── uploads/             # Storage for uploaded datasets
│   ├── generated/           # Storage for generated charts & reports
│   └── Dockerfile
├── frontend/
│   ├── src/                 # React components, state, & dashboard views
│   └── Dockerfile
├── sandbox/
│   ├── runner.py            # Isolated execution script
│   └── Dockerfile
├── docs/                    # Architecture, security, API, workflow, & deployment docs
├── tests/                   # Pytest test suite (unit, graph, e2e, security, evaluation)
├── docker-compose.yml
└── README.md
```

---

## Installation

### Prerequisites
- Python 3.11+
- Node.js 18+ & npm
- Docker Desktop (optional, for sandbox/compose)

### Clone & Install Dependencies

```bash
# Clone Repository
git clone https://github.com/user/autonomous-data-analysis-agent.git
cd autonomous-data-analysis-agent

# Setup Backend Virtual Environment
cd backend
python -m venv venv
# On Windows:
venv\Scripts\activate
# On Linux/macOS:
# source venv/bin/activate

pip install -r requirements.txt
cd ..

# Setup Frontend Dependencies
cd frontend
npm install
cd ..
```

---

## Environment Variables

Copy `.env.example` to `backend/.env` and update values:

```env
LLM_PROVIDER=openai
OPENAI_API_KEY=your_openai_api_key_here
MODEL_NAME=gpt-4o
MAX_FILE_SIZE_MB=50
EXECUTION_TIMEOUT=30
MAX_RETRIES=3
HOST=0.0.0.0
PORT=8000
CORS_ORIGINS=http://localhost:5173,http://127.0.0.1:5173,http://localhost:80,http://localhost
```

---

## Local Development

### Running Backend Service
```bash
cd backend
python -m uvicorn app.main:app --reload --port 8000
```

### Running Frontend Service
```bash
cd frontend
npm run dev
```
Open browser at `http://localhost:5173`.

---

## Docker

### Running via Docker Compose
```bash
docker-compose up -d --build
```
Access the application at `http://localhost`.

---

## API Documentation

Complete details available in [`docs/api.md`](file:///c:/Users/Aryan%20Raj/Agentic%20AI/autonomous-data-analysis-agent/docs/api.md).

Key Endpoints:
- `GET /api/health`: Operational check
- `POST /api/datasets/upload`: Upload dataset (`.csv`, `.xlsx`)
- `GET /api/datasets`: List uploaded datasets
- `POST /api/analysis`: Trigger autonomous analysis run
- `GET /api/analyses`: List historical analysis runs
- `GET /api/analyses/{id}`: Fetch complete analysis details, report, and charts

---

## Example Usage

### 1. Upload Dataset
```bash
curl -X POST "http://localhost:8000/api/datasets/upload" \
  -F "file=@sample_data/sales.csv"
```

### 2. Trigger Analysis
```bash
curl -X POST "http://localhost:8000/api/analysis" \
  -H "Content-Type: application/json" \
  -d '{
    "dataset_id": "YOUR_DATASET_ID",
    "user_query": "Identify top performing product categories and monthly revenue trends."
  }'
```

---

## Security

Detailed security specifications available in [`docs/security.md`](file:///c:/Users/Aryan%20Raj/Agentic%20AI/autonomous-data-analysis-agent/docs/security.md):
- **AST Code Inspection**: Rejects forbidden modules (`os`, `subprocess`, `sys`, `socket`) and unsafe calls (`eval`, `exec`).
- **Sandbox Isolation**: Unprivileged `sandboxuser`, 30-second execution timeout, and `--net=none` container networking.
- **Log Sanitization**: Masks API keys and sensitive tokens before writing logs.

---

## Testing

Run the full Pytest test suite covering unit tests, LangGraph routing, security checks, end-to-end scenarios, and system evaluation metrics:

```bash
cd backend
..\venv\Scripts\pytest ../tests -v
```

---

## Deployment

Refer to [`docs/deployment.md`](file:///c:/Users/Aryan%20Raj/Agentic%20AI/autonomous-data-analysis-agent/docs/deployment.md) for production deployment strategies across Docker Compose, AWS, GCP, or Kubernetes.

---

## Future Improvements

1. **Multi-File Dataset Joins**: Extend analytical capabilities to relational joins across multiple uploaded datasets.
2. **Interactive Chart Export**: Support dynamic Plotly/D3.js charts in addition to static PNG figures.
3. **Asynchronous Celery/Redis Queue**: Scale long-running analysis background workers for massive multi-gigabyte datasets.
4. **Enhanced Data Cleaning Pipeline**: Add user-in-the-loop interactive data cleaning and feature engineering prompts.
