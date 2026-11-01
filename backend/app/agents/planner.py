from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def create_analysis_plan_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Creating a structured analysis plan using LLMService.
    """
    intent = state.get("intent") or {}
    profile = state.get("dataset_profile") or {}

    plan = llm_service.create_plan(intent, profile)

    return {
        "analysis_plan": plan,
        "status": "plan_created"
    }
