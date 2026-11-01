import os
from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def generate_code_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Generating executable Python data analysis code using LLMService.
    """
    user_query = state.get("user_query", "")
    profile = state.get("dataset_profile") or {}
    intent = state.get("intent") or {}
    plan = state.get("analysis_plan") or []
    raw_path = state.get("dataset_path", "")
    dataset_path = os.path.abspath(raw_path) if raw_path else ""

    code = llm_service.generate_code(
        user_query=user_query,
        dataset_profile=profile,
        intent=intent,
        plan=plan,
        dataset_path=dataset_path
    )

    return {
        "dataset_path": dataset_path,
        "generated_code": code,
        "status": "code_generated"
    }
