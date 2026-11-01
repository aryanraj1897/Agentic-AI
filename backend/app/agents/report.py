from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def report_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Report Agent.
    Generates a structured executive Markdown report containing all Phase 7 required sections.
    """
    user_query = state.get("user_query", "")
    profile = state.get("dataset_profile") or {}
    intent = state.get("intent") or {}
    plan = state.get("analysis_plan") or []
    exec_res = state.get("execution_result") or {}
    exec_error = state.get("execution_error")
    retry_count = state.get("retry_count", 0)
    charts = state.get("charts") or []
    insights = state.get("insights") or []

    report_md = llm_service.generate_report(
        user_query=user_query,
        dataset_profile=profile,
        intent=intent,
        plan=plan,
        execution_result=exec_res,
        execution_error=exec_error,
        retry_count=retry_count,
        charts=charts,
        insights=insights
    )

    return {
        "report": report_md,
        "status": "completed"
    }
