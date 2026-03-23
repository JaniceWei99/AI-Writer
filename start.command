#!/bin/bash
# =============================================================
#  AI Writing Assistant — One-Click Startup Script for macOS
#  Double-click this file to start the application.
# =============================================================

set -e

# Resolve project root (where this script lives)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
cd "$SCRIPT_DIR"

PORT=8000
MODEL="qwen3.5:9b"

# ── Colors ──────────────────────────────────────────────────
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color

info()  { echo -e "${CYAN}[INFO]${NC}  $1"; }
ok()    { echo -e "${GREEN}[OK]${NC}    $1"; }
warn()  { echo -e "${YELLOW}[WARN]${NC}  $1"; }
fail()  { echo -e "${RED}[FAIL]${NC}  $1"; }

echo ""
echo "=========================================="
echo "   AI Writing Assistant  v1.3.1"
echo "=========================================="
echo ""

# ── Step 1: Check Ollama ────────────────────────────────────
info "Checking Ollama..."
if ! command -v ollama &>/dev/null; then
    fail "Ollama is not installed."
    echo ""
    echo "  Please install Ollama first:"
    echo "  https://ollama.ai/download"
    echo ""
    echo "  Press any key to exit..."
    read -n 1
    exit 1
fi
ok "Ollama found: $(which ollama)"

# Start Ollama service if not running
if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
    info "Starting Ollama service..."
    ollama serve &>/dev/null &
    OLLAMA_PID=$!
    sleep 3
    if ! curl -sf http://localhost:11434/api/tags &>/dev/null; then
        fail "Failed to start Ollama service."
        echo "  Press any key to exit..."
        read -n 1
        exit 1
    fi
    ok "Ollama service started (PID: $OLLAMA_PID)"
else
    ok "Ollama service is already running"
fi

# Check if model is available, pull if not
info "Checking model: $MODEL ..."
if ! ollama list 2>/dev/null | grep -q "$MODEL"; then
    warn "Model $MODEL not found. Downloading (~5GB, this may take a while)..."
    ollama pull "$MODEL"
    if [ $? -ne 0 ]; then
        fail "Failed to download model."
        echo "  Press any key to exit..."
        read -n 1
        exit 1
    fi
fi
ok "Model $MODEL is ready"

# ── Step 2: Check Python ────────────────────────────────────
info "Checking Python..."
PYTHON=""
for cmd in python3 python; do
    if command -v "$cmd" &>/dev/null; then
        version=$("$cmd" --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        major=$(echo "$version" | cut -d. -f1)
        minor=$(echo "$version" | cut -d. -f2)
        if [ "$major" -ge 3 ] && [ "$minor" -ge 10 ]; then
            PYTHON="$cmd"
            break
        fi
    fi
done

if [ -z "$PYTHON" ]; then
    fail "Python 3.10+ is required but not found."
    echo ""
    echo "  Install with Homebrew:  brew install python@3.12"
    echo ""
    echo "  Press any key to exit..."
    read -n 1
    exit 1
fi
ok "Python found: $($PYTHON --version)"

# ── Step 3: Setup backend virtual environment ────────────────
info "Setting up backend..."
cd "$SCRIPT_DIR/backend"

if [ ! -d ".venv" ]; then
    info "Creating virtual environment..."
    $PYTHON -m venv .venv
fi

source .venv/bin/activate

info "Installing backend dependencies..."
if command -v uv &>/dev/null; then
    uv sync --quiet 2>/dev/null || uv pip install -r requirements.txt --quiet 2>/dev/null || pip install -r requirements.txt --quiet
else
    pip install -r requirements.txt --quiet 2>/dev/null || pip install fastapi httpx pydantic pypdf2 python-docx python-multipart python-pptx uvicorn sqlalchemy aiosqlite fpdf2 --quiet
fi
ok "Backend dependencies installed"

# ── Step 4: Build frontend (if dist doesn't exist) ──────────
cd "$SCRIPT_DIR"
if [ ! -f "frontend/dist/index.html" ]; then
    info "Building frontend..."

    if ! command -v node &>/dev/null; then
        fail "Node.js is required to build frontend but not found."
        echo ""
        echo "  Install with Homebrew:  brew install node"
        echo ""
        echo "  Press any key to exit..."
        read -n 1
        exit 1
    fi

    cd "$SCRIPT_DIR/frontend"
    npm install --silent 2>/dev/null
    npm run build 2>/dev/null
    cd "$SCRIPT_DIR"

    if [ ! -f "frontend/dist/index.html" ]; then
        fail "Frontend build failed."
        echo "  Press any key to exit..."
        read -n 1
        exit 1
    fi
    ok "Frontend built successfully"
else
    ok "Frontend already built (frontend/dist/)"
fi

# ── Step 5: Kill any existing process on port ────────────────
if lsof -ti:$PORT &>/dev/null; then
    warn "Port $PORT is in use, killing existing process..."
    lsof -ti:$PORT | xargs kill -9 2>/dev/null
    sleep 1
fi

# ── Step 6: Start backend server ─────────────────────────────
info "Starting backend server on port $PORT ..."
cd "$SCRIPT_DIR/backend"
source .venv/bin/activate

uvicorn main:app --host 0.0.0.0 --port $PORT &
SERVER_PID=$!
sleep 2

# Verify server is running
if ! curl -sf http://localhost:$PORT/api/health &>/dev/null; then
    fail "Backend server failed to start."
    echo "  Press any key to exit..."
    read -n 1
    exit 1
fi
ok "Backend server running (PID: $SERVER_PID)"

# ── Step 7: Open browser ────────────────────────────────────
URL="http://localhost:$PORT"
info "Opening browser: $URL"
open "$URL" 2>/dev/null || echo "  Please open $URL in your browser manually."

echo ""
echo "=========================================="
echo -e "  ${GREEN}AI Writing Assistant is running!${NC}"
echo "  URL: $URL"
echo ""
echo "  Press Ctrl+C to stop the server."
echo "=========================================="
echo ""

# ── Wait for Ctrl+C and cleanup ─────────────────────────────
cleanup() {
    echo ""
    info "Shutting down..."
    kill $SERVER_PID 2>/dev/null
    [ -n "$OLLAMA_PID" ] && kill $OLLAMA_PID 2>/dev/null
    ok "Server stopped. Goodbye!"
    exit 0
}

trap cleanup INT TERM
wait $SERVER_PID
