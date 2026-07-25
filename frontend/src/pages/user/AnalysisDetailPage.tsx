import { useEffect, useState } from 'react';
import { useParams, Link } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { EmptyState } from '@/shared/ui/EmptyState';
import { apiRequest } from '@/shared/api/client';

type Risk = {
  level: string;
  title: string;
  description: string;
  location: string;
  legal_basis: string[];
  suggestion: string;
};

type AnalysisDetail = {
  id: string;
  document_name: string;
  status: string;
  risks: Risk[];
  summary: string;
  overall_risk_level?: string;
  overall_score?: number;
  created_at: string;
  completed_at: string | null;
};

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit' });
  } catch { return iso; }
}

const riskLabel: Record<string, string> = { high: '高风险', medium: '中风险', low: '低风险' };
const riskTone: Record<string, 'warning' | 'brand' | 'neutral'> = { high: 'warning', medium: 'brand', low: 'neutral' };

export function AnalysisDetailPage() {
  const { analysisId } = useParams();
  const [data, setData] = useState<AnalysisDetail | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const result = await apiRequest<AnalysisDetail>('/api/document/analysis/' + analysisId);
        if (!cancelled) setData(result);
      } catch (err) {
        if (!cancelled) setError(err instanceof Error ? err.message : '加载失败');
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, [analysisId]);

  if (loading) return <PageContainer className="space-y-4"><Skeleton className="h-16" /><Skeleton className="h-64" /></PageContainer>;
  if (error || !data) return <PageContainer><EmptyState title="加载失败" description={error || '未找到分析记录'} action={<Link to="/history"><Button variant="secondary">← 返回历史</Button></Link>} /></PageContainer>;

  return (
    <PageContainer className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Badge tone="brand">合同分析</Badge>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">{data.document_name || '未命名文档'}</h1>
          <p className="mt-1 text-sm text-slate-500">{formatDate(data.created_at)}</p>
        </div>
        <Link to="/history">
          <Button variant="secondary">← 返回历史</Button>
        </Link>
      </div>

      {data.overall_risk_level && (
        <Card>
          <div className="flex items-center gap-4">
            <Badge tone={riskTone[data.overall_risk_level] || 'neutral'}>{riskLabel[data.overall_risk_level] || data.overall_risk_level}</Badge>
            {data.overall_score != null && <span className="text-lg font-semibold text-brand-600">综合评分 {data.overall_score}</span>}
          </div>
          {data.summary && <p className="mt-4 text-sm leading-7 text-slate-600">{data.summary}</p>}
        </Card>
      )}

      {data.risks && data.risks.length > 0 ? (
        <section className="space-y-4">
          <h2 className="text-lg font-semibold text-slate-900">风险详情（{data.risks.length} 项）</h2>
          {data.risks.map((risk, i) => (
            <Card key={i}>
              <div className="flex items-center gap-2 mb-2">
                <Badge tone={riskTone[risk.level] || 'neutral'}>{riskLabel[risk.level] || risk.level}</Badge>
                <span className="font-semibold text-slate-800">{risk.title}</span>
              </div>
              <p className="text-sm leading-7 text-slate-600">{risk.description}</p>
              {risk.location && <p className="mt-2 text-xs text-slate-400">位置：{risk.location}</p>}
              {risk.legal_basis && risk.legal_basis.length > 0 && (
                <div className="mt-3 rounded-xl bg-slate-50 p-3">
                  <div className="text-xs font-medium text-slate-500 mb-1">法律依据</div>
                  <ul className="list-disc list-inside space-y-1">
                    {risk.legal_basis.map((basis, j) => (
                      <li key={j}>
                        <Link
                          to={`/search?q=${encodeURIComponent(basis)}`}
                          className="text-xs text-brand-600 hover:text-brand-700 hover:underline transition"
                        >
                          {basis}
                        </Link>
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              {risk.suggestion && (
                <div className="mt-3 rounded-xl bg-brand-50 p-3">
                  <div className="text-xs font-medium text-brand-700 mb-1">修改建议</div>
                  <p className="text-sm leading-6 text-brand-800">{risk.suggestion}</p>
                </div>
              )}
            </Card>
          ))}
        </section>
      ) : (
        <EmptyState title="未检测到风险" description="该文档未发现明显的法律风险。" />
      )}
    </PageContainer>
  );
}
