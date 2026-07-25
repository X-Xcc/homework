import { useEffect, useState } from 'react';
import { Badge } from '@/shared/ui/Badge';
import { Card } from '@/shared/ui/Card';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { EmptyState } from '@/shared/ui/EmptyState';
import { apiRequest } from '@/shared/api/client';

type Template = {
  id: string;
  name: string;
  category: string;
  description: string;
  usage_count: number;
  content: string;
};

export function TemplatesPage() {
  const [templates, setTemplates] = useState<Template[]>([]);
  const [categories, setCategories] = useState<string[]>([]);
  const [selectedCategory, setSelectedCategory] = useState('');
  const [keyword, setKeyword] = useState('');
  const [loading, setLoading] = useState(true);
  const [expanded, setExpanded] = useState<string | null>(null);

  useEffect(() => {
    void apiRequest<string[]>('/api/templates/categories/list').then(setCategories).catch(() => {});
  }, []);

  useEffect(() => {
    setLoading(true);
    const params = new URLSearchParams();
    if (selectedCategory) params.set('category', selectedCategory);
    if (keyword.trim()) params.set('keyword', keyword.trim());
    const query = params.toString();
    apiRequest<Template[]>(`/api/templates${query ? `?${query}` : ''}`)
      .then(setTemplates)
      .catch(() => setTemplates([]))
      .finally(() => setLoading(false));
  }, [selectedCategory, keyword]);

  const copyToClipboard = (content: string) => {
    navigator.clipboard.writeText(content).catch(() => {});
  };

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">合同模板</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">合同模板库</h1>
        <p className="mt-1 text-sm text-slate-500">常用合同模板，可直接复制使用。</p>
      </div>

      <Card>
        <div className="flex flex-col gap-3 sm:flex-row sm:items-center">
          <input
            type="text"
            placeholder="搜索模板..."
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
        </div>
        {categories.length > 0 && (
          <div className="mt-3 flex flex-wrap gap-2">
            <button
              onClick={() => setSelectedCategory('')}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                selectedCategory === '' ? 'bg-brand-600 text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
              }`}
            >
              全部
            </button>
            {categories.map((cat) => (
              <button
                key={cat}
                onClick={() => setSelectedCategory(cat)}
                className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${
                  selectedCategory === cat ? 'bg-brand-600 text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-50'
                }`}
              >
                {cat}
              </button>
            ))}
          </div>
        )}
      </Card>

      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
          <Skeleton className="h-28" />
        </div>
      ) : templates.length > 0 ? (
        <div className="space-y-3">
          {templates.map((tpl) => (
            <Card key={tpl.id}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Badge tone="neutral">{tpl.category}</Badge>
                    <span className="text-sm font-semibold text-slate-800">{tpl.name}</span>
                    <span className="text-xs text-slate-400">{tpl.usage_count.toLocaleString()} 次使用</span>
                  </div>
                  <p className="mt-2 text-sm text-slate-500">{tpl.description}</p>
                </div>
                <div className="flex gap-2">
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => copyToClipboard(tpl.content)}
                  >
                    复制
                  </Button>
                  <Button
                    variant="ghost"
                    size="sm"
                    onClick={() => setExpanded(expanded === tpl.id ? null : tpl.id)}
                  >
                    {expanded === tpl.id ? '收起' : '预览'}
                  </Button>
                </div>
              </div>
              {expanded === tpl.id && (
                <div className="mt-4 rounded-2xl border border-slate-100 bg-slate-50 p-4">
                  <pre className="whitespace-pre-wrap text-sm leading-7 text-slate-700">{tpl.content}</pre>
                </div>
              )}
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState title="暂无模板" description="没有找到匹配的合同模板。" />
      )}
    </PageContainer>
  );
}
