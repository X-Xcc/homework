import { NavLink, Link } from 'react-router-dom';

const adminNavItems = [
  { to: '/admin', label: '仪表板', description: '查看系统概览与统计', end: true },
  { to: '/admin/users', label: '用户管理', description: '管理用户账号与权限' },
  { to: '/admin/analyses', label: '分析记录', description: '查看所有合同分析' },
  { to: '/admin/comparisons', label: '对比记录', description: '查看所有文档对比' },
  { to: '/admin/chat-sessions', label: '聊天会话', description: '查看所有问答会话' },
  { to: '/admin/favorites', label: '收藏管理', description: '查看所有收藏条目' },
  { to: '/admin/templates', label: '模板管理', description: '管理合同模板库' },
  { to: '/admin/audit-logs', label: '操作日志', description: '查看系统操作记录' },
  { to: '/admin/settings', label: '系统设置', description: '配置系统参数' },
];

export function AdminSidebarNav() {
  return (
    <aside className="hidden w-64 shrink-0 rounded-3xl border border-slate-800 bg-slate-900/80 p-4 backdrop-blur lg:block">
      <div className="mb-4 px-2">
        <div className="text-sm font-semibold text-slate-300">后台管理</div>
      </div>
      <nav className="space-y-1">
        {adminNavItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            end={item.end}
            className={({ isActive }) =>
              [
                'block rounded-2xl px-3 py-2.5 transition',
                isActive
                  ? 'bg-brand-600/20 text-brand-400'
                  : 'text-slate-400 hover:bg-slate-800 hover:text-slate-200',
              ].join(' ')
            }
          >
            <div className="text-sm font-medium">{item.label}</div>
            <div className="mt-0.5 text-xs text-slate-500">{item.description}</div>
          </NavLink>
        ))}
      </nav>
      <div className="mt-4 border-t border-slate-800 pt-4 px-2">
        <Link
          to="/dashboard"
          className="flex items-center gap-2 rounded-2xl px-3 py-2.5 text-sm text-slate-500 transition hover:bg-slate-800 hover:text-slate-300"
        >
          <span>←</span>
          <span>返回前台</span>
        </Link>
      </div>
    </aside>
  );
}
