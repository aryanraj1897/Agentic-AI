import os
from typing import Dict, Any
from app.agents.state import AgentState
from app.services.llm_service import llm_service

def repair_code_node(state: AgentState) -> Dict[str, Any]:
    """
    LangGraph Node: Repairing broken or unsafe Python code using LLMService.
    Increments retry_count and returns corrected generated_code.
    """
    current_retry = state.get("retry_count", 0)
    new_retry_count = current_retry + 1

    user_query = state.get("user_query", "")
    profile = state.get("dataset_profile") or {}
    intent = state.get("intent") or {}
    plan = state.get("analysis_plan") or []
    dataset_path = state.get("dataset_path", "")
    broken_code = state.get("generated_code", "")
    error_msg = state.get("execution_error") or "Unknown error"

    repaired_code = llm_service.repair_code(
        user_query=user_query,
        dataset_profile=profile,
        intent=intent,
        plan=plan,
        dataset_path=dataset_path,
        code=broken_code,
        error_msg=error_msg
    )

    return {
        "generated_code": repaired_code,
        "validated_code": None,  # Force re-validation of repaired code
        "retry_count": new_retry_count,
        "status": "code_repaired"
    }
