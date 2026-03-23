from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routers.writing import router as writing_router
from routers.history import router as history_router
from db import init_db
from logging_config import setup_logging
from middleware import RequestLoggingMiddleware
from middleware.rate_limit import RateLimitMiddleware

logger = setup_logging()


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
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(RequestLoggingMiddleware)
app.add_middleware(RateLimitMiddleware, max_requests=10, window_seconds=60)

app.include_router(writing_router)
app.include_router(history_router)


@app.get("/api/health")
async def health_check():
    return {"status": "ok", "model": "qwen3.5:9b"}
