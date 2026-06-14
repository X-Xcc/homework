/**
 * 用户域 API。
 */
import { apiRequest } from './client';
import type { CurrentUser, TokenPair } from './auth-store';

export type LoginPayload = { account: string; password: string };
export type RegisterPayload = {
  username: string;
  password: string;
  email?: string;
  nickname?: string;
};

export const authApi = {
  login(payload: LoginPayload) {
    return apiRequest<TokenPair>('/api/user/login', {
      method: 'POST',
      body: payload,
      skipAuth: true,
      skipRefresh: true,
    });
  },
  register(payload: RegisterPayload) {
    return apiRequest<TokenPair>('/api/user/register', {
      method: 'POST',
      body: payload,
      skipAuth: true,
      skipRefresh: true,
    });
  },
  refresh(refresh_token: string) {
    return apiRequest<TokenPair>('/api/user/refresh', {
      method: 'POST',
      body: { refresh_token },
      skipAuth: true,
      skipRefresh: true,
    });
  },
  me() {
    return apiRequest<CurrentUser>('/api/user/me');
  },
  logout() {
    return apiRequest<{ message: string }>('/api/user/logout', { method: 'POST' });
  },
  meStats() {
    return apiRequest<{
      id: string;
      analysis_count: number;
      chat_count: number;
      favorite_count: number;
      comparison_count: number;
    }>('/api/user/me/stats');
  },
};

export type AdminUserListResponse = {
  items: Array<{
    id: string;
    username?: string | null;
    email?: string | null;
    nickname?: string | null;
    role: string;
    status: string;
    created_at?: string | null;
    last_login_at?: string | null;
    analysis_count: number;
    chat_count: number;
  }>;
  total: number;
  page: number;
  page_size: number;
};

export const adminApi = {
  listUsers(params: { page?: number; page_size?: number; keyword?: string; role?: string; status?: string } = {}) {
    const search = new URLSearchParams();
    if (params.page) search.set('page', String(params.page));
    if (params.page_size) search.set('page_size', String(params.page_size));
    if (params.keyword) search.set('keyword', params.keyword);
    if (params.role) search.set('role', params.role);
    if (params.status) search.set('status', params.status);
    const query = search.toString();
    return apiRequest<AdminUserListResponse>(`/api/admin/users${query ? `?${query}` : ''}`);
  },
  updateUser(userId: string, payload: { role?: string; status?: string; nickname?: string; password?: string }) {
    return apiRequest<AdminUserListResponse['items'][number]>(`/api/admin/users/${userId}`, {
      method: 'PATCH',
      body: payload,
    });
  },
  stats() {
    return apiRequest<{
      user_total: number;
      user_active: number;
      user_admin: number;
      analysis_total: number;
      comparison_total: number;
      chat_session_total: number;
      favorite_total: number;
      recent_24h_signups: number;
    }>('/api/admin/stats');
  },
};
