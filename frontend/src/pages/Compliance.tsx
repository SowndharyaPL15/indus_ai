import { useQuery } from '@tanstack/react-query';
import { api } from '@/services/api';
import { Card, CardContent } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { ErrorState } from '@/components/ui/ErrorState';
import { EmptyState } from '@/components/ui/EmptyState';
import { ShieldCheck, ShieldAlert, FileWarning, CheckCircle } from 'lucide-react';

export default function Compliance() {
  const { data, isLoading, isError, refetch } = useQuery({
    queryKey: ['dashboard', 'compliance'],
    queryFn: async () => (await api.get('/api/dashboard/compliance')).data,
  });

  if (isError) return <ErrorState message="Failed to load compliance data." onRetry={refetch} />;

  const kpis = [
    { title: 'Open Compliance Gaps', value: data?.open_compliance_gaps || 0, icon: <FileWarning className="h-5 w-5 text-destructive" /> },
    { title: 'Approved Exceptions', value: data?.approved_exceptions || 0, icon: <CheckCircle className="h-5 w-5 text-green-600" /> },
    { title: 'Pending Compliance Checks', value: data?.pending_compliance_checks || 0, icon: <ShieldAlert className="h-5 w-5 text-warning" /> },
    { title: 'Total Compliance Cases', value: (data?.open_compliance_gaps || 0) + (data?.approved_exceptions || 0), icon: <ShieldCheck className="h-5 w-5 text-primary" /> },
  ];

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Compliance & Auditing</h1>
        <p className="text-muted-foreground">Monitor regulatory gaps and compliance checks across all decision cases.</p>
      </div>

      {isLoading ? (
        <div className="grid gap-4 md:grid-cols-4">
          {[1, 2, 3, 4].map((i) => <Skeleton key={i} className="h-[120px]" />)}
        </div>
      ) : (
        <div className="grid gap-4 md:grid-cols-4">
          {kpis.map((kpi, idx) => (
            <Card key={idx}>
              <CardContent className="p-6 flex items-center justify-between">
                <div>
                  <p className="text-sm font-medium text-muted-foreground">{kpi.title}</p>
                  <h3 className="text-3xl font-bold mt-2">{kpi.value}</h3>
                </div>
                <div className="bg-secondary/50 p-3 rounded-full">{kpi.icon}</div>
              </CardContent>
            </Card>
          ))}
        </div>
      )}

      <div className="bg-card border rounded-lg overflow-hidden shadow-sm">
         <div className="p-12">
            <EmptyState title="No Active Audits" description="There are no detailed compliance audits currently running." />
         </div>
      </div>
    </div>
  );
}
