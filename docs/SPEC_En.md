# AI Writing Assistant — Technical Specification (Spec)

> This document is a spec-driven specification that contains complete data models, API contracts, component interfaces, business rules, and configuration definitions.
> Frontend and backend code can be generated directly from this specification.

---

## 1. System Overview

| Property | Value |
|----------|-------|
| Project Name | AI Writing Assistant |
| Architecture | Frontend-backend separation, SSE streaming communication |
| Backend | Python 3.10+, FastAPI, Pydantic v2, httpx, SQLAlchemy, aiosqlite, uvicorn |
| Frontend | React 19, TypeScript, Vite 8, Axios, react-markdown |
| LLM Backend | Ollama REST API (localhost:11434) |
| Default Model | qwen3.5:9b |
| Backend Port | 8000 |
| Frontend Port | 5173 (dev) |

---

## 2. Data Models

### 2.1 Enumerations

```
TaskType = "generate" | "polish" | "translate" | "summarize"
```

```
Style = "" | "literary" | "sh_gaokao"
      | "xiaohongshu" | "gongzhonghao" | "toutiao" | "ai_drama" | "ppt"
```

```
TargetLang = "英文" | "中文" | "日文" | "韩文" | "法文" | "德文"
```

### 2.2 Backend Pydantic Models

```yaml
WritingRequest:
  task_type: TaskType          # required
  content: str                 # required
  style: str = ""
  target_lang: str = "英文"
  attachment_text: str = ""
  model: str = ""              # Custom model name; uses default if empty
  temperature: Optional[float] = None  # Generation temperature; uses model default if None

WritingResponse:
  task_type: TaskType
  result: str
  token_count: int = 0

ExportRequest:
  content: str                 # required, Markdown text
  title: str = ""

ExportPptxRequest:
  content: str                 # required, Markdown PPT outline
  title: str = ""
  template: str = "business"   # Theme template: business | minimal | green | warm
  with_images: bool = False    # Whether to add Unsplash images
  unsplash_key: str = ""       # Unsplash API key

HistoryCreate:
  task_type: str               # required
  content: str                 # required
  result: str = ""
  style: str = ""
  token_count: int = 0

HistoryOut:
  id: int
  task_type: str
  content: str
  result: str
  style: str
  token_count: int
  created_at: str              # ISO 8601 + "Z"
```

### 2.3 Frontend TypeScript Types

```typescript
interface WritingRequest {
  task_type: TaskType
  content: string
  style: string
  target_lang: string
  attachment_text: string
  model?: string
  temperature?: number
}

interface WritingResponse {
  task_type: TaskType
  result: string
  token_count: number
}

interface HistoryItem {
  id: string                   // Backend returns int, frontend converts to string
  task_type: TaskType
  content: string
  result: string
  style: string
  token_count: number
  created_at: string           // ISO 8601
}

interface UploadResult {
  filename: string
  text: string
  char_count: number
}
```

---

## 3. API Contract

### 3.1 Global Configuration

```yaml
base_url: http://localhost:8000
router_prefix: /api/writing
cors:
  allow_origins: ["http://localhost:5173", "http://localhost:3000"]
  allow_credentials: true
  allow_methods: ["*"]
  allow_headers: ["*"]
```

### 3.2 Endpoint Definitions

#### `GET /api/health`

```yaml
response:
  200:
    body: { status: "ok", model: "qwen3.5:9b" }
```

#### `POST /api/writing/upload`

```yaml
request:
  content_type: multipart/form-data
  fields:
    file: UploadFile  # required
  constraints:
    max_size: 10MB    # 10 * 1024 * 1024 bytes
    allowed_extensions: [.pdf, .docx, .doc, .txt, .md, .csv, .json, .xml, .html, .htm]
response:
  200:
    body: { filename: str, text: str, char_count: int }
  400:
    condition: No filename | Unsupported file type | Exceeds size limit
    body: { detail: str }
  500:
    condition: Parsing failed
    body: { detail: "文件解析失败: {error}" }
```

#### `POST /api/writing/process`

```yaml
request:
  content_type: application/json
  body: WritingRequest
response:
  200:
    body: WritingResponse
behavior:
  - Call build_prompt(task_type, content, style, target_lang, attachment_text) to construct the prompt
  - If task_type == "generate" and is_poetry_request(content) == true:
      Loop up to MAX_POETRY_RETRIES(3) times:
        Call ollama.generate(prompt)
        If validate_poetry(result, content) == true: break
  - Otherwise: Call ollama.generate(prompt) once
  - Return WritingResponse
```

#### `POST /api/writing/stream`

```yaml
request:
  content_type: application/json
  body: WritingRequest
response:
  content_type: text/event-stream
  format: |
    data: {json_string_token}\n\n
    ...
    data: [DONE]\n\n
behavior:
  - Poetry path (task_type == "generate" && is_poetry_request(content)):
      1. Non-streaming call to ollama.generate(), retry up to 3 times until validate_poetry() passes
      2. Send the result character by character as SSE events
  - Normal path:
      1. Call ollama.generate_stream()
      2. Send each token as an SSE event
  - Send data: [DONE]\n\n at the end
```

#### `POST /api/writing/export-docx`

```yaml
request:
  content_type: application/json
  body: ExportRequest
response:
  200:
    content_type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
    headers:
      Content-Disposition: "attachment; filename*=UTF-8''{url_encoded_filename}"
    body: binary .docx
  500:
    body: { detail: "文档生成失败: {error}" }
```

#### `POST /api/writing/export-pdf`

```yaml
request:
  content_type: application/json
  body: ExportRequest
response:
  200:
    content_type: application/pdf
    headers:
      Content-Disposition: "attachment; filename*=UTF-8''{url_encoded_filename}"
    body: binary .pdf
  500:
    body: { detail: "PDF 生成失败: {error}" }
```

#### `POST /api/writing/export-pptx`

```yaml
request:
  content_type: application/json
  body: ExportPptxRequest
response:
  200:
    content_type: application/vnd.openxmlformats-officedocument.presentationml.presentation
    headers:
      Content-Disposition: "attachment; filename*=UTF-8''{url_encoded_filename}"
    body: binary .pptx
  500:
    body: { detail: "PPTX 生成失败: {error}" }
behavior:
  - Parse content into slide structure (titles, bullet points, speaker notes)
  - Select theme color scheme based on the template parameter
  - If with_images == true and unsplash_key is not empty:
      Call unsplash.fetch_images_for_slides() to concurrently fetch images
  - Call pptx_export.markdown_to_pptx() to generate PPTX
  - Return binary stream
```

#### `GET /api/history`

```yaml
request:
  query_params:
    keyword: str (optional)
    limit: int = 200
    offset: int = 0
response:
  200:
    body: HistoryOut[]
behavior:
  - Supports keyword search (content / result ILIKE)
  - Ordered by created_at descending
  - If keyword is not empty, fuzzy match on content and result
```

#### `POST /api/history`

```yaml
request:
  content_type: application/json
  body: HistoryCreate
response:
  201:
    body: HistoryOut
```

#### `DELETE /api/history/{id}`

```yaml
response:
  204: Deletion successful
```

#### `DELETE /api/history`

```yaml
response:
  204: All records cleared successfully
```

---

## 4. Business Rules

### 4.1 Prompt Routing

```yaml
build_prompt(task_type, content, style, target_lang, attachment_text):
  if task_type == "generate":
    if style == "xiaohongshu":   use XIAOHONGSHU_PROMPT
    if style == "gongzhonghao":  use GONGZHONGHAO_PROMPT
    if style == "toutiao":       use TOUTIAO_PROMPT
    if style == "ai_drama":      use AI_DRAMA_PROMPT
    if style == "ppt":           use PPT_PROMPT
    if is_poetry_request(content): use POETRY_PROMPT
    else:                        use GENERATE_PROMPT
  elif task_type == "polish":    use POLISH_PROMPT
  elif task_type == "translate": use TRANSLATE_PROMPT
  elif task_type == "summarize": use SUMMARIZE_PROMPT

  # Generic style injection (GENERATE_PROMPT, POLISH_PROMPT, POETRY_PROMPT):
  style_instruction = STYLE_MAP.get(style, "Use {style} style" if style else "")

  # Attachment appending:
  if attachment_text.strip():
    prompt += ATTACHMENT_SECTION.format(attachment_text=attachment_text)
```

### 4.2 Style Mapping

```yaml
STYLE_MAP:
  "literary": "使用文学化、优美的语言风格"
  "sh_gaokao":  ""  # Uses dedicated template
  "xiaohongshu":  ""  # Uses dedicated template
  "gongzhonghao": ""  # Uses dedicated template
  "toutiao":      ""  # Uses dedicated template
  "ai_drama":     ""  # Uses dedicated template
  "ppt":          ""  # Uses dedicated template
  "":             ""  # Default: no style instruction
```

### 4.3 Poetry Validation

```yaml
is_poetry_request(content):
  regex: /(五言|七言|绝句|律诗|古诗|诗词|五律|七律|七绝|五绝)/
  return: bool

validate_poetry(text, content):
  1. Extract all Chinese characters (unicode \u4e00-\u9fff)
  2. Split into sentences by punctuation [，。,.\n；;！？、], filter out empty sentences
  3. If total sentence count < 4: return false
  4. Determine expected character count:
     - content contains "五言"|"五绝"|"五律" → expected = 5
     - content contains "七言"|"七绝"|"七律" → expected = 7
     - Otherwise → return true (skip validation)
  5. return all sentences have Chinese character count == expected
```

### 4.4 File Parsing

```yaml
extract_text(filename, file_bytes):
  ext = lowercase file extension
  if ext not in SUPPORTED_EXTENSIONS: raise ValueError
  if len(file_bytes) > 10MB: raise ValueError

  .pdf  → PyPDF2.PdfReader, extract_text() per page, join with "\n\n"
  .docx/.doc → python-docx Document, non-empty paragraph text, join with "\n\n"
  other → Try decoding in order: utf-8, gbk, gb2312, latin-1, finally utf-8(errors=replace)
```

### 4.5 Markdown to Word Conversion

```yaml
markdown_to_docx(md_text, title=""):
  default_font: "Microsoft YaHei", 11pt
  if title: add level=0 heading

  Parse line by line:
    /^(#{1,3})\s+(.*)/      → doc.add_heading(text, level=N)
    /^[-*+]\s+(.*)/          → doc.add_paragraph(text, style="List Bullet")
    /^\d+\.\s+(.*)/          → doc.add_paragraph(text, style="List Number")
    /^>/                     → Indented paragraph, italic, gray(100,100,100)
    /^[-*_]{3,}$/            → Centered gray separator line
    other                    → Normal paragraph, inline processing of **bold** and *italic*

  Inline formatting: re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    **text** → bold run
    *text*   → italic run
    other    → normal run

  Return: io.BytesIO (already seek(0))
```

### 4.6 Markdown to PPTX Conversion

```yaml
markdown_to_pptx(md_text, title="", template="business", images={}):
  slide_width: 13333400 EMU (widescreen 16:9)
  slide_height: 7500950 EMU
  default_font: "Microsoft YaHei"

  Theme colors:
    business: Dark blue background (#0F1729), bright blue title (#4FC3F7), blue accent (#2979FF), light gray text (#DDDDDD)
    minimal:  Light gray background (#FAFAFA), dark gray title (#1A1A1A), dark gray accent (#333333), dark gray text (#333333)
    green:    Dark green background (#0D1F0D), green title (#66BB6A), green accent (#2E7D32), light green text (#D8E8D8)
    warm:     Dark brown background (#2E1A0E), orange title (#FFB74D), orange accent (#FF8F00), beige text (#E8D8C8)

  Parsing rules:
    /^##\s+(.*)/                → Create new slide, set title
    /\[layout:\s*(\w+)\]\s*$/   → Extract layout tag, remove from title
    /^[-*+]\s+(.*)/             → Bullet point
    /^\d+\.\s+(.*)/             → Ordered list item
    /^>\s*(.*)/                 → Speaker notes (remove "备注:" / "演讲备注:" prefix)
    /^---$/                     → Slide separator (when no title)

  Layout system (content slides dispatched based on [layout: xxx] tag):
    bullets:     Title + bullet list (default)
    stats:       Large numbers in rounded cards + labels, multi-column layout (format: "Label: Value")
    comparison:  Left-right two columns + column titles + center divider (format: "Left content | Right content")
    timeline:    Horizontal timeline + node dots + top/bottom annotations (format: "Time: Description")
    quote:       Large quotation mark decoration + centered quote + attribution (first line: quote, last line: attribution)
    grid:        Adaptive 2-3 column grid cards with top accent line (format: "Title: Description")

  Slide types:
    Cover (index == 0):    Centered title + subtitle + decorative line + decorative circle
    Closing page (contains "谢谢"|"致谢"|"Q&A"|"感谢"|"Thank"): Centered large text + decoration
    Content page:          Call corresponding renderer based on layout tag

  Return: io.BytesIO (already seek(0))
```

### 4.7 Unsplash Image Fetching

```yaml
search_image(query, api_key, width=800, height=600):
  Clean query: remove numeric prefixes, Markdown formatting, punctuation
  GET https://api.unsplash.com/search/photos
    headers: { Authorization: "Client-ID {api_key}" }
    params: { query, per_page: 1, orientation: "landscape" }
  timeout: 10s
  Return: image bytes | None

fetch_images_for_slides(slides, api_key):
  Skip cover and closing pages
  Concurrently fetch all content page images via asyncio.gather()
  Return: dict[int, bytes]  # slide index → image data
  No API Key → return empty dict
```

---

## 5. Ollama Client

```yaml
config:
  base_url: "http://localhost:11434"
  default_model: "qwen3.5:9b"
  timeout: 120s
  think: false  # Disable chain-of-thought

generate(prompt, model, temperature):
  POST {base_url}/api/generate
  body: { model, prompt, stream: false, think: false, options: { temperature } }
  return: { text: response.response, token_count: response.eval_count }

generate_stream(prompt, model, temperature):
  POST {base_url}/api/generate
  body: { model, prompt, stream: true, think: false, options: { temperature } }
  yield: Parse JSON line by line, extract non-empty token from response field
  stop: chunk.done == true
```

---

## 6. Frontend Component Specifications

### 6.1 App (Root Component)

```yaml
state:
  result: string = ""
  loading: boolean = false
  tokenCount: number = 0
  error: string = ""
  online: boolean | null = null
  history: HistoryItem[] = []
  activeId: string = ""
  sidebarOpen: boolean = false
  theme: string = "system"      # system | light | dark
  showSettings: boolean = false
  model: string = ""
  temperature: number | null = null

refs:
  abortRef: AbortController | null
  lastReqRef: WritingRequest | null

lifecycle:
  mount:
    - Call healthCheck() → setOnline
    - Call getHistory() → setHistory (async, backend API)
    - Register keyboard shortcut listeners (Ctrl+Enter, Esc, Ctrl+S)
    - Read theme preference from localStorage

handlers:
  handleSubmit(req):
    1. Reset result/tokenCount/error/loading/activeId
    2. Inject model/temperature into req (if set)
    3. Call streamWriting(req, onToken, onDone, onError)
    4. onToken: count++, fullText += token, update result and tokenCount
    5. onDone: loading=false, if fullText is non-empty then addHistory() (async) and update history/activeId
    6. onError: set error, loading=false
    7. Save AbortController to abortRef, req to lastReqRef

  handleStop:
    abortRef.abort(), loading=false

  handleRegenerate:
    If lastReqRef exists, call handleSubmit(lastReqRef)

  handleSelectHistory(item):
    Restore result/tokenCount/activeId, clear error

  handleDeleteHistory(id):
    Call removeHistory(id) (async), if deleted item is current activeId then clear display

  handleClearHistory:
    Show ConfirmDialog, on confirm call clearHistory() (async), clear all state

  toggleTheme:
    Cycle system → light → dark → system, persist to localStorage

layout:
  header: "AI Writing Assistant" + online status indicator + dark mode toggle + settings button + hamburger menu (mobile)
  sidebar: HistoryPanel (collapsible on mobile)
  main: WritingForm + ResultPanel
  footer: "Powered by Ollama · qwen3.5:9b"
```

### 6.2 WritingForm

```yaml
props:
  onSubmit: (req: WritingRequest) => void
  loading: boolean
  onStop: () => void
  online: boolean | null          # Backend online status; disable submit when offline

state:
  taskType: TaskType = "generate"
  content: string = ""
  style: string = ""
  targetLang: string = "英文"
  attachmentText: string = ""
  attachmentName: string = ""
  uploading: boolean = false
  uploadError: string = ""

refs:
  fileInputRef: HTMLInputElement

file_upload:
  accept: ".pdf,.docx,.doc,.txt,.md,.csv,.json,.xml,.html,.htm"
  on_change:
    1. setUploading(true), clear uploadError
    2. Call uploadFile(file) → set attachmentText/attachmentName
    3. catch → set uploadError, clear attachment
    4. finally → uploading=false, clear input.value

submit:
  guard: content.trim() is non-empty
  payload: { task_type, content, style, target_lang, attachment_text }

ui_elements:
  - Task type tabs (4 tabs, disabled condition: loading)
  - Content textarea (rows=8, placeholder changes based on taskType)
  - Character count (content.length, displayed in real-time below the textarea)
  - Offline banner (shown as red alert banner when online === false)
  - File upload button + attachment tag + remove button
  - Style dropdown (9 options)
  - Target language dropdown (shown only for translate task, 6 options)
  - Submit/Stop button (submit disabled when offline)
```

### 6.3 ResultPanel

```yaml
props:
  result: string
  loading: boolean
  tokenCount: number
  error: string
  taskType: TaskType              # Used to determine whether to show comparison view
  originalContent: string         # Original text for polish/translate tasks
  onRegenerate: () => void        # "Try another" callback
  onRetry: () => void             # "Retry" callback

state:
  exporting: boolean = false
  exportMsg: string = ""  # "Download successful" | "Download failed" | ""
  editing: boolean = false
  editText: string = ""
  copyMsg: string = ""    # "Copied" | "Copy failed" | ""

conditions:
  error exists:      Show error panel + "Retry" button
  No result and not loading: Show empty state prompt
  Otherwise:         Show result panel

result_panel:
  header: "Generated Result" + token count badge + "Generating..." animation
  content: <Markdown>{result}</Markdown> + blinking cursor (when loading)
  compare_view: Side-by-side comparison for polish/translate tasks (originalContent | result)
  edit_mode: Edit/Save/Cancel buttons, textarea replaces Markdown rendering
  actions (result exists and !loading):
    - "Copy Result" → navigator.clipboard.writeText(result), temporarily changes to "Copied"/"Copy failed"
    - "Try Another" → onRegenerate()
    - "Edit" → Enter edit mode
    - "Download Word" / "Download PDF" / "Download TXT" / "Download MD" / "Download PPT"
    - PPT options panel (shown only when style === "ppt"):
        - Theme selector: PPT_THEME_OPTIONS (4 options)
        - Image checkbox (shown only when Unsplash Key is set)
    - exportMsg notification (success green / failure red, disappears after 3 seconds)

handleExport:
  1. setExporting(true), clear exportMsg
  2. Call downloadDocx(result)
  3. Success: exportMsg = "Download successful", clear after 3 seconds
  4. Failure: exportMsg = "Download failed", clear after 3 seconds
  5. finally: exporting=false
```

### 6.4 HistoryPanel

```yaml
props:
  items: HistoryItem[]
  activeId: string
  onSelect: (item: HistoryItem) => void
  onDelete: (id: string) => void
  onClear: () => void

state:
  keyword: string = ""

computed:
  filtered:
    if keyword.trim() is empty: return items
    else: items.filter(item =>
      item.content.toLowerCase().includes(kw) ||
      item.result.toLowerCase().includes(kw)
    ).sort((a, b) => b.created_at - a.created_at)

ui:
  header: "History ({items.length})" + clear button (shown when items > 0, click opens ConfirmDialog)
  search: Search input + clear button (shown when keyword is non-empty, items > 0)
  empty: "No matching records" (with keyword) | "No records yet" (without keyword)
  list: filtered.map → each item displays:
    - Task type label (TASK_LABELS[task_type])
    - Timestamp (MM-DD HH:mm)
    - Content preview (first 30 characters, single-line truncation)
    - Delete button (shown on hover, stops event propagation)
    - Selected highlight (left border when activeId matches)
```

---

## 7. Frontend Service Layer

### 7.1 api.ts

```yaml
axios_instance:
  baseURL: "http://localhost:8000"
  timeout: 120000

functions:
  processWriting(req: WritingRequest) → WritingResponse:
    POST /api/writing/process

  streamWriting(req, onToken, onDone, onError) → AbortController:
    Uses native fetch (not axios, because streaming reads are needed)
    URL: "http://localhost:8000/api/writing/stream"
    SSE parsing:
      - Split by "\n", maintain buffer
      - Match "data: " prefix
      - payload == "[DONE]" → onDone()
      - Otherwise JSON.parse(payload) → onToken()
      - AbortError → ignore

  healthCheck() → boolean:
    GET /api/health, check status == "ok"

  uploadFile(file: File) → UploadResult:
    POST /api/writing/upload, FormData (do not manually set Content-Type)

  downloadDocx(content, title="") → void:
    1. Prefer calling showSaveFilePicker (before await, to preserve user gesture context)
       - suggestedName: "{title || 'Exported Document'}.docx"
       - types: Word document
       - AbortError → return (user cancelled)
    2. POST /api/writing/export-docx, responseType: blob
    3. If fileHandle exists → createWritable() + write(blob) + close()
    4. Otherwise → Blob URL + <a>.click() download

  downloadPptx(content, title="", template="business", withImages=false, unsplashKey="") → void:
    1. POST /api/writing/export-pptx, responseType: blob
       - timeout: withImages ? 300000 : 120000
       - body: { content, title, template, with_images, unsplash_key }
    2. Blob URL + <a>.click() download
```

### 7.2 history.ts

```yaml
base_url: "/api/history"

getHistory() → Promise<HistoryItem[]>:
  GET /api/history, returns array

addHistory(item: Omit<HistoryItem, "id" | "created_at">) → Promise<HistoryItem>:
  POST /api/history, returns new record

removeHistory(id) → Promise<void>:
  DELETE /api/history/{id}

clearHistory() → Promise<void>:
  DELETE /api/history
```

### 7.3 templates.ts

```yaml
storage_key: "writing_templates"

getTemplates() → Template[]:
  Read from localStorage, JSON.parse, return [] on exception

saveTemplate(template) → void:
  Insert or update template, save to localStorage

deleteTemplate(id) → void:
  Filter out template matching id, save
```

---

## 8. UI Constants

```yaml
TASK_LABELS:
  generate:  "文章生成"
  polish:    "文本润色"
  translate: "文本翻译"
  summarize: "文本摘要"

TASK_PLACEHOLDERS:
  generate:  "请输入主题或大纲，例如：写一篇关于人工智能未来发展的文章..."
  polish:    "请粘贴需要润色的文本..."
  translate: "请输入需要翻译的文本..."
  summarize: "请粘贴需要总结的长文本..."

STYLE_OPTIONS:
  - { value: "",             label: "默认" }
  - { value: "literary",    label: "文学" }
  - { value: "sh_gaokao",   label: "上海高考作文" }
  - { value: "xiaohongshu", label: "小红书爆款" }
  - { value: "gongzhonghao",label: "公众号文案" }
  - { value: "toutiao",     label: "头条文案" }
  - { value: "ai_drama",    label: "AI短剧脚本" }
  - { value: "ppt",         label: "生成PPT" }

LANG_OPTIONS:
  - { value: "英文", label: "英文" }
  - { value: "中文", label: "中文" }
  - { value: "日文", label: "日文" }
  - { value: "韩文", label: "韩文" }
  - { value: "法文", label: "法文" }
  - { value: "德文", label: "德文" }

PPT_THEME_OPTIONS:
  - { value: "business", label: "商务蓝" }
  - { value: "minimal",  label: "极简灰" }
  - { value: "green",    label: "清新绿" }
  - { value: "warm",     label: "暖色调" }
```

---

## 9. Prompt Templates

> Each template is a complete prompt string. `{content}` / `{style_instruction}` / `{target_lang}` are interpolation variables.

### GENERATE_PROMPT
```
Role: Professional Chinese writing assistant
Requirements: Clear structure / Fluent language / Rich and in-depth content
Variables: {style_instruction}, {content}
Output: Directly output the content
```

### POETRY_PROMPT
```
Role: Master of classical Chinese poetry
Format rules: 5-character lines for five-character verse, 7-character lines for seven-character verse, 4 lines for quatrains, 8 lines for regulated verse
Includes format examples and validation instructions
Variables: {style_instruction}, {content}
Output: Output only the poem itself
```

### POLISH_PROMPT
```
Role: Professional text editor
Requirements: Preserve original meaning / Improve quality / Correct grammar
Variables: {style_instruction}, {content}
```

### TRANSLATE_PROMPT
```
Role: Professional translation expert
Requirements: Accurate and faithful / Natural and fluent / Preserve tone
Variables: {target_lang}, {content}
```

### SUMMARIZE_PROMPT
```
Role: Professional text analyst
Requirements: Core ideas / No more than 1/3 of the original length / Logically complete
Variables: {content}
```

### XIAOHONGSHU_PROMPT
```
Role: Viral Xiaohongshu (RED) copywriter
Rules: Emoji title ≤ 20 characters / Bullet points / Conversational tone / Encourage engagement / 5-8 hashtags / 300-600 characters
Variables: {content}
```

### GONGZHONGHAO_PROMPT
```
Role: Senior WeChat Official Account viral copywriter
Rules: Title ≤ 25 characters / Story-driven opening / Introduction-body-conclusion structure / Short paragraphs / Bold key phrases / 800-1500 characters
Variables: {content}
```

### TOUTIAO_PROMPT
```
Role: Senior Toutiao (Headlines) content creator
Rules: Highly engaging title 25-30 characters / Present core point in first 100 characters / Short paragraphs and sentences / Suspense hooks / 600-1200 characters
Variables: {content}
```

### AI_DRAMA_PROMPT
```
Role: Professional AI short drama screenwriter
Rules: Scene/Character/Dialogue format / 2-3 minute duration / Opening suspense / At least 1 plot twist / Cliffhanger ending / Lines ≤ 20 characters
Variables: {content}
```

### PPT_PROMPT
```
Role: Professional presentation planner
Rules: Page count is highest priority / Cover + Content + Acknowledgment / 6 layout tags [layout: bullets|stats|comparison|timeline|quote|grid]
Layout selection: Numbers → stats / Comparison → comparison / Journey → timeline / Key quote → quote / Multiple modules → grid / General → bullets
Diversity: ≥8 pages require at least 3 layout types / <8 pages require at least 2 / ≤3 pages no requirement
Data formats: stats uses "Label: Value" / comparison uses "Left | Right" / timeline uses "Time: Description" / grid uses "Title: Description"
Variables: {content}
```

### ATTACHMENT_SECTION
```
Appended to any prompt (when attachment_text is non-empty):
【参考附件内容】
---
{attachment_text}
---
```

---

## 10. Project Dependencies

### Backend (pyproject.toml)

```yaml
requires-python: ">=3.10"
dependencies:
  - fastapi >= 0.135.1
  - httpx >= 0.28.1
  - pydantic >= 2.12.5
  - pypdf2 >= 3.0.1
  - python-docx >= 1.2.0
  - python-multipart >= 0.0.22
  - python-pptx >= 1.0.2
  - uvicorn >= 0.42.0
  - sqlalchemy >= 2.0
  - aiosqlite >= 0.20
  - fpdf2 >= 2.8
dev:
  - pytest >= 9.0.2
  - pytest-asyncio >= 1.3.0
```

### Frontend (package.json)

```yaml
dependencies:
  axios: ^1.13.6
  react: ^19.2.4
  react-dom: ^19.2.4
  react-markdown: ^10.1.0
devDependencies:
  vite: ^8.0.0
  typescript: ~5.9.3
  @vitejs/plugin-react: ^6.0.0
  vitest: ^4.1.0
  @testing-library/react: ^16.3.2
  @testing-library/jest-dom: ^6.9.1
  @testing-library/user-event: ^14.6.1
  happy-dom: ^20.8.4
  jsdom: ^29.0.0
```

---

## 11. Error Handling Specification

### Backend

```yaml
Unified error format: { "detail": str }

Router layer:
  - ValueError → HTTP 400 + detail
  - Exception  → HTTP 500 + detail (prefixed with "文件解析失败:" or "文档生成失败:" or "PDF 生成失败:")
  - Pydantic validation failure → HTTP 422 (handled automatically by FastAPI)
  - RateLimitMiddleware → HTTP 429 + detail "Rate limit exceeded. Try again later."

Service layer:
  - ollama_client: httpx exceptions propagated upward
  - file_parser: ValueError (unsupported type / size exceeded), other exceptions propagated upward
  - docx_export: Exceptions propagated upward
  - pdf_export: Exceptions propagated upward
  - pptx_export: Exceptions propagated upward
  - unsplash: No API Key returns empty result, httpx exceptions return None, does not interrupt PPTX generation
  - history router: Standard CRUD, 404 not handled (DELETE is idempotent)
```

### Frontend

```yaml
api.ts:
  - streamWriting: AbortError silently ignored, other errors call onError
  - healthCheck: Returns false on exception
  - uploadFile: Exceptions propagated to caller
  - downloadDocx: showSaveFilePicker AbortError → return, others propagated

Component layer:
  - WritingForm: uploadFile catch → display uploadError
  - ResultPanel: downloadDocx catch → display exportMsg="Download failed"
  - App: streamWriting onError → display error
```
