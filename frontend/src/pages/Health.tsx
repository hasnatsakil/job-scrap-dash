import React from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import { Clock, CheckCircle, XCircle, AlertTriangle, Activity, Database, Brain, Globe, Server } from 'lucide-react';
import StatusDot from '@/components/ui/StatusDot';
import { supabase } from '@/lib/supabaseClient';

interface HealthSection {
  title: string;
  icon: React.ReactNode;
  items: { label: string; value: string; status?: 'green' | 'yellow' | 'red' | 'gray' }[];
}

export default function Health() {
  const { data: health, isLoading, dataUpdatedAt } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      try {
        const { count: jobCount } = await supabase.from('jobs').select('*', { count: 'exact', head: true });
        const { data: keywords } = await supabase.from('keywords').select('id');
        const { data: latestRun } = await supabase.from('scraper_runs').select('*').order('created_at', { ascending: false }).limit(1);
        const run = latestRun?.[0];
        return {
          scheduler_status: run?.status || 'Idle',
          last_scrape_attempt: run?.started_at || null,
          active_keywords: keywords?.length ?? 0,
          database_configured: true,
          ai_budget_used: 0,
          ai_budget_total: 100,
          active_sources: 4,
          connections: { linkedin: { status: 'Not Connected' } },
          total_jobs: jobCount ?? 0,
        };
      } catch {
        return {};
      }
    },
    refetchInterval: 10000,
  });

  const linkedinStatus: any = health?.connections?.linkedin;
  const li = linkedinStatus?.status;

  const lastUpdated = dataUpdatedAt ? new Date(dataUpdatedAt).toLocaleTimeString() : '—';

  const budgetUsed = health?.ai_budget_used ?? 0;
  const budgetTotal = health?.ai_budget_total ?? 1;
  const budgetPct = Math.min(100, Math.round((budgetUsed / budgetTotal) * 100));

  const sections: HealthSection[] = [
    {
      title: 'Scheduler',
      icon: <Clock size={16} className="text-blue-400" />,
      items: [
        { label: 'Status', value: health?.scheduler_status || 'Unknown', status: health?.scheduler_status === 'Running' ? 'green' : 'yellow' },
        { label: 'Last Scrape Attempt', value: health?.last_scrape_attempt || 'Never' },
        { label: 'Active Keywords', value: String(health?.active_keywords ?? 0) },
      ],
    },
    {
      title: 'Database',
      icon: <Database size={16} className="text-green-400" />,
      items: [
        { label: 'Supabase', value: health?.database_configured ? 'Connected' : 'Missing', status: health?.database_configured ? 'green' : 'red' },
      ],
    },
    {
      title: 'AI Budget',
      icon: <Brain size={16} className="text-purple-400" />,
      items: [
        { label: 'Daily Requests Used', value: `${budgetUsed} / ${budgetTotal}`, status: budgetPct > 85 ? 'red' : budgetPct > 60 ? 'yellow' : 'green' },
        { label: 'Remaining', value: `${budgetTotal - budgetUsed} requests` },
        { label: 'Usage', value: `${budgetPct}%` },
      ],
    },
    {
      title: 'Sources & Scrapers',
      icon: <Globe size={16} className="text-zinc-400" />,
      items: [
        { label: 'Active Sources', value: String(health?.active_sources ?? 0), status: (health?.active_sources ?? 0) > 0 ? 'green' : 'yellow' },
      ],
    },
    {
      title: 'LinkedIn Session',
      icon: <Activity size={16} className="text-blue-400" />,
      items: [
        { label: 'Session Status', value: li || 'Not Connected', status: li === 'Connected' ? 'green' : li === 'Expired' ? 'red' : 'gray' },
        { label: 'Last Login', value: linkedinStatus?.last_login ? new Date(linkedinStatus.last_login).toLocaleString() : '—' },
        { label: 'Last Validation', value: linkedinStatus?.last_validation ? new Date(linkedinStatus.last_validation).toLocaleString() : '—' },
      ],
    },
    {
      title: 'System',
      icon: <Server size={16} className="text-zinc-400" />,
      items: [
        { label: 'API Status', value: 'Online', status: 'green' },
        { label: 'Last Data Refresh', value: lastUpdated },
      ],
    },
  ];

  if (isLoading) {
    return (
      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4 animate-pulse">
        {Array.from({ length: 6 }).map((_, i) => (
          <div key={i} className="h-44 bg-[#18181B] rounded-lg border border-[#27272A]" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-5">
      <div className="flex items-center justify-between">
        <p className="text-xs text-[#71717A]">Auto-refreshes every 10 seconds · Last updated {lastUpdated}</p>
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-green-500 animate-pulse" />
          <span className="text-xs text-[#71717A]">Live</span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-4">
        {sections.map((section, i) => (
          <motion.div
            key={section.title}
            initial={{ opacity: 0, y: 8 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: i * 0.05, duration: 0.2 }}
            className="bg-[#18181B] border border-[#27272A] rounded-lg p-5"
          >
            <div className="flex items-center gap-2 mb-4">
              {section.icon}
              <h3 className="text-sm font-semibold text-[#FAFAFA]">{section.title}</h3>
            </div>
            <div className="space-y-3">
              {section.items.map(({ label, value, status }) => (
                <div key={label} className="flex items-center justify-between">
                  <span className="text-xs text-[#71717A]">{label}</span>
                  <div className="flex items-center gap-2">
                    {status && <StatusDot status={status} />}
                    <span className={`text-xs font-medium ${status === 'green' ? 'text-green-400' : status === 'red' ? 'text-red-400' : status === 'yellow' ? 'text-yellow-400' : 'text-[#A1A1AA]'}`}>
                      {value}
                    </span>
                  </div>
                </div>
              ))}
            </div>
          </motion.div>
        ))}
      </div>

      {/* AI Budget Progress */}
      <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-5">
        <div className="flex items-center justify-between mb-4">
          <div className="flex items-center gap-2">
            <Brain size={15} className="text-purple-400" />
            <h3 className="text-sm font-semibold text-[#FAFAFA]">AI Budget Overview</h3>
          </div>
          <span className="text-xs text-[#71717A]">{budgetPct}% used</span>
        </div>
        <div className="h-2 bg-[#27272A] rounded-full overflow-hidden">
          <motion.div
            initial={{ width: 0 }}
            animate={{ width: `${budgetPct}%` }}
            transition={{ duration: 0.8, ease: 'easeOut' }}
            className={`h-full rounded-full ${budgetPct > 85 ? 'bg-red-500' : budgetPct > 60 ? 'bg-yellow-500' : 'bg-purple-500'}`}
          />
        </div>
        <div className="flex justify-between mt-2 text-xs text-[#71717A]">
          <span>0 requests</span>
          <span>{budgetTotal} requests</span>
        </div>
        {budgetPct > 85 && (
          <div className="flex items-center gap-2 text-xs text-yellow-400 bg-yellow-500/10 border border-yellow-500/20 rounded-md px-3 py-2 mt-3">
            <AlertTriangle size={12} />
            Daily budget nearly exhausted. Increase the limit in Settings or wait for reset.
          </div>
        )}
      </div>
    </div>
  );
}
