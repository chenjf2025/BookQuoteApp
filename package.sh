#!/bin/bash

# Book Quote App 打包脚本
# 该脚本会自动编译两个 React 前端，并将服务器所需的文件打包为 tar.gz。

echo "========================================="
echo "开始编译打包 Book Quote App..."
echo "========================================="

# 1. 编译 PC 前端
echo ">>> 正在编译 PC 端 (frontend)..."
cd frontend
npm install
npm run build
cd ..

# 2. 编译 H5 前端
echo ">>> 正在编译 H5 小程序端 (h5_frontend)..."
cd h5_frontend
npm install
# 构建时修改 Vite 的 base path，因为部署在 Nginx 的 /h5 下
npx vite build --base=/h5/
cd ..

# 3. 更新依赖清单
echo ">>> 更新 Python 后端依赖 (requirements.txt)..."
cd backend
pip freeze > requirements.txt
cd ..

# 4. 打包源文件
echo ">>> 正在将核心文件压制为 tar.gz 压缩包..."
TAR_FILE="BookQuoteApp_Release.tar.gz"

tar --exclude='backend/venv' \
    --exclude='backend/__pycache__' \
    --exclude='backend/app.db' \
    --exclude='backend/.env' \
    --exclude='backend/static/*' \
    --exclude='frontend/node_modules' \
    --exclude='h5_frontend/node_modules' \
    --exclude='.git' \
    --exclude='.DS_Store' \
    -czvf $TAR_FILE \
    backend \
    frontend/dist \
    h5_frontend/dist \
    DEPLOYMENT_UBUNTU.md \
    package.sh

echo "========================================="
echo "打包顺利完成！✅"
echo "发布包文件已生成: ${TAR_FILE}"
echo "现可将该文件传输到 Ubuntu Server 服务器，并参考 DEPLOYMENT_UBUNTU.md 指引展开部署。"
echo "========================================="
