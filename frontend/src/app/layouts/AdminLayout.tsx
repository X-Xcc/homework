import { Outlet } from 'react-router-dom';
import { AppHeader } from '@/shared/layouts/AppHeader';
import { SidebarNav } from '@/shared/layouts/SidebarNav';

export function AdminLayout() {
  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <AppHeader />
      <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-[1680px] gap-6 px-4 py-6 lg:px-6">
        <SidebarNav />
        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
