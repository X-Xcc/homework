import { useParams } from 'react-router-dom';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { EmptyState } from '@/shared/ui/EmptyState';

export function MaterialDetailPage() {
  const { materialId } = useParams();

  return (
    <PageContainer className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Badge tone="brand">材料阅读</Badge>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">材料详情</h1>
          <p className="mt-1 text-sm text-slate-500">ID: {materialId}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary">导出摘要</Button>
          <Button>触发 AI 分析</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_340px]">
        <Card className="min-h-[480px]">
          <Panel title="材料内容" description="正在加载材料内容...">
            <EmptyState
              title="暂无材料内容"
              description="请在工作台上传或选择一份材料后在此查看。"
            />
          </Panel>
        </Card>
        <div className="space-y-4">
          <Card>
            <Panel title="AI 摘要" description="AI 自动提炼的核心要点">
              <EmptyState title="暂无摘要" description="点击「触发 AI 分析」生成。" />
            </Panel>
          </Card>
          <Card>
            <Panel title="相关法条" description="与此材料相关的法律条文">
              <EmptyState title="暂无关联法条" description="系统将在分析后自动关联。" />
            </Panel>
          </Card>
          <Card>
            <Panel title="知识节点" description="从材料中提炼的知识点">
              <EmptyState title="暂无知识节点" description="触发分析后自动生成。" />
            </Panel>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
