# 法律AI助手 代码审查报告

**审查日期：** 2026-06-27  
**审查范围：** 全项目前后端代码  

---

## 一、严重问题（P0）

### 1.1 流式响应中数据库会话失效
- **位置：** `backend/app/api/chat.py` 第185-206行, `backend/app/api/document.py` 第137-169行
- **问题：** `send_message_stream` 和 `analyze_document_stream` 在异步生成器 `generate()` 内部执行 `await db.commit()`。`Depends(get_db)` 创建的数据库会话生命周期绑定到请求响应周期，当 `StreamingResponse` 返回后会话可能已关闭，客户端断开连接时消息丢失。
- **建议：** 改为在流结束后使用独立会话提交，或使用 FastAPI `background task` 处理持久化。

### 1.2 后端引用不存在的函数
- **位置：** `backend/app/api/user.py` 第283行
- **问题：** `create_anonymous_user` 内部 `from app.api.deps import get_or_create_user_by_client_id`，但 `deps.py` 中完全没有该函数定义。该端点运行时必定抛出 `ImportError`。
- **建议：** 删除该死代码或补全函数实现。

### 1.3 前端 XSS 漏洞
- **位置：** `frontend/js/app.js` 多处
- **问题：** 大量使用 `innerHTML` 拼接用户数据未做转义，攻击者可注入恶意脚本。
  - 第555行 `displaySearchResults`：`item.title`、`item.content` 直接注入
  - 第395行风险报告：`risk.title`、`risk.description` 未转义
  - 第770行聊天消息：`formatMessage()` 不转义 HTML 实体
- **建议：** 增加 `escapeHTML()` 函数，在所有注入点前调用。

### 1.4 认证流程不一致
- **位置：** `frontend/js/app.js` 第23-29行, `backend/app/api/deps.py`
- **问题：** 前端 `getAuthHeaders` 始终附加 `X-Client-Id` 和 `X-User-Id`，但后端已弃用该方式改用 JWT Bearer Token。前端无任何 JWT 管理逻辑。
- **建议：** 实现 JWT token 存储与 `Authorization` header 注入，移除旧的 X-Client-Id 方式。

---

## 二、架构问题（P1）

### 2.1 DRY 违反：风险计算函数重复
- **位置：** `document.py` 第18-36行, `user.py` 第36-54行, `document.py` 第278-279行
- **问题：** `compute_overall_risk_level` 和 `compute_overall_score` 在三处完全相同。
- **建议：** 抽取到 `app.core.risk` 模块统一引用。

### 2.2 `document_parser` 双重实例化
- **位置：** `document_parser.py` 第196行, `document_service.py` 第9行
- **问题：** 两个文件各自创建全局实例，启动时双重初始化 OCR 引擎。
- **建议：** 统一在 `document_parser.py` 创建实例，`document_service.py` 仅导入。

### 2.3 裸 `except:` 捕获
- **位置：** `chat.py` 第23、107、164行; `ai_analyzer.py` 第217行; `template.py` 第14行
- **问题：** 吞掉 `KeyboardInterrupt`、`SystemExit` 等异常，掩盖真实错误。
- **建议：** 替换为 `except Exception:`。

### 2.4 `__init__.py` 路由导出不一致
- **位置：** `backend/app/api/__init__.py`
- **问题：** 只导出4个路由，`template_router` 和 `admin_router` 需单独导入。
- **建议：** 统一路由注册模式。

---

## 三、性能问题（P2）

### 3.1 法条检索 O(n) 线性扫描
- **位置：** `backend/app/core/legal_db.py` 第25-53行
- **问题：** 每次查询遍历全部法条数据做子串匹配。
- **建议：** 构建倒排索引，或迁移到数据库全文检索。

### 3.2 模板每次请求读磁盘
- **位置：** `backend/app/api/template.py` 第10-15行
- **问题：** `load_templates()` 每次请求都 `open()` + `json.load()`。
- **建议：** 缓存到内存，文件变更时重新加载。

### 3.3 手动 schema 迁移
- **位置：** `backend/app/models/database.py` 第105-153行
- **问题：** `ensure_legacy_schema` 使用原始 SQL ALTER TABLE，无版本追踪和回滚。
- **建议：** 引入 Alembic 正式迁移工具。

---

## 四、代码质量（P2）

### 4.1 悬挂 import
- **位置：** `document.py` 第284行（`import json` 重复）; `admin.py` 第191行（`datetime` 重复导入）

### 4.2 前端架构
- 全局状态泛滥，无模块化
- 错误处理仅 console.log，用户无反馈
- 无加载态指示
- index.html 源码与实际服务不匹配

### 4.3 CSS 限制
- 仅暗色主题，无亮色模式
- `max-width: 480px` 移动端优先但缺乏响应式断点

---

## 五、改进建议汇总

| 优先级 | 措施 | 影响 |
|--------|------|------|
| P0 | 修复流式端点 db session 生命周期 | 数据一致性 |
| P0 | 删除/修复 `create_anonymous_user` 死代码 | 运行时崩溃 |
| P0 | 前端增加 XSS 防护 | 安全漏洞 |
| P0 | 统一认证流程（JWT） | 功能正常 |
| P1 | 抽取公共风险计算函数 | 可维护性 |
| P1 | 修复裸 except 捕获 | 错误处理 |
| P1 | 统一路由注册 | 架构一致性 |
| P2 | 法条检索优化 | 性能 |
| P2 | 模板缓存 | 性能 |
| P2 | 引入 Alembic 迁移 | 可维护性 |
| P2 | 清理悬挂 import | 代码质量 |
