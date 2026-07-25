import { useEffect, useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { EmptyState } from '@/shared/ui/EmptyState';
import { Skeleton } from '@/shared/ui/Skeleton';
import { apiRequest } from '@/shared/api/client';

type HistoryItem = {
  id: string;
  type: 'chat' | 'analysis' | 'comparison';
  title: string | null;
  status?: string;
  created_at: string;
  updated_at?: string | null;
  overall_risk_level?: string;
  overall_score?: number;
  document_a?: string;
  document_b?: string;
};

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch {
    return iso;
  }
}

function TypeIcon({ type }: { type: string }) {
  return <div className="text-2xl">{type === 'analysis' ? '📋' : type === 'comparison' ? '📳' : '💰'}</div>;
}

function TypeLabel({ type }: { type: string }) {
  const label = type === 'analysis' ? '分析' : type === 'comparison' ? '对比' : '问答';
  return <Badge tone="neutral">{label}</Badge>;
}

export function HistoryPage() {
  const [items, setItems] = useState<HistoryItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState<string>('');
  const [deleting, setDeleting] = useState<string | null>(null);
  const [showExportFor, setShowExportFor] = useState<string | null>(null);
  const navigate = useNavigate();

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const query = filter ? '?type=' + filter : '';
        const result = await apiRequest<HistoryItem[]>('/api/user/history' + query);
        if (!cancelled) setItems(result);
      } catch {
        // silent
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [filter]);

  const handleDelete = async (item: HistoryItem) => {
    const key = item.type + '-' + item.id;
    setDeleting(key);
    try {
      const endpoint = item.type === 'chat'
        ? '/api/chat/sessions/' + item.id
        : item.type === 'analysis'
          ? '/api/document/analysis/' + item.id
          : '/api/document/comparisons/' + item.id;
      await apiRequest(endpoint, { method: 'DELETE' });
      setItems((prev) => prev.filter((i) => i.type + '-' + i.id !== key));
    } catch {
      // silent
    } finally {
      setDeleting(null);
    }
  };

  const handleExportHistory = async (item: HistoryItem, format: string) => {
    setShowExportFor(null);
    try {
      let detailUrl = '';
      if (item.type === 'analysis') {
        detailUrl = '/api/document/analysis/' + item.id;
      } else if (item.type === 'comparison') {
        detailUrl = '/api/document/comparisons/' + item.id;
      } else {
        return;
      }

      const token = localStorage.getItem('legal_ai.access_token');
      const headers: Record<string, string> = {};
      if (token) headers['Authorization'] = 'Bearer ' + token;

      const detailResp = await fetch(detailUrl, { headers });
      if (!detailResp.ok) throw new Error('获取详情失败');
      const detail = await detailResp.json();

      const body: Record<string, unknown> = {
        document_name: item.title || item.document_a || '未知文档',
        summary: detail.summary || '',
        risks: detail.risks || detail.changes || [],
        overall_risk_level: detail.overall_risk_level || item.overall_risk_level || null,
        overall_score: detail.overall_score ?? item.overall_score ?? null,
        format,
      };

      const exportHeaders: Record<string, string> = { 'Content-Type': 'application/json' };
      if (token) exportHeaders['Authorization'] = 'Bearer ' + token;

      const exportResp = await fetch('/api/document/export', {
        method: 'POST',
        headers: exportHeaders,
        body: JSON.stringify(body),
      });

      if (!exportResp.ok) {
        const errData = await exportResp.json().catch(() => null);
        throw new Error(errData?.detail || '导出失败: ' + exportResp.status);
      }

      const blob = await exportResp.blob();
      const url = URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      const ext = format === 'docx' ? '.docx' : format === 'pdf' ? '.pdf' : '.txt';
      const docName = item.title || item.document_a || '未知文档';
      a.download = '分析报告_' + docName + '_' + Date.now() + ext;
      a.click();
      URL.revokeObjectURL(url);
    } catch (err) {
      alert(err instanceof Error ? err.message : '导出失败');
    }
  };

  const filters = [
    { key: '', label: '全部' },
    { key: 'analysis', label: '分析' },
    { key: 'comparison', label: '对比' },
    { key: 'chat', label: '问答' },
  ];

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">历史记录</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">我的分析历史</h1>
        <p className="mt-1 text-sm text-slate-500">所有合同分析、对比与问答记录。</p>
      </div>

      <div className="flex gap-2">
        {filters.map((f) => (
          <button
            key={f.key}
            onClick={() => { setFilter(f.key); setLoading(true); }}
            className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
              filter === f.key ? 'bg-brand-600 text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
            }`}
          >
            {f.label}
          </button>
        ))}
      </div>

      <Card>
        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : items.length > 0 ? (
          <div className="space-y-3">
            {items.map((item) => {
              const detailPath = item.type === 'chat'
                ? '/chat?session=' + item.id
                : item.type === 'analysis'
                  ? '/analyses/' + item.id
                  : '/comparisons/' + item.id;
              return (
              <div key={item.type + '-' + item.id} className="flex items-center justify-between rounded-2xl border border-slate-100 p-4 transition hover:border-brand-200 hover:bg-brand-50/20">
                <div className="flex items-center gap-4 cursor-pointer flex-1 min-w-0" onClick={() => navigate(detailPath)}>
                  <TypeIcon type={item.type} />
                  <div className="min-w-0">
                    <div className="font-medium text-slate-800 truncate">
                      {item.title || (item.type === 'comparison' ? (item.document_a || '') + ' vs ' + (item.document_b || '') : '未命名')}
                    </div>
                    <div className="mt-1 flex items-center gap-3 text-sm text-slate-400">
                      <span>{formatDate(item.updated_at || item.created_at)}</span>
                      <TypeLabel type={item.type} />
                      {item.status && (
                        <Badge tone={item.status === 'completed' ? 'success' : 'warning'}>
                          {item.status === 'completed' ? '已完成' : '处理中'}
                        </Badge>
                      )}
                      {item.overall_risk_level && (
                        <Badge tone={item.overall_risk_level === 'high' ? 'warning' : item.overall_risk_level === 'medium' ? 'brand' : 'neutral'}>
                          {item.overall_risk_level === 'high' ? '高风险' : item.overall_risk_level === 'medium' ? '中风险' : '低风险'}
                        </Badge>
                      )}
                      {item.overall_score != null && (
                        <span className="text-xs font-semibold text-brand-600">评分 {item.overall_score}</span>
                      )}
                    </div>
                  </div>
                </div>
                <div className="flex gap-2 shrink-0">
                  <Button variant="ghost" size="sm" onClick={() => navigate(detailPath)}>查看</Button>
                  {item.type !== 'chat' && (
                    <div className="relative">
                      <Button
                        variant="ghost"
                        size="sm"
                        onClick={(e) => { e.stopPropagation(); setShowExportFor(showExportFor === item.type + '-' + item.id ? null : item.type + '-' + item.id); }}
                      >
                        导出 ▾
                      </Button>
                      {showExportFor === item.type + '-' + item.id && (
                        <div className="absolute right-0 mt-1 w-32 rounded-xl border border-slate-200 bg-white shadow-lg z-50 py-1">
                          <button
                            className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"
                            onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'docx'); }}
                          >
                            📄 Word
                          </button>
                          <button
                            className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"
                            onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'pdf'); }}
                          >
                            📑 PDF
                          </button>
                          <button
                            className="w-full px-3 py-1.5 text-left text-xs hover:bg-slate-50 transition"
                            onClick={(e) => { e.stopPropagation(); handleExportHistory(item, 'txt'); }}
                          >
                            📝 TXT
                          </button>
                        </div>
                      )}
                    </div>
                  )}
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500"
                    disabled={deleting === item.type + '-' + item.id}
                    onClick={(e) => { e.stopPropagation(); handleDelete(item); }}
                  >
                    {deleting === item.type + '-' + item.id ? '删除中...' : '删除'}
                  </Button>
                </div>
              </div>
            )})}
          </div>
        ) : (
          <EmptyState
            title="暂无历史记录"
            description={filter ? '该类型下暂无记录' : '开始分析或对比合同后将显示在这里。'}
            action={
              <Link to="/contracts/analyze">
                <Button>开始分析</Button>
              </Link>
            }
          />
        )}
      </Card>
    </PageContainer>
  );
}