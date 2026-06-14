import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const sessions = [
  { id: 'S-3001', user: '张三', title: '违约金条款咨询', messages: 14, updatedAt: '10:02' },
  { id: 'S-3002', user: '王五', title: '劳动合同风险识别', messages: 9, updatedAt: '09:48' },
  { id: 'S-3003', user: '赵六', title: '格式条款效力', messages: 23, updatedAt: '09:12' },
];

export function AdminChatSessionsPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">聊天会话</h1>
      </div>
      <div className="space-y-3">
        {sessions.map((session) => (
          <Card key={session.id} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <div className="flex items-center justify-between gap-4">
              <div>
                <div className="text-sm text-slate-400">{session.id} · {session.user}</div>
                <div className="mt-2 text-lg font-semibold">{session.title}</div>
              </div>
              <div className="text-right text-sm text-slate-400">
                <div>{session.messages} 条消息</div>
                <div className="mt-2">最近更新：{session.updatedAt}</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
