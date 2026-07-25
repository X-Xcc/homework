import { Link } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';

const metrics = [
  { label: '待分析合同', value: '12', hint: '本周新增 5 份' },
  { label: '高风险条款', value: '28', hint: '集中在违约与免责条款' },
  { label: '待复核问答', value: '6', hint: '建议今天完成校对' },
];

const quickEntries = [
  { title: '合同分析', description: '上传合同并提取核心风险。', to: '/contracts/analyze' },
  { title: '合同对比', description: '比较甲乙双方不同版本。', to: '/contracts/compare' },
  { title: '法条检索', description: '检索民法、刑法与合同相关法条。', to: '/search' },
  { title: '智能问答', description: '基于材料与法条进行法律问答。', to: '/chat' },
];

export function DashboardPage() {
  return (
    <PageContainer className="space-y-6">
      <Card className="overflow-hidden bg-slate-950 text-white">
        <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
          <div>
            <Badge tone="brand">前台工作区</Badge>
            <h1 className="mt-4 text-3xl font-semibold">欢迎回到法律学习 AI 工作台</h1>
            <p className="mt-3 max-w-2xl text-sm leading-7 text-slate-300">
              当前已经完成前台与后台分区骨架。你可以从这里继续进入合同分析、合同对比、法条检索和 AI 问答。
            </p>
            <div className="mt-6 flex flex-wrap gap-3">
              <Link to="/contracts/analyze">
                <Button>开始合同分析</Button>
              </Link>
              <Link to="/admin">
                <Button variant="secondary" className="border-slate-700 bg-slate-900 text-slate-100 hover:bg-slate-800">
                  查看后台管理
                </Button>
              </Link>
            </div>
          </div>
          <div className="grid gap-3 sm:grid-cols-3 lg:grid-cols-1">
            {metrics.map((item) => (
              <div key={item.label} className="rounded-3xl border border-white/10 bg-white/5 p-5">
                <div className="text-sm text-slate-300">{item.label}</div>
                <div className="mt-2 text-3xl font-semibold">{item.value}</div>
                <div className="mt-2 text-sm text-slate-400">{item.hint}</div>
              </div>
            ))}
          </div>
        </div>
      </Card>

      <section className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        {quickEntries.map((entry) => (
          <Card key={entry.title} className="space-y-4">
            <div>
              <div className="text-lg font-semibold text-slate-900">{entry.title}</div>
              <p className="mt-2 text-sm leading-7 text-slate-500">{entry.description}</p>
            </div>
            <Link to={entry.to}>
              <Button variant="secondary" className="w-full">
                进入
              </Button>
            </Link>
          </Card>
        ))}
      </section>
    </PageContainer>
  );
}
