import { Link, useNavigate } from 'react-router-dom';
import { useAuth } from '@/app/providers/AuthProvider';
import { Button } from '@/shared/ui/Button';

export function AppHeader() {
  const { user, isAuthenticated, isAdmin, logout } = useAuth();
  const navigate = useNavigate();

  const handleLogout = async () => {
    await logout();
    navigate('/login', { replace: true });
  };

  return (
    <header className="sticky top-0 z-20 border-b border-slate-200 bg-white/80 backdrop-blur">
      <div className="mx-auto flex h-[72px] max-w-[1600px] items-center justify-between px-4 lg:px-6">
        <Link to={isAdmin ? '/admin' : '/dashboard'} className="block">
          <div className="text-xs font-medium uppercase tracking-[0.24em] text-brand-600">Legal Learning AI</div>
          <div className="text-lg font-semibold text-slate-900">法律学习 AI 工作台</div>
        </Link>
        <div className="flex items-center gap-3">
          {isAuthenticated && user ? (
            <>
              {isAdmin ? (
                <Link
                  to="/admin"
                  className="rounded-full border border-indigo-200 bg-indigo-50 px-3 py-1.5 text-xs font-medium text-indigo-700 hover:bg-indigo-100"
                >
                  后台管理
                </Link>
              ) : null}
              <div className="hidden text-right text-xs text-slate-500 sm:block">
                <div className="font-medium text-slate-700">
                  {user.nickname || user.username || user.email || '当前用户'}
                </div>
                <div>{user.role === 'admin' ? '管理员' : '普通用户'}</div>
              </div>
              <Button variant="secondary" size="sm" onClick={handleLogout}>
                退出登录
              </Button>
            </>
          ) : (
            <Link
              to="/login"
              className="rounded-full border border-brand-200 bg-brand-50 px-4 py-2 text-sm font-medium text-brand-700 hover:bg-brand-100"
            >
              登录 / 注册
            </Link>
          )}
        </div>
      </div>
    </header>
  );
}
