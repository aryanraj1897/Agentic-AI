from typing import Dict, Any, List
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def insights_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Insight Agent.
    Generates data-backed findings, trends, comparisons, outliers, and limitations.
    Does not invent information or make unsupported causal claims.
    """
    user_query = state.get("user_query", "")
    profile = state.get("dataset_profile") or {}
    exec_res = state.get("execution_result") or {}
    charts = state.get("charts") or []

    insights_list = llm_service.generate_insights(
        user_query=user_query,
        dataset_profile=profile,
        execution_result=exec_res,
        charts=charts
    )

    return {
        "insights": insights_list,
        "status": "insights_generated"
    }
