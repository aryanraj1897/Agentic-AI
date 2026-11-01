from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def analyze_intent_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Analyzing user intent using LLMService.
    """
    user_query = state.get("user_query", "")
    profile = state.get("dataset_profile") or {}

    intent = llm_service.analyze_intent(user_query, profile)

    return {
        "intent": intent,
        "status": "intent_analyzed"
    }
