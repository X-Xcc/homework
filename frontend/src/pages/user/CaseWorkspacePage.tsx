import { useParams } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { EmptyState } from '@/shared/ui/EmptyState';

export function CaseWorkspacePage() {
  const { caseId } = useParams();

  return (
    <PageContainer className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <Badge tone="brand">案件工作区</Badge>
          <h1 className="mt-2 text-2xl font-semibold text-slate-900">案件分析工作台</h1>
          <p className="mt-1 text-sm text-slate-500">案件 ID: {caseId}</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary">导出成果</Button>
          <Button>添加材料</Button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-[1fr_360px]">
        <Card className="min-h-[520px]">
          <Panel title="工作区主视图" description="整理争点、证据与分析">
            <EmptyState
              title="暂无案件内容"
              description="在工作台新建案件或从材料库导入后在此整理。"
            />
          </Panel>
        </Card>
        <div className="space-y-4">
          <Card>
            <Panel title="争点整理" description="从材料中提取核心争议">
              <EmptyState title="暂无争点" description="添加材料后自动分析。" />
            </Panel>
          </Card>
          <Card>
            <Panel title="证据清单" description="案件涉及的证据材料">
              <EmptyState title="暂无证据" description="在工作区中手动添加。" />
            </Panel>
          </Card>
          <Card>
            <Panel title="分析成果" description="已完成的分析项">
              <EmptyState title="暂无分析" description="开始分析以生成成果。" />
            </Panel>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
