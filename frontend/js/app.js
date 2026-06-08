const API_BASE = '';

let currentPage = 'home';
let currentSessionId = null;
let currentUser = null;
let currentHistoryFilter = 'all';
let currentTemplateCategory = 'all';

function generateClientId() {
    if (window.crypto?.randomUUID) return window.crypto.randomUUID();
    return `anon-${Date.now()}-${Math.random().toString(16).slice(2)}`;
}

function getClientId() {
    let clientId = localStorage.getItem('legal_ai_client_id');
    if (!clientId) {
        clientId = generateClientId();
        localStorage.setItem('legal_ai_client_id', clientId);
    }
    return clientId;
}

function getAuthHeaders(extraHeaders = {}) {
    return {
        'X-Client-Id': getClientId(),
        ...(currentUser?.id ? { 'X-User-Id': currentUser.id } : {}),
        ...extraHeaders,
    };
}

async function apiFetch(url, options = {}) {
    const response = await fetch(`${API_BASE}${url}`, {
        ...options,
        headers: getAuthHeaders(options.headers || {}),
    });

    if (!response.ok) {
        let detail = '请求失败';
        try {
            const data = await response.json();
            detail = data.detail || detail;
        } catch (error) {
            detail = response.statusText || detail;
        }
        throw new Error(detail);
    }

    return response;
}

async function ensureAnonymousUser() {
    const response = await fetch(`${API_BASE}/api/user/anonymous`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            client_id: getClientId(),
            nickname: '匿名企业法务用户',
        }),
    });

    if (!response.ok) {
        const data = await response.json().catch(() => ({}));
        throw new Error(data.detail || '匿名用户初始化失败');
    }

    currentUser = await response.json();
    localStorage.setItem('legal_ai_user_id', currentUser.id);
    localStorage.setItem('isLoggedIn', 'true');
    return currentUser;
}

async function loadCurrentUserProfile() {
    const response = await apiFetch('/api/user/me');
    currentUser = await response.json();
    renderUserProfile();
    return currentUser;
}

function renderUserProfile() {
    if (!currentUser) return;

    const profileName = document.getElementById('profileName');
    const analysisCount = document.getElementById('analysisCount');
    const chatCount = document.getElementById('chatCount');
    const dashboardUserName = document.getElementById('dashboardUserName');
    const dashboardUserId = document.getElementById('dashboardUserId');
    const statAnalysis = document.getElementById('statAnalysisCount');
    const statChat = document.getElementById('statChatCount');
    const statFavorite = document.getElementById('statFavoriteCount');
    const statCompare = document.getElementById('statCompareCount');
    const profileUserId = document.getElementById('profileUserId');
    const profileFavoriteCount = document.getElementById('profileFavoriteCount');
    const profileCompareCount = document.getElementById('profileCompareCount');

    if (profileName) profileName.textContent = currentUser.nickname || '匿名用户';
    if (analysisCount) analysisCount.textContent = currentUser.analysis_count || 0;
    if (chatCount) chatCount.textContent = currentUser.chat_count || 0;
    if (dashboardUserName) dashboardUserName.textContent = currentUser.nickname || '匿名用户';
    if (dashboardUserId) dashboardUserId.textContent = `用户ID：${currentUser.id}`;
    if (statAnalysis) statAnalysis.textContent = currentUser.analysis_count || 0;
    if (statChat) statChat.textContent = currentUser.chat_count || 0;
    if (statFavorite) statFavorite.textContent = currentUser.favorite_count || 0;
    if (statCompare) statCompare.textContent = currentUser.comparison_count || 0;
    if (profileUserId) profileUserId.textContent = currentUser.id || '--';
    if (profileFavoriteCount) profileFavoriteCount.textContent = currentUser.favorite_count || 0;
    if (profileCompareCount) profileCompareCount.textContent = currentUser.comparison_count || 0;
}

async function bootstrapUserSession() {
    await ensureAnonymousUser();
    await loadCurrentUserProfile();
    document.getElementById('loginPage').style.display = 'none';
    document.getElementById('mainApp').style.display = 'block';
}

async function handleLogin() {
    try {
        await bootstrapUserSession();
        await Promise.all([loadWorkspaceSummary(), loadRecentChats()]);
    } catch (error) {
        alert(`进入工作台失败：${error.message}`);
    }
}

async function checkLogin() {
    const isLoggedIn = localStorage.getItem('isLoggedIn');
    if (isLoggedIn === 'true') {
        try {
            await bootstrapUserSession();
            await Promise.all([loadWorkspaceSummary(), loadRecentChats()]);
        } catch (error) {
            localStorage.removeItem('isLoggedIn');
            document.getElementById('loginPage').style.display = 'block';
            document.getElementById('mainApp').style.display = 'none';
        }
    }
}

function navigateTo(page) {
    document.querySelectorAll('.page').forEach(p => p.classList.remove('active'));
    document.getElementById(`page-${page}`).classList.add('active');
    currentPage = page;
    updateTabBar(page);

    if (page === 'history') loadHistory();
    else if (page === 'search') { document.getElementById('lawSearchInput').focus(); loadAllLaws(); }
    else if (page === 'template') loadTemplates();
    else if (page === 'favorite') loadFavorites();
    else if (page === 'profile') loadCurrentUserProfile();
    else if (page === 'home') loadWorkspaceSummary();
}

function switchTab(tab) {
    navigateTo(tab);
}

function updateTabBar(page) {
    document.querySelectorAll('.tab-item').forEach(item => item.classList.remove('active'));
    const tabMap = { 'home': 0, 'upload': 1, 'search': 2, 'profile': 3 };
    if (tabMap[page] !== undefined) {
        document.querySelectorAll('.tab-item')[tabMap[page]].classList.add('active');
    }
}

function switchUploadMode(mode) {
    document.querySelectorAll('.upload-tab').forEach(tab => tab.classList.remove('active'));
    if (mode === 'analyze') {
        document.querySelector('.upload-tab:first-child').classList.add('active');
        document.getElementById('analyzeMode').style.display = 'block';
        document.getElementById('compareMode').style.display = 'none';
    } else {
        document.querySelector('.upload-tab:last-child').classList.add('active');
        document.getElementById('analyzeMode').style.display = 'none';
        document.getElementById('compareMode').style.display = 'block';
    }
}

let uploadType = 'single';

function triggerUpload(type) {
    uploadType = type;
    document.getElementById('fileInput').click();
}

async function handleFileUpload(event) {
    const file = event.target.files[0];
    if (!file) return;

    if (uploadType === 'single') {
        await analyzeDocument(file);
    } else if (uploadType === 'docA') {
        window.docAFile = file;
        document.querySelector('#compareMode .upload-compare-zone:first-child .upload-text').textContent = file.name;
    } else if (uploadType === 'docB') {
        window.docBFile = file;
        document.querySelector('#compareMode .upload-compare-zone:last-child .upload-text').textContent = file.name;
    }
    event.target.value = '';
}

async function analyzeDocument(file) {
    const formData = new FormData();
    formData.append('file', file);
    showLoading('正在生成法务审查报告...');

    try {
        const response = await apiFetch('/api/document/analyze', { method: 'POST', body: formData });
        const result = await response.json();
        showAnalysisResult(result);
        await Promise.all([loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        hideLoading();
        alert('分析失败: ' + error.message);
    }
}

async function compareDocuments() {
    if (!window.docAFile || !window.docBFile) { alert('请先上传两份文档'); return; }

    const formData = new FormData();
    formData.append('file_a', window.docAFile);
    formData.append('file_b', window.docBFile);
    showLoading('正在生成条款对比结果...');

    try {
        const response = await apiFetch('/api/document/compare', { method: 'POST', body: formData });
        const result = await response.json();
        showComparisonResult(result);
        await Promise.all([loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        hideLoading();
        alert('比较失败: ' + error.message);
    }
}

function showLoading(message = '处理中...') {
    const overlay = document.createElement('div');
    overlay.id = 'loadingOverlay';
    overlay.style.cssText = 'position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);display:flex;align-items:center;justify-content:center;z-index:9999;';
    overlay.innerHTML = `<div class="loading-spinner"></div><span style="color:white;margin-left:15px;">${message}</span>`;
    document.body.appendChild(overlay);
}

function hideLoading() {
    const overlay = document.getElementById('loadingOverlay');
    if (overlay) overlay.remove();
}

async function saveFavorite(itemType, itemId, title = '', summary = '') {
    const response = await apiFetch('/api/user/favorites', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
            item_type: itemType,
            item_id: itemId,
            title,
            summary,
        }),
    });
    return response.json();
}

async function removeFavoriteById(favoriteId) {
    await apiFetch(`/api/user/favorites/${favoriteId}`, { method: 'DELETE' });
}

async function getFavorites(itemType = null) {
    const query = itemType && itemType !== 'all' ? `?item_type=${encodeURIComponent(itemType)}` : '';
    const response = await apiFetch(`/api/user/favorites${query}`);
    return response.json();
}

function getRiskStats(risks = []) {
    return risks.reduce((acc, risk) => {
        const level = risk.level || 'medium';
        acc[level] = (acc[level] || 0) + 1;
        return acc;
    }, { high: 0, medium: 0, low: 0 });
}

function getOverallRiskLevel(risks = []) {
    if (risks.some(risk => risk.level === 'high')) return 'high';
    if (risks.some(risk => risk.level === 'medium')) return 'medium';
    return 'low';
}

function getOverallRiskLabel(level) {
    if (level === 'high') return '高风险';
    if (level === 'medium') return '中风险';
    return '低风险';
}

function getOverallScore(risks = []) {
    const penalty = risks.reduce((total, risk) => {
        if (risk.level === 'high') return total + 25;
        if (risk.level === 'medium') return total + 12;
        return total + 5;
    }, 0);
    return Math.max(20, 100 - penalty);
}

async function toggleCurrentAnalysisFavorite() {
    const report = window.currentAnalysisReport;
    if (!report?.id) {
        alert('当前报告暂不可收藏');
        return;
    }

    try {
        const favorites = await getFavorites('analysis');
        const existing = favorites.find(item => item.item_id === report.id);
        if (existing) {
            await removeFavoriteById(existing.id);
            alert('已取消收藏报告');
        } else {
            await saveFavorite('analysis', report.id, report.document_name || '分析报告', report.summary || '');
            alert('报告已收藏');
        }
        await Promise.all([loadFavorites(), loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        alert(`收藏失败：${error.message}`);
    }
}

function showAnalysisResult(data) {
    hideLoading();
    window.currentAnalysisReport = data;
    document.getElementById('reportFileName').textContent = data.document_name;
    document.getElementById('reportTime').textContent = `分析时间: ${new Date().toLocaleString()}`;

    const riskStats = getRiskStats(data.risks || []);
    const overallLevel = data.overall_risk_level || getOverallRiskLevel(data.risks || []);
    const overallScore = data.overall_score || getOverallScore(data.risks || []);
    const overallPanel = document.getElementById('reportOverallPanel');
    if (overallPanel) {
        overallPanel.innerHTML = `
            <div class="report-overall-card ${overallLevel}">
                <div>
                    <div class="report-overall-label">总体风险等级</div>
                    <div class="report-overall-level">${getOverallRiskLabel(overallLevel)}</div>
                </div>
                <div class="report-overall-score-block">
                    <div class="report-overall-label">合规评分</div>
                    <div class="report-overall-score">${overallScore}</div>
                </div>
            </div>
        `;
    }

    const reportSummary = document.getElementById('reportSummaryCards');
    if (reportSummary) {
        reportSummary.innerHTML = `
            <div class="workspace-stat-card compact danger">
                <div class="workspace-stat-label">高风险</div>
                <div class="workspace-stat-value">${riskStats.high || 0}</div>
            </div>
            <div class="workspace-stat-card compact warning">
                <div class="workspace-stat-label">中风险</div>
                <div class="workspace-stat-value">${riskStats.medium || 0}</div>
            </div>
            <div class="workspace-stat-card compact success">
                <div class="workspace-stat-label">低风险</div>
                <div class="workspace-stat-value">${riskStats.low || 0}</div>
            </div>
        `;
    }

    const container = document.getElementById('reportRiskContainer');
    container.innerHTML = '';

    const riskGroups = {
        high: { label: '高风险', class: 'tag-high', headerClass: 'risk-header-high', items: [] },
        medium: { label: '中风险', class: 'tag-medium', headerClass: 'risk-header-medium', items: [] },
        low: { label: '低风险', class: 'tag-low', headerClass: 'risk-header-low', items: [] }
    };

    (data.risks || []).forEach(risk => {
        const level = risk.level || 'medium';
        if (riskGroups[level]) riskGroups[level].items.push(risk);
    });

    Object.entries(riskGroups).forEach(([, group]) => {
        if (group.items.length === 0) return;
        const section = document.createElement('div');
        section.className = 'risk-section';
        section.innerHTML = `
            <div class="risk-header ${group.headerClass}">
                <span class="tag ${group.class}">${group.label}</span>
                <span class="risk-count">(${group.items.length})</span>
            </div>
            <div class="risk-items">
                ${group.items.map(risk => `
                    <div class="risk-item">
                        <div class="risk-item-title">${risk.title}</div>
                        ${risk.description ? `<div class="risk-item-desc">${risk.description}</div>` : ''}
                        ${risk.location ? `<div class="risk-item-location">位置：${risk.location}</div>` : ''}
                        <div class="risk-item-basis" onclick="toggleBasis(this)">
                            <span>▸</span> 法律依据与建议
                        </div>
                        <div class="risk-item-basis-content">
                            ${(risk.legal_basis || []).join('<br>') || '暂无法律依据'}
                            ${risk.suggestion ? '<br><br><strong>建议：</strong>' + risk.suggestion : ''}
                        </div>
                    </div>
                `).join('')}
            </div>
        `;
        container.appendChild(section);
    });

    const summaryContainer = document.getElementById('reportSummaryText');
    summaryContainer.innerHTML = data.summary
        ? `<div class="report-summary-box"><div class="report-summary-title">结论摘要</div><div class="report-summary-content">${data.summary}</div></div>`
        : '<div class="report-summary-box"><div class="report-summary-title">结论摘要</div><div class="report-summary-content">暂无总结</div></div>';

    navigateTo('report');
}

function showComparisonResult(data) {
    hideLoading();
    window.currentComparisonReport = data;
    const compareHeader = document.getElementById('compareHeaderTitle');
    if (compareHeader) {
        compareHeader.textContent = `📄 ${data.document_a} ↔ ${data.document_b}`;
    }

    const compareContent = document.getElementById('compareResultContainer');
    compareContent.innerHTML = '';

    (data.changes || []).forEach(change => {
        const div = document.createElement('div');
        div.style.cssText = 'margin-bottom:15px;';
        div.innerHTML = `
            <div class="compare-container single">
                <div class="compare-box">
                    <div class="compare-box-header">原文</div>
                    <div class="compare-box-content">${change.original || '无'}</div>
                </div>
                <div class="compare-box">
                    <div class="compare-box-header">修改后</div>
                    <div class="compare-box-content">${change.modified || '无'}</div>
                </div>
            </div>
        `;
        compareContent.appendChild(div);
    });

    if (!data.changes?.length) {
        compareContent.innerHTML = '<div class="empty-card">暂无结构化差异内容。</div>';
    }

    const summary = document.getElementById('compareSummary');
    if (summary) {
        summary.innerHTML = `
            <div class="report-summary-title">对比结论</div>
            <div class="report-summary-content">${data.summary || '暂无对比总结'}</div>
        `;
    }

    const stats = document.getElementById('compareStats');
    if (stats) {
        const count = (data.changes || []).length;
        stats.innerHTML = `
            <span>差异项：${count}</span>
            <span>状态：${data.status || 'completed'}</span>
            <span>生成时间：${formatDateTime(data.created_at || new Date().toISOString())}</span>
        `;
    }

    navigateTo('compare');
}

async function toggleCurrentComparisonFavorite() {
    const comparison = window.currentComparisonReport;
    if (!comparison?.id) {
        alert('当前对比结果暂不可收藏');
        return;
    }

    try {
        const favorites = await getFavorites('comparison');
        const existing = favorites.find(item => item.item_id === comparison.id);
        if (existing) {
            await removeFavoriteById(existing.id);
            alert('已取消收藏对比结果');
        } else {
            await saveFavorite(
                'comparison',
                comparison.id,
                `${comparison.document_a || '文档A'} vs ${comparison.document_b || '文档B'}`,
                comparison.summary || ''
            );
            alert('对比结果已收藏');
        }
        await Promise.all([loadFavorites(), loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        alert(`收藏失败：${error.message}`);
    }
}

function toggleBasis(element) {
    const content = element.nextElementSibling;
    const arrow = element.querySelector('span');
    if (content.classList.contains('show')) {
        content.classList.remove('show');
        arrow.textContent = '▸';
    } else {
        content.classList.add('show');
        arrow.textContent = '▾';
    }
}

let searchTimeout = null;

async function loadAllLaws() {
    try {
        const response = await apiFetch('/api/search/law?q=');
        displaySearchResults(await response.json());
    } catch (error) {
        console.error('Error:', error);
    }
}

async function searchLaw() {
    const query = document.getElementById('lawSearchInput').value;
    if (searchTimeout) clearTimeout(searchTimeout);

    if (!query.trim()) {
        loadAllLaws();
        return;
    }

    searchTimeout = setTimeout(async () => {
        try {
            const response = await apiFetch(`/api/search/law?q=${encodeURIComponent(query)}`);
            displaySearchResults(await response.json());
        } catch (error) {
            console.error('Search error:', error);
        }
    }, 300);
}

function getShortNum(articleNumber) {
    const match = articleNumber.match(/第([\d一二三四五六七八九十百千]+)条/);
    if (match) return match[1];
    return articleNumber;
}

function displaySearchResults(results) {
    const container = document.getElementById('searchResults');
    if (results.length === 0) {
        container.innerHTML = '<div style="text-align:center;color:var(--text-secondary);padding:40px;">未找到相关法条</div>';
        return;
    }
    container.innerHTML = '<div class="law-table">' + results.map(item => `
        <div class="law-row" onclick="viewLawDetail('${item.id}')">
            <div class="law-num">${getShortNum(item.article_number)}</div>
            <div class="law-content">
                <div class="law-title">${item.title || item.article_number}</div>
                <div class="law-preview">${item.content.substring(0, 80)}...</div>
                <div class="law-meta">📜${item.judicial_interpretations?.length || 0} ⚖️${item.related_cases?.length || 0}</div>
            </div>
        </div>
    `).join('') + '</div>';
}

async function viewLawDetail(articleId) {
    try {
        const response = await apiFetch(`/api/search/law/${articleId}`);
        const article = await response.json();

        document.getElementById('lawDetailTitle').textContent = article.title || article.article_number;
        document.getElementById('lawDetailPath').textContent = `${article.law_name} > ${article.article_number}`;
        document.getElementById('lawDetailContent').textContent = article.content;

        const interp = article.judicial_interpretations || [];
        let interpHtml = '<div style="font-size:14px;font-weight:600;margin-bottom:10px;color:var(--text-secondary);">📜 司法解释 (' + interp.length + ')</div>';
        interp.forEach(item => {
            const url = `https://www.baidu.com/s?wd=${encodeURIComponent(item)}`;
            interpHtml += `<div class="law-detail-link" onclick="window.open('${url}', '_blank')"><span>→</span> ${item}</div>`;
        });
        document.getElementById('lawInterpretations').innerHTML = interpHtml;

        const cases = article.related_cases || [];
        let casesHtml = '<div style="font-size:14px;font-weight:600;margin-bottom:10px;color:var(--text-secondary);">⚖️ 相关判例 (' + cases.length + ')</div>';
        cases.forEach(item => {
            const url = `https://wenshu.court.gov.cn/website/wenshu/181107ANFZ0BXSK4/index.html?docId=${encodeURIComponent(item)}`;
            casesHtml += `<div class="law-detail-link" onclick="window.open('${url}', '_blank')"><span>→</span> ${item}</div>`;
        });
        document.getElementById('lawCases').innerHTML = casesHtml;

        window.currentArticle = article;
        navigateTo('law-detail');
    } catch (error) {
        console.error('Error:', error);
        alert('加载法条详情失败');
    }
}

async function toggleCurrentLawFavorite() {
    if (!window.currentArticle || !window.currentArticle.id) {
        alert('当前法条信息不完整，暂时无法收藏');
        return;
    }

    try {
        const favorites = await getFavorites('law');
        const existing = favorites.find(f => f.item_id === window.currentArticle.id);
        if (existing) {
            await removeFavoriteById(existing.id);
            alert('已取消收藏');
        } else {
            await saveFavorite('law', window.currentArticle.id, window.currentArticle.title || window.currentArticle.article_number || '法条', window.currentArticle.content?.slice(0, 60) || '');
            alert('收藏成功');
        }
        await Promise.all([loadFavorites(), loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        alert(`收藏失败：${error.message}`);
    }
}

async function loadFavorites(type = 'all') {
    const container = document.querySelector('#page-favorite .favorite-list');
    const tabs = document.querySelectorAll('.favorite-tab');
    tabs.forEach(tab => tab.classList.toggle('active', tab.dataset.type === type));

    try {
        const favorites = await getFavorites(type);
        if (favorites.length === 0) {
            container.innerHTML = '<div style="text-align:center;color:var(--text-secondary);padding:40px;">暂无收藏</div>';
            return;
        }

        container.innerHTML = favorites.map(f => {
            const openAction = f.item_type === 'law'
                ? `viewLawDetail('${f.item_id}')`
                : f.item_type === 'chat'
                    ? `openChat('${f.item_id}')`
                    : f.item_type === 'analysis'
                        ? `openAnalysisReport('${f.item_id}')`
                        : f.item_type === 'comparison'
                            ? `openComparisonResult('${f.item_id}')`
                            : 'void(0)';
            const metaLabel = getFavoriteTypeLabel(f.item_type);

            return `
                <div class="favorite-card">
                    <div class="favorite-card-main" onclick="${openAction}">
                        <div class="favorite-card-badge">${metaLabel}</div>
                        <div class="favorite-card-title">${f.title || metaLabel}</div>
                        <div class="favorite-card-summary">${f.summary || '已加入你的法务工作台收藏夹，便于后续复查与追踪。'}</div>
                        <div class="favorite-card-meta">收藏于 ${formatDateTime(f.created_at)}</div>
                    </div>
                    <button class="mini-action-btn" onclick="deleteFavorite('${f.id}')">移除</button>
                </div>
            `;
        }).join('');
    } catch (error) {
        container.innerHTML = `<div style="text-align:center;color:var(--danger);padding:40px;">加载收藏失败：${error.message}</div>`;
    }
}

function getFavoriteTypeLabel(type) {
    if (type === 'law') return '法条收藏';
    if (type === 'chat') return 'AI 对话收藏';
    if (type === 'analysis') return '审查报告收藏';
    if (type === 'comparison') return '对比结果收藏';
    return '业务收藏';
}

async function deleteFavorite(favoriteId) {
    try {
        await removeFavoriteById(favoriteId);
        await Promise.all([loadFavorites(), loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        alert(`移除失败：${error.message}`);
    }
}

function shareLaw() {
    if (navigator.share) {
        navigator.share({ title: window.currentArticle?.title || '法条分享', text: window.currentArticle?.content || '', url: window.location.href });
    } else {
        alert('复制链接功能开发中');
    }
}

function askAI(question) {
    navigateTo('home');
    setTimeout(() => {
        document.getElementById('homeChatInput').value = question;
        startNewChat();
    }, 100);
}

async function startNewChat() {
    const input = document.getElementById('homeChatInput');
    const message = input.value.trim();
    if (!message) return;

    try {
        const response = await apiFetch('/api/chat/sessions', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ title: message.substring(0, 20) })
        });
        const session = await response.json();
        currentSessionId = session.id;
        input.value = '';
        navigateTo('chat');
        document.getElementById('chatInput').value = message;
        await sendMessage();
        await Promise.all([loadRecentChats(), loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        console.error('Error:', error);
        alert('创建会话失败');
    }
}

async function openChat(sessionId) {
    currentSessionId = sessionId;
    navigateTo('chat');

    try {
        const response = await apiFetch(`/api/chat/sessions/${sessionId}`);
        const session = await response.json();
        const container = document.getElementById('chatMessages');
        container.innerHTML = session.messages.map(msg => `
            <div class="chat-message ${msg.role}">
                <div class="chat-bubble">${formatMessage(msg.content)}</div>
                <span class="chat-time">${new Date(msg.created_at).toLocaleTimeString()}</span>
            </div>
        `).join('');
        container.scrollTop = container.scrollHeight;
    } catch (error) {
        console.error('Error:', error);
        alert('加载对话失败');
    }
}

function formatMessage(content) {
    return content
        .replace(/\n/g, '<br>')
        .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
        .replace(/`(.*?)`/g, '<code style="background:var(--bg-primary);padding:2px 4px;border-radius:3px;">$1</code>');
}

async function sendMessage() {
    const input = document.getElementById('chatInput');
    const message = input.value.trim();
    if (!message) return;

    if (!currentSessionId) {
        try {
            const response = await apiFetch('/api/chat/sessions', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ title: message.substring(0, 20) })
            });
            const session = await response.json();
            currentSessionId = session.id;
        } catch (error) {
            console.error('Error:', error);
            return;
        }
    }

    const container = document.getElementById('chatMessages');
    container.innerHTML += `
        <div class="chat-message user">
            <div class="chat-bubble">${formatMessage(message)}</div>
            <span class="chat-time">${new Date().toLocaleTimeString()}</span>
        </div>
    `;
    input.value = '';
    container.scrollTop = container.scrollHeight;

    const loadingDiv = document.createElement('div');
    loadingDiv.className = 'chat-message assistant';
    loadingDiv.innerHTML = '<div class="chat-bubble"><div class="loading-spinner" style="width:20px;height:20px;"></div></div>';
    container.appendChild(loadingDiv);
    container.scrollTop = container.scrollHeight;

    try {
        const response = await apiFetch(`/api/chat/sessions/${currentSessionId}/messages`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ role: 'user', content: message })
        });

        const result = await response.json();
        loadingDiv.remove();

        container.innerHTML += `
            <div class="chat-message assistant">
                <div class="chat-bubble">${formatMessage(result.content)}</div>
                <span class="chat-time">${new Date().toLocaleTimeString()}</span>
            </div>
        `;
        container.scrollTop = container.scrollHeight;
        await Promise.all([loadRecentChats(), loadHistory(), loadWorkspaceSummary(), loadCurrentUserProfile()]);
    } catch (error) {
        console.error('Error:', error);
        loadingDiv.remove();
        container.innerHTML += `
            <div class="chat-message assistant">
                <div class="chat-bubble">抱歉，请求失败，请稍后重试。</div>
                <span class="chat-time">${new Date().toLocaleTimeString()}</span>
            </div>
        `;
    }
}

async function loadRecentChats() {
    try {
        const response = await apiFetch('/api/chat/sessions?limit=3');
        const sessions = await response.json();
        const container = document.getElementById('recentChats');

        if (sessions.length === 0) {
            container.innerHTML = '<div class="empty-card">暂无对话记录，试试输入一个法律问题开始。</div>';
            return;
        }
        container.innerHTML = sessions.map(s => `
            <div class="workspace-list-card" onclick="openChat('${s.id}')">
                <div>
                    <div class="workspace-list-title">${s.title}</div>
                    <div class="workspace-list-meta">最近更新：${formatDateTime(s.updated_at)}</div>
                </div>
                <span class="workspace-list-arrow">→</span>
            </div>
        `).join('');
    } catch (error) {
        console.error('Error:', error);
    }
}

function setHistoryFilter(type, element) {
    currentHistoryFilter = type;
    document.querySelectorAll('[data-history-filter]').forEach(item => item.classList.remove('active'));
    if (element) element.classList.add('active');
    const query = document.querySelector('#page-history .search-box')?.value || '';
    if (query.trim()) {
        searchHistory(query);
    } else {
        loadHistory();
    }
}

function groupHistoryByDate(items, dateField = 'updated_at') {
    const groups = {};
    const today = new Date().toDateString();
    const yesterday = new Date(Date.now() - 86400000).toDateString();

    items.forEach(item => {
        const rawDate = item[dateField] || item.created_at;
        const date = new Date(rawDate).toDateString();
        const label = date === today ? '今天' : date === yesterday ? '昨天' : formatDate(rawDate);
        if (!groups[label]) groups[label] = [];
        groups[label].push(item);
    });
    return groups;
}

function renderHistorySections(groups) {
    let html = '';
    Object.entries(groups).forEach(([date, items]) => {
        html += `<div class="history-date">${date}</div>`;
        items.forEach(item => {
            const openAction = item.history_type === 'analysis'
                ? `openAnalysisReport('${item.id}')`
                : item.history_type === 'comparison'
                    ? `openComparisonResult('${item.id}')`
                    : `openChat('${item.id}')`;
            const icon = item.history_type === 'analysis' ? '📄' : item.history_type === 'comparison' ? '🆚' : '💬';
            const metaTime = formatTime(item.updated_at || item.created_at);
            const subtitle = item.history_type === 'analysis'
                ? (item.status === 'completed' ? '审查报告' : `审查中 · ${item.status}`)
                : item.history_type === 'comparison'
                    ? '文档对比'
                    : 'AI 对话';
            const title = item.history_type === 'comparison'
                ? `${item.document_a} vs ${item.document_b}`
                : item.document_name || item.title;

            html += `
                <div class="history-item" onclick="${openAction}">
                    <div class="history-item-info">
                        <span class="history-item-icon">${icon}</span>
                        <div>
                            <div class="history-item-title">${title}</div>
                            <div class="history-item-meta">${subtitle} · ${metaTime}</div>
                        </div>
                    </div>
                </div>
            `;
        });
    });
    return html;
}

async function loadHistory() {
    try {
        const response = await apiFetch(`/api/user/history?limit=100${currentHistoryFilter !== 'all' ? `&type=${currentHistoryFilter}` : ''}`);
        const items = await response.json();
        const container = document.getElementById('historyList');

        if (items.length === 0) {
            container.innerHTML = '<div style="text-align:center;color:var(--text-secondary);padding:40px;">暂无历史记录</div>';
            return;
        }

        const normalized = items.map(item => ({
            ...item,
            history_type: item.type,
            document_name: item.type === 'analysis' ? item.title : item.document_name,
            title: item.type === 'chat' ? item.title : item.title,
            updated_at: item.updated_at || item.created_at,
        }));

        const grouped = groupHistoryByDate(normalized);
        container.innerHTML = renderHistorySections(grouped);
    } catch (error) {
        console.error('Error:', error);
    }
}

function groupByDate(items) {
    return groupHistoryByDate(items);
}

function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}月${date.getDate()}日`;
}

function formatTime(dateStr) {
    const date = new Date(dateStr);
    return `${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
}

function formatDateTime(dateStr) {
    const date = new Date(dateStr);
    return `${date.getMonth() + 1}月${date.getDate()}日 ${date.getHours().toString().padStart(2, '0')}:${date.getMinutes().toString().padStart(2, '0')}`;
}

async function loadTemplates(category = 'all', keyword = '') {
    try {
        currentTemplateCategory = category || 'all';
        const searchInput = document.getElementById('templateSearchInput');
        const searchKeyword = keyword !== undefined ? keyword : (searchInput?.value || '');
        const query = new URLSearchParams();
        if (currentTemplateCategory && currentTemplateCategory !== 'all') query.set('category', currentTemplateCategory);
        if (searchKeyword && searchKeyword.trim()) query.set('keyword', searchKeyword.trim());

        const [templatesResponse, categoriesResponse] = await Promise.all([
            apiFetch(`/api/templates${query.toString() ? `?${query.toString()}` : ''}`),
            apiFetch('/api/templates/categories/list'),
        ]);

        const [templates, categories] = await Promise.all([
            templatesResponse.json(),
            categoriesResponse.json(),
        ]);

        const filters = document.getElementById('templateCategoryFilters');
        if (filters) {
            const allCategories = ['all', ...categories];
            filters.innerHTML = allCategories.map(item => `
                <span class="filter-tag ${item === currentTemplateCategory ? 'active' : ''}" onclick="loadTemplates('${item}', document.getElementById('templateSearchInput')?.value || '')">${item === 'all' ? '全部' : item}</span>
            `).join('');
        }

        if (searchInput && searchInput.value !== searchKeyword) {
            searchInput.value = searchKeyword;
        }

        const container = document.querySelector('#page-template .template-list');
        container.innerHTML = templates.length ? templates.map(t => `
            <div class="template-item" onclick="useTemplate('${t.id}', '${String(t.name).replace(/'/g, "&#39;")}')">
                <div class="template-info">
                    <span class="template-icon">📄</span>
                    <div>
                        <div class="template-name">${t.name}</div>
                        <div class="template-meta">${t.description || `${t.category}类模板`} · 使用 ${t.usage_count || 0} 次</div>
                    </div>
                </div>
                <span class="template-action">点击使用 →</span>
            </div>
        `).join('') : '<div class="empty-state">暂无匹配模板</div>';
    } catch (error) {
        console.error('Error:', error);
    }
}

async function useTemplate(templateId, templateName) {
    try {
        const response = await apiFetch(`/api/templates/${templateId}`);
        const template = await response.json();
        const blob = new Blob([template.content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = `${templateName}.txt`;
        a.click();
        URL.revokeObjectURL(url);
        alert(`"${templateName}"已下载，可以上传进行分析`);
    } catch (error) {
        console.error('Error:', error);
        alert('下载失败');
    }
}

async function searchHistory(query) {
    if (!query.trim()) { loadHistory(); return; }

    try {
        const response = await apiFetch(`/api/user/history?limit=100${currentHistoryFilter !== 'all' ? `&type=${currentHistoryFilter}` : ''}`);
        const items = await response.json();
        const container = document.getElementById('historyList');

        const normalized = items.map(item => ({
            ...item,
            history_type: item.type,
            document_name: item.type === 'analysis' ? item.title : item.document_name,
            updated_at: item.updated_at || item.created_at,
        }));

        const filtered = normalized.filter(item => {
            const title = item.history_type === 'comparison'
                ? `${item.document_a || ''} ${item.document_b || ''}`
                : item.document_name || item.title || '';
            return title.toLowerCase().includes(query.toLowerCase());
        });

        if (filtered.length === 0) {
            container.innerHTML = '<div style="text-align:center;color:var(--text-secondary);padding:40px;">未找到匹配记录</div>';
            return;
        }

        const grouped = groupHistoryByDate(filtered);
        container.innerHTML = renderHistorySections(grouped);
    } catch (error) {
        console.error('Error:', error);
    }
}

async function loadWorkspaceSummary() {
    try {
        const response = await apiFetch('/api/user/workspace');
        const workspace = await response.json();
        renderWorkspaceSummary(workspace);
    } catch (error) {
        console.error('load workspace error', error);
    }
}

function renderWorkspaceSummary(workspace) {
    if (!workspace) return;

    const recentReports = document.getElementById('recentReports');
    const recentComparisons = document.getElementById('recentComparisons');

    if (recentReports) {
        if (!workspace.recent_analyses?.length) {
            recentReports.innerHTML = '<div class="empty-card">暂无审查报告，上传一份合同开始生成。</div>';
        } else {
            recentReports.innerHTML = workspace.recent_analyses.map(item => `
                <div class="workspace-list-card" onclick="openAnalysisReport('${item.id}')">
                    <div>
                        <div class="workspace-list-title">${item.document_name}</div>
                        <div class="workspace-list-meta">${item.status === 'completed' ? '已完成' : item.status} · ${formatDateTime(item.created_at)}</div>
                    </div>
                    <span class="workspace-list-arrow">→</span>
                </div>
            `).join('');
        }
    }

    if (recentComparisons) {
        if (!workspace.recent_comparisons?.length) {
            recentComparisons.innerHTML = '<div class="empty-card">暂无对比记录，可上传两份文档进行差异审阅。</div>';
        } else {
            recentComparisons.innerHTML = workspace.recent_comparisons.map(item => `
                <div class="workspace-list-card" onclick="openComparisonResult('${item.id}')">
                    <div>
                        <div class="workspace-list-title">${item.document_a} vs ${item.document_b}</div>
                        <div class="workspace-list-meta">${formatDateTime(item.created_at)}</div>
                    </div>
                    <span class="workspace-list-arrow">→</span>
                </div>
            `).join('');
        }
    }
}

async function openAnalysisReport(analysisId) {
    try {
        const response = await apiFetch(`/api/document/analysis/${analysisId}`);
        const analysis = await response.json();
        showAnalysisResult(analysis);
    } catch (error) {
        alert(`加载报告失败：${error.message}`);
    }
}

async function openComparisonResult(comparisonId) {
    try {
        const response = await apiFetch(`/api/document/comparisons/${comparisonId}`);
        const comparison = await response.json();
        showComparisonResult(comparison);
    } catch (error) {
        alert(`加载对比结果失败：${error.message}`);
    }
}

function exportComparisonResult() {
    const comparison = window.currentComparisonReport;
    if (!comparison) {
        alert('当前没有可导出的对比结果');
        return;
    }

    const lines = [
        `对比文档A：${comparison.document_a || '未命名文档A'}`,
        `对比文档B：${comparison.document_b || '未命名文档B'}`,
        `用户ID：${currentUser?.id || '未知'}`,
        `导出时间：${new Date().toLocaleString()}`,
        '',
        '【差异明细】'
    ];

    (comparison.changes || []).forEach((change, index) => {
        lines.push(`${index + 1}. 类型：${change.type || 'modify'}`);
        lines.push(`原文：${change.original || '无'}`);
        lines.push(`修改后：${change.modified || '无'}`);
        lines.push(`位置：${change.location || '未提供'}`);
        lines.push('');
    });

    lines.push('【对比总结】');
    lines.push(comparison.summary || '无');

    const blob = new Blob([lines.join('\n')], { type: 'text/plain;charset=utf-8' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `${(comparison.document_a || 'comparison-result').replace(/\.[^.]+$/, '')}-对比结果.txt`;
    a.click();
    URL.revokeObjectURL(url);
}

function shareComparisonResult() {
    const comparison = window.currentComparisonReport;
    if (!comparison) {
        alert('当前没有可分享的对比结果');
        return;
    }

    const shareText = `${comparison.document_a || '文档A'} vs ${comparison.document_b || '文档B'}\n${comparison.summary || '暂无对比总结'}`;
    if (navigator.share) {
        navigator.share({
            title: '文档对比结果',
            text: shareText,
            url: window.location.href,
        });
    } else if (navigator.clipboard?.writeText) {
        navigator.clipboard.writeText(shareText)
            .then(() => alert('对比结果摘要已复制到剪贴板'))
            .catch(() => alert('复制失败，请手动分享'));
    } else {
        alert('当前环境不支持分享，请手动复制内容');
    }
}

function exportReport() {
    const report = window.currentAnalysisReport;
    if (!report) {
        alert('当前没有可导出的分析报告');
        return;
    }

    const lines = [
        `文档名称：${report.document_name || '未命名文档'}`,
        `用户ID：${currentUser?.id || '未知'}`,
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

document.addEventListener('DOMContentLoaded', async function() {
    await checkLogin();
    document.getElementById('lawSearchInput')?.addEventListener('input', searchLaw);
    document.getElementById('chatInput')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') sendMessage();
    });
    document.getElementById('homeChatInput')?.addEventListener('keypress', function(e) {
        if (e.key === 'Enter') startNewChat();
    });
});
