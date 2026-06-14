/**
 * 基础 fetch 封装：
 * - 自动注入 Authorization: Bearer <access_token>
 * - 收到 401 时调用 /api/user/refresh 刷新一次后重放
 * - 失败时抛出 ApiError
 */
import { authStore } from './auth-store';

const API_BASE = (import.meta.env.VITE_API_BASE as string | undefined) ?? '';

export class ApiError extends Error {
  status: number;
  data: unknown;
  constructor(message: string, status: number, data: unknown) {
    super(message);
    this.status = status;
    this.data = data;
  }
}

type RequestOptions = Omit<RequestInit, 'body' | 'headers'> & {
  body?: unknown;
  headers?: Record<string, string>;
  /** 标记为不需要带 token（如 login / refresh） */
  skipAuth?: boolean;
  /** 标记为不需要自动刷新（如 refresh 接口本身） */
  skipRefresh?: boolean;
};

let refreshPromise: Promise<string | null> | null = null;

async function performRefresh(): Promise<string | null> {
  if (refreshPromise) return refreshPromise;
  refreshPromise = (async () => {
    const refresh = authStore.getRefreshToken();
    if (!refresh) {
      authStore.clear();
      return null;
    }
    try {
      const resp = await fetch(`${API_BASE}/api/user/refresh`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ refresh_token: refresh }),
      });
      if (!resp.ok) {
        authStore.clear();
        return null;
      }
      const data = (await resp.json()) as { access_token: string; refresh_token: string };
      authStore.setTokens({ access_token: data.access_token, refresh_token: data.refresh_token });
      return data.access_token;
    } catch {
      authStore.clear();
      return null;
    } finally {
      refreshPromise = null;
    }
  })();
  return refreshPromise;
}

function buildUrl(path: string): string {
  if (path.startsWith('http://') || path.startsWith('https://')) return path;
  return `${API_BASE}${path.startsWith('/') ? path : `/${path}`}`;
}

function extractMessage(data: unknown, fallback: string): string {
  if (data && typeof data === 'object') {
    const detail = (data as { detail?: unknown }).detail;
    if (typeof detail === 'string') return detail;
    if (Array.isArray(detail) && detail.length > 0) {
      const first = detail[0] as { msg?: string };
      if (first && typeof first.msg === 'string') return first.msg;
    }
  }
  return fallback;
}

export async function apiRequest<T = unknown>(path: string, options: RequestOptions = {}): Promise<T> {
  const { body, headers, skipAuth, skipRefresh, ...rest } = options;
  const doFetch = async (token: string | null) => {
    const finalHeaders: Record<string, string> = {
      Accept: 'application/json',
      ...(headers ?? {}),
    };
    if (body !== undefined && !(body instanceof FormData)) {
      finalHeaders['Content-Type'] = 'application/json';
    }
    if (!skipAuth && token) {
      finalHeaders['Authorization'] = `Bearer ${token}`;
    }
    return fetch(buildUrl(path), {
      ...rest,
      headers: finalHeaders,
      body: body === undefined ? undefined : body instanceof FormData ? body : JSON.stringify(body),
    });
  };

  let response = await doFetch(skipAuth ? null : authStore.getAccessToken());

  if (response.status === 401 && !skipAuth && !skipRefresh) {
    const newToken = await performRefresh();
    if (newToken) {
      response = await doFetch(newToken);
    }
  }

  if (!response.ok) {
    let data: unknown = null;
    try {
      data = await response.json();
    } catch {
      try {
        data = await response.text();
      } catch {
        data = null;
      }
    }
    if (response.status === 401) {
      authStore.clear();
    }
    throw new ApiError(extractMessage(data, `请求失败: ${response.status}`), response.status, data);
  }

  if (response.status === 204) {
    return undefined as T;
  }

  const contentType = response.headers.get('content-type') ?? '';
  if (contentType.includes('application/json')) {
    return (await response.json()) as T;
  }
  return (await response.text()) as unknown as T;
}
