# 法律材料工作台

法律材料工作台是一套面向内部小组的法律学习、研究与材料处理系统。系统以法律材料为核心对象，提供法条检索、文档解析、合同风险分析、文档对比、上下文问答、历史追踪与报告导出等能力，帮助用户完成从材料理解到分析沉淀的完整工作流。

> 本项目用于内部学习、研究和辅助审阅。AI 生成内容不构成法律意见，所有关键结论均应结合原文和权威法律资料进行人工复核。

## 一、项目定位

本系统兼顾两类使用场景：

- **法律学习与研究**：检索法条、理解法律概念、分析判决或课程资料、保存学习记录。
- **法律材料处理**：分析合同条款、识别潜在风险、关联法律依据、提出修改建议、生成审阅报告。

两类场景共享同一套材料、检索、问答和历史能力，避免形成彼此割裂的功能系统。

## 二、主要功能

### 1. 用户与权限

- 用户注册、登录、退出和令牌刷新。
- 基于 JWT 的身份认证。
- 普通用户与管理员角色隔离。
- 用户数据按账号隔离，管理员可查看系统级统计和管理记录。

### 2. 法条检索

- 按法规名称、条款编号和关键词检索。
- 支持刑法、民法典及扩展知识库。
- 支持法条详情查看、分类筛选和相似法条检索。
- 支持从分析结果跳转到相关法律依据。

### 3. 文档处理与分析

- 支持合同及其他法律材料上传。
- 支持 DOCX、PDF、TXT 等常见文档处理流程。
- 支持文本提取和 OCR 回退。
- 生成摘要、风险等级、风险说明、法律依据和修改建议。
- 支持流式分析结果和分析历史查看。

### 4. 文档对比

- 上传两个版本的法律文档。
- 生成变更摘要和差异项。
- 重点辅助比较责任、付款、期限、违约和争议解决等条款。

### 5. 上下文问答

- 创建和保存多轮会话。
- 围绕当前文档或分析结果进行追问。
- 支持询问原文位置、法律依据、概念解释和条款差异。
- 对话记录纳入历史管理。

### 6. 工作台与管理

- 查看最近分析、对比和对话记录。
- 管理收藏和个人历史。
- 导出 TXT、DOCX、PDF 格式的分析报告。
- 管理员查看用户、分析记录、对比记录、会话记录和基础统计。

## 三、技术架构

| 层级 | 技术与职责 |
| --- | --- |
| 前端 | React 19、TypeScript、Vite 7、React Router、TanStack Query |
| 后端 | Python 3.11、FastAPI、SQLAlchemy Async |
| 数据库 | SQLite/aiosqlite，支持通过 `DATABASE_URL` 配置其他异步 SQLAlchemy 数据库 |
| 法条检索 | 本地 JSON 知识库、ChromaDB、TF-IDF 向量检索 |
| AI 服务 | OpenAI-compatible Chat Completions API |
| 文档处理 | DOCX、PDF、TXT 文本提取与 OCR |
| OCR | PaddleOCR 主引擎、Tesseract 回退引擎 |
| 测试 | pytest、Vitest、Testing Library |

系统采用单体架构。分析、问答、检索、收藏和导出通过用户、材料及业务记录关联，便于内部部署和后续维护。

## 四、快速开始

### 1. 环境要求

- Python 3.11 或更高版本。
- Node.js 18 或更高版本，建议使用 LTS。
- Windows、Linux 或 macOS 均可运行。
- 使用 Docker 部署时需要 Docker Desktop 或兼容 Docker 的运行环境。

### 2. 创建后端环境

Windows PowerShell：

~~~powershell
py -3.11 -m venv .venv
.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements.txt
~~~

安装测试和开发依赖：

~~~powershell
.\\.venv\\Scripts\\python.exe -m pip install -r backend\\requirements-dev.txt
~~~

### 3. 配置环境变量

复制配置模板：

~~~powershell
Copy-Item backend\\.env.example backend\\.env
~~~

至少配置以下内容：

~~~dotenv
AI_API_KEY=your_api_key
AI_API_URL=https://api.deepseek.com/v1/chat/completions
AI_MODEL=your_model
JWT_SECRET=replace-with-a-long-random-secret
~~~

配置文件说明：

| 变量 | 默认值 | 说明 |
| --- | --- | --- |
| `AI_API_KEY` | 空 | AI 服务密钥；为空时 AI 分析和问答不可用 |
| `AI_API_URL` | DeepSeek 兼容接口 | OpenAI-compatible API 地址 |
| `AI_MODEL` | `deepseek-v4-flash` | 使用的模型名称 |
| `DATABASE_URL` | SQLite | 异步 SQLAlchemy 数据库地址 |
| `JWT_SECRET` | 开发占位值 | 共享或生产环境必须修改 |
| `CORS_ALLOW_ORIGINS` | 本地前后端地址 | 逗号分隔的来源白名单 |
| `MAX_FILE_SIZE` | `10485760` | 上传文件大小上限，单位为字节 |
| `OCR_PRIMARY_ENGINE` | `paddle` | OCR 主引擎 |
| `OCR_FALLBACK_ENGINE` | `tesseract` | OCR 回退引擎 |

不要将 `backend/.env`、真实法律材料、用户上传目录、数据库文件或 API 密钥提交到 GitHub。

### 4. 启动后端

~~~powershell
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
~~~

启动后可访问：

- OpenAPI 文档：<http://127.0.0.1:8000/docs>
- 健康检查：<http://127.0.0.1:8000/health>

### 5. 启动前端

~~~powershell
Set-Location frontend
npm install
npm run dev
~~~

打开 <http://127.0.0.1:5173>。开发环境下，前端通过 Vite 访问本地后端 API。

### 6. 单端口运行

先构建前端：

~~~powershell
Set-Location frontend
npm run build
Set-Location ..
~~~

再启动后端：

~~~powershell
.\\.venv\\Scripts\\python.exe -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --app-dir backend
~~~

构建后的 `frontend/dist` 会由 FastAPI 提供静态页面。

## 五、Docker 部署

准备 Docker 环境变量后执行：

~~~powershell
docker compose config
docker compose up --build
~~~

应用默认监听 `http://127.0.0.1:8000`。容器使用 `app_data` 和 `app_uploads` volume 保存应用数据与上传文件。

当前 Docker 配置默认使用 SQLite。PostgreSQL 配置作为后续部署选项保留，正式启用前应完成迁移、备份和恢复验证。

详细说明见 [部署指南](docs/deployment/deployment-guide.md)。

## 六、典型使用流程

### 实务材料处理

1. 注册或登录账号。
2. 上传合同或其他法律材料。
3. 等待文本解析和 AI 分析完成。
4. 查看摘要、总体评分、风险等级、风险说明和法律依据。
5. 核对风险对应的原文位置，并结合实际业务背景判断建议是否适用。
6. 围绕当前材料继续提问。
7. 保存历史、收藏重要内容或导出分析报告。

### 学习与研究

1. 搜索法条，或上传判决书、课程资料和研究材料。
2. 查看摘要、关键词、条款详情及关联法条。
3. 在材料上下文中提问，要求解释概念、比较规则或梳理争议点。
4. 保存重要法条、分析结论和对话记录，形成可复用的学习资料。

## 七、项目结构

~~~text
backend/
  app/
    api/          API 路由、鉴权依赖和报告导出
    core/         AI、OCR、法条检索、文档解析和安全能力
    models/       SQLAlchemy 模型和 Pydantic 数据模型
  tests/          后端测试
  data/           法条、模板和知识库数据
frontend/
  src/
    app/          路由、布局和全局 Provider
    pages/        用户端和管理端页面
    shared/       API 客户端、布局和通用 UI 组件
docs/             API、部署、用户指南、审计和推进计划
scripts/          法条、知识库构建与诊断脚本
~~~

## 八、测试与质量检查

运行后端测试：

~~~powershell
Set-Location backend
..\\.venv\\Scripts\\python.exe -m pytest
~~~

运行前端测试和构建：

~~~powershell
Set-Location frontend
npm test -- --run
npm run build
~~~

运行前端代码检查：

~~~powershell
npm run lint
~~~

当前基线验证结果：

- 后端 pytest：34 项通过。
- 前端 Vitest：17 项通过。
- 前端生产构建：通过。
- 后端 Ruff 和前端 ESLint 仍有待清理的问题，详见项目审查报告和 Draft PR。

## 九、文档索引

- [API 参考](docs/api/api-reference.md)
- [部署指南](docs/deployment/deployment-guide.md)
- [用户使用手册](docs/user-guide/user-manual.md)
- [项目推进计划](docs/superpowers/plans/2026-07-25-legal-material-workbench.md)
- [当前状态审计](docs/audit/project-current-state.md)
- [交付范围冻结](docs/audit/delivery-scope-freeze.md)
- [代码审查报告](CODE_REVIEW_REPORT.md)

## 十、安全与使用边界

- 共享环境必须修改 `JWT_SECRET`、默认管理员密码和 AI API 密钥。
- 真实法律材料应在上传前完成脱敏，并按照内部数据管理规范保存。
- AI 结果必须回到原文和权威法律资料进行核验。
- 风险等级、法律依据和修改建议不应未经人工审阅直接对外使用。
- 当前项目适合内部小组试用，不应直接作为面向公众的法律服务系统部署。
