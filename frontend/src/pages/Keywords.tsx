import React, { useState } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Tag, ToggleLeft, ToggleRight, Trash2, Plus, Search } from 'lucide-react';
import StatCard from '@/components/ui/StatCard';
import { useToast } from '@/contexts/ToastContext';
import { supabase } from '@/lib/supabaseClient';

interface Keyword {
  id: string;
  keyword: string;
  enabled: boolean;
  last_search?: string;
  jobs_found?: number;
}

export default function Keywords() {
  const queryClient = useQueryClient();
  const { toast } = useToast();
  const [search, setSearch] = useState('');
  const [newKeyword, setNewKeyword] = useState('');

  const { data: rawData, isLoading } = useQuery({
    queryKey: ['keywords'],
    queryFn: async () => {
      try {
        const { data: dbRows } = await supabase.from('keywords').select('*').order('created_at');
        const { data: jobs } = await supabase.from('jobs').select('keyword');
        const { data: logs } = await supabase.from('logs').select('keyword, time').order('time', { ascending: false });
        const keywordCounts: Record<string, number> = {};
        if (jobs) for (const j of jobs) { const kw = j.keyword; if (kw) keywordCounts[kw] = (keywordCounts[kw] || 0) + 1; }
        const keywordLastSearch: Record<string, string> = {};
        if (logs) for (const l of logs) { const kw = l.keyword; if (kw && kw !== 'All' && !keywordLastSearch[kw]) keywordLastSearch[kw] = l.time; }
        const allLastSearch = logs?.find(l => l.keyword === 'All')?.time;
        return (dbRows ?? []).map((r: any) => ({
          id: r.id,
          keyword: r.keyword,
          enabled: r.enabled,
          jobs_found: keywordCounts[r.keyword] || 0,
          last_search: keywordLastSearch[r.keyword] || allLastSearch || null,
        }));
      } catch { return []; }
    },
  });

  const keywords: Keyword[] = Array.isArray(rawData) ? rawData : [];

  const addMutation = useMutation({
    mutationFn: async (kw: string) => {
      const { data } = await supabase.from('keywords').insert({ keyword: kw, enabled: true }).select().single();
      return data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
      setNewKeyword('');
      toast('success', 'Keyword Added');
    },
    onError: () => toast('error', 'Failed to Add Keyword'),
  });

  const toggleMutation = useMutation({
    mutationFn: async (kw: Keyword) => {
      await supabase.from('keywords').update({ enabled: !kw.enabled }).eq('id', kw.id);
    },
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['keywords'] }),
    onError: () => toast('error', 'Toggle Failed'),
  });

  const deleteMutation = useMutation({
    mutationFn: async (id: string) => {
      await supabase.from('keywords').delete().eq('id', id);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['keywords'] });
      toast('success', 'Keyword Removed');
    },
    onError: () => toast('error', 'Delete Failed'),
  });

  const totalEnabled = keywords.filter(k => k.enabled).length;
  const totalDisabled = keywords.filter(k => !k.enabled).length;
  const totalJobs = keywords.reduce((sum, k) => sum + (k.jobs_found || 0), 0);

  const filtered = keywords.filter(k =>
    !search || k.keyword.toLowerCase().includes(search.toLowerCase())
  );

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="grid grid-cols-4 gap-3">
          {Array.from({ length: 4 }).map((_, i) => <div key={i} className="h-24 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />)}
        </div>
        <div className="h-64 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />
      </div>
    );
  }

  return (
    <div className="space-y-5">
      {/* Stats */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
        <StatCard icon={<Tag size={15} />} title="Total Keywords" value={keywords.length} accentColor="text-blue-400" />
        <StatCard icon={<ToggleRight size={15} />} title="Enabled" value={totalEnabled} accentColor="text-green-400" />
        <StatCard icon={<ToggleLeft size={15} />} title="Disabled" value={totalDisabled} accentColor="text-zinc-400" />
        <StatCard icon={<Search size={15} />} title="Jobs Found" value={totalJobs} accentColor="text-purple-400" />
      </div>

      {/* Table */}
      <div className="bg-[var(--c-card)] border border-[var(--c-border)] rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--c-border)] gap-3">
          <div className="relative flex-1 max-w-xs">
            <Search size={13} className="absolute left-2.5 top-1/2 -translate-y-1/2 text-[var(--c-text3)]" />
            <input
              value={search}
              onChange={e => setSearch(e.target.value)}
              placeholder="Filter keywords..."
              className="w-full h-8 pl-7 pr-3 text-sm bg-[var(--c-input)] border border-[var(--c-border)] rounded-md text-[var(--c-text)] placeholder:text-[var(--c-text3)] outline-none focus:border-blue-500/50"
            />
          </div>
          <form
            onSubmit={e => { e.preventDefault(); if (newKeyword.trim()) addMutation.mutate(newKeyword.trim()); }}
            className="flex items-center gap-2"
          >
            <input
              value={newKeyword}
              onChange={e => setNewKeyword(e.target.value)}
              placeholder="New keyword..."
              className="h-8 px-3 text-sm bg-[var(--c-input)] border border-[var(--c-border)] rounded-md text-[var(--c-text)] placeholder:text-[var(--c-text3)] outline-none focus:border-blue-500/50 w-40"
            />
            <button
              type="submit"
              disabled={!newKeyword.trim() || addMutation.isPending}
              className="h-8 px-3 flex items-center gap-1.5 bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white text-sm rounded-md transition-colors"
            >
              <Plus size={13} />
              Add
            </button>
          </form>
        </div>

        <table className="w-full text-sm">
          <thead>
            <tr className="border-b border-[var(--c-border)]">
              {['Keyword', 'Enabled', 'Last Search', 'Jobs Found', 'Actions'].map(h => (
                <th key={h} className="text-left px-4 py-2.5 text-xs font-medium text-[var(--c-text3)]">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filtered.length === 0 ? (
              <tr>
                <td colSpan={5} className="px-4 py-10 text-center text-[var(--c-text3)] text-sm">
                  {keywords.length === 0
                    ? 'No keywords yet. Add one above, or connect the backend.'
                    : 'No keywords match your search.'}
                </td>
              </tr>
            ) : (
              filtered.map((kw, i) => (
                <tr key={kw.id ?? i} className="border-b border-[var(--c-border)] hover:bg-[var(--c-input)] transition-colors last:border-0">
                  <td className="px-4 py-3 font-medium text-[var(--c-text)]">{kw.keyword}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => kw.id !== undefined && toggleMutation.mutate(kw)}
                      className="transition-colors"
                      title={kw.enabled ? 'Click to disable' : 'Click to enable'}
                    >
                      {kw.enabled
                        ? <ToggleRight size={20} className="text-green-400" />
                        : <ToggleLeft size={20} className="text-[var(--c-text3)]" />
                      }
                    </button>
                  </td>
                  <td className="px-4 py-3 text-xs text-[var(--c-text3)]">
                    {kw.last_search ? new Date(kw.last_search).toLocaleDateString() : '—'}
                  </td>
                  <td className="px-4 py-3 text-[var(--c-text2)] tabular-nums">{kw.jobs_found ?? 0}</td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => kw.id !== undefined && deleteMutation.mutate(kw.id)}
                      disabled={deleteMutation.isPending}
                      className="text-[var(--c-text3)] hover:text-red-400 transition-colors p-1 rounded disabled:opacity-50"
                    >
                      <Trash2 size={14} />
                    </button>
                  </td>
                </tr>
              ))
            )}
          </tbody>
        </table>
      </div>
    </div>
  );
}
