# 项目现状审计文档

## 1. 文档目的

说明本项目在正式工程化改造开始前的真实状态，为后续范围冻结、技术治理、数据库升级、测试补齐和部署建设提供基线依据。

## 2. 项目概览

- 项目名称：法律AI - 智能法律顾问系统
- 版本阶段：可运行原型 / MVP
- 审计日期：2026-06-08
- 审计人：AI 协作审计

## 3. 项目定位

该项目面向法律咨询、合同审查和基础法务辅助场景，当前已经具备法条搜索、文档分析、文档对比、智能问答、合同模板库、用户工作台/历史/收藏等主流程能力。

从代码状态看，系统已达到“本地可运行、可演示、具备完整业务闭环”的原型阶段，但尚未达到正式交付所需的安全性、可测试性、可部署性和可维护性标准。

## 4. 当前功能现状

| 功能模块 | 页面入口 | 后端接口 | 当前状态 | 备注 |
|---|---|---|---|---|
| 法条搜索 | 搜索页 | `/api/search/law`、`/api/search/law/{article_id}` | 可用 | 支持刑法、民法典检索 |
| 相似法条搜索 | 搜索页/潜在增强入口 | `/api/search/similar` | 基本可用 | 依赖 ChromaDB 向量能力 |
| 文档分析 | 上传页 | `/api/document/analyze`、`/api/document/analyze/stream`、`/api/document/analysis/{id}` | 可用 | 支持 AI 风险识别与评分 |
| 文档对比 | 上传页 | `/api/document/compare`、`/api/document/comparisons/{id}` | 可用 | 依赖 AI 返回变更摘要 |
| 智能问答 | 工作台/聊天页 | `/api/chat/sessions`、`/api/chat/sessions/{id}`、`/api/chat/sessions/{id}/messages`、流式接口 | 可用 | 支持会话持久化 |
| 合同模板库 | 模板页 | `/api/templates`、`/api/templates/{id}`、`/api/templates/categories/list` | 可用 | 数据源为本地 JSON |
| 用户注册与登录 | 门户/登录/注册页 | `/api/user/register`、`/api/user/login`、`/api/user/me` | 待正式化实现 | 目标为本地账号密码 + 自注册体系 |
| 用户登录 | 预留能力 | `/api/user/login` | 基本可用 | 当前需升级为正式密码登录与会话机制 |
| 收藏 | 收藏页 | `/api/user/favorites` | 可用 | 支持新增、删除、列表 |
| 历史记录 | 历史页 | `/api/user/history` | 可用 | 聚合 chat / analysis / comparison |
| 工作台统计 | 首页/工作台 | `/api/user/workspace` | 可用 | 提供最近记录与统计 |
| 健康检查 | 无前端入口 | `/health` | 可用 | 仅基础存活探针 |

## 5. API 现状

| 模块 | 方法 | 路径 | 用途 | 是否核心链路 | 风险备注 |
|---|---|---|---|---|---|
| search | GET | `/api/search/law` | 法条搜索 | 是 | 无鉴权、无限流 |
| search | GET | `/api/search/law/{article_id}` | 查看法条详情 | 是 | 无鉴权 |
| search | GET | `/api/search/similar` | 相似法条检索 | 否 | 向量检索稳定性待验证 |
| document | POST | `/api/document/analyze` | 文档分析 | 是 | 上传安全与 AI 容错需加强 |
| document | POST | `/api/document/analyze/stream` | 流式文档分析 | 是 | 流式 JSON 容错较弱 |
| document | POST | `/api/document/compare` | 双文档对比 | 是 | 上传安全与 AI 容错需加强 |
| document | GET | `/api/document/analysis/{id}` | 查看分析结果 | 是 | 依赖伪身份模型 |
| document | GET | `/api/document/comparisons/{id}` | 查看对比结果 | 是 | 依赖伪身份模型 |
| chat | POST | `/api/chat/sessions` | 创建会话 | 是 | 依赖伪身份模型 |
| chat | GET | `/api/chat/sessions` | 会话列表 | 是 | 依赖伪身份模型 |
| chat | GET | `/api/chat/sessions/{id}` | 查看会话详情 | 是 | 依赖伪身份模型 |
| chat | POST | `/api/chat/sessions/{id}/messages` | 发送消息 | 是 | 无速率限制、AI 异常直接露原始文本 |
| chat | POST | `/api/chat/sessions/{id}/messages/stream` | 流式问答 | 是 | 流式异常处理较弱 |
| chat | DELETE | `/api/chat/sessions/{id}` | 删除会话 | 否 | 依赖伪身份模型 |
| user | POST | `/api/user/register` | 用户注册 | 是 | 第一版应支持自注册与唯一性校验 |
| user | POST | `/api/user/login` | 登录 | 是 | 需补密码校验、会话或 token 机制 |
| user | GET | `/api/user/me` | 当前用户信息 | 是 | 身份来源不可信 |
| user | GET | `/api/user/profile/{user_id}` | 用户资料 | 否 | 仅靠 user_id 校验 |
| user | GET | `/api/user/history` | 历史记录 | 是 | 聚合逻辑已成型 |
| user | POST | `/api/user/favorites` | 添加收藏 | 否 | 入参校验较弱 |
| user | DELETE | `/api/user/favorites/{favorite_id}` | 删除收藏 | 否 | 依赖伪身份模型 |
| user | GET | `/api/user/favorites` | 收藏列表 | 否 | 依赖伪身份模型 |
| user | GET | `/api/user/workspace` | 工作台摘要 | 是 | 依赖伪身份模型 |
| templates | GET | `/api/templates` | 模板列表 | 是 | 读本地 JSON，无持久使用统计 |
| templates | GET | `/api/templates/categories/list` | 模板分类 | 否 | 风险较低 |
| templates | GET | `/api/templates/{id}` | 模板详情 | 是 | 风险较低 |
| system | GET | `/health` | 健康检查 | 是 | 仅返回 `status=ok` |

## 6. 数据模型现状

| 表 / 模型 | 用途 | 关键字段 | 关联关系 | 风险 / 备注 |
|---|---|---|---|---|
| `users` | 用户主表 | `id`、`username`、`email`、`password_hash`、`role`、`status`、`analysis_count`、`chat_count` | 被 analyses / comparisons / chat_sessions / favorites 引用 | 第一版正式身份模型应切换为账号密码 + user/admin 角色 |
| `analyses` | 文档分析记录 | `id`、`user_id`、`document_name`、`document_path`、`status`、`risks`、`summary` | 属于 users | `risks` 为 JSON，适合后续 PostgreSQL JSONB |
| `comparisons` | 文档对比记录 | `id`、`user_id`、`document_a`、`document_b`、`changes`、`summary`、`status` | 属于 users | 已有兼容旧 schema 的补丁逻辑 |
| `chat_sessions` | 会话主表 | `id`、`user_id`、`title`、`context` | 属于 users，被 chat_messages 引用 | 基本满足正式迁移基础 |
| `chat_messages` | 会话消息表 | `id`、`session_id`、`role`、`content` | 属于 chat_sessions | 目前无 token/成本/模型信息 |
| `favorites` | 收藏记录 | `id`、`user_id`、`item_type`、`item_id`、`title` | 属于 users | 缺少唯一索引约束的数据库级保证 |

### 非关系型与文件型存储

- 法条数据：`backend/data/civil_law.json`、`backend/data/criminal_law.json`
- 模板数据：`backend/data/templates.json`
- 向量库目录：`backend/data/vector_db`（通过配置指定）
- 上传目录：`backend/uploads/`
- 本地数据库：默认 SQLite 文件，由 `DATABASE_URL` 决定

## 7. 环境与依赖现状

### 7.1 环境变量

| 变量名 | 用途 | 必需/可选 | 敏感级别 | 备注 |
|---|---|---|---|---|
| `MIMO_API_KEY` | MiMo API 鉴权 | 必需 | 高 | 核心敏感配置 |
| `MIMO_API_URL` | MiMo 接口地址 | 可选 | 中 | 默认值已提供 |
| `MIMO_MODEL` | MiMo 模型名 | 可选 | 低 | 默认 `mimo-v2.5-pro` |
| `DATABASE_URL` | 数据库连接串 | 必需 | 高 | 当前默认 SQLite |
| `CHROMA_PERSIST_DIR` | 向量库存储目录 | 可选 | 中 | 当前为本地目录 |
| `UPLOAD_DIR` | 上传目录 | 必需 | 中 | 需区分环境 |
| `MAX_FILE_SIZE` | 上传大小限制 | 必需 | 低 | 当前 10MB |
| `APP_NAME` | 应用名 | 可选 | 低 | 展示用途 |
| `DEBUG` | 调试开关 | 必需 | 中 | 正式环境应关闭 |
| OCR 相关变量 | OCR 引擎与质量参数 | 可选/半必需 | 中 | 生产需按部署环境明确 |
| `TESSERACT_CMD` | Tesseract 路径 | 可选 | 中 | Windows 部署常用 |

### 7.2 依赖与运行环境

- 后端框架：FastAPI + Uvicorn
- ORM：SQLAlchemy Async
- 当前数据库：SQLite（默认）
- 向量检索：ChromaDB + sentence-transformers
- 文档析：PyPDF2、pdfplumber、python-docx
- OCR：PaddleOCR、PaddlePaddle、pytesseract、Pillow
- AI 能力：MiMo API
- 流式输出：sse-starlette
- 测试框架：pytest（已安装但未形成测试体系）
- 前端：原生 HTML/CSS/JavaScript 单页应用

## 8. 目录结构与职责判断

### 后端
- `backend/app/main.py`：应用入口、路由注册、静态资源挂载、健康检查
- `backend/app/api/`：业务路由层，已按搜索/文档/聊天/用户/模板拆分
- `backend/app/core/`：核心业务层，包含 OCR、法条库、向量库、文档解析、AI 分析等
- `backend/app/models/`：数据库模型 + Pydantic schema
- `backend/app/config.py`：配置集中定义
- `backend/data/`：静态业务数据
- `backend/uploads/`：运行时上传文件

### 前端
- `frontend/index.html`：单页面入口
- `frontend/css/style.css`：样式文件
- `frontend/js/app.js`：几乎承载全部前端交互逻辑，是当前最明显的大文件

### 当前结构判断

优点：
- 后端已具备基本分层，主路由边界清晰
- 业务主线集中，适合在现有架构上工程化补强

问题：
- 前端 JS 单文件过大，后续维护成本高
- 后端缺少 service / repository 更细粒度边界
- 配置仍偏单环境思路，未分 dev/test/prod
- 缺少 tests、alembic、docker、ci 等正式工程目录

## 9. 当前主要问题

- 安全：CORS 全开放；缺少速率限制；上传文件只做基础校验；缺少 MIME 白名单与隔离策略
- 鉴权：当前身份依赖 `X-User-Id` / `X-Client-Id` 请求头，本质不是正式认证体系
- 数据层：默认 SQLite；无 Alembic；存在 legacy schema 补丁逻辑，说明 schema 管理尚不正规
- AI 可靠性：依赖模型输出结构化 JSON；流式场景只做基础兜底；失败治理仍偏脆弱
- 测试：仓库虽有零散测试文件和 pytest 依赖，但未形成 `tests/` 体系，也无自动化质量门槛
- 部署：无 Dockerfile、无 docker-compose、无 GitHub Actions、无正式生产部署说明
- 观测：无统一日志、无请求链路日志、无错误监控、无业务监控
- 文档：已有 README 和 OCR 部署说明，但缺少架构、数据库、API、测试、验收全套交付文档（本周已开始补）
- 前端维护性：`frontend/js/app.js` 体积大、职责集中、状态管理和 API 调用耦合严重

## 10. 审计结论

### 10.1 当前成熟度判断

该项目已经完成了一个“业务完整、可运行、可演示”的法律 AI 原型，适合作为三个月交付计划的起点；但它还不是“正式系统”，距离企业级交付的差距主要不在业务功能数量，而在认证、安全、数据库迁移、测试、部署与文档体系。

### 10.2 最适合立即推进的事项

1. 配置治理与启动方式统一
2. 交付范围冻结
3. PostgreSQL + Alembic 迁移方案
4. 认证鉴权正式化
5. 上传安全与 API 规范化

### 10.3 暂不建议立即推进的事项

1. 全量前端框架迁移
2. 大规模架构重写
3. 扩充大量新业务功能
4. 多租户、审批流、企业后台等二期能力

### 10.4 下周建议输入

第 2 周应重点完成：
- 规范 `.env.example`
- 补配置说明与目录职责说明
- 明确 dev/test/prod 差异
- 统一后端启动方式
- 明确敏感配置管理规则
