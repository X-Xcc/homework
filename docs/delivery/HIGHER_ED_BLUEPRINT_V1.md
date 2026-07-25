# 高校交付骨架蓝图 v1

> 范围：地基三件 —— 三角色 / 班级-课程组织 / 账号密码登录
> 锁定：单课程级（≤5 课 / ≤200 人）/ 账号密码 / 学生间不隔离 / 内网 LLM 兜底后续做
> 设计原则：改动尽量收敛在"地基"层，不动材料-分析-聊天的领域逻辑

---

## 0. 改动边界（一图看清）

**保留不动的**（教学功能本体，下一阶段再叠层）：

- `document.py` / `chat.py` / `search.py` / `template.py`：路由签名不动
- `core/`（ai_analyzer、vector_store、ocr_*）：完全不动
- `frontend/src/pages/user/*` 和 `frontend/src/pages/admin/*`：现有页面暂保留，数据来源改为真实 API
- `docs/` 设计稿：不动

**只改地基层**：

- 数据库：扩 3 张表 + 1 张关联表
- 鉴权：完全替换 `client_id` 匿名机制
- 路由保护：补按角色守卫
- 前端：登录态、请求头、布局按角色切

---

## 1. 数据模型（3 张新表 + 2 张扩字段）

### 1.1 `users` 扩字段（不动旧列）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | String PK | 沿用 UUID |
| `username` | String unique | **新增** 登录账号，4–32 位，账户唯一 |
| `password_hash` | String | **新增** bcrypt 哈希，不存明文 |
| `display_name` | String | **新增** 中文名 / 昵称（替代 `nickname`，但保留旧列兼容） |
| `role` | String | **新增** `student` / `teacher` / `admin` |
| `school` | String nullable | **新增** 学校名，可空 |
| `employee_id` | String nullable | **新增** 学号 / 工号 |
| `is_active` | Boolean | **新增** 默认 `true`，软删除用 |
| `openid` | String | **保留但弃用** 不再做认证凭据，仅数据迁移兜底 |
| `nickname` / `avatar` / `phone` | 保留 | 不做新功能 |
| `created_at` / `updated_at` | 保留 | 不变 |

**不删除旧列**，避免破坏既有代码（`/api/user/login?openid=...` 这条路径保留作为兼容回退，仅在缺失 `username` 时回退，但前端不调用）。

### 1.2 `classes` 新表（班级）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | String PK | UUID |
| `name` | String | 班级名（"2024 级法学 1 班"） |
| `grade_year` | Integer | 入学年份 |
| `created_by` | String FK→users.id | 创建人（教师或管理员） |
| `created_at` | DateTime | — |

### 1.3 `courses` 新表（课程）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | String PK | UUID |
| `name` | String | 课名（"民法总论"） |
| `term` | String | 学期（"2025 秋"） |
| `teacher_id` | String FK→users.id | 任课教师 |
| `class_id` | String FK→classes.id nullable | 关联班级（可空，公开课可不挂班） |
| `description` | Text | — |
| `created_at` | DateTime | — |

### 1.4 `class_members` 新表（班级成员关系，多对多）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | String PK | UUID |
| `class_id` | String FK→classes.id | — |
| `user_id` | String FK→users.id | — |
| `joined_at` | DateTime | — |
| UNIQUE | (class_id, user_id) | — |

> 学生可同时在多个班，教师可同时教多个班，未来扩展不卡

### 1.5 `course_members` 新表（课程选课关系）

| 字段 | 类型 | 说明 |
|---|---|---|
| `id` | String PK | UUID |
| `course_id` | String FK→courses.id | — |
| `user_id` | String FK→users.id | — |
| `role_in_course` | String | `student` / `co_teacher` / `ta`（预留 TA） |
| `joined_at` | DateTime | — |
| UNIQUE | (course_id, user_id) | — |

> "不隔离"选择下，学生间可见，但加这表是**为后续选择性隔离留口子**，并且教师/管理员需要"看本课所有学生"的入口，不连 course_members 查不出来

### 1.6 关联到现有对象（**本轮不做**，但占位）

`analyses` / `comparisons` / `materials` / `chat_sessions` 本轮**不加 `course_id` 字段**——避免动到领域逻辑。
教师看学生作品的入口，通过 `course_members.user_id` JOIN 现有 user_id 表查。不强加外键，留空。

---

## 2. 鉴权替换（核心）

### 2.1 旧 → 新

| 旧 | 新 |
|---|---|
| `x-user-id` 头（明文传 user_id） | `Authorization: Bearer <jwt>` |
| `x-client-id` 头（自动建匿名用户） | 移除 |
| `/api/user/login?openid=...` | `/api/auth/login`（账号密码） |
| `/api/user/anonymous` | 移除 |
| 无密码字段 | bcrypt（passlib 或 bcrypt 原生，rounds=12） |
| 无 token | JWT（HS256，1 天过期，`AUTH_SECRET` 从 env 读） |

### 2.2 新增/改动的依赖

- `passlib[bcrypt]` 或 `bcrypt`：哈希
- `python-jose[cryptography]` 或 `pyjwt`：签发 JWT
- 二选一我倾向 **`bcrypt` + `PyJWT`**（更轻，社区主流）

### 2.3 JWT payload

```json
{
  "sub": "<user_id>",
  "username": "...",
  "role": "student|teacher|admin",
  "exp": <unix_ts>,
  "iat": <unix_ts>
}
```

`role` 写进 payload，每次请求都能拿到，不必再查 DB 才知角色。

---

## 3. API 契约（本轮新增/改动）

### 3.1 认证接口（**新**）

| 方法 | 路径 | 用途 | 状态码 |
|---|---|---|---|
| `POST` | `/api/auth/login` | 账号密码登录 | 200 / 401 |
| `POST` | `/api/auth/logout` | 客户端清 token 即可，服务端做计数 | 204 |
| `GET` | `/api/auth/me` | 当前用户信息 | 200 / 401 |
| `POST` | `/api/auth/change-password` | 改密（需登录） | 200 / 401 / 403 |

`POST /api/auth/login` 请求体：

```json
{ "username": "zhangsan", "password": "..." }
```

返回：

```json
{
  "token": "eyJ...",
  "user": {
    "id": "...",
    "username": "zhangsan",
    "display_name": "张三",
    "role": "student",
    "school": "...",
    "employee_id": "..."
  }
}
```

### 3.2 用户管理（**新**，管理员用）

| 方法 | 路径 | 角色 | 用途 |
|---|---|---|---|
| `GET` | `/api/users?role=&keyword=&page=` | admin | 列表 + 筛选 |
| `POST` | `/api/users` | admin | 管理员建账号（学生/教师） |
| `GET` | `/api/users/:id` | admin / self | 看用户详情 |
| `PATCH` | `/api/users/:id` | admin | 改名、改角色、停用 |
| `POST` | `/api/users/:id/reset-password` | admin | 重置密码 |
| `DELETE` | `/api/users/:id` | admin | 软删（`is_active=false`） |

`POST /api/users` 请求体：

```json
{
  "username": "2024001",
  "password": "Init@2026",
  "display_name": "张三",
  "role": "student",
  "school": "示范大学",
  "employee_id": "2024001"
}
```

### 3.3 班级 / 课程（**新**）

| 方法 | 路径 | 角色 | 用途 |
|---|---|---|---|
| `GET` | `/api/classes` | admin / teacher | 班级列表（教师只见自己建的） |
| `POST` | `/api/classes` | admin / teacher | 建班 |
| `POST` | `/api/classes/:id/members` | admin / teacher | 加学生进班 |
| `DELETE` | `/api/classes/:id/members/:userId` | admin / teacher | 移出 |
| `GET` | `/api/classes/:id/members` | admin / teacher | 成员列表 |
| `GET` | `/api/courses` | any | 我能看到的课（教师=我教的，学生=我选的） |
| `POST` | `/api/courses` | teacher / admin | 建课 |
| `POST` | `/api/courses/:id/enroll` | student | 学生选课 |
| `GET` | `/api/courses/:id/members` | teacher / admin | 课内成员（含作业汇总用） |

### 3.4 保留兼容（**旧路径不动**，行为微调）

| 方法 | 路径 | 改动 |
|---|---|---|
| `GET` | `/api/user/me` | 改为从 JWT 读 user，行为不变 |
| `GET` | `/api/user/history` | 不变 |
| `GET` | `/api/user/workspace` | 不变 |
| `POST` | `/api/user/favorites` | 不变 |
| `GET/DELETE` | `/api/user/favorites/...` | 不变 |
| `POST` | `/api/user/login` | 标记 **deprecated**，但保留 200（避免前端引用） |
| `POST` | `/api/user/anonymous` | 标记 **deprecated**，保留 200 |

> 文档中加 deprecation 注释，下一轮彻底删

### 3.5 鉴权依赖（`deps.py`）改动

| 旧函数 | 新函数 | 行为 |
|---|---|---|
| `get_current_user` | `get_current_user` | 从 `Authorization` 头取 JWT，解出 `sub`，查 DB |
| `get_or_create_user_by_client_id` | **删除** | — |
| `build_anonymous_openid` | **删除** | — |
| **新增** | `require_role(*roles)` | 工厂函数，生成 `Depends`，校验 `user.role` |

`require_role("admin")` 用法：

```python
@router.post(..., dependencies=[Depends(require_role("admin"))])
```

或更细粒度：自己 `current_user: UserDB = Depends(require_role("admin"))`。

---

## 4. 前端改动

### 4.1 鉴权客户端（**新文件** `src/shared/auth/`）

```
src/shared/auth/
├── AuthContext.tsx       # 登录态、user、token，存 localStorage
├── useAuth.ts            # 便捷 hook
├── apiClient.ts          # axios 或 fetch 封装，自动加 Authorization 头
├── RequireAuth.tsx       # 路由守卫：未登录跳 /login
└── RequireRole.tsx       # 角色守卫：role 不匹配跳 403 页
```

> 不引入新依赖（axios 没装），用原生 `fetch` 封一层

### 4.2 登录页（**改** `LoginPage.tsx`）

- 删掉"立即注册"链接（高校不开放自注册，由管理员建）
- 真接 `/api/auth/login`，把 token 存 `localStorage['law_token']` + user 存 `localStorage['law_user']`
- 登录成功按 `role` 跳转：
  - `student` → `/dashboard`
  - `teacher` → `/teacher/courses`（**新**）
  - `admin` → `/admin`

### 4.3 RegisterPage（**改**）

- 改成"等待开通"提示页（高校不自注册），仍可访问，但不调任何 API
- 或直接 `<Navigate to="/login" replace />`

### 4.4 `AppProvider`（**改**）

- 套 `<AuthProvider>`：启动时读 localStorage 还原登录态，调 `/api/auth/me` 验证 token 有效性
- token 失效自动清掉 + 跳 `/login`

### 4.5 路由守卫（**改** `routes.tsx`）

```tsx
<Route element={<RequireAuth><UserLayout/></RequireAuth>}>
  ... 现有 user/* 路由
</Route>
<Route path="/admin" element={<RequireAuth><RequireRole roles={['admin']}><AdminLayout/></RequireRole></RequireAuth>}>
  ... 现有 admin/*
</Route>
<Route path="/teacher" element={<RequireAuth><RequireRole roles={['teacher','admin']}>...</RequireRole></RequireAuth>}>
  ... 新增 teacher/*
</Route>
```

### 4.6 AppHeader（**改**）

- 右上"前端脚手架 v1"chip → 用户名 + 角色徽章 + 退出按钮
- 顶栏菜单按 role 显隐

### 4.7 SidebarNav（**改**）

- 教师看到：工作台 / 我的课程 / 学生管理 / 资料库
- 学生看到：工作台 / 我的课程 / 资料库
- 管理员看到：工作台 / 班级管理 / 课程管理 / 账号管理

### 4.8 教师工作台（**新** 4 个页面）

| 路径 | 页面 | 内容 |
|---|---|---|
| `/teacher/courses` | `TeacherCoursesPage` | 我的课程列表 + "新建课程" |
| `/teacher/courses/:id` | `TeacherCourseDetailPage` | 课详情 + 选课学生列表 + 进入课程资料 |
| `/teacher/classes` | `TeacherClassesPage` | 我的班级 + 批量导入学生 |
| `/teacher/classes/:id` | `TeacherClassDetailPage` | 班级成员 |

### 4.9 管理员工作台（**新** 3 个页面）

| 路径 | 页面 | 内容 |
|---|---|---|
| `/admin/users` | 已有 `AdminUsersPage` | 接真实 API（之前是 mock） |
| `/admin/classes` | **新** `AdminClassesPage` | 全校班级 + 班级合并 / 转出 |
| `/admin/courses` | **新** `AdminCoursesPage` | 全校课程 + 调课 |

> 已有的 `AdminAnalysesPage` / `AdminComparisonsPage` / `AdminChatSessionsPage` / `AdminFavoritesPage` / `AdminTemplatesPage` / `AdminAuditLogsPage` / `AdminSettingsPage`：**保持空壳**，标记 TODO，本轮不接

### 4.10 axios / fetch 统一

新装一个轻量：直接用 fetch，封 `apiClient`：

```ts
const apiClient = {
  get: (path: string) => fetch(`${BASE}${path}`, { headers: authHeaders() }).then(...),
  post: ...
}
```

`authHeaders()` 读 localStorage 里的 token。

---

## 5. 文件改动清单

### 5.1 后端

| 文件 | 动作 | 改动量 |
|---|---|---|
| `backend/requirements.txt` | 改 | +`bcrypt`, +`pyjwt` |
| `backend/app/config.py` | 改 | +`AUTH_SECRET`, +`JWT_EXPIRE_HOURS`, +`JWT_ALGORITHM` |
| `backend/.env.example` | 改 | +`AUTH_SECRET=change-me-in-prod` 等 |
| `backend/app/models/database.py` | 改 | UserDB 增 7 字段；新增 4 张表；迁移兜底 |
| `backend/app/models/__init__.py` | 改 | 导出新模型 |
| `backend/app/api/deps.py` | 改 | 完全替换 |
| `backend/app/api/auth.py` | **新** | login/logout/me/change-password |
| `backend/app/api/users.py` | **新** | admin 用户管理 |
| `backend/app/api/classes.py` | **新** | 班级 + 成员 |
| `backend/app/api/courses.py` | **新** | 课程 + 选课 |
| `backend/app/api/__init__.py` | 改 | 导出新 router |
| `backend/app/main.py` | 改 | 挂载新 router |
| `backend/app/api/user.py` | 微改 | `/login` 和 `/anonymous` 加 deprecation 注释，行为保留 |
| `backend/scripts/seed_demo.py` | **新** | 种 1 管理员 + 2 教师 + 5 学生 + 1 班 + 1 课 |
| `docs/delivery/HIGHER_ED_README.md` | **新** | 高校交付部署说明（给运维） |

### 5.2 前端

| 文件 | 动作 | 改动量 |
|---|---|---|
| `frontend/src/shared/auth/*` | **新** 5 文件 | 鉴权层 |
| `frontend/src/app/providers/AppProvider.tsx` | 改 | 套 AuthProvider |
| `frontend/src/app/router/routes.tsx` | 改 | 加守卫 + 教师路由 |
| `frontend/src/pages/user/LoginPage.tsx` | 改 | 真接 API + 角色路由 |
| `frontend/src/pages/user/RegisterPage.tsx` | 改 | 改文案为"等待开通" |
| `frontend/src/pages/user/DashboardPage.tsx` | 微改 | 顶栏带用户信息 |
| `frontend/src/shared/layouts/AppHeader.tsx` | 改 | 用户名+角色+退出 |
| `frontend/src/shared/layouts/SidebarNav.tsx` | 改 | 按角色显隐 |
| `frontend/src/pages/teacher/*` | **新** 4 文件 | 教师工作台 |
| `frontend/src/pages/admin/AdminClassesPage.tsx` | **新** | 班级管理 |
| `frontend/src/pages/admin/AdminCoursesPage.tsx` | **新** | 课程管理 |
| `frontend/src/pages/admin/AdminUsersPage.tsx` | 改 | 接真实 API |
| `frontend/src/pages/user/ForbiddenPage.tsx` | **新** | 403 页 |

---

## 6. 种子数据（管理员首登）

`scripts/seed_demo.py` 输出（幂等）：

| 角色 | username | password | display_name |
|---|---|---|---|
| admin | `admin` | `Admin@2026` | 系统管理员 |
| teacher | `teacher_li` | `Teacher@2026` | 李老师 |
| teacher | `teacher_wang` | `Teacher@2026` | 王老师 |
| student | `2024001` | `Student@2026` | 张三 |
| student | `2024002` | `Student@2026` | 李四 |
| student | `2024003` | `Student@2026` | 王五 |
| student | `2024004` | `Student@2026` | 赵六 |
| student | `2024005` | `Student@2026` | 钱七 |

外加：

- 班级 "2024 级法学 1 班"，5 学生
- 课程 "民法总论（2025 秋）"，teacher_li 任课，5 学生全选

第一次启动后，运维用 `admin` 登录，**强制改密**（`change-password` 强校验首登标志，本轮不做，但留 TODO）。

---

## 7. 验证点（怎么确认改完了）

1. **后端启得起来**：
   ```bash
   cd backend && uvicorn app.main:app --reload
   ```
   看到 `Application startup complete` 且 `/health` 返 `{"status":"ok"}`

2. **种子跑通**：
   ```bash
   python -m scripts.seed_demo
   ```
   输出"8 accounts created"

3. **登录走得通**（curl）：
   ```bash
   curl -X POST localhost:8000/api/auth/login \
     -H "Content-Type: application/json" \
     -d '{"username":"admin","password":"Admin@2026"}'
   ```
   拿到 token

4. **角色守卫工作**：
   ```bash
   # 学生 token 调 admin 接口
   curl localhost:8000/api/users -H "Authorization: Bearer <student_token>"
   # 应 403
   ```

5. **旧路径仍可用**（兼容性）：
   ```bash
   curl localhost:8000/api/user/login?openid=test
   # 仍返 200（deprecated 提示在 OpenAPI doc 中）
   ```

6. **前端 dev 起得来**：
   ```bash
   cd frontend && npm run dev
   ```
   访问 `localhost:5173/login` → 用 `2024001`/`Student@2026` 登录 → 跳 `/dashboard`
   顶部看到 "张三 / 学生" + 退出按钮

7. **教师视角**：用 `teacher_li`/`Teacher@2026` 登录 → 跳 `/teacher/courses` → 看到"民法总论" + 5 个选课学生

8. **管理员视角**：用 `admin`/`Admin@2026` 登录 → 跳 `/admin` → 用户列表 8 条，班级 1 个，课程 1 个

---

## 8. 不在本轮的事（明确划线）

- ❌ 教学材料包（教师批量上传分发）
- ❌ 作业 / 任务 / 截止时间
- ❌ 互评 / 批改
- ❌ AI 调用审计日志
- ❌ 知识库共享（班级/课程级）
- ❌ 内网 LLM 网关
- ❌ Docker 镜像 / docker-compose
- ❌ pytest 补全
- ❌ 把 `analyses` 等业务表加 `course_id`（留作下一轮）

---

## 9. 风险与缓解

| 风险 | 缓解 |
|---|---|
| bcrypt + PyJWT 装包失败 | 备选：纯 Python 实现（hashlib + hmac）功能等价 |
| 旧 `x-user-id` 头被前端某处遗漏发出 | 改造完成后此头无效（`get_current_user` 不再认），不会乱鉴权，但会导致 401，前端排查简单 |
| `users` 表加字段后老数据 `role` 为 NULL | 启动时迁移脚本兜底：`role IS NULL → 'student'`，`username IS NULL → openid`（如果有） |
| 种子脚本重复执行报 unique 冲突 | 用 `INSERT ... ON CONFLICT DO NOTHING`（SQLite 语法） |
| 教师工作台 UI 工作量大 | 教师端 4 页全部新做但不接业务数据，先把页面 + 路由 + 角色守卫做对，接口数据接 4 张表的 list / detail，**不接**课程材料/作业等业务表 |

---

## 10. 预计代码量

| 区块 | 估算 |
|---|---|
| 后端 | ~700 行新增 + ~150 行改动 |
| 前端 | ~900 行新增 + ~150 行改动 |
| 文档 | ~150 行（部署说明） |
| **合计** | **约 2000 行** |

---

## 11. 验收签字栏（你的检查点）

- [ ] 字段表没问题
- [ ] API 契约没问题
- [ ] 文件改动表没问题
- [ ] 种子数据角色配比可接受
- [ ] "不在本轮"的清单无异议

签字后我开始改代码，预计 1 小时内可跑通验证 1–8。
