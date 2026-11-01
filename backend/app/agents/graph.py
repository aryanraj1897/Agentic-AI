from langgraph.graph import StateGraph, START, END
from app.agents.state import AgentState
from app.agents.profiler import profile_dataset_node
from app.agents.intent import analyze_intent_node
from app.agents.planner import create_analysis_plan_node
from app.agents.code_generator import generate_code_node
from app.agents.validator import validate_code_node
from app.agents.executor import execute_code_node
from app.agents.repair import repair_code_node
from app.agents.visualization import visualization_node
from app.agents.insights import insights_node
from app.agents.report import report_node

def route_after_execution(state: AgentState) -> str:
    """
    Conditional router after code execution.
    - If execution succeeded with no error: route to 'visualization'.
    - If execution failed and retry_count < 3: route to 'repair'.
    - Otherwise (max retries 3 reached): route to 'report' (where report clearly states execution failed).
    """
    exec_res = state.get("execution_result") or {}
    exec_error = state.get("execution_error")
    retry_count = state.get("retry_count", 0)

    if not exec_error and exec_res.get("success", False) is True:
        return "visualization"

    if retry_count < 3:
        return "repair"

    return "report"

def build_analysis_graph():
    """
    Constructs and compiles the Phase 7 LangGraph state workflow graph:
    START -> PROFILE -> INTENT -> PLANNER -> CODE_GENERATOR -> VALIDATOR -> EXECUTOR
                                                                              │
                                                                    (Conditional Route)
                                                        ┌─────────────────────┴─────────────────────┐
                                                      SUCCESS                                    ERROR
                                                         │                                          │
                                                         ▼                                   (retry < 3 ? repair : report)
                                                   VISUALIZATION                                    │
                                                         │                                    ┌─────┴─────┐
                                                         ▼                                 REPAIR       REPORT
                                                      INSIGHTS                                │           │
                                                         │                                    ▼           ▼
                                                         ▼                                VALIDATOR      END
                                                      REPORT
                                                         │
                                                         ▼
                                                        END
    """
    workflow = StateGraph(AgentState)

    # 1. Add Nodes
    workflow.add_node("profile_dataset", profile_dataset_node)
    workflow.add_node("analyze_intent", analyze_intent_node)
    workflow.add_node("create_analysis_plan", create_analysis_plan_node)
    workflow.add_node("code_generator", generate_code_node)
    workflow.add_node("validator", validate_code_node)
    workflow.add_node("executor", execute_code_node)
    workflow.add_node("repair", repair_code_node)
    workflow.add_node("visualization", visualization_node)
    workflow.add_node("insights", insights_node)
    workflow.add_node("report", report_node)

    # 2. Add Linear Edges
    workflow.add_edge(START, "profile_dataset")
    workflow.add_edge("profile_dataset", "analyze_intent")
    workflow.add_edge("analyze_intent", "create_analysis_plan")
    workflow.add_edge("create_analysis_plan", "code_generator")
    workflow.add_edge("code_generator", "validator")
    workflow.add_edge("validator", "executor")

    # 3. Add Conditional Edge after execution
    workflow.add_conditional_edges(
        "executor",
        route_after_execution,
        {
            "visualization": "visualization",
            "repair": "repair",
            "report": "report"
        }
    )

    # 4. Repair loop back to validator
    workflow.add_edge("repair", "validator")

    # 5. Success Pipeline: VISUALIZATION -> INSIGHTS -> REPORT -> END
    workflow.add_edge("visualization", "insights")
    workflow.add_edge("insights", "report")
    workflow.add_edge("report", END)

    # Compile Graph
    return workflow.compile()

# Global compiled graph instance
_graph_instance = None

def get_analysis_graph():
    """
    Returns the compiled LangGraph workflow graph instance.
    """
    global _graph_instance
    if _graph_instance is None:
        _graph_instance = build_analysis_graph()
    return _graph_instance
