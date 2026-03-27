---
name: ai-writer
description: "AI 写作助手项目开发技能：熟悉全部 5 个 Router、9 个组件、20+ API 端点、15 个 Prompt 模板的架构，可直接执行添加功能/修 Bug/重构/写测试/更新文档等任务"
argument-hint: "<任务描述，如：添加知乎风格、修复历史搜索、新增批量生成接口>"
allowed-tools:
  - read
  - edit
  - grep
  - glob
  - exec
permissions:
  allow:
    - Read(**)
    - Write(backend/**)
    - Write(frontend/src/**)
    - Write(docs/**)
    - Write(tests/**)
    - Exec(cd *)
    - Exec(npm *)
    - Exec(uv *)
    - Exec(python3 *)
    - Exec(curl *)
    - Exec(git *)
    - Exec(kill *)
    - Exec(lsof *)
triggers:
  - user
  - model
---

# AI 写作助手 — 项目开发技能

你正在维护 **AI 写作助手 v1.5.0** 项目，一个基于多 LLM Provider 的本地写作 + PPT 生成工具。

---

## 项目架构

```
my_first/
├── backend/                       # FastAPI 后端
│   ├── main.py                    # 应用入口、CORS、SPA 托管、/api/health、/api/models
│   ├── db.py                      # SQLAlchemy async + SQLite（含轻量迁移）
│   ├── routers/
│   │   ├── writing.py             # /api/writing/{stream,process,refine,outline,expand-chapter,upload,export-*}
│   │   ├── history.py             # /api/history CRUD（用户隔离）
│   │   ├── styles.py              # /api/styles CRUD（自定义风格）
│   │   ├── auth.py                # /api/auth/{register,login,me}
│   │   └── analysis.py            # /api/analysis/quality（文本质量评分）
│   ├── models/
│   │   ├── schemas.py             # Pydantic 模型 (WritingRequest, RefineRequest, OutlineRequest 等)
│   │   ├── history.py             # HistoryRecord ORM（含 user_id FK）
│   │   ├── user.py                # User ORM（username + hashed_password）
│   │   └── custom_style.py        # CustomStyle ORM（name, slug, prompt_template）
│   ├── prompts/
│   │   └── writing.py             # 15 个 prompt 模板 + build_prompt() + STYLE_MAP + 诗词校验
│   ├── services/
│   │   ├── llm_provider.py        # 多 Provider 抽象层（ollama Chat API /api/chat + openai/deepseek/qwen）
│   │   ├── ollama_client.py       # Ollama Chat API 封装（legacy，用于诗词校验路径）
│   │   ├── auth.py                # JWT 认证（bcrypt + HS256，72h 过期）
│   │   ├── text_analysis.py       # 纯算法文本质量评分（可读性 0-100）
│   │   ├── docx_export.py         # Markdown → Word
│   │   ├── pdf_export.py          # Markdown → PDF（CJK 字体支持）
│   │   ├── pptx_export.py         # Markdown → PPT（6 版式 4 主题）
│   │   ├── unsplash.py            # 配图服务（Unsplash → Bing → picsum 降级）
│   │   └── file_parser.py         # 上传文件解析（PDF/Word/PPT/TXT 等 10+ 格式）
│   └── middleware/
│       ├── __init__.py            # 请求日志中间件
│       └── rate_limit.py          # IP 限流（10 req/60s）
├── frontend/                      # React + TypeScript + Vite
│   └── src/
│       ├── App.tsx                # 主应用（主题、认证、历史、标准/长文模式切换）
│       ├── components/
│       │   ├── WritingForm.tsx     # 输入表单（模式切换、任务类型、语气控制、字数目标、快速启动、高级选项折叠）
│       │   ├── ResultPanel.tsx     # 结果展示 + 快速启动卡片 + 字数进度 + 溢出菜单 + 5 格式导出 + 对比视图
│       │   ├── HistoryPanel.tsx    # 侧边栏历史记录（搜索、风格标签显示）
│       │   ├── SettingsPanel.tsx   # 设置面板（模型/温度/Provider 信息）
│       │   ├── AuthPanel.tsx       # 用户认证（登录/注册/登出）
│       │   ├── QualityPanel.tsx    # 文本质量评分面板（4 维度 0-100 分）
│       │   ├── LongFormPanel.tsx   # 长文分章节生成（大纲→逐章展开）
│       │   ├── StyleEditor.tsx     # 自定义风格编辑器（CRUD）
│       │   └── ConfirmDialog.tsx   # 通用确认弹窗
│       ├── services/
│       │   ├── api.ts             # Axios + SSE 流式请求 + 自定义风格 CRUD + 文件操作
│       │   ├── auth.ts            # JWT 认证（localStorage 存储 + Bearer 注入）
│       │   ├── history.ts         # 历史 API 封装（自动注入 Auth Header）
│       │   └── templates.ts       # Prompt 模板管理（localStorage）
│       └── types/index.ts         # 类型定义 + STYLE_LABELS + TASK_LABELS + 选项列表
├── docs/                          # 文档（中英双语 + 竞品分析 + HTML 报告）
├── tests/                         # 前后端测试
├── Dockerfile                     # 多阶段构建（Node 构建前端 → Python 运行后端）
├── docker-compose.yml             # app + ollama 服务编排
├── .env.example                   # 环境变量模板
├── start.bat / start.command      # 一键启动脚本
```

---

## 全部 API 端点

### 写作 `/api/writing/`

| 方法   | 路径                    | 说明                     | 请求体                 |
|--------|------------------------|--------------------------|------------------------|
| POST   | `/stream`              | 流式写作（SSE）          | `WritingRequest`       |
| POST   | `/process`             | 非流式写作               | `WritingRequest`       |
| POST   | `/refine`              | 继续优化/多轮对话        | `RefineRequest`        |
| POST   | `/outline`             | 生成长文大纲（流式）     | `OutlineRequest`       |
| POST   | `/expand-chapter`      | 展开单个章节（流式）     | `ExpandChapterRequest` |
| POST   | `/upload`              | 上传参考文件             | `multipart/form-data`  |
| POST   | `/export-docx`         | 导出 Word                | `ExportRequest`        |
| POST   | `/export-pdf`          | 导出 PDF                 | `ExportRequest`        |
| POST   | `/export-pptx`         | 导出 PowerPoint          | `ExportPptxRequest`    |

### 历史 `/api/history/`

| 方法   | 路径             | 说明                    | 备注                     |
|--------|-----------------|-------------------------|--------------------------|
| GET    | `/`             | 列表/搜索历史           | 按 user_id 隔离，支持 keyword/limit/offset |
| POST   | `/`             | 创建记录                | `HistoryCreate`          |
| DELETE | `/{history_id}` | 删除单条                |                          |
| DELETE | `/`             | 清空全部                |                          |

### 自定义风格 `/api/styles/`

| 方法   | 路径             | 说明            | 备注                              |
|--------|-----------------|-----------------|-----------------------------------|
| GET    | `/`             | 列表自定义风格  |                                   |
| POST   | `/`             | 创建风格        | slug 格式 `^[a-z][a-z0-9_]{1,62}$`，内置 slug 受保护 |
| PUT    | `/{style_id}`   | 更新风格        |                                   |
| DELETE | `/{style_id}`   | 删除风格        |                                   |

### 认证 `/api/auth/`

| 方法   | 路径        | 说明              | 备注                         |
|--------|------------|-------------------|------------------------------|
| POST   | `/register`| 注册              | username 2-32 字符，password ≥4 |
| POST   | `/login`   | 登录              | 返回 JWT token               |
| GET    | `/me`      | 获取当前用户      | 需 Bearer token              |

### 分析 `/api/analysis/`

| 方法   | 路径        | 说明              | 备注                         |
|--------|------------|-------------------|------------------------------|
| POST   | `/quality` | 文本质量评分      | 纯算法，返回 readability_score 0-100 |

### 全局

| 方法   | 路径           | 说明                |
|--------|---------------|---------------------|
| GET    | `/api/health`  | 健康检查 + Provider 信息 |
| GET    | `/api/models`  | 列出可用模型        |

---

## 数据库模型

### `users` 表
| 字段              | 类型         | 说明                     |
|-------------------|-------------|--------------------------|
| `id`              | int PK      | 自增主键                 |
| `username`        | str(64)     | 唯一，有索引             |
| `hashed_password` | str(128)    | bcrypt 哈希              |
| `created_at`      | datetime    | UTC 创建时间             |

### `history` 表
| 字段          | 类型       | 说明                        |
|---------------|-----------|------------------------------|
| `id`          | int PK    | 自增主键                     |
| `user_id`     | int FK    | → users.id，可为 NULL（匿名）|
| `task_type`   | str(32)   | generate/polish/translate/summarize |
| `content`     | Text      | 用户输入内容                 |
| `result`      | Text      | 生成结果                     |
| `style`       | str(64)   | 使用的风格 slug              |
| `token_count` | int       | token 数                     |
| `created_at`  | datetime  | UTC 创建时间                 |

### `custom_styles` 表
| 字段              | 类型       | 说明                       |
|-------------------|-----------|----------------------------|
| `id`              | int PK    | 自增主键                   |
| `name`            | str(64)   | 显示名称                   |
| `slug`            | str(64)   | 唯一标识（有索引）         |
| `prompt_template` | Text      | Prompt 模板，必须含 `{content}` |
| `description`     | str(256)  | 描述                       |
| `created_at`      | datetime  | UTC 创建时间               |
| `updated_at`      | datetime  | UTC 更新时间               |

### DB 迁移说明

`db.py` 的 `init_db()` 中包含轻量迁移逻辑：
- 自动创建所有表（`create_all`）
- 用 `ALTER TABLE history ADD COLUMN user_id` 为旧表添加 user_id 列（try/except 忽略已存在情况）

---

## 关键环境变量

| 变量                | 默认值                           | 说明                     |
|---------------------|----------------------------------|--------------------------|
| `LLM_PROVIDER`      | `ollama`                         | 激活的 Provider（ollama/openai/deepseek/qwen） |
| `OLLAMA_BASE_URL`   | `http://localhost:11434`         | Ollama 地址              |
| `OLLAMA_MODEL`      | `qwen3.5:9b`                    | Ollama 默认模型          |
| `OLLAMA_NUM_GPU`    | `99`                             | GPU 最大层数             |
| `OLLAMA_NUM_PREDICT`| `4096`                           | 最大生成 token 数        |
| `OPENAI_API_KEY`    | —                                | OpenAI API 密钥          |
| `OPENAI_BASE_URL`   | `https://api.openai.com/v1`     | OpenAI 兼容地址          |
| `OPENAI_MODEL`      | `gpt-4o`                        | OpenAI 默认模型          |
| `DEEPSEEK_API_KEY`  | —                                | DeepSeek API 密钥        |
| `DEEPSEEK_BASE_URL` | `https://api.deepseek.com/v1`   | DeepSeek 地址            |
| `DEEPSEEK_MODEL`    | `deepseek-chat`                 | DeepSeek 默认模型        |
| `QWEN_API_KEY`      | —                                | 通义千问 API 密钥        |
| `QWEN_BASE_URL`     | `https://dashscope.aliyuncs.com/compatible-mode/v1` | 千问地址 |
| `QWEN_MODEL`        | `qwen-plus`                     | 千问默认模型             |
| `JWT_SECRET`        | 随机生成                         | JWT 签名密钥             |
| `JWT_EXPIRE_HOURS`  | `72`                             | Token 过期时间（小时）   |
| `CORS_ORIGINS`      | `localhost:5173,localhost:3000`  | 允许的前端来源           |
| `DATABASE_URL`      | `sqlite+aiosqlite:///backend/data/app.db` | 数据库连接串   |
| `VITE_API_BASE`     | `""`（同源）                     | 前端 API 地址（构建时嵌入） |
| `UNSPLASH_ACCESS_KEY`| —                               | Unsplash 配图密钥（可选） |

---

## 常用命令

```bash
# 启动后端（热重载）
cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload

# 启动前端开发服务器
cd frontend && npm run dev

# 前端构建
cd frontend && npm run build

# 前端类型检查
cd frontend && npx tsc --noEmit

# Vite 构建（跳过 tsc 严格模式）
cd frontend && npx vite build

# 后端测试
cd backend && uv run pytest ../tests/backend/ -v

# 前端测试
cd frontend && npx vitest run
```

---

## 任务类型 (TaskType)

- `generate` — 文章生成（支持多种风格）
- `polish` — 文本润色
- `translate` — 文本翻译
- `summarize` — 文本摘要

## 写作风格列表

内置风格定义在 `frontend/src/types/index.ts` 的 `STYLE_OPTIONS` / `TEXT_STYLE_OPTIONS` / `STYLE_LABELS` 和 `backend/prompts/writing.py` 的 `STYLE_MAP`：

| value          | 前端标签     | 说明                        |
|----------------|-------------|------------------------------|
| `""`           | 默认        | 通用写作                     |
| `literary`     | 文学        | 文学风格                     |
| `sh_gaokao`    | 上海高考作文 | 高考作文体                   |
| `xiaohongshu`  | 小红书爆款   | 小红书文案                   |
| `gongzhonghao` | 公众号文案   | 微信公众号                   |
| `toutiao`      | 头条文案     | 今日头条                     |
| `zhihu`        | 知乎回答     | 知乎高赞回答                 |
| `ai_drama`     | AI短剧脚本   | 短视频剧本                   |
| `ppt`          | 生成PPT     | PPT 大纲（切换至 PPT 模式）  |

用户还可通过 `StyleEditor` 创建自定义风格，存入 `custom_styles` 表，slug 作为风格值传入 API。

## Prompt 模板清单

`backend/prompts/writing.py` 中定义的所有模板：

| 常量                     | 用途                     |
|--------------------------|--------------------------|
| `GENERATE_PROMPT`        | 通用文章生成             |
| `POETRY_PROMPT`          | 古典诗词（自动重试校验）  |
| `POLISH_PROMPT`          | 文本润色                 |
| `TRANSLATE_PROMPT`       | 翻译（含 target_lang）    |
| `SUMMARIZE_PROMPT`       | 文本摘要                 |
| `XIAOHONGSHU_PROMPT`     | 小红书文案               |
| `GONGZHONGHAO_PROMPT`    | 公众号文案               |
| `TOUTIAO_PROMPT`         | 头条文案                 |
| `ZHIHU_PROMPT`           | 知乎回答                 |
| `AI_DRAMA_PROMPT`        | AI 短剧脚本              |
| `SH_GAOKAO_PROMPT`       | 上海高考作文             |
| `PPT_PROMPT`             | PPT 大纲（6 布局格式要求）|
| `OUTLINE_PROMPT`         | 长文大纲生成             |
| `EXPAND_CHAPTER_PROMPT`  | 章节展开                 |
| `REFINE_PROMPT`          | 多轮对话优化             |

关键函数：
- `build_prompt(task_type, content, style, target_lang, attachment_text, custom_prompt_template)` — 构建完整 prompt
- `build_refine_prompt(previous_result, feedback)` — 构建继续优化 prompt
- `build_outline_prompt(content, style)` — 构建大纲生成 prompt
- `build_expand_chapter_prompt(outline, chapter_title, chapter_desc, style)` — 构建章节展开 prompt
- `is_poetry_request(content)` — 检测是否诗词请求
- `validate_poetry(text, content)` — 校验诗词格律（字数），不合格自动重试最多 3 次

---

## PPT 生成系统

- **4 主题**：business（商务蓝）、minimal（简约白）、green（清新绿）、warm（暖色调）
- **6 版式**：bullets（要点列表）、stats（数据统计）、comparison（对比）、timeline（时间线）、quote（引言）、grid（网格）
- **配图降级策略**：Unsplash（有 key）→ Bing 搜图（内容相关）→ picsum（随机兜底）
- **实现**：`backend/services/pptx_export.py`（595+ 行）

---

## 认证系统

- **算法**：JWT HS256 + bcrypt 密码哈希
- **过期**：72 小时
- **前端存储**：`localStorage`（`writing_auth_token` / `writing_auth_user`）
- **请求注入**：`history.ts` 的 axios interceptor 自动附加 `Authorization: Bearer {token}`
- **后端工具函数**：
  - `get_current_user_optional(request)` — 返回 user dict 或 None（用于历史/风格）
  - `get_current_user_required(request)` — 返回 user dict，无效则抛 401

---

## 文本质量评分

- **端点**：`POST /api/analysis/quality`
- **实现**：`backend/services/text_analysis.py`（纯算法，无 AI 依赖）
- **指标**：
  - 基础统计：字符数、词数、句数、段落数、阅读时间
  - 4 维度评分（0-100）：句长得分、词汇多样性、段落均衡度、结构得分
  - 综合可读性评分（加权平均）
- **前端**：`QualityPanel.tsx` 集成在 `ResultPanel.tsx` 中

---

## 长文分章节生成

- **流程**：输入主题 → 生成大纲（`/outline`）→ 用户审阅/编辑 → 逐章展开（`/expand-chapter`）→ 合并终稿
- **前端**：`LongFormPanel.tsx`（独立面板，在 App.tsx 中通过"长文写作"标签切换）
- **后端**：复用 `llm_provider.generate_stream()`，prompts 在 `OUTLINE_PROMPT` 和 `EXPAND_CHAPTER_PROMPT`

---

## 前端关键数据流

### 标准写作流程
1. 用户在 `WritingForm` 中选择任务类型/风格/语气/输入内容（或通过 ResultPanel 快速启动卡片选择任务）
2. `App.tsx` 调用 `streamWriting()` 通过 SSE 流式接收
3. `ResultPanel` 实时展示结果 + 编辑/导出（溢出菜单）/对比/质量评分/字数进度
4. 完成后自动调用 `addHistory()` 保存历史记录（含 style 字段）
5. `HistoryPanel` 显示记录列表，每条显示任务类型标签和风格标签

### 继续优化流程
1. 用户在 `ResultPanel` 输入反馈
2. `App.tsx` 调用 `streamRefine()` 发送 `previous_result + feedback`
3. 新结果覆盖展示，同样保存历史

### 历史记录
- 侧边栏 `HistoryPanel` 显示所有记录
- 每条记录显示：**任务类型标签**（紫色）+ **风格标签**（绿色）+ 时间 + 内容预览
- PPT 记录使用橙色主题
- 风格标签支持内置风格（`STYLE_LABELS` 映射）和自定义风格（通过 `customStyles` prop 查找 slug→name）
- 点击记录可恢复结果到 ResultPanel

---

## CSS 设计令牌系统

前端通过 `index.css` 中的 CSS 自定义属性统一管理视觉令牌，组件 CSS 一律引用变量而非硬编码颜色：

| 类别 | 变量前缀 | 说明 |
|------|----------|------|
| 语义颜色 | `--color-ppt` / `--color-error` / `--color-success` / `--color-warning` / `--color-info` | 各含 bg/border/ring/hover/dark 变体 |
| 基础色彩 | `--text` / `--bg` / `--border` / `--accent` | 文本、背景、边框、强调色 |
| 阴影 | `--shadow-sm` / `--shadow-md` / `--shadow-lg` / `--shadow-xl` | 4 级阴影 |
| 间距 | `--sp-1` 到 `--sp-8` | 4px ~ 32px |
| 圆角 | `--radius-sm` / `--radius-md` / `--radius-lg` / `--radius-xl` | 4 级圆角 |
| 过渡 | `--ease-fast` / `--ease-base` / `--ease-slow` | 3 种速度 |
| z-index | `--z-dropdown` / `--z-modal` / `--z-toast` | 层级管理 |

**暗色模式**：`prefers-color-scheme: dark` 自动切换 + `data-theme="dark"` 手动切换。
**共享动画**：`fadeIn` / `slideUp` / `pulse` / `blink` 统一在 `index.css` 中定义，组件 CSS 不再重复声明。
**无障碍**：全局 `focus-visible` 焦点环 + `prefers-reduced-motion` 支持。

### WAI-ARIA 无障碍规范

所有组件遵循 WAI-ARIA 模式：

- **对话框**（ConfirmDialog/SettingsPanel/AuthPanel/StyleEditor）：`role="dialog"/"alertdialog"` + `aria-modal` + `aria-labelledby` + 遮罩层 `role="presentation"`
- **错误提示**：`role="alert"`（WritingForm/ResultPanel/AuthPanel/QualityPanel/StyleEditor）
- **实时区域**：`aria-live="polite"` + `role="status"`（ResultPanel/LongFormPanel/App）
- **标签导航**：`role="tablist"` + `role="tab"` + `aria-selected`（App.tsx 写作模式）
- **可展开**：`aria-expanded`（App 侧边栏、QualityPanel）
- **辅助区域**：`role="complementary"`（HistoryPanel）
- **图标按钮**：18+ 个 `aria-label`

> **修改组件时，必须保持已有的无障碍属性不被删除**，新增交互元素需添加相应 ARIA 标注。

---

## 操作指南

### 启动开发环境

1. 检查 Ollama 是否运行：`curl -s http://localhost:11434/api/tags`
2. 启动后端：`cd backend && uv run uvicorn main:app --host 0.0.0.0 --port 8000 --reload`
3. 启动前端：`cd frontend && npm run dev`
4. 确认端口：后端 8000，前端 5173

### 添加新写作风格（内置）

1. **后端** `backend/prompts/writing.py`：在 `STYLE_MAP` 字典中添加新 key → prompt 指令
2. **前端** `frontend/src/types/index.ts`：
   - 在 `TEXT_STYLE_OPTIONS` 和 `STYLE_OPTIONS` 数组中添加 `{ value, label }`
   - 在 `STYLE_LABELS` 中添加 `slug: '显示名称'`
3. 风格名称（value/slug）前后端必须一致

### 添加新导出格式

1. 在 `backend/services/` 下创建导出服务模块
2. 在 `backend/routers/writing.py` 中添加新的 `/export-xxx` 端点
3. 在 `frontend/src/services/api.ts` 中添加下载函数
4. 在 `frontend/src/components/ResultPanel.tsx` 中添加导出按钮

### 添加新 API 端点

1. 在 `backend/routers/` 下合适的 router 中添加路由
2. 如需新的请求/响应模型，在 `backend/models/schemas.py` 中定义
3. 在 `backend/main.py` 中注册 router（如果是新文件）
4. 在 `frontend/src/services/api.ts` 中添加对应调用函数

### 添加新数据库模型

1. 在 `backend/models/` 下创建 ORM 模型（继承 `db.Base`）
2. 在 `backend/main.py` 中确保导入该模型（否则 `create_all` 不会创建表）
3. 如需为旧表加列，在 `db.py` 的 `init_db()` 中添加 `ALTER TABLE` 迁移（try/except 模式）

### Docker 部署

```bash
docker compose up -d
docker compose exec ollama ollama pull qwen3.5:9b
# 访问 http://<server-ip>:8000
```

---

## 测试

```
tests/
├── backend/
│   ├── conftest.py           # Pytest fixtures（测试 DB、客户端）
│   ├── test_file_parser.py   # 文件解析测试
│   ├── test_pptx_export.py   # PPT 导出测试
│   ├── test_prompts.py       # Prompt 构建测试
│   ├── test_routers.py       # API 端点测试
│   └── test_schemas.py       # Pydantic 模型测试
├── frontend/
│   ├── WritingForm.test.tsx   # 表单组件测试（含语气控制、字数目标、快速启动、高级选项折叠）
│   ├── ResultPanel.test.tsx   # 结果面板测试（含快速卡片、字数进度、溢出菜单）
│   ├── HistoryPanel.test.tsx  # 历史面板测试
│   ├── history.test.ts        # 历史服务测试
│   └── setup.ts               # 测试配置
├── scenarios/
│   ├── backend.md             # 后端测试场景
│   └── frontend.md            # 前端测试场景
├── run_tests.sh               # 测试运行脚本
└── README.md                  # 测试文档
```

---

## 文档

```
docs/
├── API.md / SPEC.md / ARCHITECTURE.md    # 技术文档
├── CHANGELOG.md                           # 变更记录
├── DEPLOYMENT.md / DEPLOY_Mac.md / DEPLOY_Windows.md  # 部署指南
├── README.md / README_En.md               # 项目概述
├── COMPETITIVE_ANALYSIS.md                # 竞品分析（Markdown，持续追加）
├── competitive_analysis.html              # 竞品分析（HTML 可视化报告）
├── AUTO_PUBLISH_COMPARISON.md             # 自动发布对比
├── AI写作助手项目介绍.pptx               # 项目介绍 PPT
├── gen_ppt.py                             # PPT 生成脚本
└── *_En.md                                # 英文版文档
```

---

## 注意事项

- 后端使用 `uv` 管理依赖，不要用 `pip install`
- 前端环境变量 `VITE_*` 是构建时嵌入的，运行时不可改
- `main.py` 支持 SPA 模式：如果 `frontend/dist` 存在，自动托管静态文件
- SQLite 数据库自动创建在 `backend/data/app.db`
- 所有核心配置通过环境变量覆盖，默认值保持本机开发兼容
- 已知问题：`LongFormPanel.tsx` 有一个未使用变量 `currentChapter`（tsc 严格模式报 TS6133），但 vite build 可正常通过

### LLM 调用架构

- **主入口**：`llm_provider.py`，所有写作 API 统一通过此模块调用 LLM
- **Ollama 使用 Chat API**（`/api/chat`），非旧版 Generate API（`/api/generate`）
- **Prompt 拆分**：`_prompt_to_messages()` 将 prompt 在内容标记处（`主题：`、`原文：`等）分为 system + user 消息，防止 chat 模型回显 prompt
- **模型过滤**：`_EXCLUDED_MODELS` 排除 OCR、Embedding 等非文本生成模型（deepseek-ocr、nomic-embed 等）
- **超时时间**：Ollama 300 秒，云端 Provider 120 秒
- `ollama_client.py` 是 legacy 模块，仅在诗词校验路径中使用，同样使用 `/api/chat`
- **开发时前端环境变量** `VITE_API_BASE` 应为空值（`VITE_API_BASE=`），请求通过 Vite proxy 转发到后端

---

## 竞品分析文档约定

文件：`docs/COMPETITIVE_ANALYSIS.md`

格式规则（每次写入时自动遵守，无需用户提醒）：

1. **新分析放在前面**：每次新分析以 `## YYYY-MM-DD 竞品对比分析` 为标题，插在已有分析之前
2. **完整独立**：每次分析是一个完整章节，包含概览、功能对比、优势、劣势、改进建议、总结
3. **表格对齐**：所有 Markdown 表格必须按 CJK 字符宽度对齐（中文字符占 2 格）
4. **保留历史**：不修改或删除已有的分析记录
5. **HTML 报告同步更新**：`docs/competitive_analysis.html` 是可视化版本，重大更新时需同步

---

## 项目统计

| 维度           | 数量  |
|----------------|-------|
| 后端 Router    | 5 个  |
| API 端点       | 20+   |
| 后端 Service   | 9 个  |
| ORM 模型       | 3 个  |
| Pydantic Schema| 7+    |
| Prompt 模板    | 15 个 |
| 前端组件       | 9 个  |
| 前端 Service   | 4 个  |
| 内置风格       | 9 个  |
| PPT 主题       | 4 个  |
| PPT 版式       | 6 个  |
| 任务类型       | 4 个  |
| 导出格式       | 5 种  |
| 支持文件格式   | 10+ 种|

---

当收到用户任务 `$ARGUMENTS` 时，请基于以上架构知识进行开发。
