import React, { Suspense, lazy } from 'react';
import { BrowserRouter, Routes, Route, Navigate, Link } from 'react-router-dom';
import { LayoutDashboard, Briefcase, Settings as SettingsIcon, Activity, FileText } from 'lucide-react';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
const Dashboard = lazy(() => import('./pages/Dashboard'));
const Jobs = lazy(() => import('./pages/Jobs'));
const SettingsPage = lazy(() => import('./pages/Settings'));
const Health = lazy(() => import('./pages/Health'));
const Logs = lazy(() => import('./pages/Logs'));
const queryClient = new QueryClient();
const Sidebar = () => {
  const navItems = [
    { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
    { icon: Briefcase, label: 'Jobs', path: '/jobs' },
    { icon: FileText, label: 'Logs', path: '/logs' },
    { icon: SettingsIcon, label: 'Settings', path: '/settings' },
    { icon: Activity, label: 'Health', path: '/health' },
  ];
  return (
    <div className="w-64 bg-slate-900 text-white min-h-screen p-4 flex flex-col">
      <div className="mb-8 p-2"><h1 className="text-xl font-bold text-blue-400">AI Job Scraper</h1></div>
      <nav className="flex-1 space-y-2">
        {navItems.map((item) => (
          <Link key={item.path} to={item.path} className="flex items-center space-x-3 p-3 rounded-lg hover:bg-slate-800 transition-colors">
            <item.icon size={20} /><span>{item.label}</span>
          </Link>
        ))}
      </nav>
    </div>
  );
};
const Layout = ({ children }: { children: React.ReactNode }) => (
  <div className="flex min-h-screen bg-slate-50">
    <Sidebar />
    <main className="flex-1 p-8 overflow-auto"><Suspense fallback={<div className="flex items-center justify-center h-full">Loading...</div>}>{children}</Suspense></main>
  </div>
);
export default function App() {
  return (
    <QueryClientProvider client={queryClient}>
      <BrowserRouter>
        <Layout>
          <Routes>
            <Route path="/" element={<Navigate to="/dashboard" replace />} />
            <Route path="/dashboard" element={<Dashboard />} />
            <Route path="/jobs" element={<Jobs />} />
            <Route path="/logs" element={<Logs />} />
            <Route path="/settings" element={<SettingsPage />} />
            <Route path="/health" element={<Health />} />
            <Route path="*" element={<Navigate to="/dashboard" replace />} />
          </Routes>
        </Layout>
      </BrowserRouter>
    </QueryClientProvider>
  );
}
