import React from 'react';
import { Card, CardContent } from '@/components/ui/card';
export default function Logs() {
  return (
    <div className="space-y-6">
      <h1 className="text-3xl font-bold">Logs</h1>
      <Card><CardContent className="pt-6 text-gray-500">Logs feature will read from the Google Sheets "Logs" tab in a future iteration.</CardContent></Card>
    </div>
  );
}
