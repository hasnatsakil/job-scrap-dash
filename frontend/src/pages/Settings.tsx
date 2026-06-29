import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Label } from '@/components/ui/label';
export default function Settings() {
  const queryClient = useQueryClient();
  const { data: settings, isLoading } = useQuery({ queryKey: ['settings'], queryFn: async () => (await axios.get('/api/settings')).data });
  const mutation = useMutation({ mutationFn: (newSettings: any) => axios.put('/api/settings', newSettings), onSuccess: () => { queryClient.invalidateQueries({ queryKey: ['settings'] }); alert('Settings saved!'); } });
  if (isLoading) return <div>Loading settings...</div>;
  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    const formData = new FormData(e.target as HTMLFormElement);
    mutation.mutate({ ...settings, schedule_time: formData.get('schedule_time'), ai_model: formData.get('ai_model'), ai_request_budget_daily: parseInt(formData.get('ai_budget') as string) });
  };
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Settings</h1>
      <Card>
        <CardHeader><CardTitle>Configuration Cache</CardTitle></CardHeader>
        <CardContent>
          <form onSubmit={handleSubmit} className="space-y-4">
            <div className="grid grid-cols-2 gap-4">
              <div className="space-y-2"><Label htmlFor="schedule_time">Daily Schedule Time</Label><Input id="schedule_time" name="schedule_time" defaultValue={settings?.schedule_time} /></div>
              <div className="space-y-2"><Label htmlFor="ai_model">AI Model</Label><Input id="ai_model" name="ai_model" defaultValue={settings?.ai_model} /></div>
              <div className="space-y-2"><Label htmlFor="ai_budget">Daily AI Budget</Label><Input id="ai_budget" name="ai_budget" type="number" defaultValue={settings?.ai_request_budget_daily} /></div>
            </div>
            <div className="pt-4"><Button type="submit" disabled={mutation.isPending}>{mutation.isPending ? 'Saving...' : 'Save Settings'}</Button></div>
          </form>
        </CardContent>
      </Card>
    </div>
  );
}
