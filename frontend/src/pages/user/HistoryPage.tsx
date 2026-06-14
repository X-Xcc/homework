import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { EmptyState } from '@/shared/ui/EmptyState';

const mockHistory = [
  { id: '1', type: '分析', name: '租赁合同_2024版.pdf', status: 'completed', date: '2024-06-09', risks: 3 },
  { id: '2', type: '对比', name: '劳动合同_A vs B.docx', status: 'completed', date: '2024-06-08', changes: 12 },
  { id: '3', type: '分析', name: '采购协议_模板.docx', status: 'completed', date: '2024-06-07', risks: 1 },
  { id: '4', type: '分析', name: '保密协议_甲方.docx', status: 'failed', date: '2024-06-06', risks: 0 },
];

export function HistoryPage() {
  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">历史记录</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">我的分析历史</h1>
        <p className="mt-1 text-sm text-slate-500">所有合同分析、对比与问答记录。</p>
      </div>

      <Card>
        {mockHistory.length > 0 ? (
          <div className="space-y-3">
            {mockHistory.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-2xl border border-slate-100 p-4 transition hover:border-brand-200 hover:bg-brand-50/20">
                <div className="flex items-center gap-4">
                  <div className="text-2xl">{item.type === '分析' ? '📄' : '📑'}</div>
                  <div>
                    <div className="font-medium text-slate-800">{item.name}</div>
                    <div className="mt-1 flex items-center gap-3 text-sm text-slate-400">
                      <span>{item.date}</span>
                      <Badge tone={item.status === 'completed' ? 'success' : 'warning'}>{item.status === 'completed' ? '已完成' : '处理中'}</Badge>
                      <span>{item.type === '分析' ? `${item.risks} 个风险点` : `${item.changes} 处变更`}</span>
                    </div>
                  </div>
                </div>
                <Button variant="ghost" size="sm">查看</Button>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="暂无历史记录" description="开始分析或对比合同后将显示在这里。" />
        )}
      </Card>
    </PageContainer>
  );
}
