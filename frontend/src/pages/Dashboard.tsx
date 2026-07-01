import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { motion } from 'framer-motion';
import {
  Briefcase, CheckCircle, Clock, Activity, Globe, Zap,
  Brain, TrendingUp, AlertTriangle, Database
} from 'lucide-react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';
import StatCard from '@/components/ui/StatCard';
import StatusDot from '@/components/ui/StatusDot';
import JobDrawer from '@/components/ui/JobDrawer';
import { supabase } from '@/lib/supabaseClient';

const CHART_COLORS = ['#3B82F6', '#22C55E', '#F59E0B', '#A855F7', '#EC4899'];

const cardVariants = {
  hidden: { opacity: 0, y: 12 },
  visible: (i: number) => ({ opacity: 1, y: 0, transition: { delay: i * 0.04, duration: 0.25 } }),
};

const SkeletonStat = () => (
  <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-4 animate-pulse">
    <div className="h-3 w-20 bg-[#27272A] rounded mb-4" />
    <div className="h-7 w-16 bg-[#27272A] rounded" />
  </div>
);

const CustomTooltip = ({ active, payload, label }: any) => {
  if (!active || !payload?.length) return null;
  return (
    <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-3 text-xs shadow-xl">
      <p className="text-[#A1A1AA] mb-1">{label}</p>
      <p className="text-[#FAFAFA] font-semibold">{payload[0].value} jobs</p>
    </div>
  );
};

export default function Dashboard() {
  const [selectedJob, setSelectedJob] = useState<any>(null);

  const { data: stats, isLoading: statsLoading } = useQuery({
    queryKey: ['stats'],
    queryFn: async () => {
      try {
        const { count: total } = await supabase.from('jobs').select('*', { count: 'exact', head: true });
        const today = new Date().toISOString().slice(0, 10);
        const { count: todayCount } = await supabase.from('jobs').select('*', { count: 'exact', head: true }).gte('scraped_at', today);
        const { count: accepted } = await supabase.from('jobs').select('*', { count: 'exact', head: true }).eq('ai_status', 'Keep');
        const { count: rejected } = await supabase.from('jobs').select('*', { count: 'exact', head: true }).eq('ai_status', 'Reject');
        return { total_found: total ?? 0, today: todayCount ?? 0, ai_accepted: accepted ?? 0, ai_rejected: rejected ?? 0 };
      } catch { return {}; }
    },
    staleTime: 30000,
  });

  const { data: health, isLoading: healthLoading } = useQuery({
    queryKey: ['health'],
    queryFn: async () => {
      try {
        const { data: run } = await supabase.from('scraper_runs').select('*').order('created_at', { ascending: false }).limit(1).single();
        const { data: settings } = await supabase.from('settings').select('*').limit(1).single();
        return {
          scheduler_status: run?.status ?? 'Idle',
          ai_budget_used: 0,
          ai_budget_total: settings?.ai_request_budget_daily ?? 100,
          captcha_blocked_sources: run?.captcha_blocked_sources ?? [],
          active_sources: settings?.enabled_sources?.length ?? 0,
          enabled_sources: settings?.enabled_sources ?? [],
        };
      } catch { return {}; }
    },
    refetchInterval: 30000,
  });

  const { data: rawJobsData } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      try {
        const { data } = await supabase.from('jobs').select('*').order('scraped_at', { ascending: false }).limit(100);
        return data ?? [];
      } catch { return []; }
    },
  });

  const jobs: any[] = Array.isArray(rawJobsData) ? rawJobsData : [];

  // Compute daily job counts for the last 7 days from real data
  const chartData = (() => {
    const days: { name: string; jobs: number; date: string }[] = [];
    const today = new Date();
    for (let i = 6; i >= 0; i--) {
      const d = new Date(today);
      d.setDate(d.getDate() - i);
      const name = d.toLocaleDateString('en-US', { weekday: 'short' });
      const date = d.toISOString().slice(0, 10);
      days.push({ name, jobs: 0, date });
    }
    for (const job of jobs) {
      const scrapedAt = job['scraped_at'];
      if (!scrapedAt) continue;
      const match = days.find(d => d.date === scrapedAt.slice(0, 10));
      if (match) match.jobs++;
    }
    return days;
  })();

  // Derive source breakdown from real data
  const sourceCounts: Record<string, number> = {};
  jobs.forEach((job: any) => {
    const src = job['source'] || 'Unknown';
    sourceCounts[src] = (sourceCounts[src] || 0) + 1;
  });
  const sourceData = Object.entries(sourceCounts).slice(0, 5).map(([name, value]) => ({ name, value }));

  const totalJobs = stats?.total_found ?? 0;
  const aiAccepted = stats?.ai_accepted ?? 0;
  const aiRejected = stats?.ai_rejected ?? 0;
  const pending = totalJobs - aiAccepted - aiRejected;
  const activeSources = health?.active_sources ?? 0;
  const schedulerOk = health?.scheduler_status === 'Running';
  const budgetUsed = health?.ai_budget_used ?? 0;
  const budgetTotal = health?.ai_budget_total ?? 1;
  const budgetPct = Math.min(100, Math.round((budgetUsed / budgetTotal) * 100));

  const recentJobs = jobs.slice(0, 8);

  const getDecisionStyle = (decision: string) => {
    if (decision === 'Keep') return 'text-green-400 bg-green-500/10 border-green-500/20';
    if (decision === 'Reject') return 'text-red-400 bg-red-500/10 border-red-500/20';
    return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
  };

  return (
    <div className="space-y-6">
      {/* CAPTCHA Warning Banner */}
      {health?.captcha_blocked_sources?.length > 0 && (
        <div className="bg-yellow-500/10 border border-yellow-500/20 text-yellow-400 p-4 rounded-lg flex items-start gap-3">
          <AlertTriangle size={18} className="shrink-0 mt-0.5" />
          <div className="text-sm">
            <p className="font-semibold mb-1">⚠ CAPTCHA Detected</p>
            <p className="opacity-90">
              {health.captcha_blocked_sources.join(', ')} encountered a CAPTCHA during the last run. 
              The scraper skipped these sources and continued scraping the remaining sources.
            </p>
          </div>
        </div>
      )}

      {/* Stat Cards Row */}
      <div className="grid grid-cols-2 md:grid-cols-3 xl:grid-cols-6 gap-3">
        {statsLoading ? (
          Array.from({ length: 6 }).map((_, i) => <SkeletonStat key={i} />)
        ) : (
          <>
            {[
              { icon: <Briefcase size={16} />, title: 'Total Jobs', value: totalJobs, subtitle: 'all time', accentColor: 'text-blue-400' },
              { icon: <TrendingUp size={16} />, title: 'Jobs Today', value: stats?.today ?? 0, trendValue: '+today', trend: 'up' as const, accentColor: 'text-emerald-400' },
              { icon: <Clock size={16} />, title: 'Pending Review', value: pending, subtitle: 'awaiting AI', accentColor: 'text-yellow-400' },
              { icon: <CheckCircle size={16} />, title: 'AI Accepted', value: aiAccepted, accentColor: 'text-green-400' },
              { icon: <Globe size={16} />, title: 'Active Sources', value: activeSources, accentColor: 'text-purple-400' },
              { icon: <Activity size={16} />, title: 'Scheduler', value: schedulerOk ? 'Running' : 'Idle', accentColor: schedulerOk ? 'text-green-400' : 'text-zinc-400' },
            ].map((card, i) => (
              <motion.div key={i} custom={i} initial="hidden" animate="visible" variants={cardVariants}>
                <StatCard {...card} />
              </motion.div>
            ))}
          </>
        )}
      </div>

      {/* Charts Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Jobs Over Time */}
        <div className="xl:col-span-2 bg-[#18181B] border border-[#27272A] rounded-lg p-5">
          <div className="flex items-center justify-between mb-5">
            <div>
              <h2 className="text-sm font-semibold text-[#FAFAFA]">Jobs Over Time</h2>
              <p className="text-xs text-[#71717A] mt-0.5">Last 7 days</p>
            </div>
          </div>
          <div className="h-52">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData} barSize={22}>
                <XAxis dataKey="name" axisLine={false} tickLine={false} tick={{ fill: '#71717A', fontSize: 11 }} />
                <YAxis axisLine={false} tickLine={false} tick={{ fill: '#71717A', fontSize: 11 }} />
                <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                <Bar dataKey="jobs" fill="#3B82F6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Jobs by Source */}
        <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-5">
          <h2 className="text-sm font-semibold text-[#FAFAFA] mb-1">Jobs by Source</h2>
          <p className="text-xs text-[#71717A] mb-4">Distribution</p>
          {sourceData.length > 0 ? (
            <div className="h-52">
              <ResponsiveContainer width="100%" height="100%">
                <PieChart>
                  <Pie data={sourceData} cx="50%" cy="45%" innerRadius={50} outerRadius={72} dataKey="value" paddingAngle={2}>
                    {sourceData.map((_, i) => (
                      <Cell key={i} fill={CHART_COLORS[i % CHART_COLORS.length]} />
                    ))}
                  </Pie>
                  <Legend formatter={(v) => <span className="text-xs text-[#A1A1AA]">{v}</span>} />
                  <Tooltip contentStyle={{ background: '#18181B', border: '1px solid #27272A', borderRadius: '8px', fontSize: '12px' }} />
                </PieChart>
              </ResponsiveContainer>
            </div>
          ) : (
            <div className="h-52 flex items-center justify-center text-[#71717A] text-sm">
              No source data yet
            </div>
          )}
        </div>
      </div>

      {/* Latest Jobs + AI Usage Row */}
      <div className="grid grid-cols-1 xl:grid-cols-3 gap-4">
        {/* Latest Jobs Table */}
        <div className="xl:col-span-2 bg-[#18181B] border border-[#27272A] rounded-lg overflow-hidden">
          <div className="px-5 py-4 border-b border-[#27272A]">
            <h2 className="text-sm font-semibold text-[#FAFAFA]">Latest Jobs</h2>
          </div>
          {recentJobs.length === 0 ? (
            <div className="p-8 text-center text-[#71717A] text-sm">No jobs found. Run the scraper to get started.</div>
          ) : (
            <div className="overflow-x-auto">
              <table className="w-full text-sm">
                <thead>
                  <tr className="border-b border-[#27272A]">
                    {['Job', 'Company', 'Source', 'AI Status'].map(h => (
                      <th key={h} className="text-left px-4 py-2.5 text-xs font-medium text-[#71717A]">{h}</th>
                    ))}
                  </tr>
                </thead>
                <tbody>
                  {recentJobs.map((job: any, i: number) => (
                    <tr
                      key={i}
                      onClick={() => setSelectedJob(job)}
                      className="border-b border-[#27272A] hover:bg-[#111113] cursor-pointer transition-colors last:border-0"
                    >
                      <td className="px-4 py-3">
                        <div className="font-medium text-[#FAFAFA] truncate max-w-[180px]">{job['title']}</div>
                        <div className="text-xs text-[#71717A]">{job['location']}</div>
                      </td>
                      <td className="px-4 py-3 text-[#A1A1AA] truncate max-w-[120px]">{job['company']}</td>
                      <td className="px-4 py-3">
                        <span className="text-xs bg-[#27272A] text-[#A1A1AA] px-2 py-0.5 rounded-full">{job['source']}</span>
                      </td>
                      <td className="px-4 py-3">
                        <span className={`text-xs border px-2 py-0.5 rounded-full font-medium ${getDecisionStyle(job['ai_status'] || '')}`}>
                          {job['ai_status'] || 'Pending'}
                          {typeof job['ai_score'] === 'number' && ` · ${job['ai_score']}`}
                        </span>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          )}
        </div>

        {/* Right Column: AI Usage + Health */}
        <div className="space-y-4">
          {/* AI Usage Card */}
          <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-5">
            <div className="flex items-center gap-2 mb-4">
              <Brain size={15} className="text-purple-400" />
              <h2 className="text-sm font-semibold text-[#FAFAFA]">AI Usage</h2>
            </div>
            <div className="space-y-3">
              <div className="flex justify-between text-xs">
                <span className="text-[#71717A]">Daily Budget</span>
                <span className="text-[#FAFAFA] font-medium tabular-nums">{budgetUsed} / {budgetTotal}</span>
              </div>
              <div className="h-1.5 bg-[#27272A] rounded-full overflow-hidden">
                <div
                  className={`h-full rounded-full transition-all duration-500 ${budgetPct > 85 ? 'bg-red-500' : budgetPct > 60 ? 'bg-yellow-500' : 'bg-blue-500'}`}
                  style={{ width: `${budgetPct}%` }}
                />
              </div>
              <div className="flex justify-between text-xs">
                <span className="text-[#71717A]">Remaining</span>
                <span className={`font-medium tabular-nums ${budgetPct > 85 ? 'text-red-400' : 'text-green-400'}`}>
                  {budgetTotal - budgetUsed} left
                </span>
              </div>
              {budgetPct > 85 && (
                <div className="flex items-center gap-2 text-xs text-yellow-400 bg-yellow-500/10 border border-yellow-500/20 rounded-md px-3 py-2">
                  <AlertTriangle size={12} />
                  Budget nearly exhausted
                </div>
              )}
            </div>
          </div>

          {/* Sources Summary Widget */}
          <div className="bg-[#18181B] border border-[#27272A] rounded-lg p-5">
            <div className="flex items-center gap-2 mb-4">
              <Globe size={15} className="text-blue-400" />
              <h2 className="text-sm font-semibold text-[#FAFAFA]">Sources Summary</h2>
            </div>
            <div className="space-y-2">
              {health?.enabled_sources?.length > 0 ? (
                health.enabled_sources.map((source: string) => (
                  <div key={source} className="flex justify-between items-center text-xs">
                    <span className="text-[#A1A1AA] capitalize">{source}</span>
                    <span className="text-green-400 bg-green-500/10 border border-green-500/20 px-2 py-0.5 rounded-full">Enabled</span>
                  </div>
                ))
              ) : (
                <div className="text-xs text-[#71717A]">No sources enabled.</div>
              )}
            </div>
          </div>

        </div>
      </div>
      {/* Job Drawer */}
      <JobDrawer job={selectedJob} onClose={() => setSelectedJob(null)} />
    </div>
  );
}
