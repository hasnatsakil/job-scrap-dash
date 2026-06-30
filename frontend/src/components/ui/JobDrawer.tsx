import React from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, ExternalLink, Copy, Star, RefreshCw, Building2, MapPin, Clock, Tag, Brain } from 'lucide-react';

interface Job {
  title?: string;
  company?: string;
  location?: string;
  source?: string;
  work_type?: string;
  scraped_at?: string;
  job_url?: string;
  ai_status?: string;
  ai_score?: number | string;
  ai_reason?: string;
  description?: string;
  [key: string]: any;
}

interface JobDrawerProps {
  job: Job | null;
  onClose: () => void;
}

const DrawerRow: React.FC<{ icon: React.ReactNode; label: string; value?: string }> = ({ icon, label, value }) => (
  <div className="flex items-start gap-3">
    <div className="text-[#71717A] mt-0.5 shrink-0">{icon}</div>
    <div>
      <div className="text-xs text-[#71717A] mb-0.5">{label}</div>
      <div className="text-sm text-[#FAFAFA]">{value || '—'}</div>
    </div>
  </div>
);

const JobDrawer: React.FC<JobDrawerProps> = ({ job, onClose }) => {
  const aiDecision = job?.['ai_status'];
  const aiScore = job?.['ai_score'];
  const aiReason = job?.['ai_reason'];

  const decisionBg =
    aiDecision === 'Keep' ? 'bg-green-500/10 border-green-500/20 text-green-400' :
    aiDecision === 'Reject' ? 'bg-red-500/10 border-red-500/20 text-red-400' :
    'bg-zinc-800 border-zinc-700 text-zinc-400';

  return (
    <AnimatePresence>
      {job && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="fixed inset-0 bg-black/50 z-40"
            onClick={onClose}
          />

          {/* Drawer */}
          <motion.div
            initial={{ x: '100%' }}
            animate={{ x: 0 }}
            exit={{ x: '100%' }}
            transition={{ type: 'spring', damping: 30, stiffness: 300 }}
            className="fixed right-0 top-0 h-full w-[600px] max-w-full bg-[#111113] border-l border-[#27272A] z-50 flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-start justify-between p-6 border-b border-[#27272A]">
              <div className="flex-1 min-w-0 pr-4">
                <h2 className="text-base font-semibold text-[#FAFAFA] leading-tight mb-1 line-clamp-2">
                  {job['title'] || 'Untitled Position'}
                </h2>
                <div className="flex items-center gap-1.5 text-sm text-[#A1A1AA]">
                  <Building2 size={13} />
                  <span>{job['company'] || 'Unknown Company'}</span>
                </div>
              </div>
              <button
                onClick={onClose}
                className="text-[#71717A] hover:text-[#FAFAFA] transition-colors shrink-0"
              >
                <X size={18} />
              </button>
            </div>

            {/* Scrollable content */}
            <div className="flex-1 overflow-y-auto p-6 space-y-6">
              {/* Details */}
              <div>
                <h3 className="text-xs font-medium text-[#71717A] uppercase tracking-wide mb-4">Details</h3>
                <div className="grid grid-cols-2 gap-4">
                  <DrawerRow icon={<MapPin size={14} />} label="Location" value={job['location']} />
                  <DrawerRow icon={<Tag size={14} />} label="Work Type" value={job['work_type']} />
                  <DrawerRow icon={<Clock size={14} />} label="Posted" value={job['scraped_at']?.split('T')[0]} />
                  <DrawerRow icon={<ExternalLink size={14} />} label="Source" value={job['source']} />
                </div>
              </div>

              {/* AI Analysis */}
              <div>
                <h3 className="text-xs font-medium text-[#71717A] uppercase tracking-wide mb-4">AI Analysis</h3>
                <div className={`rounded-lg border p-4 ${decisionBg}`}>
                  <div className="flex items-center justify-between mb-2">
                    <div className="flex items-center gap-2">
                      <Brain size={14} />
                      <span className="text-sm font-medium">{aiDecision || 'Pending Review'}</span>
                    </div>
                    {aiScore && (
                      <span className="text-sm font-bold tabular-nums">{aiScore}/10</span>
                    )}
                  </div>
                  {aiReason && (
                    <p className="text-xs opacity-80 leading-relaxed">{aiReason}</p>
                  )}
                </div>
              </div>

              {/* Description */}
              {job['description'] && (
                <div>
                  <h3 className="text-xs font-medium text-[#71717A] uppercase tracking-wide mb-3">Description</h3>
                  <p className="text-sm text-[#A1A1AA] leading-relaxed whitespace-pre-wrap">{job['description']}</p>
                </div>
              )}
            </div>

            {/* Footer actions */}
            <div className="p-4 border-t border-[#27272A] flex items-center gap-2">
              {job['job_url'] && (
                <a
                  href={job['job_url']}
                  target="_blank"
                  rel="noopener noreferrer"
                  className="flex items-center gap-2 h-9 px-4 rounded-md bg-blue-600 hover:bg-blue-500 text-white text-sm font-medium transition-colors"
                >
                  <ExternalLink size={14} />
                  Open Job
                </a>
              )}
              {job['job_url'] && (
                <button
                  onClick={() => navigator.clipboard.writeText(job['job_url'] ?? '')}
                  className="flex items-center gap-2 h-9 px-3 rounded-md border border-[#27272A] text-[#A1A1AA] hover:text-[#FAFAFA] hover:border-[#3F3F46] text-sm transition-colors"
                >
                  <Copy size={14} />
                  Copy URL
                </button>
              )}
              <button className="flex items-center gap-2 h-9 px-3 rounded-md border border-[#27272A] text-[#A1A1AA] hover:text-[#FAFAFA] hover:border-[#3F3F46] text-sm transition-colors">
                <Star size={14} />
                Favorite
              </button>
              <button className="flex items-center gap-2 h-9 px-3 rounded-md border border-[#27272A] text-[#A1A1AA] hover:text-[#FAFAFA] hover:border-[#3F3F46] text-sm transition-colors ml-auto">
                <RefreshCw size={14} />
                Refresh AI
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
};

export default JobDrawer;
