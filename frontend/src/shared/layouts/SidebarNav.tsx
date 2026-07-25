import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/dashboard', label: '工作台', description: '查看统计与继续已有工作' },
  { to: '/contracts/analyze', label: '合同分析', description: '上传合同提取风险' },
  { to: '/contracts/compare', label: '合同对比', description: '比较两份合同差异' },
  { to: '/search', label: '法条检索', description: '检索民法典与刑法条文' },
  { to: '/chat', label: '智能问答', description: '向 AI 法律顾问提问' },
  { to: '/history', label: '历史记录', description: '查看分析与问答记录' },
  { to: '/favorites', label: '我的收藏', description: '收藏法条与分析报告' },
  { to: '/templates', label: '合同模板', description: '常用合同模板下载' },
];

export function SidebarNav() {
  return (
    <aside className="hidden w-64 shrink-0 rounded-3xl border border-slate-200 bg-white/80 p-4 shadow-soft backdrop-blur lg:block">
      <div className="mb-4 px-2">
        <div className="text-sm font-semibold text-slate-900">功能导航</div>
      </div>
      <nav className="space-y-1">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.to === '/dashboard'}
            className={({ isActive }) =>
              [
                'block rounded-2xl px-3 py-2.5 transition',
                isActive
                  ? 'bg-brand-50 text-brand-700'
                  : 'text-slate-600 hover:bg-slate-50',
              ].join(' ')
            }
          >
            <div className="text-sm font-medium">{item.label}</div>
            <div className="mt-0.5 text-xs text-slate-400">{item.description}</div>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}