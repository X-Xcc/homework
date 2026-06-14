import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { PageContainer } from '@/shared/layouts/PageContainer';

const favorites = [
  { type: '法条', title: '民法典第四百六十五条', user: '张三', createdAt: '2026-06-10' },
  { type: '报告', title: '采购合同风险报告', user: '李四', createdAt: '2026-06-09' },
  { type: '法条', title: '劳动合同法第三十九条', user: '王五', createdAt: '2026-06-08' },
];

export function AdminFavoritesPage() {
  return (
    <PageContainer className="space-y-6 max-w-none">
      <div>
        <Badge tone="brand">后台管理</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-white">收藏管理</h1>
      </div>
      <div className="grid gap-4 lg:grid-cols-3">
        {favorites.map((item) => (
          <Card key={`${item.user}-${item.title}`} className="border-slate-800 bg-slate-900 text-white shadow-none">
            <Badge tone="brand">{item.type}</Badge>
            <div className="mt-3 text-lg font-semibold">{item.title}</div>
            <div className="mt-4 text-sm text-slate-400">收藏用户：{item.user}</div>
            <div className="mt-1 text-sm text-slate-500">收藏时间：{item.createdAt}</div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
