# 法律学习 AI 工作台 — 前端脚手架初始化建议 v1

> 版本：v1  
> 日期：2026-06-10  
> 作用：基于前端页面树与交互原型，为 MVP 前端项目提供可直接开工的脚手架初始化方案，覆盖技术栈、目录、依赖、基础文件、Provider、Mock、请求层与首批页面骨架

---

## 1. 文档目标

本文件用于回答以下问题：

1. 前端 MVP 适合采用什么技术栈？
2. 项目初始化时第一批应该创建哪些目录与文件？
3. 路由、Provider、请求层、Mock、状态缓存应如何起步？
4. 三个核心页面的最小可运行骨架应如何落地？
5. 第一阶段前端开发任务如何拆分？

---

## 2. 初始化目标

脚手架第一阶段不追求“全功能”，而追求三件事：

1. **能启动**：本地开发环境一键运行
2. **能扩展**：目录与分层足够支撑后续业务增长
3. **能演示**：三大核心页面可先用 Mock 数据跑通

---

## 3. 技术栈建议

## 3.1 核心框架

建议：

- `React`
- `TypeScript`
- `Vite`

### 原因

- 启动快，适合 MVP
- TypeScript 能承接后续对象模型与 API 契约
- Vite 对页面骨架、Mock 联调和组件迭代足够轻量

---

## 3.2 路由层

建议：

- `react-router-dom`

### 用途

- 路由定义
- 嵌套路由
- 页面级 layout
- 动态参数页

---

## 3.3 服务端状态层

建议：

- `@tanstack/react-query`

### 用途

- 页面聚合查询
- 异步请求缓存
- loading / error / refetch 管理
- mutation 成功后局部失效刷新

---

## 3.4 HTTP 层

建议：

- 原生 `fetch` + 自封装请求客户端

### 原因

- MVP 阶段不必先引入更重封装
- 后续若需要统一拦截器、取消请求、上传进度，再向上扩展

---

## 3.5 UI 基础层

建议：

- `Tailwind CSS`
- `clsx`
- `tailwind-merge`

### 原因

- 适合快速搭页面骨架
- 能高效实现布局、状态和响应式
- 与 feature 分层不会冲突

---

## 3.6 表单层

建议：

- `react-hook-form`
- `zod`

### 用途

- 新建案件弹层
- 上传材料表单
- 关系绑定确认表单
- 简化的表单校验与类型联动

---

## 3.7 Mock 层

建议：

- `msw`

### 用途

- 在前端开发期模拟 `dashboard`、`materialDetail`、`caseWorkspace`
- 在 API 未完成前先跑通页面与交互
- 后续便于切换为真实接口

---

## 3.8 编辑器与增强能力

MVP 第一阶段建议：

- 分析编辑器先用 `textarea` 或轻量编辑容器起步

P1 再考虑：

- 富文本编辑器
- 引用块
- 段落锚点
- AI 建议插入块

### 原因

- 先把分析流跑通，比过早投入重编辑器更重要

---

## 4. 推荐依赖清单

## 4.1 运行时依赖

建议首批安装：

```text
react
react-dom
react-router-dom
@tanstack/react-query
clsx
tailwind-merge
react-hook-form
zod
```

## 4.2 开发依赖

建议首批安装：

```text
typescript
vite
@vitejs/plugin-react
tailwindcss
postcss
autoprefixer
msw
eslint
@typescript-eslint/eslint-plugin
@typescript-eslint/parser
prettier
```

### 可选开发依赖

```text
eslint-config-prettier
eslint-plugin-react-hooks
eslint-plugin-react-refresh
```

---

## 5. 初始化目录建议

建议初始化后，至少先建立以下目录：

```text
frontend/
├─ public/
├─ src/
│  ├─ app/
│  │  ├─ layouts/
│  │  ├─ providers/
│  │  ├─ router/
│  │  └─ styles/
│  ├─ pages/
│  │  ├─ dashboard/
│  │  ├─ materials/
│  │  └─ cases/
│  ├─ features/
│  │  ├─ dashboard/
│  │  ├─ materials/
│  │  ├─ cases/
│  │  ├─ analyses/
│  │  ├─ knowledge/
│  │  └─ collections/
│  ├─ shared/
│  │  ├─ ui/
│  │  ├─ layouts/
│  │  ├─ forms/
│  │  ├─ feedback/
│  │  └─ utils/
│  ├─ entities/
│  │  ├─ material/
│  │  ├─ case/
│  │  ├─ analysis/
│  │  ├─ knowledge/
│  │  └─ collection/
│  ├─ services/
│  │  ├─ http/
│  │  ├─ query/
│  │  └─ domain/
│  ├─ types/
│  ├─ mocks/
│  │  ├─ fixtures/
│  │  └─ handlers/
│  └─ main.tsx
├─ index.html
├─ package.json
├─ tsconfig.json
├─ vite.config.ts
├─ tailwind.config.ts
├─ postcss.config.js
└─ .eslintrc.cjs
```

---

## 6. 首批必须创建的文件

## 6.1 工程入口

```text
src/main.tsx
src/App.tsx
src/app/router/index.tsx
src/app/router/routes.tsx
src/app/providers/AppProvider.tsx
src/app/providers/QueryProvider.tsx
src/app/styles/index.css
```

### 职责

- `main.tsx`：挂载根节点
- `App.tsx`：承接全局 Provider 与 Router
- `router/*`：管理路由树
- `providers/*`：集中装配 Query、Theme、Mock 初始化等
- `styles/index.css`：全局样式入口

---

## 6.2 布局骨架

```text
src/app/layouts/AppShell.tsx
src/app/layouts/WorkspaceShell.tsx
src/shared/layouts/AppHeader.tsx
src/shared/layouts/SidebarNav.tsx
src/shared/layouts/PageContainer.tsx
```

### 职责

- `AppShell`：全局主框架
- `WorkspaceShell`：适合材料页 / 工作区这种多栏布局页面
- `AppHeader`：顶栏
- `SidebarNav`：左侧主导航
- `PageContainer`：统一内容宽度与内边距

---

## 6.3 通用 UI 基础组件

```text
src/shared/ui/Button.tsx
src/shared/ui/Card.tsx
src/shared/ui/Badge.tsx
src/shared/ui/Panel.tsx
src/shared/ui/EmptyState.tsx
src/shared/ui/Skeleton.tsx
src/shared/ui/Input.tsx
src/shared/ui/Textarea.tsx
src/shared/ui/Modal.tsx
src/shared/ui/Drawer.tsx
```

### 原则

- 先做最小能力版本
- 不过度抽象
- 统一 className 拼接方式
- 支持 disabled / loading / error 等常见状态

---

## 6.4 请求与缓存层

```text
src/services/http/client.ts
src/services/http/request.ts
src/services/query/keys.ts
src/types/api.ts
src/types/common.ts
src/types/enums.ts
```

### 建议职责

#### `client.ts`

- 暴露基础请求函数
- 处理 base URL
- 处理 JSON 解析
- 处理统一错误结构

#### `request.ts`

- 封装 GET / POST / PATCH 等轻量方法

#### `keys.ts`

- 管理查询 key
- 避免 key 分散硬编码

---

## 6.5 Mock 文件

```text
src/mocks/browser.ts
src/mocks/handlers/index.ts
src/mocks/handlers/dashboard.ts
src/mocks/handlers/materials.ts
src/mocks/handlers/cases.ts
src/mocks/fixtures/dashboard.fixture.ts
src/mocks/fixtures/material-detail.fixture.ts
src/mocks/fixtures/case-workspace.fixture.ts
```

### 初始化目标

先用 3 个聚合接口完成页面联调：

- `GET /api/dashboard`
- `GET /api/materials/:id/detail`
- `GET /api/cases/:id/workspace`

---

## 7. 首批页面骨架建议

## 7.1 页面文件

第一批建议先创建：

```text
src/pages/dashboard/DashboardPage.tsx
src/pages/materials/MaterialDetailPage.tsx
src/pages/cases/CaseWorkspacePage.tsx
```

### 目标

先让这 3 个页面能：

- 正常路由进入
- 正常显示 layout
- 正常显示 mock 数据
- 正常展示 loading / empty / error 骨架

---

## 7.2 对应 feature 起步文件

### Dashboard

```text
src/features/dashboard/components/DashboardHeroSection.tsx
src/features/dashboard/components/DashboardContinueSection.tsx
src/features/dashboard/components/DashboardRecentObjectsSection.tsx
src/features/dashboard/hooks/useDashboardPageData.ts
src/features/dashboard/api/getDashboard.ts
src/features/dashboard/adapters/dashboardViewModel.ts
```

### Materials

```text
src/features/materials/components/MaterialHeaderSection.tsx
src/features/materials/components/MaterialReaderSection.tsx
src/features/materials/components/MaterialAiSidebar.tsx
src/features/materials/components/MaterialRelationsSidebar.tsx
src/features/materials/hooks/useMaterialDetailPageData.ts
src/features/materials/api/getMaterialDetail.ts
src/features/materials/adapters/materialDetailViewModel.ts
```

### Cases

```text
src/features/cases/components/CaseWorkspaceHeader.tsx
src/features/cases/components/CaseIssueTreePanel.tsx
src/features/cases/components/CaseAnalysisCanvas.tsx
src/features/cases/components/CaseEvidencePanel.tsx
src/features/cases/components/CaseAiActionSidebar.tsx
src/features/cases/hooks/useCaseWorkspacePageData.ts
src/features/cases/api/getCaseWorkspace.ts
src/features/cases/adapters/caseWorkspaceViewModel.ts
```

---

## 8. 路由初始化建议

## 8.1 MVP 路由树

```text
/
├─ /dashboard
├─ /materials/:materialId
└─ /cases/:caseId/workspace
```

### 建议规则

- `/` 直接重定向到 `/dashboard`
- 三个核心页统一挂在 `AppShell` 下
- 材料页与案件工作区可在页面内再切换 `WorkspaceShell`

---

## 8.2 路由分层建议

### `routes.tsx`

负责：

- 声明路径
- 绑定页面组件
- 包装 layout

### `router/index.tsx`

负责：

- 导出 router 实例
- 与 Provider 集成

---

## 9. Provider 初始化建议

## 9.1 `AppProvider`

建议装配顺序：

1. Query Provider
2. Router Provider
3. 可选 Theme Provider
4. 可选 Mock 启动逻辑

### 原则

- Provider 不承载业务逻辑
- 仅做全局上下文装配

---

## 9.2 Query 默认策略

MVP 建议：

- 不要把缓存策略配得太激进
- 先偏保守，保证联调行为清晰

### 建议默认方向

- 页面查询允许缓存
- mutation 成功后按 key 精准失效
- 出错时允许显式重试

---

## 10. 请求层初始化建议

## 10.1 页面聚合查询优先

第一阶段不要先把所有对象 CRUD 都铺开，先实现页面聚合查询：

- `getDashboard`
- `getMaterialDetail`
- `getCaseWorkspace`

### 原因

- 这三个接口决定 MVP 页面是否能先跑起来
- 页面比完整 CRUD 更优先

---

## 10.2 ViewModel 适配优先

建议每个页面查询都先经过 adapter。

### 原因

- 后端结构可能更偏领域对象
- 前端页面更需要 ViewModel
- 避免页面组件直接耦合后端原始结构

---

## 11. 表单与弹层初始化建议

## 11.1 MVP 第一批弹层

建议先做：

- `UploadMaterialModal`
- `CreateCaseModal`
- `AttachCaseModal`
- `AttachAnalysisDrawer`

### 原则

- 每个弹层仅处理单一任务
- 校验规则明确
- 提交成功后立刻反馈

---

## 11.2 第一批表单规则

### 上传材料

- 文件必选
- 标题可自动带出并允许编辑

### 新建案件

- 标题必填
- 类型与阶段可选

### 绑定案件 / 分析

- 选择目标对象必填

---

## 12. 页面状态骨架初始化建议

## 12.1 页面级状态组件

建议尽早准备：

```text
src/shared/feedback/PageSkeleton.tsx
src/shared/feedback/PageErrorState.tsx
src/shared/feedback/InlineError.tsx
src/shared/feedback/SectionEmptyState.tsx
```

### 原因

交互原型已经明确了大量状态切换，如果没有统一反馈组件，后续页面很快会散乱。

---

## 12.2 三页最小状态支持

### DashboardPage

- `initial-loading`
- `empty`
- `ready`
- `error`

### MaterialDetailPage

- `initial-loading`
- `processing-source`
- `ready`
- `error`

### CaseWorkspacePage

- `initial-loading`
- `empty-analysis`
- `ready`
- `save-error`
- `error`

---

## 13. 样式系统初始化建议

## 13.1 第一阶段只做基础设计令牌

建议先定义：

- 颜色语义
- 间距尺度
- 圆角尺度
- 阴影层级
- 字号层级

### 不建议第一阶段做的事

- 过于复杂的主题切换
- 过早做深色模式全覆盖
- 过度抽象设计 token 系统

---

## 13.2 页面布局优先级

优先保证：

- 顶栏稳定
- 左导航稳定
- 中间主区宽度合理
- 右侧栏可折叠
- 长文阅读区稳定滚动

---

## 14. 环境变量建议

建议先定义：

```text
VITE_API_BASE_URL=
VITE_ENABLE_MOCK=true
```

### 用途

- `VITE_API_BASE_URL`：真实后端地址
- `VITE_ENABLE_MOCK`：开发期切换 mock

---

## 15. 开发命令建议

初始化后应保证以下命令清晰可用：

```text
npm install
npm run dev
npm run build
npm run lint
```

如果后续加测试，再补：

```text
npm run test
```

---

## 16. 首阶段开发顺序建议

## 16.1 第一步：搭工程底座

先完成：

- Vite + React + TypeScript
- Tailwind
- Router
- Query Provider
- AppShell
- 基础 UI 组件

## 16.2 第二步：接入 Mock

先完成：

- `msw`
- 三个聚合接口 fixture
- 页面能读到 mock 数据

## 16.3 第三步：搭三大页面骨架

先完成：

- `DashboardPage`
- `MaterialDetailPage`
- `CaseWorkspacePage`

只要骨架、状态、主要区块先出来即可。

## 16.4 第四步：补关键交互

先补：

- 上传材料弹层
- 新建案件弹层
- 材料页 AI 动作按钮
- 工作区分析编辑与保存状态

---

## 17. 前端任务拆分建议

## 17.1 任务包 A：工程初始化

- 初始化 Vite 项目
- 接入 TypeScript
- 配置 Tailwind
- 配置 ESLint / Prettier

## 17.2 任务包 B：AppShell 与路由

- 顶栏
- 左导航
- 页面容器
- 三个核心路由

## 17.3 任务包 C：请求层与 Mock

- request client
- query keys
- msw handlers
- fixtures

## 17.4 任务包 D：三个页面骨架

- Dashboard
- Material Detail
- Case Workspace

## 17.5 任务包 E：关键交互

- Upload Material
- Create Case
- Attach Case
- Analysis Save

---

## 18. 第一版完成标准

当前脚手架阶段完成后，应该达到：

1. 本地可以启动前端
2. 三大页面能独立进入
3. 页面可以显示 mock 数据
4. 至少支持基础 loading / empty / error 状态
5. 至少有两个弹层和一个编辑区流程可演示

---

## 19. 本阶段结论

### 19.1 工程结论

- 前端已经具备从产品文档进入真实工程初始化的条件
- 技术栈、依赖、目录、核心文件、Provider、Mock、页面骨架都已明确

### 19.2 执行结论

这份文档已经足够支撑：

- 初始化 `frontend` 项目
- 拆分前端开发任务
- 先用 mock 联调页面
- 再逐步切换真实 API

---

## 20. 下一步建议

建议按以下顺序继续：

1. 已输出 `页面状态矩阵 v1`（见 `PAGE_STATE_MATRIX_V1.md`）
2. **OpenAPI / 接口清单 v1**：把接口草案转成更正式契约
3. **SQL / ORM 初稿 v1**：把数据库草模转成实际 schema
4. **frontend 项目初始化执行**：直接开始创建项目目录与基础文件

如果继续顺推，我建议下一步做：

> **frontend 项目初始化执行**

因为交互原型已经定义了状态，页面状态矩阵也已经把实现与测试视角对齐了，现在最适合直接开始搭真实前端工程。