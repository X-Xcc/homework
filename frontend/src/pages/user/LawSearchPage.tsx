import { useState, useEffect, useCallback } from 'react';
import { useSearchParams } from 'react-router-dom';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';
import { Skeleton } from '@/shared/ui/Skeleton';
import { EmptyState } from '@/shared/ui/EmptyState';
import { apiRequest } from '@/shared/api/client';

type LawArticle = {
  id: string;
  law_name: string;
  chapter?: string | null;
  article_number: string;
  title?: string | null;
  content: string;
  judicial_interpretations?: string[];
  related_cases?: string[];
  distance?: number;
};

export function LawSearchPage() {
  const [searchParams] = useSearchParams();
  const urlQuery = searchParams.get('q') || '';
  const [keyword, setKeyword] = useState('');
  const [category, setCategory] = useState('');
  const [lawName, setLawName] = useState('');
  const [results, setResults] = useState<LawArticle[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [searched, setSearched] = useState(false);
  const [semantic, setSemantic] = useState(false);

  // Dynamic data from API
  const [categories, setCategories] = useState<string[]>([]);
  const [lawNames, setLawNames] = useState<string[]>([]);
  const [categoriesLoading, setCategoriesLoading] = useState(true);

  // Load categories on mount
  useEffect(() => {
    apiRequest<{ categories: string[] }>('/api/search/categories')
      .then((data) => {
        setCategories(data.categories || []);
      })
      .catch(() => {
        setCategories(['民法基础', 'AI运营合规', '数据安全', '商事法规', '行业专项', '刑事风险', '涉外法规']);
      })
      .finally(() => setCategoriesLoading(false));
  }, []);

  const doSearch = useCallback(async () => {
    const q = keyword.trim();
    if (!q) return;
    setLoading(true);
    setError(null);
    setSearched(true);
    try {
      if (semantic) {
        const params = new URLSearchParams({ q, limit: '20' });
        if (category) params.set('category', category);
        const data = await apiRequest<{ results: Array<{ id: string; content: string; metadata: { law_name?: string; article_number?: string; title?: string; judicial_interpretations?: string[] }; distance: number }> }>(
          `/api/search/similar?${params.toString()}`,
        );
        const mapped: LawArticle[] = data.results.map((r) => ({
          id: r.id,
          law_name: r.metadata.law_name ?? '',
          article_number: r.metadata.article_number ?? '',
          title: r.metadata.title,
          content: r.content,
          judicial_interpretations: r.metadata.judicial_interpretations,
          distance: r.distance,
        }));
        setResults(mapped);
      } else {
        const params = new URLSearchParams({ q, limit: '50' });
        if (category) params.set('category', category);
        const data = await apiRequest<LawArticle[]>(`/api/search/law?${params.toString()}`);
        setResults(data);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : '检索失败');
      setResults([]);
    } finally {
      setLoading(false);
    }
  }, [keyword, category, semantic]);

  // Extract unique law names from results for second-level filter
  useEffect(() => {
    if (results.length > 0) {
      const names = [...new Set(results.map((r) => r.law_name))].sort();
      setLawNames(names);
    } else {
      setLawNames([]);
    }
  }, [results]);

  // Auto-search when URL has q param
  useEffect(() => {
    if (urlQuery && !keyword && !searched) {
      setKeyword(urlQuery);
      setTimeout(() => {
        const q = urlQuery.trim();
        if (!q) return;
        setLoading(true);
        setError(null);
        setSearched(true);
        const params2 = new URLSearchParams({ q, limit: '50' });
        apiRequest<LawArticle[]>('/api/search/law?' + params2.toString())
          .then((data) => { setResults(data); setLoading(false); })
          .catch((err) => { setError(err instanceof Error ? err.message : '检索失败'); setResults([]); setLoading(false); });
      }, 0);
    }
  }, [urlQuery]);

  // Apply law name filter on top of results
  const filteredResults = lawName
    ? results.filter((r) => r.law_name === lawName)
    : results;

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter') doSearch();
  };

  const clearFilters = () => {
    setCategory('');
    setLawName('');
  };

  const hasActiveFilters = category || lawName;

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">法条检索</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">法律条文检索</h1>
        <p className="mt-1 text-sm text-slate-500">支持关键词与语义相似度检索，可按分类和法律名筛选。</p>
      </div>

      <Card>
        {/* Search bar */}
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="输入关键词，例如：格式条款、违约金、个人信息保护"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            onKeyDown={handleKeyDown}
            className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
          <Button onClick={doSearch} loading={loading}>检索</Button>
        </div>

        {/* Filters panel */}
        <div className="mt-4 space-y-3">
          {/* Category filter row */}
          <div className="flex flex-wrap items-center gap-2">
            <span className="text-xs font-medium text-slate-400 w-10 shrink-0">分类</span>
            {categoriesLoading ? (
              <Skeleton className="h-7 w-40" />
            ) : (
              <>
                <button
                  onClick={() => { setCategory(''); setLawName(''); }}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                    !category
                      ? 'bg-brand-600 text-white'
                      : 'border border-slate-200 text-slate-500 hover:bg-slate-50'
                  }`}
                >
                  全部
                </button>
                {categories.map((cat) => (
                  <button
                    key={cat}
                    onClick={() => { setCategory(category === cat ? '' : cat); setLawName(''); }}
                    className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                      category === cat
                        ? 'bg-brand-600 text-white'
                        : 'border border-slate-200 text-slate-500 hover:bg-slate-50'
                    }`}
                  >
                    {cat}
                  </button>
                ))}
              </>
            )}
          </div>

          {/* Law name filter row — shown only when results exist */}
          {lawNames.length > 0 && (
            <div className="flex flex-wrap items-center gap-2 pt-2 border-t border-slate-100">
              <span className="text-xs font-medium text-slate-400 w-10 shrink-0">法律</span>
              <button
                onClick={() => setLawName('')}
                className={`rounded-full px-3 py-1 text-xs font-medium transition ${
                  !lawName
                    ? 'bg-slate-700 text-white'
                    : 'border border-slate-200 text-slate-500 hover:bg-slate-50'
                }`}
              >
                全部
              </button>
              {lawNames.map((name) => (
                <button
                  key={name}
                  onClick={() => setLawName(lawName === name ? '' : name)}
                  className={`rounded-full px-3 py-1 text-xs font-medium transition max-w-48 truncate ${
                    lawName === name
                      ? 'bg-slate-700 text-white'
                      : 'border border-slate-200 text-slate-500 hover:bg-slate-50'
                  }`}
                  title={name}
                >
                  {name.length > 16 ? name.slice(0, 14) + '...' : name}
                </button>
              ))}
            </div>
          )}

          {/* Bottom bar */}
          <div className="flex items-center gap-3 pt-2 border-t border-slate-100">
            {searched && !loading && (
              <span className="text-xs text-slate-400">
                {category || lawName
                  ? `筛选后 ${filteredResults.length} 条结果`
                  : `共 ${results.length} 条结果`}
              </span>
            )}
            {hasActiveFilters && (
              <button onClick={clearFilters} className="text-xs text-brand-600 hover:underline">
                清除筛选
              </button>
            )}
            <div className="ml-auto flex items-center gap-2">
              <span className="text-xs text-slate-400">语义检索</span>
              <button
                onClick={() => setSemantic((v) => !v)}
                className={`relative inline-flex h-6 w-11 items-center rounded-full transition ${
                  semantic ? 'bg-brand-600' : 'bg-slate-300'
                }`}
              >
                <span
                  className={`inline-block h-4 w-4 transform rounded-full bg-white transition ${
                    semantic ? 'translate-x-6' : 'translate-x-1'
                  }`}
                />
              </button>
            </div>
          </div>
        </div>
      </Card>

      {loading ? (
        <div className="space-y-3">
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
          <Skeleton className="h-24" />
        </div>
      ) : error ? (
        <EmptyState title="检索失败" description={error} />
      ) : searched && filteredResults.length === 0 ? (
        <EmptyState
          title={lawName || category ? '筛选后无结果' : '未找到相关条文'}
          description={lawName || category ? '请尝试放宽筛选条件。' : '请尝试更换关键词或筛选条件。'}
        />
      ) : filteredResults.length > 0 ? (
        <div className="space-y-3">
          {filteredResults.map((r) => (
            <Card key={r.id}>
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-2 flex-wrap">
                    <Badge tone="neutral">{r.law_name}</Badge>
                    <span className="text-sm font-semibold text-slate-800">
                      {r.chapter ? `${r.chapter} · ` : ''}{r.article_number}
                    </span>
                    {r.title ? <span className="text-sm text-slate-500">— {r.title}</span> : null}
                    {r.distance != null && (
                      <Badge tone="brand" className="text-xs">
                        相关度 {Math.round((1 - r.distance) * 100)}%
                      </Badge>
                    )}
                  </div>
                  <p className="text-sm leading-7 text-slate-600">{r.content}</p>
                  {r.judicial_interpretations && r.judicial_interpretations.length > 0 && (
                    <div className="mt-3">
                      <div className="text-xs font-medium text-slate-400 mb-1">司法解释</div>
                      <ul className="list-disc list-inside space-y-1">
                        {r.judicial_interpretations.map((interp, i) => (
                          <li key={i} className="text-xs text-slate-500">{interp}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                  {r.related_cases && r.related_cases.length > 0 && (
                    <div className="mt-2">
                      <div className="text-xs font-medium text-slate-400 mb-1">相关案例</div>
                      <ul className="list-disc list-inside space-y-1">
                        {r.related_cases.map((c, i) => (
                          <li key={i} className="text-xs text-slate-500">{c}</li>
                        ))}
                      </ul>
                    </div>
                  )}
                </div>
              </div>
            </Card>
          ))}
        </div>
      ) : (
        <EmptyState title="开始检索" description="输入关键词后点击检索，即可查找相关法律条文。" />
      )}
    </PageContainer>
  );
}
