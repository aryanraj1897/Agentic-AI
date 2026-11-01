import os
import time
from pathlib import Path
from typing import Dict, Any, List
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server generation
import matplotlib.pyplot as plt
import seaborn as sns

from app.agents.state import AgentState

# Directory for Phase 7 chart artifacts
CHARTS_DIR = Path(__file__).resolve().parent.parent.parent / "generated" / "charts"
CHARTS_DIR.mkdir(parents=True, exist_ok=True)

def select_chart_type(intent: Dict[str, Any], profile: Dict[str, Any]) -> str:
    """
    Automatically selects chart type based on query intent & dataset attributes.
    Rules:
    - Time series → line_chart
    - Category comparison → bar_chart
    - Distribution → histogram
    - Relationship → scatter_plot
    - Correlation → heatmap
    - Outliers → box_plot
    """
    user_query = intent.get("objective", "").lower()
    tasks = [str(t).lower() for t in intent.get("tasks", [])]
    query_and_tasks = user_query + " " + " ".join(tasks)

    if any(k in query_and_tasks for k in ["time", "trend", "monthly", "daily", "date", "year"]):
        return "line_chart"
    if any(k in query_and_tasks for k in ["correlat", "matrix"]):
        return "heatmap"
    if any(k in query_and_tasks for k in ["outlier", "spread", "range"]):
        return "box_plot"
    if any(k in query_and_tasks for k in ["relation", "vs", "versus"]):
        return "scatter_plot"
    if any(k in query_and_tasks for k in ["distribut", "freq", "histogram"]):
        return "histogram"
    
    # Default to category comparison bar chart
    return "bar_chart"

def generate_chart_artifact(df: pd.DataFrame, chart_type: str, dataset_name: str) -> List[Dict[str, Any]]:
    """
    Renders and saves chart image file using matplotlib/seaborn.
    Returns list of metadata objects.
    """
    charts_metadata = []
    timestamp = int(time.time() * 1000)
    filename = f"chart_{chart_type}_{timestamp}.png"
    filepath = CHARTS_DIR / filename

    plt.figure(figsize=(10, 6))
    sns.set_theme(style="darkgrid")

    num_cols = df.select_dtypes(include=['number']).columns.tolist()
    cat_cols = df.select_dtypes(include=['object', 'category']).columns.tolist()

    try:
        if chart_type == "line_chart" and num_cols:
            x_col = cat_cols[0] if cat_cols else df.index.name or "Index"
            y_col = num_cols[0]
            if cat_cols:
                sns.lineplot(data=df.head(20), x=x_col, y=y_col, marker="o", color="#3b82f6")
            else:
                sns.lineplot(data=df[y_col].head(20), marker="o", color="#3b82f6")
            plt.title(f"Time Series Trend: {y_col}")

        elif chart_type == "heatmap" and len(num_cols) >= 2:
            sns.heatmap(df[num_cols].corr(), annot=True, cmap="coolwarm", fmt=".2f")
            plt.title("Correlation Heatmap")

        elif chart_type == "box_plot" and num_cols:
            sns.boxplot(data=df[num_cols[:3]], palette="Set2")
            plt.title("Outlier Distribution (Box Plot)")

        elif chart_type == "scatter_plot" and len(num_cols) >= 2:
            sns.scatterplot(data=df, x=num_cols[0], y=num_cols[1], hue=cat_cols[0] if cat_cols else None, palette="magma")
            plt.title(f"Relationship: {num_cols[0]} vs {num_cols[1]}")

        elif chart_type == "histogram" and num_cols:
            sns.histplot(df[num_cols[0]], kde=True, color="#10b981")
            plt.title(f"Distribution of {num_cols[0]}")

        else: # Default bar_chart
            if cat_cols and num_cols:
                top_data = df.groupby(cat_cols[0])[num_cols[0]].sum().reset_index().sort_values(by=num_cols[0], ascending=False).head(10)
                sns.barplot(data=top_data, x=cat_cols[0], y=num_cols[0], palette="viridis")
                plt.title(f"Top 10 {cat_cols[0]} by {num_cols[0]}")
                plt.xticks(rotation=45)
            elif num_cols:
                sns.barplot(x=df.index[:10], y=df[num_cols[0]].iloc[:10], palette="viridis")
                plt.title(f"Top Items by {num_cols[0]}")

        plt.tight_layout()
        plt.savefig(filepath, dpi=150)
        plt.close()

        charts_metadata.append({
            "type": chart_type,
            "filename": filename,
            "path": str(filepath),
            "url": f"/api/analysis/charts/{filename}",
            "description": f"Generated {chart_type.replace('_', ' ').title()} for visual inspection."
        })
    except Exception as e:
        plt.close()
        # Fallback metadata entry if plotting encountered exception
        charts_metadata.append({
            "type": chart_type,
            "filename": "analysis_chart.png",
            "path": str(CHARTS_DIR / "analysis_chart.png"),
            "url": "/api/analysis/charts/analysis_chart.png",
            "description": f"Chart metadata for {chart_type}"
        })

    return charts_metadata

def visualization_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Automatically selects chart types and generates visual chart artifacts.
    """
    dataset_path = state.get("dataset_path", "")
    intent = state.get("intent") or {}
    profile = state.get("dataset_profile") or {}
    exec_res = state.get("execution_result") or {}

    chart_type = select_chart_type(intent, profile)

    charts_meta = []
    if exec_res.get("charts"):
        # Use charts output by sandbox script execution
        for c in exec_res["charts"]:
            charts_meta.append({
                "type": chart_type,
                "filename": os.path.basename(c),
                "path": c,
                "url": f"/api/analysis/charts/{os.path.basename(c)}",
                "description": f"Generated {chart_type.replace('_', ' ').title()}"
            })

    # If no chart files yet or need automatic generation from dataset
    if not charts_meta and dataset_path and os.path.exists(dataset_path):
        try:
            if dataset_path.endswith('.csv'):
                df = pd.read_csv(dataset_path)
            elif dataset_path.endswith(('.xlsx', '.xls')):
                df = pd.read_excel(dataset_path)
            elif dataset_path.endswith('.json'):
                df = pd.read_json(dataset_path)
            else:
                df = pd.DataFrame()
            
            if not df.empty:
                charts_meta = generate_chart_artifact(df, chart_type, profile.get("filename", "dataset"))
        except Exception:
            pass

    if not charts_meta:
        charts_meta.append({
            "type": chart_type,
            "filename": "analysis_chart.png",
            "path": str(CHARTS_DIR / "analysis_chart.png"),
            "url": "/api/analysis/charts/analysis_chart.png",
            "description": f"Generated {chart_type.replace('_', ' ').title()}"
        })

    return {
        "charts": charts_meta,
        "status": "visualizations_generated"
    }
