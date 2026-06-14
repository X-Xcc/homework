import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { EmptyState } from '@/shared/ui/EmptyState';

const mockFavorites = [
  { id: '1', type: '法条', title: '《民法典》第四百六十五条', summary: '合同受法律保护的相关规定' },
  { id: '2', type: '法条', title: '《合同法》第六十条', summary: '全面履行与诚实信用原则' },
  { id: '3', type: '分析', title: '租赁合同_风险报告', summary: '共发现 5 处风险点，高风险 2 处' },
];

export function FavoritesPage() {
  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">我的收藏</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">收藏夹</h1>
        <p className="mt-1 text-sm text-slate-500">收藏常用法条、分析报告与模板。</p>
      </div>

      <Card>
        {mockFavorites.length > 0 ? (
          <div className="space-y-3">
            {mockFavorites.map((item) => (
              <div key={item.id} className="flex items-center justify-between rounded-2xl border border-slate-100 p-4 transition hover:border-brand-200 hover:bg-brand-50/20">
                <div className="flex items-center gap-4">
                  <div className="text-2xl">{item.type === '法条' ? '⚖️' : '📄'}</div>
                  <div>
                    <div className="font-medium text-slate-800">{item.title}</div>
                    <div className="mt-1 text-sm text-slate-400">{item.summary}</div>
                  </div>
                </div>
                <div className="flex gap-2">
                  <Button variant="ghost" size="sm">查看</Button>
                  <Button variant="ghost" size="sm" className="text-red-500">取消收藏</Button>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <EmptyState title="暂无收藏" description="收藏常用法条和分析报告以便快速访问。" />
        )}
      </Card>
    </PageContainer>
  );
}
