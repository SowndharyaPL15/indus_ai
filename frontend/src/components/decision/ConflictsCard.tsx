import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { AlertCircle } from 'lucide-react';

export function ConflictsCard({ conflicts }: { conflicts: any }) {
  if (!conflicts || !conflicts.has_conflicts || conflicts.conflicts.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>Conflict Summary</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex items-center text-green-600 text-sm">
            <Badge variant="success" className="mr-2">SAFE</Badge>
            No critical operational conflicts detected.
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card className="border-destructive">
      <CardHeader className="bg-destructive/10 text-destructive">
        <CardTitle className="flex items-center">
          <AlertCircle className="mr-2 h-5 w-5" />
          Conflict Summary
        </CardTitle>
      </CardHeader>
      <CardContent className="pt-4 space-y-4">
        {conflicts.conflicts.map((conflict: any, idx: number) => (
          <div key={idx} className="flex flex-col space-y-1 pb-4 border-b last:border-0 last:pb-0">
            <div className="flex justify-between items-start">
              <span className="font-semibold text-sm">{conflict.type}</span>
              <Badge variant="destructive">{conflict.severity}</Badge>
            </div>
            <p className="text-sm text-muted-foreground">{conflict.description}</p>
          </div>
        ))}
      </CardContent>
    </Card>
  );
}
