import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, ChevronDown, ChevronRight, X, FileText } from 'lucide-react';
import { supabase } from '@/lib/supabaseClient';

interface LogEntry {
  id?: number;
  timestamp?: string;
  date?: string;
  keyword?: string;
  source?: string;
  status?: string;
  message?: string;
  jobs_found?: number;
  error?: string;
  [key: string]: any;
}

const statusStyle: Record<string, string> = {
  success: 'text-green-400 bg-green-500/10 border-green-500/20',
  error: 'text-red-400 bg-red-500/10 border-red-500/20',
  warning: 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20',
  info: 'text-blue-400 bg-blue-500/10 border-blue-500/20',
};

const SKIP_KEYS = new Set(['timestamp', 'date', 'keyword', 'source', 'status', 'message', 'error', 'id', 'jobs_found']);

const LogRow: React.FC<{ log: LogEntry }> = ({ log }) => {
  const [expanded, setExpanded] = useState(false);
  const status = (log.status || 'info').toLowerCase();
  const extraEntries = Object.entries(log).filter(([k]) => !SKIP_KEYS.has(k));

  return (
    <>
      <tr
        onClick={() => setExpanded(e => !e)}
        className="border-b border-[var(--c-border)] hover:bg-[var(--c-input)] cursor-pointer transition-colors"
      >
        <td className="px-4 py-3 text-xs text-[var(--c-text3)] whitespace-nowrap">
          {log.time ? new Date(log.time).toLocaleString() : (log.date || '—')}
        </td>
        <td className="px-4 py-3">
          <span className={`text-xs border px-2 py-0.5 rounded-full font-medium ${statusStyle[status] ?? statusStyle.info}`}>
            {log.status || 'Info'}
          </span>
        </td>
        <td className="px-4 py-3 text-xs text-[var(--c-text2)]">{log.keyword || '—'}</td>
        <td className="px-4 py-3 text-xs text-[var(--c-text2)]">{log.source || '—'}</td>
        <td className="px-4 py-3 text-xs text-[var(--c-text3)] max-w-[300px] truncate">{log.message || '—'}</td>
        <td className="px-4 py-3 text-xs text-[var(--c-text2)] tabular-nums">{log.jobs_found ?? '—'}</td>
        <td className="px-4 py-3 text-[var(--c-text3)]">
          {expanded ? <ChevronDown size={13} /> : <ChevronRight size={13} />}
        </td>
      </tr>
      {expanded && (
        <tr className="bg-[var(--c-bg)] border-b border-[var(--c-border)]">
          <td colSpan={7} className="px-6 py-4">
            <div className="space-y-2 text-xs">
              {log.message && (
                <div>
                  <span className="text-[var(--c-text3)] font-medium">Message: </span>
                  <span className="text-[var(--c-text2)]">{log.message}</span>
                </div>
              )}
              {log.error && (
                <div>
                  <span className="text-red-400 font-medium">Error: </span>
                  <span className="text-red-300 font-mono">{log.error}</span>
                </div>
              )}
              {extraEntries.length > 0 && (
                <div className="grid grid-cols-3 gap-4 mt-2 pt-2 border-t border-[var(--c-border)]">
                  {extraEntries.map(([k, v]) => (
                    <div key={k}>
                      <span className="text-[var(--c-text3)]">{k}: </span>
                      <span className="text-[var(--c-text2)]">{String(v)}</span>
                    </div>
                  ))}
                </div>
              )}
            </div>
          </td>
        </tr>
      )}
    </>
  );
};

export default function Logs() {
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');

  const { data: rawData = [], isLoading } = useQuery({
    queryKey: ['logs'],
    queryFn: async () => {
      try {
        const { data } = await supabase.from('logs').select('*').order('time', { ascending: false }).limit(500);
        return data ?? [];
      } catch {
        return [];
      }
    },
    refetchInterval: 30000,
  });

  const data: LogEntry[] = Array.isArray(rawData) ? rawData : [];

  const filtered = data.filter(log => {
    const q = search.toLowerCase();
    const matchSearch = !search ||
      (log.message || '').toLowerCase().includes(q) ||
      (log.keyword || '').toLowerCase().includes(q) ||
      (log.source || '').toLowerCase().includes(q);
    const matchStatus = !statusFilter || (log.status || '').toLowerCase() === statusFilter;
    const matchSource = !sourceFilter || log.source === sourceFilter;
    return matchSearch && matchStatus && matchSource;
  });

  const sources = [...new Set(data.map(l => l.source).filter(Boolean))];

  if (isLoading) {
    return (
      <div className="space-y-3 animate-pulse">
        <div className="h-10 bg-[var(--c-card)] rounded-lg" />
        <div className="h-96 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Filters */}
      <div className="flex items-center gap-2 flex-wrap">
        <div className="relative flex-1 min-w-[200px] max-w-xs">
          <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--c-text3)]" />
          <input
            value={search}
            onChange={e => setSearch(e.target.value)}
            placeholder="Search logs..."
            className="w-full h-9 pl-7 pr-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text)] placeholder:text-[var(--c-text3)] outline-none focus:border-blue-500/50"
          />
        </div>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="h-9 px-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none cursor-pointer"
        >
          <option value="">All Status</option>
          <option value="success">Success</option>
          <option value="error">Error</option>
          <option value="warning">Warning</option>
          <option value="info">Info</option>
        </select>
        <select
          value={sourceFilter}
          onChange={e => setSourceFilter(e.target.value)}
          className="h-9 px-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none cursor-pointer"
        >
          <option value="">All Sources</option>
          {sources.map(s => <option key={s as string} value={s as string}>{s as string}</option>)}
        </select>
        {(search || statusFilter || sourceFilter) && (
          <button
            onClick={() => { setSearch(''); setStatusFilter(''); setSourceFilter(''); }}
            className="h-9 px-3 text-sm text-[var(--c-text3)] hover:text-[var(--c-text)] border border-[var(--c-border)] rounded-md transition-colors flex items-center gap-1.5"
          >
            <X size={12} /> Reset
          </button>
        )}
        <span className="ml-auto text-xs text-[var(--c-text3)]">{filtered.length} entries</span>
      </div>

      {/* Table */}
      <div className="bg-[var(--c-card)] border border-[var(--c-border)] rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--c-border)]">
                {['Time', 'Status', 'Keyword', 'Source', 'Message', 'Jobs Found', ''].map(h => (
                  <th key={h} className="text-left px-4 py-2.5 text-xs font-medium text-[var(--c-text3)] whitespace-nowrap">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {filtered.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-16 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <FileText size={28} className="text-[var(--c-icon)]" />
                      <p className="text-sm text-[var(--c-text3)]">
                        {data.length === 0
                          ? 'No logs yet. Run the scraper to see activity here.'
                          : 'No logs match your filters.'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                filtered.map((log, i) => <LogRow key={log.id ?? i} log={log} />)
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}
