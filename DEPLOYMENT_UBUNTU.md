# Book Quote App - Ubuntu 22.04 生产环境部署指南

本指南将指导您如何在干净的 Ubuntu 22.04 LTS 服务器上部署本项目的后端（FastAPI）、PC 端前端（React）和 H5 小程序前端（React）。

## 1. 基础环境准备

首先，连接到您的 Ubuntu 服务器并更新系统包，安装 Python、Node.js、Nginx 以及 Puppeteer 依赖的系统字体和图形库：

```bash
sudo apt update && sudo apt upgrade -y

# 安装 Python 3.10+ 及虚拟环境支持
sudo apt install -y python3 python3-pip python3-venv

# 安装 Node.js (推荐 18.x 或 20.x)
curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash -
sudo apt install -y nodejs

# 安装 Nginx (用于托管前端页面及反向代理后端)
sudo apt install -y nginx

# 【关键】安装 Puppeteer (无头浏览器) 运行所需的底层依赖及中文字体
sudo apt install -y libx11-xcb1 libxcomposite1 libxdamage1 libxext6 libxfixes3 \
    libnss3 libcups2 libxrandr2 libasound2t64 libpangocairo-1.0-0 libatk1.0-0 \
    libatk-bridge2.0-0 libgtk-3-0 libgbm1
sudo apt install -y fonts-noto-cjk fonts-wqy-zenhei

# 安装进程守护工具 PM2
sudo npm install -g pm2
```

## 2. 上传与解压代码

在您的本地电脑上运行打包脚本 `package.sh`（位于项目根目录），它会生成 `BookQuoteApp_Release.tar.gz`。将该压缩包上传到 Ubuntu 服务器（例如放在 `/var/www/` 目录下）：

```bash
# 在 Ubuntu 上解压
mkdir -p /var/www/BookQuoteApp
tar -xzvf BookQuoteApp_Release.tar.gz -C /var/www/BookQuoteApp
cd /var/www/BookQuoteApp
```

## 3. 后端服务部署 (FastAPI)

```bash
cd /var/www/BookQuoteApp/backend

# 1. 创建并激活 Python 虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装 Python 依赖（请确保 backend 目录下有 requirements.txt，或手动安装）
pip install fastapi uvicorn python-dotenv pydantic requests pillow duckduckgo-search zhipuai sqlalchemy bcrypt pyjwt passlib

# 3. 安装后端 Node.js 依赖 (用于执行 Puppeteer 和 markmap 渲染)
npm init -y
npm install puppeteer markmap-cli
npx puppeteer browsers install chrome

# 4. 配置环境变量
# 请在 backend 目录下创建 .env 文件，并填入您的 API Keys
nano .env
# 内容示例:
# DEEPSEEK_API_KEY=your_key_here
# ZHIPU_API_KEY=your_key_here

# 5. 使用 PM2 启动后台守护进程运行 FastAPI
pm2 start venv/bin/python3 --name "bookquote-api" -- -m uvicorn main:app --host 127.0.0.1 --port 8000
pm2 save
pm2 startup
```

## 4. Nginx 路由代理与前端部署

前端项目（`frontend` 和 `h5_frontend`）已经在打包压缩前编译成了静态的 `dist` 文件夹结构。我们直接配置 Nginx 托管它们。

编辑 Nginx 配置文件：
```bash
sudo nano /etc/nginx/sites-available/bookquote.conf
```

填入以下 Nginx 配置内容（假设您的服务器 IP 或域名是 `your_domain_or_ip`）：

```nginx
server {
    listen 80;
    server_name your_domain_or_ip; # 修改为您的服务器 IP 或域名

    # 1. 部署 PC 端官网 (默认根挂载)
    location / {
        root /var/www/BookQuoteApp/frontend/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }

    # 2. 部署 H5 小程序端 (挂载在 /h5 路径下)
    location /h5/ {
        alias /var/www/BookQuoteApp/h5_frontend/dist/;
        index index.html;
        try_files $uri $uri/ /h5/index.html;
    }

    # 3. 反向代理到 Python FastAPI 后端
    location /api/ {
        proxy_pass http://127.0.0.1:8000/api/;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }

    # 4. 反向代理获取后端生成的 PDF/JPG/MindMap 静态文件
    location /static/ {
        proxy_pass http://127.0.0.1:8000/static/;
        autoindex off;
    }
}
```

保存后，启用该配置并重启 Nginx：

```bash
sudo ln -s /etc/nginx/sites-available/bookquote.conf /etc/nginx/sites-enabled/
sudo nginx -t
sudo systemctl restart nginx
```

## 5. 校验与日常维护

到此为止，您的应用已经发布成功：
- 访问桌面端：`http://your_domain_or_ip/`
- 访问 H5 端：`http://your_domain_or_ip/h5/`

**日常维护命令：**
- 查看 API 运行日志：`pm2 logs bookquote-api`
- 重启 API 服务：`pm2 restart bookquote-api`
- 刷新前端静态资源：直接覆盖 `/var/www/BookQuoteApp/frontend/dist` 即可瞬间生效。
