# Autonomous Data Analysis Agent - Architecture Overview

## System Flow Architecture

The Autonomous Data Analysis Agent follows a modern decoupled architecture separating the client interface, API gateway, orchestration engine, isolated code execution, and data storage.

```
┌─────────────────┐       HTTP / REST       ┌───────────────────────┐
│                 │ ──────────────────────> │                       │
│  React Frontend │                         │   FastAPI Backend     │
│  (Vite + Web UI)│ <────────────────────── │   (REST Endpoints)    │
└─────────────────┘                         └───────────┬───────────┘
                                                        │
                                                        ▼
                                            ┌───────────────────────┐
                                            │                       │
                                            │   LangGraph Workflow  │
                                            │  (State Orchestrator) │
                                            └───────────┬───────────┘
                                                        │
                    ┌───────────────────────────────────┼───────────────────────────────────┐
                    ▼                                   ▼                                   ▼
          ┌───────────────────┐               ┌───────────────────┐               ┌───────────────────┐
          │  Dataset Loader   │               │   Code Generator  │               │   Visualization   │
          │    & Profiler     │               │   & Validator     │               │     & Insights    │
          └───────────────────┘               └─────────┬─────────┘               └───────────────────┘
                                                        │
                                                        ▼
                                              ┌───────────────────┐
                                              │ Isolated Sandbox  │
                                              │ Execution Engine  │
                                              └───────────────────┘
```

## Detailed Component Lifecycle

### 1. User Interaction Layer
- The user interacts with the React single-page application built with Vite and Tailwind CSS.
- Users upload CSV/Excel files and submit analytical queries in plain natural language.
- Real-time updates poll backend endpoints to display active LangGraph execution steps, code logs, and visual progress.

### 2. FastAPI Backend & Database Layer
- FastAPI serves as the high-performance API gateway handling file uploads, validation, state management, and API persistence.
- SQLite + SQLAlchemy manages persistent relational records across datasets, analysis runs, step logs, and generated files.

### 3. LangGraph Orchestration State Machine
- LangGraph coordinates the lifecycle through an explicit state graph using `AgentState`.
- Each processing step represents a distinct node operating autonomously on state context:
  - `PROFILE`: Inspects dataset structure, column types, missing values, duplicates, and numerical distribution.
  - `INTENT`: Parses analytical goal and categorizes query type (e.g., aggregation, trend, distribution, correlation).
  - `PLANNER`: Formulates a step-by-step data analysis strategy.
  - `CODE`: Generates executable Python pandas/numpy analysis script.
  - `VALIDATE`: Performs AST security validation to block malicious calls (`os.system`, `eval`, `exec`, `subprocess`, socket operations).
  - `EXECUTE`: Executes code inside a restricted environment with timeout and memory constraints.
  - `REPAIR`: Triggers LLM self-healing if execution fails, analyzing traceback to fix errors.
  - `VISUALIZATION`: Automatically creates charts using matplotlib and seaborn.
  - `INSIGHTS`: Synthesizes numerical findings into factual, data-grounded text insights.
  - `REPORT`: Generates executive summary and structured Markdown report.

### 4. Restricted Sandbox Execution
- Python code execution takes place inside an isolated containerized environment (or restricted subprocess with timeouts).
- Network access is disabled, execution runtime is capped at 30 seconds, and filesystem access is scoped strictly to temporary workspace directories.

### 5. Results & Frontend Rendering
- Generated Markdown reports, metrics summary, and chart files are exposed via secure API routes.
- The React dashboard presents interactive charts, dataset overview cards, step timeline progress, and historical logs.
