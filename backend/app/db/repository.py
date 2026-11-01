from datetime import datetime
from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session
from app.db.models import Dataset, Analysis, AnalysisStep, GeneratedFile

def save_dataset_db(
    db: Session,
    dataset_id: str,
    filename: str,
    filepath: str,
    rows: int,
    columns: int,
    profile: Optional[Dict[str, Any]] = None
) -> Dataset:
    db_dataset = db.query(Dataset).filter(Dataset.id == dataset_id).first()
    if not db_dataset:
        db_dataset = Dataset(
            id=dataset_id,
            filename=filename,
            filepath=filepath,
            upload_time=datetime.utcnow(),
            rows=rows,
            columns=columns,
            profile=profile
        )
        db.add(db_dataset)
    else:
        db_dataset.filename = filename
        db_dataset.filepath = filepath
        db_dataset.rows = rows
        db_dataset.columns = columns
        if profile:
            db_dataset.profile = profile
    db.commit()
    db.refresh(db_dataset)
    return db_dataset

def get_dataset_db(db: Session, dataset_id: str) -> Optional[Dataset]:
    return db.query(Dataset).filter(Dataset.id == dataset_id).first()

def list_datasets_db(db: Session) -> List[Dataset]:
    return db.query(Dataset).order_by(Dataset.upload_time.desc()).all()

def create_analysis_db(
    db: Session,
    analysis_id: str,
    dataset_id: str,
    user_query: str,
    status: str = "started"
) -> Analysis:
    db_analysis = Analysis(
        id=analysis_id,
        dataset_id=dataset_id,
        user_query=user_query,
        status=status,
        created_at=datetime.utcnow()
    )
    db.add(db_analysis)
    db.commit()
    db.refresh(db_analysis)
    return db_analysis

def update_analysis_db(
    db: Session,
    analysis_id: str,
    status: str,
    analysis_plan: Optional[List[Dict[str, Any]]] = None,
    generated_code: Optional[str] = None,
    execution_result: Optional[Dict[str, Any]] = None,
    completed_at: Optional[datetime] = None
) -> Optional[Analysis]:
    db_analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if db_analysis:
        db_analysis.status = status
        if analysis_plan is not None:
            db_analysis.analysis_plan = analysis_plan
        if generated_code is not None:
            db_analysis.generated_code = generated_code
        if execution_result is not None:
            db_analysis.execution_result = execution_result
        if completed_at is not None:
            db_analysis.completed_at = completed_at
        else:
            db_analysis.completed_at = datetime.utcnow()
        db.commit()
        db.refresh(db_analysis)
    return db_analysis

def add_analysis_step_db(
    db: Session,
    analysis_id: str,
    step_name: str,
    status: str = "completed",
    started_at: Optional[datetime] = None,
    completed_at: Optional[datetime] = None,
    error: Optional[str] = None
) -> AnalysisStep:
    step = AnalysisStep(
        analysis_id=analysis_id,
        step_name=step_name,
        status=status,
        started_at=started_at or datetime.utcnow(),
        completed_at=completed_at or datetime.utcnow(),
        error=error
    )
    db.add(step)
    db.commit()
    db.refresh(step)
    return step

def add_generated_file_db(
    db: Session,
    analysis_id: str,
    file_type: str,
    filepath: str
) -> GeneratedFile:
    gf = GeneratedFile(
        analysis_id=analysis_id,
        file_type=file_type,
        filepath=filepath,
        created_at=datetime.utcnow()
    )
    db.add(gf)
    db.commit()
    db.refresh(gf)
    return gf

def get_analysis_db(db: Session, analysis_id: str) -> Optional[Analysis]:
    return db.query(Analysis).filter(Analysis.id == analysis_id).first()

def list_analyses_db(db: Session) -> List[Analysis]:
    return db.query(Analysis).order_by(Analysis.created_at.desc()).all()

def delete_analysis_db(db: Session, analysis_id: str) -> bool:
    db_analysis = db.query(Analysis).filter(Analysis.id == analysis_id).first()
    if db_analysis:
        db.delete(db_analysis)
        db.commit()
        return True
    return False
