import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

export function AdminSettingsPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">系统设置</h1>
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-900 text-white shadow-none">
          <div className="text-lg font-semibold">AI 分析配置</div>
          <div className="mt-4 space-y-4">
            <label className="block text-sm text-slate-300">
              风险阈值
              <input className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none" defaultValue="0.72" />
            </label>
            <label className="block text-sm text-slate-300">
              并发任务数
              <input className="mt-2 w-full rounded-2xl border border-slate-700 bg-slate-950 px-4 py-3 text-sm text-white outline-none" defaultValue="4" />
            </label>
          </div>
        </Card>
        <Card className="border-slate-800 bg-slate-900 text-white shadow-none">
          <div className="text-lg font-semibold">系统开关</div>
          <div className="mt-4 space-y-4 text-sm text-slate-300">
            <label className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3">
              <span>启用 OCR 回退</span>
              <input type="checkbox" defaultChecked className="h-4 w-4" />
            </label>
            <label className="flex items-center justify-between rounded-2xl border border-slate-800 bg-slate-950 px-4 py-3">
              <span>启用问答日志记录</span>
              <input type="checkbox" defaultChecked className="h-4 w-4" />
            </label>
          </div>
        </Card>
      </div>
      <div className="flex justify-end">
        <Button>保存设置</Button>
      </div>
    </PageContainer>
  );
}
