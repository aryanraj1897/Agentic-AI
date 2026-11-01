from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from app.config import settings
from app.api.datasets import router as datasets_router
from app.api.analysis import router as analysis_router
from app.db.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    init_db()
    # Ensure generated directory exists
    generated_dir = Path(__file__).resolve().parent.parent / "generated"
    generated_dir.mkdir(parents=True, exist_ok=True)
    yield

app = FastAPI(
    title="Autonomous Data Analysis Agent API",
    description="Backend service for Autonomous Data Analysis Agent",
    version="0.3.0",
    lifespan=lifespan
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routers
app.include_router(datasets_router)
app.include_router(analysis_router)

# Static file serving for generated charts & reports
generated_path = Path(__file__).resolve().parent.parent / "generated"
generated_path.mkdir(parents=True, exist_ok=True)
app.mount("/generated", StaticFiles(directory=str(generated_path)), name="generated")

@app.get("/api/health")
async def health_check():
    return {
        "status": "ok",
        "service": "autonomous-data-analysis-agent"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=True
    )

