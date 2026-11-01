# LangGraph Agent Workflow Documentation

The Autonomous Data Analysis Agent utilizes a stateful LangGraph state machine to process analytical requests. This document explains every node, transition, and retry policy in the workflow.

```
                  ┌────────────────────────┐
                  │         START          │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │        PROFILE         │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │         INTENT         │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │        PLANNER         │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │          CODE          │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │        VALIDATE        │
                  └───────────┬────────────┘
                              │
                              ▼
                  ┌────────────────────────┐
                  │        EXECUTE         │
                  └───────────┬────────────┘
                              │
               ┌──────────────┴──────────────┐
               │                             │
         Success Path                   Error Path
               │                             │
               ▼                             ▼
   ┌───────────────────────┐     ┌───────────────────────┐
   │     VISUALIZATION     │     │        REPAIR         │
   └───────────┬───────────┘     └───────────┬───────────┘
               │                             │
               ▼                             │ (Retry Count < 3)
   ┌───────────────────────┐                 │
   │       INSIGHTS        │ <───────────────┘ (Re-enters VALIDATE -> EXECUTE)
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │        REPORT         │
   └───────────┬───────────┘
               │
               ▼
   ┌───────────────────────┐
   │          END          │
   └───────────────────────┘
```

---

## State Machine Nodes

### 1. `profile_dataset_node` (PROFILE)
- **Role**: Automatically extracts tabular metadata and dataset characteristics.
- **Inputs**: Dataset file path (`csv` / `xlsx`).
- **Outputs**: Column names, data types, row/column counts, missing value counts, duplicate count, and numerical summary stats.
- **State Updates**: `dataset_profile`.

### 2. `analyze_intent_node` (INTENT)
- **Role**: Interprets user query and determines the target analysis domain.
- **Inputs**: Natural language user query + `dataset_profile`.
- **Outputs**: Intent category (e.g. `trend_analysis`, `distribution`, `correlation`, `aggregation`, `group_comparison`).
- **State Updates**: `intent`.

### 3. `generate_plan_node` (PLANNER)
- **Role**: Deconstructs the intent into a multi-step execution strategy.
- **Inputs**: `user_query`, `intent`, `dataset_profile`.
- **Outputs**: List of analytical goals, filtering steps, aggregations, and plotting requirements.
- **State Updates**: `plan`.

### 4. `generate_code_node` (CODE)
- **Role**: Translates the plan into self-contained Python analysis script using `pandas`, `numpy`, `matplotlib`, and `seaborn`.
- **Inputs**: `user_query`, `dataset_profile`, `plan`.
- **Outputs**: Generated Python code string writing output figures to `backend/generated/charts/`.
- **State Updates**: `generated_code`.

### 5. `validate_code_node` (VALIDATE)
- **Role**: Performs static AST security inspection.
- **Checks**: Verifies allowed libraries (`pandas`, `numpy`, `matplotlib`, `seaborn`, `scipy`, `sklearn`) and flags unauthorized operations (`os`, `subprocess`, `eval`, `exec`, `socket`, `requests`, `urllib`).
- **Outputs**: `valid: bool`, `validation_errors: list`.
- **State Updates**: `validation_result`, `error`.

### 6. `execute_code_node` (EXECUTE)
- **Role**: Runs valid code within the sandbox environment under resource limits (30-second timeout).
- **Inputs**: `generated_code`, `dataset_path`.
- **Outputs**: Standard output, computed statistics, generated chart paths, or execution traceback error.
- **State Updates**: `execution_result`, `error`.

### 7. `repair_code_node` (REPAIR)
- **Role**: Autonomous error correction node triggered when code execution or validation fails.
- **Inputs**: `user_query`, `dataset_profile`, `generated_code`, `error`, `retry_count`.
- **Outputs**: Corrected Python script addressing runtime exception or syntax flaw. Increments `retry_count`.
- **State Updates**: `generated_code`, `retry_count`.

### 8. `generate_visualizations_node` (VISUALIZATION)
- **Role**: Inspects visual chart requirements, automatically chooses optimal chart types, and generates chart files if not created during code execution.
- **Inputs**: `dataset_profile`, `execution_result`, `plan`.
- **Outputs**: Chart file metadata and saved chart image paths.
- **State Updates**: `visualizations`.

### 9. `generate_insights_node` (INSIGHTS)
- **Role**: Generates analytical key findings grounded exclusively on computed execution statistics.
- **Inputs**: `user_query`, `dataset_profile`, `execution_result`, `visualizations`.
- **Outputs**: Fact-checked bullet points highlighting trends, outliers, distributions, and business conclusions.
- **State Updates**: `insights`.

### 10. `generate_report_node` (REPORT)
- **Role**: Compiles complete Markdown analysis report combining metadata, methodology, code, execution output, charts, and insights.
- **Inputs**: All state values (`dataset_profile`, `plan`, `generated_code`, `execution_result`, `visualizations`, `insights`).
- **Outputs**: Formatted Markdown document saved to `backend/generated/reports/`.
- **State Updates**: `final_report`.

---

## Routing Logic

### Execution Router (`route_after_execution`)
```python
if no error:
    return "visualization"
elif state.retry_count >= 3:
    return "report"  # Generate report documenting execution failure
else:
    return "repair"  # Route back to repair -> validate -> execute
```
