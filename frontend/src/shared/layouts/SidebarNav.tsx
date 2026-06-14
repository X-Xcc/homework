import { NavLink } from 'react-router-dom';

const navItems = [
  { to: '/dashboard', label: '工作台首页', description: '继续已有工作与快速新建' },
  { to: '/materials/material-001', label: '材料详情', description: '阅读材料并触发 AI 提炼' },
  { to: '/cases/case-001/workspace', label: '案件工作区', description: '整理争点、证据与分析' },
];

export function SidebarNav() {
  return (
    <aside className="hidden w-72 shrink-0 rounded-3xl border border-slate-200 bg-white/80 p-4 shadow-soft backdrop-blur lg:block">
      <div className="mb-4 px-2">
        <div className="text-sm font-semibold text-slate-900">MVP 导航</div>
        <p className="mt-1 text-sm text-slate-500">先用 Mock 数据跑通三大核心页面。</p>
      </div>
      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              [
                'block rounded-2xl border px-4 py-3 transition',
                isActive
                  ? 'border-brand-200 bg-brand-50 text-brand-700'
                  : 'border-transparent bg-slate-50 text-slate-700 hover:border-slate-200 hover:bg-white',
              ].join(' ')
            }
          >
            <div className="text-sm font-semibold">{item.label}</div>
            <div className="mt-1 text-sm text-slate-500">{item.description}</div>
          </NavLink>
        ))}
      </nav>
    </aside>
  );
}
