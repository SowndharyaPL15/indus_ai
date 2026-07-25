import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';

interface CCProps {
  complianceData: any;
  conflictsData: any;
  isLoading: boolean;
}

export function ComplianceConflictsSection({ complianceData, conflictsData, isLoading }: CCProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-4">
        {Array.from({ length: 4 }).map((_, i) => (
          <Skeleton key={i} className="h-[120px]" />
        ))}
      </div>
    );
  }

  const items = [
    { title: "Compliance Gaps", value: complianceData?.open_compliance_gaps || 0, color: "text-destructive" },
    { title: "Pending Approvals", value: complianceData?.pending_approvals || 0, color: "text-yellow-600" },
    { title: "Approved Cases", value: complianceData?.approved_cases || 0, color: "text-green-600" },
    { title: "Total Conflicts", value: conflictsData?.total_conflicts || 0, color: "text-orange-500" },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-4">
      {items.map((item, idx) => (
        <Card key={idx}>
          <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
            <CardTitle className="text-sm font-medium text-muted-foreground">{item.title}</CardTitle>
          </CardHeader>
          <CardContent>
            <div className={`text-2xl font-bold ${item.color}`}>{item.value}</div>
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
