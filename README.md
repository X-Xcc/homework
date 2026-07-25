# 法律材料工作台

面向内部法律学习、研究和材料处理的小型 AI 工作台。系统围绕法律材料组织法条检索、文档分析、文档对比、上下文问答、收藏、历史和报告导出。

## 当前能力

- 用户注册、登录、刷新令牌和管理员权限控制
- 法条关键词搜索、详情查看和相似法条检索
- 合同及法律文档上传、文本解析、OCR 回退和 AI 风险分析
- 两份文档的差异分析
- 绑定材料上下文的多轮 AI 问答
- 分析记录、对话、收藏、历史和工作台统计
- TXT、DOCX、PDF 分析报告导出
- 管理员用户管理、分析记录和基础统计

> AI 输出用于学习和辅助审阅，不能替代律师判断、正式法律意见或人工复核。

## 技术栈

| 部分 | 技术 |
| --- | --- |
| 后端 | Python 3.11、FastAPI、SQLAlchemy Async、SQLite/aiosqlite |
| 检索 | 本地法条 JSON、ChromaDB、TF-IDF 向量检索 |
| AI | OpenAI-compatible Chat Completions API |
| OCR | PaddleOCR + Tesseract 回退 |
| 前端 | React 19、TypeScript、Vite 7、React Router、TanStack Query |
| 测试 | pytest、Vitest、Testing Library |

## 快速开始

### 1. 创建后端环境

Windows PowerShell：

\`\`\`powershell
py -3.11 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt
\`\`\`

开发依赖：

\`\`\`powershell
.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements-dev.txt
\`\`\`

### 2. 配置环境变量

\`\`\`powershell
Copy-Item backend\\.env.example backend\\.env
\`\`\`

至少配置以下变量：

\`\`\`dotenv
AI_API_KEY=your_api_key
AI_API_URL=https://api.deepseek.com/v1/chat/completions
AI_MODEL=your_model
JWT_SECRET=replace-with-a-long-random-secret
\`\`\`

不要把 \`backend/.env\`、真实合同、用户上传文件或 API 密钥提交到 GitHub。

常用配置：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| \`AI_API_KEY\` | 空 | AI 服务密钥；为空时 AI 功能不可用 |
| \`AI_API_URL\` | DeepSeek 兼容接口 | OpenAI-compatible API 地址 |
| \`AI_MODEL\` | \`deepseek-v4-flash\` | 使用的模型名称 |
| \`DATABASE_URL\` | SQLite | 异步 SQLAlchemy 数据库地址 |
| \`JWT_SECRET\` | 开发占位值 | 生产或共享环境必须修改 |
| \`CORS_ALLOW_ORIGINS\` | 本地前后端地址 | 逗号分隔的白名单 |
| \`MAX_FILE_SIZE\` | \`10485760\` | 上传文件大小上限，单位字节 |
| \`OCR_PRIMARY_ENGINE\` | \`paddle\` | OCR 主引擎 |
| \`OCR_FALLBACK_ENGINE\` | \`tesseract\` | OCR 回退引擎 |

### 3. 启动后端

\`\`\`powershell
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
\`\`\`

- API 文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

### 4. 启动前端

\`\`\`powershell
Set-Location frontend
npm install
npm run dev
\`\`\`

打开 <http://127.0.0.1:5173>。前端开发服务器会将 API 请求发送到本地后端。

### 5. 单端口运行

\`\`\`powershell
Set-Location frontend
npm run build
Set-Location ..
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
\`\`\`

构建后的 \`frontend/dist\` 会由 FastAPI 提供静态页面。

## Docker

准备 \`.env\` 后运行：

\`\`\`powershell
docker compose up --build
\`\`\`

应用默认监听 \`http://127.0.0.1:8000\`。容器数据通过 \`app_data\` 和 \`app_uploads\` volume 保存。

Docker 配置默认使用 SQLite。PostgreSQL 配置目前作为可选部署参考，正式启用前需要完成数据库迁移验证。

## 使用流程

### 实务材料处理

1. 注册或登录账号。
2. 上传合同或其他法律文档。
3. 等待解析和 AI 分析完成。
4. 查看摘要、风险等级、风险说明、法律依据和修改建议。
5. 在当前材料上下文中继续提问。
6. 将结果保存到历史或收藏，并导出报告。

### 学习和研究

1. 搜索法条或上传判决书、课程资料。
2. 查看摘要、关键词和相关法条。
3. 围绕当前材料提问，要求解释概念或比较规则。
4. 保存重要法条、分析结果和对话记录。

## 项目结构

\`\`\`text
backend/
  app/
    api/          API 路由、鉴权依赖和导出
    core/         AI、OCR、法条检索、文档解析和安全能力
    models/       SQLAlchemy 模型和 Pydantic schema
  tests/          后端测试
  data/           法条、模板和知识库数据
frontend/
  src/
    app/          路由、布局和全局 provider
    pages/        用户端和管理端页面
    shared/       API 客户端、布局和 UI 组件
docs/             API、部署、用户指南、审计和推进计划
scripts/          法条/知识库构建与诊断脚本
\`\`\`

## 测试与质量检查

后端：

\`\`\`powershell
Set-Location backend
..\\.venv\\Scripts\\python.exe -m pytest
\`\`\`

前端：

\`\`\`powershell
Set-Location frontend
npm test -- --run
npm run build
npm run lint
\`\`\`

## 文档入口

- [API 参考](docs/api/api-reference.md)
- [部署指南](docs/deployment/deployment-guide.md)
- [用户使用手册](docs/user-guide/user-manual.md)
- [项目推进计划](docs/superpowers/plans/2026-07-25-legal-material-workbench.md)
- [当前状态审计](docs/audit/project-current-state.md)
- [交付范围冻结](docs/audit/delivery-scope-freeze.md)

## 安全和数据说明

- 不要将真实敏感法律材料、API 密钥、数据库文件或上传目录提交到公共仓库。
- 共享环境必须修改 \`JWT_SECRET\`、默认管理员密码和 AI API 密钥。
- AI 结果必须经过人工复核，尤其是法律依据、风险等级和修改建议。
- 当前项目适合内部小组试用，不应直接作为面向公众的法律服务部署。
