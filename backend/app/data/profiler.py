import pandas as pd
import numpy as np
from typing import Dict, Any, List

def _clean_val(val: Any) -> Any:
    """Helper to convert NumPy/pandas types to JSON-serializable Python native types."""
    if pd.isna(val) or val is None:
        return None
    if isinstance(val, (np.integer, int)):
        return int(val)
    if isinstance(val, (np.floating, float)):
        if np.isnan(val) or np.isinf(val):
            return None
        return float(val)
    if isinstance(val, (np.bool_, bool)):
        return bool(val)
    if isinstance(val, (pd.Timestamp, np.datetime64)):
        return str(val)
    return str(val)

def generate_profile(df: pd.DataFrame, dataset_id: str, filename: str, file_size_bytes: int, file_type: str, created_at: str) -> Dict[str, Any]:
    """
    Generates a comprehensive dataset profile from a pandas DataFrame.
    """
    rows = int(len(df))
    cols = int(len(df.columns))

    if rows == 0 or cols == 0:
        raise ValueError("Cannot profile an empty dataset.")

    # Duplicate rows detection
    duplicate_rows = int(df.duplicated().sum())
    duplicate_percentage = round(float((duplicate_rows / rows) * 100), 2) if rows > 0 else 0.0

    # Total missing values
    total_missing_values = int(df.isna().sum().sum())
    total_cells = rows * cols
    total_missing_percentage = round(float((total_missing_values / total_cells) * 100), 2) if total_cells > 0 else 0.0

    numeric_columns: List[str] = []
    categorical_columns: List[str] = []
    date_columns: List[str] = []
    boolean_columns: List[str] = []
    constant_columns: List[str] = []
    potential_id_columns: List[str] = []

    column_profiles: Dict[str, Dict[str, Any]] = {}

    for col in df.columns:
        col_name = str(col)
        series = df[col]

        missing_count = int(series.isna().sum())
        missing_percentage = round(float((missing_count / rows) * 100), 2) if rows > 0 else 0.0
        unique_count = int(series.nunique(dropna=False))
        non_null_unique_count = int(series.nunique(dropna=True))

        dtype_str = str(series.dtype)

        # Detect boolean column
        is_boolean = (
            pd.api.types.is_bool_dtype(series) or
            set(series.dropna().unique()).issubset({True, False, 0, 1, "true", "false", "True", "False"})
        )

        # Detect date column
        is_date = pd.api.types.is_datetime64_any_dtype(series)
        if not is_date and pd.api.types.is_object_dtype(series) and not is_boolean:
            col_lower = col_name.lower()
            if any(k in col_lower for k in ["date", "time", "created", "timestamp", "year", "month"]):
                try:
                    parsed = pd.to_datetime(series.dropna().head(20), errors="coerce")
                    if parsed.notna().sum() > 0.8 * len(series.dropna().head(20)):
                        is_date = True
                except Exception:
                    pass

        # Detect numeric column (excluding boolean)
        is_numeric = pd.api.types.is_numeric_dtype(series) and not is_boolean

        # Detect constant column (only 1 non-null value)
        is_constant = non_null_unique_count <= 1

        # Detect potential ID column
        is_potential_id = False
        col_lower = col_name.lower()
        has_id_name = any(k in col_lower for k in ["id", "uuid", "code", "index", "key", "pk", "fk"])
        is_unique = (non_null_unique_count == (rows - missing_count)) and rows > 1

        if not is_constant and non_null_unique_count > 0:
            if has_id_name and (is_unique or (non_null_unique_count / max(rows, 1)) > 0.5):
                is_potential_id = True
            elif is_unique and (pd.api.types.is_integer_dtype(series) or pd.api.types.is_object_dtype(series)) and not any(k in col_lower for k in ["age", "salary", "price", "amount", "score", "val", "count", "num"]):
                is_potential_id = True

        # Detect categorical column
        is_categorical = (
            not is_numeric and
            not is_date and
            not is_boolean and
            not is_potential_id
        ) or (
            is_numeric and non_null_unique_count <= 10 and not has_id_name and not is_potential_id
        )

        # Classification lists
        if is_numeric:
            numeric_columns.append(col_name)
        if is_categorical:
            categorical_columns.append(col_name)
        if is_date:
            date_columns.append(col_name)
        if is_boolean:
            boolean_columns.append(col_name)
        if is_constant:
            constant_columns.append(col_name)
        if is_potential_id:
            potential_id_columns.append(col_name)


        # Numerical statistics
        mean_val = None
        median_val = None
        std_val = None
        min_val = None
        max_val = None

        if is_numeric:
            valid_series = series.dropna()
            if len(valid_series) > 0:
                mean_val = _clean_val(valid_series.mean())
                median_val = _clean_val(valid_series.median())
                std_val = _clean_val(valid_series.std()) if len(valid_series) > 1 else 0.0
                min_val = _clean_val(valid_series.min())
                max_val = _clean_val(valid_series.max())
        else:
            valid_series = series.dropna()
            if len(valid_series) > 0:
                try:
                    min_val = _clean_val(valid_series.min())
                    max_val = _clean_val(valid_series.max())
                except Exception:
                    pass

        # Get top 5 sample values
        sample_vals = [_clean_val(v) for v in series.dropna().unique()[:5]]

        column_profiles[col_name] = {
            "name": col_name,
            "dtype": dtype_str,
            "missing_count": missing_count,
            "missing_percentage": missing_percentage,
            "unique_count": unique_count,
            "is_numeric": is_numeric,
            "is_categorical": is_categorical,
            "is_date": is_date,
            "is_boolean": is_boolean,
            "is_constant": is_constant,
            "is_potential_id": is_potential_id,
            "mean": mean_val,
            "median": median_val,
            "std": std_val,
            "min": min_val,
            "max": max_val,
            "sample_values": sample_vals,
        }

    profile = {
        "dataset_id": dataset_id,
        "filename": filename,
        "rows": rows,
        "columns": cols,
        "file_size_bytes": file_size_bytes,
        "file_type": file_type,
        "created_at": created_at,
        "duplicate_rows": duplicate_rows,
        "duplicate_percentage": duplicate_percentage,
        "total_missing_values": total_missing_values,
        "total_missing_percentage": total_missing_percentage,
        "numeric_columns": numeric_columns,
        "categorical_columns": categorical_columns,
        "date_columns": date_columns,
        "boolean_columns": boolean_columns,
        "constant_columns": constant_columns,
        "potential_id_columns": potential_id_columns,
        "column_profiles": column_profiles,
    }

    return profile
