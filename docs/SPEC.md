# AI 写作助手 — 技术规格书 (Spec)

> 本文档是 spec-driven 规格书，包含完整的数据模型、接口契约、组件接口、业务规则和配置定义。
> 可据此规格书直接生成前后端代码。

---

## 1. 系统概述

| 属性 | 值 |
|------|-----|
| 项目名称 | AI 写作助手 |
| 架构 | 前后端分离，SSE 流式通信 |
| 后端 | Python 3.10+, FastAPI, Pydantic v2, httpx, SQLAlchemy, aiosqlite, uvicorn |
| 前端 | React 19, TypeScript, Vite 8, Axios, react-markdown |
| LLM 后端 | Ollama REST API (localhost:11434) |
| 默认模型 | qwen3.5:9b |
| 后端端口 | 8000 |
| 前端端口 | 5173 (dev) |

---

## 2. 数据模型

### 2.1 枚举

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

### 2.2 后端 Pydantic 模型

```yaml
WritingRequest:
  task_type: TaskType          # required
  content: str                 # required
  style: str = ""
  target_lang: str = "英文"
  attachment_text: str = ""
  model: str = ""              # 自定义模型名称，空则使用默认
  temperature: Optional[float] = None  # 生成温度，None 则用模型默认

WritingResponse:
  task_type: TaskType
  result: str
  token_count: int = 0

ExportRequest:
  content: str                 # required, Markdown 文本
  title: str = ""

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

### 2.3 前端 TypeScript 类型

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
  id: string                   // 后端返回 int，前端转为 string
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

## 3. API 契约

### 3.1 全局配置

```yaml
base_url: http://localhost:8000
router_prefix: /api/writing
cors:
  allow_origins: ["http://localhost:5173", "http://localhost:3000"]
  allow_credentials: true
  allow_methods: ["*"]
  allow_headers: ["*"]
```

### 3.2 端点定义

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
    condition: 无文件名 | 不支持的文件类型 | 超过大小限制
    body: { detail: str }
  500:
    condition: 解析失败
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
  - 调用 build_prompt(task_type, content, style, target_lang, attachment_text) 构建提示词
  - 若 task_type == "generate" 且 is_poetry_request(content) == true:
      循环最多 MAX_POETRY_RETRIES(3) 次:
        调用 ollama.generate(prompt)
        若 validate_poetry(result, content) == true: 跳出
  - 否则: 调用 ollama.generate(prompt) 一次
  - 返回 WritingResponse
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
  - 诗词路径 (task_type == "generate" && is_poetry_request(content)):
      1. 非流式调用 ollama.generate()，重试最多 3 次直到 validate_poetry() 通过
      2. 将结果逐字符以 SSE 事件发送
  - 普通路径:
      1. 调用 ollama.generate_stream()
      2. 每个 token 以 SSE 事件发送
  - 结束发送 data: [DONE]\n\n
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
  - 支持关键词搜索（content / result ILIKE）
  - 按 created_at 倒序排列
  - 若 keyword 非空，模糊匹配 content 和 result
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
  204: 删除成功
```

#### `DELETE /api/history`

```yaml
response:
  204: 清空成功
```

---

## 4. 业务规则

### 4.1 提示词路由

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

  # 通用风格注入 (GENERATE_PROMPT, POLISH_PROMPT, POETRY_PROMPT):
  style_instruction = STYLE_MAP.get(style, "使用{style}风格" if style else "")

  # 附件追加:
  if attachment_text.strip():
    prompt += ATTACHMENT_SECTION.format(attachment_text=attachment_text)
```

### 4.2 风格映射

```yaml
STYLE_MAP:
  "literary": "使用文学化、优美的语言风格"
  "sh_gaokao":  ""  # 使用独立模板
  "xiaohongshu":  ""  # 使用独立模板
  "gongzhonghao": ""  # 使用独立模板
  "toutiao":      ""  # 使用独立模板
  "ai_drama":     ""  # 使用独立模板
  "ppt":          ""  # 使用独立模板
  "":             ""  # 默认无风格指令
```

### 4.3 诗词校验

```yaml
is_poetry_request(content):
  regex: /(五言|七言|绝句|律诗|古诗|诗词|五律|七律|七绝|五绝)/
  return: bool

validate_poetry(text, content):
  1. 提取所有汉字 (unicode \u4e00-\u9fff)
  2. 按标点 [，。,.\n；;！？、] 分句，过滤空句
  3. 若总句数 < 4: return false
  4. 确定期望字数:
     - content 含 "五言"|"五绝"|"五律" → expected = 5
     - content 含 "七言"|"七绝"|"七律" → expected = 7
     - 否则 → return true (不校验)
  5. return 所有句子汉字数 == expected
```

### 4.4 文件解析

```yaml
extract_text(filename, file_bytes):
  ext = filename 后缀小写
  if ext not in SUPPORTED_EXTENSIONS: raise ValueError
  if len(file_bytes) > 10MB: raise ValueError

  .pdf  → PyPDF2.PdfReader, 逐页 extract_text(), "\n\n" 连接
  .docx/.doc → python-docx Document, 非空段落文本, "\n\n" 连接
  其他  → 依次尝试 utf-8, gbk, gb2312, latin-1 解码, 最终 utf-8(errors=replace)
```

### 4.5 Markdown → Word 转换

```yaml
markdown_to_docx(md_text, title=""):
  default_font: "Microsoft YaHei", 11pt
  if title: 添加 level=0 标题

  逐行解析:
    /^(#{1,3})\s+(.*)/      → doc.add_heading(text, level=N)
    /^[-*+]\s+(.*)/          → doc.add_paragraph(text, style="List Bullet")
    /^\d+\.\s+(.*)/          → doc.add_paragraph(text, style="List Number")
    /^>/                     → 缩进段落, 斜体, 灰色(100,100,100)
    /^[-*_]{3,}$/            → 居中灰色分隔线
    其他                      → 普通段落, 内联处理 **bold** 和 *italic*

  内联格式: re.split(r"(\*\*.*?\*\*|\*.*?\*)", text)
    **text** → bold run
    *text*   → italic run
    其他     → normal run

  返回: io.BytesIO (已 seek(0))
```

---

## 5. Ollama 客户端

```yaml
config:
  base_url: "http://localhost:11434"
  default_model: "qwen3.5:9b"
  timeout: 120s
  think: false  # 禁用思考链

generate(prompt, model, temperature):
  POST {base_url}/api/generate
  body: { model, prompt, stream: false, think: false, options: { temperature } }
  return: { text: response.response, token_count: response.eval_count }

generate_stream(prompt, model, temperature):
  POST {base_url}/api/generate
  body: { model, prompt, stream: true, think: false, options: { temperature } }
  yield: 逐行解析 JSON, 提取 response 字段非空 token
  stop: chunk.done == true
```

---

## 6. 前端组件规格

### 6.1 App (根组件)

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
    - 调用 healthCheck() → setOnline
    - 调用 getHistory() → setHistory (async, 后端 API)
    - 注册快捷键监听 (Ctrl+Enter, Esc, Ctrl+S)
    - 读取 localStorage 中的 theme 偏好

handlers:
  handleSubmit(req):
    1. 重置 result/tokenCount/error/loading/activeId
    2. 注入 model/temperature 到 req（若已设置）
    3. 调用 streamWriting(req, onToken, onDone, onError)
    4. onToken: count++, fullText += token, 更新 result 和 tokenCount
    5. onDone: loading=false, 若 fullText 非空则 addHistory() (async) 并更新 history/activeId
    6. onError: 设置 error, loading=false
    7. 保存 AbortController 到 abortRef, req 到 lastReqRef

  handleStop:
    abortRef.abort(), loading=false

  handleRegenerate:
    若 lastReqRef 存在, 调用 handleSubmit(lastReqRef)

  handleSelectHistory(item):
    恢复 result/tokenCount/activeId, 清空 error

  handleDeleteHistory(id):
    调用 removeHistory(id) (async), 若删除的是当前 activeId 则清空显示

  handleClearHistory:
    显示 ConfirmDialog, 确认后调用 clearHistory() (async), 清空所有状态

  toggleTheme:
    system → light → dark → system 循环, 持久化到 localStorage

layout:
  header: "AI 写作助手" + 在线状态指示器 + 深色模式切换 + 设置按钮 + 汉堡菜单(移动端)
  sidebar: HistoryPanel (移动端可折叠)
  main: WritingForm + ResultPanel
  footer: "Powered by Ollama · qwen3.5:9b"
```

### 6.2 WritingForm

```yaml
props:
  onSubmit: (req: WritingRequest) => void
  loading: boolean
  onStop: () => void
  online: boolean | null          # 后端在线状态，离线时禁用提交

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
    1. setUploading(true), 清空 uploadError
    2. 调用 uploadFile(file) → 设置 attachmentText/attachmentName
    3. catch → 设置 uploadError, 清空 attachment
    4. finally → uploading=false, 清空 input.value

submit:
  guard: content.trim() 非空
  payload: { task_type, content, style, target_lang, attachment_text }

ui_elements:
  - 任务类型标签页 (4 个 tab, 禁用条件: loading)
  - 内容文本域 (rows=8, placeholder 随 taskType 变化)
  - 字数统计 (content.length, 文本域下方实时显示)
  - 离线横幅 (online === false 时显示红色提示横幅)
  - 文件上传按钮 + 附件标签 + 移除按钮
  - 风格下拉框 (9 个选项)
  - 目标语言下拉框 (仅 translate 时显示, 6 个选项)
  - 提交/停止按钮 (离线时禁用提交)
```

### 6.3 ResultPanel

```yaml
props:
  result: string
  loading: boolean
  tokenCount: number
  error: string
  taskType: TaskType              # 用于判断是否显示对比视图
  originalContent: string         # 润色/翻译时的原文
  onRegenerate: () => void        # "换一个"回调
  onRetry: () => void             # "重新尝试"回调

state:
  exporting: boolean = false
  exportMsg: string = ""  # "下载成功" | "下载失败" | ""
  editing: boolean = false
  editText: string = ""
  copyMsg: string = ""    # "已复制" | "复制失败" | ""

conditions:
  error 存在:      显示错误面板 + "重新尝试"按钮
  无 result 且不 loading: 显示空态提示
  否则:            显示结果面板

result_panel:
  header: "生成结果" + token 计数 badge + "生成中..." 动画
  content: <Markdown>{result}</Markdown> + 闪烁光标 (loading 时)
  compare_view: 润色/翻译任务时左右对比 (originalContent | result)
  edit_mode: 编辑/保存/取消按钮，textarea 替代 Markdown 渲染
  actions (result 存在且 !loading):
    - "复制结果" → navigator.clipboard.writeText(result), 临时变为"已复制"/"复制失败"
    - "换一个" → onRegenerate()
    - "编辑" → 进入编辑模式
    - "下载 Word" / "下载 PDF" / "下载 TXT" / "下载 MD"
    - exportMsg 提示 (成功绿色 / 失败红色, 3 秒后消失)

handleExport:
  1. setExporting(true), 清空 exportMsg
  2. 调用 downloadDocx(result)
  3. 成功: exportMsg = "下载成功", 3 秒后清空
  4. 失败: exportMsg = "下载失败", 3 秒后清空
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
    if keyword.trim() 为空: return items
    else: items.filter(item =>
      item.content.toLowerCase().includes(kw) ||
      item.result.toLowerCase().includes(kw)
    ).sort((a, b) => b.created_at - a.created_at)

ui:
  header: "历史记录 ({items.length})" + 清空按钮 (items > 0 时显示, 点击弹出 ConfirmDialog)
  search: 搜索输入框 + 清除按钮 (keyword 非空时, items > 0 时显示)
  empty: "没有匹配的记录" (有 keyword) | "暂无记录" (无 keyword)
  list: filtered.map → 每条显示:
    - 任务类型标签 (TASK_LABELS[task_type])
    - 时间 (MM-DD HH:mm)
    - 内容预览 (前 30 字, 单行截断)
    - 删除按钮 (hover 显示, 阻止事件冒泡)
    - 选中高亮 (activeId 匹配时左边框)
```

---

## 7. 前端 Service 层

### 7.1 api.ts

```yaml
axios_instance:
  baseURL: "http://localhost:8000"
  timeout: 120000

functions:
  processWriting(req: WritingRequest) → WritingResponse:
    POST /api/writing/process

  streamWriting(req, onToken, onDone, onError) → AbortController:
    使用原生 fetch (非 axios, 因需流式读取)
    URL: "http://localhost:8000/api/writing/stream"
    解析 SSE:
      - 按 "\n" 分行, 维护 buffer
      - 匹配 "data: " 前缀
      - payload == "[DONE]" → onDone()
      - 否则 JSON.parse(payload) → onToken()
      - AbortError → 忽略

  healthCheck() → boolean:
    GET /api/health, 检查 status == "ok"

  uploadFile(file: File) → UploadResult:
    POST /api/writing/upload, FormData (不手动设置 Content-Type)

  downloadDocx(content, title="") → void:
    1. 优先调用 showSaveFilePicker (在 await 之前, 保持用户手势上下文)
       - suggestedName: "{title || '导出文档'}.docx"
       - types: Word 文档
       - AbortError → return (用户取消)
    2. POST /api/writing/export-docx, responseType: blob
    3. 若有 fileHandle → createWritable() + write(blob) + close()
    4. 否则 → Blob URL + <a>.click() 下载
```

### 7.2 history.ts

```yaml
base_url: "/api/history"

getHistory() → Promise<HistoryItem[]>:
  GET /api/history, 返回数组

addHistory(item: Omit<HistoryItem, "id" | "created_at">) → Promise<HistoryItem>:
  POST /api/history, 返回新记录

removeHistory(id) → Promise<void>:
  DELETE /api/history/{id}

clearHistory() → Promise<void>:
  DELETE /api/history
```

### 7.3 templates.ts

```yaml
storage_key: "writing_templates"

getTemplates() → Template[]:
  读取 localStorage, JSON.parse, 异常返回 []

saveTemplate(template) → void:
  插入或更新模板, 保存到 localStorage

deleteTemplate(id) → void:
  过滤掉 id 匹配的模板, 保存
```

---

## 8. UI 常量

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
```

---

## 9. 提示词模板

> 每个模板均为完整的 prompt 字符串，`{content}` / `{style_instruction}` / `{target_lang}` 为插值变量。

### GENERATE_PROMPT
```
角色: 专业中文写作助手
要求: 结构清晰 / 语言流畅 / 内容丰富有深度
变量: {style_instruction}, {content}
输出: 直接输出内容
```

### POETRY_PROMPT
```
角色: 精通中国古典诗词的大师
格式规则: 五言5字/句, 七言7字/句, 绝句4句, 律诗8句
含格式示例和验证说明
变量: {style_instruction}, {content}
输出: 仅输出诗词本身
```

### POLISH_PROMPT
```
角色: 专业文字编辑
要求: 保持原意 / 提升质量 / 修正语法
变量: {style_instruction}, {content}
```

### TRANSLATE_PROMPT
```
角色: 专业翻译专家
要求: 准确忠实 / 自然流畅 / 保持语气
变量: {target_lang}, {content}
```

### SUMMARIZE_PROMPT
```
角色: 专业文本分析师
要求: 核心观点 / 不超过原文1/3 / 逻辑完整
变量: {content}
```

### XIAOHONGSHU_PROMPT
```
角色: 小红书爆款文案写手
规则: emoji标题≤20字 / 分点叙述 / 口语化 / 引导互动 / 5-8标签 / 300-600字
变量: {content}
```

### GONGZHONGHAO_PROMPT
```
角色: 资深微信公众号爆款写手
规则: 标题≤25字 / 故事切入 / 总分总结构 / 短段落 / 金句加粗 / 800-1500字
变量: {content}
```

### TOUTIAO_PROMPT
```
角色: 今日头条资深创作者
规则: 强吸引力标题25-30字 / 前100字抛出核心 / 短段落短句 / 悬念钩子 / 600-1200字
变量: {content}
```

### AI_DRAMA_PROMPT
```
角色: 专业AI短剧编剧
规则: 场景/角色/对白格式 / 2-3分钟时长 / 开头悬念 / 至少1个反转 / 结尾钩子 / 台词≤20字
变量: {content}
```

### PPT_PROMPT
```
角色: 专业演示文稿策划师
规则: 8-15页 / 封面+目录+内容+总结+致谢 / 每页3-5要点 / Markdown格式 / 演讲备注
变量: {content}
```

### ATTACHMENT_SECTION
```
追加到任何 prompt 末尾 (当 attachment_text 非空时):
【参考附件内容】
---
{attachment_text}
---
```

---

## 10. 项目依赖

### 后端 (pyproject.toml)

```yaml
requires-python: ">=3.10"
dependencies:
  - fastapi >= 0.135.1
  - httpx >= 0.28.1
  - pydantic >= 2.12.5
  - pypdf2 >= 3.0.1
  - python-docx >= 1.2.0
  - python-multipart >= 0.0.22
  - uvicorn >= 0.42.0
  - sqlalchemy >= 2.0
  - aiosqlite >= 0.20
  - fpdf2 >= 2.8
dev:
  - pytest >= 9.0.2
  - pytest-asyncio >= 1.3.0
```

### 前端 (package.json)

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

## 11. 错误处理规范

### 后端

```yaml
统一错误格式: { "detail": str }

路由层:
  - ValueError → HTTP 400 + detail
  - Exception  → HTTP 500 + detail (前缀 "文件解析失败:" 或 "文档生成失败:" 或 "PDF 生成失败:")
  - Pydantic 校验失败 → HTTP 422 (FastAPI 自动处理)
  - RateLimitMiddleware → HTTP 429 + detail "Rate limit exceeded. Try again later."

服务层:
  - ollama_client: httpx 异常上抛
  - file_parser: ValueError (不支持的类型/超大小), 其他异常上抛
  - docx_export: 异常上抛
  - pdf_export: 异常上抛
  - history router: 标准 CRUD, 404 不处理 (DELETE 幂等)
```

### 前端

```yaml
api.ts:
  - streamWriting: AbortError 静默忽略, 其他错误调用 onError
  - healthCheck: 异常返回 false
  - uploadFile: 异常上抛给调用方
  - downloadDocx: showSaveFilePicker AbortError → return, 其他上抛

组件层:
  - WritingForm: uploadFile catch → 显示 uploadError
  - ResultPanel: downloadDocx catch → 显示 exportMsg="下载失败"
  - App: streamWriting onError → 显示 error
```
