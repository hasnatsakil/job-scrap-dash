import React from 'react';
import { useQuery, useMutation } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Play } from 'lucide-react';
export default function Health() {
  const { data: health, isLoading } = useQuery({ queryKey: ['health'], queryFn: async () => (await axios.get('/api/health')).data, refetchInterval: 5000 });
  const runMutation = useMutation({ mutationFn: () => axios.post('/api/run'), onSuccess: () => alert('Scraping started') });
  if (isLoading) return <div>Loading...</div>;
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center"><h1 className="text-3xl font-bold">System Health</h1><Button onClick={() => runMutation.mutate()} disabled={runMutation.isPending}><Play className="mr-2 h-4 w-4" /> Run Scraper Now</Button></div>
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        <Card><CardHeader><CardTitle>System Status</CardTitle></CardHeader><CardContent className="space-y-4"><div className="flex justify-between border-b pb-2"><span className="text-gray-500">Scheduler</span><span className="font-medium">{health?.scheduler_status}</span></div><div className="flex justify-between border-b pb-2"><span className="text-gray-500">Sheets Configured</span><span className="font-medium">{health?.google_sheets_configured ? 'Yes' : 'No'}</span></div><div className="flex justify-between border-b pb-2"><span className="text-gray-500">Last Attempt</span><span className="font-medium">{health?.last_scrape_attempt || 'Never'}</span></div></CardContent></Card>
        <Card><CardHeader><CardTitle>AI & Limits</CardTitle></CardHeader><CardContent className="space-y-4"><div className="flex justify-between border-b pb-2"><span className="text-gray-500">Daily AI Budget</span><span className="font-medium">{health?.ai_budget_used} / {health?.ai_budget_total}</span></div><div className="flex justify-between border-b pb-2"><span className="text-gray-500">Active Sources</span><span className="font-medium">{health?.active_sources}</span></div><div className="flex justify-between border-b pb-2"><span className="text-gray-500">Active Keywords</span><span className="font-medium">{health?.active_keywords}</span></div></CardContent></Card>
      </div>
    </div>
  );
}
