import { useState } from 'react';
import { Link, Navigate, useNavigate } from 'react-router-dom';
import { Button } from '@/shared/ui/Button';
import { useAuth } from '@/app/providers/AuthProvider';
import { ApiError } from '@/shared/api/client';

export function RegisterPage() {
  const { register, isAuthenticated, isAdmin } = useAuth();
  const navigate = useNavigate();
  const [form, setForm] = useState({ username: '', email: '', password: '', confirm: '', nickname: '' });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  if (isAuthenticated) {
    return <Navigate to={isAdmin ? '/admin' : '/dashboard'} replace />;
  }

  const updateField = (key: keyof typeof form) => (event: React.ChangeEvent<HTMLInputElement>) =>
    setForm((prev) => ({ ...prev, [key]: event.target.value }));

  const handleSubmit = async (event: React.FormEvent) => {
    event.preventDefault();
    setError(null);

    const username = form.username.trim();
    if (!/^[A-Za-z0-9_\-.]{3,32}$/.test(username)) {
      setError('用户名仅支持字母/数字/_-.，长度 3-32');
      return;
    }
    if (form.password.length < 8) {
      setError('密码至少 8 位');
      return;
    }
    if (form.password !== form.confirm) {
      setError('两次输入的密码不一致');
      return;
    }
    if (form.email && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(form.email.trim())) {
      setError('邮箱格式不正确');
      return;
    }

    setLoading(true);
    try {
      await register({
        username,
        password: form.password,
        email: form.email.trim() || undefined,
        nickname: form.nickname.trim() || undefined,
      });
      navigate('/dashboard', { replace: true });
    } catch (err) {
      if (err instanceof ApiError) {
        setError(err.message);
      } else {
        setError('注册失败，请稍后重试');
      }
    } finally {
      setLoading(false);
    }
  };

  return (
    <form className="space-y-6" onSubmit={handleSubmit}>
      <div>
        <h2 className="text-3xl font-semibold text-slate-900">创建账号</h2>
        <p className="mt-2 text-sm text-slate-500">开始使用法律学习 AI 工作台</p>
      </div>
      <div className="space-y-4">
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">用户名</label>
          <input
            type="text"
            value={form.username}
            onChange={updateField('username')}
            placeholder="设置用户名"
            autoComplete="username"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">昵称（可选）</label>
          <input
            type="text"
            value={form.nickname}
            onChange={updateField('nickname')}
            placeholder="想让别人怎么称呼你"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">邮箱（可选）</label>
          <input
            type="email"
            value={form.email}
            onChange={updateField('email')}
            placeholder="请输入邮箱"
            autoComplete="email"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">密码</label>
          <input
            type="password"
            value={form.password}
            onChange={updateField('password')}
            placeholder="设置密码（不少于 8 位）"
            autoComplete="new-password"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
        <div>
          <label className="mb-2 block text-sm font-medium text-slate-700">确认密码</label>
          <input
            type="password"
            value={form.confirm}
            onChange={updateField('confirm')}
            placeholder="再次输入密码"
            autoComplete="new-password"
            className="w-full rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
      </div>
      {error ? (
        <div className="rounded-2xl border border-rose-200 bg-rose-50 px-4 py-3 text-sm text-rose-700">{error}</div>
      ) : null}
      <Button type="submit" className="w-full" loading={loading}>
        注册
      </Button>
      <div className="text-center text-sm text-slate-500">
        已有账号？{' '}
        <Link to="/login" className="font-medium text-brand-600 hover:underline">
          立即登录
        </Link>
      </div>
    </form>
  );
}
