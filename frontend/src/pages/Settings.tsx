import React, { useState, useEffect } from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { motion, AnimatePresence } from 'framer-motion';
import { Save, Settings as SettingsIcon, Clock, Brain, Search, Sliders, ChevronDown } from 'lucide-react';
import { useToast } from '@/contexts/ToastContext';
import { supabase } from '@/lib/supabaseClient';

const DEFAULTS: SettingsData = {
  schedule_time: '08:00 AM',
  ai_model: 'openai/gpt-oss-20b:free',
  ai_system_prompt: 'You are the AI processing engine for a job search platform.\n\nYour purpose is to analyze job postings, improve data quality, and generate structured metadata.\n\nResponsibilities:\n1. Job Relevance (decision: accepted/rejected, relevance_score: 0-100). Reject only for spam, unrelated, or unpaid. Prefer accepted if missing info.\n2. Job Summary: Generate a concise, user-friendly summary under 100 words. Max 5 bullet points starting with "- ". Do NOT repeat technical skills. Focus on role, responsibilities, team context, location, and non-technical requirements. Do not invent info or copy long sentences.\n3. Skills Extraction: JSON array of explicit skills only.\n4. Category: ONE primary category (e.g., Software Engineering, Data Science).\n5. Work Arrangement: Remote/Hybrid/Onsite/Unknown.\n6. Seniority: Internship/Entry/Junior/Mid/Senior/Lead/Manager/Unknown.\n7. Employment Type: Full Time/Contract/Freelance/Unknown.\n8. Salary: Only if explicit.\n9. Quality Rules: Never fabricate or guess missing info.\n\nOutput strictly valid JSON with exact fields: decision, relevance_score, category, summary, skills, work_arrangement, seniority, employment_type, salary, reason.',
  ai_request_budget_daily: 100,
  max_pages_per_source: 5,
  max_jobs_per_keyword: 50,
  delay_between_requests: 2,
  retry_count: 3,
  timeout: 30,
  concurrency: 2,
  search_provider: 'google',
  enabled_sources: ['linkedin', 'glassdoor'],
  search_keywords: ['Python Developer', 'Backend Engineer'],
  search_locations: 'United States, United Kingdom, Singapore',
};

const REGIONS = {
  'Americas & Europe': ['United States', 'United Kingdom', 'Canada', 'Germany', 'France'],
  'Asia & Oceania': ['Australia', 'New Zealand', 'India', 'Singapore', 'Japan', 'South Korea', 'Philippines', 'Malaysia', 'United Arab Emirates']
};

interface SettingsData {
  schedule_time?: string;
  ai_model?: string;
  ai_system_prompt?: string;
  ai_request_budget_daily?: number;
  max_pages_per_source?: number;
  max_jobs_per_keyword?: number;
  delay_between_requests?: number;
  retry_count?: number;
  timeout?: number;
  concurrency?: number;
  search_provider?: string;
  enabled_sources?: string[];
  search_keywords?: string[];
  search_locations?: string;
  [key: string]: any;
}

const SETTINGS_KEY = 'app_settings';

interface SettingFieldProps {
  label: string;
  description?: string;
  children: React.ReactNode;
}

const SettingField: React.FC<SettingFieldProps> = ({ label, description, children }) => (
  <div className="flex items-start justify-between gap-6 py-4 border-b border-[var(--c-border)] last:border-0">
    <div className="flex-1">
      <label className="text-sm font-medium text-[var(--c-text)]">{label}</label>
      {description && <p className="text-xs text-[var(--c-text3)] mt-0.5 leading-relaxed">{description}</p>}
    </div>
    <div className="shrink-0 w-64">{children}</div>
  </div>
);

const inputClass = "w-full h-9 px-3 text-sm bg-[var(--c-input)] border border-[var(--c-border)] rounded-md text-[var(--c-text)] placeholder:text-[var(--c-text3)] outline-none focus:border-blue-500/50 transition-colors";
const selectClass = "w-full h-9 px-3 text-sm bg-[var(--c-input)] border border-[var(--c-border)] rounded-md text-[var(--c-text2)] outline-none focus:border-blue-500/50 cursor-pointer transition-colors";
const textareaClass = "w-full p-3 text-sm bg-[var(--c-input)] border border-[var(--c-border)] rounded-md text-[var(--c-text)] font-mono placeholder:text-[var(--c-text3)] outline-none focus:border-blue-500/50 transition-colors resize-y min-h-[120px]";

interface SectionProps {
  id: string;
  icon: React.ReactNode;
  title: string;
  description: string;
  children: React.ReactNode;
}

const Section: React.FC<SectionProps> = ({ id, icon, title, description, children }) => {
  const [open, setOpen] = useState(true);
  return (
    <div id={id} className="bg-[var(--c-card)] border border-[var(--c-border)] rounded-lg overflow-hidden">
      <button
        onClick={() => setOpen(o => !o)}
        className="w-full flex items-center justify-between px-5 py-4 hover:bg-[var(--c-input)] transition-colors text-left"
      >
        <div className="flex items-center gap-3">
          <div className="text-[var(--c-text3)]">{icon}</div>
          <div>
            <h3 className="text-sm font-semibold text-[var(--c-text)]">{title}</h3>
            <p className="text-xs text-[var(--c-text3)] mt-0.5">{description}</p>
          </div>
        </div>
        <ChevronDown size={15} className={`text-[var(--c-text3)] transition-transform ${open ? 'rotate-180' : ''}`} />
      </button>
      <AnimatePresence>
        {open && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: 'auto', opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            transition={{ duration: 0.2 }}
            className="overflow-hidden"
          >
            <div className="px-5 border-t border-[var(--c-border)]">
              {children}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
};

export default function Settings() {
  const queryClient = useQueryClient();
  const { toast } = useToast();

  const { data: settings, isLoading } = useQuery<SettingsData>({
    queryKey: ['settings'],
    queryFn: async () => {
      try {
        const { data } = await supabase.from('settings').select('*').limit(1).single();
        if (data) {
          const s = { ...data, enabled_sources: typeof data.enabled_sources === 'string' ? JSON.parse(data.enabled_sources) : (data.enabled_sources || DEFAULTS.enabled_sources) };
          localStorage.setItem(SETTINGS_KEY, JSON.stringify(s));
          return s;
        }
      } catch {}
      const stored = localStorage.getItem(SETTINGS_KEY);
      return stored ? JSON.parse(stored) : DEFAULTS;
    },
  });

  const [form, setForm] = useState<SettingsData>({});
  const [isDirty, setIsDirty] = useState(false);

  useEffect(() => {
    if (settings) {
      setForm(settings);
    }
  }, [settings]);

  const set = (key: string, value: any) => {
    setForm(prev => ({ ...prev, [key]: value }));
    setIsDirty(true);
  };

  const saveToBackend = async (data: SettingsData) => {
    const payload = { ...data, enabled_sources: JSON.stringify(data.enabled_sources) };
    delete (payload as any).search_keywords;
    delete (payload as any).disabled_keywords;
    const { error } = await supabase.from('settings').update(payload).eq('id', 1);
    if (error) {
      console.error("Failed to save settings:", error);
      throw error;
    }
  };

  const mutation = useMutation({
    mutationFn: async (data: SettingsData) => {
      const toSave = { ...DEFAULTS, ...data };
      localStorage.setItem(SETTINGS_KEY, JSON.stringify(toSave));
      await saveToBackend(toSave);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['settings'] });
      setIsDirty(false);
      toast('success', 'Settings Saved', 'Your configuration has been updated.');
    },
    onError: () => toast('error', 'Failed to Save Settings'),
  });

  const handleSaveFull = () => {
    if (isDirty) mutation.mutate(form);
  };

  const handleSavePartial = () => {
    if (isDirty) mutation.mutate(form);
  };

  const hasChanges = isDirty;

  if (isLoading) {
    return (
      <div className="space-y-4 animate-pulse">
        {Array.from({ length: 4 }).map((_, i) => (
          <div key={i} className="h-48 bg-[var(--c-card)] rounded-lg border border-[var(--c-border)]" />
        ))}
      </div>
    );
  }

  return (
    <div className="space-y-4 pb-24">
      <div className="flex items-center justify-between">
        <p className="text-sm text-[var(--c-text3)]">Manage your scraper configuration, AI settings, and integrations.</p>
        <button
          onClick={handleSaveFull}
          disabled={!hasChanges && !mutation.isPending}
          className="flex items-center gap-2 h-9 px-4 text-sm bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-md transition-colors"
        >
          <Save size={14} />
          {mutation.isPending ? 'Saving…' : 'Save All'}
        </button>
      </div>

      {/* General */}
      <Section id="general" icon={<SettingsIcon size={15} />} title="General" description="Application-wide settings">
        <SettingField label="Daily Schedule Time" description="Time the scraper automatically runs each day (24h format, e.g. 08:00 AM). Use top 'Save All' button to apply.">
          <input
            value={form.schedule_time ?? ''}
            onChange={e => set('schedule_time', e.target.value)}
            placeholder="08:00 AM"
            className={inputClass}
          />
        </SettingField>
      </Section>

      {/* Scraper */}
      <Section id="scraper" icon={<Sliders size={15} />} title="Scraper" description="Sources, timing and rate limit settings">
        <SettingField label="Enabled Sources" description="Select the job boards and platforms to scrape.">
          <div className="flex flex-col gap-2">
            {[
              { id: 'linkedin', label: 'LinkedIn (Scraper)' },
              { id: 'glassdoor', label: 'Glassdoor (Scraper)' },
            ].map(src => {
              const enabled = form.enabled_sources?.includes(src.id) || false;
              return (
                <label key={src.id} className="flex items-center gap-3 cursor-pointer group">
                  <div className={`w-4 h-4 rounded border flex items-center justify-center transition-colors ${enabled ? 'bg-blue-600 border-blue-600 text-white' : 'bg-[var(--c-input)] border-[var(--c-border)] text-transparent group-hover:border-[var(--c-hover)]'}`}>
                    <svg viewBox="0 0 14 14" fill="none" className="w-3 h-3" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <polyline points="2.5 7 5.5 10 11.5 4" />
                    </svg>
                  </div>
                  <span className={`text-sm ${enabled ? 'text-[var(--c-text)]' : 'text-[var(--c-text3)] group-hover:text-[var(--c-text2)]'}`}>{src.label}</span>
                  <input
                    type="checkbox"
                    className="hidden"
                    checked={enabled}
                    onChange={(e) => {
                      const newSources = e.target.checked
                        ? [...(form.enabled_sources || []), src.id]
                        : (form.enabled_sources || []).filter(s => s !== src.id);
                      set('enabled_sources', newSources);
                    }}
                  />
                </label>
              );
            })}
          </div>
        </SettingField>
        <SettingField label="Request Delay (sec)" description="Seconds to wait between requests to avoid rate limiting.">
          <input
            type="number"
            value={form.delay_between_requests ?? ''}
            onChange={e => set('delay_between_requests', parseFloat(e.target.value))}
            placeholder="2"
            min={0}
            step={0.5}
            className={inputClass}
          />
        </SettingField>
        <SettingField label="Request Timeout (sec)" description="Max seconds to wait for a page to load.">
          <input
            type="number"
            value={form.timeout ?? ''}
            onChange={e => set('timeout', parseInt(e.target.value))}
            placeholder="30"
            min={5}
            className={inputClass}
          />
        </SettingField>
        <SettingField label="Max Jobs per Keyword" description="Maximum number of jobs to collect per keyword per run.">
          <input
            type="number"
            value={form.max_jobs_per_keyword ?? ''}
            onChange={e => set('max_jobs_per_keyword', parseInt(e.target.value))}
            placeholder="50"
            min={1}
            className={inputClass}
          />
        </SettingField>
        <SettingField label="Max Pages per Source" description="Maximum number of pages to paginate through.">
          <input
            type="number"
            value={form.max_pages_per_source ?? ''}
            onChange={e => set('max_pages_per_source', parseInt(e.target.value))}
            placeholder="5"
            min={1}
            className={inputClass}
          />
        </SettingField>
        <SettingField label="Retry Count" description="Number of times to retry failed requests.">
          <input
            type="number"
            value={form.retry_count ?? ''}
            onChange={e => set('retry_count', parseInt(e.target.value))}
            placeholder="3"
            min={0}
            className={inputClass}
          />
        </SettingField>
        <SettingField label="Concurrency" description="Number of parallel scraping tasks.">
          <input
            type="number"
            value={form.concurrency ?? ''}
            onChange={e => set('concurrency', parseInt(e.target.value))}
            placeholder="2"
            min={1}
            className={inputClass}
          />
        </SettingField>
      </Section>

      {/* AI */}
      <Section id="ai" icon={<Brain size={15} />} title="AI" description="AI model and budget configuration">
        <SettingField label="AI Model" description="The model used for job evaluation.">
          <input
            value={form.ai_model ?? ''}
            onChange={e => set('ai_model', e.target.value)}
            placeholder="openai/gpt-4o-mini"
            className={inputClass}
          />
        </SettingField>
        <SettingField label="AI System Prompt" description="The instruction provided to the AI for filtering.">
          <textarea
            value={form.ai_system_prompt ?? ''}
            onChange={e => set('ai_system_prompt', e.target.value)}
            placeholder="Evaluate if this job is a good fit."
            className={textareaClass}
          />
        </SettingField>
        <SettingField label="Daily AI Budget" description="Maximum number of AI evaluation requests per day.">
          <input
            type="number"
            value={form.ai_request_budget_daily ?? ''}
            onChange={e => set('ai_request_budget_daily', parseInt(e.target.value))}
            placeholder="100"
            min={1}
            className={inputClass}
          />
        </SettingField>
      </Section>

      {/* Search */}
      <Section id="search" icon={<Search size={15} />} title="Search" description="Job search preferences and filters">
        <div className="py-4 border-b border-[var(--c-border)]">
          <div className="mb-4">
            <label className="text-sm font-medium text-[var(--c-text)]">Search Locations</label>
            <p className="text-xs text-[var(--c-text3)] mt-0.5 leading-relaxed">Select the countries you want to search in.</p>
          </div>
          <div className="space-y-4">
            {Object.entries(REGIONS).map(([regionName, countries]) => (
              <div key={regionName}>
                <div className="text-xs font-semibold text-[var(--c-text3)] mb-2 uppercase tracking-wide">{regionName}</div>
                <div className="flex flex-wrap gap-2">
                  {countries.map(country => {
                    const selectedList = (form.search_locations ?? '').split(',').map(s => s.trim()).filter(Boolean);
                    const isSelected = selectedList.includes(country);
                    return (
                      <button
                        key={country}
                        onClick={() => {
                          if (isSelected) {
                            set('search_locations', selectedList.filter(c => c !== country).join(', '));
                          } else {
                            set('search_locations', [...selectedList, country].join(', '));
                          }
                        }}
                        className={`px-3 py-1.5 text-xs font-medium rounded-full border transition-colors ${
                          isSelected 
                            ? 'bg-blue-600/10 border-blue-500/30 text-blue-400' 
                            : 'bg-[var(--c-bg)] border-[var(--c-border)] text-[var(--c-text2)] hover:border-[var(--c-hover)]'
                        }`}
                      >
                        {country}
                      </button>
                    );
                  })}
                </div>
              </div>
            ))}
          </div>
        </div>
        <SettingField label="Search Provider" description="Default search provider used as fallback.">
          <select value={form.search_provider ?? ''} onChange={e => set('search_provider', e.target.value)} className={selectClass}>
            <option value="google">Google</option>
          </select>
        </SettingField>
      </Section>

      {/* Sticky Save Bar */}
      <AnimatePresence>
        {hasChanges && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: 20 }}
            className="fixed bottom-0 left-0 right-0 z-40 border-t border-[var(--c-border)] bg-[var(--c-bg)]/95 backdrop-blur px-6 py-4 flex items-center justify-between shadow-2xl"
          >
            <p className="text-sm text-[var(--c-text2)]">You have unsaved changes.</p>
            <div className="flex items-center gap-3">
              <button
                onClick={() => {
                  setForm(settings ?? {});
                  setIsDirty(false);
                }}
                className="h-9 px-4 text-sm text-[var(--c-text3)] hover:text-[var(--c-text)] border border-[var(--c-border)] rounded-md transition-colors"
              >
                Discard
              </button>
              <button
                onClick={handleSavePartial}
                disabled={mutation.isPending}
                className="flex items-center gap-2 h-9 px-4 text-sm bg-blue-600 hover:bg-blue-500 disabled:opacity-50 text-white rounded-md transition-colors"
              >
                <Save size={14} />
                {mutation.isPending ? 'Saving…' : 'Save (excl. schedule)'}
              </button>
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
