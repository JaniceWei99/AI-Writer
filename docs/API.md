# AI 写作助手 — 后端 API 文档

> 基于 FastAPI 构建的 AI 写作助手后端服务，提供文件上传解析、AI 写作生成/润色/翻译/摘要、流式输出及文档导出等能力。

**基础地址：** `http://localhost:8000`

**写作路由前缀：** `/api/writing`

---

## 接口概览

| 方法   | 路径                         | 说明                         |
| ------ | ---------------------------- | ---------------------------- |
| GET    | `/api/health`                | 健康检查 + Provider 信息     |
| GET    | `/api/models`                | 获取可用模型列表             |
| POST   | `/api/writing/upload`        | 上传文件并提取文本内容       |
| POST   | `/api/writing/process`       | 非流式处理写作请求           |
| POST   | `/api/writing/stream`        | 流式处理写作请求（SSE）      |
| POST   | `/api/writing/refine`        | 继续优化/多轮对话            |
| POST   | `/api/writing/outline`       | 生成长文大纲（流式）         |
| POST   | `/api/writing/expand-chapter`| 展开单个章节（流式）         |
| POST   | `/api/writing/export-docx`   | 将 Markdown 导出为 Word 文档 |
| POST   | `/api/writing/export-pdf`    | 将 Markdown 导出为 PDF 文档  |
| POST   | `/api/writing/export-pptx`   | 将 Markdown 导出为 PPT 文档  |
| GET    | `/api/history`               | 获取历史记录列表             |
| POST   | `/api/history`               | 新增历史记录                 |
| DELETE | `/api/history/{id}`          | 删除单条历史记录             |
| DELETE | `/api/history`               | 清空全部历史记录             |
| GET    | `/api/styles`                | 获取自定义风格列表           |
| POST   | `/api/styles`                | 创建自定义风格               |
| PUT    | `/api/styles/{style_id}`     | 更新自定义风格               |
| DELETE | `/api/styles/{style_id}`     | 删除自定义风格               |
| POST   | `/api/auth/register`         | 用户注册                     |
| POST   | `/api/auth/login`            | 用户登录                     |
| GET    | `/api/auth/me`               | 获取当前用户信息             |
| POST   | `/api/analysis/quality`      | 文本质量评分                 |

---

## 1. 健康检查

### `GET /api/health`

检查服务是否正常运行，返回当前使用的模型名称。

#### 响应

```json
{
  "status": "ok",
  "provider": "ollama",
  "model": "qwen3.5:9b",
  "available_providers": ["ollama"]
}
```

#### 示例

```bash
curl http://localhost:8000/api/health
```

---

## 1.5 获取可用模型列表

### `GET /api/models`

返回当前 LLM Provider 中可用的模型列表。自动过滤 OCR、Embedding 等非文本生成模型。

#### 响应

```json
{
  "models": ["qwen3.5:9b"],
  "default": "qwen3.5:9b"
}
```

#### 示例

```bash
curl http://localhost:8000/api/models
```

---

## 2. 上传文件并提取文本

### `POST /api/writing/upload`

上传文件并自动提取文本内容，支持多种常见文件格式。提取的文本可作为后续写作任务的附件材料。

#### 请求

**Content-Type：** `multipart/form-data`

| 字段   | 类型       | 必填 | 说明         |
| ------ | ---------- | ---- | ------------ |
| `file` | UploadFile | 是   | 待上传的文件 |

**支持的文件格式：** `.pdf`、`.docx`、`.doc`、`.txt`、`.md`、`.csv`、`.json`、`.xml`、`.html`、`.htm`

**文件大小限制：** 最大 10MB

#### 响应

```json
{
  "filename": "example.pdf",
  "text": "这是从 PDF 文件中提取的文本内容...",
  "char_count": 2048
}
```

| 字段         | 类型   | 说明             |
| ------------ | ------ | ---------------- |
| `filename`   | string | 上传的文件名     |
| `text`       | string | 提取出的文本内容 |
| `char_count` | int    | 提取文本的字符数 |

#### 错误响应

| 状态码 | 说明                               |
| ------ | ---------------------------------- |
| `400`  | 不支持的文件类型，或文件缺少文件名 |
| `500`  | 文件解析失败（文件损坏或内部错误） |

#### 示例

```bash
curl -X POST http://localhost:8000/api/writing/upload \
  -F "file=@./example.pdf"
```

---

## 3. 非流式处理写作请求

### `POST /api/writing/process`

提交写作任务，等待 AI 处理完成后一次性返回完整结果。

#### 请求

**Content-Type：** `application/json`

```json
{
  "task_type": "generate",
  "content": "请帮我写一篇关于人工智能的文章",
  "style": "literary",
  "target_lang": "英文",
  "attachment_text": ""
}
```

| 字段              | 类型   | 必填 | 默认值   | 说明                                   |
| ----------------- | ------ | ---- | -------- | -------------------------------------- |
| `task_type`       | string | 是   | —        | 任务类型，见下方枚举值                 |
| `content`         | string | 是   | —        | 用户输入的文本内容或写作指令           |
| `style`           | string | 否   | `""`     | 写作风格，见下方枚举值                 |
| `target_lang`     | string | 否   | `"英文"` | 翻译目标语言（仅 `translate` 时生效）  |
| `attachment_text` | string | 否   | `""`     | 附件文本（通过上传接口获取）           |
| `model`           | string | 否   | `""`     | 自定义模型名称，为空则使用服务端默认值 |
| `temperature`     | number | 否   | `null`   | 生成温度（0-2），null 使用模型默认值   |

**`task_type` 枚举值：**

| 值          | 说明                   |
| ----------- | ---------------------- |
| `generate`  | 根据指令生成全新文本   |
| `polish`    | 对已有文本进行润色优化 |
| `translate` | 将文本翻译为目标语言   |
| `summarize` | 对长文本进行摘要提炼   |

**`style` 枚举值：**

| 值               | 说明              |
| ---------------- | ----------------- |
| `""`（空字符串） | 默认风格          |
| `literary`       | 文学创作风格      |
| `sh_gaokao`      | 上海高考作文风格  |
| `xiaohongshu`    | 小红书风格        |
| `gongzhonghao`   | 微信公众号风格    |
| `toutiao`        | 今日头条风格      |
| `ai_drama`       | AI 短剧脚本风格   |
| `ppt`            | 生成 PPT 大纲风格 |
| `zhihu`          | 知乎回答风格      |

```json
{
  "task_type": "generate",
  "result": "人工智能（AI）是计算机科学的一个分支...",
  "token_count": 856
}
```

#### 示例

```bash
# 生成文本
curl -X POST http://localhost:8000/api/writing/process \
  -H "Content-Type: application/json" \
  -d '{"task_type": "generate", "content": "写一篇关于人工智能的文章", "style": "literary"}'

# 润色文本
curl -X POST http://localhost:8000/api/writing/process \
  -H "Content-Type: application/json" \
  -d '{"task_type": "polish", "content": "AI很好用能帮人干很多事", "style": "literary"}'

# 翻译文本
curl -X POST http://localhost:8000/api/writing/process \
  -H "Content-Type: application/json" \
  -d '{"task_type": "translate", "content": "人工智能正在改变世界。", "target_lang": "英文"}'

# 摘要（带附件）
curl -X POST http://localhost:8000/api/writing/process \
  -H "Content-Type: application/json" \
  -d '{"task_type": "summarize", "content": "请总结文档核心内容", "attachment_text": "这是一篇很长的文档..."}'

# 指定模型和温度
curl -X POST http://localhost:8000/api/writing/process \
  -H "Content-Type: application/json" \
  -d '{"task_type": "generate", "content": "写一篇散文", "model": "qwen3:8b", "temperature": 0.8}'
```

---

## 4. 流式处理写作请求（SSE）

### `POST /api/writing/stream`

以 Server-Sent Events（SSE）方式流式返回 AI 生成的文本，实时展示生成过程。

#### 请求

**Content-Type：** `application/json`

请求体与 `/api/writing/process` 完全相同。

| 字段              | 类型   | 必填 | 默认值   | 说明                                  |
| ----------------- | ------ | ---- | -------- | ------------------------------------- |
| `task_type`       | string | 是   | —        | 任务类型                              |
| `content`         | string | 是   | —        | 用户输入的文本内容或写作指令          |
| `style`           | string | 否   | `""`     | 写作风格                              |
| `target_lang`     | string | 否   | `"英文"` | 翻译目标语言（仅 `translate` 时生效） |
| `attachment_text` | string | 否   | `""`     | 附件文本                              |
| `model`           | string | 否   | `""`     | 自定义模型名称                        |
| `temperature`     | number | 否   | `null`   | 生成温度（0-2）                       |

#### 响应

**Content-Type：** `text/event-stream`

每个事件以 `data:` 开头，后跟一个 JSON 字符串，以两个换行符结尾：

```
data: "春"

data: "风"

data: "拂"

data: "面"

data: [DONE]

```

| 事件内容       | 说明                              |
| -------------- | --------------------------------- |
| `data: "..."`  | 单个文本 token（JSON 字符串格式） |
| `data: [DONE]` | 流式传输结束标志                  |

#### 示例

```bash
curl -X POST http://localhost:8000/api/writing/stream \
  -H "Content-Type: application/json" \
  -d '{"task_type": "generate", "content": "写一段小红书旅行分享", "style": "xiaohongshu"}' \
  --no-buffer
```

---

## 5. 导出 Word 文档

### `POST /api/writing/export-docx`

将 Markdown 格式的文本内容导出为 Word（.docx）文档。

#### 请求

**Content-Type：** `application/json`

```json
{
  "content": "# 标题\n\n这是正文内容...",
  "title": "我的文档"
}
```

| 字段      | 类型   | 必填 | 说明                                 |
| --------- | ------ | ---- | ------------------------------------ |
| `content` | string | 是   | Markdown 格式的文本内容              |
| `title`   | string | 否   | 文档标题（用于文件名和文档内部标题） |

#### 响应

**Content-Type：** `application/vnd.openxmlformats-officedocument.wordprocessingml.document`

返回二进制 `.docx` 文件。

#### 示例

```bash
curl -X POST http://localhost:8000/api/writing/export-docx \
  -H "Content-Type: application/json" \
  -d '{"content": "# 报告\n\n## 概述\n\n这是一份报告...", "title": "AI写作报告"}' \
  -o "AI写作报告.docx"
```

---

## 6. 导出 PDF 文档

### `POST /api/writing/export-pdf`

将 Markdown 格式的文本内容导出为 PDF 文档，支持中文字体渲染（基于 fpdf2）。

#### 请求

**Content-Type：** `application/json`

```json
{
  "content": "# 标题\n\n这是正文内容...",
  "title": "我的文档"
}
```

| 字段      | 类型   | 必填 | 说明                    |
| --------- | ------ | ---- | ----------------------- |
| `content` | string | 是   | Markdown 格式的文本内容 |
| `title`   | string | 否   | 文档标题（用于文件名）  |

#### 响应

**Content-Type：** `application/pdf`

返回二进制 `.pdf` 文件。

#### 示例

```bash
curl -X POST http://localhost:8000/api/writing/export-pdf \
  -H "Content-Type: application/json" \
  -d '{"content": "# 报告\n\n## 概述\n\n这是一份报告...", "title": "AI写作报告"}' \
  -o "AI写作报告.pdf"
```

---

## 6.5 导出 PPT 演示文稿

### `POST /api/writing/export-pptx`

将 Markdown PPT 大纲导出为 PowerPoint（.pptx）演示文稿，支持主题模板和自动配图。

#### 请求

**Content-Type：** `application/json`

```json
{
  "content": "## 封面\n标题：人工智能\n---\n## 第一章 概述\n- 要点一\n- 要点二",
  "title": "AI演示文稿",
  "template": "business",
  "with_images": false,
  "unsplash_key": ""
}
```

| 字段            | 类型    | 必填 | 默认值       | 说明                                    |
| --------------- | ------- | ---- | ------------ | --------------------------------------- |
| `content`       | string  | 是   | —            | Markdown PPT 大纲内容                   |
| `title`         | string  | 否   | `"演示文稿"` | 文档标题                                |
| `template`      | string  | 否   | `"business"` | 主题模板（business/minimal/green/warm） |
| `with_images`   | boolean | 否   | `false`      | 是否启用自动配图                        |
| `unsplash_key`  | string  | 否   | `""`         | Unsplash API Key（配图需要）            |

#### 响应

**Content-Type：** `application/vnd.openxmlformats-officedocument.presentationml.presentation`

返回二进制 `.pptx` 文件。

---

## 6.6 继续优化（多轮对话）

### `POST /api/writing/refine`

基于上次生成结果和用户反馈，以 SSE 流式方式返回改进后的版本。

#### 请求

**Content-Type：** `application/json`

```json
{
  "previous_result": "上次生成的文本...",
  "feedback": "请让语言更加口语化",
  "model": "",
  "temperature": null
}
```

| 字段              | 类型   | 必填 | 说明                   |
| ----------------- | ------ | ---- | ---------------------- |
| `previous_result` | string | 是   | 上一次生成的结果文本   |
| `feedback`        | string | 是   | 用户反馈/优化指令      |
| `model`           | string | 否   | 自定义模型名称         |
| `temperature`     | number | 否   | 生成温度（0-2）        |

#### 响应

**Content-Type：** `text/event-stream`

与 `/api/writing/stream` 格式相同。

---

## 6.7 生成长文大纲

### `POST /api/writing/outline`

根据主题和风格生成结构化长文大纲，以 SSE 流式方式返回。

#### 请求

**Content-Type：** `application/json`

```json
{
  "content": "人工智能在教育领域的应用",
  "style": "literary",
  "model": "",
  "temperature": null
}
```

| 字段          | 类型   | 必填 | 说明             |
| ------------- | ------ | ---- | ---------------- |
| `content`     | string | 是   | 长文主题         |
| `style`       | string | 否   | 写作风格         |
| `model`       | string | 否   | 自定义模型名称   |
| `temperature` | number | 否   | 生成温度（0-2）  |

#### 响应

**Content-Type：** `text/event-stream`

与 `/api/writing/stream` 格式相同。

---

## 6.8 展开单个章节

### `POST /api/writing/expand-chapter`

基于大纲和章节标题，生成该章节的详细内容，以 SSE 流式方式返回。

#### 请求

**Content-Type：** `application/json`

```json
{
  "outline": "完整大纲文本...",
  "chapter_title": "第一章 概述",
  "chapter_desc": "本章简要介绍背景",
  "style": "literary",
  "model": "",
  "temperature": null
}
```

| 字段            | 类型   | 必填 | 说明             |
| --------------- | ------ | ---- | ---------------- |
| `outline`       | string | 是   | 完整大纲文本     |
| `chapter_title` | string | 是   | 章节标题         |
| `chapter_desc`  | string | 否   | 章节描述         |
| `style`         | string | 否   | 写作风格         |
| `model`         | string | 否   | 自定义模型名称   |
| `temperature`   | number | 否   | 生成温度（0-2）  |

#### 响应

**Content-Type：** `text/event-stream`

与 `/api/writing/stream` 格式相同。

---

## 7. 历史记录管理

历史记录存储在后端 SQLite 数据库中，支持 CRUD 操作。

**路由前缀：** `/api/history`

### 7.1 获取历史记录列表

#### `GET /api/history`

按时间倒序返回历史记录列表。

##### 请求参数（Query）

| 参数      | 类型   | 默认值 | 说明                         |
| --------- | ------ | ------ | ---------------------------- |
| `keyword` | string | —      | 搜索关键词（匹配内容和结果） |
| `limit`   | int    | 200    | 每页数量（1-1000）           |
| `offset`  | int    | 0      | 偏移量                       |

##### 响应

```json
[
  {
    "id": 1,
    "task_type": "generate",
    "content": "写一篇关于AI的文章",
    "result": "人工智能（AI）是...",
    "style": "literary",
    "token_count": 856,
    "created_at": "2026-03-21T15:30:00.000000Z"
  }
]
```

##### 示例

```bash
curl http://localhost:8000/api/history
curl "http://localhost:8000/api/history?keyword=AI&limit=10"
```

### 7.2 新增历史记录

#### `POST /api/history`

新增一条历史记录。

##### 请求

**Content-Type：** `application/json`

```json
{
  "task_type": "generate",
  "content": "写一篇关于AI的文章",
  "result": "人工智能（AI）是...",
  "style": "literary",
  "token_count": 856
}
```

| 字段          | 类型   | 必填 | 说明       |
| ------------- | ------ | ---- | ---------- |
| `task_type`   | string | 是   | 任务类型   |
| `content`     | string | 是   | 输入内容   |
| `result`      | string | 否   | 生成结果   |
| `style`       | string | 否   | 写作风格   |
| `token_count` | int    | 否   | Token 数量 |

##### 响应（201 Created）

返回新创建的历史记录对象（含 `id` 和 `created_at`）。

### 7.3 删除单条历史记录

#### `DELETE /api/history/{id}`

删除指定 ID 的历史记录。成功返回 `204 No Content`。

```bash
curl -X DELETE http://localhost:8000/api/history/1
```

### 7.4 清空全部历史记录

#### `DELETE /api/history`

清空全部历史记录。成功返回 `204 No Content`。

```bash
curl -X DELETE http://localhost:8000/api/history
```

---

## 通用说明

### 错误响应格式

所有接口在发生错误时，统一返回如下 JSON 格式：

```json
{
  "detail": "错误描述信息"
}
```

### 常见 HTTP 状态码

| 状态码 | 说明                                                    |
| ------ | ------------------------------------------------------- |
| `200`  | 请求成功                                                |
| `201`  | 资源创建成功（新增历史记录）                            |
| `204`  | 操作成功，无返回内容（删除操作）                        |
| `400`  | 请求参数错误（如不支持的文件类型）                      |
| `422`  | 请求体验证失败（字段缺失或类型错误）                    |
| `429`  | 请求过于频繁（AI 生成端点限流：每 IP 每分钟最多 10 次） |
| `500`  | 服务器内部错误                                          |

### 限流说明

AI 生成端点（`/api/writing/process`、`/api/writing/stream`）启用了 IP 限流中间件，每个 IP 每分钟最多 10 次请求。超出限制时返回 `429 Too Many Requests`：

```json
{
  "detail": "Rate limit exceeded. Try again later."
}
```

### CORS 跨域

服务默认允许来自 `http://localhost:5173` 和 `http://localhost:3000` 的跨域请求。

---

## 8. 自定义风格管理

自定义风格存储在后端 SQLite 数据库中，支持 CRUD 操作。

**路由前缀：** `/api/styles`

### 8.1 获取自定义风格列表

#### `GET /api/styles`

返回所有自定义风格。

##### 响应

```json
[
  {
    "id": 1,
    "name": "科技评论",
    "slug": "tech_review",
    "prompt_template": "你是一位专业的科技评论家。请根据以下主题写一篇深度评论：\n\n{content}",
    "description": "科技产品深度评论风格",
    "created_at": "2026-03-26T10:00:00Z",
    "updated_at": "2026-03-26T10:00:00Z"
  }
]
```

### 8.2 创建自定义风格

#### `POST /api/styles`

创建一个新的自定义风格。

##### 请求

```json
{
  "name": "科技评论",
  "slug": "tech_review",
  "prompt_template": "你是一位专业的科技评论家。请根据以下主题写一篇深度评论：\n\n{content}",
  "description": "科技产品深度评论风格"
}
```

| 字段              | 类型   | 必填 | 说明                                          |
| ----------------- | ------ | ---- | --------------------------------------------- |
| `name`            | string | 是   | 风格显示名称                                  |
| `slug`            | string | 是   | 唯一标识（`^[a-z][a-z0-9_]{1,62}$`，内置 slug 受保护） |
| `prompt_template` | string | 是   | Prompt 模板，必须包含 `{content}` 占位符      |
| `description`     | string | 否   | 风格描述                                      |

##### 响应（201 Created）

返回创建的风格对象。

##### 错误响应

| 状态码 | 说明                     |
| ------ | ------------------------ |
| `409`  | slug 已存在              |
| `422`  | slug 格式不合法或模板缺少 `{content}` |

### 8.3 更新自定义风格

#### `PUT /api/styles/{style_id}`

更新指定 ID 的自定义风格。

##### 请求

```json
{
  "name": "科技深度评论",
  "prompt_template": "你是一位资深科技记者...\n\n{content}",
  "description": "更深入的科技评论"
}
```

所有字段均为可选，仅更新提供的字段。

##### 响应

返回更新后的风格对象。

### 8.4 删除自定义风格

#### `DELETE /api/styles/{style_id}`

删除指定 ID 的自定义风格。成功返回 `204 No Content`。

---

## 9. 用户认证

**路由前缀：** `/api/auth`

### 9.1 用户注册

#### `POST /api/auth/register`

##### 请求

```json
{
  "username": "myuser",
  "password": "mypassword"
}
```

| 字段       | 类型   | 必填 | 说明                      |
| ---------- | ------ | ---- | ------------------------- |
| `username` | string | 是   | 用户名（2-32 个字符）     |
| `password` | string | 是   | 密码（不少于 4 个字符）   |

##### 响应（201 Created）

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": 1,
  "username": "myuser"
}
```

##### 错误响应

| 状态码 | 说明         |
| ------ | ------------ |
| `409`  | 用户名已存在 |

### 9.2 用户登录

#### `POST /api/auth/login`

##### 请求

```json
{
  "username": "myuser",
  "password": "mypassword"
}
```

##### 响应

```json
{
  "token": "eyJhbGciOiJIUzI1NiIs...",
  "user_id": 1,
  "username": "myuser"
}
```

##### 错误响应

| 状态码 | 说明             |
| ------ | ---------------- |
| `401`  | 用户名或密码错误 |

### 9.3 获取当前用户

#### `GET /api/auth/me`

需在请求头中携带 `Authorization: Bearer {token}`。

##### 响应

```json
{
  "user_id": 1,
  "username": "myuser"
}
```

##### 错误响应

| 状态码 | 说明                |
| ------ | ------------------- |
| `401`  | Token 无效或已过期  |

---

## 10. 文本质量评分

**路由前缀：** `/api/analysis`

### `POST /api/analysis/quality`

纯算法文本质量分析，无 AI 依赖。

#### 请求

**Content-Type：** `application/json`

```json
{
  "text": "要分析的文本内容..."
}
```

| 字段   | 类型   | 必填 | 说明           |
| ------ | ------ | ---- | -------------- |
| `text` | string | 是   | 待分析的文本   |

#### 响应

```json
{
  "char_count": 1200,
  "word_count": 600,
  "sentence_count": 40,
  "paragraph_count": 8,
  "reading_time_minutes": 3.0,
  "sentence_length_score": 85,
  "vocabulary_diversity_score": 72,
  "paragraph_balance_score": 90,
  "structure_score": 78,
  "readability_score": 81
}
```

#### 示例

```bash
curl -X POST http://localhost:8000/api/analysis/quality \
  -H "Content-Type: application/json" \
  -d '{"text": "这是一段需要分析质量的文本..."}'
```
