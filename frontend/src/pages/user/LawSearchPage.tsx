import { useState } from 'react';
import { Card } from '@/shared/ui/Card';
import { Badge } from '@/shared/ui/Badge';
import { Button } from '@/shared/ui/Button';
import { PageContainer } from '@/shared/layouts/PageContainer';

const mockResults = [
  { title: '《中华人民共和国民法典》第四百六十五条', clause: '依法成立的合同，受法律保护。', category: '民法典', relevance: 96 },
  { title: '《中华人民共和国合同法》第八条', clause: '依法成立的合同，对当事人具有法律约束力。', category: '合同法', relevance: 92 },
  { title: '《最高人民法院关于适用〈中华人民共和国合同法〉若干问题的解释》', clause: '当事人对合同条款的理解有争议的，应当依据合同所使用的词句确定其含义。', category: '司法解释', relevance: 85 },
];

const categories = ['全部', '民法典', '刑法', '合同法', '司法解释'];

export function LawSearchPage() {
  const [keyword, setKeyword] = useState('');
  const [selected, setSelected] = useState('全部');

  return (
    <PageContainer className="space-y-6">
      <div>
        <Badge tone="brand">法条检索</Badge>
        <h1 className="mt-2 text-2xl font-semibold text-slate-900">法律条文检索</h1>
        <p className="mt-1 text-sm text-slate-500">基于关键词与语义相似度检索相关法律条文。</p>
      </div>

      <Card>
        <div className="flex gap-3">
          <input
            type="text"
            placeholder="输入关键词，例如：合同 违约 解除"
            value={keyword}
            onChange={(e) => setKeyword(e.target.value)}
            className="flex-1 rounded-2xl border border-slate-200 bg-slate-50 px-4 py-3 text-sm outline-none transition focus:border-brand-300 focus:bg-white focus:ring-2 focus:ring-brand-100"
          />
          <Button>检索</Button>
        </div>
        <div className="mt-4 flex flex-wrap gap-2">
          {categories.map((cat) => (
            <button
              key={cat}
              onClick={() => setSelected(cat)}
              className={`rounded-full px-4 py-1.5 text-sm font-medium transition ${selected === cat ? 'bg-brand-600 text-white' : 'border border-slate-200 text-slate-600 hover:bg-slate-50'}`}
            >
              {cat}
            </button>
          ))}
        </div>
      </Card>

      <div className="space-y-3">
        {mockResults.map((r, i) => (
          <Card key={i}>
            <div className="flex items-start justify-between">
              <div className="flex-1">
                <div className="flex items-center gap-2 mb-2">
                  <Badge tone="neutral">{r.category}</Badge>
                  <span className="text-sm font-semibold text-slate-800">{r.title}</span>
                </div>
                <p className="text-sm leading-7 text-slate-600">{r.clause}</p>
              </div>
              <div className="ml-4 shrink-0 text-right">
                <div className="text-2xl font-bold text-brand-600">{r.relevance}</div>
                <div className="text-xs text-slate-400">相关度</div>
              </div>
            </div>
          </Card>
        ))}
      </div>
    </PageContainer>
  );
}
