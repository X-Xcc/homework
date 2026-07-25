# 数据库设计文档

## 1. 文档目的

描述“法律 AI”系统在第一版正式交付方案下的核心数据实体、表关系、权限边界与 PostgreSQL 目标结构，为账号密码登录、自注册、管理员后台和核心业务功能提供一致的数据基线。

---

## 2. 数据库选型

### 当前
- SQLite（通过 `sqlite+aiosqlite` 使用）
- 初始化方式：`SQLAlchemy Base.metadata.create_all()`
- 兼容补丁：在运行时通过 `ensure_legacy_schema()` 对旧结构做兼容

### 目标
- PostgreSQL
- ORM：继续使用 SQLAlchemy Async
- 迁移机制：Alembic

### 选型结论

保留当前单体 + ORM 技术路线，将数据底座正式升级到 PostgreSQL，并以 Alembic 管理 schema 演进，是本期风险最低、收益最高的方案。

---

## 3. 第一版身份模型

### 3.1 角色模型
第一版只保留两种角色：
- `user`
- `admin`

### 3.2 注册方式
- 允许用户自己注册
- 用户名唯一
- 邮箱唯一
- 密码加密保存

### 3.3 数据权限原则
- `user` 只能访问自己的分析、对比、聊天、收藏和个人资料
- `admin` 可以查看全站用户、记录和系统状态

### 3.4 对旧模型的调整结论
旧文档中的“匿名用户”“openid 登录”“游客边界”不再作为第一版正式模型。后续数据库设计统一围绕“账号密码 + user/admin”展开。

---

## 4. 核心实体清单

| 表 / 模型 | 作用 | 关键字段 | 备注 |
|---|---|---|---|
| `users` | 用户主表 | `id`、`username`、`email`、`password_hash`、`role`、`status`、`last_login_at`、`created_at`、`updated_at` | 第一版认证核心表 |
| `analyses` | 文档分析记录 | `id`、`user_id`、`document_name`、`document_path`、`status`、`risks`、`summary`、`overall_score`、`created_at`、`completed_at` | `risks` 建议使用 JSONB |
| `comparisons` | 文档对比记录 | `id`、`user_id`、`document_a`、`document_b`、`document_a_path`、`document_b_path`、`changes`、`summary`、`status`、`created_at`、`completed_at` | `changes` 建议使用 JSONB |
| `chat_sessions` | 聊天会话主表 | `id`、`user_id`、`title`、`context`、`created_at`、`updated_at` | 一对多关联消息 |
| `chat_messages` | 聊天消息表 | `id`、`session_id`、`role`、`content`、`model_name`、`token_usage`、`latency_ms`、`created_at` | 为后续观测预留字段 |
| `favorites` | 收藏表 | `id`、`user_id`、`item_type`、`item_id`、`title`、`summary`、`created_at` | 需有去重唯一约束 |
| `system_notices` | 系统公告/门户内容（可选） | `id`、`title`、`content`、`status`、`created_at`、`updated_at` | 第一版可预留 |

---

## 5. 推荐字段设计

### 5.1 `users`

建议字段：
- `id`：字符串 UUID 主键
- `username`：用户名，唯一
- `email`：邮箱，唯一
- `password_hash`：密码哈希
- `role`：`user` / `admin`
- `status`：`active` / `disabled`
- `analysis_count`：可选冗余统计字段
- `chat_count`：可选冗余统计字段
- `last_login_at`
- `created_at`
- `updated_at`

说明：
- 删除 `openid` 作为主认证字段的设计中心地位
- 不再把匿名用户与正式用户混存为同一概念

### 5.2 `analyses`
- `id`
- `user_id`
- `document_name`
- `document_path`
- `source_type`
- `status`
- `risks`
- `summary`
- `overall_score`
- `overall_risk_level`
- `error_message`
- `created_at`
- `completed_at`

### 5.3 `comparisons`
- `id`
- `user_id`
- `document_a`
- `document_b`
- `document_a_path`
- `document_b_path`
- `changes`
- `summary`
- `change_count`
- `status`
- `error_message`
- `created_at`
- `completed_at`

### 5.4 `chat_sessions`
- `id`
- `user_id`
- `title`
- `context`
- `created_at`
- `updated_at`

### 5.5 `chat_messages`
- `id`
- `session_id`
- `role`
- `content`
- `model_name`
- `token_usage`
- `latency_ms`
- `created_at`

### 5.6 `favorites`
- `id`
- `user_id`
- `item_type`
- `item_id`
- `title`
- `summary`
- `created_at`

### 5.7 `system_notices`（预留）
- `id`
- `title`
- `content`
- `status`
- `created_at`
- `updated_at`

---

## 6. 实体关系

### 6.1 用户相关
- 一个 `user` 可以拥有多条 `analysis`
- 一个 `user` 可以拥有多条 `comparison`
- 一个 `user` 可以拥有多条 `chat_session`
- 一个 `user` 可以拥有多条 `favorite`

### 6.2 会话相关
- `chat_sessions.user_id -> users.id`
- `chat_messages.session_id -> chat_sessions.id`

### 6.3 业务记录相关
- `analyses.user_id -> users.id`
- `comparisons.user_id -> users.id`
- `favorites.user_id -> users.id`

---

## 7. 数据权限落点

### `users`
- `user` 只能查看自己的用户资料
- `admin` 可查看用户列表和用户详情

### `analyses`
- `user` 只能查看自己的分析记录
- `admin` 可查看全站分析记录

### `comparisons`
- `user` 只能查看自己的对比记录
- `admin` 可查看全站对比记录

### `chat_sessions` / `chat_messages`
- `user` 只能操作自己的会话
- `admin` 原则上只做查看统计，不介入消息内容管理，除非后续确有需要

### `favorites`
- `user` 只能管理自己的收藏
- `admin` 一般不直接管理收藏内容

---

## 8. 当前结构评估

### 8.1 现有优点
- 已覆盖分析、对比、聊天、收藏等主要业务对象
- 时间字段整体较齐全
- JSON 结构适合承载 AI 输出
- 单体模型适合当前项目体量

### 8.2 现有不足
- `users` 仍偏向 `openid/匿名` 模型，不适合当前正式方案
- 缺少 `username`、`email`、`password_hash`、`role`、`status` 等正式认证字段
- `favorites` 缺少数据库级唯一约束
- `chat_messages` 缺少模型、token、耗时字段
- SQLite + 运行时补丁方案不适合作为正式数据基座

---

## 9. PostgreSQL 约束与索引建议

### `users`
- `UNIQUE(username)`
- `UNIQUE(email)`
- `INDEX(role)`
- `INDEX(status)`
- `INDEX(created_at)`（可选）

### `analyses`
- `INDEX(user_id)`
- `INDEX(status)`
- `INDEX(created_at)`

### `comparisons`
- `INDEX(user_id)`
- `INDEX(status)`
- `INDEX(created_at)`

### `chat_sessions`
- `INDEX(user_id)`
- `INDEX(updated_at)`

### `chat_messages`
- `INDEX(session_id)`
- `INDEX(created_at)`

### `favorites`
- `INDEX(user_id)`
- `UNIQUE(user_id, item_type, item_id)`

---

## 10. 第一版管理后台所需统计口径

为了支持 `/admin` 的系统状态页，数据库层至少应支持以下聚合：
- 用户总数
- 活跃用户数（可按最近登录时间定义）
- 分析记录总数
- 对比记录总数
- 聊天会话总数
- 今日新增记录数
- 失败任务数
- 最近活动列表

这意味着在设计接口时，应预留面向管理仪表盘的聚合查询能力。

---

## 11. 迁移策略建议

### 推荐迁移方向
1. 用 Alembic 建立 PostgreSQL 初始化 schema
2. 重构 `users` 表字段，使其符合账号密码模型
3. 保留 `analyses`、`comparisons`、`chat_sessions`、`chat_messages`、`favorites` 作为核心业务表
4. 对旧匿名/openid 数据做一次性清理或放弃迁移
5. 新环境优先采用冷启动方式上线

### 更推荐的初始化方案
- 方案 A：冷启动
  - 不保留匿名历史数据
  - 只迁移新的正式 schema
  - 适合当前答辩/校园交付环境

- 方案 B：有限数据迁移
  - 仅迁移必要的分析/对话数据
  - 需要先完成旧 `users` 到新 `users` 的映射规则

当前更推荐 **方案 A**。

---

## 12. 结论

本项目第一版数据库的关键，不是扩很多新表，而是把用户身份模型从“演示型匿名/openid”收口为“自注册账号密码 + admin/user 角色”。只要这一步走稳，再配合 PostgreSQL 和 Alembic，现有分析、对比、聊天等核心业务表都可以继续沿用并逐步正规化。
