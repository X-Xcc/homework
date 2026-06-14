import { Navigate, Outlet, createBrowserRouter } from 'react-router-dom';
import { UserLayout } from '@/app/layouts/UserLayout';
import { AdminLayout } from '@/app/layouts/AdminLayout';
import { AuthLayout } from '@/app/layouts/AuthLayout';
import { AuthGuard, GuestOnly } from '@/app/providers/AuthGuard';
import { LoginPage } from '@/pages/user/LoginPage';
import { RegisterPage } from '@/pages/user/RegisterPage';
import { DashboardPage } from '@/pages/user/DashboardPage';
import { MaterialDetailPage } from '@/pages/user/MaterialDetailPage';
import { CaseWorkspacePage } from '@/pages/user/CaseWorkspacePage';
import { ContractAnalyzePage } from '@/pages/user/ContractAnalyzePage';
import { ContractComparePage } from '@/pages/user/ContractComparePage';
import { LawSearchPage } from '@/pages/user/LawSearchPage';
import { ChatAssistantPage } from '@/pages/user/ChatAssistantPage';
import { HistoryPage } from '@/pages/user/HistoryPage';
import { FavoritesPage } from '@/pages/user/FavoritesPage';
import { ProfilePage } from '@/pages/user/ProfilePage';
import { AdminDashboardPage } from '@/pages/admin/AdminDashboardPage';
import { AdminUsersPage } from '@/pages/admin/AdminUsersPage';
import { AdminAnalysesPage } from '@/pages/admin/AdminAnalysesPage';
import { AdminComparisonsPage } from '@/pages/admin/AdminComparisonsPage';
import { AdminChatSessionsPage } from '@/pages/admin/AdminChatSessionsPage';
import { AdminFavoritesPage } from '@/pages/admin/AdminFavoritesPage';
import { AdminTemplatesPage } from '@/pages/admin/AdminTemplatesPage';
import { AdminAuditLogsPage } from '@/pages/admin/AdminAuditLogsPage';
import { AdminSettingsPage } from '@/pages/admin/AdminSettingsPage';

function guardOutlet() {
  return (
    <AuthGuard>
      <Outlet />
    </AuthGuard>
  );
}

function guardAdminOutlet() {
  return (
    <AuthGuard requireAdmin>
      <Outlet />
    </AuthGuard>
  );
}

function guestOnlyOutlet() {
  return (
    <GuestOnly>
      <Outlet />
    </GuestOnly>
  );
}

export const router = createBrowserRouter([
  {
    path: '/',
    element: <Navigate to="/dashboard" replace />,
  },
  {
    element: <AuthLayout />,
    children: [
      {
        element: guestOnlyOutlet(),
        children: [
          { path: '/login', element: <LoginPage /> },
          { path: '/register', element: <RegisterPage /> },
        ],
      },
    ],
  },
  {
    element: <UserLayout />,
    children: [
      {
        element: guardOutlet(),
        children: [
          { path: '/dashboard', element: <DashboardPage /> },
          { path: '/materials/:materialId', element: <MaterialDetailPage /> },
          { path: '/cases/:caseId/workspace', element: <CaseWorkspacePage /> },
          { path: '/contracts/analyze', element: <ContractAnalyzePage /> },
          { path: '/contracts/compare', element: <ContractComparePage /> },
          { path: '/search', element: <LawSearchPage /> },
          { path: '/chat', element: <ChatAssistantPage /> },
          { path: '/history', element: <HistoryPage /> },
          { path: '/favorites', element: <FavoritesPage /> },
          { path: '/profile', element: <ProfilePage /> },
        ],
      },
    ],
  },
  {
    path: '/admin',
    element: <AdminLayout />,
    children: [
      {
        element: guardAdminOutlet(),
        children: [
          { index: true, element: <AdminDashboardPage /> },
          { path: 'users', element: <AdminUsersPage /> },
          { path: 'analyses', element: <AdminAnalysesPage /> },
          { path: 'comparisons', element: <AdminComparisonsPage /> },
          { path: 'chat-sessions', element: <AdminChatSessionsPage /> },
          { path: 'favorites', element: <AdminFavoritesPage /> },
          { path: 'templates', element: <AdminTemplatesPage /> },
          { path: 'audit-logs', element: <AdminAuditLogsPage /> },
          { path: 'settings', element: <AdminSettingsPage /> },
        ],
      },
    ],
  },
]);
