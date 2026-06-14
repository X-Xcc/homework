# 前台 / 后台分离重构实现文档

> 目标：把现有 React 前端拆分为**前台（用户工作区）** 和 **后台（管理端）** 两个独立区域，复用公共布局和组件，后端适配新的 Vite 构建产物路径。

## 一、现状分析

### 1.1 前端现状

- 技术栈：React 19 + Vite 7 + React Router 7 + TanStack Query + Tailwind CSS
- 已搭建骨架：`AppShell`（Header + Sidebar + Outlet），`AppHeader`，`SidebarNav`
- 路由引用了 3 个页面：`DashboardPage`、`MaterialDetailPage`、`CaseWorkspacePage`，但**文件均不存在**
- 路由方式：React Router 7 新版 `createBrowserRouter` + `route()` 数组配置（分散在 `routes.tsx`）

### 1.2 后端现状

- FastAPI，路由注册在 `backend/app/main.py`
- 静态文件挂载指向旧路径：
  ```python
  app.mount("/css", StaticFiles(directory=str(FRONTEND_DIR / "css")), name="css")
  app.mount("/js", StaticFiles(directory=str(FRONTEND_DIR / "js")), name="js")
  ```
- 旧前端 `frontend/css/` 和 `frontend/js/` 是旧的原生 HTML 时代资源

### 1.3 待解决问题

| # | 问题 | 影响 |
|---|------|------|
| 1 | 3 个页面文件缺失 | 路由无法渲染，页面 404 |
| 2 | 前台/后台未分区 | 用户和管理员共用水银 Navigation |
| 3 | 后端静态路径指向旧目录 | 新 Vite 构建产物无法被后端服务 |
| 4 | 后端 index.html 路径指向旧目录 | 所有页面访问都会 404 |

## 二、目标结构

### 2.1 前端目录

```
frontend/src/
├─ app/
│  ├─ router/
│  │  ├─ index.tsx          ← 导出 router（不改）
│  │  └─ routes.tsx         ← 重写为前后台分离路由
│  ├─ layouts/
│  │  ├─ AppShell.tsx        ← 保留，改名参考 UserLayout
│  │  ├─ WorkspaceShell.tsx
│  │  ├─ UserLayout.tsx     ← 新增：前台用户布局
│  │  ├─ AdminLayout.tsx    ← 新增：后台管理布局
│  │  └─ AuthLayout.tsx     ← 新增：登录注册布局
│  └─ providers/
│     ├─ AppProvider.tsx
│     └─ QueryProvider.tsx
├─ pages/
│  ├─ user/                 ← 前台用户页面
│  │  ├─ LoginPage.tsx
│  │  ├─ RegisterPage.tsx
│  │  ├─ DashboardPage.tsx   ← 修复：从 pages/dashboard/ 迁移
│  │  ├─ MaterialDetailPage.tsx ← 修复
│  │  ├─ CaseWorkspacePage.tsx  ← 修复
│  │  ├─ ContractAnalyzePage.tsx ← 新增
│  │  ├─ ContractComparePage.tsx ← 新增
│  │  ├─ LawSearchPage.tsx      ← 新增
│  │  ├─ ChatAssistantPage.tsx   ← 新增
│  │  ├─ HistoryPage.tsx         ← 新增
│  │  ├─ FavoritesPage.tsx       ← 新增
│  │  └─ ProfilePage.tsx        ← 新增
│  └─ admin/                ← 后台管理页面
│     ├─ AdminDashboardPage.tsx
│     ├─ AdminUsersPage.tsx
│     ├─ AdminAnalysesPage.tsx
│     ├─ AdminComparisonsPage.tsx
│     ├─ AdminChatSessionsPage.tsx
│     ├─ AdminFavoritesPage.tsx
│     ├─ AdminTemplatesPage.tsx
│     ├─ AdminAuditLogsPage.tsx
│     └─ AdminSettingsPage.tsx
├─ features/
│  ├─ auth/
│  │  ├─ api.ts
│  │  ├─ types.ts
│  │  └─ components/
│  │     └─ ProtectedRoute.tsx
│  ├─ contract/
│  │  └─ api.ts
│  ├─ chat/
│  │  └─ api.ts
│  ├─ law-search/
│  │  └─ api.ts
│  └─ admin/
│     └─ api.ts
├─ shared/
│  ├─ ui/
│  ├─ layouts/
│  └─ utils/
└─ main.tsx
```

### 2.2 路由设计

```
/                        → 重定向到 /dashboard
/login                   → 登录页（AuthLayout）
/register               → 注册页（AuthLayout）

# 前台用户区（UserLayout）
/dashboard              → 工作台首页
/materials/:id         → 材料详情
/cases/:id/workspace   → 案件工作区
/contracts/analyze     → 合同分析
/contracts/compare     → 合同对比
/search                → 法条检索
/chat                  → 智能问答
/history               → 历史记录
/favorites             → 我的收藏
/profile               → 个人中心

# 后台管理区（AdminLayout）
/admin                  → 管理仪表板
/admin/users            → 用户管理
/admin/analyses         → 分析记录
/admin/comparisons      → 对比记录
/admin/chat-sessions    → 聊天会话
/admin/favorites        → 收藏管理
/admin/templates        → 模板管理
/admin/audit-logs       → 操作日志
/admin/settings         → 系统设置
```

### 2.3 后端改造

- Vite 构建产物在 `frontend/dist/`
- 后端静态路径改为 `FRONTEND_DIST_DIR = frontend/dist`，挂载 `/`
- 注册 `AdminLayout` 专属 API 前缀：`/api/v1/admin/*`

## 三、实施步骤

### Step 1：创建实现文档（本步骤）

本文件即为实现文档，作为后续执行的依据。

### Step 2：修复缺失页面文件

创建 3 个被路由引用但不存在的页面文件，恢复路由可用：

- `pages/dashboard/DashboardPage.tsx`
- `pages/materials/MaterialDetailPage.tsx`
- `pages/cases/CaseWorkspacePage.tsx`

### Step 3：新增前台布局 `UserLayout`

- 基于现有 `AppShell` 重构，移除 `SidebarNav` 中的硬编码导航
- 动态渲染前台导航菜单（工作台、分析、对比、检索、问答、历史、收藏）

### Step 4：新增后台布局 `AdminLayout`

- 独立后台 Header（包含管理员标识、退出）
- 独立后台 Sidebar（用户、分析、对比、会话、模板、日志、设置）
- 独立内容 Outlet 区域

### Step 5：新增登录注册布局 `AuthLayout`

- 纯居中卡片式登录/注册页
- 无 Header、无 Sidebar

### Step 6：新增前台页面

按优先级依次实现：
1. `LoginPage` / `RegisterPage`（基础 Auth）
2. `ContractAnalyzePage` / `ContractComparePage`（核心业务）
3. `LawSearchPage` / `ChatAssistantPage`（AI 能力）
4. `HistoryPage` / `FavoritesPage` / `ProfilePage`（用户资产）

### Step 7：新增后台页面

全部新建：
1. `AdminDashboardPage`（数据汇总卡片）
2. `AdminUsersPage`（用户表格 + 状态切换）
3. `AdminAnalysesPage` / `AdminComparisonsPage`（记录查看）
4. `AdminTemplatesPage` / `AdminSettingsPage`

### Step 8：重写路由 `routes.tsx`

用 React Router 7 声明式路由（`route()` 对象）重组所有路由，按布局分组：
- 公共路由组（AuthLayout）
- 前台路由组（UserLayout）
- 后台路由组（AdminLayout）

### Step 9：创建 Auth Feature

- `ProtectedRoute` 组件：未登录 → 跳转 `/login`
- `AdminRoute` 组件：非管理员 → 跳转 `/dashboard`
- `useAuth` Hook：`useCurrentUser`、`useLogin`、`useLogout`

### Step 10：调整后端静态路径

```python
# 改为指向 Vite 构建产物
FRONTEND_DIST_DIR = Path(__file__).resolve().parent.parent.parent / "frontend" / "dist"
app.mount("/", StaticFiles(directory=str(FRONTEND_DIST_DIR), html=True), name="static")
```

### Step 11：更新 AppHeader

- 前台显示 Logo + 导航标签
- 后台显示 Logo + 管理员角色标识
- 右上角：用户头像 + 退出按钮

### Step 12：验证

- 确认 `npm run dev` 前台可访问
- 确认 `npm run build && uvicorn main:app` 后端可访问所有页面
- 确认前后台路由切换正常
- 确认 TypeScript 编译无错误

## 四、文件清单

### 新增文件（按优先级）

| 文件 | 说明 |
|------|------|
| `pages/user/LoginPage.tsx` | 登录页 |
| `pages/user/RegisterPage.tsx` | 注册页 |
| `pages/user/ContractAnalyzePage.tsx` | 合同分析页 |
| `pages/user/ContractComparePage.tsx` | 合同对比页 |
| `pages/user/LawSearchPage.tsx` | 法条检索页 |
| `pages/user/ChatAssistantPage.tsx` | 智能问答页 |
| `pages/user/HistoryPage.tsx` | 历史记录页 |
| `pages/user/FavoritesPage.tsx` | 收藏页 |
| `pages/user/ProfilePage.tsx` | 个人中心页 |
| `app/layouts/UserLayout.tsx` | 前台布局 |
| `app/layouts/AdminLayout.tsx` | 后台布局 |
| `app/layouts/AuthLayout.tsx` | 认证布局 |
| `pages/admin/AdminDashboardPage.tsx` | 管理仪表板 |
| `pages/admin/AdminUsersPage.tsx` | 用户管理 |
| `pages/admin/AdminAnalysesPage.tsx` | 分析记录 |
| `pages/admin/AdminComparisonsPage.tsx` | 对比记录 |
| `pages/admin/AdminChatSessionsPage.tsx` | 会话管理 |
| `pages/admin/AdminFavoritesPage.tsx` | 收藏管理 |
| `pages/admin/AdminTemplatesPage.tsx` | 模板管理 |
| `pages/admin/AdminAuditLogsPage.tsx` | 操作日志 |
| `pages/admin/AdminSettingsPage.tsx` | 系统设置 |
| `features/auth/api.ts` | Auth API |
| `features/auth/types.ts` | Auth 类型 |
| `features/auth/components/ProtectedRoute.tsx` | 路由守卫 |
| `features/auth/hooks.ts` | Auth Hooks |

### 修复文件

| 文件 | 变更 |
|------|------|
| `pages/dashboard/DashboardPage.tsx` | 新建，迁移现有 Mock 内容 |
| `pages/materials/MaterialDetailPage.tsx` | 新建，恢复路由引用 |
| `pages/cases/CaseWorkspacePage.tsx` | 新建，恢复路由引用 |
| `app/router/routes.tsx` | 重写，支持三 Layout 分组 |
| `shared/layouts/SidebarNav.tsx` | 拆分前台导航 + 后台导航 |
| `shared/layouts/AppHeader.tsx` | 增强：支持 Admin 模式 |
| `backend/app/main.py` | 静态路径改为 `frontend/dist` |

### 依赖改造

| 文件 | 变更 |
|------|------|
| `frontend/package.json` | 确认依赖完整 |
| `backend/app/main.py` | 修改静态路径 |
| `backend/app/config.py` | 新增 `FRONTEND_DIST_DIR` 配置 |

## 五、成功标准

1. 所有页面路由可正常访问（`/dashboard`、`/admin`、`/admin/users` 等）
2. 前台 `UserLayout` 和后台 `AdminLayout` 视觉风格不同
3. 未登录访问前台页面 → 跳转 `/login`
4. 后端 `uvicorn app.main:app` 后可直接访问前端（静态服务）
5. TypeScript 编译零错误
6. ESLint 零错误（允许部分 `console.log` 和 TODO 注释）
