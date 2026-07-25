import { Card, CardHeader, CardTitle, CardContent } from '@/components/ui/Card';

export function EvidenceGraphCard({ graph }: { graph: any }) {
  if (!graph) return null;

  // Find groups based on CaseContextResponse schema
  const documentsGroup = graph.groups?.find((g: any) => g.entity_type === 'DOCUMENT') || { entities: [] };
  const reasoningGroup = graph.groups?.find((g: any) => g.entity_type === 'REASONING_MEMORY') || { entities: [] };

  return (
    <Card className="col-span-full">
      <CardHeader>
        <CardTitle>Evidence & Knowledge Graph Context</CardTitle>
      </CardHeader>
      <CardContent className="grid grid-cols-1 md:grid-cols-2 gap-8">
        <div>
          <h4 className="font-semibold text-sm mb-3">Supporting Documents</h4>
          <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4">
            {documentsGroup.entities.map((e: any, i: number) => (
              <li key={i}>{e.entity_id} ({e.relationship_type})</li>
            ))}
            {documentsGroup.entities.length === 0 && <li>No direct documents linked.</li>}
          </ul>
        </div>
        <div>
          <h4 className="font-semibold text-sm mb-3">Similar Reasoning Cases</h4>
          <ul className="space-y-2 text-sm text-muted-foreground list-disc pl-4">
            {reasoningGroup.entities.map((e: any, i: number) => (
              <li key={i}>{e.entity_id} (Score: {(e.properties?.similarity_score || 0).toFixed(2)})</li>
            ))}
             {reasoningGroup.entities.length === 0 && <li>No historical cases match.</li>}
          </ul>
        </div>
        <div className="col-span-full pt-4 border-t">
           <h4 className="font-semibold text-sm mb-3">Factory Memory Context</h4>
           <p className="text-sm text-muted-foreground">
             Total connected entities evaluated: {graph.total_connections || 0}
           </p>
        </div>
      </CardContent>
    </Card>
  );
}
