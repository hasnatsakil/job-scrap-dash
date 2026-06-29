import React, { useState } from 'react';
import { useQuery } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent } from '@/components/ui/card';
import { Table, TableBody, TableCell, TableHead, TableHeader, TableRow } from '@/components/ui/table';
import { Badge } from '@/components/ui/badge';
import { Input } from '@/components/ui/input';
export default function Jobs() {
  const [search, setSearch] = useState('');
  const { data, isLoading } = useQuery({ queryKey: ['jobs'], queryFn: async () => (await axios.get('/api/jobs')).data.jobs || [] });
  if (isLoading) return <div>Loading jobs...</div>;
  const filteredJobs = data?.filter((job: any) => job['Job Title']?.toLowerCase().includes(search.toLowerCase()) || job['Company']?.toLowerCase().includes(search.toLowerCase())) || [];
  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center"><h1 className="text-3xl font-bold">Jobs</h1><Input placeholder="Search jobs..." className="w-64" value={search} onChange={(e) => setSearch(e.target.value)} /></div>
      <Card>
        <CardContent className="p-0">
          <Table>
            <TableHeader><TableRow><TableHead>Date</TableHead><TableHead>Company</TableHead><TableHead>Title</TableHead><TableHead>Location</TableHead><TableHead>Source</TableHead><TableHead>AI Status</TableHead><TableHead>Action</TableHead></TableRow></TableHeader>
            <TableBody>
              {filteredJobs.slice(0, 50).map((job: any, i: number) => (
                <TableRow key={i}>
                  <TableCell>{job['Scraped Date']?.split('T')[0]}</TableCell><TableCell className="font-medium">{job['Company']}</TableCell><TableCell>{job['Job Title']}</TableCell><TableCell>{job['Location']}</TableCell><TableCell>{job['Source']}</TableCell>
                  <TableCell>{job['AI Decision'] === 'Keep' ? <Badge className="bg-green-500">Keep ({job['AI Score']})</Badge> : job['AI Decision'] === 'Reject' ? <Badge variant="destructive">Reject</Badge> : <Badge variant="outline" className="text-orange-500 border-orange-500">Pending</Badge>}</TableCell>
                  <TableCell><a href={job['Job URL']} target="_blank" rel="noopener noreferrer" className="text-blue-500 hover:underline">View</a></TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </CardContent>
      </Card>
    </div>
  );
}
