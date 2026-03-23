@echo off
chcp 65001 >nul 2>&1
setlocal enabledelayedexpansion

:: =============================================================
::  AI Writing Assistant — One-Click Startup Script for Windows
::  Double-click this file to start the application.
:: =============================================================

set PORT=8000
set MODEL=qwen3.5:9b

echo.
echo ==========================================
echo    AI Writing Assistant  v1.3.1
echo ==========================================
echo.

:: ── Step 1: Check Ollama ────────────────────────────────────
echo [INFO]  Checking Ollama...
where ollama >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL]  Ollama is not installed.
    echo.
    echo   Please install Ollama first:
    echo   https://ollama.ai/download
    echo.
    pause
    exit /b 1
)
echo [OK]    Ollama found

:: Start Ollama service if not running
curl -sf http://localhost:11434/api/tags >nul 2>&1
if %errorlevel% neq 0 (
    echo [INFO]  Starting Ollama service...
    start /b "" ollama serve >nul 2>&1
    timeout /t 5 /nobreak >nul
    curl -sf http://localhost:11434/api/tags >nul 2>&1
    if %errorlevel% neq 0 (
        echo [FAIL]  Failed to start Ollama service.
        pause
        exit /b 1
    )
    echo [OK]    Ollama service started
) else (
    echo [OK]    Ollama service is already running
)

:: Check if model is available, pull if not
echo [INFO]  Checking model: %MODEL% ...
ollama list 2>nul | findstr /i "%MODEL%" >nul 2>&1
if %errorlevel% neq 0 (
    echo [WARN]  Model %MODEL% not found. Downloading (~5GB, this may take a while^)...
    ollama pull %MODEL%
    if %errorlevel% neq 0 (
        echo [FAIL]  Failed to download model.
        pause
        exit /b 1
    )
)
echo [OK]    Model %MODEL% is ready

:: ── Step 2: Check Python ────────────────────────────────────
echo [INFO]  Checking Python...
set PYTHON=
for %%p in (python python3) do (
    where %%p >nul 2>&1
    if !errorlevel! equ 0 (
        for /f "tokens=2 delims= " %%v in ('%%p --version 2^>^&1') do (
            for /f "tokens=1,2 delims=." %%a in ("%%v") do (
                if %%a geq 3 if %%b geq 10 (
                    set PYTHON=%%p
                )
            )
        )
    )
)

if "%PYTHON%"=="" (
    echo [FAIL]  Python 3.10+ is required but not found.
    echo.
    echo   Download from: https://www.python.org/downloads/
    echo   Make sure to check "Add Python to PATH" during installation.
    echo.
    pause
    exit /b 1
)
for /f "delims=" %%v in ('%PYTHON% --version 2^>^&1') do echo [OK]    %%v found

:: ── Step 3: Setup backend virtual environment ────────────────
echo [INFO]  Setting up backend...
cd /d "%~dp0backend"

if not exist ".venv" (
    echo [INFO]  Creating virtual environment...
    %PYTHON% -m venv .venv
)

call .venv\Scripts\activate.bat

echo [INFO]  Installing backend dependencies...
where uv >nul 2>&1
if %errorlevel% equ 0 (
    uv sync --quiet 2>nul || uv pip install -r requirements.txt --quiet 2>nul || pip install -r requirements.txt --quiet
) else (
    pip install -r requirements.txt --quiet 2>nul || pip install fastapi httpx pydantic pypdf2 python-docx python-multipart python-pptx uvicorn sqlalchemy aiosqlite fpdf2 --quiet
)
echo [OK]    Backend dependencies installed

:: ── Step 4: Build frontend (if dist doesn't exist) ──────────
cd /d "%~dp0"
if not exist "frontend\dist\index.html" (
    echo [INFO]  Building frontend...

    where node >nul 2>&1
    if %errorlevel% neq 0 (
        echo [FAIL]  Node.js is required to build frontend but not found.
        echo.
        echo   Download from: https://nodejs.org/
        echo.
        pause
        exit /b 1
    )

    cd /d "%~dp0frontend"
    call npm install --silent 2>nul
    call npm run build 2>nul
    cd /d "%~dp0"

    if not exist "frontend\dist\index.html" (
        echo [FAIL]  Frontend build failed.
        pause
        exit /b 1
    )
    echo [OK]    Frontend built successfully
) else (
    echo [OK]    Frontend already built (frontend\dist\^)
)

:: ── Step 5: Kill any existing process on port ────────────────
for /f "tokens=5" %%a in ('netstat -aon ^| findstr ":%PORT% " ^| findstr "LISTENING"') do (
    echo [WARN]  Port %PORT% is in use, killing PID %%a ...
    taskkill /PID %%a /F >nul 2>&1
)
timeout /t 1 /nobreak >nul

:: ── Step 6: Start backend server ─────────────────────────────
echo [INFO]  Starting backend server on port %PORT% ...
cd /d "%~dp0backend"
call .venv\Scripts\activate.bat

start /b "" uvicorn main:app --host 0.0.0.0 --port %PORT%
timeout /t 3 /nobreak >nul

:: Verify server is running
curl -sf http://localhost:%PORT%/api/health >nul 2>&1
if %errorlevel% neq 0 (
    echo [FAIL]  Backend server failed to start.
    pause
    exit /b 1
)
echo [OK]    Backend server running on port %PORT%

:: ── Step 7: Open browser ────────────────────────────────────
set URL=http://localhost:%PORT%
echo [INFO]  Opening browser: %URL%
start "" "%URL%"

echo.
echo ==========================================
echo   AI Writing Assistant is running!
echo   URL: %URL%
echo.
echo   Close this window to stop the server.
echo ==========================================
echo.

:: ── Keep window open, wait for user to close ────────────────
:wait_loop
timeout /t 60 /nobreak >nul
curl -sf http://localhost:%PORT%/api/health >nul 2>&1
if %errorlevel% equ 0 goto wait_loop

echo [INFO]  Server stopped.
pause
