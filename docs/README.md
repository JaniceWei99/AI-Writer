# AI 写作助手

## 项目简介

**AI 写作助手** 是一个基于大语言模型（LLM）的智能写作辅助工具，采用前后端分离架构开发。后端使用 Python FastAPI 框架，前端使用 React + TypeScript + Vite 构建，通过 Ollama 本地部署的大模型提供 AI 能力。

本项目支持文章生成、文本润色、文本翻译、文本摘要、附件上传解析、多格式结果导出（Word/TXT/Markdown/PDF）、流式生成输出、历史记录数据库持久化、深色模式、模型参数设置、Prompt 模板管理等功能，旨在为用户提供高效、便捷的 AI 写作体验。

---

## 技术栈

### 后端

| 技术 | 说明 |
| --- | --- |
| Python 3.10+ | 编程语言 |
| FastAPI | Web 框架 |
| Pydantic | 数据校验与序列化 |
| Uvicorn | ASGI 服务器 |
| httpx | 异步 HTTP 客户端（调用 Ollama API） |
| SQLAlchemy + aiosqlite | 异步 ORM 与 SQLite 数据库 |
| python-docx | Word 文档生成与导出 |
| fpdf2 | PDF 文档生成与导出 |
| PyPDF2 | PDF 文件解析 |
| python-multipart | 文件上传支持 |
| uv | 依赖管理工具 |

### 前端

| 技术 | 说明 |
| --- | --- |
| React 19 | UI 框架 |
| TypeScript | 类型安全的 JavaScript |
| Vite 8 | 构建工具与开发服务器 |
| Axios | HTTP 请求库 |
| react-markdown | Markdown 渲染组件 |

### LLM

| 技术 | 说明 |
| --- | --- |
| Ollama | 本地大模型运行时 |
| qwen3.5:9b | 默认使用模型 |

---

## 功能特性

### 1. 文章生成

根据用户输入的主题和要求，自动生成文章内容。支持多种写作风格：

- **通用风格**：文学
- **考试风格**：上海高考作文
- **新媒体风格**：小红书爆款、公众号文案、头条文案、AI 短剧脚本
- **诗词创作**：五言绝句、七言绝句、五言律诗、七言律诗

### 2. 文本润色

对用户提供的文本进行润色优化，提升文章质量和可读性。

### 3. 文本翻译

支持多语言互译，目前支持以下语言：英语、中文、日语、韩语、法语、德语。

### 4. 文本摘要

对长文本自动生成摘要，提取核心要点。

### 5. 附件上传

支持上传多种格式的文件作为输入：

- **文档格式**：PDF、Word（.docx）、TXT、Markdown（.md）
- **数据格式**：CSV、JSON、XML
- **网页格式**：HTML
- **文件大小限制**：最大 10MB

### 6. 多格式导出

支持将 AI 生成的结果导出为多种格式：

- **Word（.docx）**：支持系统"另存为"对话框选择保存路径
- **纯文本（.txt）**：客户端直接生成下载
- **Markdown（.md）**：客户端直接生成下载
- **PDF（.pdf）**：后端使用 fpdf2 生成，支持中文

### 7. 流式生成

采用 SSE（Server-Sent Events）实现流式输出，实时展示 AI 生成内容，无需等待全部生成完毕。

### 8. 历史记录

- 自动保存每次生成的历史记录至后端 SQLite 数据库
- 支持关键词搜索历史记录
- 自动清理 30 天前的过期记录
- 换浏览器/清缓存不丢失数据

### 9. 结果编辑与重新生成

- 支持在导出前编辑 AI 生成的内容
- "换一个"按钮，用相同参数重新生成不同结果
- 请求失败后显示重试按钮

### 10. 深色模式

支持三种主题模式手动切换：跟随系统、亮色、暗色，设置自动持久化。

### 11. 模型/参数设置

可在设置面板中自定义模型名称和生成温度（temperature），无需修改代码。

### 12. Prompt 模板管理

支持保存和复用常用的写作指令模板，避免重复输入。模板存储在浏览器本地。

### 13. 润色/翻译对比视图

润色和翻译任务完成后，可点击"对比原文"按钮左右对比原文与结果。

### 14. 快捷键

- `Ctrl+Enter`：提交请求
- `Esc`：停止生成
- `Ctrl+S`：拦截浏览器保存

### 15. 后端日志与限流

- 结构化日志记录每个请求的方法、路径、状态码和耗时
- IP 限流保护 AI 生成端点（每 IP 每分钟最多 10 次）

### 16. 移动端适配

- 768px 以下侧边栏可折叠/展开
- Ollama 离线时禁用提交按钮并显示引导提示

---

## 快速启动

### 前置条件

1. **Python 3.10+**：确保已安装 Python 3.10 或更高版本
2. **Node.js**：确保已安装 Node.js（推荐 18+）
3. **uv**：Python 依赖管理工具，安装方式参考 [uv 官方文档](https://docs.astral.sh/uv/)
4. **Ollama**：本地大模型运行时，安装方式参考 [Ollama 官方网站](https://ollama.ai/)

### 1. 启动 Ollama 并拉取模型

```bash
# 启动 Ollama 服务（确保运行在 localhost:11434）
ollama serve

# 拉取默认模型
ollama pull qwen3.5:9b
```

### 2. 安装并启动后端

```bash
cd backend

# 使用 uv 安装依赖
uv sync

# 启动后端服务（默认端口 8000）
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

后端服务启动后，可访问 API 文档：http://localhost:8000/docs

### 3. 安装并启动前端

```bash
cd frontend

# 安装依赖
npm install

# 启动开发服务器（默认端口 5173）
npm run dev
```

前端启动后，在浏览器中访问：http://localhost:5173

---

## 项目结构

```
my_first/
├── backend/                    # 后端（Python FastAPI）
│   ├── main.py                 # 应用入口，FastAPI 实例、CORS、日志、限流、数据库初始化
│   ├── db.py                   # SQLite + SQLAlchemy 异步数据库配置
│   ├── logging_config.py       # 结构化日志配置
│   ├── models/
│   │   ├── schemas.py          # Pydantic 数据模型定义
│   │   └── history.py          # 历史记录 ORM 模型（HistoryRecord）
│   ├── routers/
│   │   ├── writing.py          # 写作相关 API 路由
│   │   └── history.py          # 历史记录 CRUD API 路由
│   ├── middleware/
│   │   ├── __init__.py         # 请求日志中间件
│   │   └── rate_limit.py       # IP 限流中间件
│   ├── services/
│   │   ├── ollama_client.py    # Ollama API 调用客户端
│   │   ├── file_parser.py      # 附件文件解析服务
│   │   ├── docx_export.py      # Word 文档导出服务
│   │   └── pdf_export.py       # PDF 文档导出服务
│   ├── prompts/
│   │   └── writing.py          # 写作提示词模板
│   ├── data/                   # SQLite 数据库文件目录
│   ├── tests/                  # 测试目录
│   ├── pyproject.toml          # 项目配置与依赖声明
│   └── requirements.txt        # 依赖列表（备用）
├── frontend/                   # 前端（React + TypeScript + Vite）
│   └── src/
│       ├── App.tsx             # 根组件，状态管理与流式逻辑
│       ├── components/
│       │   ├── WritingForm.tsx  # 任务选择、文本输入、附件上传、模板管理
│       │   ├── ResultPanel.tsx  # 结果渲染、编辑、多格式导出、对比视图
│       │   ├── HistoryPanel.tsx # 历史记录与关键词搜索
│       │   ├── SettingsPanel.tsx# 模型/参数设置面板
│       │   └── ConfirmDialog.tsx# 确认对话框组件
│       ├── services/
│       │   ├── api.ts          # API 请求函数（含多格式导出）
│       │   ├── history.ts      # 后端历史记录 API 客户端
│       │   └── templates.ts    # Prompt 模板管理
│       └── types/
│           └── index.ts        # TypeScript 类型定义与常量
├── docs/                       # 文档目录
└── .vscode/                    # VS Code 编辑器配置
```
