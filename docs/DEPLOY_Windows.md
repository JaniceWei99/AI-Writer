# Windows One-Click Deployment Guide

## Quick Start

### Prerequisites

Install these on the target Windows PC (one-time setup):

1. **Ollama** — Download from [ollama.ai/download](https://ollama.ai/download)
2. **Python 3.10+** — Download from [python.org](https://www.python.org/downloads/)
   - **Important**: Check "Add Python to PATH" during installation
3. **Node.js 18+** — Download from [nodejs.org](https://nodejs.org/) (only needed for the first build)

### Deploy

1. Copy the entire project folder to the PC (or `git clone`)
2. Double-click **`start.bat`**
3. Done! The browser will open automatically.

The script handles everything automatically:
- Checks and starts Ollama service
- Downloads the AI model if not present (~5GB, first time only)
- Creates Python virtual environment and installs dependencies
- Builds the frontend (first time only)
- Starts the backend server
- Opens the browser

### Stop

Close the command prompt window to stop the server.

---

## What the Script Does

```
start.bat
    │
    ├── 1. Check Ollama installed → start service if needed
    ├── 2. Check model (qwen3.5:9b) → pull if missing
    ├── 3. Check Python 3.10+ → setup venv + install deps
    ├── 4. Build frontend (if dist\ missing) → npm install + build
    ├── 5. Start backend (uvicorn on port 8000)
    ├── 6. Open browser → http://localhost:8000
    └── 7. Keep window open until closed
```

## FAQ

**Q: First startup is slow?**
A: The first run downloads the AI model (~5GB) and installs all dependencies. Subsequent startups take about 5 seconds.

**Q: Port 8000 is already in use?**
A: The script automatically kills any existing process on port 8000.

**Q: How to change the AI model?**
A: Open the app → click the gear icon (Settings) → change the model name. Make sure the model is pulled in Ollama first (`ollama pull <model-name>`).

**Q: Python is installed but script says "not found"?**
A: Make sure "Add Python to PATH" was checked during installation. Or reinstall Python and check that option.

**Q: "Windows protected your PC" warning?**
A: Click "More info" → "Run anyway". This is normal for unsigned scripts.

**Q: How to update?**
A: Pull the latest code (`git pull`), delete the `frontend\dist\` folder, and double-click `start.bat` again. The frontend will be rebuilt automatically.
