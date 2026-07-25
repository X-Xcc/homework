# 法律学习 AI 工作台 — 前端页面树 v1

> 版本：v1  
> 日期：2026-06-09  
> 作用：把页面、组件、对象与 API 草案映射到真实前端工程结构，供前端开发、脚手架初始化与任务拆分使用

---

## 1. 文档目标

本文件用于回答以下问题：

1. 前端项目建议采用什么目录结构？
2. 三个核心页面分别落在哪些路由和页面文件？
3. 页面组件、业务组件、数据请求、类型定义如何分层？
4. MVP 第一版应该先实现哪些前端模块？

---

## 2. 结构设计原则

### 2.1 先按业务域组织，再按技术角色分层

本版建议优先按业务域拆目录，而不是把所有东西按 `components / hooks / services` 散平。

原因：

- 三个核心页面都带明显业务边界
- 同一页面下的组件、hooks、types、api 耦合较高
- 后续继续扩展案件、材料、知识时更容易定位文件

### 2.2 页面层与业务层分开

建议拆成两层：

- **页面层**：负责路由、首屏装配、页面级状态
- **业务模块层**：负责组件、数据适配、交互逻辑

### 2.3 聚合接口配页面级查询 hook

以下页面聚合接口分别对应页面级查询 hook：

- `GET /api/dashboard` → `useDashboardPageData`
- `GET /api/materials/:id/detail` → `useMaterialDetailPageData`
- `GET /api/cases/:id/workspace` → `useCaseWorkspacePageData`

### 2.4 对象 CRUD 配领域 service

五类对象统一由领域 service 管理：

- `materialService`
- `caseService`
- `analysisService`
- `knowledgeService`
- `collectionService`

### 2.5 UI 组件分三类

建议分成：

1. `shared/ui`：纯展示通用组件
2. `shared/layouts`：页面外壳与通用布局
3. `features/*`：带业务语义的页面组件

---

## 3. 推荐工程目录

以下为建议的前端目录结构。

```text
src/
├─ app/
│  ├─ router/
│  │  ├─ index.tsx
│  │  └─ routes.tsx
│  ├─ providers/
│  │  ├─ QueryProvider.tsx
│  │  ├─ ThemeProvider.tsx
│  │  └─ AppProvider.tsx
│  └─ layouts/
│     ├─ AppShell.tsx
│     └─ WorkspaceShell.tsx
│
├─ pages/
│  ├─ dashboard/
│  │  └─ DashboardPage.tsx
│  ├─ materials/
│  │  └─ MaterialDetailPage.tsx
│  ├─ cases/
│  │  ├─ CaseWorkspacePage.tsx
│  │  └─ CaseListPage.tsx
│  └─ collections/
│     └─ CollectionListPage.tsx
│
├─ features/
│  ├─ dashboard/
│  │  ├─ components/
│  │  ├─ hooks/
│  │  ├─ api/
│  │  ├─ adapters/
│  │  └─ types/
│  ├─ materials/
│  │  ├─ components/
│  │  ├─ hooks/
│  │  ├─ api/
│  │  ├─ adapters/
│  │  └─ types/
│  ├─ cases/
│  │  ├─ components/
│  │  ├─ hooks/
│  │  ├─ api/
│  │  ├─ adapters/
│  │  └─ types/
│  ├─ analyses/
│  │  ├─ components/
│  │  ├─ hooks/
│  │  ├─ api/
│  │  └─ types/
│  ├─ knowledge/
│  │  ├─ components/
│  │  ├─ hooks/
│  │  ├─ api/
│  │  └─ types/
│  └─ collections/
│     ├─ components/
│     ├─ hooks/
│     ├─ api/
│     └─ types/
│
├─ shared/
│  ├─ ui/
│  ├─ layouts/
│  ├─ forms/
│  ├─ feedback/
│  ├─ icons/
│  └─ utils/
│
├─ entities/
│  ├─ material/
│  ├─ case/
│  ├─ analysis/
│  ├─ knowledge/
│  └─ collection/
│
├─ services/
│  ├─ http/
│  │  ├─ client.ts
│  │  └─ request.ts
│  ├─ query/
│  │  └─ keys.ts
│  └─ domain/
│     ├─ materialService.ts
│     ├─ caseService.ts
│     ├─ analysisService.ts
│     ├─ knowledgeService.ts
│     └─ collectionService.ts
│
├─ types/
│  ├─ api.ts
│  ├─ common.ts
│  └─ enums.ts
│
└─ mocks/
   ├─ handlers/
   └─ fixtures/
```

---

## 4. 路由树建议

## 4.1 MVP 路由树

```text
/
├─ /dashboard
├─ /materials/:materialId
├─ /cases/:caseId/workspace
├─ /cases
└─ /collections
```

### 推荐默认入口

建议首页直接落到：

- `/dashboard`

如果保留 `/`，建议做重定向：

- `/ -> /dashboard`

---

## 5. 页面到文件映射

## 5.1 工作台首页

### 路由

- `/dashboard`

### 页面文件

- `src/pages/dashboard/DashboardPage.tsx`

### 页面职责

- 装配首页所有 section
- 调用 `useDashboardPageData`
- 处理首屏 loading / empty / error

### 对应模块

- `src/features/dashboard/components/*`
- `src/features/dashboard/hooks/useDashboardPageData.ts`
- `src/features/dashboard/api/getDashboard.ts`
- `src/features/dashboard/adapters/dashboardViewModel.ts`

---

## 5.2 材料详情 / 阅读页

### 路由

- `/materials/:materialId`

### 页面文件

- `src/pages/materials/MaterialDetailPage.tsx`

### 页面职责

- 读取路由参数 `materialId`
- 调用 `useMaterialDetailPageData(materialId)`
- 组织材料正文、AI 侧栏、关系侧栏

### 对应模块

- `src/features/materials/components/*`
- `src/features/materials/hooks/useMaterialDetailPageData.ts`
- `src/features/materials/api/getMaterialDetail.ts`
- `src/features/materials/adapters/materialDetailViewModel.ts`

---

## 5.3 案件分析工作区

### 路由

- `/cases/:caseId/workspace`

### 页面文件

- `src/pages/cases/CaseWorkspacePage.tsx`

### 页面职责

- 读取 `caseId`
- 调用 `useCaseWorkspacePageData(caseId)`
- 组织头部、争点树、分析画布、证据区、AI 动作侧栏

### 对应模块

- `src/features/cases/components/*`
- `src/features/cases/hooks/useCaseWorkspacePageData.ts`
- `src/features/cases/api/getCaseWorkspace.ts`
- `src/features/cases/adapters/caseWorkspaceViewModel.ts`

---

## 6. 页面组件落位建议

## 6.1 Dashboard 模块

```text
src/features/dashboard/
├─ components/
│  ├─ DashboardHeroSection.tsx
│  ├─ DashboardGreeting.tsx
│  ├─ DashboardPrimaryActions.tsx
│  ├─ DashboardContinueSection.tsx
│  ├─ DashboardContinueCardList.tsx
│  ├─ DashboardContinueCard.tsx
│  ├─ DashboardQuickStartSection.tsx
│  ├─ DashboardRecentObjectsSection.tsx
│  ├─ DashboardRecentCollectionsSection.tsx
│  └─ DashboardKnowledgePreviewSection.tsx
├─ hooks/
│  └─ useDashboardPageData.ts
├─ api/
│  └─ getDashboard.ts
├─ adapters/
│  └─ dashboardViewModel.ts
└─ types/
   ├─ dashboard.api.ts
   └─ dashboard.vm.ts
```

---

## 6.2 Materials 模块

```text
src/features/materials/
├─ components/
│  ├─ MaterialHeaderSection.tsx
│  ├─ MaterialHeaderMeta.tsx
│  ├─ MaterialReaderSection.tsx
│  ├─ MaterialContentViewer.tsx
│  ├─ MaterialAiSidebar.tsx
│  ├─ MaterialSummaryCard.tsx
│  ├─ MaterialIssueCandidatesCard.tsx
│  ├─ MaterialKnowledgeCandidatesCard.tsx
│  ├─ MaterialRelationsSidebar.tsx
│  ├─ MaterialRelatedCasesCard.tsx
│  ├─ MaterialRelatedAnalysesCard.tsx
│  └─ MaterialRelatedKnowledgeCard.tsx
├─ hooks/
│  └─ useMaterialDetailPageData.ts
├─ api/
│  ├─ getMaterialDetail.ts
│  ├─ updateMaterial.ts
│  └─ processMaterial.ts
├─ adapters/
│  └─ materialDetailViewModel.ts
└─ types/
   ├─ material.api.ts
   └─ material.vm.ts
```

---

## 6.3 Cases 模块

```text
src/features/cases/
├─ components/
│  ├─ CaseWorkspaceHeader.tsx
│  ├─ CaseMetaBar.tsx
│  ├─ CaseIssueTreePanel.tsx
│  ├─ CaseIssueTreeNode.tsx
│  ├─ CaseAnalysisCanvas.tsx
│  ├─ CaseAnalysisEditor.tsx
│  ├─ CaseEvidencePanel.tsx
│  ├─ CaseEvidenceMaterialList.tsx
│  ├─ CaseKnowledgeReferenceList.tsx
│  ├─ CaseAiActionSidebar.tsx
│  ├─ CaseSuggestedNextSteps.tsx
│  └─ CaseGenerationActions.tsx
├─ hooks/
│  └─ useCaseWorkspacePageData.ts
├─ api/
│  ├─ getCaseWorkspace.ts
│  ├─ updateCase.ts
│  └─ attachCaseMaterial.ts
├─ adapters/
│  └─ caseWorkspaceViewModel.ts
└─ types/
   ├─ case.api.ts
   └─ case.vm.ts
```

---

## 6.4 Analyses 模块

```text
src/features/analyses/
├─ components/
│  ├─ AnalysisEditorToolbar.tsx
│  ├─ AnalysisStatusBadge.tsx
│  ├─ AnalysisSourceList.tsx
│  └─ AnalysisKnowledgeLinkList.tsx
├─ hooks/
│  ├─ useCreateAnalysis.ts
│  ├─ useUpdateAnalysis.ts
│  └─ useGenerateCollection.ts
├─ api/
│  ├─ createAnalysis.ts
│  ├─ updateAnalysis.ts
│  ├─ linkAnalysisMaterial.ts
│  └─ generateAnalysisCollection.ts
└─ types/
   └─ analysis.api.ts
```

---

## 6.5 Knowledge / Collections 模块

第一版它们可以先作为“被引用对象模块”存在，不必一开始就做完整独立页面。

### `knowledge`

```text
src/features/knowledge/
├─ components/
│  ├─ KnowledgeReferenceCard.tsx
│  └─ KnowledgeCandidateList.tsx
├─ hooks/
│  └─ useLinkMaterialKnowledge.ts
└─ api/
   └─ createKnowledgeNode.ts
```

### `collections`

```text
src/features/collections/
├─ components/
│  ├─ CollectionPreviewCard.tsx
│  └─ CollectionSourceTraceCard.tsx
├─ hooks/
│  └─ useExportCollection.ts
└─ api/
   └─ exportCollection.ts
```

---

## 7. 数据层分工建议

## 7.1 `api/` 文件职责

每个 `api/` 文件只做一件事：

- 发请求
- 返回原始 API Response

例如：

- `getDashboard.ts`
- `getMaterialDetail.ts`
- `getCaseWorkspace.ts`

## 7.2 `adapters/` 文件职责

负责把后端响应结构转换为页面更好用的 ViewModel。

例如：

- 把 `continue_cases` 转成 `ContinueCardVM[]`
- 把 `related_cases / related_analyses / related_knowledge` 整理成 sidebar sections
- 把 `issue_tree + current_analysis + ai_sidebar` 整理成 workspace model

## 7.3 `hooks/` 文件职责

负责：

- 触发请求
- 管理 loading / error / refetch
- 暴露页面组件真正需要的数据

例如：

- `useDashboardPageData`
- `useMaterialDetailPageData`
- `useCaseWorkspacePageData`

## 7.4 `entities/` 文件职责

保存领域对象的基础类型与纯函数，不直接关心页面结构。

例如：

- `Material`
- `Case`
- `Analysis`
- `KnowledgeNode`
- `Collection`

---

## 8. 类型文件建议

## 8.1 全局类型

- `src/types/api.ts`：统一 API envelope
- `src/types/common.ts`：分页、排序、ID、时间等通用类型
- `src/types/enums.ts`：状态与枚举值

## 8.2 领域类型

建议每个实体单独一组基础类型：

- `src/entities/material/types.ts`
- `src/entities/case/types.ts`
- `src/entities/analysis/types.ts`
- `src/entities/knowledge/types.ts`
- `src/entities/collection/types.ts`

## 8.3 页面 ViewModel 类型

放在各 feature 的 `types/*.vm.ts` 里。

原因：

- ViewModel 属于页面层，不应污染基础实体类型
- 同一对象在不同页面可能需要不同变形

---

## 9. 共享组件建议

## 9.1 `shared/ui`

建议放纯展示、低业务耦合组件：

- `Button`
- `Card`
- `Tabs`
- `Badge`
- `EmptyState`
- `Skeleton`
- `Panel`
- `Drawer`

## 9.2 `shared/layouts`

建议放页面布局骨架：

- `AppHeader`
- `SidebarNav`
- `PageContainer`
- `WorkspaceSplitLayout`

## 9.3 `shared/forms`

建议放通用输入组件：

- `SearchInput`
- `TagInput`
- `RichTextEditor`（若抽象足够通用）

---

## 10. 状态管理建议

## 10.1 服务端状态

建议使用查询层统一管理服务端状态。

适合放在查询缓存中的数据：

- `dashboard`
- `materialDetail`
- `caseWorkspace`
- `caseList`
- `collectionList`

## 10.2 本地 UI 状态

建议页面本地管理：

- 当前展开的 sidebar tab
- 当前选中的 issue node
- 编辑器草稿状态
- drawer / modal 开关

## 10.3 暂不建议全局大状态仓库

MVP 第一版先不要把全部状态塞进统一 store。

原因：

- 页面边界清晰
- 服务端数据占主导
- 过早引入全局 store 会增加维护成本

---

## 11. Mock 与联调策略

## 11.1 Mock 目录

建议：

```text
src/mocks/
├─ handlers/
│  ├─ dashboard.ts
│  ├─ materials.ts
│  ├─ cases.ts
│  ├─ analyses.ts
│  └─ collections.ts
└─ fixtures/
   ├─ dashboard.fixture.ts
   ├─ material-detail.fixture.ts
   └─ case-workspace.fixture.ts
```

## 11.2 建议先 Mock 的三个接口

- `GET /api/dashboard`
- `GET /api/materials/:id/detail`
- `GET /api/cases/:id/workspace`

因为这三个接口决定了三大核心页面能否先搭出来。

---

## 12. MVP 第一版开发顺序

## 12.1 第一步：基础壳层

先搭：

- `AppShell`
- 路由系统
- 查询层 Provider
- 通用 `Card / Button / Skeleton / EmptyState`

## 12.2 第二步：三大页面骨架

先出：

- `DashboardPage`
- `MaterialDetailPage`
- `CaseWorkspacePage`

即使先用假数据，也先把结构站起来。

## 12.3 第三步：页面聚合 hook + Mock

实现：

- `useDashboardPageData`
- `useMaterialDetailPageData`
- `useCaseWorkspacePageData`

## 12.4 第四步：分析编辑与关系绑定

实现：

- 创建分析
- 更新分析
- 绑定分析材料
- 绑定案件材料

---

## 13. 模块优先级建议

## 13.1 P0 必做

- `app/router`
- `pages/dashboard`
- `pages/materials/MaterialDetailPage`
- `pages/cases/CaseWorkspacePage`
- `features/dashboard`
- `features/materials`
- `features/cases`
- `features/analyses`（最小子集）
- `shared/ui`
- `services/http`
- `services/query`
- `mocks`

## 13.2 P1 建议首版做

- `pages/cases/CaseListPage`
- `pages/collections/CollectionListPage`
- `features/knowledge`
- `features/collections`
- `shared/forms`

## 13.3 P2 后补

- 全局搜索
- 知识复习队列
- 导出中心
- 批量操作页

---

## 14. 本阶段结论

### 14.1 结构结论

- 页面、组件、接口、数据层已经能映射到真实工程目录
- 三个核心页面都有明确的文件落点和依赖模块
- 前端代码可以按 feature 直接开工

### 14.2 MVP 结论

- 第一版只要把首页、材料详情、案件工作区搭起来，就能形成可演示产品骨架
- 知识与成果模块可以先以被引用视角接入，不必一开始就做全页

### 14.3 执行结论

这份页面树已经足够支撑：

- 前端仓库初始化
- 页面与组件任务拆分
- Mock 数据开发
- 路由与查询层搭建

---

## 15. 下一步建议

建议按以下顺序继续：

1. **交互原型 v1**：把三大页面关键路径做成真实原型
2. **OpenAPI / 接口清单 v1**：把 API 草案转成正式契约
3. **SQL / ORM 初稿 v1**：把数据库草模转成 schema
4. **前端脚手架初始化建议 v1**：给出实际项目起步文件清单

如果继续顺推，我建议下一步做：

> **交互原型 v1**

因为现在信息架构、页面线框、组件、数据模型、接口边界、工程结构都已经齐了，下一步最适合把关键交互路径做成可演示原型。