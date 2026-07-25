import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { Panel } from '@/shared/ui/Panel';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { useAuth } from '@/app/providers/AuthProvider';
import { apiRequest } from '@/shared/api/client';

type UserStats = {
  id: string;
  analysis_count: number;
  chat_count: number;
  favorite_count: number;
  comparison_count: number;
};

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '未知';
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { year: 'numeric', month: 'long', day: 'numeric' });
  } catch {
    return iso;
  }
}

export function ProfilePage() {
  const { user, logout } = useAuth();
  const navigate = useNavigate();
  const [stats, setStats] = useState<UserStats | null>(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    (async () => {
      try {
        const data = await apiRequest<UserStats>('/api/user/me/stats');
        if (!cancelled) setStats(data);
      } catch {
        // 静默处理
      } finally {
        if (!cancelled) setLoading(false);
      }
    })();
    return () => { cancelled = true; };
  }, []);

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  const displayName = user?.nickname || user?.username || user?.email || '当前用户';
  const initial = displayName.charAt(0).toUpperCase();

  const statItems = [
    { label: '合同分析', value: stats?.analysis_count ?? 0, unit: '次' },
    { label: '合同对比', value: stats?.comparison_count ?? 0, unit: '次' },
    { label: '智能问答', value: stats?.chat_count ?? 0, unit: '次' },
    { label: '收藏条目', value: stats?.favorite_count ?? 0, unit: '条' },
  ];

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">个人中心</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">我的账号</h1>
      </div>

      <div className="grid gap-6 lg:grid-cols-[280px_1fr]">
        <Card className="flex flex-col items-center py-8">
          <div className="flex h-20 w-20 items-center justify-center rounded-full bg-brand-100 text-3xl font-bold text-brand-600">
            {initial}
          </div>
          <div className="mt-4 text-lg font-semibold text-slate-900">{displayName}</div>
          <div className="mt-1 text-sm text-slate-500">{user?.email || '未设置邮箱'}</div>
          <Badge tone={user?.role === 'admin' ? 'brand' : 'neutral'} className="mt-3">
            {user?.role === 'admin' ? '管理员' : '普通用户'}
          </Badge>
          <div className="mt-2 text-xs text-slate-400">注册时间：{formatDate(user?.created_at)}</div>
          <Button variant="ghost" className="mt-6 w-full text-red-500" onClick={handleLogout}>退出登录</Button>
        </Card>

        <div className="space-y-4">
          <Card>
            <Panel title="使用统计" description="你的使用概况">
              {loading ? (
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                  {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-20" />)}
                </div>
              ) : (
                <div className="grid grid-cols-2 gap-4 sm:grid-cols-4">
                  {statItems.map((s) => (
                    <div key={s.label} className="rounded-2xl border border-slate-100 p-4 text-center">
                      <div className="text-3xl font-bold text-brand-600">{s.value}</div>
                      <div className="mt-1 text-sm text-slate-500">{s.label}（{s.unit}）</div>
                    </div>
                  ))}
                </div>
              )}
            </Panel>
          </Card>
          <Card>
            <Panel title="账号安全" description="密码与登录安全">
              <div className="space-y-3">
                <div className="flex items-center justify-between rounded-2xl border border-slate-100 p-4">
                  <div className="text-sm text-slate-700">用户名</div>
                  <div className="text-sm text-slate-400">{user?.username || '未设置'}</div>
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-slate-100 p-4">
                  <div className="text-sm text-slate-700">绑定邮箱</div>
                  <div className="text-sm text-slate-400">{user?.email || '未绑定'}</div>
                </div>
                <div className="flex items-center justify-between rounded-2xl border border-slate-100 p-4">
                  <div className="text-sm text-slate-700">最近登录</div>
                  <div className="text-sm text-slate-400">{formatDate(user?.last_login_at)}</div>
                </div>
              </div>
            </Panel>
          </Card>
        </div>
      </div>
    </PageContainer>
  );
}
