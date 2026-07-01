import React, { useState, useMemo } from 'react';
import { useQuery } from '@tanstack/react-query';
import { Search, Download, ChevronUp, ChevronDown, ChevronLeft, ChevronRight, X, SlidersHorizontal } from 'lucide-react';
import JobDrawer from '@/components/ui/JobDrawer';
import { supabase } from '@/lib/supabaseClient';

type SortDir = 'asc' | 'desc' | null;

const PAGE_SIZE = 25;

const getDecisionStyle = (decision: string) => {
  if (decision === 'Keep') return 'text-green-400 bg-green-500/10 border-green-500/20';
  if (decision === 'Reject') return 'text-red-400 bg-red-500/10 border-red-500/20';
  return 'text-yellow-400 bg-yellow-500/10 border-yellow-500/20';
};

interface ColumnDef {
  key: string;
  label: string;
  visible: boolean;
}

export default function Jobs() {
  const [search, setSearch] = useState('');
  const [sourceFilter, setSourceFilter] = useState('');
  const [decisionFilter, setDecisionFilter] = useState('');
  const [workTypeFilter, setWorkTypeFilter] = useState('');
  const [categoryFilter, setCategoryFilter] = useState('');
  const [sortKey, setSortKey] = useState<string | null>(null);
  const [sortDir, setSortDir] = useState<SortDir>(null);
  const [page, setPage] = useState(1);
  const [selectedJob, setSelectedJob] = useState<any>(null);
  const [showColumns, setShowColumns] = useState(false);
  const [columns, setColumns] = useState<ColumnDef[]>([
    { key: 'title', label: 'Job', visible: true },
    { key: 'company', label: 'Company', visible: true },
    { key: 'location', label: 'Location', visible: true },
    { key: 'source', label: 'Source', visible: true },
    { key: 'work_type', label: 'Work Type', visible: true },
    { key: 'scraped_at', label: 'Posted', visible: true },
    { key: 'ai_score', label: 'AI Score', visible: true },
    { key: 'ai_status', label: 'Status', visible: true },
  ]);

  const { data: rawData, isLoading } = useQuery({
    queryKey: ['jobs'],
    queryFn: async () => {
      const { data, error } = await supabase
        .from('jobs')
        .select('id,title,company,location,source,work_type,ai_status,ai_score,scraped_at,job_url,keyword,category,employment_type,salary,remote,skills')
        .order('scraped_at', { ascending: false })
        .limit(500);
      if (error) console.error('Jobs fetch error:', error);
      return data ?? [];
    },
    staleTime: 60000,
  });

  const jobs: any[] = Array.isArray(rawData) ? rawData : [];

  const handleRowClick = async (job: any) => {
    if (!job.description || !job.summary) {
      const { data } = await supabase.from('jobs').select('description,summary').eq('id', job.id).single();
      setSelectedJob(data ? { ...job, description: data.description, summary: data.summary } : job);
    } else {
      setSelectedJob(job);
    }
  };

  const sources = useMemo(() => [...new Set(jobs.map((j: any) => j['source']).filter(Boolean))], [jobs]);
  const workTypes = useMemo(() => [...new Set(jobs.map((j: any) => j['work_type']).filter(Boolean))], [jobs]);
  const categories = useMemo(() => [...new Set(jobs.map((j: any) => j['category']).filter(Boolean))], [jobs]);

  const filtered = useMemo(() => {
    let result = jobs.filter((job: any) => {
      const q = search.toLowerCase();
      const matchSearch = !search ||
        job['title']?.toLowerCase().includes(q) ||
        job['company']?.toLowerCase().includes(q) ||
        job['location']?.toLowerCase().includes(q) ||
        (Array.isArray(job['skills']) && job['skills'].some((s: string) => s.toLowerCase().includes(q)));
      const matchSource = !sourceFilter || job['source'] === sourceFilter;
      const matchDecision = !decisionFilter || job['ai_status'] === decisionFilter;
      const matchWorkType = !workTypeFilter || job['work_type'] === workTypeFilter;
      const matchCategory = !categoryFilter || job['category'] === categoryFilter;
      return matchSearch && matchSource && matchDecision && matchWorkType && matchCategory;
    });

    if (sortKey && sortDir) {
      result = [...result].sort((a, b) => {
        const av = a[sortKey] ?? '';
        const bv = b[sortKey] ?? '';
        const cmp = String(av).localeCompare(String(bv), undefined, { numeric: true });
        return sortDir === 'asc' ? cmp : -cmp;
      });
    }

    return result;
  }, [jobs, search, sourceFilter, decisionFilter, workTypeFilter, categoryFilter, sortKey, sortDir]);

  const totalPages = Math.max(1, Math.ceil(filtered.length / PAGE_SIZE));
  const pageJobs = filtered.slice((page - 1) * PAGE_SIZE, page * PAGE_SIZE);

  const handleSort = (key: string) => {
    if (sortKey === key) {
      if (sortDir === 'asc') { setSortDir('desc'); }
      else if (sortDir === 'desc') { setSortKey(null); setSortDir(null); }
      else { setSortDir('asc'); }
    } else {
      setSortKey(key);
      setSortDir('asc');
    }
  };

  const SortIcon = ({ col }: { col: string }) => {
    if (sortKey !== col) return <ChevronUp size={12} className="opacity-20" />;
    if (sortDir === 'asc') return <ChevronUp size={12} className="text-blue-400" />;
    return <ChevronDown size={12} className="text-blue-400" />;
  };

  const exportCSV = () => {
    const headers = columns.filter(c => c.visible).map(c => c.key);
    const rows = filtered.map((job: any) => headers.map(h => `"${(job[h] ?? '').toString().replace(/"/g, '""')}"`).join(','));
    const csv = [headers.join(','), ...rows].join('\n');
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([csv], { type: 'text/csv' }));
    a.download = 'jobs.csv';
    a.click();
  };

  const visibleColumns = columns.filter(c => c.visible);
  const activeFilters = [sourceFilter, decisionFilter, workTypeFilter, categoryFilter].filter(Boolean);

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        <div className="h-10 bg-[var(--c-card)] rounded-lg" />
        <div className="h-96 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />
      </div>
    );
  }

  return (
    <div className="space-y-4">
      {/* Toolbar */}
      <div className="flex flex-col gap-3">
        <div className="flex items-center gap-2 flex-wrap">
          <div className="relative flex-1 min-w-[200px] max-w-sm">
            <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-[var(--c-text3)]" />
            <input
              value={search}
              onChange={e => { setSearch(e.target.value); setPage(1); }}
              placeholder="Search jobs, companies..."
              className="w-full h-9 pl-8 pr-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text)] placeholder:text-[var(--c-text3)] outline-none focus:border-blue-500/50"
            />
            {search && (
              <button onClick={() => setSearch('')} className="absolute right-2 top-1/2 -translate-y-1/2 text-[var(--c-text3)] hover:text-[var(--c-text)]">
                <X size={12} />
              </button>
            )}
          </div>

          <select
            value={sourceFilter}
            onChange={e => { setSourceFilter(e.target.value); setPage(1); }}
            className="h-9 px-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none focus:border-blue-500/50 cursor-pointer"
          >
            <option value="">All Sources</option>
            {sources.map(s => <option key={s as string} value={s as string}>{s as string}</option>)}
          </select>

          <select
            value={decisionFilter}
            onChange={e => { setDecisionFilter(e.target.value); setPage(1); }}
            className="h-9 px-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none focus:border-blue-500/50 cursor-pointer"
          >
            <option value="">All AI Status</option>
            <option value="Keep">Keep</option>
            <option value="Reject">Reject</option>
          </select>

          <select
            value={workTypeFilter}
            onChange={e => { setWorkTypeFilter(e.target.value); setPage(1); }}
            className="h-9 px-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none focus:border-blue-500/50 cursor-pointer"
          >
            <option value="">All Work Types</option>
            {workTypes.map(w => <option key={w as string} value={w as string}>{w as string}</option>)}
          </select>

          <select
            value={categoryFilter}
            onChange={e => { setCategoryFilter(e.target.value); setPage(1); }}
            className="h-9 px-3 text-sm bg-[var(--c-card)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none focus:border-blue-500/50 cursor-pointer"
          >
            <option value="">All Categories</option>
            {categories.map(c => <option key={c as string} value={c as string}>{c as string}</option>)}
          </select>

          {activeFilters.length > 0 && (
            <button
              onClick={() => { setSourceFilter(''); setDecisionFilter(''); setWorkTypeFilter(''); setCategoryFilter(''); setPage(1); }}
              className="h-9 px-3 text-sm text-[var(--c-text3)] hover:text-[var(--c-text)] border border-[var(--c-border)] rounded-md transition-colors flex items-center gap-1.5"
            >
              <X size={12} /> Reset
            </button>
          )}

          <div className="ml-auto flex items-center gap-2">
            <div className="relative">
              <button
                onClick={() => setShowColumns(c => !c)}
                className="h-9 px-3 text-sm text-[var(--c-text3)] hover:text-[var(--c-text)] border border-[var(--c-border)] rounded-md transition-colors flex items-center gap-1.5"
              >
                <SlidersHorizontal size={13} /> Columns
              </button>
              {showColumns && (
                <div className="absolute right-0 top-10 bg-[var(--c-card)] border border-[var(--c-border)] rounded-lg p-3 z-10 shadow-xl min-w-[160px]">
                  {columns.map(col => (
                    <label key={col.key} className="flex items-center gap-2 py-1 text-sm text-[var(--c-text2)] cursor-pointer hover:text-[var(--c-text)]">
                      <input
                        type="checkbox"
                        checked={col.visible}
                        onChange={() => setColumns(prev => prev.map(c => c.key === col.key ? { ...c, visible: !c.visible } : c))}
                        className="w-3.5 h-3.5 accent-blue-500"
                      />
                      {col.label}
                    </label>
                  ))}
                </div>
              )}
            </div>

            <button
              onClick={exportCSV}
              className="h-9 px-3 text-sm text-[var(--c-text3)] hover:text-[var(--c-text)] border border-[var(--c-border)] rounded-md transition-colors flex items-center gap-1.5"
            >
              <Download size={13} /> Export
            </button>
          </div>
        </div>

        {activeFilters.length > 0 && (
          <div className="flex items-center gap-2 flex-wrap">
            <span className="text-xs text-[var(--c-text3)]">Filters:</span>
            {sourceFilter && (
              <span className="flex items-center gap-1 text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">
                Source: {sourceFilter}
                <button onClick={() => setSourceFilter('')}><X size={10} /></button>
              </span>
            )}
            {decisionFilter && (
              <span className="flex items-center gap-1 text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">
                Status: {decisionFilter}
                <button onClick={() => setDecisionFilter('')}><X size={10} /></button>
              </span>
            )}
            {workTypeFilter && (
              <span className="flex items-center gap-1 text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">
                Type: {workTypeFilter}
                <button onClick={() => setWorkTypeFilter('')}><X size={10} /></button>
              </span>
            )}
            {categoryFilter && (
              <span className="flex items-center gap-1 text-xs bg-blue-500/10 border border-blue-500/20 text-blue-400 px-2 py-0.5 rounded-full">
                Category: {categoryFilter}
                <button onClick={() => setCategoryFilter('')}><X size={10} /></button>
              </span>
            )}
          </div>
        )}
      </div>

      {/* Table */}
      <div className="bg-[var(--c-card)] border border-[var(--c-border)] rounded-lg overflow-hidden">
        <div className="flex items-center justify-between px-4 py-3 border-b border-[var(--c-border)]">
          <span className="text-xs text-[var(--c-text3)]">
            {filtered.length.toLocaleString()} jobs
            {filtered.length !== jobs.length && <span className="text-[var(--c-icon)]"> (of {jobs.length.toLocaleString()})</span>}
          </span>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <thead>
              <tr className="border-b border-[var(--c-border)]">
                {visibleColumns.map(col => (
                  <th
                    key={col.key}
                    onClick={() => handleSort(col.key)}
                    className="text-left px-4 py-2.5 text-xs font-medium text-[var(--c-text3)] cursor-pointer hover:text-[var(--c-text2)] whitespace-nowrap select-none"
                  >
                    <div className="flex items-center gap-1">
                      {col.label}
                      <SortIcon col={col.key} />
                    </div>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {pageJobs.length === 0 ? (
                <tr>
                  <td colSpan={visibleColumns.length} className="px-4 py-16 text-center">
                    <div className="flex flex-col items-center gap-2">
                      <p className="text-sm text-[var(--c-text3)]">
                        {jobs.length === 0
                          ? 'No jobs yet — connect to the backend and run the scraper.'
                          : 'No jobs match your filters.'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                pageJobs.map((job: any, i: number) => (
                  <tr
                    key={i}
                    onClick={() => handleRowClick(job)}
                    className="border-b border-[var(--c-border)] hover:bg-[var(--c-input)] cursor-pointer transition-colors last:border-0"
                  >
                    {visibleColumns.map(col => (
                      <td key={col.key} className="px-4 py-3 text-[var(--c-text2)]">
                        {col.key === 'title' ? (
                          <div className="font-medium text-[var(--c-text)] max-w-[200px] truncate">{job[col.key]}</div>
                        ) : col.key === 'ai_status' ? (
                          <span className={`text-xs border px-2 py-0.5 rounded-full font-medium ${getDecisionStyle(job[col.key] || '')}`}>
                            {job[col.key] || 'Pending'}
                          </span>
                        ) : col.key === 'ai_score' ? (
                          <span className="tabular-nums font-medium text-[var(--c-text)]">{job[col.key] ?? '—'}</span>
                        ) : col.key === 'scraped_at' ? (
                          <span className="text-xs">{job[col.key]?.split('T')[0] || '—'}</span>
                        ) : col.key === 'source' ? (
                          <span className="text-xs bg-[var(--c-pill)] px-2 py-0.5 rounded-full">{job[col.key]}</span>
                        ) : (
                          <span className="max-w-[140px] truncate block">{job[col.key] || '—'}</span>
                        )}
                      </td>
                    ))}
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {totalPages > 1 && (
          <div className="flex items-center justify-between px-4 py-3 border-t border-[var(--c-border)]">
            <span className="text-xs text-[var(--c-text3)]">Page {page} of {totalPages}</span>
            <div className="flex items-center gap-1">
              <button
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                className="h-7 w-7 flex items-center justify-center rounded-md border border-[var(--c-border)] text-[var(--c-text3)] hover:text-[var(--c-text)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronLeft size={13} />
              </button>
              {Array.from({ length: Math.min(5, totalPages) }, (_, i) => {
                const p = Math.max(1, Math.min(totalPages - 4, page - 2)) + i;
                return (
                  <button
                    key={p}
                    onClick={() => setPage(p)}
                    className={`h-7 w-7 text-xs rounded-md border transition-colors ${
                      p === page
                        ? 'border-blue-500 bg-blue-500/10 text-blue-400'
                        : 'border-[var(--c-border)] text-[var(--c-text3)] hover:text-[var(--c-text)]'
                    }`}
                  >
                    {p}
                  </button>
                );
              })}
              <button
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                className="h-7 w-7 flex items-center justify-center rounded-md border border-[var(--c-border)] text-[var(--c-text3)] hover:text-[var(--c-text)] disabled:opacity-30 disabled:cursor-not-allowed transition-colors"
              >
                <ChevronRight size={13} />
              </button>
            </div>
          </div>
        )}
      </div>

      <JobDrawer job={selectedJob} onClose={() => setSelectedJob(null)} />
    </div>
  );
}
