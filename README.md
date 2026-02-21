# Book Quote Generator (书籍金句与思维导图生成器)

这是一个全栈的 AI 阅读辅助工具。依托于大语言模型的惊人总结能和全网搜索，它可以根据书名，全自动提炼出该书的核心观点与高赞金句，并一键渲染生成**精美朋友圈配图**与**极具科技感的高清思维导图（支持JPG/PDF/XMind等跨平台格式导出）**。

工程架构包含三个部分：
- **PC 前端网站** (React + Vite)
- **H5 移动端小程序** (React + Vite)
- **AI 渲染后端** (Python FastAPI + Node.js Puppeteer)

## 🌟 核心功能

- 🤖 **AI 名人金句海报生成**：一键归纳全网经典语录，搭配智谱底层文生图视觉配图，自动排版 4 款极致版式的朋友圈海报。
- 📊 **智能思维导图拆解**：大模型结构化提取“内容简介/作者洞见/核心观点”，绘制出极其出彩的赛博暗黑风交互导图。
- 📥 **多格式超清无损导出**：基于底层服务器发起的图形引擎渲染，打破设备限制，直接提供下载千万级像素的高清长图 (JPG)、纯净高分辨率 (PDF)，以及原生支持无缝导入 XMind/MindManager 的 Markdown 源文件。

---

## 🛠️ 本地开发与体验

### 1. 获取代码
```bash
git clone https://github.com/chenjf2025/BookQuoteApp.git
cd BookQuoteApp
```

### 2. 后端核心服务启动 (重中之重)
后端负责着极其复杂的爬原数据、调大模型驱动分工协作、以及呼叫图形系统进行截图。

**环境搭建：**
```bash
cd backend

# 安装 Python 相关环境
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# 下载图形渲染组件（非常重要，少装图形引擎画不出导图）
npm init -y
npm install puppeteer markmap-cli
npx puppeteer browsers install chrome
```

**配置极其重要的 `.env` 环境变量：**
请必须手动在 **`backend` 目录下** 创建一个叫 `.env` 的文本文件。后端离开了大脑 API Key 无法运作，请在 `.env` 中填入：
```env
# -----------------------------
# 复制以下内容保存为 backend/.env 文件
# -----------------------------

# 1. 深度求索 (DeepSeek API Key) - 必填，用于绝大部分强大的逻辑推理、内容归纳和海报大纲的结构化分发
DEEPSEEK_API_KEY=sk-xxxxxxxxxxxx

# 2. 智谱 AI (Zhipu API Key) - 必填，专门用来画海报里的写实/水墨/油画风精美配图
ZHIPU_API_KEY=xxxxxx.xxxxxx

# 其他后台运行参数（如 JWT 安全秘钥鉴权，可自行修改加强安全性，保持默认也可运行）
SECRET_KEY=your_super_secret_key_here
```

**运行服务端：**
```bash
# 开启本机的 API 节点服务 
uvicorn main:app --reload --host 127.0.0.1 --port 8000
```

### 3. Web & H5 端启动

```bash
# 启动 PC 大屏版 (默认运行在 http://localhost:5173)
cd frontend
npm install
npm run dev

# -- 另开一个终端窗口 --

# 启动手机 H5 小屏端 (默认运行在 http://localhost:5174)
cd h5_frontend
npm install
npm run dev
```

---

## 🚀 生产环境服务部署 (Linux / Ubuntu)

当您在本地开发完毕，准备将服务彻底搬上云服务器做成真实的网络服务时，我们已经为您排查过了所有的坑！

请直接参阅根目录下的绝杀出海秘籍：**[DEPLOYMENT_UBUNTU.md](./DEPLOYMENT_UBUNTU.md)**

这篇部署文档涵盖了大量生产级别实战经验，包括且不限于：
1. **Nginx 子目录与 API 的完美反向代理映射规则**。
2. **PM2 系统常驻守护进程的后台命令配置**。
3. 如何使用最高权力的 `apt-get` 解决在纯命令行虚拟云主机上**强装图形依赖 (libnss3/libasound2t64)**，并躲开由于缺失显卡/共享内存引发的 `SIGABRT -6` Node.js 底层恐怖崩溃！

## 📦 自动化发布打包

如果您在本地修改了任意细节准备上服更新，再也不用手动压缩几十个文件夹了。
在根目录下双击或者执行：
```bash
./package.sh
```
该引擎会为您自动压缩打包好编译完毕的精简静态 `dist` 并携带后端业务，吐出一枚轻快的 `BookQuoteApp_Release.tar.gz` 升级包，您只管扔进服务器 `tar` 命令解压覆盖替换即能秒更新！
