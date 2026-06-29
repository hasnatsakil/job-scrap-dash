import React from 'react';
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import axios from 'axios';
import { Card, CardContent, CardHeader, CardTitle, CardDescription, CardFooter } from '@/components/ui/card';
import { Button } from '@/components/ui/button';
import { Badge } from '@/components/ui/badge';
import { Loader2, Link, Database, BrainCircuit, AlertTriangle, CheckCircle2 } from 'lucide-react';

export default function Connections() {
  const queryClient = useQueryClient();

  const { data: health, isLoading } = useQuery({
    queryKey: ['health'],
    queryFn: async () => (await axios.get('/api/health')).data,
    refetchInterval: 10000
  });

  const connectMutation = useMutation({
    mutationFn: (provider: string) => axios.post(`/api/connections/${provider}/connect`),
    onSuccess: () => {
        queryClient.invalidateQueries({ queryKey: ['health'] });
        alert("Connection successful");
    },
    onError: (error: any) => alert(`Connection failed: ${error.response?.data?.detail || error.message}`)
  });

  const disconnectMutation = useMutation({
    mutationFn: (provider: string) => axios.post(`/api/connections/${provider}/disconnect`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['health'] })
  });

  const validateMutation = useMutation({
    mutationFn: (provider: string) => axios.post(`/api/connections/${provider}/validate`),
    onSuccess: () => queryClient.invalidateQueries({ queryKey: ['health'] }),
    onError: () => alert("Validation check failed.")
  });

  if (isLoading) return <div>Loading connections...</div>;

  const linkedinStatus = health?.connections?.linkedin;

  return (
    <div className="space-y-6">
      <div className="flex justify-between items-center">
        <h1 className="text-3xl font-bold">Connections</h1>
        <p className="text-sm text-gray-500">Manage authenticated sessions for job boards and external services.</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">

        {/* LinkedIn Connection Card */}
        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-2">
                <Link className="h-6 w-6 text-blue-600" />
                <CardTitle>LinkedIn</CardTitle>
              </div>
              {linkedinStatus?.status === "Connected" ? (
                <Badge className="bg-green-500">Connected</Badge>
              ) : linkedinStatus?.status === "Expired" ? (
                <Badge variant="destructive">Expired</Badge>
              ) : (
                <Badge variant="secondary">Not Connected</Badge>
              )}
            </div>
            <CardDescription>
              Authenticated browser session for reliable scraping without limits.
            </CardDescription>
          </CardHeader>

          <CardContent className="flex-1 space-y-4 text-sm">
            {linkedinStatus?.status !== "Not Connected" ? (
              <>
                <div className="flex justify-between">
                  <span className="text-gray-500">Last Login</span>
                  <span>{linkedinStatus?.last_login ? new Date(linkedinStatus.last_login).toLocaleString() : 'N/A'}</span>
                </div>
                <div className="flex justify-between">
                  <span className="text-gray-500">Last Validated</span>
                  <span>{linkedinStatus?.last_validation ? new Date(linkedinStatus.last_validation).toLocaleString() : 'N/A'}</span>
                </div>
                {linkedinStatus?.status === "Expired" && (
                  <div className="bg-red-50 text-red-700 p-3 rounded-md flex items-center space-x-2 mt-4">
                    <AlertTriangle className="h-4 w-4" />
                    <span>Session expired. Please reconnect.</span>
                  </div>
                )}
              </>
            ) : (
              <div className="text-gray-500 italic">No active session stored.</div>
            )}
          </CardContent>

          <CardFooter className="flex flex-wrap gap-2 border-t pt-4">
            {linkedinStatus?.status !== "Connected" ? (
              <Button
                onClick={() => connectMutation.mutate('linkedin')}
                disabled={connectMutation.isPending}
                className="w-full sm:w-auto"
              >
                {connectMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                Connect LinkedIn
              </Button>
            ) : (
              <>
                <Button
                  variant="outline"
                  onClick={() => validateMutation.mutate('linkedin')}
                  disabled={validateMutation.isPending}
                >
                  {validateMutation.isPending && <Loader2 className="mr-2 h-4 w-4 animate-spin" />}
                  Test Connection
                </Button>
                <Button
                  variant="destructive"
                  onClick={() => disconnectMutation.mutate('linkedin')}
                  disabled={disconnectMutation.isPending}
                >
                  Disconnect
                </Button>
              </>
            )}
          </CardFooter>
        </Card>

        {/* Google Sheets Connection Card */}
        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-2">
                <Database className="h-6 w-6 text-green-600" />
                <CardTitle>Google Sheets</CardTitle>
              </div>
              {health?.google_sheets_configured ? (
                <Badge className="bg-green-500">Configured</Badge>
              ) : (
                <Badge variant="destructive">Missing Config</Badge>
              )}
            </div>
            <CardDescription>
              Primary database for persistence.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 space-y-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Sync Status</span>
              <span>{health?.google_sheets_configured ? 'Active via Environment' : 'Requires .env setup'}</span>
            </div>
          </CardContent>
        </Card>

        {/* OpenRouter Connection Card */}
        <Card className="flex flex-col">
          <CardHeader>
            <div className="flex justify-between items-start">
              <div className="flex items-center space-x-2">
                <BrainCircuit className="h-6 w-6 text-purple-600" />
                <CardTitle>OpenRouter AI</CardTitle>
              </div>
              <Badge className="bg-green-500">Active</Badge>
            </div>
            <CardDescription>
              AI filtering service provider.
            </CardDescription>
          </CardHeader>
          <CardContent className="flex-1 space-y-4 text-sm">
            <div className="flex justify-between">
              <span className="text-gray-500">Daily Budget Used</span>
              <span>{health?.ai_budget_used} / {health?.ai_budget_total}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-gray-500">Remaining</span>
              <span className="font-medium text-green-600">{health?.ai_budget_total - health?.ai_budget_used}</span>
            </div>
          </CardContent>
        </Card>

      </div>
    </div>
  );
}
