from typing import TypedDict, Optional, List, Dict, Any

class AgentState(TypedDict, total=False):
    dataset_path: str
    dataset_id: str
    dataset_profile: Optional[Dict[str, Any]]
    user_query: str
    intent: Optional[Dict[str, Any]]
    analysis_plan: Optional[List[Dict[str, Any]]]
    generated_code: Optional[str]
    validated_code: Optional[str]
    execution_result: Optional[Dict[str, Any]]
    execution_error: Optional[str]
    retry_count: int
    charts: Optional[List[Dict[str, Any]]]
    insights: Optional[List[str]]
    report: Optional[str]
    status: str
    messages: Optional[List[Dict[str, Any]]]
