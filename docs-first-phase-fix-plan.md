# 第一阶段关键修复实施计划

> **面向 AI 代理的工作者：** 优先以最小改动打通核心流程，先修稳定性与假功能，再考虑增强。步骤使用复选框（`- [ ]`）语法来跟踪进度。

**目标：** 将当前法律 AI 原型从“部分可演示”修复到“关键路径可真实跑通”。

**架构：** 保持现有 FastAPI + 原生前端结构不变，优先修复前后端通信、未接线 UI、收藏与报告导出等断点。避免大规模重构，先建立一致的数据流与稳定的交互闭环。

**技术栈：** FastAPI、原生 JavaScript、HTML/CSS、SQLite、MiMo API

---

## 涉及文件与职责

- 修改：`frontend/js/app.js` — 修复 API 基址、收藏逻辑、报告导出、对比按钮行为、假入口行为
- 修改：`frontend/index.html` — 给未接线按钮补上事件绑定，移除错误占位参数
- 可能修改：`backend/app/api/user.py` — 如前端接后端收藏时需要最小接口适配
- 可能修改：`backend/app/api/search.py` — 如前端收藏/法条详情需要附带更稳定字段时微调
- 验证：`README.md` — 启动说明是否与实际一致

## 任务 1：统一前端 API 调用方式

**文件：**
- 修改：`frontend/js/app.js:1-120`

- [ ] **步骤 1：将硬编码 API 地址改为同源相对路径**

```javascript
const API_BASE = '';
```

或等价实现：

```javascript
const API_BASE = window.location.origin;
```

优先选择空字符串方案，使 `fetch(`${API_BASE}/api/...`)` 直接落到当前 FastAPI 域名和端口。

- [ ] **步骤 2：检查所有 fetch 路径仍然可用**

确认这些调用仍然组成合法 URL：

```javascript
fetch(`${API_BASE}/api/document/analyze`, ...)
fetch(`${API_BASE}/api/document/compare`, ...)
fetch(`${API_BASE}/api/search/law?q=${encodeURIComponent(query)}`)
fetch(`${API_BASE}/api/chat/sessions`, ...)
fetch(`${API_BASE}/api/templates`, ...)
```

预期：相对路径调用在同域部署下无跨域问题。

## 任务 2：修复上传对比页的未接线按钮

**文件：**
- 修改：`frontend/index.html:90-105`
- 测试：手工点击验证

- [ ] **步骤 1：为“开始对比”按钮绑定点击事件**

将按钮改为：

```html
<button class="btn btn-primary btn-block" style="margin-top: 20px;" onclick="compareDocuments()">开始对比</button>
```

- [ ] **步骤 2：手工验证空文件与正常文件两种路径**

验证行为：
- 未上传两份文件时，提示“请先上传两份文档”
- 上传两份文件后，能够调用 `/api/document/compare`

## 任务 3：修复法条收藏参数错误并减少假功能

**文件：**
- 修改：`frontend/index.html:150-163`
- 修改：`frontend/js/app.js:289-340`

- [ ] **步骤 1：让法条收藏使用当前文章真实 ID**

将 HTML 中的空参数调用从：

```html
onclick="toggleFavorite('law', '')"
```

改为：

```html
onclick="toggleCurrentLawFavorite()"
```

- [ ] **步骤 2：在 `app.js` 中新增当前法条收藏辅助函数**

新增：

```javascript
function toggleCurrentLawFavorite() {
    if (!window.currentArticle || !window.currentArticle.id) {
        alert('当前法条信息不完整，暂时无法收藏');
        return;
    }
    toggleFavorite('law', window.currentArticle.id);
}
```

- [ ] **步骤 3：确保查看法条详情时已缓存当前文章**

保留或确认存在：

```javascript
window.currentArticle = article;
```

预期：收藏法条时不再写入空 ID。

## 任务 4：把分析报告导出功能做成可用版本

**文件：**
- 修改：`frontend/js/app.js:128-189,653-655`

- [ ] **步骤 1：在展示分析结果时缓存当前报告**

在 `showAnalysisResult(data)` 中加入：

```javascript
window.currentAnalysisReport = data;
```

- [ ] **步骤 2：实现最小可用的文本导出**

将 `exportReport()` 改为导出 `.txt` 文件，至少包含：
- 文档名
- 分析时间
- 风险分组
- 每条风险的标题/依据/建议
- 总结

建议结构：

```javascript
function exportReport() {
    const report = window.currentAnalysisReport;
    if (!report) {
        alert('当前没有可导出的分析报告');
        return;
    }

    const lines = [
        `文档名称：${report.document_name || '未命名文档'}`,
        `导出时间：${new Date().toLocaleString()}`,
        '',
        '【风险明细】'
    ];

    (report.risks || []).forEach((risk, index) => {
        lines.push(`${index + 1}. [${risk.level || 'medium'}] ${risk.title || '未命名风险'}`);
        lines.push(`描述：${risk.description || '无'}`);
        lines.push(`位置：${risk.location || '未提供'}`);
        lines.push(`法律依据：${(risk.legal_basis || []).join('；') || '无'}`);
        lines.push(`建议：${risk.suggestion || '无'}`);
        lines.push('');
    });

    lines.push('【分析总结】');
    lines.push(report.summary || '无');

    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(report.document_name || 'analysis-report').replace(/\.[^.]+$/, '')}-分析报告.txt`;
    a.click();
    URL.revokeObjectURL(url);
}
```

- [ ] **步骤 3：手工验证导出文件内容**

预期：点击后能下载文本文件，内容包含风险与总结。

## 任务 5：下线误导性“假入口”并补明确提示

**文件：**
- 修改：`frontend/js/app.js:181-186`
- 可选修改：`frontend/index.html:250-253`

- [ ] **步骤 1：移除“跳到对比页即等于一键修复”的错误暗示**

将：

```javascript
<button class="btn btn-primary" style="flex:1;" onclick="navigateTo('compare')">一键修复</button>
```

替换为更真实的行为，例如：

```javascript
<button class="btn btn-primary" style="flex:1;" onclick="alert('自动修复功能暂未开放，当前仅支持风险分析与文档对比。')">自动修复</button>
```

或直接改文案为“查看对比页”。

- [ ] **步骤 2：保证界面表意与真实能力一致**

预期：用户不会误以为系统已经具备自动改写合同能力。

## 任务 6：快速核对 README 运行说明

**文件：**
- 修改：`README.md`

- [ ] **步骤 1：确认 README 中启动端口与实际运行方式一致**

如果前端改为同域相对路径，则 README 保持由 FastAPI 承载前端即可。

建议说明改为：

```bash
cd legal-ai/backend
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

然后访问：

```text
http://127.0.0.1:8000/
```

- [ ] **步骤 2：移除“直接打开 frontend/index.html 即可”的误导**

因为当前页面依赖后端 API，推荐统一从 FastAPI 根路径访问。

## 自检

- [ ] 核对所有 `fetch` 是否都走相对路径
- [ ] 核对“开始对比”按钮确实已绑定
- [ ] 核对法条收藏不再写入空 ID
- [ ] 核对报告导出可以下载实际文本
- [ ] 核对不存在会误导用户的“假功能文案”
- [ ] 核对 README 启动方式与真实访问方式一致
