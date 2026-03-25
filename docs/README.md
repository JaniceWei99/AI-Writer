# AI 写作助手 v1.3.1

> 基于本地大模型的全能写作工具，支持多风格文章生成、PPT 多版式导出、诗词创作、多语言翻译，数据完全本地化，隐私无忧。

## 项目简介

**AI 写作助手**是一个前后端分离的智能写作平台。后端基于 Python FastAPI，前端使用 React + TypeScript + Vite，通过 Ollama 本地部署大模型（默认 qwen3.5:9b）提供 AI 能力。所有数据存储在本地 SQLite 数据库，不依赖任何云端服务。

### 核心亮点

- **8 种写作风格**：文学、高考作文、小红书爆款、公众号文案、头条文案、AI 短剧脚本、PPT 大纲、古典诗词
- **PPT 专业导出**：4 种主题配色 × 6 种幻灯片版式，AI 自动选择最佳排版
- **5 种导出格式**：Word / PDF / PPT / TXT / Markdown
- **完全本地运行**：Ollama + SQLite，无需联网，无数据泄露风险
- **实时流式输出**：SSE 技术逐字呈现，无需等待

---

## 功能全景

| 模块           | 功能         | 说明                                                                   |
| -------------- | ------------ | ---------------------------------------------------------------------- |
| **文章生成**   | 多风格创作   | 文学 / 上海高考作文 / 小红书爆款 / 公众号文案 / 头条文案 / AI 短剧脚本 |
| **PPT 生成**   | 多版式排版   | 6 种版式自动匹配：bullets、stats、comparison、timeline、quote、grid    |
| **诗词创作**   | 古典格律     | 五言/七言绝句、五言/七言律诗，含字数校验与自动重试                     |
| **文本润色**   | 内容优化     | 改善行文质量与可读性，支持原文对比视图                                 |
| **多语言翻译** | 6 种语言     | 中/英/日/韩/法/德互译，支持原文对比                                    |
| **文本摘要**   | 要点提取     | 长文自动生成结构化摘要                                                 |
| **附件上传**   | 8 种格式     | PDF / Word / TXT / Markdown / CSV / JSON / XML / HTML（最大 10MB）     |
| **多格式导出** | 5 种格式     | Word(.docx) / PDF(.pdf) / PPT(.pptx) / TXT(.txt) / Markdown(.md)       |
| **历史记录**   | 数据库持久化 | SQLite 存储，关键词搜索，换浏览器不丢失                                |

---

## PPT 生成系统

AI 写作助手的 PPT 功能支持从主题到成品演示文稿的一键生成。

### 主题模板

| 模板              | 配色方案 | 适用场景           |
| ----------------- | -------- | ------------------ |
| 商务蓝 (business) | 蓝色调   | 商业汇报、工作总结 |
| 极简灰 (minimal)  | 灰白色调 | 学术展示、技术分享 |
| 清新绿 (green)    | 绿色调   | 环保议题、教育培训 |
| 暖色调 (warm)     | 橙红色调 | 创意展示、团队分享 |

### 幻灯片版式

| 版式         | 用途     | 效果                  |
| ------------ | -------- | --------------------- |
| `bullets`    | 常规内容 | 标题 + 要点列表       |
| `stats`      | 数据展示 | 大数字卡片并排        |
| `comparison` | 对比分析 | 左右两栏对比 + 分割线 |
| `timeline`   | 时间线   | 水平轴 + 节点标注     |
| `quote`      | 金句引用 | 大引号装饰 + 居中引文 |
| `grid`       | 多项并列 | 2~3 列网格卡片        |

AI 根据每页内容自动标注最佳版式，同时支持 Bing 图片搜索自动配图。

---

## 技术栈

### 后端

| 技术                   | 说明                                |
| ---------------------- | ----------------------------------- |
| Python 3.10+           | 编程语言                            |
| FastAPI                | Web 框架                            |
| Pydantic               | 数据校验与序列化                    |
| Uvicorn                | ASGI 服务器                         |
| httpx                  | 异步 HTTP 客户端（调用 Ollama API） |
| SQLAlchemy + aiosqlite | 异步 ORM 与 SQLite 数据库           |
| python-docx            | Word 文档生成与导出                 |
| fpdf2                  | PDF 文档生成与导出                  |
| python-pptx            | PowerPoint 演示文稿生成与导出       |
| PyPDF2                 | PDF 文件解析                        |
| python-multipart       | 文件上传支持                        |
| uv                     | 依赖管理工具                        |

### 前端

| 技术           | 说明                  |
| -------------- | --------------------- |
| React 19       | UI 框架               |
| TypeScript     | 类型安全的 JavaScript |
| Vite 8         | 构建工具与开发服务器  |
| Axios          | HTTP 请求库           |
| react-markdown | Markdown 渲染组件     |

### LLM

| 技术       | 说明                           |
| ---------- | ------------------------------ |
| Ollama     | 本地大模型运行时               |
| qwen3.5:9b | 默认使用模型（可在设置中切换） |

---

## 用户体验

### 编辑与交互

- **结果编辑**：导出前可直接修改 AI 生成内容
- **重新生成**："换一个"按钮，相同参数生成不同结果
- **对比视图**：润色/翻译完成后左右对比原文与结果
- **复制反馈**：一键复制到剪贴板，显示成功/失败提示
- **字数统计**：输入区实时显示字符数
- **失败重试**：请求失败后显示重试按钮

### 个性化设置

- **深色模式**：跟随系统 / 亮色 / 暗色 三态切换
- **模型参数**：设置面板自定义模型名称和 temperature
- **Prompt 模板**：保存/加载/删除常用写作指令
- **Unsplash 配图**：设置面板输入 API Key 启用高质量配图

### 快捷键

| 快捷键       | 功能           |
| ------------ | -------------- |
| `Ctrl+Enter` | 提交请求       |
| `Esc`        | 停止生成       |
| `Ctrl+S`     | 拦截浏览器保存 |

### 移动端适配

- 768px 以下侧边栏自动折叠，汉堡菜单控制展开
- Ollama 离线时禁用提交并显示引导提示

---

## 后端能力

- **结构化日志**：记录每个请求的方法、路径、状态码和耗时
- **IP 限流**：AI 生成端点每 IP 每分钟最多 10 次请求
- **CORS 跨域**：支持前端开发服务器跨域访问
- **健康检查**：`GET /api/health` 实时检测服务状态
- **数据库持久化**：历史记录存储在 SQLite，不依赖浏览器缓存

---

## 快速启动

### 前置条件

1. **Python 3.10+**
2. **Node.js 18+**
3. **uv**：Python 依赖管理工具（[安装文档](https://docs.astral.sh/uv/)）
4. **Ollama**：本地大模型运行时（[下载地址](https://ollama.ai/)）

### 1. 启动 Ollama 并拉取模型

```bash
ollama serve
ollama pull qwen3.5:9b
```

### 2. 启动后端

```bash
cd backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

API 文档：http://localhost:8000/docs

### 3. 启动前端

```bash
cd frontend
npm install
npm run dev
```

访问：http://localhost:5173

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
│   │   └── history.py          # 历史记录 ORM 模型
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
│   │   ├── pdf_export.py       # PDF 文档导出服务
│   │   ├── pptx_export.py      # PPT 演示文稿导出服务（6 种版式）
│   │   └── unsplash.py         # 图片搜索服务（Bing / Unsplash）
│   ├── prompts/
│   │   └── writing.py          # 写作提示词模板
│   ├── data/                   # SQLite 数据库文件目录
│   └── pyproject.toml          # 项目配置与依赖声明
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
│       │   ├── api.ts          # API 请求函数（含多格式导出及 PPTX 导出）
│       │   ├── history.ts      # 后端历史记录 API 客户端
│       │   └── templates.ts    # Prompt 模板管理
│       └── types/
│           └── index.ts        # TypeScript 类型定义与常量
├── tests/                      # 测试目录（117 个测试用例）
└── docs/                       # 项目文档
    ├── README.md               # 项目介绍（本文件）
    ├── SPEC.md                 # 详细功能规格说明
    ├── ARCHITECTURE.md         # 架构设计文档
    └── CHANGELOG.md            # 版本更新日志
```

---

## 版本历史

| 版本   | 日期       | 主要变更                                             |
| ------ | ---------- | ---------------------------------------------------- |
| v1.3.1 | 2026-03-23 | 版本号统一，PPT 生成功能稳定版本                     |
| v1.3.0 | 2026-03-23 | PPT 多版式排版系统：6 种幻灯片版式 + AI 自动版式标注 |
| v1.2.0 | 2026-03-22 | PPT 导出功能：4 种主题模板 + Unsplash/Bing 配图      |
| v1.1.0 | 2026-03-22 | 结果编辑、深色模式、数据库持久化、限流、设置面板     |
| v1.0.0 | 2026-03-21 | 核心写作功能、流式输出、附件上传、Word 导出          |

详细更新日志见 [CHANGELOG.md](./CHANGELOG.md)。

---

## 许可证

MIT License
