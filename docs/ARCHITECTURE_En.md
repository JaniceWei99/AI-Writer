# AI Writing Assistant — Project Architecture Document

## Overall Architecture

The AI Writing Assistant is an intelligent writing tool powered by a **local large language model (Ollama)**, built with a decoupled front-end/back-end architecture:

```
┌─────────────────┐      SSE / HTTP       ┌─────────────────┐      HTTP       ┌───────────┐
│                 │  ◄──────────────────►  │                 │  ◄───────────►  │           │
│  React 前端      │   localhost:8000      │  FastAPI 后端     │  localhost:11434│  Ollama   │
│  (Vite + TS)    │                       │  (Python 3.10+)  │                │  qwen3.5  │
│  :5173          │                       │  :8000           │                │  :11434   │
└─────────────────┘                       └─────────────────┘                └───────────┘
```

| Layer             | Tech Stack                                          | Responsibilities                                                                                                                                |
| ----------------- | --------------------------------------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------- |
| **Front-end**     | React 19 + TypeScript + Vite                        | User interaction, task selection, streaming result display, history management, dark mode, settings panel                                       |
| **Back-end**      | FastAPI + Pydantic + httpx + SQLAlchemy + aiosqlite | Route dispatching, prompt construction, Ollama invocation, file parsing, document export, history persistence, logging/rate-limiting middleware |
| **Database**      | SQLite (backend/data/app.db)                        | Persistent history storage                                                                                                                      |
| **Model Service** | Ollama (qwen3.5:9b)                                 | Local large language model inference                                                                                                            |

---

## Directory Structure

```
my_first/
├── backend/
│   ├── main.py                  # FastAPI application entry point, CORS config, SPA hosting, /api/health, /api/models
│   ├── db.py                    # SQLAlchemy async engine + session factory, SQLite at data/app.db (with lightweight migration)
│   ├── logging_config.py        # Structured logging config (console + file rotation)
│   ├── pyproject.toml           # Python dependency management (uv)
│   ├── data/
│   │   └── app.db               # SQLite database file (auto-created at runtime)
│   ├── models/
│   │   ├── schemas.py           # Pydantic data models: TaskType enum, request/response models (incl. model/temperature)
│   │   ├── history.py           # SQLAlchemy ORM model: HistoryRecord (with user_id FK)
│   │   ├── user.py              # SQLAlchemy ORM model: User (username + hashed_password)
│   │   └── custom_style.py      # SQLAlchemy ORM model: CustomStyle (name, slug, prompt_template)
│   ├── routers/
│   │   ├── writing.py           # Writing API routes: stream / process / refine / outline / expand-chapter / upload / export-*
│   │   ├── history.py           # History CRUD routes: GET / POST / DELETE (user-isolated)
│   │   ├── styles.py            # Custom style CRUD routes: GET / POST / PUT / DELETE
│   │   ├── auth.py              # User auth routes: register / login / me
│   │   └── analysis.py          # Text quality analysis routes: POST /quality
│   ├── middleware/
│   │   ├── __init__.py          # RequestLoggingMiddleware (logs request method/path/status code/duration)
│   │   └── rate_limit.py        # RateLimitMiddleware (IP sliding-window rate limiting, 10 req/min for AI endpoints)
│   ├── prompts/
│   │   └── writing.py           # 15 prompt templates (9 styles + outline/chapter/refine/poetry/PPT) and poetry validation
│   ├── services/
│   │   ├── llm_provider.py      # Multi-LLM Provider abstraction (Ollama/OpenAI/DeepSeek/Qwen/GLM/MM)
│   │   ├── ollama_client.py     # Ollama Chat API client (legacy, used for poetry validation path)
│   │   ├── auth.py              # JWT auth service (bcrypt + HS256, 72h expiry)
│   │   ├── text_analysis.py     # Algorithmic text quality scoring (readability 0-100)
│   │   ├── file_parser.py       # File text extraction (PDF / DOCX / plain text)
│   │   ├── docx_export.py       # Markdown → Word document conversion
│   │   ├── pdf_export.py        # Markdown → PDF document conversion (fpdf2, Chinese font support)
│   │   ├── pptx_export.py       # Markdown → PPTX presentation conversion (python-pptx, 4 themes, 6 layouts)
│   │   └── unsplash.py          # Image search service (Unsplash → Bing → picsum fallback)
│   └── tests/
│       ├── test_routers.py      # Route endpoint tests
│       ├── test_file_parser.py  # File parsing tests
│       ├── test_prompts.py      # Prompt construction tests
│       ├── test_pptx_export.py  # PPTX export tests
│       └── test_schemas.py      # Data model tests
├── frontend/
│   └── src/
│       ├── main.tsx             # React entry point
│       ├── App.tsx              # Root component: global state, streaming, dark mode, auth, standard/long-form mode
│       ├── App.css              # Global styles + dark mode variables + responsive media queries
│       ├── index.css            # CSS design token system (122 custom properties + dark mode + shared animations + a11y)
│       ├── components/
│       │   ├── WritingForm.tsx   # Task selection, text input (word count/target), tone control, advanced options, quick-start
│       │   ├── WritingForm.css   # Form styles + offline banner
│       │   ├── ResultPanel.tsx   # Markdown rendering, quick-start cards, word count progress, overflow menu, exports, comparison
│       │   ├── ResultPanel.css   # Result panel styles + comparison view layout
│       │   ├── HistoryPanel.tsx  # History list: search, filter, style labels, delete, clear (back-end API)
│       │   ├── AuthPanel.tsx     # User auth panel (login/register/logout)
│       │   ├── AuthPanel.css     # Auth panel styles
│       │   ├── QualityPanel.tsx  # Text quality scoring panel (4 dimensions, 0-100)
│       │   ├── QualityPanel.css  # Scoring panel styles
│       │   ├── LongFormPanel.tsx # Long-form chapter-based generation (outline → expand → merge)
│       │   ├── LongFormPanel.css # Long-form panel styles
│       │   ├── StyleEditor.tsx   # Custom style editor (CRUD)
│       │   ├── StyleEditor.css   # Style editor styles
│       │   ├── ConfirmDialog.tsx # Generic confirmation dialog component
│       │   ├── ConfirmDialog.css # Confirmation dialog styles
│       │   ├── SettingsPanel.tsx # Model name + temperature + Provider info settings panel
│       │   └── SettingsPanel.css # Settings panel styles
│       ├── services/
│       │   ├── api.ts           # Axios client + API functions (streaming/non-streaming/upload/export/custom style CRUD)
│       │   ├── auth.ts          # JWT auth client (localStorage + Bearer injection)
│       │   ├── history.ts       # Back-end history API wrapper (auto-injects Auth Header)
│       │   └── templates.ts     # Prompt template management (save/load/delete, localStorage)
│       └── types/
│           └── index.ts         # TypeScript type definitions, TaskType constants, style/language options, STYLE_LABELS
└── docs/                        # Documentation directory (Chinese/English bilingual)
```

---

## Back-end Module Details

### `main.py` — Application Entry Point

- Creates a FastAPI instance (title `AI 写作助手`, version `1.5.0`)
- Uses a `lifespan` context manager to initialize the database on startup (`init_db()`)
- Configures CORS middleware to allow cross-origin requests from the front-end dev server:
  - `http://localhost:5173` (Vite dev server)
  - `http://localhost:3000` (fallback port)
- Mounts request logging middleware (`RequestLoggingMiddleware`) and IP rate-limiting middleware (`RateLimitMiddleware`)
- Mounts five route modules: `writing_router`, `history_router`, `styles_router`, `auth_router`, `analysis_router`
- Provides a health-check endpoint `GET /api/health` that returns the service status, provider info, and current model name
- Provides a model listing endpoint `GET /api/models` that returns all available models (auto-filters non-generation models)
- Supports SPA mode: if `frontend/dist` exists, automatically serves static files with SPA fallback
- Returns 404 for `/sw.js` to unregister stale Service Workers

### `db.py` — Database Configuration

- Uses SQLAlchemy async engine + aiosqlite; database file is located at `backend/data/app.db`
- Provides `init_db()` to create all tables
- Provides `get_session()` async session generator for dependency injection

### `logging_config.py` — Logging Configuration

- Structured log output (console formatted)
- Supplies a logger instance for the request logging middleware

### `models/schemas.py` — Data Models

| Model                 | Description                                                                                                                           |
| --------------------- | ------------------------------------------------------------------------------------------------------------------------------------- |
| `TaskType(str, Enum)` | Task type enum: `generate`, `polish`, `translate`, `summarize`                                                                        |
| `WritingRequest`      | Writing request body: `task_type`, `content`, `style`, `target_lang`, `attachment_text`, `model` (optional), `temperature` (optional) |
| `WritingResponse`     | Writing response body: `task_type`, `result` (generated text), `token_count`                                                          |
| `ExportRequest`       | Export request body: `content` (Markdown content), `title` (document title)                                                           |
| `ExportPptxRequest`   | PPTX export request body: `content`, `title`, `template` (theme template), `with_images` (whether to include images), `unsplash_key`  |
| `HistoryCreate`       | History creation request: `task_type`, `content`, `result`, `style`, `token_count`                                                    |
| `HistoryOut`          | History response: includes full fields such as `id`, `created_at`, etc.                                                               |

### `models/history.py` — ORM Model

SQLAlchemy ORM model `HistoryRecord`, mapped to the `history` table:

| Field         | Type         | Description                    |
| ------------- | ------------ | ------------------------------ |
| `id`          | Integer (PK) | Auto-increment primary key     |
| `user_id`     | Integer (FK) | References users.id, nullable  |
| `task_type`   | String       | Task type                      |
| `content`     | Text         | Input content                  |
| `result`      | Text         | Generated result               |
| `style`       | String       | Writing style                  |
| `token_count` | Integer      | Token count                    |
| `created_at`  | DateTime     | Creation timestamp (UTC)       |

### `models/user.py` — User ORM Model

SQLAlchemy ORM model `User`, mapped to the `users` table:

| Field             | Type         | Description                    |
| ----------------- | ------------ | ------------------------------ |
| `id`              | Integer (PK) | Auto-increment primary key     |
| `username`        | String(64)   | Unique, indexed                |
| `hashed_password` | String(128)  | bcrypt hash                    |
| `created_at`      | DateTime     | Creation timestamp (UTC)       |

### `models/custom_style.py` — Custom Style ORM Model

SQLAlchemy ORM model `CustomStyle`, mapped to the `custom_styles` table:

| Field             | Type         | Description                         |
| ----------------- | ------------ | ----------------------------------- |
| `id`              | Integer (PK) | Auto-increment primary key          |
| `name`            | String(64)   | Display name                        |
| `slug`            | String(64)   | Unique identifier (indexed)         |
| `prompt_template` | Text         | Prompt template, must contain `{content}` |
| `description`     | String(256)  | Description                         |
| `created_at`      | DateTime     | Creation timestamp (UTC)            |
| `updated_at`      | DateTime     | Last update timestamp (UTC)         |

### `routers/writing.py` — Writing API Routes

Provides nine core endpoints, all under the prefix `/api/writing`:

| Endpoint            | Method | Function                                                                                                                                   |
| ------------------- | ------ | ------------------------------------------------------------------------------------------------------------------------------------------ |
| `/upload`           | POST   | Receives an uploaded file, calls `file_parser.extract_text()` to extract text, returns filename, text content, and character count         |
| `/process`          | POST   | Non-streaming writing processing; builds a prompt and calls `llm_provider.generate()`, returns the complete result                         |
| `/stream`           | POST   | Streaming writing processing; returns tokens incrementally in SSE format. Poetry requests follow a special path                            |
| `/refine`           | POST   | Streaming refinement of existing text; supports iterative improvements                                                                     |
| `/outline`          | POST   | Streaming long-form outline generation; returns a structured chapter outline                                                                |
| `/expand-chapter`   | POST   | Streaming chapter expansion; expands a single chapter from the outline into full content                                                    |
| `/export-docx`      | POST   | Accepts Markdown text, converts to a Word document, returns as a binary stream                                                             |
| `/export-pdf`       | POST   | Accepts Markdown text, converts to a PDF document (fpdf2, Chinese support), returns as a binary stream                                     |
| `/export-pptx`      | POST   | Accepts a Markdown PPT outline, converts to a PPTX presentation (supports theme templates and Unsplash images), returns as a binary stream |

### `routers/history.py` — History Routes

Provides four CRUD endpoints, all under the prefix `/api/history`:

| Endpoint | Method | Function                                                           |
| -------- | ------ | ------------------------------------------------------------------ |
| `/`      | GET    | Retrieves the history list; supports keyword search and pagination |
| `/`      | POST   | Creates a new history record; returns 201                          |
| `/{id}`  | DELETE | Deletes the history record with the specified ID; returns 204      |
| `/`      | DELETE | Clears all history records; returns 204                            |

### `routers/styles.py` — Custom Style Routes

Provides full CRUD endpoints for custom writing styles, all under the prefix `/api/styles`:

| Endpoint | Method | Function                                                           |
| -------- | ------ | ------------------------------------------------------------------ |
| `/`      | GET    | Retrieves all custom styles                                        |
| `/`      | POST   | Creates a new custom style; returns 201                            |
| `/{id}`  | PUT    | Updates the custom style with the specified ID                     |
| `/{id}`  | DELETE | Deletes the custom style with the specified ID; returns 204        |

### `routers/auth.py` — Authentication Routes

Provides user registration and login endpoints, all under the prefix `/api/auth`:

| Endpoint    | Method | Function                                                                           |
| ----------- | ------ | ---------------------------------------------------------------------------------- |
| `/register` | POST   | Registers a new user; validates username uniqueness, hashes password with bcrypt   |
| `/login`    | POST   | User login; verifies credentials, returns JWT token (HS256, 72h expiry)           |
| `/me`       | GET    | Returns current user info; requires valid Bearer token                             |

### `routers/analysis.py` — Text Analysis Routes

Provides text quality analysis endpoints, all under the prefix `/api/analysis`:

| Endpoint   | Method | Function                                                                                     |
| ---------- | ------ | -------------------------------------------------------------------------------------------- |
| `/quality` | POST   | Accepts text content, returns a quality score (0-100) across 4 dimensions (algorithmic, no LLM) |

### `middleware/` — Middleware

| Middleware                 | Description                                                                                                                                                                      |
| -------------------------- | -------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `RequestLoggingMiddleware` | Logs the method, path, status code, and processing duration of each request                                                                                                      |
| `RateLimitMiddleware`      | IP sliding-window rate limiting; AI generation endpoints (`/api/writing/process`, `/api/writing/stream`) are limited to 10 requests per IP per minute; returns 429 when exceeded |

**Poetry Special Handling Logic** (within the `/stream` endpoint):

1. Uses `is_poetry_request()` to detect whether the user input contains poetry-related keywords
2. If it is a poetry request, switches to **non-streaming generation** + **retry with validation** (up to 3 attempts)
3. Calls `validate_poetry()` to verify that the number of Chinese characters per line conforms to metrical requirements
4. Once validation passes, sends the complete text character by character as SSE events

### `prompts/writing.py` — Prompt Templates

Contains **9 prompt templates** covering a variety of writing scenarios:

| Template Constant     | Applicable Scenario                             | Trigger Condition                                      |
| --------------------- | ----------------------------------------------- | ------------------------------------------------------ |
| `GENERATE_PROMPT`     | General article generation                      | `task_type=generate`, default style                    |
| `POETRY_PROMPT`       | Classical Chinese poetry composition            | `task_type=generate`, content contains poetry keywords |
| `POLISH_PROMPT`       | Text polishing and rewriting                    | `task_type=polish`                                     |
| `TRANSLATE_PROMPT`    | Multi-language translation                      | `task_type=translate`                                  |
| `SUMMARIZE_PROMPT`    | Text summarization                              | `task_type=summarize`                                  |
| `XIAOHONGSHU_PROMPT`  | Xiaohongshu (Little Red Book) viral copywriting | `style=xiaohongshu`                                    |
| `GONGZHONGHAO_PROMPT` | WeChat Official Account long-form articles      | `style=gongzhonghao`                                   |
| `TOUTIAO_PROMPT`      | Toutiao (Today's Headlines) articles            | `style=toutiao`                                        |
| `AI_DRAMA_PROMPT`     | AI short drama scripts                          | `style=ai_drama`                                       |
| `PPT_PROMPT`          | Presentation outlines (with 6 layout markers)   | `style=ppt`                                            |

**Core Functions**:

- `build_prompt()` — Selects a template based on task type and style, injects content and parameters, and automatically appends attachment content
- `is_poetry_request()` — Regex-matches poetry-related keywords
- `validate_poetry()` — Validates poetic meter (extracts Chinese characters, splits by punctuation into lines, checks character count per line)

### `services/llm_provider.py` — Multi-LLM Provider

Unified abstraction layer supporting multiple LLM providers; automatically selects the provider based on the `LLM_PROVIDER` environment variable:

| `LLM_PROVIDER` | Service             | Base URL                              | Default Model        |
| --------------- | ------------------- | ------------------------------------- | -------------------- |
| `ollama`        | Ollama (local)      | `http://localhost:11434`              | `qwen3.5:latest`     |
| `openai`        | OpenAI API          | `https://api.openai.com/v1`          | `gpt-4o-mini`        |
| `deepseek`      | DeepSeek API        | `https://api.deepseek.com/v1`        | `deepseek-chat`      |
| `qwen`          | Qwen (Alibaba)      | `https://dashscope.aliyuncs.com/compatible-mode/v1` | `qwen-plus`    |
| `glm`           | GLM (Zhipu AI)      | `https://open.bigmodel.cn/api/paas/v4` | `glm-4-flash`     |
| `mm`            | MiniMax API         | `https://api.minimax.chat/v1`        | `MiniMax-Text-01`    |

**Core Functions**:

| Function             | Mode          | Description                                                                        |
| -------------------- | ------------- | ---------------------------------------------------------------------------------- |
| `generate()`         | Non-streaming | Sends a chat completion request, returns complete text and token count              |
| `generate_stream()`  | Streaming     | Sends a chat completion request, returns an `AsyncGenerator` that yields tokens    |
| `list_models()`      | —             | Retrieves available model list from the provider                                   |
| `get_default_model()`| —             | Returns the default model name for the current provider                            |
| `get_provider_info()`| —             | Returns provider name and base URL information                                     |

**Ollama-Specific Optimizations**:

- Uses Chat API (`/api/chat`) instead of Generate API, converting prompts to `system` + `user` messages via `_prompt_to_messages()`
- Model listing filters out non-generation models (embedding models, etc.)
- Timeout: 300 seconds (longer for local inference)

### `services/ollama_client.py` — Ollama Client (Legacy)

Legacy client kept for the poetry validation path. Communicates with the local Ollama service via httpx:

- Uses `/api/chat` (not `/api/generate`), converts prompt into `system` + `user` messages
- Timeout: 300 seconds
- Sets `think=False` to disable chain-of-thought output

### `services/auth.py` — Authentication Service

JWT-based user authentication service:

- Password hashing: bcrypt via `passlib`
- Token generation: HS256 algorithm, 72-hour expiry
- Token verification: Decodes and validates JWT, returns the current user
- Provides `get_current_user()` dependency for protected routes

### `services/text_analysis.py` — Text Quality Analysis

Algorithmic text quality scoring (no LLM required):

- Accepts text content and returns a score from 0 to 100
- Evaluates across 4 dimensions: readability, structure, vocabulary richness, and coherence
- Pure algorithmic analysis — fast, deterministic, and free

### `services/file_parser.py` — File Parsing

| File Type        | Parsing Method                           | Dependency  |
| ---------------- | ---------------------------------------- | ----------- |
| `.pdf`           | Extracts text page by page               | PyPDF2      |
| `.docx` / `.doc` | Extracts paragraph text                  | python-docx |
| Plain text       | Attempts multiple encodings for decoding | Built-in    |

- Maximum file size: **10 MB**
- Plain text encoding attempt order: `utf-8` → `gbk` → `gb2312` → `latin-1`

### `services/docx_export.py` — Word Document Export

Converts Markdown text to a `.docx` file (generated in memory):

| Markdown Element  | Conversion Rule                   |
| ----------------- | --------------------------------- |
| `# / ## / ###`    | Mapped to Word heading levels 1–3 |
| `- / * / +` lists | Word unordered list               |
| `1. 2. 3.` lists  | Word ordered list                 |
| `>` blockquote    | Left indent + italic + gray font  |
| `---` / `***`     | Centered gray divider line        |
| `**bold**`        | Word bold                         |
| `*italic*`        | Word italic                       |

### `services/pdf_export.py` — PDF Document Export

Converts Markdown text to a `.pdf` file (generated in memory), based on fpdf2:

- Supports Chinese font rendering (auto-detects system Chinese fonts)
- Parses Markdown headings, lists, blockquotes, dividers, and other elements
- Returns an `io.BytesIO` byte stream

### `services/pptx_export.py` — PPTX Presentation Export

Converts a Markdown PPT outline to a `.pptx` file (generated in memory), based on python-pptx:

- **Markdown Parsing**: Recognizes `## Title` (slide title), `- Bullet points`, `> Speaker notes`, `---` (separators), `[layout: layout_name]` (layout markers)
- **Slide Types**: Automatically distinguishes cover slides, content slides, and closing slides (detects keywords like "谢谢", "致谢", "Q&A", etc.)
- **6 Layouts** (content slides select based on `[layout: xxx]` markers):
  - `bullets` — Default bullet-point list (title + bullet points)
  - `stats` — Key data display (large numbers in rounded cards + labels, multi-column side-by-side)
  - `comparison` — Two-column comparison (column headers + divider line + dual-column content)
  - `timeline` — Horizontal timeline (node dots + labels above + descriptions below)
  - `quote` — Quote/highlight (decorative large quotation marks + centered text + attribution)
  - `grid` — Grid cards (adaptive 2–3 columns, with top accent lines)
- **4 Theme Templates**:
  - `business` (Business Blue) — Default
  - `minimal` (Minimalist Gray)
  - `green` (Fresh Green)
  - `warm` (Warm Tones)
- **Image Support**: Optionally adds images to content slides (right-side layout); images are provided by the Unsplash / Bing service
- **Speaker Notes**: Embedded in the notes section of each slide
- **Slide Numbers**: Automatically added as page numbers

### `services/unsplash.py` — Unsplash Image Search

Provides automatic image sourcing for PPT slides by searching relevant images via the Unsplash API:

- `search_image(query, api_key)` — Searches for a single image, automatically strips Markdown formatting from the title
- `fetch_images_for_slides(slides, api_key)` — Concurrently fetches multiple images (`asyncio.gather`)
- Gracefully returns empty results when no API key is provided, without affecting PPTX generation
- Request timeout: 10 seconds

---

## Front-end Module Details

### `App.tsx` — Root Component

The central hub for global state management and business logic orchestration:

| State         | Type            | Purpose                                     |                                |
| ------------- | --------------- | ------------------------------------------- |                                |
| `result`      | `string`        | Currently displayed generated result text   |                                |
| `loading`     | `boolean`       | Whether streaming generation is in progress |                                |
| `tokenCount`  | `number`        | Number of tokens received                   |                                |
| `error`       | `string`        | Error message                               |                                |
| `online`      | `boolean \      | null`                                       | Back-end service online status |
| `history`     | `HistoryItem[]` | History record list                         |                                |
| `activeId`    | `string`        | Currently selected history record ID        |                                |
| `sidebarOpen` | `boolean`       | Mobile sidebar expanded state               |                                |
| `theme`       | `string`        | Dark mode state (system/light/dark)         |                                |

**Core Logic**:

1. On initialization, calls `healthCheck()` to detect back-end status and loads history from the back-end API
2. `handleSubmit` — Initiates a streaming request, progressively accumulating tokens via callbacks
3. `handleStop` — Aborts an in-progress streaming request via `AbortController`
4. `handleRegenerate` — Regenerates using the previous request parameters
5. After streaming completes, automatically saves the result to the back-end database
6. Dark mode three-state cycle: Follow System → Light → Dark, with preference persisted to localStorage
7. Mobile sidebar controlled via a hamburger menu button for collapse/expand
8. Keyboard shortcut listeners: Ctrl+Enter to submit, Esc to stop generation, Ctrl+S intercepted

### `components/WritingForm.tsx` — Writing Form

- **Task Type Switching**: Displays four task types as tabs
- **Text Input Area**: Switches placeholder text based on task type; real-time word count displayed at the bottom
- **File Upload**: Calls `/api/writing/upload` to extract file text, used as attachment reference
- **Style Selection**: 9 style options
- **Target Language**: Displayed for translation tasks; supports 6 languages
- **Offline Fallback**: Receives an `online` prop; when the service is offline, disables the submit button and shows a red banner with guidance

### `components/ResultPanel.tsx` — Result Panel

- Uses react-markdown to render generated results
- **Result Editing**: Supports edit/save/cancel to modify generated content before export
- **Comparison View**: Side-by-side comparison of original text and generated result for polish/translate tasks
- **One-Click Copy**: Success/failure feedback; button text temporarily changes to "Copied" / "Copy Failed"
- **Multi-Format Export**: Word (.docx), PDF (.pdf), PPT (.pptx), Plain Text (.txt), Markdown (.md)
- **"Try Another" Button**: Regenerates a different result using the same parameters
- **"Retry" Button**: Displayed after a request failure
- Displays token count and loading status

### `components/HistoryPanel.tsx` — History Panel

- Displays the history record list in reverse chronological order (data sourced from the back-end API)
- Supports keyword search (matches content and results)
- Clicking a history entry restores the corresponding generated result
- Supports individual deletion and one-click clear (clearing triggers a ConfirmDialog for secondary confirmation)

### `components/ConfirmDialog.tsx` — Confirmation Dialog

- A generic secondary confirmation component for destructive operations such as clearing history
- Accepts `message`, `onConfirm`, and `onCancel` props

### `components/SettingsPanel.tsx` — Settings Panel

- Model name input field (custom Ollama model)
- Temperature parameter slider (0–2, step 0.1)
- Unsplash Access Key input field (for PPT images, password-type to protect privacy)
- Setting values are passed back to the App component via props

### `services/api.ts` — API Client

HTTP requests wrapped with Axios; base URL configured via `VITE_API_BASE` env var (empty for same-origin proxy in dev mode), timeout 120 seconds:

| Function                                                          | Description                                                                                                  |
| ----------------------------------------------------------------- | ------------------------------------------------------------------------------------------------------------ |
| `processWriting(req)`                                             | Non-streaming request                                                                                        |
| `streamWriting(req, onToken, onDone, onError)`                    | Streaming request; uses native `fetch()` + `ReadableStream` to read SSE events                               |
| `healthCheck()`                                                   | Health check                                                                                                 |
| `uploadFile(file)`                                                | File upload                                                                                                  |
| `downloadDocx(content, title)`                                    | Export to Word; preferentially uses the File System Access API                                               |
| `downloadPdf(content, title)`                                     | Export to PDF; preferentially uses the File System Access API                                                |
| `downloadPptx(content, title, template, withImages, unsplashKey)` | Export to PPTX; supports theme templates and Unsplash images; timeout is 300 seconds when images are enabled |

> **Note**: `streamWriting` uses native `fetch()` instead of Axios because Axios does not support streaming response body reading.

### `services/history.ts` — History Management

Back-end API-based history management (data persisted in SQLite):

- Provides four async functions: `getHistory()` / `addHistory()` / `removeHistory()` / `clearHistory()`
- All operations call the `/api/history` endpoint via axios
- Auto-injects Authorization Bearer token (if user is logged in)
- History records are permanently retained, stored by the back-end SQLite database

### `services/auth.ts` — Authentication Client

JWT-based front-end authentication client:

- Stores JWT token in `localStorage`
- Provides `login()` / `register()` / `getMe()` / `logout()` functions
- Automatically injects `Authorization: Bearer <token>` header into all API requests
- Token is cleared on logout or 401 response

### `services/templates.ts` — Prompt Template Management

localStorage-based template persistence scheme:

- Storage key: `writing_templates`
- Provides three methods: `getTemplates()` / `saveTemplate()` / `deleteTemplate()`
- Templates contain fields such as name, task type, content, and style

---

## Data Flow

### Main Flow: Streaming Writing Generation

```
用户操作                    前端                         后端                        Ollama
  │                         │                            │                           │
  │  1. 选择任务 + 输入内容   │                            │                           │
  │────────────────────────►│                            │                           │
  │                         │  2. POST /api/writing/stream│                           │
  │                         │───────────────────────────►│                            │
  │                         │                            │  3. build_prompt()         │
  │                         │                            │  (选择模板+注入参数)        │
  │                         │                            │  4. POST /api/chat       │
  │                         │                            │  (system+user messages)  │
  │                         │                            │──────────────────────────►│
  │                         │     SSE: data: "token"     │  5. 逐行返回 JSON token    │
  │                         │◄───────────────────────────│◄──────────────────────────│
  │  6. 实时渲染 Markdown    │                            │                           │
  │◄────────────────────────│                            │                           │
  │                         │     SSE: data: [DONE]      │                           │
  │                         │◄───────────────────────────│                           │
  │                         │  7. addHistory() → POST /api/history → SQLite         │
```

### File Upload Flow

```
用户选择文件 → POST /api/writing/upload → file_parser.extract_text()
                                              │
                                    ┌─────────┼─────────┐
                                    │         │         │
                                  PDF       DOCX      纯文本
                                (PyPDF2) (python-docx) (多编码尝试)
                                    │         │         │
                                    └─────────┼─────────┘
                                              │
                                      返回提取的文本 → 填入 attachment_text → 追加到提示词末尾
```

### Word Export Flow

```
用户点击导出 → showSaveFilePicker() 弹窗
                    │
                    ▼
             POST /api/writing/export-docx
                    │
                    ▼
          markdown_to_docx() 内存中转换
                    │
                    ▼
           返回 .docx 二进制流
                    │
              ┌─────┴─────┐
              │           │
        File System    Blob URL
        Access API     回退下载
```

### PPTX Export Flow

```
用户选择"生成PPT"风格 → AI 生成带版式标记的 Markdown PPT 大纲
                              │
                    用户点击"导出 PPT"
                              │
                   ┌──────────┴──────────┐
                   │                     │
             选择主题模板          是否启用配图？
          (business/minimal/       │
           green/warm)        ┌────┴────┐
                              │         │
                             否         是
                              │    Unsplash/Bing
                              │    并发获取图片
                              │         │
                   └──────────┴─────────┘
                              │
                  POST /api/writing/export-pptx
                              │
                   pptx_export.py 内存中转换
                  (解析大纲 → 识别版式标记 →
                   按版式渲染幻灯片 → 嵌入图片)
                              │
                   6 种版式渲染器:
                   bullets / stats / comparison
                   timeline / quote / grid
                              │
                     返回 .pptx 二进制流
                              │
                        Blob URL 下载
```

---

## Key Design Decisions

### 1. SSE Streaming Output

Server-Sent Events are used instead of WebSocket. SSE is unidirectional communication, which fits the "request → streaming response" use case and is simpler to implement. The front-end supports aborting generation via `AbortController`.

### 2. Non-Streaming Poetry Generation + Retry Validation

Poetry requests use non-streaming generation with back-end metrical validation, retrying up to 3 times. This is because streaming output cannot validate the overall format before generation is complete — the full output must be available before character counts can be verified.

### 3. Multi-Encoding File Parsing

Plain text files are decoded by attempting encodings in the order `utf-8 → gbk → gb2312 → latin-1`, covering the most common encoding scenarios for Chinese users.

### 4. SQLite History Persistence

History records were migrated from localStorage to a back-end SQLite database (SQLAlchemy + aiosqlite), enabling cross-device and cross-browser data sharing.

### 5. Prompt Template System

Independent prompt templates are designed for different writing scenarios. Each template embeds platform-specific writing rules and formatting guidelines, and the `style` parameter routes to the corresponding template.

### 6. Word Export Strategy

The front-end preferentially uses `showSaveFilePicker` (allowing the user to choose a save location), with a fallback to Blob URL download. The back-end generates the `.docx` in memory without writing to disk. Filenames are URL-encoded to support Chinese characters.

### 7. IP Rate-Limiting Middleware

A sliding-window algorithm is used to limit the request rate to AI generation endpoints by IP address (10 requests per minute). Only `/api/writing/process` and `/api/writing/stream` are rate-limited; other endpoints such as file upload and export are unaffected.

### 8. Dark Mode Implementation

CSS custom properties (CSS Variables) are used for theme switching, controlled via the `data-theme` attribute. Three-state cycle: Follow System → Light → Dark, with the preference persisted to localStorage.

### 9. PPTX Export Strategy

The back-end generates the `.pptx` file in memory without writing to disk. A Markdown outline format is used as an intermediate representation, which is parsed into structured slide data before generating the presentation. The AI Prompt instructs the LLM to embed `[layout: xxx]` layout markers in titles; the parser extracts these and dispatches to 6 specialized renderers (bullets, stats, comparison, timeline, quote, grid) to achieve diverse layouts. Four preset themes are differentiated by color schemes and font configurations, with automatic detection of cover, content, and closing slides. Unsplash / Bing image sourcing is optional — basic export is unaffected when no API key is provided.

### 12. Multi-LLM Provider Architecture

The `llm_provider.py` module implements a unified abstraction layer that supports 6 LLM providers (Ollama, OpenAI, DeepSeek, Qwen, GLM, MiniMax). Provider selection is controlled via the `LLM_PROVIDER` environment variable, with Ollama as the default. All providers expose the same `generate()` / `generate_stream()` interface, so the upper-layer business logic is completely decoupled from the specific provider. This design allows seamless switching between local and cloud LLM services without modifying any route or prompt code.

### 13. User Authentication System

JWT-based user authentication is implemented with bcrypt password hashing and HS256 token signing (72-hour expiry). The system is designed to be optional — all core writing features work without login. When authenticated, history records are isolated per user via a `user_id` foreign key, enabling multi-user data separation. The front-end stores the JWT in localStorage and automatically injects the Bearer token into API requests.
