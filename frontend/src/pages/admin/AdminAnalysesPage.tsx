import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const records = [
  { id: 'A-1001', user: '张三', document: '采购合同_v2.pdf', status: 'completed', risks: 5, time: '2026-06-10 09:20' },
  { id: 'A-1002', user: '王五', document: '保密协议.docx', status: 'running', risks: 0, time: '2026-06-10 09:45' },
  { id: 'A-1003', user: '赵六', document: '劳动合同.pdf', status: 'failed', risks: 0, time: '2026-06-10 10:02' },
];

export function AdminAnalysesPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">分析记录</h1>
      </div>
      <div className="space-y-3">
        {records.map((record) => (
          <Card key={record.id} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <div className="flex items-start justify-between gap-4">
              <div>
                <div className="text-sm text-slate-400">{record.id} · {record.user}</div>
                <div className="mt-2 text-lg font-semibold">{record.document}</div>
                <div className="mt-2 text-sm text-slate-400">提交时间：{record.time}</div>
              </div>
              <div className="text-right">
                <Badge tone={record.status === 'completed' ? 'success' : record.status === 'running' ? 'brand' : 'warning'}>
                  {record.status}
                </Badge>
                <div className="mt-3 text-sm text-slate-300">风险点：{record.risks}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
