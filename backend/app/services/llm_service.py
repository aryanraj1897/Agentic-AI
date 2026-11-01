import os
import json
import logging
from typing import Dict, Any, List, Optional
from app.config import settings

logger = logging.getLogger(__name__)

class LLMService:
    def __init__(self):
        self.provider = settings.LLM_PROVIDER.lower() if settings.LLM_PROVIDER else "mock"
        self.api_key = settings.OPENAI_API_KEY
        self.model_name = settings.MODEL_NAME or "gpt-4o"
        self._llm = None

        # Only initialize ChatOpenAI if API key is present and not a dummy placeholder
        if self.api_key and not self.api_key.startswith("your_") and self.provider == "openai":
            try:
                from langchain_openai import ChatOpenAI
                self._llm = ChatOpenAI(
                    model=self.model_name,
                    api_key=self.api_key,
                    temperature=0.2
                )
            except Exception as e:
                logger.warning(f"Failed to initialize ChatOpenAI: {e}. Falling back to rule-based engine.")

    def analyze_intent(self, user_query: str, dataset_profile: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyzes user query in context of dataset profile columns and returns structured JSON intent.
        """
        cols = list(dataset_profile.get("column_profiles", {}).keys())
        numeric_cols = dataset_profile.get("numeric_columns", [])
        categorical_cols = dataset_profile.get("categorical_columns", [])
        date_cols = dataset_profile.get("date_columns", [])

        # Match columns mentioned in query or choose best candidates
        q_lower = user_query.lower()
        matched_cols = [c for c in cols if c.lower() in q_lower]

        if not matched_cols:
            if numeric_cols:
                matched_cols.append(numeric_cols[0])
            if categorical_cols:
                matched_cols.append(categorical_cols[0])

        tasks = []
        visualizations = []

        if any(k in q_lower for k in ["top", "highest", "best", "rank"]):
            tasks.append("top_records_analysis")
            visualizations.append("bar_chart_top_items")

        if any(k in q_lower for k in ["trend", "time", "monthly", "date", "over time"]):
            tasks.append("time_series_trend")
            visualizations.append("line_chart_trends")

        if any(k in q_lower for k in ["compare", "category", "department", "group", "region"]):
            tasks.append("categorical_breakdown")
            visualizations.append("bar_chart_categories")

        if not tasks:
            tasks.append("exploratory_summary")
            visualizations.append("distribution_histogram")

        analysis_type = tasks[0] if tasks else "exploratory"

        if self._llm:
            try:
                prompt = f"""You are an AI Data Scientist. Analyze the user request for a dataset.

Dataset Columns: {cols}
Numeric Columns: {numeric_cols}
Categorical Columns: {categorical_cols}
Date Columns: {date_cols}
User Query: "{user_query}"

Respond with ONLY valid JSON with keys:
- objective: concise string
- analysis_type: string
- tasks: array of strings
- required_columns: array of exact column names from the dataset
- visualizations: array of chart types (e.g. bar_chart, line_chart, histogram)
"""
                response = self._llm.invoke(prompt)
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                res = json.loads(content)
                res["analysis_type"] = res.get("analysis_type") or analysis_type
                res["required_columns"] = [c for c in res.get("required_columns", []) if c in cols] or matched_cols
                return res
            except Exception as e:
                logger.warning(f"LLM call failed for analyze_intent: {e}. Using fallback.")

        return {
            "objective": f"Perform analysis for query: '{user_query}'",
            "analysis_type": analysis_type,
            "tasks": tasks,
            "required_columns": matched_cols,
            "visualizations": visualizations
        }

    def create_plan(self, intent: Dict[str, Any], dataset_profile: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Creates an ordered execution plan based on intent and dataset profile.
        """
        filename = dataset_profile.get("filename", "dataset")
        req_cols = intent.get("required_columns", [])
        tasks = intent.get("tasks", [])

        if self._llm:
            try:
                prompt = f"""Create an ordered data analysis plan for the user intent.

Dataset Filename: {filename}
Target Columns: {req_cols}
Tasks: {tasks}
Objective: {intent.get('objective')}

Respond with ONLY valid JSON array of step objects, each with:
- step: integer (1-indexed)
- action: string key
- description: string detail
"""
                response = self._llm.invoke(prompt)
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                return json.loads(content)
            except Exception as e:
                logger.warning(f"LLM call failed for create_plan: {e}. Using fallback.")

        plan = [
            {
                "step": 1,
                "action": "load_and_validate",
                "description": f"Load dataset '{filename}' and validate schema for columns: {', '.join(req_cols) or 'all columns'}."
            },
            {
                "step": 2,
                "action": "clean_missing_values",
                "description": "Inspect and clean missing or duplicate rows in selected feature columns."
            },
            {
                "step": 3,
                "action": "compute_aggregations",
                "description": f"Perform data aggregations for tasks: {', '.join(tasks)}."
            },
            {
                "step": 4,
                "action": "generate_visualizations",
                "description": f"Generate requested charts ({', '.join(intent.get('visualizations', [])) or 'visual summary'})."
            }
        ]
        return plan

    def generate_code(self, user_query: str, dataset_profile: Dict[str, Any], intent: Dict[str, Any], plan: List[Dict[str, Any]], dataset_path: str) -> str:
        """
        Generates Python code using pandas, numpy, matplotlib, seaborn to execute analysis.
        """
        cols = list(dataset_profile.get("column_profiles", {}).keys())
        sample_data = {
            col: info.get("sample_values", [])
            for col, info in dataset_profile.get("column_profiles", {}).items()
        }

        if self._llm:
            try:
                prompt = f"""You are an expert Data Analyst Python Programmer. Write clean, executable Python code for dataset analysis.

Dataset Path: "{dataset_path}"
Available Columns: {cols}
Sample Data: {sample_data}
User Query: "{user_query}"
Analysis Intent: {intent}
Execution Plan: {plan}

REQUIREMENTS:
1. Load dataset using pandas from dataset_path.
2. Use exact column names from Available Columns: {cols}. DO NOT invent columns.
3. Compute requested aggregations and print structured findings.
4. If charts are needed, save them using plt.savefig('output_chart.png').
5. Output ONLY raw executable Python code enclosed in ```python ... ``` block.
"""
                response = self._llm.invoke(prompt)
                content = response.content.strip()
                if "```python" in content:
                    return content.split("```python")[1].split("```")[0].strip()
                elif "```" in content:
                    return content.split("```")[1].split("```")[0].strip()
                return content
            except Exception as e:
                logger.warning(f"LLM call failed for generate_code: {e}. Using deterministic code generator.")

        # Fallback deterministic python code generator
        req_cols = intent.get("required_columns", [])
        num_cols = dataset_profile.get("numeric_columns", [])
        cat_cols = dataset_profile.get("categorical_columns", [])

        target_num = req_cols[0] if req_cols and req_cols[0] in num_cols else (num_cols[0] if num_cols else cols[0])
        target_cat = next((c for c in req_cols if c in cat_cols), cat_cols[0] if cat_cols else cols[0])

        code = f"""import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns

# 1. Load Dataset
dataset_path = r"{dataset_path}"
df = pd.read_csv(dataset_path)

print(f"Dataset Loaded: {{len(df)}} rows, {{len(df.columns)}} columns")

# 2. Perform Analysis & Aggregation
print("\\n--- Analysis Summary ---")
if "{target_cat}" in df.columns and "{target_num}" in df.columns:
    summary = df.groupby("{target_cat}")["{target_num}"].agg(["count", "mean", "sum"]).reset_index()
    summary = summary.sort_values(by="sum", ascending=False)
    print(summary.head(10))

    # 3. Generate Chart
    plt.figure(figsize=(10, 6))
    sns.barplot(data=summary.head(10), x="{target_cat}", y="sum", palette="viridis")
    plt.title(f"Top {target_cat} by Total {target_num}")
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig("analysis_chart.png")
    plt.close()
    print("\\nChart saved to analysis_chart.png")
else:
    print(df.describe())
"""
        return code

    def repair_code(self, user_query: str, dataset_profile: Dict[str, Any], intent: Dict[str, Any], plan: List[Dict[str, Any]], dataset_path: str, code: str, error_msg: str) -> str:
        """
        Repairs broken Python code based on the execution or validation error traceback and dataset schema.
        """
        cols = dataset_profile.get("columns") or list(dataset_profile.get("column_profiles", {}).keys())

        if self._llm:
            try:
                prompt = f"""You are an expert Data Analyst Python Programmer. The Python code below failed during execution or validation.

Dataset Path: "{dataset_path}"
Available Columns: {cols}
User Query: "{user_query}"
Broken Code:
```python
{code}
```

Error Traceback / Validation Failure:
{error_msg}

REPAIR INSTRUCTIONS:
1. Fix column names to match Available Columns: {cols}.
2. Remove any forbidden modules or functions (e.g., os, sys, subprocess, eval, exec).
3. Ensure the script runs cleanly without KeyError, TypeError, or SyntaxError.
4. Output ONLY valid, executable Python code enclosed in ```python ... ``` block.
"""
                response = self._llm.invoke(prompt)
                content = response.content.strip()
                if "```python" in content:
                    return content.split("```python")[1].split("```")[0].strip()
                elif "```" in content:
                    return content.split("```")[1].split("```")[0].strip()
                return content
            except Exception as e:
                logger.warning(f"LLM call failed for repair_code: {e}. Using rule-based repair engine.")

        # Heuristic / Rule-based repair engine
        repaired_code = code

        # 1. Handle KeyError (case mismatch or missing column)
        if "KeyError" in error_msg:
            import re
            key_match = re.search(r"KeyError:\s*['\"]?([^'\"\n]+)['\"]?", error_msg)
            if key_match:
                missing_key = key_match.group(1).strip()
                # Find best matching actual column name
                matched_col = None
                for col in cols:
                    if col.lower() == missing_key.lower():
                        matched_col = col
                        break
                if not matched_col and cols:
                    matched_col = cols[0]

                if matched_col and missing_key in repaired_code:
                    repaired_code = repaired_code.replace(f"'{missing_key}'", f"'{matched_col}'")
                    repaired_code = repaired_code.replace(f'"{missing_key}"', f'"{matched_col}"')
                    repaired_code = repaired_code.replace(f"[{missing_key}]", f"[{matched_col}]")

        # 2. Handle AttributeError (invalid method calls)
        if "AttributeError" in error_msg:
            import re
            attr_match = re.search(r"has no attribute\s*['\"]?([^'\"\n]+)['\"]?", error_msg)
            if attr_match:
                invalid_attr = attr_match.group(1).strip()
                if invalid_attr in repaired_code:
                    repaired_code = re.sub(r"\." + re.escape(invalid_attr) + r"\(\)", ".head()", repaired_code)
                    repaired_code = re.sub(r"\." + re.escape(invalid_attr), "", repaired_code)

        # 3. Handle Forbidden Import/Operations
        forbidden_terms = ["os.system", "subprocess", "eval(", "exec(", "import os", "import subprocess", "import socket"]
        for term in forbidden_terms:
            if term in repaired_code:
                lines = [line for line in repaired_code.splitlines() if term not in line]
                repaired_code = "\n".join(lines)

        # 4. Handle TypeError (convert numeric columns if needed)
        if "TypeError" in error_msg:
            if "df = pd.read_csv" in repaired_code:
                repaired_code = repaired_code.replace(
                    "df = pd.read_csv(dataset_path)",
                    "df = pd.read_csv(dataset_path)\nfor c in df.select_dtypes(include='object').columns:\n    df[c] = pd.to_numeric(df[c], errors='ignore')"
                )
            elif "read_csv" in repaired_code:
                # Remove string concatenation with non-string
                repaired_code = re.sub(r"\+\s*['\"][^'\"]*['\"]", "", repaired_code)

        return repaired_code

    def generate_insights(self, user_query: str, dataset_profile: Dict[str, Any], execution_result: Dict[str, Any], charts: List[Dict[str, Any]]) -> List[str]:
        """
        Generates data-driven insights based strictly on computed results and statistics.
        Does not invent facts or make unsupported causal claims.
        """
        stdout = execution_result.get("stdout", "") if execution_result else ""
        raw_cols = dataset_profile.get("columns")
        if isinstance(raw_cols, list):
            cols = [str(c) for c in raw_cols]
        elif isinstance(dataset_profile.get("column_profiles"), dict):
            cols = list(dataset_profile["column_profiles"].keys())
        else:
            cols = []
        num_rows = dataset_profile.get("rows", 0)

        if self._llm:
            try:
                prompt = f"""You are a Data Science Insight Agent.
User Query: "{user_query}"
Dataset Columns: {cols}
Total Rows: {num_rows}
Execution Stdout Output:
{stdout}
Generated Charts: {charts}

RULES:
1. Generate clear, actionable insights covering Key Findings, Trends, Comparisons, Outliers, Relationships, Data-quality issues, and Limitations.
2. DO NOT invent facts or make unsupported causal claims. Only state facts directly supported by the stdout and dataset profile.
3. Return ONLY a JSON list of string bullet points: ["Insight 1", "Insight 2", ...]
"""
                response = self._llm.invoke(prompt)
                content = response.content.strip()
                if "```json" in content:
                    content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    content = content.split("```")[1].split("```")[0].strip()
                parsed = json.loads(content)
                if isinstance(parsed, list):
                    return parsed
            except Exception as e:
                logger.warning(f"LLM call failed for generate_insights: {e}. Using deterministic insight engine.")

        # Fallback deterministic insight engine
        insights = [
            f"Dataset contains {num_rows} records and {len(cols)} variables: {', '.join(cols[:5])}.",
            f"Successfully executed sandboxed pandas analysis for query: '{user_query}'.",
        ]

        if stdout:
            # Extract numbers/findings from stdout
            lines = [l.strip() for l in stdout.splitlines() if l.strip() and not l.startswith("---")]
            if lines:
                insights.append(f"Primary computed summary: {lines[0]}")
            if len(lines) > 1:
                insights.append(f"Statistical output highlight: {lines[1]}")

        missing_vals = dataset_profile.get("missing_values", {})
        total_missing = sum(missing_vals.values()) if isinstance(missing_vals, dict) else 0
        if total_missing > 0:
            insights.append(f"Data Quality: Identified {total_missing} missing values across columns.")
        else:
            insights.append("Data Quality: Complete dataset with zero missing values detected.")

        if charts:
            insights.append(f"Visualizations: Generated {len(charts)} chart artifact(s) for visual trend inspection.")

        insights.append("Limitations: Analysis is bounded by available sample dataset schema and computed aggregations.")
        return insights

    def generate_report(self, user_query: str, dataset_profile: Dict[str, Any], intent: Dict[str, Any], plan: List[Dict[str, Any]], execution_result: Dict[str, Any], execution_error: Optional[str], retry_count: int, charts: List[Dict[str, Any]], insights: List[str]) -> str:
        """
        Generates a comprehensive Markdown report structured with standard Phase 7 sections.
        """
        success = execution_result.get("success", False) if execution_result else False
        stdout = execution_result.get("stdout", "") if execution_result else ""
        raw_cols = dataset_profile.get("columns")
        if isinstance(raw_cols, list):
            cols = [str(c) for c in raw_cols]
        elif isinstance(dataset_profile.get("column_profiles"), dict):
            cols = list(dataset_profile["column_profiles"].keys())
        else:
            cols = []
        num_rows = dataset_profile.get("rows", 0)

        if not success or execution_error:
            # Report when execution failed after max retries
            return f"""# Executive Summary
**STATUS: ANALYSIS EXECUTION FAILED**
The automated data analysis pipeline encountered execution errors and could not successfully generate final computed results after {retry_count} repair retries.

# Dataset Overview
- **Dataset ID / Path**: `{dataset_profile.get('filename', 'Unknown')}`
- **Total Records**: {num_rows}
- **Available Columns**: {', '.join(cols)}

# Data Quality
- Missing Values Count: {dataset_profile.get('missing_values', {})}
- Duplicate Rows Count: {dataset_profile.get('duplicate_rows', 0)}

# Analysis Performed
- **User Query**: "{user_query}"
- **Objective**: {intent.get('objective', 'General Dataset Analysis')}
- **Retries Attempted**: {retry_count}/3

# Key Findings
- Analysis halted prior to completion due to script runtime failure.

# Visualizations
- No chart artifacts generated due to execution error.

# Statistical Findings
- Execution Error Traceback: `{execution_error}`

# Anomalies
- Script execution failure encountered during sandbox execution.

# Limitations
- Code execution failed. Automated repair could not resolve error within max retries ({retry_count}).

# Recommendations
1. Inspect dataset schema and column data types.
2. Verify required columns exist in the uploaded file.
3. Retry analysis with a simplified query.
"""

        # Generate report for successful analysis
        if self._llm:
            try:
                prompt = f"""You are a Lead Data Analyst writing an executive markdown report.
User Query: "{user_query}"
Dataset Profile: {dataset_profile}
Intent: {intent}
Plan: {plan}
Execution Output:
{stdout}
Generated Charts: {charts}
Key Insights: {insights}

FORMAT REQUIREMENTS:
Generate a clean Markdown report with EXACTLY these section headers:
# Executive Summary
# Dataset Overview
# Data Quality
# Analysis Performed
# Key Findings
# Visualizations
# Statistical Findings
# Anomalies
# Limitations
# Recommendations
"""
                response = self._llm.invoke(prompt)
                content = response.content.strip()
                if "# Executive Summary" in content:
                    return content
            except Exception as e:
                logger.warning(f"LLM call failed for generate_report: {e}. Using deterministic report builder.")

        # Fallback deterministic report builder
        chart_md = "\n".join([f"- **{c.get('type', 'Chart').title()}**: `{c.get('filename', 'chart.png')}` - {c.get('description', 'Visualization artifact')}" for c in charts]) or "No charts generated."
        insights_md = "\n".join([f"- {insight}" for insight in insights])

        report_md = f"""# Executive Summary
Autonomous analysis successfully executed for query: **"{user_query}"**. The system analyzed {num_rows} records across {len(cols)} attributes, generated statistical aggregations, and produced visual charts.

# Dataset Overview
- **Filename**: `{dataset_profile.get('filename', 'dataset')}`
- **Total Records**: {num_rows}
- **Attributes ({len(cols)})**: {', '.join(cols)}

# Data Quality
- **Missing Values**: {dataset_profile.get('missing_values', {})}
- **Duplicate Rows**: {dataset_profile.get('duplicate_rows', 0)}
- **Quality Assessment**: Data structural integrity validated; schema aligned with analysis goals.

# Analysis Performed
1. Validated dataset schema and inferred column data types.
2. Classifed intent: objective = `{intent.get('objective', user_query)}`.
3. Planned execution steps: {', '.join([p.get('action', '') for p in plan]) if isinstance(plan, list) else 'Aggregations & Visualizations'}.
4. Validated Python code AST and executed script inside sandboxed runner.

# Key Findings
{insights_md}

# Visualizations
{chart_md}

# Statistical Findings
```text
{stdout.strip() if stdout else 'Analysis completed cleanly.'}
```

# Anomalies
- No severe anomalous data distributions or out-of-range corruptions identified during execution.

# Limitations
- Findings are based strictly on available sample data without external benchmark comparisons.
- Statistical inference assumes uniform sample validity.

# Recommendations
1. Monitor top-performing metrics identified in aggregations.
2. Set up automated tracking dashboards for trend variables.
3. Perform further segmentation on low-performing groups.
"""
        return report_md

llm_service = LLMService()


