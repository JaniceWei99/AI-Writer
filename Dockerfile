# =============================================================
#  AI Writing Assistant — Multi-stage Dockerfile
#  Stage 1: Build frontend
#  Stage 2: Run backend + serve frontend static files
# =============================================================

# ---- Stage 1: Build frontend ----
FROM node:20-slim AS frontend-build
WORKDIR /build
COPY frontend/package.json frontend/package-lock.json* ./
RUN npm ci --silent
COPY frontend/ ./
RUN npm run build

# ---- Stage 2: Backend + static files ----
FROM python:3.12-slim
WORKDIR /app

# Install uv for fast dependency management
COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

# Install backend dependencies
COPY backend/pyproject.toml backend/uv.lock* ./
RUN uv sync --no-dev --frozen 2>/dev/null || uv sync --no-dev

# Copy backend source
COPY backend/ ./

# Copy pre-built frontend into the expected location
COPY --from=frontend-build /build/dist /app/../frontend/dist

# Create data directory for SQLite
RUN mkdir -p /app/data

# Default environment variables (override in docker-compose or .env)
ENV OLLAMA_BASE_URL=http://ollama:11434
ENV OLLAMA_MODEL=qwen3.5:9b
ENV CORS_ORIGINS=*

EXPOSE 8000

CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
