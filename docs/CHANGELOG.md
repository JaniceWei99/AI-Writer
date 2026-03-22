# 更新日志

本文件记录本项目的所有重要变更。

格式基于 [Keep a Changelog](https://keepachangelog.com/zh-CN/1.1.0/)，
本项目遵循 [语义化版本](https://semver.org/lang/zh-CN/)。

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

[1.1.0]: https://github.com/USERNAME/REPO/releases/tag/v1.1.0
[1.0.0]: https://github.com/USERNAME/REPO/releases/tag/v1.0.0
