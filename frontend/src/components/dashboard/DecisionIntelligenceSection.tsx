import { useMemo } from 'react';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { EmptyState } from '@/components/ui/EmptyState';
import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
  PieChart, Pie, Cell, Legend
} from 'recharts';

interface DIProps {
  data: any;
  isLoading: boolean;
}

const COLORS = ['#1e3a8a', '#3b82f6', '#64748b', '#94a3b8'];
const STATUS_COLORS = { 'OPEN': '#eab308', 'CLOSED': '#22c55e', 'PENDING': '#f97316', 'APPROVED': '#3b82f6' };

export function DecisionIntelligenceSection({ data, isLoading }: DIProps) {
  const { barData, pieData } = useMemo(() => {
    if (!data) return { barData: [], pieData: [] };
    
    const intents = data.cases_by_intent || {};
    const statuses = data.cases_by_status || {};
    
    const bData = Object.keys(intents).map(k => ({ name: k, value: intents[k] }));
    const pData = Object.keys(statuses).map(k => ({ name: k, value: statuses[k] }));
    
    return { barData: bData, pieData: pData };
  }, [data]);

  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2">
        <Skeleton className="h-[350px]" />
        <Skeleton className="h-[350px]" />
      </div>
    );
  }

  return (
    <div className="grid gap-4 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>Cases by Intent</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px]">
          {barData.length === 0 ? (
            <EmptyState description="No intent data logged yet." />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <BarChart data={barData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <CartesianGrid strokeDasharray="3 3" vertical={false} stroke="#e2e8f0" />
                <XAxis dataKey="name" tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <YAxis tick={{ fontSize: 12, fill: '#64748b' }} axisLine={false} tickLine={false} />
                <Tooltip cursor={{ fill: '#f1f5f9' }} contentStyle={{ borderRadius: '6px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Bar dataKey="value" fill="#1e3a8a" radius={[4, 4, 0, 0]} />
              </BarChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
      
      <Card>
        <CardHeader>
          <CardTitle>Decision Status</CardTitle>
        </CardHeader>
        <CardContent className="h-[300px]">
          {pieData.length === 0 ? (
            <EmptyState description="No status data logged yet." />
          ) : (
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={80}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={STATUS_COLORS[entry.name as keyof typeof STATUS_COLORS] || COLORS[index % COLORS.length]} />
                  ))}
                </Pie>
                <Tooltip contentStyle={{ borderRadius: '6px', border: 'none', boxShadow: '0 4px 6px -1px rgb(0 0 0 / 0.1)' }} />
                <Legend verticalAlign="bottom" height={36} iconType="circle" />
              </PieChart>
            </ResponsiveContainer>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
