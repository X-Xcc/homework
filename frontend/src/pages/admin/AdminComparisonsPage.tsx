import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const records = [
  { id: 'C-2001', user: '张三', pair: '租赁合同_A / B', changes: 12, time: '2026-06-09 18:30' },
  { id: 'C-2002', user: '李四', pair: '劳务合同_v1 / v3', changes: 7, time: '2026-06-10 08:40' },
];

export function AdminComparisonsPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">对比记录</h1>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        {records.map((record) => (
          <Card key={record.id} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <div className="text-sm text-slate-400">{record.id} · {record.user}</div>
            <div className="mt-2 text-lg font-semibold">{record.pair}</div>
            <div className="mt-4 flex items-center justify-between text-sm">
              <Badge tone="brand">{record.changes} 处变更</Badge>
              <span className="text-slate-400">{record.time}</span>
            </div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
