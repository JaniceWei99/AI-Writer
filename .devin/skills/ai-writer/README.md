# ai-writer Skill — 使用说明

## 这是什么

`ai-writer` 是 **AI 写作助手** 项目的 Devin 开发技能。激活后，Devin 会自动了解项目的完整架构（后端 API、前端组件、数据库模型、Prompt 模板等），无需你手动解释项目结构，直接说任务即可。

## 调用方式

在 Devin 会话中输入：

```
/ai-writer <你的任务描述>
```

或者 Devin 在处理本项目任务时也可能自动激活此 skill（因为 triggers 包含 `model`）。

## 使用示例

```bash
# 添加新功能
/ai-writer 添加一个"学术论文"写作风格

# 修 Bug
/ai-writer 历史记录搜索不区分大小写，但中文搜索有时匹配不到

# 添加新 API
/ai-writer 新增批量生成接口 POST /api/writing/batch，支持多主题队列生成

# 前端改动
/ai-writer 在 ResultPanel 中增加一个"复制为 Markdown"按钮

# 测试
/ai-writer 为 auth.py 的注册和登录接口编写单元测试

# 部署相关
/ai-writer 更新 Dockerfile 支持多架构构建（amd64 + arm64）

# 文档
/ai-writer 更新竞品分析，加入最新的 Claude Artifacts 竞品对比

# 调试
/ai-writer 后端 /api/writing/stream 接口偶尔返回空响应，帮我排查

# 重构
/ai-writer 把 pptx_export.py 里的 6 个 layout renderer 拆成独立模块
```

## 它知道什么

激活后 Devin 会立即了解：

| 类别 | 内容 |
|------|------|
| **后端架构** | 5 个 Router、9 个 Service、3 个 ORM 模型、15 个 Prompt 模板 |
| **前端架构** | 9 个 React 组件、4 个 Service 模块、全部类型定义 |
| **API 端点** | 20+ 个端点的完整路径、请求体、响应格式 |
| **数据库** | 3 张表的字段定义、迁移策略 |
| **环境变量** | 17 个配置项及默认值（4 家 LLM Provider） |
| **风格系统** | 9 个内置风格 + 自定义风格的 CRUD 流程 |
| **PPT 系统** | 4 主题、6 版式、配图降级策略 |
| **认证系统** | JWT 流程、前后端 token 传递链路 |
| **操作指南** | 添加新风格/新导出格式/新 API/新 DB 模型的步骤 |
| **常用命令** | 启动/构建/测试/部署命令 |
| **竞品分析** | 文档格式约定 |

## 前提条件

- 在本项目根目录（`my_first/`）下启动 Devin 会话
- skill 文件位于 `.devin/skills/ai-writer/SKILL.md`（随 git 仓库分发）

## 权限

此 skill 自动授权以下操作（无需逐次确认）：

| 权限 | 范围 |
|------|------|
| 读取 | 所有文件 |
| 写入 | `backend/**`、`frontend/src/**`、`docs/**`、`tests/**` |
| 执行 | `npm`、`uv`、`python3`、`curl`、`git`、`kill`、`lsof` |

## 维护

当项目架构发生变化时（新增路由、新增组件、新增数据库表等），请同步更新 `SKILL.md` 中的对应章节，保持信息准确。
