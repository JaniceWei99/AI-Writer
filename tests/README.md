# 测试目录

本目录集中管理 AI 写作助手项目的所有测试资源。

## 目录结构

```
tests/
├── README.md              # 本文件
├── run_tests.sh           # 统一测试运行脚本
├── backend/               # 后端测试用例 (pytest)
│   ├── conftest.py        # pytest 配置 — 将 backend/ 加入 sys.path
│   ├── __init__.py
│   ├── test_routers.py    # API 路由测试（健康检查、上传、处理、流式）
│   ├── test_file_parser.py# 文件解析服务测试（多格式、编码、校验）
│   ├── test_prompts.py    # Prompt 构建测试（风格映射、诗词识别/校验）
│   └── test_schemas.py    # Pydantic 数据模型校验测试
├── frontend/              # 前端测试用例 (vitest)
│   ├── setup.ts           # vitest 初始化（旧版，已弃用）
│   ├── WritingForm.test.tsx   # 写作表单组件测试（含无障碍、语气控制、字数目标、快速启动、高级选项折叠）
│   ├── ResultPanel.test.tsx   # 结果面板组件测试（含无障碍、快速卡片、字数进度、溢出菜单）
│   ├── HistoryPanel.test.tsx  # 历史记录面板组件测试（含无障碍）
│   ├── Accessibility.test.tsx # 无障碍专项测试（ConfirmDialog、SettingsPanel、AuthPanel、StyleEditor）
│   └── history.test.ts        # 历史记录 Service 测试
├── scenarios/             # 测试场景文档
│   ├── backend.md         # 后端测试场景清单（含编号）
│   └── frontend.md        # 前端测试场景清单（含编号）
└── reports/               # 测试报告输出目录
    └── backend_report.html    # pytest-html 生成
```

## 快速开始

### 运行全部测试

```bash
bash tests/run_tests.sh
```

### 只运行后端测试

```bash
bash tests/run_tests.sh backend
```

### 只运行前端测试

```bash
bash tests/run_tests.sh frontend
```

### 直接使用原生命令

```bash
# 后端
cd backend && uv run pytest

# 前端
cd frontend && npx vitest run
```

## 测试框架

| 端 | 框架 | 说明 |
|----|------|------|
| 后端 | pytest 9.x + pytest-asyncio | pytest-html（self-contained HTML） |
| 前端 | vitest 4.x + @testing-library/react | happy-dom 环境 |

## 测试场景文档

详细的测试场景清单见 `scenarios/` 目录：

- [`scenarios/backend.md`](scenarios/backend.md) — 后端 4 大模块、50+ 场景
- [`scenarios/frontend.md`](scenarios/frontend.md) — 前端 8 大模块、66 场景（含无障碍测试、快速启动、语气控制、字数目标、溢出菜单）

每个场景包含编号、场景描述和预期结果，便于追溯和回归。

## 注意事项

- 前端测试 setup 文件位于 `frontend/src/test-setup.ts`（vitest 4.x 要求 setup 文件在 `node_modules` 可达范围内）
- `history.test.ts` 需要后端运行才能通过（历史服务已迁移至后端 API）
