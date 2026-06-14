import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const templates = [
  { name: '租赁合同模板', version: 'v2.1', status: 'published' },
  { name: '劳动合同模板', version: 'v1.5', status: 'draft' },
  { name: '保密协议模板', version: 'v3.0', status: 'published' },
];

export function AdminTemplatesPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div className="flex items-center justify-between gap-4">
        <div>
          <Badge tone="brand">后台管理</Badge>
          <h1 className="mt-2 text-2xl font-semibold text-white">模板管理</h1>
        </div>
        <Button>新建模板</Button>
      </div>
      <div className="space-y-3">
        {templates.map((template) => (
          <Card key={template.name} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <div className="flex items-center justify-between">
              <div>
                <div className="text-lg font-semibold">{template.name}</div>
                <div className="mt-2 text-sm text-slate-400">当前版本：{template.version}</div>
              </div>
              <Badge tone={template.status === 'published' ? 'success' : 'warning'}>
                {template.status === 'published' ? '已发布' : '草稿'}
              </Badge>
            </div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
