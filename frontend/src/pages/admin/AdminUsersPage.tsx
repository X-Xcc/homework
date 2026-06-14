import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const users = [
  { name: '张三', email: 'zhangsan@example.com', role: 'user', status: 'active', analyses: 42 },
  { name: '李四', email: 'lisi@example.com', role: 'admin', status: 'active', analyses: 18 },
  { name: '王五', email: 'wangwu@example.com', role: 'user', status: 'suspended', analyses: 3 },
];

export function AdminUsersPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">用户管理</h1>
      </div>
      <Card className="border-slate-800 bg-slate-900 text-white shadow-none">
        <div className="overflow-x-auto">
          <table className="min-w-full text-left text-sm">
            <thead className="text-slate-400">
              <tr>
                <th className="px-4 py-3">用户</th>
                <th className="px-4 py-3">邮箱</th>
                <th className="px-4 py-3">角色</th>
                <th className="px-4 py-3">状态</th>
                <th className="px-4 py-3">分析次数</th>
              </tr>
            </thead>
            <tbody>
              {users.map((user) => (
                <tr key={user.email} className="border-t border-slate-800 text-slate-200">
                  <td className="px-4 py-4">{user.name}</td>
                  <td className="px-4 py-4">{user.email}</td>
                  <td className="px-4 py-4">{user.role}</td>
                  <td className="px-4 py-4">
                    <Badge tone={user.status === 'active' ? 'success' : 'warning'}>
                      {user.status === 'active' ? '正常' : '已停用'}
                    </Badge>
                  </td>
                  <td className="px-4 py-4">{user.analyses}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Card>
    </PageContainer>
  );
}
