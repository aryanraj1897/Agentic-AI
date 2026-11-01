import os
import re
import uuid
import tempfile
from pathlib import Path
from datetime import datetime, timezone
from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.config import settings
from app.data.loader import load_dataset, SUPPORTED_EXTENSIONS
from app.data.profiler import generate_profile
from app.data.store import dataset_store

router = APIRouter(prefix="/api/datasets", tags=["Datasets"])

ALLOWED_MIME_TYPES = {
    ".csv": ["text/csv", "text/plain", "application/csv", "application/x-csv", "text/x-comma-separated-values", "application/vnd.ms-excel", "application/octet-stream"],
    ".xlsx": ["application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", "application/vnd.ms-excel", "application/excel", "application/octet-stream"],
    ".xls": ["application/vnd.ms-excel", "application/excel", "application/octet-stream"],
    ".json": ["application/json", "text/json", "text/plain", "application/octet-stream"]
}

def sanitize_filename(filename: str) -> str:
    """
    Sanitizes filenames to prevent path traversal or shell injection exploits.
    """
    if not filename:
        return "dataset.csv"
    # Strip directory paths
    base_name = os.path.basename(filename)
    # Remove path traversal dots and backslashes
    base_name = re.sub(r"\.\.+", ".", base_name)
    base_name = re.sub(r"[^\w\.\-]", "_", base_name)
    # Truncate filename length
    if len(base_name) > 100:
        name, ext = os.path.splitext(base_name)
        base_name = name[:90] + ext
    return base_name

def sanitize_id(identifier: str) -> str:
    """
    Sanitizes dataset_id or analysis_id against path traversal attacks.
    """
    if not identifier or ".." in identifier or "/" in identifier or "\\" in identifier:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or malformed ID format."
        )
    return re.sub(r"[^\w\-]", "", identifier)

@router.post("/upload", status_code=status.HTTP_201_CREATED)
async def upload_dataset(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Filename cannot be empty."
        )

    # 1. Sanitize filename & validate path traversal
    safe_filename = sanitize_filename(file.filename)
    ext = os.path.splitext(safe_filename)[1].lower()

    if ext not in SUPPORTED_EXTENSIONS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Unsupported file format '{ext}'. Supported formats: CSV, XLSX, XLS, JSON."
        )

    # 2. MIME type validation
    content_type = (file.content_type or "").lower()
    allowed_mimes = ALLOWED_MIME_TYPES.get(ext, [])
    if content_type and allowed_mimes and not any(mime in content_type for mime in allowed_mimes):
        # Log warning but allow if content_type is octet-stream
        if "octet-stream" not in content_type and "application/unknown" not in content_type:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid MIME type '{content_type}' for file extension '{ext}'."
            )

    # 3. Read content with size check (50 MB limit)
    content = await file.read()
    file_size_bytes = len(content)
    max_size_bytes = settings.MAX_FILE_SIZE_MB * 1024 * 1024  # 50 MB

    if file_size_bytes == 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Uploaded file is empty (0 bytes)."
        )

    if file_size_bytes > max_size_bytes:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail=f"File size exceeds maximum allowed limit of {settings.MAX_FILE_SIZE_MB}MB."
        )

    # 4. Generate unique safe dataset ID
    dataset_id = str(uuid.uuid4())
    created_at = datetime.now(timezone.utc).isoformat()

    # 5. Load & profile dataset safely using tempfile
    with tempfile.NamedTemporaryFile(suffix=ext, delete=False) as tmp_file:
        tmp_file.write(content)
        tmp_file_path = tmp_file.name

    try:
        df = load_dataset(content, safe_filename)
        profile = generate_profile(
            df=df,
            dataset_id=dataset_id,
            filename=safe_filename,
            file_size_bytes=file_size_bytes,
            file_type=ext.replace(".", "").upper(),
            created_at=created_at
        )
    except ValueError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Failed to process dataset file safely: {str(e)}"
        )
    finally:
        # Clean up temporary file
        if os.path.exists(tmp_file_path):
            try:
                os.remove(tmp_file_path)
            except Exception:
                pass

    # 6. Save dataset file & profile in unique directory
    file_path_str = str(dataset_store.save_dataset(dataset_id, safe_filename, content, profile))

    # Persist in SQLite database
    try:
        from app.db.database import SessionLocal
        from app.db.repository import save_dataset_db
        db = SessionLocal()
        try:
            save_dataset_db(
                db=db,
                dataset_id=dataset_id,
                filename=safe_filename,
                filepath=file_path_str,
                rows=profile["rows"],
                columns=profile["columns"],
                profile=profile
            )
        finally:
            db.close()
    except Exception:
        pass

    return {
        "dataset_id": dataset_id,
        "filename": safe_filename,
        "rows": profile["rows"],
        "columns": profile["columns"],
        "file_size_bytes": file_size_bytes,
        "file_type": profile["file_type"],
        "created_at": created_at,
    }

@router.get("/{dataset_id}")
async def get_dataset_metadata(dataset_id: str):
    clean_id = sanitize_id(dataset_id)
    summary = dataset_store.get_summary(clean_id)
    if not summary:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset with ID '{clean_id}' not found."
        )
    return summary

@router.get("/{dataset_id}/profile")
async def get_dataset_profile(dataset_id: str):
    clean_id = sanitize_id(dataset_id)
    profile = dataset_store.get_profile(clean_id)
    if not profile:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Dataset profile for ID '{clean_id}' not found."
        )
    return profile
