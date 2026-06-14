import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';

const stats = [
  { label: '合同分析', value: 12, unit: '次' },
  { label: '合同对比', value: 5, unit: '次' },
  { label: '智能问答', value: 38, unit: '次' },
  { label: '法条检索', value: 24, unit: '次' },
];

export function ProfilePage() {
  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">个人中心</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">我的账号</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <Card className="flex flex-col items-center py-8">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-brand-100 text-3xl font-bold text-brand-600">用</div>
          <div className="mt-4 text-lg font-semibold text-slate-900">用户名</div>
          <div className="mt-1 text-sm text-slate-500">user@example.com</div>
          <Badge tone="neutral" className="mt-3">普通用户</Badge>
          <Button variant="secondary" className="mt-6 w-full">编辑资料</Button>
          <Button variant="ghost" className="mt-2 w-full text-red-500">退出登录</Button>
        </Card>

        <div className="space-y-4">
          <Card>
            <Panel title="使用统计" description="近 30 天使用情况">
              <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                {stats.map((s) => (
                  <div key={s.label} className="rounded-2xl border border-slate-100 p-4 text-center">
                    <div className="text-3xl font-bold text-brand-600">{s.value}</div>
                    <div className="mt-1 text-sm text-slate-500">{s.label}（{s.unit}）</div>
                  </div>
                ))}
              </div>
            </Panel>
          </Card>
          <Card>
            <Panel title="账号安全" description="密码与登录安全">
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-2xl border border-slate-100 p-4">
                  <div className="text-sm text-slate-700">登录密码</div>
                  <Button variant="secondary" size="sm">修改密码</Button>
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-slate-100 p-4">
                  <div className="text-sm text-slate-700">绑定邮箱</div>
                  <div className="text-sm text-slate-400">user@example.com</div>
                </div>
              </div>
            </Panel>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
