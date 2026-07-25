import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';

export function ConfidenceCard({ confidence }: { confidence: any }) {
  if (!confidence) return null;

  return (
    <Card>
      <CardHeader>
        <CardTitle>Confidence Breakdown</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex items-center space-x-4 mb-4">
          <div className="text-4xl font-bold text-primary">{(confidence.score * 100).toFixed(1)}%</div>
          <Badge variant={confidence.score >= 0.7 ? "success" : "warning"}>
            {confidence.level}
          </Badge>
        </div>
        <div className="space-y-2">
          {Object.entries(confidence.component_scores || {}).map(([key, val]: [string, any]) => (
            <div key={key} className="flex justify-between items-center text-sm border-b pb-2 last:border-0 capitalize">
              <span className="text-muted-foreground">{key.replace('_', ' ')}</span>
              <span className="font-medium">{(val * 100).toFixed(0)}% Score</span>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
