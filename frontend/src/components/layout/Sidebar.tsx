import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { useLocation, Link } from 'react-router-dom';
import {
  LayoutDashboard, Briefcase, Tag, Globe, Link as LinkIcon,
  FileText, Activity, Settings, ChevronLeft, ChevronRight,
  Zap, Bot
} from 'lucide-react';
import { useQuery } from '@tanstack/react-query';
import { supabase } from '@/lib/supabaseClient';

interface SidebarProps {
  collapsed: boolean;
  onToggle: () => void;
}

const navItems = [
  { icon: LayoutDashboard, label: 'Dashboard', path: '/dashboard' },
  { icon: Briefcase, label: 'Jobs', path: '/jobs' },
  { icon: Tag, label: 'Keywords', path: '/keywords' },
  { icon: FileText, label: 'Logs', path: '/logs' },
  { icon: Activity, label: 'Health', path: '/health' },
  { icon: Settings, label: 'Settings', path: '/settings' },
];

const StatusPill: React.FC<{ label: string; ok: boolean; collapsed: boolean }> = ({ label, ok, collapsed }) => (
  <div className="flex items-center gap-2 px-2 py-1.5">
    <div className={`w-1.5 h-1.5 rounded-full shrink-0 ${ok ? 'bg-green-500' : 'bg-red-500'}`} />
    <AnimatePresence>
      {!collapsed && (
        <motion.span
          initial={{ opacity: 0, width: 0 }}
          animate={{ opacity: 1, width: 'auto' }}
          exit={{ opacity: 0, width: 0 }}
          transition={{ duration: 0.15 }}
          className="text-xs text-[var(--c-text3)] whitespace-nowrap overflow-hidden"
        >
          {label}
        </motion.span>
      )}
    </AnimatePresence>
  </div>
);

const Sidebar: React.FC<SidebarProps> = ({ collapsed, onToggle }) => {
  const location = useLocation();

  const { data: health } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      try {
        const { data: run } = await supabase.from('scraper_runs').select('*').order('created_at', { ascending: false }).limit(1).single();
        return { scheduler_status: run?.status || 'Idle', database_configured: true, ai_budget_used: 0, ai_budget_total: 100 };
      } catch { return {}; }
    },
    refetchInterval: 30000,
    staleTime: 15000,
  });

  const schedulerOk = health?.scheduler_status === 'Running';
  const sheetsOk = !!health?.database_configured;
  const aiOk = (health?.ai_budget_used ?? 0) < (health?.ai_budget_total ?? 1);

  return (
    <motion.div
      animate={{ width: collapsed ? 64 : 280 }}
      transition={{ duration: 0.2, ease: 'easeInOut' }}
      className="relative flex flex-col h-screen bg-[var(--c-bg)] border-r border-[var(--c-border)] shrink-0 overflow-hidden"
    >
      {/* Logo */}
      <div className="flex items-center gap-3 px-4 h-[72px] border-b border-[var(--c-border)] shrink-0">
        <div className="w-8 h-8 flex items-center justify-center shrink-0">
          <img src="/favicon.svg" alt="Logo" className="w-6 h-6" />
        </div>
        <AnimatePresence>
          {!collapsed && (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              transition={{ duration: 0.15 }}
              className="overflow-hidden"
            >
              <span className="font-semibold text-[var(--c-text)] text-sm whitespace-nowrap">JobScrape AI</span>
            </motion.div>
          )}
        </AnimatePresence>
      </div>

      {/* Nav */}
      <nav className="flex-1 py-3 overflow-y-auto overflow-x-hidden">
        {navItems.map(({ icon: Icon, label, path }) => {
          const active = location.pathname === path;
          return (
            <Link
              key={path}
              to={path}
              title={collapsed ? label : undefined}
              className={`flex items-center gap-3 mx-2 px-3 py-2 rounded-md mb-0.5 transition-all duration-150 group ${
                active
                  ? 'bg-[var(--c-pill)] text-[var(--c-text)]'
                  : 'text-[var(--c-text3)] hover:bg-[var(--c-card)] hover:text-[var(--c-text2)]'
              }`}
            >
              <Icon size={18} className="shrink-0" />
              <AnimatePresence>
                {!collapsed && (
                  <motion.span
                    initial={{ opacity: 0, width: 0 }}
                    animate={{ opacity: 1, width: 'auto' }}
                    exit={{ opacity: 0, width: 0 }}
                    transition={{ duration: 0.15 }}
                    className="text-sm font-medium whitespace-nowrap overflow-hidden"
                  >
                    {label}
                  </motion.span>
                )}
              </AnimatePresence>
              {active && (
                <motion.div
                  layoutId="activeIndicator"
                  className="absolute left-0 w-0.5 h-5 bg-blue-500 rounded-r-full"
                />
              )}
            </Link>
          );
        })}
      </nav>

      {/* Bottom status */}
      <div className="border-t border-[var(--c-border)] p-2 space-y-0.5">
        <StatusPill label="Scheduler" ok={schedulerOk} collapsed={collapsed} />
        <StatusPill label="Database" ok={sheetsOk} collapsed={collapsed} />
        <StatusPill label="AI Budget" ok={aiOk} collapsed={collapsed} />
        {!collapsed && (
          <div className="px-2 pt-1">
            <span className="text-[10px] text-[var(--c-icon)]">v1.0.0</span>
          </div>
        )}
      </div>

      {/* Collapse toggle */}
      <button
        onClick={onToggle}
        className="absolute -right-3 top-[84px] w-6 h-6 rounded-full bg-[var(--c-pill)] border border-[var(--c-hover)] flex items-center justify-center text-[var(--c-text3)] hover:text-[var(--c-text)] transition-colors z-10"
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </motion.div>
  );
};

export default Sidebar;
