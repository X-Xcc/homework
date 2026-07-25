import { createContext, PropsWithChildren, useCallback, useContext, useEffect, useMemo, useState } from 'react';
import { authApi } from '@/shared/api/user';
import { ApiError } from '@/shared/api/client';
import { authStore, CurrentUser } from '@/shared/api/auth-store';

type AuthContextValue = {
  user: CurrentUser | null;
  isAuthenticated: boolean;
  isAdmin: boolean;
  status: 'idle' | 'loading' | 'ready';
  login: (account: string, password: string) => Promise<void>;
  register: (payload: { username: string; password: string; email?: string; nickname?: string }) => Promise<void>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: PropsWithChildren) {
  const [user, setUser] = useState<CurrentUser | null>(() => authStore.getUser());
  const [status, setStatus] = useState<'idle' | 'loading' | 'ready'>(() =>
    authStore.getAccessToken() ? 'loading' : 'idle',
  );

  const refreshUser = useCallback(async () => {
    if (!authStore.getAccessToken()) {
      setUser(null);
      setStatus('ready');
      return;
    }
    setStatus('loading');
    try {
      const me = await authApi.me();
      authStore.setUser(me);
      setUser(me);
    } catch (err) {
      if (err instanceof ApiError && err.status === 401) {
        authStore.clear();
        setUser(null);
      } else {
        // 网络错误等场景：保留 token，避免无限重试；标记 ready 即可
        setUser(authStore.getUser());
      }
    } finally {
      setStatus('ready');
    }
  }, []);

  useEffect(() => {
    void refreshUser();
  }, [refreshUser]);

  const handleAuthSuccess = useCallback((tokens: { access_token: string; refresh_token: string }) => {
    authStore.setTokens(tokens);
  }, []);

  const login = useCallback(
    async (account: string, password: string) => {
      const tokens = await authApi.login({ account, password });
      handleAuthSuccess(tokens);
      await refreshUser();
    },
    [handleAuthSuccess, refreshUser],
  );

  const register = useCallback(
    async (payload: { username: string; password: string; email?: string; nickname?: string }) => {
      const tokens = await authApi.register(payload);
      handleAuthSuccess(tokens);
      await refreshUser();
    },
    [handleAuthSuccess, refreshUser],
  );

  const logout = useCallback(async () => {
    try {
      await authApi.logout();
    } catch {
      // 即便后端失败也清本地
    }
    authStore.clear();
    setUser(null);
  }, []);

  const value = useMemo<AuthContextValue>(
    () => ({
      user,
      isAuthenticated: !!user,
      isAdmin: user?.role === 'admin',
      status,
      login,
      register,
      logout,
      refresh: refreshUser,
    }),
    [user, status, login, register, logout, refreshUser],
  );

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error('useAuth 必须在 <AuthProvider> 内使用');
  }
  return ctx;
}
