import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const logs = [
  { actor: 'admin', action: '更新模板', target: '租赁合同模板 v2.1', time: '2026-06-10 09:18' },
  { actor: 'admin', action: '冻结用户', target: 'wangwu@example.com', time: '2026-06-10 08:42' },
  { actor: 'system', action: '任务重试', target: 'analysis:A-1002', time: '2026-06-10 08:11' },
];

export function AdminAuditLogsPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">操作日志</h1>
      </div>
      <div className="space-y-3">
        {logs.map((log, index) => (
          <Card key={index} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <div className="flex items-center justify-between gap-4 text-sm">
              <div>
                <span className="font-semibold text-slate-200">{log.actor}</span>
                <span className="mx-2 text-slate-500">执行</span>
                <span className="text-slate-200">{log.action}</span>
                <span className="mx-2 text-slate-500">→</span>
                <span className="text-slate-400">{log.target}</span>
              </div>
              <div className="text-slate-500">{log.time}</div>
            </div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
