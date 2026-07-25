import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { EmptyState } from '@/shared/ui/EmptyState';
import { apiRequest } from '@/shared/api/client';

type Change = {
  type: string;
  original: string;
  modified: string;
  location: string;
};

type ComparisonDetail = {
  id: string;
  document_a: string;
  document_b: string;
  status: string;
  changes: Change[];
  summary: string;
  created_at: string;
  completed_at: string | null;
};

const typeLabel: Record<string, string> = { modify: '修改', add: '新增', delete: '删除' };
const typeTone: Record<string, 'warning' | 'success' | 'neutral'> = { modify: 'warning', add: 'success', delete: 'neutral' };

export function ComparisonDetailPage() {
  const { comparisonId } = useParams();
  const [data, setData] = useState<ComparisonDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await apiRequest<ComparisonDetail>('/api/document/comparisons/' + comparisonId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : '加载失败');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [comparisonId]);

  if (loading) return <PageContainer className="space-y-4"><Skeleton className="h-16" /><Skeleton className="h-64" /></PageContainer>;
  if (error || !data) return <PageContainer><EmptyState title="加载失败" description={error || '对比记录'} action={<Link to="/history"><Button variant="secondary">← 返回历史</Button></Link>} /></PageContainer>;

  return (
    <PageContainer className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Badge tone="brand">文档对比</Badge>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">对比详情</h1>
          <p className="mt-1 text-sm text-slate-500">{data.document_a} vs {data.document_b}</p>
        </div>
        <Link to="/history">
          <Button variant="secondary">← 返回历史</Button>
        </Link>
      </div>

      {data.summary && (
        <Card>
          <h2 className="text-sm font-semibold text-slate-700 mb-2">对比总结</h2>
          <p className="text-sm leading-7 text-slate-600">{data.summary}</p>
        </Card>
      )}

      {data.changes && data.changes.length > 0 ? (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">修改差异（{data.changes.length} 处）</h2>
          {data.changes.map((change, i) => (
            <Card key={i}>
              <div className="flex items-center gap-2 mb-3">
                <Badge tone={typeTone[change.type] || 'neutral'}>{typeLabel[change.type] || change.type}</Badge>
                {change.location && <span className="text-xs text-slate-400">{change.location}</span>}
              </div>
              <div className="grid gap-3 sm:grid-cols-2">
                <div className="rounded-xl bg-red-50 p-3">
                  <div className="text-xs font-medium text-red-600 mb-1">原文</div>
                  <p className="text-sm leading-6 text-slate-700 line-through">{change.original}</p>
                </div>
                <div className="rounded-xl bg-green-50 p-3">
                  <div className="text-xs font-medium text-green-600 mb-1">修改后</div>
                  <p className="text-sm leading-6 text-slate-700">{change.modified}</p>
                </div>
              </div>
            </Card>
          ))})
        </section>
      ) : (
        <EmptyState title="无差异内容" description="两份文档之间未检测到差异。" />
      )}
    </PageContainer>
  );
}