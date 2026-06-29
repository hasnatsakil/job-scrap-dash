import React from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { CheckCircle, XCircle, Search, Clock } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer } from 'recharts';
export default function Dashboard() {
  const { data: stats, isLoading } = useQuery({ queryKey: ['stats'], queryFn: async () => (await axios.get('/api/stats')).data });
  const chartData = [
    { name: 'Mon', jobs: 40 }, { name: 'Tue', jobs: 30 }, { name: 'Wed', jobs: 20 },
    { name: 'Thu', jobs: 27 }, { name: 'Fri', jobs: 18 }, { name: 'Sat', jobs: 23 }, { name: 'Sun', jobs: 34 }
  ];
  if (isLoading) return <div>Loading dashboard...</div>;
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Dashboard</h1>
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Total Found</CardTitle><Search className="h-4 w-4 text-muted-foreground" /></CardHeader><CardContent><div className="text-2xl font-bold">{stats?.total_found || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">AI Accepted</CardTitle><CheckCircle className="h-4 w-4 text-green-500" /></CardHeader><CardContent><div className="text-2xl font-bold">{stats?.ai_accepted || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">AI Rejected</CardTitle><XCircle className="h-4 w-4 text-red-500" /></CardHeader><CardContent><div className="text-2xl font-bold">{stats?.ai_rejected || 0}</div></CardContent></Card>
        <Card><CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2"><CardTitle className="text-sm font-medium">Pending Review</CardTitle><Clock className="h-4 w-4 text-orange-500" /></CardHeader><CardContent><div className="text-2xl font-bold">{(stats?.total_found || 0) - (stats?.ai_accepted || 0) - (stats?.ai_rejected || 0)}</div></CardContent></Card>
      </div>
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
