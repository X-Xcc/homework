import { Outlet } from 'react-router-dom';
import { AppHeader } from '@/shared/layouts/AppHeader';
import { SidebarNav } from '@/shared/layouts/SidebarNav';

export function AppShell() {
  return (
    <div className="min-h-screen bg-slate-50 text-slate-900">
      <AppHeader />
      <div className="mx-auto flex min-h-[calc(100vh-72px)] max-w-[1600px] gap-6 px-4 py-6 lg:px-6">
        <SidebarNav />
        <main className="min-w-0 flex-1">
          <Outlet />
        </main>
      </div>
    </div>
  );
}
