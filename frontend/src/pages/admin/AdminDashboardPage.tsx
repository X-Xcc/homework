import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const metrics = [
  { label: '总用户数', value: '1,248', tone: 'brand' as const },
  { label: '分析总量', value: '8,426', tone: 'success' as const },
  { label: '活跃会话', value: '312', tone: 'warning' as const },
  { label: '系统告警', value: '2', tone: 'neutral' as const },
];

const modules = [
  '用户管理',
  '分析记录',
  '对比记录',
  '聊天会话',
  '收藏管理',
  '模板管理',
  '日志审计',
  '系统配置',
];

export function AdminDashboardPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">管理仪表板</h1>
        <p className="mt-1 text-sm text-slate-400">查看系统运行状态、核心指标和治理入口。</p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {metrics.map((metric) => (
          <Card key={metric.label} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-sm text-slate-400">{metric.label}</div>
                <div className="mt-2 text-3xl font-semibold">{metric.value}</div>
              </div>
              <Badge tone={metric.tone}>{metric.label}</Badge>
            </div>
          </Card>
        ))}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <Card className="border-slate-800 bg-slate-900 text-white shadow-none">
          <div className="text-lg font-semibold">待处理事项</div>
          <div className="mt-4 space-y-3 text-sm text-slate-300">
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">2 个系统告警等待处理</div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">8 个用户反馈待审核</div>
            <div className="rounded-2xl border border-slate-800 bg-slate-950 p-4">3 个模板版本需要发布</div>
          </div>
        </Card>
        <Card className="border-slate-800 bg-slate-900 text-white shadow-none">
          <div className="text-lg font-semibold">管理模块</div>
          <div className="mt-4 grid gap-3 sm:grid-cols-2">
            {modules.map((module) => (
              <div key={module} className="rounded-2xl border border-slate-800 bg-slate-950 p-4 text-sm text-slate-300">
                {module}
              </div>
            ))}
          </div>
        </Card>
      </div>
    </PageContainer>
  );
}
