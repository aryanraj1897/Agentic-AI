import os
import io
import pandas as pd
from typing import Union

SUPPORTED_EXTENSIONS = {".csv", ".xlsx", ".xls", ".json"}

def load_dataset(file_source: Union[str, bytes, io.BytesIO], filename: str) -> pd.DataFrame:
    """
    Loads a dataset into a pandas DataFrame from a file path or bytes buffer.
    Supports CSV, Excel (.xlsx, .xls), and JSON formats.
    """
    ext = os.path.splitext(filename)[1].lower()
    if ext not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file extension '{ext}'. Supported formats: CSV, XLSX, XLS, JSON")

    try:
        if isinstance(file_source, bytes):
            buffer = io.BytesIO(file_source)
        else:
            buffer = file_source

        if ext == ".csv":
            # Try loading CSV with default pandas parser
            df = pd.read_csv(buffer)
        elif ext in [".xlsx", ".xls"]:
            df = pd.read_excel(buffer)
        elif ext == ".json":
            # Attempt loading JSON
            try:
                df = pd.read_json(buffer)
            except ValueError:
                if isinstance(buffer, io.BytesIO):
                    buffer.seek(0)
                df = pd.read_json(buffer, lines=True)

        if df is None or df.empty:
            raise ValueError("The uploaded dataset is empty (0 rows or no columns).")

        return df

    except Exception as e:
        if "empty" in str(e).lower() or "unsupported" in str(e).lower():
            raise
        raise ValueError(f"Failed to parse dataset file '{filename}': {str(e)}")
