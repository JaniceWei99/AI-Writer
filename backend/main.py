import os
from contextlib import asynccontextmanager
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from routers.writing import router as writing_router
from routers.history import router as history_router
from routers.styles import router as styles_router
from db import init_db
from logging_config import setup_logging
from middleware import RequestLoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware

logger = setup_logging()

# --- Environment-based configuration ---
# Defaults are for local development; override via env vars for shared deployment.
CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS", "http://localhost:5173,http://localhost:3000"
).split(",")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen3.5:9b")

# Pre-built frontend static files directory
STATIC_DIR = Path(__file__).resolve().parent.parent / "frontend" / "dist"


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting AI 写作助手 v1.3.1")
    await init_db()
    logger.info("Database ready")
    yield
    logger.info("Shutting down")


app = FastAPI(title="AI 写作助手", version="1.3.1", lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=10, window_seconds=60)

app.include_router(writing_router)
app.include_router(history_router)
app.include_router(styles_router)


@app.get("/api/health")
async def health_check():
    from services.llm_provider import get_provider_info
    info = get_provider_info()
    return {"status": "ok", **info}


@app.get("/api/models")
async def get_models():
    """返回当前 LLM provider 中可用的模型列表。"""
    from services.llm_provider import list_models, get_default_model
    try:
        names = await list_models()
        return {"models": names, "default": get_default_model()}
    except Exception:
        from services.llm_provider import get_default_model as gdm
        return {"models": [], "default": gdm()}


# Serve pre-built frontend static files (production mode)
if STATIC_DIR.is_dir():
    app.mount("/assets", StaticFiles(directory=STATIC_DIR / "assets"), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        """Serve index.html for any non-API route (SPA fallback)."""
        file_path = STATIC_DIR / full_path
        if full_path and file_path.is_file():
            return FileResponse(file_path)
        return FileResponse(STATIC_DIR / "index.html")
