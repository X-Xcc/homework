/**
 * 鉴权令牌与当前用户的轻量 store。localStorage 持久化 + 跨 tab 同步。
 */
const ACCESS_KEY = 'legal_ai.access_token';
const REFRESH_KEY = 'legal_ai.refresh_token';
const USER_KEY = 'legal_ai.current_user';

export type CurrentUser = {
  id: string;
  username?: string | null;
  email?: string | null;
  nickname?: string | null;
  avatar?: string | null;
  role: 'user' | 'admin' | string;
  status: string;
  created_at?: string | null;
  last_login_at?: string | null;
};

export type TokenPair = {
  access_token: string;
  refresh_token: string;
};

type Listener = () => void;

class AuthStore {
  private listeners = new Set<Listener>();

  getAccessToken(): string | null {
    return localStorage.getItem(ACCESS_KEY);
  }

  getRefreshToken(): string | null {
    return localStorage.getItem(REFRESH_KEY);
  }

  getUser(): CurrentUser | null {
    const raw = localStorage.getItem(USER_KEY);
    if (!raw) return null;
    try {
      return JSON.parse(raw) as CurrentUser;
    } catch {
      return null;
    }
  }

  setTokens(tokens: TokenPair): void {
    localStorage.setItem(ACCESS_KEY, tokens.access_token);
    localStorage.setItem(REFRESH_KEY, tokens.refresh_token);
    this.emit();
  }

  setUser(user: CurrentUser | null): void {
    if (user === null) {
      localStorage.removeItem(USER_KEY);
    } else {
      localStorage.setItem(USER_KEY, JSON.stringify(user));
    }
    this.emit();
  }

  clear(): void {
    localStorage.removeItem(ACCESS_KEY);
    localStorage.removeItem(REFRESH_KEY);
    localStorage.removeItem(USER_KEY);
    this.emit();
  }

  subscribe(listener: Listener): () => void {
    this.listeners.add(listener);
    return () => this.listeners.delete(listener);
  }

  private emit(): void {
    for (const listener of this.listeners) listener();
  }
}

export const authStore = new AuthStore();

if (typeof window !== 'undefined') {
  window.addEventListener('storage', (event) => {
    if (event.key && [ACCESS_KEY, REFRESH_KEY, USER_KEY].includes(event.key)) {
      authStore['emit']();
    }
  });
}
