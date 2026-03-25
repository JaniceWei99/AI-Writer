# AI 写作助手 — 部署指南

本文档介绍如何在本地或服务器上部署 **AI 写作助手** 应用。

---

## 目录

1. [环境要求](#1-环境要求)
2. [Ollama 安装与配置](#2-ollama-安装与配置)
3. [后端部署](#3-后端部署)
4. [前端部署](#4-前端部署)
5. [环境变量与配置项](#5-环境变量与配置项)
6. [Docker 一键部署（共享/团队模式）](#6-docker-一键部署共享团队模式)
7. [Nginx 反向代理配置示例](#7-nginx-反向代理配置示例)
8. [常见问题](#8-常见问题)

---

## 1. 环境要求

| 依赖    | 最低版本 | 说明                   |
| ------- | -------- | ---------------------- |
| Python  | 3.10+    | 后端运行环境           |
| Node.js | 18+      | 前端构建与开发         |
| Ollama  | 最新版   | 本地大语言模型推理引擎 |
| uv      | 最新版   | Python 依赖管理工具    |

请在部署前确认以上工具均已安装：

```bash
python --version   # 应输出 Python 3.10 或更高
node --version     # 应输出 v18 或更高
ollama --version   # 确认 Ollama 已安装
uv --version       # 确认 uv 已安装
```

> **提示：** 如果尚未安装 `uv`，可通过以下命令快速安装：
>
> ```bash
> curl -LsSf https://astral.sh/uv/install.sh | sh
> ```

---

## 2. Ollama 安装与配置

### 2.1 安装 Ollama

前往 [Ollama 官网](https://ollama.com/) 下载并安装适合你操作系统的版本。

Linux 用户可直接运行：

```bash
curl -fsSL https://ollama.com/install.sh | sh
```

### 2.2 拉取模型

本项目默认使用 `qwen3.5:9b` 模型：

```bash
ollama pull qwen3.5:9b
```

### 2.3 验证安装

```bash
# 查看已下载的模型列表
ollama list

# 确认 Ollama API 可以访问
curl http://localhost:11434/api/tags
```

若返回 JSON 格式的模型列表，说明 Ollama 服务运行正常（默认监听端口 `11434`）。

---

## 3. 后端部署

后端基于 FastAPI 框架，使用 `uv` 管理依赖，`uvicorn` 作为 ASGI 服务器。

### 3.1 安装依赖

```bash
cd backend
uv sync
```

### 3.2 开发环境启动

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000
```

启动后，后端会自动：
- 创建 `backend/data/` 目录和 SQLite 数据库文件（`app.db`）

可访问：

- API 服务：`http://localhost:8000`
- 健康检查：`http://localhost:8000/api/health`
- 交互式 API 文档：`http://localhost:8000/docs`

### 3.3 生产环境启动

使用多 worker 提高并发能力：

```bash
uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

> **进阶：** 也可以使用 `gunicorn` 搭配 `uvicorn` worker：
>
> ```bash
> uv add gunicorn
> uv run gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker --bind 0.0.0.0:8000
> ```

### 3.4 使用 systemd 管理后端服务（可选）

```ini
# /etc/systemd/system/ai-writing-backend.service
[Unit]
Description=AI Writing Assistant Backend
After=network.target ollama.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/path/to/project/backend
ExecStart=/path/to/.local/bin/uv run uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

```bash
sudo systemctl daemon-reload
sudo systemctl enable ai-writing-backend
sudo systemctl start ai-writing-backend
```

---

## 4. 前端部署

### 4.1 安装依赖

```bash
cd frontend
npm install
```

### 4.2 开发环境启动

```bash
npm run dev
```

开发服务器默认监听 `http://localhost:5173`，支持热更新。

### 4.3 构建生产版本

```bash
npm run build
```

构建产物输出到 `dist/` 目录，可部署到任意静态文件服务器。

### 4.4 本地预览构建产物

```bash
npm run preview
```

### 4.5 部署静态文件

`dist/` 目录中的文件可通过以下方式提供服务：

- **Nginx**（推荐）：参见[第 7 节](#7-nginx-反向代理配置示例)
- **其他静态文件服务器**：

  ```bash
  npx serve dist -s -l 3000
  ```

---

## 5. 环境变量与配置项

所有核心配置均已支持通过 **环境变量** 覆盖，无需修改源代码。项目根目录提供了 `.env.example` 模板，按需复制为 `.env` 即可。

```bash
cp .env.example .env
# 编辑 .env，修改需要覆盖的值
```

### 5.1 后端配置

| 环境变量         | 默认值                                             | 说明                                                                                 |
| ---------------- | -------------------------------------------------- | ------------------------------------------------------------------------------------ |
| `OLLAMA_BASE_URL`  | `http://localhost:11434`                           | Ollama API 地址。Docker 部署时自动设为 `http://ollama:11434`                          |
| `OLLAMA_MODEL`     | `qwen3.5:9b`                                       | 默认 LLM 模型名称，可更换为其他 Ollama 支持的模型                                    |
| `CORS_ORIGINS`     | `http://localhost:5173,http://localhost:3000`      | 逗号分隔的允许来源列表。共享部署可设为 `*` 或实际域名                                 |
| `DATABASE_URL`     | `sqlite+aiosqlite:///backend/data/app.db`          | 数据库连接串。留空使用默认 SQLite；可改为 PostgreSQL 等                               |

**不通过环境变量的配置（需改源码）：**

| 配置项           | 当前值       | 所在文件                           | 说明                                                                                 |
| ---------------- | ------------ | ---------------------------------- | ------------------------------------------------------------------------------------ |
| 请求超时时间     | `120.0` 秒   | `backend/services/ollama_client.py` | 大文本处理可能需要增大                                                               |
| 限流频率         | `10` 次/分钟 | `backend/middleware/rate_limit.py`  | AI 生成端点每 IP 每分钟最大请求数                                                    |
| Unsplash API Key | 无（可选）   | 前端设置面板                        | PPT 导出配图功能所需，在 [Unsplash Developers](https://unsplash.com/developers) 申请 |

### 5.2 前端配置

| 环境变量（构建时） | 默认值 | 说明                                                                   |
| ------------------- | ------ | ---------------------------------------------------------------------- |
| `VITE_API_BASE`       | `""`   | API 基础地址。空字符串 = 同源（SPA 模式由 FastAPI 托管时推荐留空）     |

> **提示：** 前端环境变量在 `npm run build` 时嵌入产物，运行时不可更改。如果前后端分离部署，需在构建前设置 `VITE_API_BASE=https://api.your-domain.com`。

### 5.3 生产环境配置示例

**方式一：使用 `.env` 文件（推荐）**

```bash
# .env
OLLAMA_BASE_URL=http://gpu-server:11434
OLLAMA_MODEL=qwen3.5:9b
CORS_ORIGINS=https://your-domain.com
```

**方式二：Docker 部署（自动配置）**

使用 `docker-compose.yml` 部署时，Ollama 地址会自动设为容器内部网络地址，无需手动配置。详见[第 6 节](#6-docker-一键部署共享团队模式)。

---

## 6. Docker 一键部署（共享/团队模式）

适合需要让**多人共享使用**或在**服务器上长期运行**的场景。Docker 会自动打包前后端并启动 Ollama 服务。

### 6.1 前置要求

| 依赖           | 安装指南                                                                 |
| -------------- | ------------------------------------------------------------------------ |
| Docker Engine  | [安装 Docker](https://docs.docker.com/engine/install/)                   |
| Docker Compose | Docker Desktop 已内置；Linux 另安装 `docker-compose-plugin`              |
| NVIDIA 驱动    | （可选）GPU 加速需要；安装后运行 `nvidia-smi` 确认                       |

### 6.2 快速启动

```bash
# 1. 克隆项目
git clone <repo-url> && cd ai-writing-assistant

# 2. （可选）自定义配置
cp .env.example .env
# 编辑 .env 修改模型名称、端口等

# 3. 构建并启动
docker compose up -d

# 4. 首次启动需拉取模型（约 5 GB，耗时取决于网速）
docker compose exec ollama ollama pull qwen3.5:9b

# 5. 访问应用
#    http://<服务器IP>:8000
```

### 6.3 GPU 加速（NVIDIA）

编辑 `docker-compose.yml`，取消 `ollama` 服务中 `deploy` 部分的注释：

```yaml
ollama:
  image: ollama/ollama:latest
  deploy:
    resources:
      reservations:
        devices:
          - driver: nvidia
            count: all
            capabilities: [gpu]
```

然后重新启动：

```bash
docker compose up -d
```

### 6.4 常用操作

```bash
# 查看运行状态
docker compose ps

# 查看应用日志
docker compose logs -f app

# 查看 Ollama 日志
docker compose logs -f ollama

# 停止所有服务
docker compose down

# 重新构建（代码更新后）
docker compose up -d --build

# 进入 Ollama 容器管理模型
docker compose exec ollama ollama list
docker compose exec ollama ollama pull <model-name>
```

### 6.5 数据持久化

| Docker Volume | 容器路径          | 说明                   |
| ------------- | ----------------- | ---------------------- |
| `app-data`    | `/app/data`       | SQLite 数据库          |
| `ollama-data` | `/root/.ollama`   | Ollama 模型文件        |

数据存储在 Docker Volume 中，`docker compose down` 不会删除。若需彻底清理：

```bash
docker compose down -v   # -v 同时删除 volumes（数据将丢失！）
```

---

## 7. Nginx 反向代理配置示例

将前端静态文件和后端 API 统一在同一域名下，消除跨域问题：

```nginx
server {
    listen 80;
    server_name your-domain.com;

    # 前端静态文件
    root /path/to/project/frontend/dist;
    index index.html;

    # 文件上传大小限制
    client_max_body_size 20m;

    # 后端 API 反向代理
    location /api/ {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # SSE 流式响应支持
        proxy_buffering off;
        proxy_cache off;
        proxy_read_timeout 300s;
    }

    # 前端路由 — SPA 回退
    location / {
        try_files $uri $uri/ /index.html;
    }

    # 静态资源缓存
    location /assets/ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }
}
```

**启用 HTTPS（推荐）：**

```bash
sudo apt install certbot python3-certbot-nginx
sudo certbot --nginx -d your-domain.com
```

---

## 8. 常见问题

### 8.1 Ollama 未运行 / 模型未找到

**症状：** 后端返回连接错误或 500 错误。

**排查步骤：**

```bash
# 1. 检查 Ollama 服务是否运行
curl http://localhost:11434/api/tags

# 2. 如果未运行，启动 Ollama
ollama serve

# 3. 检查模型是否已下载
ollama list

# 4. 如果模型不存在，重新拉取
ollama pull qwen3.5:9b
```

### 8.2 CORS 跨域错误

**症状：** 浏览器控制台出现 `Access-Control-Allow-Origin` 相关错误。

**解决方法：**

1. 确认前端实际访问的地址（包括协议、主机名、端口号）
2. 将该地址添加到环境变量 `CORS_ORIGINS`（逗号分隔）
3. 重启后端服务

> **最佳实践：** 使用 Nginx 反向代理将前后端统一到同一域名下，可彻底避免跨域问题。

### 8.3 文件上传大小限制

**症状：** 上传较大文件时返回 413 错误。

**解决方法：** 在 Nginx 配置中增大 `client_max_body_size`：

```nginx
client_max_body_size 20m;
```

### 8.4 数据库与数据目录

后端启动时会自动在 `backend/data/` 目录下创建 SQLite 数据库文件 `app.db`。该目录和文件会在首次启动时自动生成，无需手动创建。

**注意事项：**
- 多 worker 部署（`--workers > 1`）时，SQLite 可能在高并发下遇到锁竞争。若需更高并发，可考虑迁移到 PostgreSQL。
- 数据库文件应包含在备份策略中。
- `backend/data/` 目录不应加入版本控制（已在 `.gitignore` 中排除）。

### 8.5 WSL 用户注意事项（Windows）

1. **使用 Linux 原生的 Node.js**：不要使用 Windows 侧安装的 Node.js，请在 WSL 内部安装 Linux 版本：

   ```bash
   curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.3/install.sh | bash
   source ~/.bashrc
   nvm install 18
   ```

2. **避免在 /mnt/ 路径下开发**：将项目放在 WSL 的 Linux 文件系统中（如 `~/projects/`），避免放在 `/mnt/c/` 等 Windows 挂载路径下。

3. **Ollama 服务访问**：如果 Ollama 安装在 Windows 侧，WSL 中可能需要通过 Windows 主机 IP 访问而非 `localhost`。

---

## 快速启动清单

```bash
# 1. 启动 Ollama 并确认模型就绪
ollama serve &
ollama pull qwen3.5:9b

# 2. 启动后端
cd backend
uv sync
uv run uvicorn main:app --host 0.0.0.0 --port 8000 &

# 3. 启动前端
cd ../frontend
npm install
npm run dev

# 4. 浏览器访问 http://localhost:5173
```
