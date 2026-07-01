import React, { useState } from 'react';
import { useLocation } from 'react-router-dom';
import { Play, Bell, Sun, Moon, Search, ChevronRight, ExternalLink } from 'lucide-react';
import { useTheme } from '@/contexts/ThemeContext';
import { useToast } from '@/contexts/ToastContext';

const routeTitles: Record<string, { title: string; crumbs: string[] }> = {
  '/dashboard': { title: 'Dashboard', crumbs: [] },
  '/jobs': { title: 'Jobs', crumbs: ['Jobs'] },
  '/keywords': { title: 'Keywords', crumbs: ['Keywords'] },
  '/sources': { title: 'Sources', crumbs: ['Sources'] },
  '/connections': { title: 'Connections', crumbs: ['Connections'] },
  '/logs': { title: 'Logs', crumbs: ['Logs'] },
  '/health': { title: 'System Health', crumbs: ['Health'] },
  '/settings': { title: 'Settings', crumbs: ['Settings'] },
};

const TopNav: React.FC = () => {
  const location = useLocation();
  const { theme, toggleTheme } = useTheme();
  const { toast } = useToast();
  const [searchOpen, setSearchOpen] = useState(false);

  const routeInfo = routeTitles[location.pathname] ?? { title: 'Dashboard', crumbs: [] };

  const handleRunScraper = async () => {
    try {
      const resp = await fetch('/api/dispatch', { method: 'POST' });
      if (resp.ok) {
        toast('success', 'Scraper triggered', 'The scraper workflow has been dispatched on GitHub Actions.');
      } else {
        const err = await resp.json().catch(() => ({ error: 'Unknown error' }));
        toast('error', 'Failed to trigger', err.error || 'Unknown error');
      }
    } catch {
      toast('error', 'Network error', 'Could not reach the dispatch endpoint.');
    }
  };

  return (
    <header className="h-[72px] flex items-center justify-between px-6 border-b border-[#27272A] bg-[#09090B] shrink-0">
      {/* Left: Title + Breadcrumb */}
      <div>
        <div className="flex items-center gap-1.5 text-xs text-[#71717A] mb-0.5">
          <span>JobScrape AI</span>
          {routeInfo.crumbs.map((crumb, i) => (
            <React.Fragment key={i}>
              <ChevronRight size={10} />
              <span>{crumb}</span>
            </React.Fragment>
          ))}
        </div>
        <h1 className="text-base font-semibold text-[#FAFAFA] leading-tight">{routeInfo.title}</h1>
      </div>

      {/* Right: Actions */}
      <div className="flex items-center gap-2">
        {/* Search */}
        <div className="relative">
          {searchOpen ? (
            <input
              autoFocus
              onBlur={() => setSearchOpen(false)}
              placeholder="Search..."
              className="h-8 pl-8 pr-3 text-sm bg-[#18181B] border border-[#27272A] rounded-md text-[#FAFAFA] placeholder:text-[#71717A] outline-none focus:border-blue-500/50 w-48 transition-all"
            />
          ) : (
            <button
              onClick={() => setSearchOpen(true)}
              className="h-8 w-8 flex items-center justify-center rounded-md text-[#71717A] hover:text-[#A1A1AA] hover:bg-[#18181B] transition-colors"
            >
              <Search size={16} />
            </button>
          )}
          {searchOpen && (
            <Search size={14} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[#71717A]" />
          )}
        </div>

        {/* Run Scraper */}
        <button
          onClick={handleRunScraper}
          className="flex items-center gap-2 h-8 px-3 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors"
        >
          <ExternalLink size={13} />
          Run Scraper
        </button>

        {/* Notifications */}
        <button className="h-8 w-8 flex items-center justify-center rounded-md text-[#71717A] hover:text-[#A1A1AA] hover:bg-[#18181B] transition-colors relative">
          <Bell size={16} />
          <span className="absolute top-1.5 right-1.5 w-1.5 h-1.5 rounded-full bg-blue-500" />
        </button>

        {/* Theme Toggle */}
        <button
          onClick={toggleTheme}
          className="h-8 w-8 flex items-center justify-center rounded-md text-[#71717A] hover:text-[#A1A1AA] hover:bg-[#18181B] transition-colors"
        >
          {theme === 'dark' ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        {/* Profile */}
        <div className="h-8 w-8 rounded-full bg-blue-600/20 border border-blue-500/30 flex items-center justify-center text-xs font-semibold text-blue-400 cursor-pointer">
          JS
        </div>
      </div>
    </header>
  );
};

export default TopNav;
