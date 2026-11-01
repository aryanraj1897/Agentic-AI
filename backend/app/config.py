import os
from pathlib import Path
from pydantic_settings import BaseSettings, SettingsConfigDict
from typing import List

# Determine base directory of backend
BASE_DIR = Path(__file__).resolve().parent.parent

class Settings(BaseSettings):
    LLM_PROVIDER: str = "openai"
    OPENAI_API_KEY: str = ""
    MODEL_NAME: str = "gpt-4o"
    MAX_FILE_SIZE_MB: int = 50
    EXECUTION_TIMEOUT: int = 30
    MAX_RETRIES: int = 3
    PORT: int = 8000
    HOST: str = "0.0.0.0"
    CORS_ORIGINS: str = "http://localhost:5173,http://127.0.0.1:5173,http://localhost:3000"

    model_config = SettingsConfigDict(
        env_file=str(BASE_DIR / ".env"),
        env_file_encoding="utf-8",
        extra="ignore"
    )

    @property
    def cors_origins_list(self) -> List[str]:
        return [origin.strip() for origin in self.CORS_ORIGINS.split(",") if origin.strip()]

settings = Settings()
