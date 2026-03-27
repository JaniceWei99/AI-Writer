# AI Writing Assistant v1.5.0

> A local LLM-powered all-in-one writing tool with multi-style article generation, multi-layout PPT export, classical poetry creation, and multilingual translation. Fully local data — zero privacy concerns.

## Introduction

**AI Writing Assistant** is a full-stack intelligent writing platform. The backend is built with Python FastAPI, the frontend uses React + TypeScript + Vite, and AI capabilities are provided by a locally deployed LLM via Ollama (default: qwen3.5:9b). All data is stored in a local SQLite database with no dependency on any cloud services.

### Key Highlights

- **9 Writing Styles**: Literary, college entrance essay, Xiaohongshu viral, WeChat Official Account, Toutiao headlines, AI drama script, PPT outline, classical poetry, Zhihu top answers
- **Professional PPT Export**: 4 theme palettes x 6 slide layouts, with AI-powered automatic layout selection
- **5 Export Formats**: Word / PDF / PPT / TXT / Markdown
- **Fully Local**: Ollama + SQLite, no internet required, zero data leakage risk
- **Real-time Streaming**: SSE technology for character-by-character output

---

## Feature Overview

| Module                       | Feature              | Description                                                                                                          |
| ---------------------------- | -------------------- | -------------------------------------------------------------------------------------------------------------------- |
| **Article Generation**       | Multi-style writing  | Literary / Shanghai Gaokao Essay / Xiaohongshu Viral / WeChat Official Account / Toutiao Headlines / AI Drama Script |
| **PPT Generation**           | Multi-layout slides  | 6 auto-matched layouts: bullets, stats, comparison, timeline, quote, grid                                            |
| **Poetry Creation**          | Classical Chinese    | 5-char/7-char quatrains & regulated verse, with character count validation and auto-retry                            |
| **Text Polishing**           | Content refinement   | Improve writing quality and readability, with original text comparison view                                          |
| **Multilingual Translation** | 6 languages          | Chinese / English / Japanese / Korean / French / German, with comparison view                                        |
| **Text Summarization**       | Key point extraction | Automatically generate structured summaries from long texts                                                          |
| **File Upload**              | 8 formats            | PDF / Word / TXT / Markdown / CSV / JSON / XML / HTML (max 10MB)                                                     |
| **Multi-format Export**      | 5 formats            | Word(.docx) / PDF(.pdf) / PPT(.pptx) / TXT(.txt) / Markdown(.md)                                                     |
| **History**                  | Database persistence | SQLite storage, keyword search, survives browser changes                                                             |
| **User Authentication**      | Registration/Login   | JWT-based authentication with user isolation                                                                         |
| **Custom Styles**            | Create/Edit/Delete   | User-defined writing style templates with custom prompts                                                             |
| **Text Quality Scoring**     | Four dimensions      | Readability/vocabulary diversity/sentence length/structure scoring (0-100)                                            |
| **Long-form Writing**        | Chapter-based        | Outline generation → chapter expansion → final assembly                                                              |

---

## PPT Generation System

The PPT feature supports one-click generation from topic to finished presentation.

### Theme Templates

| Template                 | Color Scheme     | Use Case                           |
| ------------------------ | ---------------- | ---------------------------------- |
| Business Blue (business) | Blue tones       | Business reports, work summaries   |
| Minimal Gray (minimal)   | Gray-white tones | Academic presentations, tech talks |
| Fresh Green (green)      | Green tones      | Environmental topics, education    |
| Warm Tones (warm)        | Orange-red tones | Creative showcases, team sharing   |

### Slide Layouts

| Layout       | Purpose              | Effect                            |
| ------------ | -------------------- | --------------------------------- |
| `bullets`    | General content      | Title + bullet point list         |
| `stats`      | Data display         | Large number cards side by side   |
| `comparison` | Comparative analysis | Two-column layout with divider    |
| `timeline`   | Timeline             | Horizontal axis with node markers |
| `quote`      | Quotations           | Large quote marks + centered text |
| `grid`       | Multiple items       | Adaptive 2-3 column card grid     |

AI automatically annotates the best layout for each slide, with optional Bing image search for auto-illustration.

---

## Tech Stack

### Backend

| Technology             | Description                                   |
| ---------------------- | --------------------------------------------- |
| Python 3.10+           | Programming language                          |
| FastAPI                | Web framework                                 |
| Pydantic               | Data validation and serialization             |
| Uvicorn                | ASGI server                                   |
| httpx                  | Async HTTP client (Ollama API calls)          |
| SQLAlchemy + aiosqlite | Async ORM with SQLite database                |
| python-docx            | Word document generation and export           |
| fpdf2                  | PDF document generation and export            |
| python-pptx            | PowerPoint presentation generation and export |
| PyPDF2                 | PDF file parsing                              |
| python-multipart       | File upload support                           |
| uv                     | Dependency management tool                    |

### Frontend

| Technology     | Description                  |
| -------------- | ---------------------------- |
| React 19       | UI framework                 |
| TypeScript     | Type-safe JavaScript         |
| Vite 8         | Build tool and dev server    |
| Axios          | HTTP request library         |
| react-markdown | Markdown rendering component |

### LLM

| Technology | Description                            |
| ---------- | -------------------------------------- |
| Ollama     | Local LLM runtime                      |
| qwen3.5:9b | Default model (switchable in settings) |
| Multi-Provider | Ollama (default) / OpenAI / DeepSeek / Qwen, unified abstraction layer |

---

## User Experience

### Editing & Interaction

- **Result Editing**: Modify AI-generated content before export
- **Regenerate**: "Try Another" button to generate alternative results with the same parameters
- **Comparison View**: Side-by-side comparison of original vs. polished/translated text
- **Copy Feedback**: One-click copy to clipboard with success/failure notification
- **Character Counter**: Real-time character count in the input area
- **Retry on Failure**: Retry button appears after request failures

### Personalization

- **Dark Mode**: Three-state toggle — Follow System / Light / Dark
- **Model Parameters**: Settings panel for custom model name and temperature
- **Prompt Templates**: Save/load/delete frequently used writing instructions
- **Unsplash Images**: Enter API Key in settings to enable high-quality slide images

### Keyboard Shortcuts

| Shortcut     | Function               |
| ------------ | ---------------------- |
| `Ctrl+Enter` | Submit request         |
| `Esc`        | Stop generation        |
| `Ctrl+S`     | Intercept browser save |

### Mobile Responsive

- Sidebar auto-collapses below 768px, controlled by hamburger menu
- Submission disabled with guidance prompt when Ollama is offline

---

## Backend Capabilities

- **Structured Logging**: Records method, path, status code, and duration for every request
- **IP Rate Limiting**: AI generation endpoints limited to 10 requests per IP per minute
- **CORS**: Cross-origin access enabled for frontend dev server
- **Health Check**: `GET /api/health` for real-time service status
- **Database Persistence**: History stored in SQLite, independent of browser cache
- **Multi-LLM Provider**: Supports Ollama, OpenAI, DeepSeek, and Qwen, switchable via environment variables
- **User Authentication**: JWT HS256 + bcrypt, 72-hour token expiry
- **Custom Styles**: Users can create and manage custom writing style templates

---

## Quick Start

### Prerequisites

1. **Python 3.10+**
2. **Node.js 18+**
3. **uv**: Python dependency management tool ([installation docs](https://docs.astral.sh/uv/))
4. **Ollama**: Local LLM runtime ([download](https://ollama.ai/))

### 1. Start Ollama and Pull Model

```bash
ollama serve
ollama pull qwen3.5:9b
```

### 2. Start Backend

```bash
cd backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

API documentation: http://localhost:8000/docs

### 3. Start Frontend

```bash
cd frontend
npm install
npm run dev
```

Visit: http://localhost:5173

---

## Project Structure

```
my_first/
├── backend/                    # Backend (Python FastAPI)
│   ├── main.py                 # App entry point, FastAPI instance, CORS, SPA hosting, health check, model list
│   ├── db.py                   # SQLite + SQLAlchemy async database config (with lightweight migration)
│   ├── logging_config.py       # Structured logging configuration
│   ├── models/
│   │   ├── schemas.py          # Pydantic data model definitions
│   │   ├── history.py          # History record ORM model (with user_id FK)
│   │   ├── user.py             # User ORM model (username + hashed_password)
│   │   └── custom_style.py     # Custom style ORM model (name, slug, prompt_template)
│   ├── routers/
│   │   ├── writing.py          # Writing API routes (stream/process/refine/outline/expand-chapter/upload/export-*)
│   │   ├── history.py          # History CRUD API routes (user-isolated)
│   │   ├── styles.py           # Custom style CRUD API routes
│   │   ├── auth.py             # User auth API routes (register/login/me)
│   │   └── analysis.py         # Text quality analysis API routes
│   ├── middleware/
│   │   ├── __init__.py         # Request logging middleware
│   │   └── rate_limit.py       # IP rate limiting middleware
│   ├── services/
│   │   ├── llm_provider.py     # Multi-LLM Provider abstraction (Ollama/OpenAI/DeepSeek/Qwen)
│   │   ├── ollama_client.py    # Ollama Chat API client (legacy, used for poetry validation)
│   │   ├── auth.py             # JWT authentication service (bcrypt + HS256, 72h expiry)
│   │   ├── text_analysis.py    # Algorithmic text quality scoring (readability 0-100)
│   │   ├── file_parser.py      # File text extraction service
│   │   ├── docx_export.py      # Word document export service
│   │   ├── pdf_export.py       # PDF document export service
│   │   ├── pptx_export.py      # PPT presentation export service (6 layouts)
│   │   └── unsplash.py         # Image search service (Bing / Unsplash)
│   ├── prompts/
│   │   └── writing.py          # 15 writing prompt templates
│   ├── data/                   # SQLite database file directory
│   └── pyproject.toml          # Project configuration and dependencies
├── frontend/                   # Frontend (React + TypeScript + Vite)
│   └── src/
│       ├── App.tsx             # Root component, global state, theme, auth, standard/long-form mode
│       ├── components/
│       │   ├── WritingForm.tsx  # Task selection, text input, tone control, word count target, advanced options
│       │   ├── ResultPanel.tsx  # Result rendering, quick-start cards, word count progress, overflow menu, exports
│       │   ├── HistoryPanel.tsx # History records, keyword search, style label display
│       │   ├── SettingsPanel.tsx# Model/parameter settings panel
│       │   ├── AuthPanel.tsx   # User auth panel (login/register/logout)
│       │   ├── QualityPanel.tsx# Text quality scoring panel (4 dimensions, 0-100)
│       │   ├── LongFormPanel.tsx# Long-form chapter-based generation (outline → expand → merge)
│       │   ├── StyleEditor.tsx # Custom style editor
│       │   └── ConfirmDialog.tsx# Confirmation dialog component
│       ├── services/
│       │   ├── api.ts          # API functions (streaming/export/custom style CRUD)
│       │   ├── auth.ts         # JWT auth client (localStorage + Bearer injection)
│       │   ├── history.ts      # Backend history API client
│       │   └── templates.ts    # Prompt template management
│       └── types/
│           └── index.ts        # TypeScript type definitions and constants
├── tests/                      # Test directory
├── docs/                       # Project documentation (Chinese/English bilingual)
├── Dockerfile                  # Multi-stage build (Node frontend → Python backend)
├── docker-compose.yml          # app + ollama service orchestration
└── start.bat / start.command   # One-click startup scripts (Windows/macOS)
```

---

## Version History

| Version | Date       | Major Changes                                                                  |
| ------- | ---------- | ------------------------------------------------------------------------------ |
| v1.5.0  | 2026-03-26 | Quick-start cards, token count animation, word count target, tone control, streamlined action bar |
| v1.4.0  | 2026-03-26 | CSS design token system, auto dark mode, WAI-ARIA accessibility, shared animations |
| v1.3.1  | 2026-03-23 | Unified version numbering, PPT generation stable release                       |
| v1.3.0  | 2026-03-23 | PPT multi-layout system: 6 slide layout types + AI auto-layout annotation      |
| v1.2.0  | 2026-03-22 | PPT export: 4 theme templates + Unsplash/Bing image integration                |
| v1.1.0  | 2026-03-22 | Result editing, dark mode, database persistence, rate limiting, settings panel |
| v1.0.0  | 2026-03-21 | Core writing features, streaming output, file upload, Word export              |

See [CHANGELOG_En.md](./CHANGELOG_En.md) for detailed release notes.

---

## License

MIT License
