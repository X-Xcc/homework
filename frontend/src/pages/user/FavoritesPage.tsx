import { useEffect, useState } from 'react';
import { Link } from 'react-router-dom';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { EmptyState } from '@/shared/ui/EmptyState';
import { Skeleton } from '@/shared/ui/Skeleton';
import { apiRequest } from '@/shared/api/client';

type FavoriteItem = {
  id: string;
  item_type: string;
  item_id: string;
  title: string | null;
  summary: string | null;
  created_at: string;
};

function formatDate(iso: string | null | undefined): string {
  if (!iso) return '';
  try {
    return new Date(iso).toLocaleDateString('zh-CN', { month: 'short', day: 'numeric' });
  } catch {
    return iso;
  }
}

export function FavoritesPage() {
  const [items, setItems] = useState<FavoriteItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [removing, setRemoving] = useState<string | null>(null);

  const fetchFavorites = async () => {
    try {
      const result = await apiRequest<FavoriteItem[]>('/api/user/favorites');
      setItems(result);
    } catch {
      // 静默处理
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    void fetchFavorites();
  }, []);

  const handleRemove = async (id: string) => {
    setRemoving(id);
    try {
      await apiRequest(`/api/user/favorites/${id}`, { method: 'DELETE' });
      setItems((prev) => prev.filter((item) => item.id !== id));
    } catch {
      // 静默处理
    } finally {
      setRemoving(null);
    }
  };

  const typeIcon = (type: string) => {
    if (type === 'law') return '⚖️';
    if (type === 'analysis') return '📄';
    return '📌';
  };

  const typeLabel = (type: string) => {
    if (type === 'law') return '法条';
    if (type === 'analysis') return '分析';
    if (type === 'template') return '模板';
    return type;
  };

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">我的收藏</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">收藏夹</h1>
        <p className="mt-1 text-sm text-slate-500">收藏常用法条、分析报告与模板。</p>
      </div>

      <Card>
        {loading ? (
          <div className="space-y-3">
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
            <Skeleton className="h-16" />
          </div>
        ) : items.length > 0 ? (
          <div className="space-y-3">
            {items.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-2xl border border-slate-100 p-4 transition hover:border-brand-200 hover:bg-brand-50/20">
                <div className="flex items-center gap-4">
                  <div className="text-2xl">{typeIcon(item.item_type)}</div>
                  <div>
                    <div className="flex items-center gap-2">
                      <Badge tone="neutral">{typeLabel(item.item_type)}</Badge>
                      <span className="font-medium text-slate-800">{item.title || '未命名'}</span>
                    </div>
                    <div className="mt-1 text-sm text-slate-400">
                      {item.summary || '暂无摘要'}
                      <span className="ml-2 text-xs text-slate-300">{formatDate(item.created_at)}</span>
                    </div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm">查看</Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    className="text-red-500"
                    disabled={removing === item.id}
                    onClick={() => handleRemove(item.id)}
                  >
                    {removing === item.id ? '移除中...' : '取消收藏'}
                  </Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState
            title="暂无收藏"
            description="收藏常用法条和分析报告以便快速访问。"
            action={
              <Link to="/search">
                <Button>去检索法条</Button>
              </Link>
            }
          />
        )}
      </Card>
    </PageContainer>
  );
}