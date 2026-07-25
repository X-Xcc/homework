# 法律学习 AI 工作台 — 页面组件清单 v1

> 版本：v1  
> 日期：2026-06-09  
> 作用：把 PRD、线框与对象字段继续拆到页面组件层，作为设计与开发执行桥梁

---

## 1. 文档目标

本文件用于回答以下问题：

1. 三个核心页面分别由哪些组件组成？
2. 每个组件承担什么职责？
3. 每个组件依赖哪些对象与字段？
4. 哪些组件属于 MVP 必做，哪些可以后补？

本版聚焦 3 个核心页面：

1. 工作台首页
2. 材料详情 / 阅读页
3. 案件分析工作区

---

## 2. 组件拆分原则

### 2.1 拆分层级

本文件统一按 4 层拆分：

1. 页面 `Page`
2. 页面分区 `Section`
3. 业务组件 `Component`
4. 交互单元 `Element`

### 2.2 组件命名原则

命名尽量满足三点：

- 一看就知道放在哪个页面
- 一看就知道承担什么职责
- 一看就知道和哪个对象有关

例如：

- `DashboardContinueCard`
- `MaterialHeaderMeta`
- `CaseIssueTreePanel`

### 2.3 MVP 判断原则

组件优先级分为：

- `P0`：MVP 必做
- `P1`：建议首版做
- `P2`：可后补

### 2.4 数据依赖原则

每个组件尽量只依赖“完成职责所需的最小字段集”。

---

## 3. 页面一：工作台首页组件清单

## 3.1 页面目标

帮助用户：

- 快速继续已有工作
- 快速开始新工作
- 回看最近沉淀结果

---

## 3.2 页面结构

```text
DashboardPage
├─ DashboardHeroSection
├─ DashboardContinueSection
├─ DashboardQuickStartSection
├─ DashboardRecentObjectsSection
├─ DashboardRecentCollectionsSection
└─ DashboardKnowledgePreviewSection
```

---

## 3.3 组件列表

### 3.3.1 `DashboardPage`

**层级：** Page  
**优先级：** `P0`

**职责：**

- 承载首页完整布局
- 组织各首页分区
- 处理页面级加载与空状态

**依赖对象：**

- `Case`
- `Material`
- `Analysis`
- `Knowledge`
- `Collection`

---

### 3.3.2 `DashboardHeroSection`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 显示欢迎语与工作台定位
- 提供首页主动作入口

**子组件：**

- `DashboardGreeting`
- `DashboardPrimaryActions`

**关键字段：**

- 用户名（如有）
- 最近活跃时间（可选）

---

### 3.3.3 `DashboardGreeting`

**层级：** Component  
**优先级：** `P1`

**职责：**

- 展示欢迎文案
- 提供轻量状态感

---

### 3.3.4 `DashboardPrimaryActions`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 提供 `上传材料`
- 提供 `新建案件`

**元素：**

- `UploadMaterialButton`
- `CreateCaseButton`

---

### 3.3.5 `DashboardContinueSection`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示最近可继续的案件
- 帮助用户直接回到工作现场

**子组件：**

- `DashboardContinueCardList`
- `DashboardContinueCard`

**关键字段：**

- `Case.id`
- `Case.title`
- `Case.stage`
- `Case.updated_at`
- `Case.material_count`
- `Case.analysis_count`

---

### 3.3.6 `DashboardContinueCard`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 展示单个案件继续入口
- 呈现下一步建议与状态

**元素：**

- `CaseTitle`
- `CaseStageBadge`
- `CaseUpdatedAt`
- `ContinueCaseButton`

---

### 3.3.7 `DashboardQuickStartSection`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 承接新任务开始入口

**子组件：**

- `QuickStartActionGrid`
- `QuickStartActionCard`

**建议动作：**

- 上传材料
- 从主题开始
- 新建案件
- 从法条开始

---

### 3.3.8 `DashboardRecentObjectsSection`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示最近处理过的关键对象

**子组件：**

- `RecentMaterialsPanel`
- `RecentCasesPanel`
- `RecentAnalysesPanel`

---

### 3.3.9 `RecentMaterialsPanel`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 列出最近材料

**关键字段：**

- `Material.id`
- `Material.title`
- `Material.material_type`
- `Material.updated_at`

---

### 3.3.10 `RecentCasesPanel`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 列出最近案件

**关键字段：**

- `Case.id`
- `Case.title`
- `Case.stage`
- `Case.updated_at`

---

### 3.3.11 `RecentAnalysesPanel`

**层级：** Component  
**优先级：** `P1`

**职责：**

- 列出最近分析工作件

**关键字段：**

- `Analysis.id`
- `Analysis.title`
- `Analysis.analysis_type`
- `Analysis.updated_at`

---

### 3.3.12 `DashboardRecentCollectionsSection`

**层级：** Section  
**优先级：** `P1`

**职责：**

- 展示最近沉淀的成果

**子组件：**

- `RecentCollectionList`
- `RecentCollectionCard`

**关键字段：**

- `Collection.id`
- `Collection.title`
- `Collection.collection_type`
- `Collection.updated_at`

---

### 3.3.13 `DashboardKnowledgePreviewSection`

**层级：** Section  
**优先级：** `P2`

**职责：**

- 预览知识空间活跃情况
- 强化产品“长期积累”感知

**子组件：**

- `KnowledgeHotspotsCard`
- `KnowledgeLinkPreviewCard`
- `TopicTrendCard`

---

## 3.4 首页 MVP 组件集合

首页第一版建议只做：

- `DashboardPage`
- `DashboardHeroSection`
- `DashboardPrimaryActions`
- `DashboardContinueSection`
- `DashboardQuickStartSection`
- `DashboardRecentObjectsSection`
- `RecentMaterialsPanel`
- `RecentCasesPanel`

`RecentAnalysesPanel` 与成果、知识预览可按节奏补上。

---

## 4. 页面二：材料详情 / 阅读页组件清单

## 4.1 页面目标

帮助用户：

- 阅读并理解材料
- 看见 AI 的结构化辅助
- 把材料连接到案件与知识

---

## 4.2 页面结构

```text
MaterialDetailPage
├─ MaterialHeaderSection
├─ MaterialReaderSection
├─ MaterialAnnotationSection
├─ MaterialAiSidebar
└─ MaterialRelationsSidebar
```

---

## 4.3 组件列表

### 4.3.1 `MaterialDetailPage`

**层级：** Page  
**优先级：** `P0`

**职责：**

- 承载材料详情页完整布局
- 协调头部、阅读区、AI 区与关联区

**依赖对象：**

- `Material`
- `Case`
- `Knowledge`
- `Analysis`
- `Collection`

---

### 4.3.2 `MaterialHeaderSection`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示材料身份信息
- 提供材料级操作入口

**子组件：**

- `MaterialTitleBlock`
- `MaterialMetaRow`
- `MaterialActionBar`

**关键字段：**

- `Material.title`
- `Material.material_type`
- `Material.status`
- `Material.created_at`
- `Material.case_ids`

---

### 4.3.3 `MaterialTitleBlock`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 展示材料标题与摘要

**关键字段：**

- `Material.title`
- `Material.summary`

---

### 4.3.4 `MaterialMetaRow`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 展示类型、状态、所属案件等元信息

**关键字段：**

- `Material.material_type`
- `Material.status`
- `Material.processing_status`
- `Material.case_ids`

---

### 4.3.5 `MaterialActionBar`

**层级：** Component  
**优先级：** `P1`

**职责：**

- 提供重命名、归入案件、导出摘录等动作

**元素：**

- `RenameMaterialButton`
- `AttachToCaseButton`
- `ExportExcerptButton`

---

### 4.3.6 `MaterialReaderSection`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 承载原文主阅读体验

**子组件：**

- `MaterialOutlineNav`
- `MaterialContentViewer`

---

### 4.3.7 `MaterialOutlineNav`

**层级：** Component  
**优先级：** `P1`

**职责：**

- 显示材料结构目录
- 允许跳转到指定段落

**关键字段：**

- `Material.outline`

---

### 4.3.8 `MaterialContentViewer`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 展示原文正文
- 承载选区交互

**关键字段：**

- `Material.original_text`
- `Material.excerpt_text`

---

### 4.3.9 `MaterialAnnotationSection`

**层级：** Section  
**优先级：** `P1`

**职责：**

- 承载标注、摘录、问题等辅助处理

**子组件：**

- `MaterialSelectionToolbar`
- `MaterialAnnotationList`
- `MaterialExcerptList`

---

### 4.3.10 `MaterialSelectionToolbar`

**层级：** Component  
**优先级：** `P2`

**职责：**

- 对选中文本执行高亮、提问、摘录等动作

---

### 4.3.11 `MaterialAiSidebar`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示 AI 对当前材料的结构化理解

**子组件：**

- `MaterialSummaryCard`
- `MaterialIssuesCard`
- `MaterialLegalRefsCard`
- `MaterialKnowledgeCandidatesCard`

**关键字段：**

- `Material.summary`
- `Material.detected_issue_candidates`
- `Material.detected_legal_articles`
- `Material.detected_concept_candidates`

---

### 4.3.12 `MaterialRelationsSidebar`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示材料与案件、分析、知识、成果之间的连接

**子组件：**

- `RelatedCaseCard`
- `RelatedAnalysisList`
- `RelatedKnowledgeList`
- `RelatedCollectionList`

---

## 4.4 材料页 MVP 组件集合

材料页第一版建议做：

- `MaterialDetailPage`
- `MaterialHeaderSection`
- `MaterialTitleBlock`
- `MaterialMetaRow`
- `MaterialReaderSection`
- `MaterialContentViewer`
- `MaterialAiSidebar`
- `MaterialRelationsSidebar`

标注交互与目录跳转可以在首版后增强。

---

## 5. 页面三：案件分析工作区组件清单

## 5.1 页面目标

帮助用户：

- 围绕一个问题组织分析
- 在争点结构中推进论证
- 将中间分析转化为知识与成果

---

## 5.2 页面结构

```text
CaseWorkspacePage
├─ CaseWorkspaceHeader
├─ CaseIssueTreePanel
├─ CaseAnalysisCanvas
├─ CaseEvidencePanel
└─ CaseAiActionSidebar
```

---

## 5.3 组件列表

### 5.3.1 `CaseWorkspacePage`

**层级：** Page  
**优先级：** `P0`

**职责：**

- 承载案件分析工作区整体布局
- 管理当前案件与当前分析上下文

**依赖对象：**

- `Case`
- `Analysis`
- `Material`
- `Knowledge`
- `Collection`

---

### 5.3.2 `CaseWorkspaceHeader`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 显示案件身份、阶段与主要操作

**子组件：**

- `CaseHeaderInfo`
- `CaseHeaderStats`
- `CaseHeaderActions`

**关键字段：**

- `Case.title`
- `Case.case_type`
- `Case.stage`
- `Case.material_count`
- `Case.analysis_count`
- `Case.knowledge_count`

---

### 5.3.3 `CaseIssueTreePanel`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示案件争点结构
- 作为分析的主导航骨架

**子组件：**

- `IssueTreeList`
- `IssueTreeNode`
- `CreateIssueButton`

**关键字段：**

- `Case.issue_tree`
- `Case.status`

---

### 5.3.4 `IssueTreeNode`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 展示单个争点节点
- 允许切换当前分析焦点

**元素：**

- `IssueTitle`
- `IssueStatusBadge`
- `IssueMaterialCount`
- `IssueKnowledgeCount`

---

### 5.3.5 `CaseAnalysisCanvas`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 作为案件分析的中心工作区域

**子组件：**

- `AnalysisModeTabs`
- `AnalysisEditor`
- `AnalysisConclusionBox`
- `AnalysisOpenQuestionsBox`

**关键字段：**

- `Analysis.id`
- `Analysis.analysis_type`
- `Analysis.content`
- `Analysis.structured_content`
- `Analysis.current_conclusion`
- `Analysis.open_questions`

---

### 5.3.6 `AnalysisModeTabs`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 在 `事实 / 要件 / 论证 / 对比` 等分析模式间切换

---

### 5.3.7 `AnalysisEditor`

**层级：** Component  
**优先级：** `P0`

**职责：**

- 承载当前分析正文编辑
- 支持结构化输入与内容保存

---

### 5.3.8 `CaseEvidencePanel`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 展示支持当前分析的依据对象

**子组件：**

- `ReferencedMaterialList`
- `ReferencedKnowledgeList`
- `ReferencedLegalArticleList`
- `RelatedCaseRuleList`

**关键字段：**

- `Analysis.material_ids`
- `Analysis.knowledge_ids`
- `Material.title`
- `Knowledge.title`

---

### 5.3.9 `CaseAiActionSidebar`

**层级：** Section  
**优先级：** `P0`

**职责：**

- 给出 AI 分析建议与成果生成入口

**子组件：**

- `AiSuggestionCard`
- `ArgumentGapCard`
- `GenerateKnowledgeButton`
- `GenerateCollectionButton`

**关键字段：**

- `Analysis.suggested_next_steps`
- `Analysis.human_verified`
- `Case.stage`

---

### 5.3.10 `GenerateCollectionButton`

**层级：** Component  
**优先级：** `P1`

**职责：**

- 将当前分析转为成果对象

---

## 5.4 案件工作区 MVP 组件集合

案件页第一版建议做：

- `CaseWorkspacePage`
- `CaseWorkspaceHeader`
- `CaseIssueTreePanel`
- `IssueTreeNode`
- `CaseAnalysisCanvas`
- `AnalysisModeTabs`
- `AnalysisEditor`
- `CaseEvidencePanel`
- `CaseAiActionSidebar`

成果转化和复杂争点编辑可在后续迭代增强。

---

## 6. 跨页面公共组件建议

虽然本文件聚焦页面组件，但以下组件建议尽早抽公共层。

### 6.1 布局组件

- `AppTopBar`
- `AppSidebarNav`
- `RightContextSidebar`
- `EmptyStateBlock`
- `LoadingSkeletonBlock`

### 6.2 对象展示组件

- `ObjectTitleRow`
- `ObjectMetaChips`
- `StatusBadge`
- `RelatedObjectList`
- `SourceTraceBlock`

### 6.3 AI 交互组件

- `AiSummaryCard`
- `AiSuggestionList`
- `AiActionButtonGroup`
- `AiConfidenceBadge`

### 6.4 操作组件

- `PrimaryActionButton`
- `SecondaryActionButton`
- `CreateObjectButton`
- `AttachObjectSelector`

---

## 7. 开发优先级建议

## 7.1 第一批必须开发

- 全局布局组件
- 首页 P0 组件
- 材料页 P0 组件
- 案件工作区 P0 组件

## 7.2 第二批建议开发

- 首页 P1 组件
- 材料页 P1 组件
- 案件页 P1 组件
- 公共 AI 组件抽象

## 7.3 第三批再开发

- 首页知识空间预览
- 材料高级标注交互
- 更复杂的成果生成面板
- 高级关系探索组件

---

## 8. 组件与对象依赖总结

### 8.1 首页主要依赖

- `Case`
- `Material`
- `Analysis`
- `Collection`
- `Knowledge`

### 8.2 材料页主要依赖

- `Material`
- `Case`
- `Analysis`
- `Knowledge`
- `Collection`

### 8.3 案件页主要依赖

- `Case`
- `Analysis`
- `Material`
- `Knowledge`
- `Collection`

---

## 9. 本阶段结论

### 9.1 结构结论

- 三大核心页面已经具备组件级拆分基础
- 已经可以继续细化成真实原型或前端页面树

### 9.2 MVP 结论

- 第一版应优先保证 `P0` 组件闭环
- 不要过早实现 `P2` 级视觉或图谱增强组件

### 9.3 执行结论

这一版组件清单适合直接作为：

- 原型设计拆分依据
- 前端页面开发拆分依据
- 后端接口范围对照依据

---

## 10. 下一步建议

建议按以下顺序继续：

1. 已输出 `数据库草模 v1`（见 `DATABASE_SCHEMA_DRAFT_V1.md`）
2. 已输出 `API 草案 v1`（见 `API_DRAFT_V1.md`）
3. 已输出 `前端页面树 v1`（见 `FRONTEND_PAGE_TREE_V1.md`）
4. **交互原型 v1**：开始做真实原型稿

如果顺推，我建议下一步做：

> **交互原型 v1**

因为现在产品定义已经从愿景、IA、页面、对象、PRD、组件推进到了数据结构、接口边界和工程结构，下一步最自然的就是把关键流程做成原型。