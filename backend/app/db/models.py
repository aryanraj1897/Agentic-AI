from datetime import datetime
from sqlalchemy import Column, String, Integer, Text, DateTime, ForeignKey, JSON
from sqlalchemy.orm import relationship
from app.db.database import Base

class Dataset(Base):
    __tablename__ = "datasets"

    id = Column(String, primary_key=True, index=True)
    filename = Column(String, nullable=False)
    filepath = Column(String, nullable=False)
    upload_time = Column(DateTime, default=datetime.utcnow)
    rows = Column(Integer, default=0)
    columns = Column(Integer, default=0)
    profile = Column(JSON, nullable=True)

    analyses = relationship("Analysis", back_populates="dataset", cascade="all, delete-orphan")

class Analysis(Base):
    __tablename__ = "analyses"

    id = Column(String, primary_key=True, index=True)
    dataset_id = Column(String, ForeignKey("datasets.id"), nullable=False)
    user_query = Column(Text, nullable=False)
    status = Column(String, default="started")
    analysis_plan = Column(JSON, nullable=True)
    generated_code = Column(Text, nullable=True)
    execution_result = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)

    dataset = relationship("Dataset", back_populates="analyses")
    steps = relationship("AnalysisStep", back_populates="analysis", cascade="all, delete-orphan")
    generated_files = relationship("GeneratedFile", back_populates="analysis", cascade="all, delete-orphan")

class AnalysisStep(Base):
    __tablename__ = "analysis_steps"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    step_name = Column(String, nullable=False)
    status = Column(String, default="pending")
    started_at = Column(DateTime, default=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    error = Column(Text, nullable=True)

    analysis = relationship("Analysis", back_populates="steps")

class GeneratedFile(Base):
    __tablename__ = "generated_files"

    id = Column(Integer, primary_key=True, autoincrement=True)
    analysis_id = Column(String, ForeignKey("analyses.id"), nullable=False)
    file_type = Column(String, nullable=False)  # e.g., "chart", "report"
    filepath = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    analysis = relationship("Analysis", back_populates="generated_files")
