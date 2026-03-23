# macOS 一键部署指南

> 本文档面向非技术用户，手把手指导你在 Mac 上部署 AI 写作助手。

---

## 第一步：安装必备软件（仅首次需要）

你需要安装 3 个软件。如果已经装过，可以跳过对应步骤。

### 1.1 安装 Ollama（AI 模型运行环境）

1. 打开浏览器，访问 https://ollama.ai/download
2. 点击 **Download for macOS** 按钮，下载 `.dmg` 文件
3. 双击下载的 `.dmg` 文件
4. 将 **Ollama** 图标拖入 **Applications（应用程序）** 文件夹
5. 打开 **启动台（Launchpad）**，找到并点击 **Ollama** 启动一次
6. 菜单栏上方会出现一个 Ollama 图标，说明安装成功

### 1.2 安装 Python 3.12（后端运行环境）

**方式一：通过 Homebrew 安装（推荐）**

1. 打开 **终端（Terminal）**：
   - 按 `Command + 空格`，输入 `Terminal`，按回车
   - 或者打开 **访达（Finder）** → **应用程序** → **实用工具** → **终端**
2. 检查是否已安装 Homebrew，在终端输入以下命令后按回车：
   ```
   brew --version
   ```
   - 如果显示版本号（如 `Homebrew 4.x.x`），说明已安装，跳到第 4 步
   - 如果提示 `command not found`，需要先安装 Homebrew，继续第 3 步
3. 安装 Homebrew，在终端粘贴以下命令后按回车（需要输入电脑密码）：
   ```
   /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
   ```
   等待安装完成（可能需要几分钟）
4. 安装 Python，在终端输入：
   ```
   brew install python@3.12
   ```
5. 验证安装成功，输入：
   ```
   python3 --version
   ```
   应显示 `Python 3.12.x`

**方式二：官网下载安装**

1. 打开浏览器，访问 https://www.python.org/downloads/
2. 点击 **Download Python 3.12.x** 按钮
3. 双击下载的 `.pkg` 文件，按提示一路点 **Continue** → **Install**
4. 安装完成后，打开终端验证：
   ```
   python3 --version
   ```

### 1.3 安装 Node.js（前端构建工具，仅首次需要）

**方式一：通过 Homebrew 安装（推荐）**

在终端输入：
```
brew install node
```

**方式二：官网下载安装**

1. 打开浏览器，访问 https://nodejs.org/
2. 点击 **LTS（长期支持版）** 下载按钮
3. 双击下载的 `.pkg` 文件，按提示安装
4. 安装完成后，打开终端验证：
   ```
   node --version
   ```
   应显示 `v18.x.x` 或更高版本

---

## 第二步：下载项目代码

### 方式一：Git Clone（推荐）

1. 打开 **终端**（按 `Command + 空格`，输入 `Terminal`，按回车）
2. 输入以下命令，选择一个你想放置项目的位置（例如桌面）：
   ```
   cd ~/Desktop
   ```
3. 下载项目代码：
   ```
   git clone https://github.com/JaniceWei99/AI-Writer.git
   ```
4. 等待下载完成，桌面上会出现一个 `AI-Writer` 文件夹

### 方式二：直接拷贝

如果你有项目的压缩包或文件夹，直接拷贝到 Mac 上任意位置即可。

---

## 第三步：一键启动

1. 打开 **访达（Finder）**
2. 找到项目文件夹（例如桌面上的 `AI-Writer`）
3. 双击文件夹中的 **`start.command`** 文件
4. 如果弹出安全提示 **"无法打开，因为它来自身份不明的开发者"**：
   - 方法一：**右键点击** `start.command` → 选择 **打开** → 再点 **打开**
   - 方法二：打开 **系统设置** → **隐私与安全性** → 滚动到下方找到 **仍要打开** 按钮
5. 终端窗口会自动打开，显示启动进程：
   ```
   ==========================================
      AI Writing Assistant  v1.3.1
   ==========================================

   [INFO]  Checking Ollama...
   [OK]    Ollama found
   [OK]    Ollama service is already running
   [INFO]  Checking model: qwen3.5:9b ...
   [OK]    Model qwen3.5:9b is ready
   ...
   ```
6. 等待所有步骤完成后，**浏览器会自动打开**，显示 AI 写作助手界面
7. 如果浏览器没有自动打开，手动打开浏览器访问：**http://localhost:8000**

> **首次启动说明**：第一次运行需要下载 AI 模型（约 5GB）和安装依赖，可能需要 10-30 分钟（取决于网速）。之后每次启动只需约 5 秒。

---

## 第四步：停止服务

在终端窗口中按 **`Ctrl + C`**（同时按住 Control 键和 C 键），服务会自动停止。

---

## 日常使用

每次想使用 AI 写作助手时：

1. 双击 **`start.command`**
2. 等待浏览器自动打开
3. 开始使用
4. 用完后按 `Ctrl + C` 停止

---

## 常见问题

### Q: 首次启动很慢？
A: 正常现象。首次运行需要下载 AI 模型（约 5GB）和安装所有依赖。后续启动约 5 秒。

### Q: 端口 8000 被占用？
A: 脚本会自动终止占用 8000 端口的进程。如果仍有问题，打开终端输入：
```
lsof -ti:8000 | xargs kill -9
```
然后重新双击 `start.command`。

### Q: 如何更换 AI 模型？
A: 打开应用 → 点击右上角齿轮图标（设置）→ 修改模型名称。确保先在终端中拉取了对应模型：
```
ollama pull <模型名称>
```

### Q: 如何更新到最新版本？
A: 打开终端，进入项目文件夹，执行：
```
cd ~/Desktop/AI-Writer
git pull
rm -rf frontend/dist
```
然后重新双击 `start.command`，前端会自动重新构建。

### Q: 提示 "Python not found"？
A: 确认 Python 已安装。打开终端输入 `python3 --version`，如果提示找不到命令，请重新按照 1.2 步骤安装 Python。

### Q: Ollama 模型下载失败？
A: 可能是网络问题。打开终端手动下载：
```
ollama pull qwen3.5:9b
```
如果仍然失败，尝试使用 VPN 或换一个网络环境。
