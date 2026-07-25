# 部署指南

本文档说明如何在本地或 Docker 环境部署法律材料工作台。

## 环境要求

| 环境 | 要求 |
| --- | --- |
| Python | 3.11 或更高版本 |
| Node.js | 18 或更高版本，建议使用 LTS |
| Docker | Docker Desktop，使用 Docker 部署时需要 |
| 操作系统 | Windows、Linux 或 macOS |

后端当前默认使用 SQLite，数据库文件由 \`DATABASE_URL\` 决定；OCR 和 AI 分别依赖本地引擎和外部 API。

## 本地部署

### 安装后端依赖

\`\`\`powershell
py -3.11 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt
\`\`\`

开发和测试依赖：

\`\`\`powershell
.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements-dev.txt
\`\`\`

### 配置环境

\`\`\`powershell
Copy-Item backend\\.env.example backend\\.env
\`\`\`

共享或生产环境至少修改：

\`\`\`dotenv
AI_API_KEY=your_api_key
JWT_SECRET=use-a-long-random-secret
DEFAULT_ADMIN_PASSWORD=use-a-unique-password
\`\`\`

不要将 \`backend/.env\` 提交到 GitHub。

### 启动后端

\`\`\`powershell
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
\`\`\`

### 启动前端

\`\`\`powershell
Set-Location frontend
npm install
npm run dev
\`\`\`

访问 \`http://127.0.0.1:5173\`。若需要单端口运行，先执行 \`npm run build\`，再启动后端；FastAPI 会自动提供 \`frontend/dist\`。

## Docker 部署

在仓库根目录创建 \`.env\`，至少填写：

\`\`\`dotenv
AI_API_KEY=your_api_key
JWT_SECRET=use-a-long-random-secret
DEFAULT_ADMIN_PASSWORD=use-a-unique-password
\`\`\`

构建并启动：

\`\`\`powershell
docker compose config
docker compose up --build -d
\`\`\`

查看日志：

\`\`\`powershell
docker compose logs -f app
\`\`\`

停止服务：

\`\`\`powershell
docker compose down
\`\`\`

应用默认端口为 \`8000\`。\`app_data\` 保存应用数据，\`app_uploads\` 保存上传文件；删除 volume 会导致对应数据丢失。

## 部署验证

### 健康检查

\`\`\`powershell
Invoke-WebRequest http://127.0.0.1:8000/health | Select-Object -ExpandProperty Content
\`\`\`

健康检查会返回数据库、AI、OCR 和向量库状态。没有 AI Key 时服务可能返回 \`503 degraded\`，但账号和不依赖 AI 的接口仍可用于排查部署问题。

### 功能验证

1. 打开前端页面并注册一个普通用户。
2. 登录后访问工作台。
3. 搜索一条法条并打开详情。
4. 上传一个脱敏文档，确认能看到处理状态。
5. AI 配置正确时执行分析和问答。
6. 检查历史记录、收藏和报告导出。
7. 使用管理员账号确认管理员页面可访问，普通用户不能访问。

## 备份建议

SQLite 部署至少备份：

- \`DATABASE_URL\` 指向的 SQLite 数据库文件
- \`UPLOAD_DIR\` 对应的上传目录
- \`backend/data\` 中需要持久化的知识库和向量数据
- 当前 \`.env\` 的安全副本，不要放入代码仓库

备份恢复后，应重新访问 \`/health\`，并验证一条历史分析和一份上传材料。

## 常见问题

### AI 状态为 \`missing_api_key\`

确认 \`backend/.env\` 或 Docker \`.env\` 使用的是 \`AI_API_KEY\`，不是旧文档中的 \`MIMO_API_KEY\`，然后重启后端。

### 前端请求被 CORS 拒绝

将前端地址加入 \`CORS_ALLOW_ORIGINS\`，多个地址使用逗号分隔，并重启后端。

### OCR 不可用

确认 \`OCR_PRIMARY_ENGINE\` 和 \`OCR_FALLBACK_ENGINE\` 已配置，并参考 OCR 部署说明检查对应依赖；纯文本 PDF 或 DOCX 可以先绕过 OCR 验证主流程。

### 生产环境拒绝启动

检查 \`DEBUG=false\` 时是否仍使用默认 \`JWT_SECRET\`。共享环境也应修改默认管理员密码。
