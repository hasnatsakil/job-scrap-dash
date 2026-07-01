import React, { Suspense, useState } from 'react';
import Sidebar from './Sidebar';
import TopNav from './TopNav';

const PageSkeleton: React.FC = () => (
  <div className="p-6 space-y-4 animate-pulse">
    <div className="h-6 w-48 bg-[var(--c-pill)] rounded" />
    <div className="grid grid-cols-4 gap-4">
      {Array.from({ length: 4 }).map((_, i) => (
        <div key={i} className="h-24 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />
      ))}
    </div>
    <div className="h-64 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />
  </div>
);

const Layout: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [collapsed, setCollapsed] = useState(false);

  return (
    <div className="flex h-screen overflow-hidden bg-[var(--c-bg)]">
      <Sidebar collapsed={collapsed} onToggle={() => setCollapsed(c => !c)} />
      <div className="flex flex-col flex-1 overflow-hidden">
        <TopNav />
        <main className="flex-1 overflow-y-auto">
          <div className="max-w-[1600px] mx-auto p-6">
            <Suspense fallback={<PageSkeleton />}>
              {children}
            </Suspense>
          </div>
        </main>
      </div>
    </div>
  );
};

export default Layout;
