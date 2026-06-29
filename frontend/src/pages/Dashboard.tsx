import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, XCircle, Search, Clock, Link as LinkIcon, HeartPulse } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';

export default function Dashboard() {
  const { data: stats, isLoading: statsLoading } = useQuery({ queryKey: ['stats'], queryFn: async () => (await axios.get('/api/stats')).data });
  const { data: health, isLoading: healthLoading } = useQuery({ queryKey: ['health'], queryFn: async () => (await axios.get('/api/health')).data });

  const chartData = [
    { name: 'Mon', jobs: 40 }, { name: 'Tue', jobs: 30 }, { name: 'Wed', jobs: 20 },
    { name: 'Thu', jobs: 27 }, { name: 'Fri', jobs: 18 }, { name: 'Sat', jobs: 23 }, { name: 'Sun', jobs: 34 }
  ];

  if (statsLoading || healthLoading) return <div>Loading dashboard...</div>;

  const linkedinStatus = health?.connections?.linkedin?.status;

  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>

      {/* Top Stats */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Total Found</CardTitle><Search className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{stats?.total_found || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">AI Accepted</CardTitle><CheckCircle className="h-4 w-4 text-green-500" /></CardHeader><CardContent><div className="text-2xl font-bold">{stats?.ai_accepted || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">AI Rejected</CardTitle><XCircle className="h-4 w-4 text-red-500" /></CardHeader><CardContent><div className="text-2xl font-bold">{stats?.ai_rejected || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Pending Review</CardTitle><Clock className="h-4 w-4 text-orange-500" /></CardHeader><CardContent><div className="text-2xl font-bold">{(stats?.total_found || 0) - (stats?.ai_accepted || 0) - (stats?.ai_rejected || 0)}</div></CardContent></Card>
      </div>

      {/* Health Overview */}
      <Card className="bg-slate-50">
        <CardHeader className="pb-3">
          <CardTitle className="flex items-center text-lg"><HeartPulse className="h-5 w-5 mr-2" /> System Health</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm">
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${health?.scheduler_status === 'Running' ? 'bg-green-500' : 'bg-yellow-500'}`}></div>
              <span>Scheduler: {health?.scheduler_status}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${linkedinStatus === 'Connected' ? 'bg-green-500' : linkedinStatus === 'Expired' ? 'bg-red-500' : 'bg-yellow-500'}`}></div>
              <span>LinkedIn: {linkedinStatus || 'Not Connected'}</span>
            </div>
            <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${health?.google_sheets_configured ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span>Sheets: {health?.google_sheets_configured ? 'Ready' : 'Missing'}</span>
            </div>
             <div className="flex items-center space-x-2">
              <div className={`w-3 h-3 rounded-full ${health?.ai_budget_used < health?.ai_budget_total ? 'bg-green-500' : 'bg-red-500'}`}></div>
              <span>AI Budget: {health?.ai_budget_total - health?.ai_budget_used} left</span>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card className="col-span-4">
        <CardHeader><CardTitle>Jobs Over Time</CardTitle></CardHeader>
        <CardContent className="pl-2">
          <div className="h-[300px] w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={chartData}>
                <XAxis dataKey="name" stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <YAxis stroke="#888888" fontSize={12} tickLine={false} axisLine={false} />
                <Tooltip />
                <Bar dataKey="jobs" fill="#3b82f6" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
