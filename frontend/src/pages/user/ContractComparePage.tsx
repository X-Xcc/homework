import { useState } from 'react';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';

export function ContractComparePage() {
  const [fileA, setFileA] = useState<File | null>(null);
  const [fileB, setFileB] = useState<File | null>(null);
  const [comparing, setComparing] = useState(false);
  const [compared, setCompared] = useState(false);

  const handleCompare = () => {
    if (!fileA || !fileB) return;
    setComparing(true);
    setTimeout(() => {
      setComparing(false);
      setCompared(true);
    }, 2500);
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
              <input type="file" accept=".pdf,.docx,.doc" className="hidden" onChange={(e) => setFileA(e.target.files?.[0] || null)} />
              <div className="text-4xl text-slate-300">📄</div>
              <div className="mt-3 text-sm font-medium text-slate-500">{fileA ? fileA.name : '点击上传版本 A'}</div>
            </label>
          </Panel>
        </Card>
        <Card>
          <Panel title="版本 B（修改版本）" description="请上传修改后的版本">
            <label className="flex flex-col items-center justify-center rounded-2xl border-2 border-dashed border-slate-200 bg-slate-50 p-8 transition hover:border-brand-200 hover:bg-brand-50/30 cursor-pointer">
              <input type="file" accept=".pdf,.docx,.doc" className="hidden" onChange={(e) => setFileB(e.target.files?.[0] || null)} />
              <div className="text-4xl text-slate-300">📑</div>
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

      {compared && (
        <Card>
          <Panel title="差异分析结果" description="两版合同的主要差异">
            <div className="space-y-3">
              {[
                { type: '新增', desc: '第三条增加了不可抗力条款的详细定义', color: 'bg-emerald-50 text-emerald-700 border-emerald-200' },
                { type: '删除', desc: '原第七条关于竞业限制的约定已删除', color: 'bg-red-50 text-red-700 border-red-200' },
                { type: '修改', desc: '第十条违约金由固定金额改为按日计算', color: 'bg-amber-50 text-amber-700 border-amber-200' },
              ].map((item, i) => (
                <div key={i} className={`rounded-2xl border p-4 text-sm ${item.color}`}>
                  <span className="font-semibold">{item.type}：</span>{item.desc}
                </div>
              ))}
            </div>
          </Panel>
        </Card>
      )}
    </PageContainer>
  );
}
