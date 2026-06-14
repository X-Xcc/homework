import { PropsWithChildren } from 'react';
import { Navigate, useLocation } from 'react-router-dom';
import { useAuth } from './AuthProvider';

type GuardProps = PropsWithChildren<{
  /** 是否要求管理员角色 */
  requireAdmin?: boolean;
}>;

export function AuthGuard({ children, requireAdmin = false }: GuardProps) {
  const { isAuthenticated, isAdmin, status } = useAuth();
  const location = useLocation();

  if (status === 'loading') {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-sm text-slate-500">
        正在校验身份...
      </div>
    );
  }

  if (!isAuthenticated) {
    return <Navigate to="/login" replace state={{ from: location.pathname }} />;
  }

  if (requireAdmin && !isAdmin) {
    return <Navigate to="/dashboard" replace />;
  }

  return <>{children}</>;
}

export function GuestOnly({ children }: PropsWithChildren) {
  const { isAuthenticated, isAdmin, status } = useAuth();

  if (status === 'loading') {
    return (
      <div className="flex min-h-[40vh] items-center justify-center text-sm text-slate-500">
        正在校验身份...
      </div>
    );
  }

  if (isAuthenticated) {
    return <Navigate to={isAdmin ? '/admin' : '/dashboard'} replace />;
  }

  return <>{children}</>;
}
