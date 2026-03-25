# AI 写作助手 — 项目架构文档

## 总体架构

AI 写作助手是一个基于**本地大语言模型（Ollama）**的智能写作工具，采用前后端分离架构：

```
┌─────────────────┐      SSE / HTTP       ┌─────────────────┐      HTTP       ┌───────────┐
│                 │  ◄──────────────────►  │                 │  ◄───────────►  │           │
│  React 前端      │   localhost:8000      │  FastAPI 后端     │  localhost:11434│  Ollama   │
│  (Vite + TS)    │                       │  (Python 3.10+)  │                │  qwen3.5  │
│  :5173          │                       │  :8000           │                │  :11434   │
└─────────────────┘                       └─────────────────┘                └───────────┘
```

| 层级         | 技术栈                                              | 职责                                                                                   |
| ------------ | --------------------------------------------------- | -------------------------------------------------------------------------------------- |
| **前端**     | React 19 + TypeScript + Vite                        | 用户交互、任务选择、流式结果展示、历史管理、深色模式、设置面板                         |
| **后端**     | FastAPI + Pydantic + httpx + SQLAlchemy + aiosqlite | 路由分发、提示词构建、Ollama 调用、文件解析、文档导出、历史记录持久化、日志/限流中间件 |
| **数据库**   | SQLite (backend/data/app.db)                        | 历史记录永久存储                                                                       |
| **模型服务** | Ollama (qwen3.5:9b)                                 | 本地大语言模型推理                                                                     |

---

## 目录结构

```
my_first/
├── backend/
│   ├── main.py                  # FastAPI 应用入口，CORS 配置，路由挂载，lifespan（DB 初始化）
│   ├── db.py                    # SQLAlchemy async 引擎 + 会话工厂，SQLite 数据库位于 data/app.db
│   ├── logging_config.py        # 结构化日志配置（控制台 + 文件轮转）
│   ├── pyproject.toml           # Python 依赖管理（uv）
│   ├── requirements.txt         # 依赖清单
│   ├── data/
│   │   └── app.db               # SQLite 数据库文件（运行时自动创建）
│   ├── models/
│   │   ├── schemas.py           # Pydantic 数据模型：TaskType 枚举、请求/响应模型（含 model/temperature）
│   │   └── history.py           # SQLAlchemy ORM 模型：HistoryRecord（id, task_type, content, result, style, token_count, created_at）
│   ├── routers/
│   │   ├── writing.py           # 写作 API 路由：upload / process / stream / export-docx / export-pdf
│   │   └── history.py           # 历史记录 CRUD 路由：GET / POST / DELETE（单条+全部）
│   ├── middleware/
│   │   ├── __init__.py          # RequestLoggingMiddleware（请求方法/路径/状态码/耗时日志）
│   │   └── rate_limit.py        # RateLimitMiddleware（IP 滑动窗口限流，AI 端点每分钟 10 次）
│   ├── prompts/
│   │   └── writing.py           # 提示词模板（9 种风格）及诗词校验逻辑
│   ├── services/
│   │   ├── ollama_client.py     # Ollama HTTP 客户端（generate / generate_stream，支持自定义 model/temperature）
│   │   ├── file_parser.py       # 文件文本提取（PDF / DOCX / 纯文本）
│   │   ├── docx_export.py       # Markdown → Word 文档转换
│   │   ├── pdf_export.py        # Markdown → PDF 文档转换（fpdf2，中文字体支持）
│   │   ├── pptx_export.py       # Markdown → PPTX 演示文稿转换（python-pptx，4 种主题模板，6 种版式）
│   │   └── unsplash.py          # Unsplash 图片搜索服务（为 PPT 幻灯片获取配图）
│   └── tests/
│       ├── test_routers.py      # 路由接口测试
│       ├── test_file_parser.py  # 文件解析测试
│       ├── test_prompts.py      # 提示词构建测试
│       ├── test_pptx_export.py  # PPTX 导出测试
│       └── test_schemas.py      # 数据模型测试
├── frontend/
│   └── src/
│       ├── main.tsx             # React 入口
│       ├── App.tsx              # 根组件：全局状态管理、流式调用编排、深色模式、侧边栏折叠
│       ├── App.css              # 全局样式 + 深色模式变量 + 响应式媒体查询
│       ├── components/
│       │   ├── WritingForm.tsx   # 任务选择标签页、文本输入（字数统计）、文件上传、风格/语言选项、离线降级
│       │   ├── WritingForm.css   # 表单样式 + 离线横幅
│       │   ├── ResultPanel.tsx   # Markdown 渲染、编辑、复制、多格式导出（Word/PDF/TXT/MD）、对比视图
│       │   ├── ResultPanel.css   # 结果面板样式 + 对比视图布局
│       │   ├── HistoryPanel.tsx  # 历史列表：搜索、筛选、删除、清空（后端 API）
│       │   ├── ConfirmDialog.tsx # 通用确认对话框组件
│       │   ├── ConfirmDialog.css # 确认对话框样式
│       │   ├── SettingsPanel.tsx # 模型名称 + 温度参数设置面板
│       │   └── SettingsPanel.css # 设置面板样式
│       ├── services/
│       │   ├── api.ts           # Axios 客户端 + API 函数（流式/非流式/上传/导出/健康检查）
│       │   ├── history.ts       # 后端历史记录 API 封装（getHistory / addHistory / removeHistory / clearHistory）
│       │   └── templates.ts     # Prompt 模板管理（保存/加载/删除，localStorage）
│       └── types/
│           └── index.ts         # TypeScript 类型定义、TaskType 常量、风格/语言选项
└── docs/                        # 文档目录
```

---

## 后端模块说明

### `main.py` — 应用入口

- 创建 FastAPI 实例（标题 `AI 写作助手`，版本 `1.3.1`）
- 使用 `lifespan` 上下文管理器，在启动时初始化数据库（`init_db()`）
- 配置 CORS 中间件，允许前端开发服务器跨域请求：
  - `http://localhost:5173`（Vite 开发服务器）
  - `http://localhost:3000`（备用端口）
- 挂载请求日志中间件（`RequestLoggingMiddleware`）和 IP 限流中间件（`RateLimitMiddleware`）
- 挂载写作路由 `writing_router`，前缀 `/api/writing`
- 挂载历史记录路由 `history_router`，前缀 `/api/history`
- 提供健康检查端点 `GET /api/health`，返回服务状态和当前模型名称

### `db.py` — 数据库配置

- 使用 SQLAlchemy async 引擎 + aiosqlite，数据库文件位于 `backend/data/app.db`
- 提供 `init_db()` 函数创建所有表
- 提供 `get_session()` 异步会话生成器，用于依赖注入

### `logging_config.py` — 日志配置

- 结构化日志输出（控制台格式化）
- 为请求日志中间件提供 logger 实例

### `models/schemas.py` — 数据模型

| 模型                  | 说明                                                                                                                  |
| --------------------- | --------------------------------------------------------------------------------------------------------------------- |
| `TaskType(str, Enum)` | 任务类型枚举：`generate`（生成）、`polish`（润色）、`translate`（翻译）、`summarize`（摘要）                          |
| `WritingRequest`      | 写作请求体：`task_type`、`content`、`style`、`target_lang`、`attachment_text`、`model`（可选）、`temperature`（可选） |
| `WritingResponse`     | 写作响应体：`task_type`、`result`（生成文本）、`token_count`（token 计数）                                            |
| `ExportRequest`       | 导出请求体：`content`（Markdown 内容）、`title`（文档标题）                                                           |
| `ExportPptxRequest`   | PPTX 导出请求体：`content`、`title`、`template`（主题模板）、`with_images`（是否配图）、`unsplash_key`                |
| `HistoryCreate`       | 历史记录创建请求：`task_type`、`content`、`result`、`style`、`token_count`                                            |
| `HistoryOut`          | 历史记录响应：含 `id`、`created_at` 等完整字段                                                                        |

### `models/history.py` — ORM 模型

SQLAlchemy ORM 模型 `HistoryRecord`，映射到 `history` 表：

| 字段          | 类型         | 说明            |
| ------------- | ------------ | --------------- |
| `id`          | Integer (PK) | 自增主键        |
| `task_type`   | String       | 任务类型        |
| `content`     | Text         | 输入内容        |
| `result`      | Text         | 生成结果        |
| `style`       | String       | 写作风格        |
| `token_count` | Integer      | Token 数量      |
| `created_at`  | DateTime     | 创建时间（UTC） |

### `routers/writing.py` — 写作 API 路由

提供六个核心端点，统一前缀 `/api/writing`：

| 端点           | 方法 | 功能                                                                                         |
| -------------- | ---- | -------------------------------------------------------------------------------------------- |
| `/upload`      | POST | 接收上传文件，调用 `file_parser.extract_text()` 提取文本，返回文件名、文本内容及字符数       |
| `/process`     | POST | 非流式写作处理，构建提示词后调用 `ollama_client.generate()`，返回完整结果                    |
| `/stream`      | POST | 流式写作处理，以 SSE 格式逐 token 返回。诗词请求走特殊路径                                   |
| `/export-docx` | POST | 接收 Markdown 文本，转换为 Word 文档，以二进制流返回                                         |
| `/export-pdf`  | POST | 接收 Markdown 文本，转换为 PDF 文档（fpdf2，中文支持），以二进制流返回                       |
| `/export-pptx` | POST | 接收 Markdown PPT 大纲，转换为 PPTX 演示文稿（支持主题模板和 Unsplash 配图），以二进制流返回 |

### `routers/history.py` — 历史记录路由

提供四个 CRUD 端点，统一前缀 `/api/history`：

| 端点    | 方法   | 功能                                   |
| ------- | ------ | -------------------------------------- |
| `/`     | GET    | 获取历史记录列表，支持关键词搜索、分页 |
| `/`     | POST   | 新增一条历史记录，返回 201             |
| `/{id}` | DELETE | 删除指定 ID 的历史记录，返回 204       |
| `/`     | DELETE | 清空全部历史记录，返回 204             |

### `middleware/` — 中间件

| 中间件                     | 说明                                                                                                              |
| -------------------------- | ----------------------------------------------------------------------------------------------------------------- |
| `RequestLoggingMiddleware` | 记录每个请求的方法、路径、状态码和处理耗时                                                                        |
| `RateLimitMiddleware`      | IP 滑动窗口限流，AI 生成端点（`/api/writing/process`、`/api/writing/stream`）每 IP 每分钟最多 10 次，超限返回 429 |

**诗词特殊处理逻辑**（`/stream` 端点内）：

1. 通过 `is_poetry_request()` 检测用户输入是否包含诗词关键词
2. 若为诗词请求，改用**非流式生成** + **重试校验**（最多 3 次）
3. 调用 `validate_poetry()` 验证每句汉字数量是否符合格律要求
4. 校验通过后，将完整文本逐字符以 SSE 事件形式发送

### `prompts/writing.py` — 提示词模板

包含 **9 种提示词模板**，覆盖各类写作场景：

| 模板常量              | 适用场景                        | 触发条件                               |
| --------------------- | ------------------------------- | -------------------------------------- |
| `GENERATE_PROMPT`     | 通用文章生成                    | `task_type=generate`，默认风格         |
| `POETRY_PROMPT`       | 古典诗词创作                    | `task_type=generate`，内容含诗词关键词 |
| `POLISH_PROMPT`       | 文本润色改写                    | `task_type=polish`                     |
| `TRANSLATE_PROMPT`    | 多语言翻译                      | `task_type=translate`                  |
| `SUMMARIZE_PROMPT`    | 文本摘要总结                    | `task_type=summarize`                  |
| `XIAOHONGSHU_PROMPT`  | 小红书爆款文案                  | `style=xiaohongshu`                    |
| `GONGZHONGHAO_PROMPT` | 微信公众号长文                  | `style=gongzhonghao`                   |
| `TOUTIAO_PROMPT`      | 今日头条文章                    | `style=toutiao`                        |
| `AI_DRAMA_PROMPT`     | AI 短剧脚本                     | `style=ai_drama`                       |
| `PPT_PROMPT`          | 演示文稿大纲（含 6 种版式标记） | `style=ppt`                            |

**核心函数**：

- `build_prompt()` — 根据任务类型和风格选择模板，注入内容和参数，自动追加附件内容
- `is_poetry_request()` — 正则匹配诗词关键词
- `validate_poetry()` — 校验诗词格律（提取汉字，按标点分句，检查每句字数）

### `services/ollama_client.py` — Ollama 客户端

通过 httpx 与本地 Ollama 服务通信，默认模型 `qwen3.5:9b`，支持自定义 model 和 temperature：

| 函数                                          | 模式   | 说明                                                                                        |
| --------------------------------------------- | ------ | ------------------------------------------------------------------------------------------- |
| `generate(prompt, model, temperature)`        | 非流式 | 发送 `POST /api/generate`（`stream=False`），返回完整文本和 token 计数                      |
| `generate_stream(prompt, model, temperature)` | 流式   | 发送 `POST /api/generate`（`stream=True`），返回 `AsyncGenerator`，逐行解析 JSON 提取 token |

- 统一设置 `think=False` 禁用模型思考链输出
- 超时时间：120 秒

### `services/file_parser.py` — 文件解析

| 文件类型         | 解析方式       | 依赖库      |
| ---------------- | -------------- | ----------- |
| `.pdf`           | 逐页提取文本   | PyPDF2      |
| `.docx` / `.doc` | 提取段落文本   | python-docx |
| 纯文本类         | 多编码尝试解码 | 内置        |

- 文件大小上限：**10 MB**
- 纯文本编码尝试顺序：`utf-8` → `gbk` → `gb2312` → `latin-1`

### `services/docx_export.py` — Word 文档导出

将 Markdown 文本转换为 `.docx` 文件（内存中生成）：

| Markdown 元素    | 转换规则                 |
| ---------------- | ------------------------ |
| `# / ## / ###`   | 对应 1-3 级 Word 标题    |
| `- / * / +` 列表 | Word 无序列表            |
| `1. 2. 3.` 列表  | Word 有序列表            |
| `>` 引用         | 左缩进 + 斜体 + 灰色字体 |
| `---` / `***`    | 居中灰色分隔线           |
| `**粗体**`       | Word 粗体                |
| `*斜体*`         | Word 斜体                |

### `services/pdf_export.py` — PDF 文档导出

将 Markdown 文本转换为 `.pdf` 文件（内存中生成），基于 fpdf2：

- 支持中文字体渲染（自动查找系统中文字体）
- 解析 Markdown 标题、列表、引用、分隔线等元素
- 返回 `io.BytesIO` 字节流

### `services/pptx_export.py` — PPTX 演示文稿导出

将 Markdown PPT 大纲转换为 `.pptx` 文件（内存中生成），基于 python-pptx：

- **Markdown 解析**：识别 `## 标题`（幻灯片标题）、`- 项目符号`、`> 演讲备注`、`---`（分隔符）、`[layout: 版式名]`（版式标记）
- **幻灯片类型**：自动区分封面、内容页、结束页（检测"谢谢"、"致谢"、"Q&A"等关键词）
- **6 种版式**（内容页根据 `[layout: xxx]` 标记选择）：
  - `bullets` — 默认要点列表（标题 + 项目符号）
  - `stats` — 关键数据展示（圆角卡片内大数字 + 标签，多列并排）
  - `comparison` — 左右两栏对比（列标题 + 分割线 + 双栏内容）
  - `timeline` — 水平时间轴（节点圆点 + 上方标签 + 下方描述）
  - `quote` — 引用/金句（大引号装饰 + 居中文字 + 出处）
  - `grid` — 网格卡片（自适应 2~3 列，带顶部强调线）
- **4 种主题模板**：
  - `business`（商务蓝）— 默认
  - `minimal`（极简灰）
  - `green`（清新绿）
  - `warm`（暖色调）
- **图片支持**：可为内容幻灯片添加配图（右侧布局），图片由 Unsplash / Bing 服务提供
- **演讲备注**：嵌入到每张幻灯片的备注区域
- **幻灯片编号**：自动添加页码

### `services/unsplash.py` — Unsplash 图片搜索

为 PPT 幻灯片提供自动配图能力，通过 Unsplash API 搜索相关图片：

- `search_image(query, api_key)` — 搜索单张图片，自动清理标题中的 Markdown 格式
- `fetch_images_for_slides(slides, api_key)` — 并发获取多张图片（`asyncio.gather`）
- 无 API 密钥时优雅返回空结果，不影响 PPTX 生成
- 请求超时：10 秒

---

## 前端模块说明

### `App.tsx` — 根组件

全局状态管理与业务编排的中枢：

| 状态          | 类型            | 用途                              |                  |
| ------------- | --------------- | --------------------------------- |                  |
| `result`      | `string`        | 当前展示的生成结果文本            |                  |
| `loading`     | `boolean`       | 是否正在流式生成中                |                  |
| `tokenCount`  | `number`        | 已接收 token 数量                 |                  |
| `error`       | `string`        | 错误信息                          |                  |
| `online`      | `boolean \      | null`                             | 后端服务在线状态 |
| `history`     | `HistoryItem[]` | 历史记录列表                      |                  |
| `activeId`    | `string`        | 当前选中的历史记录 ID             |                  |
| `sidebarOpen` | `boolean`       | 移动端侧边栏展开状态              |                  |
| `theme`       | `string`        | 深色模式状态（system/light/dark） |                  |

**核心逻辑**：

1. 初始化时调用 `healthCheck()` 检测后端状态，从后端 API 加载历史记录
2. `handleSubmit` — 发起流式请求，通过回调逐步累加 token
3. `handleStop` — 通过 `AbortController` 中断正在进行的流式请求
4. `handleRegenerate` — 使用上次请求参数重新生成
5. 流式完成后，自动将结果保存到后端数据库
6. 深色模式三态循环：跟随系统 → 亮色 → 暗色，设置持久化到 localStorage
7. 移动端侧边栏通过汉堡菜单按钮控制折叠/展开
8. 快捷键监听：Ctrl+Enter 提交、Esc 停止生成、Ctrl+S 拦截

### `components/WritingForm.tsx` — 写作表单

- **任务类型切换**：标签页形式展示四种任务
- **文本输入区**：根据任务类型切换占位提示语，底部实时显示字数统计
- **文件上传**：调用 `/api/writing/upload` 提取文件文本，作为附件参考
- **风格选择**：9 种风格选项
- **目标语言**：翻译任务时显示，支持 6 种语言
- **离线降级**：接收 `online` prop，服务离线时禁用提交按钮并显示红色横幅引导信息

### `components/ResultPanel.tsx` — 结果面板

- 使用 react-markdown 渲染生成结果
- **结果编辑**：支持编辑/保存/取消，在导出前修改生成内容
- **对比视图**：润色/翻译任务左右对比原文与生成结果
- **一键复制**：成功/失败提示，按钮文字临时变为"已复制"/"复制失败"
- **多格式导出**：Word（.docx）、PDF（.pdf）、PPT（.pptx）、纯文本（.txt）、Markdown（.md）
- **"换一个"按钮**：用相同参数重新生成不同结果
- **"重新尝试"按钮**：请求失败后显示
- 显示 token 计数、加载状态

### `components/HistoryPanel.tsx` — 历史面板

- 展示历史记录列表，按时间倒序排列（数据来自后端 API）
- 支持关键词搜索（匹配内容和结果）
- 点击历史条目可恢复对应的生成结果
- 支持单条删除和一键清空（清空时弹出 ConfirmDialog 二次确认）

### `components/ConfirmDialog.tsx` — 确认对话框

- 通用二次确认组件，用于清空历史等破坏性操作
- 接收 `message`、`onConfirm`、`onCancel` 属性

### `components/SettingsPanel.tsx` — 设置面板

- 模型名称输入框（自定义 Ollama 模型）
- 温度参数滑块（0-2，步长 0.1）
- Unsplash Access Key 输入框（用于 PPT 配图，密码类型保护隐私）
- 设置值通过 props 回传到 App 组件

### `services/api.ts` — API 客户端

基于 Axios 封装 HTTP 请求，基础地址 `http://localhost:8000`，超时 120 秒：

| 函数                                                              | 说明                                                          |
| ----------------------------------------------------------------- | ------------------------------------------------------------- |
| `processWriting(req)`                                             | 非流式请求                                                    |
| `streamWriting(req, onToken, onDone, onError)`                    | 流式请求，使用原生 `fetch()` + `ReadableStream` 读取 SSE 事件 |
| `healthCheck()`                                                   | 健康检查                                                      |
| `uploadFile(file)`                                                | 文件上传                                                      |
| `downloadDocx(content, title)`                                    | 导出 Word，优先使用 File System Access API                    |
| `downloadPdf(content, title)`                                     | 导出 PDF，优先使用 File System Access API                     |
| `downloadPptx(content, title, template, withImages, unsplashKey)` | 导出 PPTX，支持主题模板和 Unsplash 配图，配图时超时 300 秒    |

> **注意**：`streamWriting` 使用原生 `fetch()` 而非 Axios，因为 Axios 不支持流式读取响应体。

### `services/history.ts` — 历史记录管理

基于后端 API 的历史记录管理（数据持久化在 SQLite 中）：

- 提供 `getHistory()` / `addHistory()` / `removeHistory()` / `clearHistory()` 四个异步函数
- 所有操作通过 axios 调用 `/api/history` 端点
- 历史记录永久保留，由后端 SQLite 存储

### `services/templates.ts` — Prompt 模板管理

基于 localStorage 的模板持久化方案：

- 存储键：`writing_templates`
- 提供 `getTemplates()` / `saveTemplate()` / `deleteTemplate()` 三个方法
- 模板包含名称、任务类型、内容、风格等字段

---

## 数据流

### 主流程：流式写作生成

```
用户操作                    前端                         后端                        Ollama
  │                         │                            │                           │
  │  1. 选择任务 + 输入内容   │                            │                           │
  │────────────────────────►│                            │                           │
  │                         │  2. POST /api/writing/stream│                           │
  │                         │───────────────────────────►│                            │
  │                         │                            │  3. build_prompt()         │
  │                         │                            │  (选择模板+注入参数)        │
  │                         │                            │  4. POST /api/generate     │
  │                         │                            │──────────────────────────►│
  │                         │     SSE: data: "token"     │  5. 逐行返回 JSON token    │
  │                         │◄───────────────────────────│◄──────────────────────────│
  │  6. 实时渲染 Markdown    │                            │                           │
  │◄────────────────────────│                            │                           │
  │                         │     SSE: data: [DONE]      │                           │
  │                         │◄───────────────────────────│                           │
  │                         │  7. addHistory() → POST /api/history → SQLite         │
```

### 文件上传流程

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

### Word 导出流程

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

### PPTX 导出流程

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

## 关键设计决策

### 1. SSE 流式输出

采用 Server-Sent Events 而非 WebSocket。SSE 是单向通信，符合"请求→流式响应"的使用场景，实现简单。前端通过 `AbortController` 支持中断生成。

### 2. 诗词非流式 + 重试校验

诗词请求使用非流式生成，后端进行格律校验，最多重试 3 次。因为流式输出无法在生成完成前校验整体格式，需要完整输出后再校验字数。

### 3. 多编码文件解析

纯文本文件按 `utf-8 → gbk → gb2312 → latin-1` 顺序尝试解码，覆盖中文用户常见编码场景。

### 4. SQLite 历史记录持久化

历史记录从 localStorage 迁移到后端 SQLite 数据库（SQLAlchemy + aiosqlite），实现跨设备/跨浏览器数据共享。

### 5. 提示词模板系统

为不同写作场景设计独立提示词模板，每个模板内嵌平台特定的写作规则和格式规范，通过 `style` 参数路由到对应模板。

### 6. Word 导出策略

前端优先使用 `showSaveFilePicker`（可选择保存位置），回退到 Blob URL 下载。后端在内存中生成 `.docx`，不写入磁盘。文件名使用 URL 编码支持中文。

### 7. IP 限流中间件

采用滑动窗口算法，按 IP 地址限制 AI 生成端点的请求频率（每分钟 10 次）。仅限制 `/api/writing/process` 和 `/api/writing/stream`，不影响文件上传、导出等其他端点。

### 8. 深色模式实现

使用 CSS 自定义属性（CSS Variables）实现主题切换，通过 `data-theme` 属性控制。三态循环：跟随系统 → 亮色 → 暗色，偏好设置持久化到 localStorage。

### 9. PPTX 导出策略

后端在内存中生成 `.pptx` 文件，不写入磁盘。采用 Markdown 大纲格式作为中间表示，解析为结构化幻灯片数据后再生成演示文稿。AI Prompt 指导 LLM 在标题中嵌入 `[layout: xxx]` 版式标记，解析器提取后分发到 6 种专用渲染器（bullets、stats、comparison、timeline、quote、grid），实现多样化排版。4 种预置主题通过颜色方案和字体配置区分，支持自动识别封面、内容页和结束页。Unsplash / Bing 配图为可选功能，无 API Key 时不影响基本导出。
