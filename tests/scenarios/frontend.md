# 前端测试场景

## 1. WritingForm 组件测试 (`WritingForm.test.tsx`)

### 1.1 UI 渲染
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-01 | 初始渲染 | 显示四个任务 tab：文章生成/文本润色/文本翻译/文本摘要 |
| WF-02 | 风格选择器（高级选项内） | 展开"高级选项"后可见"风格"标签 |
| WF-03 | 上传按钮（高级选项内） | 展开"高级选项"后可见"上传附件"按钮 |
| WF-04 | 模式切换器 | 显示"文案创作"和"演示文稿"两个模式卡片 |
| WF-05 | PPT 模式切换 | 点击"演示文稿"后显示 PPT 占位提示和"生成PPT大纲"按钮 |

### 1.2 表单交互
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-06 | 输入为空时提交按钮 | "开始处理"按钮 disabled |
| WF-07 | 输入内容后提交按钮 | "开始处理"按钮 enabled |
| WF-08 | 点击提交 | 调用 onSubmit，payload 包含 task_type + content |
| WF-09 | 切换任务 tab | 文本框 placeholder 随之变化 |
| WF-10 | 切换到翻译任务（高级选项内） | 展开高级选项后出现"目标语言"下拉框 |
| WF-11 | 非翻译任务（高级选项内） | 展开高级选项后不显示"目标语言"下拉框 |

### 1.3 加载状态
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-12 | loading=true | 显示"停止生成"按钮，隐藏"开始处理" |
| WF-13 | 点击停止按钮 | 调用 onStop 回调 |
| WF-14 | loading 时 tab 状态 | 所有任务 tab 被 disabled |

### 1.4 语气控制（P2-9）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-15 | 语气按钮渲染 | 显示"随意"、"标准"、"正式"三个分段控制按钮 |
| WF-16 | 随意语气提交 | 提交内容末尾追加 `[写作语气要求：轻松随意]` |
| WF-17 | 正式语气提交 | 提交内容末尾追加 `[写作语气要求：正式严谨]` |
| WF-18 | 标准语气提交 | 提交内容不追加语气指令 |

### 1.5 字数目标（P2-8）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-19 | 字数目标输入框 | 显示 type=number 的目标输入框（placeholder "—"） |
| WF-20 | 修改字数目标 | 输入值后调用 onWordCountTargetChange 回调 |

### 1.6 快速启动（P1）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-21 | quickStart 切换任务 | 传入 quickStart={taskType:'polish'} 后润色 tab 变为 active |
| WF-22 | quickStart 消费 | quickStart 后调用 onQuickStartConsumed 回调 |

### 1.7 高级选项折叠（P1）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-23 | 初始状态 | 高级选项区域默认折叠，"风格"不可见 |
| WF-24 | 展开/折叠 | 点击"高级选项"按钮可切换展开/折叠状态 |

### 1.8 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| WF-25 | 文本区 aria-label | textarea 具有 `aria-label` 属性 |
| WF-26 | 上传错误 role=alert | 上传失败时错误信息具有 `role="alert"` |
| WF-27 | 离线横幅 role=alert | 离线提示横幅具有 `role="alert"` |

---

## 2. ResultPanel 组件测试 (`ResultPanel.test.tsx`)

### 2.1 空状态
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-01 | 无结果且未加载 | 显示"开始创作"提示文字 |

### 2.2 错误状态
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-02 | error 非空 | 显示"出错了"和具体错误信息 |

### 2.3 正常展示
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-03 | Markdown 结果 | `**bold text**` 渲染为粗体，显示 token 数 |
| RP-04 | 结果就绪 | 显示"复制"按钮 |

### 2.4 加载中
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-05 | loading=true | 显示"生成中..."指示器 |
| RP-06 | loading 时复制按钮 | 不显示"复制"按钮 |

### 2.5 快速启动卡片（P1）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-07 | 空状态快速卡片 | 提供 onQuickStart 后显示"写一篇文章"/"润色文本"/"翻译内容"三张卡片 |
| RP-08 | 卡片点击 | 点击卡片调用 onQuickStart('generate'/'polish'/'translate') |
| RP-09 | 无 onQuickStart | 不提供 onQuickStart 时不显示快速卡片 |

### 2.6 字数进度条（P2-8）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-10 | 有目标字数 | wordCountTarget > 0 时显示 `.word-count-progress` 进度条 |
| RP-11 | 无目标字数 | wordCountTarget = 0 时不显示进度条 |

### 2.7 溢出菜单（P2-10）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-12 | ⋯ 按钮 | 结果就绪时显示 `.btn-overflow` 溢出菜单按钮 |
| RP-13 | 菜单内容 | 点击后显示"编辑结果"和 4 种导出格式（Word/TXT/MD/PDF） |

### 2.8 换一个按钮
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-14 | onRegenerate 提供 | 结果就绪时显示"换一个"按钮 |

### 2.9 Token 计数动画（P1）
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-15 | 动画类 | token 计数元素具有 `.token-count-anim` 类 |

### 2.10 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| RP-16 | 错误 role=alert | 错误提示容器具有 `role="alert"` |
| RP-17 | 结果区 aria-live | 结果内容区域具有 `aria-live="polite"` |

---

## 3. HistoryPanel 组件测试 (`HistoryPanel.test.tsx`)

### 3.1 空状态
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| HP-01 | items 为空 | 显示"暂无记录" |

### 3.2 列表渲染
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| HP-02 | 有历史项 | 显示任务标签（文章生成）和内容预览 |
| HP-03 | 多条记录 | header 显示"历史记录 (N)"计数 |

### 3.3 交互
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| HP-04 | 点击历史项 | 调用 onSelect 并传入该 item |
| HP-05 | 点击清空 | 调用 onClear 回调 |
| HP-06 | 点击删除按钮 | 调用 onDelete(id)，且不触发 onSelect |

### 3.4 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| HP-07 | 面板 role | 历史面板具有 `role="complementary"` |
| HP-08 | 面板 aria-label | 历史面板具有 `aria-label="历史记录"` |
| HP-09 | 清空按钮 aria-label | 清空按钮具有 `aria-label` |
| HP-10 | 删除按钮 aria-label | 删除按钮具有 `aria-label="删除此记录"` |

---

## 4. History Service 测试 (`history.test.ts`)

### 4.1 基础 CRUD
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| HS-01 | 无历史记录 | getHistory() 返回空数组 |
| HS-02 | 添加记录 | 返回含 id 和 created_at 的条目 |
| HS-03 | 获取列表 | 按时间倒序排列（最新在前） |
| HS-04 | 删除记录 | 指定 id 的记录被移除 |
| HS-05 | 清空记录 | 所有记录被删除 |

### 4.2 边界情况
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| HS-06 | 超过 50 条上限 | 自动裁剪为 50 条 |
| HS-07 | localStorage 数据损坏 | 优雅降级，返回空数组 |

---

## 5. ConfirmDialog 组件测试 (`Accessibility.test.tsx`)

### 5.1 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| CD-01 | alertdialog 角色 | 对话框具有 `role="alertdialog"` |
| CD-02 | aria-modal | 对话框具有 `aria-modal="true"` |
| CD-03 | 遮罩层 role | 遮罩层具有 `role="presentation"` |
| CD-04 | aria-describedby | 对话框通过 `aria-describedby` 关联消息内容 |

---

## 6. SettingsPanel 组件测试 (`Accessibility.test.tsx`)

### 6.1 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| SP-01 | dialog 角色 | 设置面板具有 `role="dialog"` |
| SP-02 | aria-modal | 设置面板具有 `aria-modal="true"` |
| SP-03 | aria-labelledby | 面板通过 `aria-labelledby` 关联标题 |
| SP-04 | 关闭按钮 aria-label | 关闭按钮具有 `aria-label="关闭设置"` |

---

## 7. AuthPanel 组件测试 (`Accessibility.test.tsx`)

### 7.1 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| AP-01 | dialog 角色 | 认证面板具有 `role="dialog"` |
| AP-02 | aria-modal | 认证面板具有 `aria-modal="true"` |
| AP-03 | aria-labelledby | 面板通过 `aria-labelledby` 关联标题 |
| AP-04 | 关闭按钮 aria-label | 关闭按钮具有 `aria-label="关闭"` |
| AP-05 | 错误 role=alert | 认证错误具有 `role="alert"` |

---

## 8. StyleEditor 组件测试 (`Accessibility.test.tsx`)

### 8.1 无障碍
| 编号 | 场景 | 预期结果 |
|------|------|----------|
| SE-01 | dialog 角色 | 编辑器具有 `role="dialog"` |
| SE-02 | aria-modal | 编辑器具有 `aria-modal="true"` |
| SE-03 | aria-labelledby | 编辑器通过 `aria-labelledby` 关联标题 |
| SE-04 | 关闭按钮 aria-label | 关闭按钮具有 `aria-label="关闭"` |
