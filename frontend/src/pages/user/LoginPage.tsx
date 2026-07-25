import { useState } from 'react';
import { Link, Navigate, useLocation, useNavigate } from 'react-router-dom';
import { Button } from '@/shared/ui/Button';
import { useAuth } from '@/app/providers/AuthProvider';
import { ApiError } from '@/shared/api/client';

type LocationState = { from?: string } | null;

export function LoginPage() {
  const { login,  isAuthenticated, isAdmin } = useAuth();
  const navigate = useNavigate();
  const location = useLocation();
  const [account, setAccount] = useState('');
  const [password, setPassword] = useState('');
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to={isAdmin ? '/admin' : (location.state as LocationState)?.from || '/dashboard'} replace />;
  }

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    if (!account.trim() || !password) {
      setError('请输入账号和密码');
      return;
    }
    setError(null);
    setLoading(true);
    try {
      await login(account.trim(), password);
      const from = (location.state as LocationState)?.from;
      navigate(from || '/dashboard', { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('登录失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <h2 className="text-3xl font-semibold text-slate-900">登录账号</h2>
        <p className="mt-2 text-sm text-slate-500">法律学习 AI 工作台</p>
      </div>
      <div className="space-y-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">用户名 / 邮箱</label>
          <input
            type="text"
            value={account}
            onChange={(e) => setAccount(e.target.value)}
            placeholder="请输入用户名或邮箱"
            autoComplete="username"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">密码</label>
          <input
            type="password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            placeholder="请输入密码"
            autoComplete="current-password"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
      </div>
      {error ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}
      <Button type="submit" className="w-full" loading={loading}>
        登录
      </Button>
      <div className="text-center text-sm text-slate-500">
        还没有账号？{' '}
        <Link to="/register" className="font-medium text-brand-600 hover:underline">
          立即注册
        </Link>
      </div>
      <div className="relative">
        <div className="absolute inset-0 flex items-center">
          <div className="w-full border-t border-slate-200" />
        </div>
        <div className="relative flex justify-center text-xs">
          <span className="bg-white px-3 text-slate-400">或</span>
        </div>
      </div>
      <div className="rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-xs text-slate-500">
        默认管理员账号 <code className="font-mono">admin / Admin@12345</code>，首次启动后请尽快修改密码。
      </div>
    </form>
  );
}
