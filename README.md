# 法律 AI - 智能法律顾问系统

> 阶段二·真鉴权已落地：前后端接通 JWT，前台/后台由角色路由守卫分流。

## 功能特性

- 🔐 **真鉴权体系**：注册 / 登录 / access + refresh 双 token，bcrypt 密码哈希，401 自动刷新
- 📖 **法条搜索**：支持模糊搜索刑法、民法典法条，含司法解释和判例
- 📤 **文档分析**：上传合同/法律文件，AI 自动识别风险并评分
- 🔄 **文档对比**：两份文档对比，显示修改差异
- 💬 **智能问答**：AI 法律顾问，解答法律问题
- 📋 **合同模板**：常用合同模板库，一键使用
- 🛡️ **管理后台**：用户管理、统计概览（`/admin`），`require_admin` 守卫

## 技术栈

### 后端
- Python 3.10+
- FastAPI + SQLAlchemy (异步) + aiosqlite
- ChromaDB（向量搜索）
- MiMo API（AI 分析）
- JWT（python-jose）+ bcrypt（passlib）

### 前端
- Vite 7 + React 19 + TypeScript
- React Router v7（路由守卫）
- TanStack Query v5
- TailwindCSS

## 快速开始

### 1. 准备后端虚拟环境并安装依赖

```bash
py -3.11 -m venv .venv
.\.venv\Scripts\python -m pip install -r backend\requirements.txt "numpy<2"
```

### 2. 配置环境变量

```bash
copy backend\.env.example backend\.env
```

随后编辑 `backend/.env`：

- 必须：**填入 `MIMO_API_KEY`**
- 强烈建议：把 `JWT_SECRET` 改成一段随机长字符串
- 可选：`DEFAULT_ADMIN_USERNAME` / `DEFAULT_ADMIN_PASSWORD`（首次启动会自动创建管理员）

### 3. 启动后端

```bash
.\.venv\Scripts\python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 --app-dir backend
```

启动后请访问 `http://127.0.0.1:8000/`，或直接访问 `http://127.0.0.1:8000/docs` 查看 OpenAPI。

### 4. 启动前端开发服务器

```bash
cd frontend
npm install
npm run dev
```

打开 `http://127.0.0.1:5173/`。

> 前端默认通过 Vite dev server 直接访问 `http://127.0.0.1:8000` 调后端 API（已在 CORS 白名单中）。  
> 若直接构建前端产物 `npm run build`，FastAPI 会自动 mount `frontend/dist`，单端口也能用。

### 5. 默认管理员与首登

- 默认管理员：`admin` / `Admin@12345`
- 首次登录后请尽快通过 `PATCH /api/admin/users/{user_id}` 修改密码

## 鉴权 API 速查

| 方法 | 路径 | 说明 |
| --- | --- | --- |
| POST | `/api/user/register` | 注册（username + password + email 可选） |
| POST | `/api/user/login` | 登录（account 支持用户名/邮箱） |
| POST | `/api/user/refresh` | 用 refresh token 换新 access |
| POST | `/api/user/logout` | 登出（清本地 token） |
| GET  | `/api/user/me` | 当前用户信息 |
| GET  | `/api/user/me/stats` | 当前用户统计 |
| GET  | `/api/admin/users` | 用户列表（admin） |
| PATCH| `/api/admin/users/{id}` | 修改用户角色/状态/密码（admin） |
| GET  | `/api/admin/stats` | 概览统计（admin） |
| GET  | `/health` | 健康检查（db/ai/ocr 三态） |

鉴权头：`Authorization: Bearer <access_token>`。前端 `shared/api/client.ts` 已统一注入并在 401 时自动刷新一次。

## 项目结构

```
legal-ai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   ├── search.py
│   │   │   ├── document.py
│   │   │   ├── chat.py
│   │   │   ├── user.py         # 鉴权路由
│   │   │   ├── admin.py        # 管理后台路由
│   │   │   ├── template.py
│   │   │   └── deps.py         # get_current_user / require_admin
│   │   ├── core/
│   │   │   ├── security.py     # JWT + bcrypt
│   │   │   ├── ai_analyzer.py
│   │   │   ├── ocr_*.py
│   │   │   └── ...
│   │   ├── models/
│   │   │   ├── database.py     # UserDB 已扩展 username/role/status
│   │   │   └── schemas.py
│   │   ├── config.py           # JWT/CORS/管理员配置
│   │   └── main.py             # CORS 收口 + 健康检查
│   ├── data/
│   ├── uploads/
│   ├── .env.example
│   ├── OCR_DEPLOYMENT.md
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── providers/      # AuthProvider / AuthGuard / QueryProvider
│   │   │   ├── router/         # 路由表（含守卫）
│   │   │   └── layouts/
│   │   ├── pages/
│   │   ├── shared/
│   │   │   ├── api/            # 客户端 + auth-store + user.ts
│   │   │   ├── layouts/
│   │   │   └── ui/
│   │   └── main.tsx
│   └── package.json
├── .venv/
├── start.bat
└── README.md
```

## 注意事项

1. 首次运行会自动创建数据库，并对老库做 schema 兼容（`ALTER TABLE users` 补 `username/email/password_hash/role/status/last_login_at`）。
2. JWT 默认在 `DEBUG=true` 时使用占位 `JWT_SECRET`，**生产前务必修改**；`DEBUG=false` 时未设置 `JWT_SECRET` 会直接拒绝启动。
3. CORS 已收口为白名单模式（`CORS_ALLOW_ORIGINS` 逗号分隔），不再支持通配。
4. `Admin@12345` 是默认管理员密码，仅用于首次部署；务必尽快修改。
5. `passlib[bcrypt]` 已显式锁定 `bcrypt==4.0.1`，避免新版 bcrypt 与 passlib 兼容问题。
