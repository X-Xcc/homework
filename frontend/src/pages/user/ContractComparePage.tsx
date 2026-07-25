import { useState } from 'react';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { EmptyState } from '@/shared/ui/EmptyState';
import { apiRequest } from '@/shared/api/client';

type ChangeItem = {
  type: string;
  original?: string | null;
  modified?: string | null;
  location?: string | null;
};

type CompareResult = {
  id: string;
  document_a: string;
  document_b: string;
  status: string;
  changes: ChangeItem[];
  summary?: string | null;
};

function changeTypeLabel(type: string): string {
  if (type === 'add') return '新增';
  if (type === 'delete') return '删除';
  if (type === 'modify') return '修改';
  return type;
}

function changeTypeColor(type: string): string {
  if (type === 'add') return 'bg-emerald-50 text-emerald-700 border-emerald-200';
  if (type === 'delete') return 'bg-red-50 text-red-700 border-red-200';
  return 'bg-amber-50 text-amber-700 border-amber-200';
}

export function ContractComparePage() {
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [comparing, setComparing] = useState(false);
  const [result, setResult] = useState<CompareResult | null>(null);
  const [error, setError] = useState<string | null>(null);

  const handleCompare = async () => {
    if (!fileA || !fileB) return;
    setComparing(true);
    setError(null);
    setResult(null);
    try {
      const formData = new FormData();
      formData.append('file_a', fileA);
      formData.append('file_b', fileB);
      const data = await apiRequest<CompareResult>('/api/document/compare', {
        method: 'POST',
        body: formData,
      });
      setResult(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : '对比失败');
    } finally {
      setComparing(false);
    }
  };

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">合同对比</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">合同版本对比</h1>
        <p className="mt-1 text-sm text-slate-500">上传两个版本的合同文件，快速识别差异内容。</p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <Card>
          <Panel title="版本 A（原始版本）" description="请上传较早的版本">
            <label className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-8 transition hover:border-brand-200 hover:bg-brand-50/30 cursor-pointer">
              <input type="file" accept=".pdf,.docx,.doc,.txt" className="hidden" onChange={(e) => setFileA(e.target.files?.[0] || null)} />
              <div className="text-4xl text-slate-300">📄</div>
              <div className="mt-3 text-sm font-medium text-slate-500">{fileA ? fileA.name : '点击上传版本 A'}</div>
            </label>
          </Panel>
        </Card>
        <Card>
          <Panel title="版本 B（修改版本）" description="请上传修改后的版本">
            <label className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-8 transition hover:border-brand-200 hover:bg-brand-50/30 cursor-pointer">
              <input type="file" accept=".pdf,.docx,.doc,.txt" className="hidden" onChange={(e) => setFileB(e.target.files?.[0] || null)} />
              <div className="text-4xl text-slate-300">📝</div>
              <div className="mt-3 text-sm font-medium text-slate-500">{fileB ? fileB.name : '点击上传版本 B'}</div>
            </label>
          </Panel>
        </Card>
      </div>

      <div className="flex justify-center">
        <Button onClick={handleCompare} loading={comparing} disabled={!fileA || !fileB}>
          开始对比
        </Button>
      </div>

      {comparing && (
        <Card>
          <Skeleton className="h-40" />
        </Card>
      )}

      {error && <EmptyState title="对比失败" description={error} />}

      {result && (
        <Card>
          <Panel title="差异分析结果" description={result.summary || '两版合同的主要差异'}>
            {result.changes.length > 0 ? (
              <div className="space-y-3">
                {result.changes.map((item, i) => (
                  <div key={i} className={`rounded-2xl border p-4 text-sm ${changeTypeColor(item.type)}`}>
                    <div className="flex items-center gap-2 mb-2">
                      <span className="font-semibold">{changeTypeLabel(item.type)}</span>
                      {item.location && <span className="text-xs opacity-70">位置: {item.location}</span>}
                    </div>
                    {item.original && (
                      <p className="text-xs opacity-80 mb-1">
                        <span className="font-medium">原文：</span>{item.original}
                      </p>
                    )}
                    {item.modified && (
                      <p className="text-xs opacity-80">
                        <span className="font-medium">修改后：</span>{item.modified}
                      </p>
                    )}
                  </div>
                ))}
              </div>
            ) : (
              <EmptyState title="未发现差异" description="两份文档内容一致。" />
            )}
          </Panel>
        </Card>
      )}
    </PageContainer>
  );
}
