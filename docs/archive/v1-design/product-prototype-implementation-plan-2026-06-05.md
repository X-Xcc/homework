# 劳动用工与合同审查 AI 助手第一轮产品化 实现计划

> **面向 AI 代理的工作者：** 必需子技能：使用 superpowers:subagent-driven-development（推荐）或 superpowers:executing-plans 逐任务实现此计划。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 把现有法律 AI 原型升级为面向小微企业 HR/行政的第一轮真实产品原型，完成匿名用户、真实记录、工作台首页和结构化审查结果闭环。

**架构：** 保持 FastAPI + 原生前端架构不变，优先打通“匿名用户 → 聊天/分析/对比/收藏 → 首页/历史/收藏展示”的真实数据链。后端补齐用户绑定、聚合接口和结果归一化，前端改为后端驱动的企业法务工作台。

**技术栈：** FastAPI、SQLAlchemy Async、SQLite、原生 JavaScript、HTML/CSS

---

## 涉及文件与职责

- 修改：`backend/app/models/database.py` — 补充模型字段与默认值，支持用户绑定与展示元信息
- 修改：`backend/app/models/schemas.py` — 补充产品原型所需响应结构
- 修改：`backend/app/api/user.py` — 新增匿名登录、工作台聚合、后端收藏列表能力
- 修改：`backend/app/api/chat.py` — 全链路改为显式绑定 `user_id`
- 修改：`backend/app/api/document.py` — 分析/对比改为显式绑定 `user_id`，返回更完整结构
- 修改：`backend/app/api/search.py` — 支持空关键词兜底，改善产品可用性
- 修改：`backend/app/main.py` — 如需新增接口挂载或启动初始化逻辑，保持一致
- 修改：`frontend/index.html` — 首页改为工作台，补充真实记录容器和免责声明文案
- 修改：`frontend/js/app.js` — 接入匿名用户、统一请求携带 `user_id`、工作台/历史/收藏数据渲染
- 修改：`frontend/css/style.css` — 为工作台首页、统计卡、记录块等补样式
- 修改：`README.md` — 同步真实产品原型的启动与能力说明

---

### 任务 1：建立匿名用户体系与前端登录态

**文件：**
- 修改：`backend/app/api/user.py`
- 修改：`frontend/js/app.js`
- 测试：后端接口手工调用 + 前端首次进入验证

- [ ] **步骤 1：在后端新增匿名登录接口**

在 `backend/app/api/user.py` 中新增 `POST /api/user/guest-login`，请求体可为空或接收可选 `device_id`。实现逻辑：

```python
@router.post("/guest-login")
async def guest_login(request: Request, db: AsyncSession = Depends(get_db)):
    try:
        body = await request.json()
    except Exception:
        body = {}

    device_id = body.get("device_id") or str(uuid.uuid4())
    openid = f"guest:{device_id}"

    query = select(UserDB).where(UserDB.openid == openid)
    result = await db.execute(query)
    user = result.scalar_one_or_none()

    if not user:
        user = UserDB(
            id=str(uuid.uuid4()),
            openid=openid,
            nickname=f"访客用户-{device_id[:6]}",
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)

    return {
        "id": user.id,
        "openid": user.openid,
        "nickname": user.nickname,
        "analysis_count": user.analysis_count,
        "chat_count": user.chat_count,
        "created_at": user.created_at,
    }
```

- [ ] **步骤 2：前端新增本地设备 ID 与匿名登录流程**

在 `frontend/js/app.js` 顶部新增：

```javascript
let currentUser = null;

function getDeviceId() {
    let deviceId = localStorage.getItem('deviceId');
    if (!deviceId) {
        deviceId = crypto.randomUUID ? crypto.randomUUID() : `device-${Date.now()}`;
        localStorage.setItem('deviceId', deviceId);
    }
    return deviceId;
}
```

并新增：

```javascript
async function ensureGuestSession() {
    const savedUser = localStorage.getItem('userProfile');
    if (savedUser) {
        currentUser = JSON.parse(savedUser);
        return currentUser;
    }

    const response = await fetch(`${API_BASE}/api/user/guest-login`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ device_id: getDeviceId() })
    });

    if (!response.ok) {
        throw new Error('匿名登录失败');
    }

    currentUser = await response.json();
    localStorage.setItem('userProfile', JSON.stringify(currentUser));
    localStorage.setItem('isLoggedIn', 'true');
    return currentUser;
}
```

- [ ] **步骤 3：把现有 `handleLogin` 改为触发匿名登录**

将 `handleLogin()` 改为：

```javascript
async function handleLogin() {
    try {
        await ensureGuestSession();
        document.getElementById('loginPage').style.display = 'none';
        document.getElementById('mainApp').style.display = 'block';
        await loadDashboard();
        await loadRecentChats();
    } catch (error) {
        alert('进入系统失败：' + error.message);
    }
}
```

- [ ] **步骤 4：在 `checkLogin` 中恢复匿名用户会话**

将 `checkLogin()` 调整为：

```javascript
async function checkLogin() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    if (isLoggedIn === 'true') {
        try {
            await ensureGuestSession();
            document.getElementById('loginPage').style.display = 'none';
            document.getElementById('mainApp').style.display = 'block';
            await loadDashboard();
            await loadRecentChats();
        } catch (error) {
            localStorage.removeItem('isLoggedIn');
            localStorage.removeItem('userProfile');
        }
    }
}
```

- [ ] **步骤 5：手工验证匿名登录**

运行后端后，在浏览器首次点击登录。

预期：
- 数据库生成一条 `users` 记录
- 前端保存 `userProfile`
- 刷新页面后仍可恢复登录态

---

### 任务 2：把聊天系统改为真实按用户隔离

**文件：**
- 修改：`backend/app/api/chat.py`
- 修改：`backend/app/models/database.py`
- 修改：`frontend/js/app.js`
- 测试：创建两个会话并验证只读取当前用户自己的数据

- [ ] **步骤 1：创建会话接口接收并校验 `user_id`**

在 `backend/app/api/chat.py` 的 `create_session()` 中加入用户读取：

```python
user_id = body.get("user_id")
if not user_id:
    raise HTTPException(status_code=400, detail="缺少 user_id")

user = await db.get(UserDB, user_id)
if not user:
    raise HTTPException(status_code=404, detail="用户未找到")
```

创建会话时写入：

```python
session = ChatSessionDB(
    id=session_id,
    user_id=user_id,
    title=body.get("title", "新对话"),
    context=body.get("context")
)
```

- [ ] **步骤 2：会话列表按 `user_id` 过滤**

将列表接口改为：

```python
@router.get("/sessions")
async def list_sessions(
    user_id: str,
    limit: int = 20,
    offset: int = 0,
    db: AsyncSession = Depends(get_db)
):
    query = (
        select(ChatSessionDB)
        .where(ChatSessionDB.user_id == user_id)
        .order_by(desc(ChatSessionDB.updated_at))
        .offset(offset)
        .limit(limit)
    )
```

- [ ] **步骤 3：会话详情和发消息都做用户归属校验**

详情接口加：

```python
if session.user_id != user_id:
    raise HTTPException(status_code=403, detail="无权访问该会话")
```

发消息接口请求体增加：

```python
user_id = body.get("user_id")
if not user_id or session.user_id != user_id:
    raise HTTPException(status_code=403, detail="无权操作该会话")
```

- [ ] **步骤 4：发消息成功后更新用户计数**

在生成 AI 回复并提交前：

```python
user = await db.get(UserDB, user_id)
if user:
    user.chat_count = (user.chat_count or 0) + 1
```

- [ ] **步骤 5：前端所有聊天请求带上 `currentUser.id`**

在 `startNewChat()` 中改为：

```javascript
body: JSON.stringify({
    user_id: currentUser.id,
    title: message.substring(0, 20)
})
```

在 `loadRecentChats()` / `loadHistory()` 中使用：

```javascript
fetch(`${API_BASE}/api/chat/sessions?user_id=${encodeURIComponent(currentUser.id)}&limit=3`)
```

在 `sendMessage()` 中使用：

```javascript
body: JSON.stringify({
    user_id: currentUser.id,
    role: 'user',
    content: message
})
```

- [ ] **步骤 6：手工验证聊天隔离**

预期：
- 当前匿名用户创建的会话可见
- 缺少 `user_id` 时接口报错
- 他人会话不能被当前用户读取

---

### 任务 3：把分析和对比记录改为真实绑定用户

**文件：**
- 修改：`backend/app/api/document.py`
- 修改：`backend/app/models/database.py`
- 修改：`frontend/js/app.js`
- 测试：上传分析、上传对比、查询分析详情

- [ ] **步骤 1：文档分析接口改为接收表单中的 `user_id`**

在 `backend/app/api/document.py` 中把签名改为：

```python
from fastapi import Form

@router.post("/analyze")
async def analyze_document(
    user_id: str = Form(...),
    file: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
```

分析记录写入：

```python
analysis = AnalysisDB(
    id=file_id,
    user_id=user_id,
    document_name=file.filename,
    document_path=file_path,
    status="processing"
)
```

- [ ] **步骤 2：文档对比接口改为接收表单中的 `user_id`**

函数签名改为：

```python
@router.post("/compare")
async def compare_documents(
    user_id: str = Form(...),
    file_a: UploadFile = File(...),
    file_b: UploadFile = File(...),
    db: AsyncSession = Depends(get_db)
):
```

对比记录写入：

```python
comparison = ComparisonDB(
    id=comparison_id,
    user_id=user_id,
    document_a=file_a.filename,
    document_b=file_b.filename,
    document_a_path=files[0]["path"],
    document_b_path=files[1]["path"]
)
```

- [ ] **步骤 3：分析成功后更新用户分析次数**

在分析完成分支加入：

```python
user = await db.get(UserDB, user_id)
if user:
    user.analysis_count = (user.analysis_count or 0) + 1
```

- [ ] **步骤 4：前端上传请求增加 `user_id`**

在 `analyzeDocument(file)` 中加入：

```javascript
formData.append('user_id', currentUser.id);
```

在 `compareDocuments()` 中加入：

```javascript
formData.append('user_id', currentUser.id);
```

- [ ] **步骤 5：新增最近记录查询辅助接口**

在 `backend/app/api/document.py` 中新增：

```python
@router.get("/records")
async def list_document_records(user_id: str, limit: int = 5, db: AsyncSession = Depends(get_db)):
    analyses_query = (
        select(AnalysisDB)
        .where(AnalysisDB.user_id == user_id)
        .order_by(AnalysisDB.created_at.desc())
        .limit(limit)
    )
    comparisons_query = (
        select(ComparisonDB)
        .where(ComparisonDB.user_id == user_id)
        .order_by(ComparisonDB.created_at.desc())
        .limit(limit)
    )
```

返回统一结构：

```python
return {
    "analyses": [...],
    "comparisons": [...]
}
```

- [ ] **步骤 6：手工验证审查记录绑定**

预期：
- 新分析记录 `user_id` 不再是 `default`
- 新对比记录 `user_id` 不再是 `default`
- 用户计数增长

---

### 任务 4：把收藏功能改为后端驱动

**文件：**
- 修改：`backend/app/api/user.py`
- 修改：`frontend/js/app.js`
- 测试：收藏法条、刷新页面、再次读取列表

- [ ] **步骤 1：收藏列表返回足够的展示信息**

在 `backend/app/api/user.py` 中把返回结构从仅 `item_id` 改为至少：

```python
return [{
    "id": f.id,
    "item_type": f.item_type,
    "item_id": f.item_id,
    "title": f.title,
    "subtitle": f.subtitle,
    "created_at": f.created_at,
} for f in favorites]
```

若 `FavoriteDB` 没有 `title/subtitle` 字段，则先在 `backend/app/models/database.py` 增加：

```python
title = Column(String)
subtitle = Column(String)
```

- [ ] **步骤 2：新增收藏时支持写入标题信息**

把 `add_favorite()` 改为从 JSON 请求体读取：

```python
body = await request.json()
user_id = body.get("user_id")
item_type = body.get("item_type")
item_id = body.get("item_id")
title = body.get("title")
subtitle = body.get("subtitle")
```

保存时写入：

```python
favorite = FavoriteDB(
    id=str(uuid.uuid4()),
    user_id=user_id,
    item_type=item_type,
    item_id=item_id,
    title=title,
    subtitle=subtitle,
)
```

- [ ] **步骤 3：前端去掉 `localStorage` 收藏主逻辑**

将 `toggleFavorite()` 改为调用后端。

新增创建请求：

```javascript
await fetch(`${API_BASE}/api/user/favorites`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
        user_id: currentUser.id,
        item_type: type,
        item_id: id,
        title,
        subtitle
    })
});
```

取消收藏时，先从后端收藏列表中找到对应 `favorite.id`，再调用：

```javascript
await fetch(`${API_BASE}/api/user/favorites/${favoriteId}`, { method: 'DELETE' });
```

- [ ] **步骤 4：收藏列表从后端读取**

重写 `loadFavorites(type = 'all')`：

```javascript
let url = `${API_BASE}/api/user/favorites/${currentUser.id}`;
if (type !== 'all') {
    url += `?item_type=${encodeURIComponent(type)}`;
}
const response = await fetch(url);
const favorites = await response.json();
```

渲染时使用后端返回的 `title` 和 `subtitle`。

- [ ] **步骤 5：法条收藏调用携带标题**

在 `toggleCurrentLawFavorite()` 中调用：

```javascript
toggleFavorite('law', window.currentArticle.id, {
    title: window.currentArticle.title || window.currentArticle.article_number,
    subtitle: window.currentArticle.law_name || '法条'
});
```

并把函数签名改为：

```javascript
async function toggleFavorite(type, id, meta = {})
```

- [ ] **步骤 6：手工验证收藏刷新后可见**

预期：
- 收藏法条后后端新增记录
- 刷新页面后收藏仍然存在
- 收藏页能展示标题信息

---

### 任务 5：新增工作台聚合接口并重构首页

**文件：**
- 修改：`backend/app/api/user.py`
- 修改：`frontend/index.html`
- 修改：`frontend/js/app.js`
- 修改：`frontend/css/style.css`
- 测试：登录后首页展示真实统计与最近记录

- [ ] **步骤 1：后端新增工作台聚合接口**

在 `backend/app/api/user.py` 中新增：

```python
@router.get("/dashboard/{user_id}")
async def get_dashboard(user_id: str, db: AsyncSession = Depends(get_db)):
    user = await db.get(UserDB, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="用户未找到")
```

查询最近会话、最近分析、最近对比、收藏数量，并返回：

```python
return {
    "user": {
        "id": user.id,
        "nickname": user.nickname,
        "analysis_count": user.analysis_count,
        "chat_count": user.chat_count,
    },
    "stats": {
        "favorite_count": favorite_count,
        "analysis_count": user.analysis_count or 0,
        "chat_count": user.chat_count or 0,
        "comparison_count": comparison_count,
    },
    "recent_analyses": [...],
    "recent_comparisons": [...],
    "recent_chats": [...],
}
```

- [ ] **步骤 2：首页 HTML 改为企业法务工作台结构**

将 `frontend/index.html` 首页区域替换为以下结构骨架：

```html
<div id="page-home" class="page active">
    <div class="navbar">
        <span class="navbar-title">企业法务助手</span>
        <span id="homeUserName" class="navbar-subtitle"></span>
    </div>

    <div class="dashboard-hero">
        <div class="dashboard-hero-title">劳动用工与合同审查 AI 助手</div>
        <div class="dashboard-hero-subtitle">适用于 HR、行政与小微企业日常合同及用工风险处理</div>
    </div>

    <div class="dashboard-stats" id="dashboardStats"></div>
    <div class="quick-actions">...</div>
    <div class="dashboard-section">
        <div class="dashboard-section-title">最近审查</div>
        <div id="recentAnalyses"></div>
    </div>
    <div class="dashboard-section">
        <div class="dashboard-section-title">最近问答</div>
        <div id="recentChats"></div>
    </div>
    <div class="dashboard-disclaimer">系统结果仅供参考，重大决策请咨询专业律师。</div>
</div>
```

- [ ] **步骤 3：前端新增 `loadDashboard()` 渲染逻辑**

在 `frontend/js/app.js` 中新增：

```javascript
async function loadDashboard() {
    const response = await fetch(`${API_BASE}/api/user/dashboard/${currentUser.id}`);
    if (!response.ok) throw new Error('加载工作台失败');

    const data = await response.json();
    document.getElementById('homeUserName').textContent = data.user.nickname;

    document.getElementById('dashboardStats').innerHTML = [
        { label: '审查次数', value: data.stats.analysis_count },
        { label: '问答次数', value: data.stats.chat_count },
        { label: '对比次数', value: data.stats.comparison_count },
        { label: '收藏数量', value: data.stats.favorite_count },
    ].map(item => `
        <div class="dashboard-stat-card">
            <div class="dashboard-stat-value">${item.value}</div>
            <div class="dashboard-stat-label">${item.label}</div>
        </div>
    `).join('');
}
```

- [ ] **步骤 4：把最近记录渲染为真实数据**

在 `loadDashboard()` 或单独函数中渲染：

```javascript
document.getElementById('recentAnalyses').innerHTML = data.recent_analyses.length
    ? data.recent_analyses.map(item => `
        <div class="card" onclick="openAnalysisRecord('${item.id}')">
            <div style="font-size:14px;margin-bottom:4px;">${item.document_name}</div>
            <div style="font-size:12px;color:var(--text-secondary);">${item.status} · ${formatDate(item.created_at)}</div>
        </div>
    `).join('')
    : '<div class="empty-state">暂无审查记录</div>';
```

聊天记录同理渲染到 `recentChats`。

- [ ] **步骤 5：补首页样式**

在 `frontend/css/style.css` 中新增：

```css
.dashboard-hero { padding: 20px; }
.dashboard-hero-title { font-size: 20px; font-weight: 700; }
.dashboard-hero-subtitle { font-size: 13px; color: var(--text-secondary); margin-top: 6px; line-height: 1.6; }
.dashboard-stats { display: grid; grid-template-columns: repeat(2, 1fr); gap: 12px; padding: 0 20px 20px; }
.dashboard-stat-card { background: var(--bg-card); border: 1px solid var(--border); border-radius: 14px; padding: 16px; }
.dashboard-stat-value { font-size: 20px; font-weight: 700; }
.dashboard-stat-label { font-size: 12px; color: var(--text-secondary); margin-top: 4px; }
.dashboard-section { padding: 0 20px 20px; }
.dashboard-disclaimer { margin: 0 20px 90px; font-size: 12px; color: var(--text-secondary); line-height: 1.6; }
```

- [ ] **步骤 6：手工验证工作台首页**

预期：
- 登录后首页显示用户昵称
- 统计卡显示真实数字
- 最近审查与最近问答显示后端数据
- 有清晰免责声明

---

### 任务 6：增强历史页、报告页与搜索空结果体验

**文件：**
- 修改：`backend/app/api/search.py`
- 修改：`frontend/js/app.js`
- 修改：`frontend/index.html`
- 测试：空搜索、历史页、报告页展示

- [ ] **步骤 1：修复空关键词搜索体验**

将 `backend/app/api/search.py` 中的搜索逻辑改为：

```python
query = (q or "").strip()
if not query:
    return legal_db.search("劳动", law_type=type, limit=limit)
return legal_db.search(query, law_type=type, limit=limit)
```

- [ ] **步骤 2：历史页按类型聚合显示**

在 `frontend/js/app.js` 的 `loadHistory()` 中，新增对 `/api/document/records` 的请求：

```javascript
const [chatRes, documentRes] = await Promise.all([
    fetch(`${API_BASE}/api/chat/sessions?user_id=${encodeURIComponent(currentUser.id)}&limit=50`),
    fetch(`${API_BASE}/api/document/records?user_id=${encodeURIComponent(currentUser.id)}&limit=20`)
]);
```

然后合并渲染为：
- 问答记录
- 审查记录
- 对比记录

- [ ] **步骤 3：报告页增加风险总览区**

在 `showAnalysisResult(data)` 中于风险列表前插入：

```javascript
const summaryStats = document.createElement('div');
summaryStats.className = 'dashboard-stats';
summaryStats.innerHTML = `
    <div class="dashboard-stat-card"><div class="dashboard-stat-value">${riskGroups.high.items.length}</div><div class="dashboard-stat-label">高风险</div></div>
    <div class="dashboard-stat-card"><div class="dashboard-stat-value">${riskGroups.medium.items.length}</div><div class="dashboard-stat-label">中风险</div></div>
    <div class="dashboard-stat-card"><div class="dashboard-stat-value">${riskGroups.low.items.length}</div><div class="dashboard-stat-label">低风险</div></div>
    <div class="dashboard-stat-card"><div class="dashboard-stat-value">${(data.risks || []).length}</div><div class="dashboard-stat-label">总风险项</div></div>
`;
container.appendChild(summaryStats);
```

- [ ] **步骤 4：报告页追加免责声明**

在报告页底部追加：

```javascript
const disclaimer = document.createElement('div');
disclaimer.style.cssText = 'margin-top:20px;font-size:12px;color:var(--text-secondary);line-height:1.6;';
disclaimer.textContent = '提示：本报告仅供企业内部初步合规参考，重大决策请咨询专业律师。';
container.appendChild(disclaimer);
```

- [ ] **步骤 5：手工验证产品体验改进**

预期：
- 打开法条页时空搜索不报错
- 历史页包含审查、对比、聊天三类记录
- 报告页有风险总览和免责声明

---

### 任务 7：更新 README 并做回归验证

**文件：**
- 修改：`README.md`
- 测试：编译/运行/关键接口检查

- [ ] **步骤 1：更新 README 的产品定位说明**

在 README 开头补充：

```markdown
本项目现定位为面向小微企业 HR / 行政的劳动用工与合同审查 AI 助手原型，核心能力包括：
- 合同风险审查
- 文档版本对比
- 劳动用工问答
- 法条依据查询
- 模板与个人记录管理
```

- [ ] **步骤 2：更新 README 的使用流程**

补充真实使用顺序：

```markdown
1. 首次进入系统会自动创建匿名访客身份
2. 可在“上传”页进行合同审查或文档对比
3. 可在首页查看最近审查和问答记录
4. 收藏、历史、统计信息均由后端持久化
```

- [ ] **步骤 3：运行后端编译检查**

运行：

```bash
py -m compileall "D:\homework\legal-ai\backend\app"
```

预期：PASS，无语法错误。

- [ ] **步骤 4：启动服务做关键路径冒烟验证**

运行：

```bash
cd D:\homework\legal-ai\backend && uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

验证：
- `POST /api/user/guest-login`
- `POST /api/chat/sessions`
- `POST /api/document/analyze`（至少校验缺少文件时接口行为正常）
- 打开首页后工作台正常渲染

- [ ] **步骤 5：回归确认第一轮产品化目标**

确认以下结论均为真：
- 匿名用户流程已打通
- 聊天/审查/对比/收藏都绑定真实用户
- 首页已从聊天入口改为企业法务工作台
- 历史与收藏不再依赖纯前端缓存
- 报告页具备更像产品的结构化展示

---

## 自检

- [ ] 规格中的匿名用户、真实记录、工作台首页、结构化报告均有对应任务
- [ ] 计划中没有“后续补充”“适当处理”等占位描述
- [ ] 前后端使用的字段名统一为 `user_id`、`currentUser.id`、`recent_analyses`、`recent_chats`
- [ ] 所有新增接口都给出明确路径、请求体与返回结构
- [ ] 第一轮范围控制在产品原型底座，不扩散到支付、微信真登录或自动修复合同
