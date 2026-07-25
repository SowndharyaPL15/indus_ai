import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export function DetailsOverviewCard({ caseDetails }: { caseDetails: any }) {
  if (!caseDetails) return null;
  
  return (
    <Card>
      <CardHeader>
        <CardTitle>Case Overview</CardTitle>
      </CardHeader>
      <CardContent className="space-y-4">
        <div>
          <h4 className="text-sm font-semibold text-muted-foreground">Original Query</h4>
          <p className="mt-1 text-sm">{caseDetails.query}</p>
        </div>
        <div className="grid grid-cols-2 gap-4 pt-4 border-t">
          <div>
            <h4 className="text-sm font-semibold text-muted-foreground">Recommended Action</h4>
            <p className="mt-1 text-sm font-medium">Auto-shutdown CNC Machine and schedule Maintenance.</p>
          </div>
          <div>
            <h4 className="text-sm font-semibold text-muted-foreground">Approval Status</h4>
            <div className="mt-1">
               <Badge variant="warning">PENDING APPROVAL</Badge>
            </div>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
