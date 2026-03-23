# Windows 一键部署指南

> 本文档面向非技术用户，手把手指导你在 Windows 电脑上部署 AI 写作助手。

---

## 第一步：安装必备软件（仅首次需要）

你需要安装 3 个软件。如果已经装过，可以跳过对应步骤。

### 1.1 安装 Ollama（AI 模型运行环境）

1. 打开浏览器，访问 https://ollama.ai/download
2. 点击 **Download for Windows** 按钮，下载安装文件
3. 双击下载的安装文件（`OllamaSetup.exe`）
4. 按提示一路点 **Next** → **Install** → **Finish**
5. 安装完成后，Ollama 会自动启动，任务栏右下角会出现 Ollama 图标
6. 如果没有自动启动，打开 **开始菜单**，搜索 **Ollama**，点击运行一次

### 1.2 安装 Python 3.12（后端运行环境）

1. 打开浏览器，访问 https://www.python.org/downloads/
2. 点击页面上方黄色的 **Download Python 3.12.x** 按钮
3. 双击下载的安装文件（`python-3.12.x-amd64.exe`）
4. **重要！** 在安装界面底部，**勾选 "Add python.exe to PATH"**（把 Python 加入环境变量）
5. 点击 **Install Now**
6. 等待安装完成，点击 **Close**
7. 验证安装成功：
   - 按 `Win + R`（同时按住 Windows 徽标键和 R 键），弹出"运行"对话框
   - 输入 `cmd`，按回车，打开命令提示符（黑色窗口）
   - 在命令提示符中输入以下命令后按回车：
     ```
     python --version
     ```
   - 应显示 `Python 3.12.x`，说明安装成功
   - 输入 `exit` 关闭命令提示符窗口

> **如果忘记勾选 "Add to PATH"**：卸载 Python 后重新安装，这次记得勾选。或者重新运行安装程序，选择 **Modify** → 勾选 **Add Python to environment variables**。

### 1.3 安装 Node.js（前端构建工具，仅首次需要）

1. 打开浏览器，访问 https://nodejs.org/
2. 点击左侧 **LTS（长期支持版）** 下载按钮（不要选右边的 Current 版本）
3. 双击下载的安装文件（`node-v18.x.x-x64.msi` 或更高版本）
4. 按提示一路点 **Next** → **Install** → **Finish**
5. 验证安装成功：
   - 按 `Win + R`，输入 `cmd`，按回车
   - 输入：
     ```
     node --version
     ```
   - 应显示 `v18.x.x` 或更高版本
   - 输入 `exit` 关闭窗口

---

## 第二步：下载项目代码

### 方式一：Git Clone（推荐，需要安装 Git）

如果你已经安装了 Git：

1. 打开 **命令提示符**：
   - 按 `Win + R`，输入 `cmd`，按回车
2. 输入以下命令，进入桌面：
   ```
   cd %USERPROFILE%\Desktop
   ```
3. 下载项目代码：
   ```
   git clone https://github.com/JaniceWei99/AI-Writer.git
   ```
4. 等待下载完成，桌面上会出现一个 `AI-Writer` 文件夹

> 如果没有安装 Git，可以从 https://git-scm.com/downloads 下载安装（一路默认即可）。

### 方式二：下载 ZIP 压缩包

1. 打开浏览器，访问 https://github.com/JaniceWei99/AI-Writer
2. 点击绿色的 **Code** 按钮 → **Download ZIP**
3. 下载完成后，右键点击 ZIP 文件 → **全部解压缩** → 选择桌面 → **解压缩**
4. 桌面上会出现 `AI-Writer-main` 文件夹

### 方式三：直接拷贝

如果你有项目的文件夹，直接拷贝到电脑上任意位置即可。

---

## 第三步：一键启动

1. 打开 **文件资源管理器**（按 `Win + E`，或点击任务栏的文件夹图标）
2. 找到项目文件夹（例如桌面上的 `AI-Writer`）
3. 双击文件夹中的 **`start.bat`** 文件
4. 如果弹出 **"Windows 已保护你的电脑"** 蓝色提示：
   - 点击 **更多信息**（More info）
   - 点击 **仍要运行**（Run anyway）
5. 命令提示符窗口（黑色窗口）会打开，显示启动进程：
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

直接 **关闭命令提示符窗口**（点击窗口右上角的 X 按钮）即可停止服务。

---

## 日常使用

每次想使用 AI 写作助手时：

1. 双击 **`start.bat`**
2. 等待浏览器自动打开
3. 开始使用
4. 用完后关闭黑色窗口即可

---

## 常见问题

### Q: 首次启动很慢？
A: 正常现象。首次运行需要下载 AI 模型（约 5GB）和安装所有依赖。后续启动约 5 秒。

### Q: 端口 8000 被占用？
A: 脚本会自动终止占用 8000 端口的进程。如果仍有问题：
1. 按 `Win + R`，输入 `cmd`，按回车
2. 输入：
   ```
   netstat -ano | findstr :8000
   ```
3. 记下最后一列的数字（PID），然后输入：
   ```
   taskkill /PID <那个数字> /F
   ```
4. 重新双击 `start.bat`

### Q: 如何更换 AI 模型？
A: 打开应用 → 点击右上角齿轮图标（设置）→ 修改模型名称。确保先下载了对应模型：
1. 按 `Win + R`，输入 `cmd`，按回车
2. 输入：
   ```
   ollama pull <模型名称>
   ```

### Q: 提示 "Python is not recognized" 或 "python not found"？
A: 安装 Python 时没有勾选 "Add python.exe to PATH"。解决方法：
1. 打开 **设置** → **应用** → 找到 **Python 3.12.x** → **卸载**
2. 重新从 https://www.python.org/downloads/ 下载安装
3. **务必勾选 "Add python.exe to PATH"**
4. 安装完成后重新双击 `start.bat`

### Q: 提示 "node is not recognized"？
A: Node.js 没有正确安装。重新从 https://nodejs.org/ 下载 LTS 版本安装。安装完成后**重启电脑**，再重新双击 `start.bat`。

### Q: Ollama 模型下载失败？
A: 可能是网络问题。手动下载：
1. 按 `Win + R`，输入 `cmd`，按回车
2. 输入：
   ```
   ollama pull qwen3.5:9b
   ```
3. 如果仍然失败，尝试使用 VPN 或换一个网络环境。

### Q: 如何更新到最新版本？
A: 
1. 按 `Win + R`，输入 `cmd`，按回车
2. 进入项目文件夹（假设在桌面）：
   ```
   cd %USERPROFILE%\Desktop\AI-Writer
   git pull
   rmdir /s /q frontend\dist
   ```
3. 重新双击 `start.bat`，前端会自动重新构建。

### Q: 双击 start.bat 闪退（窗口一闪就关了）？
A: 手动打开命令提示符来运行脚本，以便看到错误信息：
1. 按 `Win + R`，输入 `cmd`，按回车
2. 进入项目文件夹（假设在桌面）：
   ```
   cd %USERPROFILE%\Desktop\AI-Writer
   ```
3. 运行脚本：
   ```
   start.bat
   ```
4. 查看报错信息，根据提示解决问题
