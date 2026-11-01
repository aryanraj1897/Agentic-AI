import os
import json

from pathlib import Path
from typing import Dict, Any, Optional

UPLOAD_DIR = Path(__file__).resolve().parent.parent.parent / "uploads"
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

class DatasetStore:
    def __init__(self):
        self._memory_store: Dict[str, Dict[str, Any]] = {}
        self._load_existing_from_disk()

    def _load_existing_from_disk(self):
        for profile_file in UPLOAD_DIR.glob("*_profile.json"):
            try:
                with open(profile_file, "r", encoding="utf-8") as f:
                    profile = json.load(f)
                    dataset_id = profile.get("dataset_id")
                    if dataset_id:
                        self._memory_store[dataset_id] = profile
            except Exception:
                pass

    def save_dataset(self, dataset_id: str, filename: str, content: bytes, profile: Dict[str, Any]) -> str:
        # Save raw dataset file
        file_path = UPLOAD_DIR / f"{dataset_id}_{filename}"
        with open(file_path, "wb") as f:
            f.write(content)

        # Save profile JSON file
        profile_path = UPLOAD_DIR / f"{dataset_id}_profile.json"
        with open(profile_path, "w", encoding="utf-8") as f:
            json.dump(profile, f, indent=2)

        # Store in memory cache
        self._memory_store[dataset_id] = profile
        return str(file_path)

    def get_profile(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        if dataset_id in self._memory_store:
            return self._memory_store[dataset_id]

        profile_path = UPLOAD_DIR / f"{dataset_id}_profile.json"
        if profile_path.exists():
            with open(profile_path, "r", encoding="utf-8") as f:
                profile = json.load(f)
                self._memory_store[dataset_id] = profile
                return profile

        return None

    def get_summary(self, dataset_id: str) -> Optional[Dict[str, Any]]:
        profile = self.get_profile(dataset_id)
        if not profile:
            return None

        return {
            "dataset_id": profile["dataset_id"],
            "filename": profile["filename"],
            "rows": profile["rows"],
            "columns": profile["columns"],
            "file_size_bytes": profile["file_size_bytes"],
            "file_type": profile["file_type"],
            "created_at": profile["created_at"],
        }

dataset_store = DatasetStore()
