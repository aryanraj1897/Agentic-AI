from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional

class ColumnProfile(BaseModel):
    name: str
    dtype: str
    missing_count: int
    missing_percentage: float
    unique_count: int
    is_numeric: bool
    is_categorical: bool
    is_date: bool
    is_boolean: bool
    is_constant: bool
    is_potential_id: bool
    mean: Optional[float] = None
    median: Optional[float] = None
    std: Optional[float] = None
    min: Optional[Any] = None
    max: Optional[Any] = None
    sample_values: List[Any] = Field(default_factory=list)

class DatasetSummary(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    file_size_bytes: int
    file_type: str
    created_at: str

class DatasetProfileResponse(BaseModel):
    dataset_id: str
    filename: str
    rows: int
    columns: int
    file_size_bytes: int
    file_type: str
    created_at: str
    duplicate_rows: int
    duplicate_percentage: float
    total_missing_values: int
    total_missing_percentage: float
    numeric_columns: List[str]
    categorical_columns: List[str]
    date_columns: List[str]
    boolean_columns: List[str]
    constant_columns: List[str]
    potential_id_columns: List[str]
    column_profiles: Dict[str, ColumnProfile]
