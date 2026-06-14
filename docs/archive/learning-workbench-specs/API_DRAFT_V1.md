# 法律学习 AI 工作台 — API 草案 v1

> 版本：v1  
> 日期：2026-06-09  
> 作用：把页面、组件与数据结构收束为接口边界，供前后端协同、Mock 数据、ORM 服务层与联调使用

---

## 1. 文档目标

本文件用于回答以下问题：

1. 三大核心页面各需要哪些页面聚合接口？
2. 五个核心对象分别需要哪些基础 CRUD 接口？
3. 多对多关系通过哪些接口管理？
4. 哪些接口属于 MVP 必做，哪些可后补？

---

## 2. API 设计原则

### 2.1 先服务页面，再服务对象

本版 API 采用两层思路：

1. **页面聚合接口**：给页面首屏或工作区直接供数
2. **对象接口**：负责标准读写、列表、状态变更、关系管理

### 2.2 REST 为主，聚合接口允许偏 ViewModel

对象接口尽量保持 REST 风格。

但以下页面接口允许返回聚合后的 ViewModel：

- 工作台首页
- 材料详情页
- 案件分析工作区

### 2.3 v1 统一单用户上下文

第一版默认所有接口都运行在当前登录用户上下文内：

- 不在路径上体现 `workspace_id`
- 不做团队权限模型
- 服务端基于当前用户过滤 `owner_id`

### 2.4 返回格式尽量统一

建议统一返回：

```json
{
  "success": true,
  "data": {},
  "meta": {},
  "error": null
}
```

列表接口建议统一支持：

- `page`
- `page_size`
- `sort_by`
- `sort_order`

### 2.5 状态变更与复杂动作单独设 action 接口

以下类型不强行塞进普通 `PATCH`：

- 归档
- 完成
- 生成知识
- 生成成果
- 绑定关系
- 触发 AI 处理

---

## 3. 接口分层总览

## 3.1 页面聚合接口

1. `GET /api/dashboard`
2. `GET /api/materials/:id/detail`
3. `GET /api/cases/:id/workspace`

## 3.2 核心对象接口

4. `materials`
5. `cases`
6. `knowledge-nodes`
7. `analyses`
8. `collections`

## 3.3 关系与动作接口

9. `case-materials`
10. `analysis-materials`
11. `analysis-knowledge-links`
12. `material-knowledge-links`
13. `collection-sources`
14. AI / 生成动作接口

---

## 4. 页面聚合接口

## 4.1 `GET /api/dashboard`

### 用途

给工作台首页一次性返回首屏所需主要数据。

### 优先级

`P0`

### 覆盖组件

- `DashboardHeroSection`
- `DashboardContinueSection`
- `DashboardQuickStartSection`
- `DashboardRecentObjectsSection`
- `DashboardRecentCollectionsSection`（可选）

### 请求参数

无必填。

可选：

- `include=collections,knowledge_preview`

### 返回建议

```json
{
  "success": true,
  "data": {
    "greeting": {
      "display_name": "张三",
      "last_active_at": "2026-06-09T16:00:00Z"
    },
    "continue_cases": [],
    "quick_actions": [],
    "recent_materials": [],
    "recent_cases": [],
    "recent_analyses": [],
    "recent_collections": []
  },
  "meta": {},
  "error": null
}
```

---

## 4.2 `GET /api/materials/:id/detail`

### 用途

给材料详情 / 阅读页返回完整页面数据。

### 优先级

`P0`

### 覆盖组件

- `MaterialHeaderSection`
- `MaterialReaderSection`
- `MaterialAiSidebar`
- `MaterialRelationsSidebar`

### 返回建议

```json
{
  "success": true,
  "data": {
    "material": {},
    "related_cases": [],
    "related_analyses": [],
    "related_knowledge": [],
    "related_collections": [],
    "ai_insights": {
      "summary": "",
      "issue_candidates": [],
      "legal_article_refs": [],
      "knowledge_candidates": []
    }
  },
  "meta": {},
  "error": null
}
```

---

## 4.3 `GET /api/cases/:id/workspace`

### 用途

给案件分析工作区返回完整工作上下文。

### 优先级

`P0`

### 覆盖组件

- `CaseWorkspaceHeader`
- `CaseIssueTreePanel`
- `CaseAnalysisCanvas`
- `CaseEvidencePanel`
- `CaseAiActionSidebar`

### 请求参数

可选：

- `analysis_id`
- `focused_issue_id`

### 返回建议

```json
{
  "success": true,
  "data": {
    "case": {},
    "issue_tree": [],
    "current_analysis": {},
    "case_analyses": [],
    "referenced_materials": [],
    "referenced_knowledge": [],
    "ai_sidebar": {
      "suggested_next_steps": [],
      "argument_gaps": [],
      "generation_actions": []
    }
  },
  "meta": {},
  "error": null
}
```

---

## 5. `materials` 对象接口

## 5.1 `GET /api/materials`

### 用途

获取材料列表。

### 优先级

`P0`

### 支持筛选

- `keyword`
- `material_type`
- `status`
- `case_id`
- `updated_after`

---

## 5.2 `POST /api/materials`

### 用途

新建材料记录。

### 优先级

`P0`

### 请求体建议

```json
{
  "title": "合同法案例一",
  "material_type": "case_text",
  "original_text": "...",
  "source_url": "",
  "case_ids": []
}
```

---

## 5.3 `GET /api/materials/:id`

### 用途

读取单个材料基础对象。

### 优先级

`P0`

---

## 5.4 `PATCH /api/materials/:id`

### 用途

更新材料基础字段。

### 可更新字段

- `title`
- `summary`
- `topic_tags`
- `status`

---

## 5.5 `POST /api/materials/:id/process`

### 用途

触发材料 AI 解析。

### 优先级

`P1`

### 动作内容

- 提取摘要
- 提取争点候选
- 提取法条候选
- 提取知识候选

---

## 5.6 `POST /api/materials/:id/archive`

### 用途

归档材料。

### 优先级

`P1`

---

## 6. `cases` 对象接口

## 6.1 `GET /api/cases`

### 用途

获取案件列表。

### 优先级

`P0`

### 支持筛选

- `keyword`
- `case_type`
- `stage`
- `status`

---

## 6.2 `POST /api/cases`

### 用途

新建案件。

### 优先级

`P0`

### 请求体建议

```json
{
  "title": "不当得利争议分析",
  "case_type": "study_case",
  "main_question": "是否构成不当得利？",
  "learning_goal": "理解构成要件与抗辩"
}
```

---

## 6.3 `GET /api/cases/:id`

### 用途

读取单个案件基础对象。

### 优先级

`P0`

---

## 6.4 `PATCH /api/cases/:id`

### 用途

更新案件基础信息。

### 可更新字段

- `title`
- `summary`
- `description`
- `main_question`
- `stage`
- `status`
- `issue_tree`

---

## 6.5 `POST /api/cases/:id/complete`

### 用途

标记案件完成。

### 优先级

`P1`

---

## 6.6 `POST /api/cases/:id/archive`

### 用途

归档案件。

### 优先级

`P1`

---

## 7. `knowledge-nodes` 对象接口

## 7.1 `GET /api/knowledge-nodes`

### 用途

获取知识节点列表。

### 优先级

`P1`

### 支持筛选

- `keyword`
- `knowledge_type`
- `review_status`
- `topic_tag`

---

## 7.2 `POST /api/knowledge-nodes`

### 用途

手动创建知识节点。

### 优先级

`P1`

---

## 7.3 `GET /api/knowledge-nodes/:id`

### 用途

读取单个知识节点。

### 优先级

`P1`

---

## 7.4 `PATCH /api/knowledge-nodes/:id`

### 用途

更新知识节点。

### 可更新字段

- `title`
- `summary`
- `definition`
- `core_rule`
- `applicable_conditions`
- `exceptions`
- `topic_tags`
- `review_status`

---

## 7.5 `POST /api/knowledge-nodes/:id/review`

### 用途

记录一次复核或确认。

### 优先级

`P2`

---

## 8. `analyses` 对象接口

## 8.1 `GET /api/analyses`

### 用途

获取分析对象列表。

### 优先级

`P1`

### 支持筛选

- `case_id`
- `analysis_type`
- `status`
- `focused_issue_id`

---

## 8.2 `POST /api/analyses`

### 用途

新建分析对象。

### 优先级

`P0`

### 请求体建议

```json
{
  "case_id": "uuid",
  "title": "争点一：是否构成不当得利",
  "analysis_type": "issue_analysis",
  "focused_issue_id": "issue_1"
}
```

---

## 8.3 `GET /api/analyses/:id`

### 用途

读取单个分析对象。

### 优先级

`P0`

---

## 8.4 `PATCH /api/analyses/:id`

### 用途

更新分析对象。

### 可更新字段

- `title`
- `summary`
- `content`
- `structured_content`
- `current_conclusion`
- `open_questions`
- `status`

---

## 8.5 `POST /api/analyses/:id/generate-knowledge`

### 用途

根据当前分析生成知识节点候选。

### 优先级

`P1`

---

## 8.6 `POST /api/analyses/:id/generate-collection`

### 用途

根据当前分析生成成果对象。

### 优先级

`P1`

---

## 9. `collections` 对象接口

## 9.1 `GET /api/collections`

### 用途

获取成果列表。

### 优先级

`P1`

### 支持筛选

- `keyword`
- `collection_type`
- `status`
- `is_pinned`

---

## 9.2 `POST /api/collections`

### 用途

手动创建成果对象。

### 优先级

`P1`

---

## 9.3 `GET /api/collections/:id`

### 用途

读取单个成果对象。

### 优先级

`P1`

---

## 9.4 `PATCH /api/collections/:id`

### 用途

更新成果对象。

### 可更新字段

- `title`
- `summary`
- `content`
- `topic_tags`
- `is_pinned`
- `status`

---

## 9.5 `POST /api/collections/:id/export`

### 用途

导出成果对象。

### 优先级

`P2`

### 请求体建议

```json
{
  "format": "markdown"
}
```

---

## 10. 关系接口

## 10.1 `POST /api/cases/:id/materials`

### 用途

把材料加入案件。

### 优先级

`P0`

### 请求体建议

```json
{
  "material_id": "uuid",
  "relation_role": "primary_source"
}
```

---

## 10.2 `DELETE /api/cases/:id/materials/:materialId`

### 用途

把材料从案件移除。

### 优先级

`P1`

---

## 10.3 `POST /api/analyses/:id/materials`

### 用途

给分析对象绑定引用材料。

### 优先级

`P0`

### 请求体建议

```json
{
  "material_id": "uuid",
  "usage_type": "evidence"
}
```

---

## 10.4 `DELETE /api/analyses/:id/materials/:materialId`

### 用途

移除分析引用材料。

### 优先级

`P1`

---

## 10.5 `POST /api/materials/:id/knowledge-links`

### 用途

创建材料与知识节点的关联。

### 优先级

`P1`

### 请求体建议

```json
{
  "knowledge_id": "uuid",
  "link_type": "supports_definition",
  "source_excerpt": "..."
}
```

---

## 10.6 `POST /api/analyses/:id/knowledge-links`

### 用途

创建分析与知识节点的关联。

### 优先级

`P1`

---

## 10.7 `POST /api/collections/:id/sources`

### 用途

给成果对象增加来源对象。

### 优先级

`P1`

### 请求体建议

```json
{
  "source_type": "analysis",
  "source_id": "uuid",
  "source_role": "primary_basis"
}
```

---

## 11. AI 与生成动作接口

## 11.1 `POST /api/materials/:id/process`

### 说明

材料级 AI 处理动作，建议异步。

### 返回建议

```json
{
  "success": true,
  "data": {
    "job_id": "uuid",
    "processing_status": "queued"
  },
  "meta": {},
  "error": null
}
```

---

## 11.2 `POST /api/analyses/:id/generate-knowledge`

### 说明

从分析中生成知识候选，可先返回候选列表，再由用户确认落库。

---

## 11.3 `POST /api/analyses/:id/generate-collection`

### 说明

从分析生成成果候选。

建议返回：

- 候选标题
- 候选摘要
- 候选正文
- 来源追踪

---

## 12. MVP 必做接口集合

## 12.1 页面接口

- `GET /api/dashboard`
- `GET /api/materials/:id/detail`
- `GET /api/cases/:id/workspace`

## 12.2 对象接口

- `GET /api/materials`
- `POST /api/materials`
- `GET /api/materials/:id`
- `PATCH /api/materials/:id`
- `GET /api/cases`
- `POST /api/cases`
- `GET /api/cases/:id`
- `PATCH /api/cases/:id`
- `POST /api/analyses`
- `GET /api/analyses/:id`
- `PATCH /api/analyses/:id`

## 12.3 关系接口

- `POST /api/cases/:id/materials`
- `POST /api/analyses/:id/materials`

### 结论

只靠这批接口，就已经能支撑：

- 首页继续工作
- 上传材料并查看详情
- 新建案件并绑定材料
- 在案件下创建分析并推进工作

---

## 13. 错误码建议

建议第一版统一业务错误码前缀：

- `MATERIAL_NOT_FOUND`
- `CASE_NOT_FOUND`
- `ANALYSIS_NOT_FOUND`
- `KNOWLEDGE_NOT_FOUND`
- `COLLECTION_NOT_FOUND`
- `INVALID_STATUS_TRANSITION`
- `RELATION_ALREADY_EXISTS`
- `VALIDATION_ERROR`
- `FORBIDDEN`

---

## 14. 版本与演进建议

### 14.1 v1 不必急着公开 API version

如果当前只是内部开发与原型期，可暂时使用：

- `/api/...`

等接口稳定后再切换为：

- `/api/v1/...`

### 14.2 后续可能补充的接口

- 批量导入材料
- 搜索建议接口
- 标注 / 摘录接口
- 审核 / 复核接口
- 导出异步任务接口
- 知识复习队列接口

---

## 15. 本阶段结论

### 15.1 结构结论

- 页面层已经有首屏聚合接口
- 对象层已经有基础 CRUD 边界
- 关系层已经有最小闭环接口

### 15.2 MVP 结论

- 第一版无需把所有对象都做全量接口
- 只要把 `materials + cases + analyses + 页面聚合接口` 做扎实，就能跑通主路径

### 15.3 执行结论

这一版 API 草案已经足够支撑：

- 前端 Mock 数据
- 后端 Controller / Service 拆分
- OpenAPI 初稿
- 前后端联调范围确认

---

## 16. 下一步建议

建议按以下顺序继续：

1. 已输出 `前端页面树 v1`（见 `FRONTEND_PAGE_TREE_V1.md`）
2. 已输出 `交互原型 v1`（见 `INTERACTION_PROTOTYPE_V1.md`）
3. **OpenAPI / 接口清单 v1**：把三大页面关键接口整理成更正式契约
4. **SQL / ORM 初稿 v1**：把数据库草模转成具体 schema

如果继续顺推，我建议下一步做：

> **前端脚手架初始化建议 v1**

因为现在产品定义已经推进到接口边界、前端工程结构和交互原型，最自然的下一步就是把它们映射成实际项目起步方案。