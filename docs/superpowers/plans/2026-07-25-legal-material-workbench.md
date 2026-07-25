# 法律材料工作台实施计划

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** 将现有法律 AI 原型推进为供内部小组持续使用的法律材料工作台，兼顾法律学习、材料理解和合同处理，保证核心功能真实、数据可追溯、流程可恢复。

**Architecture:** 保持 FastAPI + SQLite/SQLAlchemy 的单体架构和 React/TypeScript 前端。以“材料”为统一业务中心，分析、对话、法条检索、笔记和导出都围绕材料建立关联；当前阶段不引入微服务、消息队列或第二套前端。

**Tech Stack:** Python 3.11、FastAPI、SQLAlchemy、Alembic、SQLite、ChromaDB/TF-IDF、外部 OpenAI-compatible AI API、React 19、TypeScript、Vite、TanStack Query、Vitest、pytest。

---

## 版本目标与范围

### 本版本必须支持

- 用户注册、登录和退出；用户只能访问自己的材料、分析、对话、收藏和历史。
- 上传合同、法规、判决书或学习资料，并完成文本解析、持久化和历史查看。
- 对材料执行 AI 摘要、风险识别、法律依据关联和修改建议生成。
- 在当前材料上下文中进行多轮追问，并保存会话。
- 搜索本地法条数据，查看法条详情，并将法条加入收藏或笔记。
- 对分析结果进行人工复核标记，并导出可读的分析报告。
- 管理员查看用户、分析记录和基础使用统计。

### 本版本明确不做

- 多租户、复杂 RBAC、企业审批流和组织架构。
- 移动端、小程序和独立桌面端。
- 全国法规超大规模扩库和自动实时更新法规。
- 多模型编排、私有大模型训练和异步任务平台。
- 完整知识图谱；只保留材料、法条、风险和笔记之间的基础关联。

## 文件地图

- 后端入口和配置：`backend/app/main.py`、`backend/app/config.py`
- 后端数据模型与数据库：`backend/app/models/database.py`、`backend/app/models/schemas.py`
- 文档接口与文件流程：`backend/app/api/document.py`、`backend/app/core/document_service.py`
- AI 分析与流式输出：`backend/app/core/ai_analyzer.py`、`backend/app/api/chat.py`
- 法条与向量检索：`backend/app/api/search.py`、`backend/app/core/legal_db.py`、`backend/app/core/vector_store.py`
- 用户与权限：`backend/app/api/user.py`、`backend/app/api/deps.py`、`backend/app/core/security.py`
- 前端路由和布局：`frontend/src/app/router/routes.tsx`、`frontend/src/app/layouts/`、`frontend/src/shared/layouts/`
- 前端业务页面：`frontend/src/pages/user/`、`frontend/src/pages/admin/`
- 前端 API 和状态：`frontend/src/shared/api/`、`frontend/src/app/providers/`
- 后端测试：`backend/tests/`
- 前端测试：`frontend/src/**/__tests__/`

---

## Task 1: 建立产品与数据基线

**Files:**
- Create: `docs/product/product-positioning-v1.md`
- Create: `docs/product/core-user-flows-v1.md`
- Modify: `README.md`
- Modify: `PRODUCT_BRIEF.md`
- Modify: `docs/audit/project-current-state.md`
- Modify: `docs/audit/delivery-scope-freeze.md`

- [ ] **Step 1: 写明统一产品定位**
  明确产品是“法律材料工作台”，统一描述材料中心、理解模式、处理模式、对话模式和沉淀模式；删除或改写“纯法律顾问”和“纯学习平台”的冲突表述。

- [ ] **Step 2: 固定两条核心用户流程**
  在 `docs/product/core-user-flows-v1.md` 写明：
  1. 学习流程：上传资料 → 摘要/概念理解 → 法条检索 → 提问 → 笔记/收藏。
  2. 实务流程：上传合同 → 风险分析 → 法律依据 → 修改建议 → 复核 → 导出报告。

- [ ] **Step 3: 对齐运行说明**
  将所有 AI 配置统一为 `AI_API_KEY`、`AI_API_URL`、`AI_MODEL`，并以实际代码和 `backend/.env.example` 为准修订 README。

- [ ] **Step 4: 建立现状基线**
  更新当前状态文档，区分“已实现”“部分实现”“计划实现”，明确当前测试基线为后端 pytest、前端 Vitest、前端 build。

- [ ] **Step 5: 检查文档一致性**
  Run: `rg -n "MIMO_API_KEY|AI_API_KEY|法律顾问|学习工作台" README.md PRODUCT_BRIEF.md docs`
  Expected: 配置名称统一，产品定位不再出现互相冲突的主称谓。

## Task 2: 收口材料上传与数据访问

**Files:**
- Modify: `backend/app/api/document.py`
- Modify: `backend/app/core/document_service.py`
- Modify: `backend/app/models/database.py`
- Modify: `backend/app/models/schemas.py`
- Modify: `backend/app/api/user.py`
- Test: `backend/tests/test_document.py`
- Test: `backend/tests/test_user_workspace.py`
- Test: `backend/tests/test_document_security.py`

- [ ] **Step 1: 先写上传安全测试**
  覆盖允许的文件类型、拒绝的扩展名、超出 `MAX_FILE_SIZE`、空文件名、路径穿越文件名和用户读取他人分析记录等场景。

- [ ] **Step 2: 实现上传校验顺序**
  在写入 `uploads` 前校验文件大小、扩展名和 MIME；使用 UUID 生成存储文件名，只把原始文件名作为展示字段；失败时不留下临时文件。

- [ ] **Step 3: 收敛材料记录字段**
  为分析和对比记录补齐原始文件名、存储路径、文件类型、文件大小、处理状态、失败原因和所属用户字段，保留现有 API 响应兼容性。

- [ ] **Step 4: 强化对象级权限**
  所有分析、对比、会话、收藏和历史查询都必须通过当前用户过滤；不存在或不属于当前用户时统一返回 404，避免泄露对象存在性。

- [ ] **Step 5: 运行后端定向测试**
  Run: `..\.venv\Scripts\python.exe -m pytest tests/test_document.py tests/test_user_workspace.py tests/test_document_security.py -q`
  Expected: 所有上传、权限和历史相关测试通过。

## Task 3: 打造可解释的分析结果

**Files:**
- Modify: `backend/app/core/ai_analyzer.py`
- Modify: `backend/app/core/risk.py`
- Modify: `backend/app/api/document.py`
- Modify: `backend/app/models/schemas.py`
- Modify: `frontend/src/pages/user/ContractAnalyzePage.tsx`
- Modify: `frontend/src/pages/user/AnalysisDetailPage.tsx`
- Create: `frontend/src/shared/ui/RiskCard.tsx`
- Create: `frontend/src/shared/ui/SourceReference.tsx`
- Test: `backend/tests/test_document.py`
- Test: `frontend/src/pages/user/__tests__/AnalysisDetailPage.test.tsx`

- [ ] **Step 1: 固定分析结果结构**
  每个风险至少包含风险等级、标题、说明、原文位置、法律依据、建议和复核状态；摘要、评分和风险列表使用明确的 schema 校验。

- [ ] **Step 2: 增加 AI 输出容错**
  对空响应、非法 JSON、缺字段、超时和供应商错误返回统一的可识别错误；保留原始错误日志，不把密钥或完整敏感材料写入日志。

- [ ] **Step 3: 增加前端状态展示**
  分析页必须区分上传中、解析中、AI 分析中、成功、失败和可重试状态；风险卡展示法律依据和原文位置，而不是只展示评分。

- [ ] **Step 4: 增加复核状态**
  支持风险项标记为“待复核”“确认”“不准确”，保存操作者和更新时间，并在详情页显示。

- [ ] **Step 5: 验证失败路径**
  Run: `..\.venv\Scripts\python.exe -m pytest tests/test_document.py tests/test_ai_analyzer_stream.py -q`
  Run: `npm test -- --run`
  Expected: 正常结果和 AI 异常结果都能稳定呈现。

## Task 4: 建立材料上下文对话与学习沉淀

**Files:**
- Modify: `backend/app/api/chat.py`
- Modify: `backend/app/api/user.py`
- Modify: `backend/app/models/database.py`
- Modify: `frontend/src/pages/user/ChatAssistantPage.tsx`
- Modify: `frontend/src/pages/user/FavoritesPage.tsx`
- Modify: `frontend/src/pages/user/HistoryPage.tsx`
- Create: `frontend/src/pages/user/NotesPage.tsx`
- Modify: `frontend/src/app/router/routes.tsx`
- Test: `backend/tests/test_chat.py`
- Test: `backend/tests/test_user_workspace.py`
- Test: `frontend/src/pages/user/__tests__/ChatAssistantPage.test.tsx`

- [ ] **Step 1: 设计材料上下文关联**
  会话记录保存关联材料、分析记录或法条 ID；进入聊天页时优先使用当前材料上下文，明确展示上下文来源。

- [ ] **Step 2: 限制对话输入和成本**
  对消息长度、单用户频率和会话历史长度设置限制；超限时返回可理解的提示，不直接让上游 API 失败。

- [ ] **Step 3: 增加笔记模型和接口**
  新增最小笔记字段：用户、标题、内容、来源材料、来源法条、标签、创建时间和更新时间；提供创建、编辑、列表和删除接口。

- [ ] **Step 4: 接入学习沉淀页面**
  支持从分析风险、法条详情和聊天消息保存笔记；历史页区分分析、对比、会话和笔记。

- [ ] **Step 5: 验证闭环**
  Run: `..\.venv\Scripts\python.exe -m pytest tests/test_chat.py tests/test_user_workspace.py -q`
  Expected: 会话可恢复，笔记可保存并只对所属用户可见。

## Task 5: 完善法条检索与依据关联

**Files:**
- Modify: `backend/app/api/search.py`
- Modify: `backend/app/core/legal_db.py`
- Modify: `backend/app/core/vector_store.py`
- Modify: `frontend/src/pages/user/LawSearchPage.tsx`
- Modify: `frontend/src/pages/user/AnalysisDetailPage.tsx`
- Test: `backend/tests/test_search_templates.py`
- Create: `backend/tests/test_search_quality.py`

- [ ] **Step 1: 固定搜索响应字段**
  搜索结果统一返回法源、法规名称、条款编号、正文、更新时间或数据版本和匹配原因；无结果时返回空列表而非异常。

- [ ] **Step 2: 增加检索质量样例**
  为常见合同和学习问题准备固定查询及期望命中的法条 ID，测试关键词搜索、分类过滤、相似检索和详情查询。

- [ ] **Step 3: 将分析依据链接到法条**
  风险项的法律依据可以点击进入法条详情；找不到可靠依据时明确显示“需要人工复核”，禁止伪造条款号。

- [ ] **Step 4: 运行检索测试**
  Run: `..\.venv\Scripts\python.exe -m pytest tests/test_search_templates.py tests/test_search_quality.py -q`
  Expected: 固定查询的命中结果稳定，法条详情可从分析页打开。

## Task 6: 稳定导出、管理员和运行环境

**Files:**
- Modify: `backend/app/api/export_utils.py`
- Modify: `backend/app/api/admin.py`
- Modify: `backend/app/main.py`
- Modify: `backend/app/config.py`
- Modify: `backend/alembic/versions/3dd5a89652cc_initial.py`
- Modify: `docker-compose.yml`
- Modify: `Dockerfile`
- Modify: `README.md`
- Test: `backend/tests/test_admin.py`
- Create: `backend/tests/test_export.py`
- Create: `.github/workflows/quality.yml`

- [ ] **Step 1: 让 Alembic 成为正式迁移入口**
  将当前模型创建结果生成可执行 baseline，明确新环境初始化、升级和回滚命令；`init_db` 不再静默承担全部结构变更。

- [ ] **Step 2: 验证导出格式**
  测试 TXT、DOCX、PDF 的状态、文件名、内容摘要、风险列表和法律依据；导出失败返回统一错误响应。

- [ ] **Step 3: 收敛管理员能力**
  保留用户管理、分析记录、对话记录和统计；补齐最后一个管理员保护、停用用户行为和敏感字段脱敏展示。

- [ ] **Step 4: 修正生产配置保护**
  非调试环境拒绝默认 JWT 密钥和默认管理员密码；健康检查区分数据库、AI、OCR 和向量库状态，避免所有组件失败时只返回模糊错误。

- [ ] **Step 5: 建立 CI 质量门槛**
  GitHub Actions 至少运行后端 pytest、前端 Vitest、前端 build；后端 Ruff 先以新增代码无错误为阶段目标，再逐步清理历史问题。

- [ ] **Step 6: 验证部署路径**
  Run: `docker compose config`
  Run: `docker compose build`
  Run: `docker compose up -d`
  Expected: 新环境能启动应用、初始化数据库、访问 `/health`，并能通过 README 完成配置。

## Task 7: 建立内部小组反馈与验收机制

**Files:**
- Create: `docs/operations/internal-user-guide.md`
- Create: `docs/operations/feedback-rubric.md`
- Create: `docs/operations/demo-dataset.md`
- Modify: `docs/testing/test-report.md`
- Modify: `README.md`

- [ ] **Step 1: 编写内部使用指南**
  说明材料上传、分析、追问、法条检索、笔记、复核和导出流程，并明确 AI 结果不能替代人工判断。

- [ ] **Step 2: 固定反馈维度**
  每条 AI 结果按“事实提取准确性、风险判断合理性、法律依据相关性、建议可执行性”四项反馈，使用统一等级和备注格式。

- [ ] **Step 3: 准备脱敏样本集**
  准备合同、法条和学习资料样本，记录预期解析结果、关键风险、法律依据和人工判断；禁止把真实敏感材料提交到仓库。

- [ ] **Step 4: 完成端到端验收**
  使用新用户执行注册、上传、分析、对话、收藏、笔记、历史、导出；使用管理员验证统计和权限边界；将结果记录到测试报告。

---

## 完成定义

当以下条件全部满足时，版本可交给内部小组试用：

- 新环境可以按 README 启动，数据库结构可迁移，健康检查状态明确。
- 核心材料流程可以真实完成，分析结果、会话、笔记和导出可恢复。
- 用户数据隔离测试通过，上传文件不会因文件名或类型造成路径风险。
- 后端 pytest 全部通过，前端 Vitest 和 production build 全部通过。
- AI 异常、OCR 不可用、无搜索结果和导出失败均有可理解的恢复路径。
- 至少一组脱敏样本经过人工复核，并记录 AI 结果质量反馈。

## 推荐执行顺序

1. Task 1：产品与数据基线。
2. Task 2：上传、权限和数据访问。
3. Task 3：可解释分析结果。
4. Task 6：迁移、导出、配置和 CI 基础。
5. Task 4：上下文对话和学习沉淀。
6. Task 5：法条质量和依据关联。
7. Task 7：内部试用、反馈和验收。

执行过程中每完成一个 Task，先运行该 Task 的定向测试，再运行完整检查：

```powershell
Set-Location D:\homework\backend
..\.venv\Scripts\python.exe -m pytest
Set-Location D:\homework\frontend
npm test -- --run
npm run build
```
