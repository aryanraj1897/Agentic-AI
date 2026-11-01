import uuid
from datetime import datetime
from pathlib import Path
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.responses import FileResponse
from pydantic import BaseModel, Field
from typing import Optional, Dict, Any, List

from app.agents.graph import get_analysis_graph
from app.agents.state import AgentState
from app.data.store import dataset_store, UPLOAD_DIR
from app.agents.visualization import CHARTS_DIR
from app.db.database import SessionLocal
from app.db.repository import (
    create_analysis_db,
    update_analysis_db,
    add_analysis_step_db,
    add_generated_file_db,
    get_analysis_db,
    list_analyses_db,
    delete_analysis_db,
    get_dataset_db
)

# APIRouter registered for both /api/analysis and /api/analyses
router = APIRouter(tags=["Analysis"])

# Dual in-memory backup cache
analysis_store: Dict[str, Dict[str, Any]] = {}

class StartAnalysisRequest(BaseModel):
    dataset_id: str = Field(..., description="ID of the uploaded dataset")
    user_query: str = Field(..., description="User query describing analysis goal")
    analysis_id: Optional[str] = Field(None, description="Optional custom analysis ID")

def get_db_session():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------------------------------------
# 1. Start Analysis Workflow & Record Persistence
# ----------------------------------------------------
from app.api.datasets import sanitize_id

@router.post("/api/analysis/start", status_code=status.HTTP_200_OK)
async def start_analysis(request: StartAnalysisRequest):
    dataset_id = sanitize_id(request.dataset_id)
    raw_query = (request.user_query or "").strip()
    
    if not dataset_id or not raw_query:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="dataset_id and user_query are required."
        )

    if len(raw_query) > 1000:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_query exceeds maximum allowed length of 1000 characters."
        )

    # Sanitize user query text
    user_query = raw_query.replace("<script>", "").replace("</script>", "")

    analysis_id = sanitize_id(request.analysis_id) if request.analysis_id else f"analysis_{uuid.uuid4().hex[:8]}"

    # Resolve dataset path if present in store
    summary = dataset_store.get_summary(dataset_id)
    dataset_path = ""
    if summary:
        file_path = UPLOAD_DIR / f"{dataset_id}_{summary['filename']}"
        if file_path.exists():
            dataset_path = str(file_path)

    # Record initial analysis entry in SQLite database
    db = SessionLocal()
    try:
        create_analysis_db(db, analysis_id=analysis_id, dataset_id=dataset_id, user_query=user_query, status="started")
        add_analysis_step_db(db, analysis_id=analysis_id, step_name="profile_dataset", status="completed")
    except Exception as e:
        print(f"[Warning] Failed to record initial analysis entry in SQLite: {e}")
    finally:
        db.close()

    # Build initial LangGraph state
    initial_state: AgentState = {
        "dataset_id": dataset_id,
        "dataset_path": dataset_path,
        "user_query": user_query,
        "retry_count": 0,
        "status": "started",
    }

    # Invoke LangGraph state workflow
    try:
        graph = get_analysis_graph()
        final_state = graph.invoke(initial_state)

        result_dict = dict(final_state)
        result_dict["analysis_id"] = analysis_id
        analysis_store[analysis_id] = result_dict

        # Persist completed analysis in SQLite database
        db = SessionLocal()
        try:
            update_analysis_db(
                db=db,
                analysis_id=analysis_id,
                status=result_dict.get("status", "completed"),
                analysis_plan=result_dict.get("analysis_plan"),
                generated_code=result_dict.get("generated_code"),
                execution_result={
                    "success": result_dict.get("execution_result", {}).get("success", False),
                    "stdout": result_dict.get("execution_result", {}).get("stdout", ""),
                    "stderr": result_dict.get("execution_result", {}).get("stderr", ""),
                    "charts": result_dict.get("charts", []),
                    "insights": result_dict.get("insights", []),
                    "report": result_dict.get("report", ""),
                },
                completed_at=datetime.utcnow()
            )

            # Record steps
            steps = ["analyze_intent", "create_analysis_plan", "code_generator", "validator", "executor", "visualization", "insights", "report"]
            for step_name in steps:
                add_analysis_step_db(db, analysis_id=analysis_id, step_name=step_name, status="completed")

            # Record generated chart files
            charts = result_dict.get("charts", [])
            for c in charts:
                add_generated_file_db(
                    db=db,
                    analysis_id=analysis_id,
                    file_type="chart",
                    filepath=c.get("path") or str(CHARTS_DIR / c.get("filename", "chart.png"))
                )

        except Exception as e:
            print(f"[Warning] Failed to persist completed analysis in SQLite: {e}")
        finally:
            db.close()

        return result_dict

    except Exception as e:
        # Record error state in SQLite database
        db = SessionLocal()
        try:
            update_analysis_db(db=db, analysis_id=analysis_id, status="failed", completed_at=datetime.utcnow())
            add_analysis_step_db(db, analysis_id=analysis_id, step_name="executor", status="failed", error=str(e))
        except Exception:
            pass
        finally:
            db.close()

        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"LangGraph execution error: {str(e)}"
        )

# ----------------------------------------------------
# 2. Phase 9 Required Endpoints: GET /api/analyses, GET /api/analyses/{id}, DELETE /api/analyses/{id}
# ----------------------------------------------------
@router.get("/api/analyses", status_code=status.HTTP_200_OK)
async def list_all_analyses():
    """
    Lists all saved analyses with metadata from SQLite database.
    """
    db = SessionLocal()
    try:
        db_analyses = list_analyses_db(db)
        results = []
        for a in db_analyses:
            filename = "Uploaded Dataset"
            if a.dataset:
                filename = a.dataset.filename
            else:
                summary = dataset_store.get_summary(a.dataset_id)
                if summary:
                    filename = summary.get("filename", "Dataset")

            results.append({
                "id": a.id,
                "analysis_id": a.id,
                "dataset_id": a.dataset_id,
                "filename": filename,
                "user_query": a.user_query,
                "status": a.status,
                "created_at": a.created_at.isoformat() if a.created_at else None,
                "completed_at": a.completed_at.isoformat() if a.completed_at else None,
            })
        return results
    finally:
        db.close()

@router.get("/api/analyses/{analysis_id}", status_code=status.HTTP_200_OK)
async def get_single_analysis(analysis_id: str):
    """
    Retrieves full saved analysis state by analysis ID from SQLite database.
    """
    # Check in-memory store first
    if analysis_id in analysis_store:
        state = analysis_store[analysis_id]
        return {
            "id": analysis_id,
            "analysis_id": analysis_id,
            "dataset_id": state.get("dataset_id"),
            "user_query": state.get("user_query"),
            "status": state.get("status", "completed"),
            "intent": state.get("intent"),
            "analysis_plan": state.get("analysis_plan"),
            "generated_code": state.get("generated_code"),
            "execution_result": state.get("execution_result"),
            "execution_error": state.get("execution_error"),
            "retry_count": state.get("retry_count", 0),
            "charts": state.get("charts", []),
            "insights": state.get("insights", []),
            "report": state.get("report", ""),
            "created_at": datetime.utcnow().isoformat(),
        }

    # Query SQLite database
    db = SessionLocal()
    try:
        a = get_analysis_db(db, analysis_id)
        if not a:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID '{analysis_id}' not found."
            )

        exec_res = a.execution_result or {}
        charts = exec_res.get("charts", [])
        insights = exec_res.get("insights", [])
        report = exec_res.get("report", "")

        return {
            "id": a.id,
            "analysis_id": a.id,
            "dataset_id": a.dataset_id,
            "user_query": a.user_query,
            "status": a.status,
            "analysis_plan": a.analysis_plan,
            "generated_code": a.generated_code,
            "execution_result": exec_res,
            "charts": charts,
            "insights": insights,
            "report": report,
            "created_at": a.created_at.isoformat() if a.created_at else None,
            "completed_at": a.completed_at.isoformat() if a.completed_at else None,
        }
    finally:
        db.close()

@router.delete("/api/analyses/{analysis_id}", status_code=status.HTTP_200_OK)
async def delete_single_analysis(analysis_id: str):
    """
    Deletes an analysis record from SQLite database (does NOT delete raw uploaded dataset files).
    """
    if analysis_id in analysis_store:
        del analysis_store[analysis_id]

    db = SessionLocal()
    try:
        deleted = delete_analysis_db(db, analysis_id)
        if not deleted and analysis_id not in analysis_store:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Analysis with ID '{analysis_id}' not found."
            )
        return {"success": True, "message": f"Analysis '{analysis_id}' deleted successfully."}
    finally:
        db.close()

# ----------------------------------------------------
# 3. Compatibility / Sub-resource endpoints (/api/analysis/{analysis_id}/...)
# ----------------------------------------------------
@router.get("/api/analysis/{analysis_id}/results", status_code=status.HTTP_200_OK)
async def get_analysis_results(analysis_id: str):
    return await get_single_analysis(analysis_id)

@router.get("/api/analysis/{analysis_id}/charts", status_code=status.HTTP_200_OK)
async def get_analysis_charts(analysis_id: str):
    data = await get_single_analysis(analysis_id)
    return {
        "analysis_id": analysis_id,
        "charts": data.get("charts", [])
    }

@router.get("/api/analysis/{analysis_id}/report", status_code=status.HTTP_200_OK)
async def get_analysis_report(analysis_id: str):
    data = await get_single_analysis(analysis_id)
    return {
        "analysis_id": analysis_id,
        "report": data.get("report", "# Executive Summary\nNo report generated.")
    }

@router.get("/api/analysis/charts/{filename}", status_code=status.HTTP_200_OK)
async def serve_chart_image(filename: str):
    file_path = CHARTS_DIR / filename
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path, media_type="image/png")
    
    sandbox_chart = Path(__file__).resolve().parent.parent.parent / "analysis_chart.png"
    if sandbox_chart.exists():
        return FileResponse(sandbox_chart, media_type="image/png")

    raise HTTPException(
        status_code=status.HTTP_404_NOT_FOUND,
        detail=f"Chart image '{filename}' not found."
    )
