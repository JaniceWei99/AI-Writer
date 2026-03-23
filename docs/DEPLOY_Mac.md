# macOS One-Click Deployment Guide

## Quick Start

### Prerequisites

Install these on the target Mac (one-time setup):

1. **Ollama** — Download from [ollama.ai/download](https://ollama.ai/download)
2. **Python 3.10+** — `brew install python@3.12` (or download from [python.org](https://www.python.org/downloads/))
3. **Node.js 18+** — `brew install node` (only needed for the first build)

### Deploy

1. Copy the entire project folder to the Mac (or `git clone`)
2. Double-click **`start.command`**
3. Done! The browser will open automatically.

The script handles everything automatically:
- Checks and starts Ollama service
- Downloads the AI model if not present (~5GB, first time only)
- Creates Python virtual environment and installs dependencies
- Builds the frontend (first time only)
- Starts the backend server
- Opens the browser

### Stop

Press `Ctrl+C` in the terminal window to stop the server.

---

## What the Script Does

```
start.command
    │
    ├── 1. Check Ollama installed → start service if needed
    ├── 2. Check model (qwen3.5:9b) → pull if missing
    ├── 3. Check Python 3.10+ → setup venv + install deps
    ├── 4. Build frontend (if dist/ missing) → npm install + build
    ├── 5. Start backend (uvicorn on port 8000)
    ├── 6. Open browser → http://localhost:8000
    └── 7. Wait for Ctrl+C → cleanup
```

## FAQ

**Q: First startup is slow?**
A: The first run downloads the AI model (~5GB) and installs all dependencies. Subsequent startups take about 5 seconds.

**Q: Port 8000 is already in use?**
A: The script automatically kills any existing process on port 8000.

**Q: How to change the AI model?**
A: Open the app → click the gear icon (Settings) → change the model name. Make sure the model is pulled in Ollama first (`ollama pull <model-name>`).

**Q: "Cannot be opened because it is from an unidentified developer"?**
A: Right-click `start.command` → "Open" → "Open" again. Or go to System Settings → Privacy & Security → "Open Anyway".

**Q: How to update?**
A: Pull the latest code (`git pull`), delete `frontend/dist/`, and double-click `start.command` again. The frontend will be rebuilt automatically.
