# 后端测试场景

## 1. API 路由测试 (`test_routers.py`)

### 1.1 健康检查
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| R-01 | GET /api/health | 200, 返回 `{"status": "ok", "model": "..."}` |

### 1.2 文件上传 (POST /api/writing/upload)
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| R-02 | 上传 .txt 文件 | 200, 返回文件名、提取文本、字符数 |
| R-03 | 上传 .docx 文件 | 200, 正确提取 Word 内容 |
| R-04 | 上传不支持的格式 (如 .png) | 400, 错误信息包含"不支持" |

### 1.3 同步处理 (POST /api/writing/process)
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| R-05 | 生成任务 (generate) | 200, 返回生成文本和 token 数 |
| R-06 | 润色任务 (polish) 带风格 | 200, 调用 Ollama 并返回润色结果 |
| R-07 | 翻译任务 (translate) | 200, 返回翻译结果 |
| R-08 | 摘要任务 (summarize) | 200, 返回摘要结果 |
| R-09 | 无效 task_type | 422, Pydantic 校验失败 |
| R-10 | 带附件文本 | 200, prompt 中包含附件内容 |
| R-11 | 诗词请求自动重试 | 字数校验失败后自动重试，返回正确诗词 |

### 1.4 流式处理 (POST /api/writing/stream)
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| R-12 | 普通流式生成 | 200, SSE 格式逐 token 输出，以 `[DONE]` 结尾 |
| R-13 | 诗词回退为非流式 | 诗词请求走非流式生成 + 字数校验 |

---

## 2. 文件解析测试 (`test_file_parser.py`)

### 2.1 纯文本解析
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| F-01 | UTF-8 编码 .txt | 正确读取文本内容 |
| F-02 | GBK 编码 .txt | 自动检测编码并正确读取 |
| F-03 | Markdown 文件 | 正确解析 .md 内容 |
| F-04 | CSV 文件 | 正确解析 CSV 内容 |
| F-05 | JSON 文件 | 正确解析 JSON 内容 |
| F-06 | XML 文件 | 正确解析 XML 内容 |
| F-07 | HTML 文件 | 正确提取 HTML 文本 |

### 2.2 二进制文档解析
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| F-08 | PDF 文件 | 使用 PyPDF2 提取文本 |
| F-09 | DOCX 文件 | 使用 python-docx 提取文本 |
| F-10 | DOC 文件 (旧格式) | 返回不支持旧格式的提示 |

### 2.3 校验规则
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| F-11 | 不支持的文件类型 | 抛出错误或返回 400 |
| F-12 | 文件超过 10MB | 拒绝处理 |
| F-13 | 支持的扩展名列表 | 包含 pdf/docx/txt/md/csv/json/xml/html |

---

## 3. Prompt 构建测试 (`test_prompts.py`)

### 3.1 诗词识别
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| P-01 | 包含"五言绝句"等关键词 | `is_poetry_request` 返回 True |
| P-02 | 普通写作请求 | `is_poetry_request` 返回 False |

### 3.2 诗词校验
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| P-03 | 标准五言绝句 (每句5字) | `validate_poetry` 返回 True |
| P-04 | 标准七言绝句 (每句7字) | 返回 True |
| P-05 | 五言诗但某句字数不对 | 返回 False |
| P-06 | 不足4句 | 返回 False |
| P-07 | 通用"古诗"跳过字数检查 | 返回 True |
| P-08 | 五言律诗 (8句) | 返回 True |

### 3.3 Prompt 生成
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| P-09 | generate + 默认风格 | 使用 GENERATE_PROMPT |
| P-10 | generate + sh_gaokao | 使用 SH_GAOKAO_PROMPT，包含"上海高考" |
| P-11 | generate + 诗词主题 | 使用 POETRY_PROMPT |
| P-12 | generate + xiaohongshu | 使用 XIAOHONGSHU_PROMPT |
| P-13 | generate + gongzhonghao | 使用 GONGZHONGHAO_PROMPT |
| P-14 | generate + toutiao | 使用 TOUTIAO_PROMPT |
| P-15 | generate + ai_drama | 使用 AI_DRAMA_PROMPT |
| P-16 | polish 任务 | 使用 POLISH_PROMPT |
| P-17 | polish + literary | prompt 包含"文学" |
| P-18 | translate 任务 | 使用 TRANSLATE_PROMPT + 目标语言 |
| P-19 | summarize 任务 | 使用 SUMMARIZE_PROMPT |
| P-20 | 未知 task_type | 抛出 ValueError |
| P-21 | 带附件文本 | prompt 末尾包含附件内容 |
| P-22 | 空附件文本 | prompt 不包含附件区段 |
| P-23 | 自定义风格回退 | 使用"使用{style}风格"格式 |

---

## 4. 数据模型测试 (`test_schemas.py`)

### 4.1 TaskType 枚举
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| S-01 | 枚举值正确 | generate/polish/translate/summarize |
| S-02 | 枚举数量 | 共 4 个 |

### 4.2 WritingRequest
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| S-03 | 最小有效请求 | 只需 task_type + content |
| S-04 | 完整字段 | 所有可选字段正确赋值 |
| S-05 | 无效 task_type | ValidationError |
| S-06 | 缺少 content | ValidationError |
| S-07 | 所有 task_type 遍历 | 均可创建成功 |

### 4.3 WritingResponse
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| S-08 | 基础响应 | token_count 默认为 0 |
| S-09 | 带 token_count | 正确赋值 |
| S-10 | 无效 task_type | ValidationError |
