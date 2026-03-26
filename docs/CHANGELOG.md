# 更新日志

本文件记录本项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

## [1.5.0] - 2026-03-26

### 新增

- **快速启动卡片**（P1）：ResultPanel 空状态显示 3 张可点击卡片（写一篇文章/润色文本/翻译内容），点击后自动设置任务类型并聚焦输入框
  - 通过 `onQuickStart` 回调传递任务类型到 App.tsx
  - WritingForm 新增 `quickStart` / `onQuickStartConsumed` prop，接收后切换任务并 focus textarea
- **Token 计数动画**（P1）：token 数字变化时带平滑过渡动画（`.token-count-anim` 类，`transition: all 0.3s ease-out`）
- **字数目标**（P2-8）：WritingForm 字符计数行新增目标字数输入框（`word-target-input`），ResultPanel 标题栏显示字数进度条（`.word-count-progress`），目标达成时进度条变绿
  - App.tsx 新增 `wordCountTarget` / `setWordCountTarget` 状态
  - ResultPanel 内部 `countChars()` 函数去除 Markdown 标记后统计纯文字字符数
- **语气/正式度控制**（P2-9）：WritingForm 提交行新增分段控制（随意 | 标准 | 正式），非"标准"语气时自动追加 `[写作语气要求：轻松随意/正式严谨]` 到内容末尾
- **操作栏精简**（P2-10）：ResultPanel 操作栏重构 — 复制 + 换一个按钮常驻显示；编辑 + 全部导出格式收入 `⋯` 溢出菜单（`showOverflow` 状态 + `.overflow-menu`）；PPT 导出保持内联

### 改进

- ResultPanel 空状态插画和文案更新：图标 + "开始创作" + "选择一个方式快速开始"
- 复制按钮文案从"复制结果"简化为"复制"
- WritingForm 高级选项（风格、语言、模板、附件）折叠到可展开区域，提交行更简洁
- 前端测试覆盖从 54 个增加到 66 个，新增 12 个测试用例覆盖快速启动、语气控制、字数目标、溢出菜单等新功能

## [1.4.0] - 2026-03-26

### 新增

- **CSS 设计令牌系统**：`index.css` 中定义 122 个 CSS 自定义属性，覆盖语义色彩、阴影、间距、圆角、过渡和 z-index
  - 语义颜色变量：`--color-ppt`、`--color-error`、`--color-success`、`--color-warning`、`--color-info` 及其 bg/border/ring 变体
  - 阴影层级：`--shadow-sm` / `--shadow-md` / `--shadow-lg` / `--shadow-xl`
  - 间距刻度：`--sp-1` 到 `--sp-8`
  - 圆角刻度：`--radius-sm` 到 `--radius-full`
  - 过渡预设：`--transition-fast` / `--transition-normal` / `--transition-slow`
  - z-index 层级：`--z-dropdown` / `--z-modal` / `--z-toast`
- **暗色模式自动适配**：`prefers-color-scheme: dark` 媒体查询 + `data-theme="dark"` 手动切换，所有语义变量自动翻转
- **全局共享动画**：4 个 `@keyframes`（`fadeIn`、`slideUp`、`pulse`、`blink`）统一在 `index.css` 中定义
- **全局 focus-visible 样式**：所有交互元素获得统一的可访问焦点环
- **prefers-reduced-motion 支持**：减弱动画媒体查询，为动画敏感用户禁用非必要动画

### 改进

- **10 个组件 CSS 文件**全面替换硬编码颜色为 CSS 变量（922 行变更），确保主题一致性
  - `App.css`、`WritingForm.css`、`ResultPanel.css`、`HistoryPanel.css`、`AuthPanel.css`、`QualityPanel.css`、`LongFormPanel.css`、`ConfirmDialog.css`、`StyleEditor.css`、`SettingsPanel.css`
- **消除 8 处重复 `@keyframes`** 定义，所有组件共享全局动画
- **10 个 TSX 组件**添加 WAI-ARIA 无障碍属性：
  - 对话框：`role="dialog"` / `role="alertdialog"`、`aria-modal="true"`、`aria-labelledby`（ConfirmDialog、SettingsPanel、AuthPanel、StyleEditor）
  - 错误提示：`role="alert"`（认证错误、上传错误、离线横幅、质量评分错误、结果错误、风格编辑错误）
  - 实时区域：`aria-live="polite"`（ResultPanel 内容、LongFormPanel 结果、App 状态指示器）
  - 标签导航：`role="tablist"` / `role="tab"` / `aria-selected`（App.tsx 写作模式标签）
  - 可展开区域：`aria-expanded`（App.tsx 侧边栏、QualityPanel 折叠面板）
  - 图标按钮标注：18+ 个 `aria-label`（主题切换、设置、侧边栏、关闭、删除、搜索清除等图标按钮）
- `QualityPanel.tsx` 评分颜色函数改用 CSS 变量（`var(--color-success)` / `var(--color-warning)` / `var(--color-error)`）

## [1.3.1] - 2026-03-23

### 改进

- 版本号统一升级至 1.3.1，标识 PPT 生成功能稳定版本
- 后端 FastAPI 版本号同步更新

## [1.3.0] - 2026-03-23

### 新增

- PPT 多版式排版系统：6 种幻灯片版式（bullets、stats、comparison、timeline、quote、grid）
- AI Prompt 自动标注版式：LLM 根据内容性质在标题中嵌入 `[layout: xxx]` 标记
- `stats` 版式：圆角卡片内大数字 + 标签，多列并排展示关键指标
- `comparison` 版式：左右两栏对比，带列标题和中间分割线
- `timeline` 版式：水平时间轴 + 节点圆点 + 上下标注
- `quote` 版式：大引号装饰 + 居中引文 + 出处
- `grid` 版式：自适应 2~3 列网格卡片，带顶部强调线
- 12 个新增测试用例覆盖所有版式及边界情况

### 改进

- 页数控制提升为最高优先级，严格遵循用户指定页数
- 版式多样性要求适配不同页数（>=8 页至少 3 种，<8 页至少 2 种，<=3 页不强制）
- 目录/总结页门槛从 6 页提高到 8 页，避免小页数时浪费页面
- 向后兼容：无版式标记的幻灯片自动使用 bullets 默认版式

## [1.2.0] - 2026-03-22

### 新增

- PPT 导出功能：将 AI 生成的 PPT 大纲导出为 `.pptx` 文件
- 4 种 PPT 主题模板：商务蓝（business）、极简灰（minimal）、清新绿（green）、暖色调（warm）
- 可选 Unsplash 配图：为 PPT 幻灯片自动获取相关图片
- 后端端点 `POST /api/writing/export-pptx`（基于 python-pptx）
- 前端 PPT 导出选项：主题选择器、配图开关
- 设置面板新增 Unsplash Access Key 输入
- PPT 导出单元测试和集成测试（22 个新测试用例）

## [1.1.0] - 2026-03-22

### 新增

- 结果编辑功能，支持在导出前修改 AI 生成的内容（编辑/保存/取消）
- "换一个"按钮，用相同参数重新生成不同结果
- 输入字数统计，文本输入区下方实时显示字符数
- 多格式导出：新增纯文本（.txt）、Markdown（.md）、PDF（.pdf）导出
- PDF 导出后端端点 `POST /api/writing/export-pdf`（基于 fpdf2，支持中文）
- 清空历史记录时的二次确认对话框（ConfirmDialog 组件）
- 请求失败后显示"重新尝试"按钮
- 深色模式手动切换（跟随系统/亮色/暗色三态循环），设置持久化
- 润色/翻译对比视图，左右对比原文与生成结果
- 模型/参数设置面板（SettingsPanel），可自定义模型名称和温度参数
- WritingRequest 新增 `model` 和 `temperature` 可选字段
- 常用 Prompt 模板管理，支持保存/加载/删除模板
- 快捷键支持：Ctrl+Enter 提交、Esc 停止生成、Ctrl+S 拦截
- 复制成功/失败提示，按钮文字临时变为"已复制"/"复制失败"
- 历史记录迁移至后端 SQLite 数据库（SQLAlchemy + aiosqlite）
- 历史记录 CRUD API：`GET/POST/DELETE /api/history`
- 后端结构化日志系统（请求方法/路径/状态码/耗时）
- 请求日志中间件（RequestLoggingMiddleware）
- IP 限流中间件（RateLimitMiddleware），AI 生成端点每 IP 每分钟最多 10 次
- 移动端侧边栏折叠/展开（768px 以下汉堡菜单按钮控制）
- Ollama 离线降级提示：服务离线时禁用提交按钮并显示引导信息

## [1.0.0] - 2026-03-21

### 新增

- 文章生成功能，支持多种风格：文学、上海高考作文、小红书爆款、公众号文案、头条文案、AI短剧脚本、生成PPT
- 古诗词创作（五言/七言绝句、律诗），含字数校验与自动重试
- 文本润色功能
- 文本翻译功能，支持英、中、日、韩、法、德六种语言
- 文本摘要功能
- 流式输出（SSE），实时显示生成内容
- 附件上传功能，支持 PDF、Word、TXT、Markdown、CSV、JSON、XML、HTML 格式（最大 10MB）
- 生成结果导出为 Word 文档（.docx），支持系统"另存为"对话框选择保存路径
- 历史记录管理（基于 localStorage），支持关键词搜索、按时间排序
- 复制结果到剪贴板
- 下载成功/失败提示消息
- 后端健康检查接口
- CORS 跨域支持

### 修复

- 修复附件上传 network error：移除手动设置的 Content-Type header，让 axios 自动生成含 boundary 的 multipart header
- 修复 Word 导出文件内容为空：Content-Disposition header 中的中文文件名未做 URL 编码导致 latin-1 编码失败返回 500
- 修复 showSaveFilePicker 弹窗不显示：将弹窗调用移至 await 请求之前，确保在用户手势上下文中执行

[1.5.0]: https://github.com/USERNAME/REPO/releases/tag/v1.5.0
[1.4.0]: https://github.com/USERNAME/REPO/releases/tag/v1.4.0
[1.3.1]: https://github.com/USERNAME/REPO/releases/tag/v1.3.1
[1.3.0]: https://github.com/USERNAME/REPO/releases/tag/v1.3.0
[1.2.0]: https://github.com/USERNAME/REPO/releases/tag/v1.2.0
[1.1.0]: https://github.com/USERNAME/REPO/releases/tag/v1.1.0
[1.0.0]: https://github.com/USERNAME/REPO/releases/tag/v1.0.0
