import { FileText, Database, GitMerge, Network } from 'lucide-react';

interface Props {
  graph: any;
}

export function EvidenceTimeline({ graph }: Props) {
  if (!graph) {
    return <p className="text-sm text-muted-foreground pt-3">No evidence data available.</p>;
  }

  const docEdges = graph.edges?.filter((e: any) => e.relationship === "REFERENCES") || [];
  const similarEdges = graph.edges?.filter((e: any) => e.relationship === "SIMILAR_TO") || [];
  const otherEdges = graph.edges?.filter((e: any) => e.relationship !== "REFERENCES" && e.relationship !== "SIMILAR_TO") || [];

  const categories = [
    { title: "Documents", icon: <FileText className="h-4 w-4" />, items: docEdges.map((e: any) => e.target) },
    { title: "Factory Memories", icon: <Database className="h-4 w-4" />, items: otherEdges.map((e: any) => e.target) },
    { title: "Similar Reasoning Cases", icon: <GitMerge className="h-4 w-4" />, items: similarEdges.map((e: any) => `${e.target} (${(e.weight * 100).toFixed(0)}% match)`) },
    { title: "Knowledge Graph Nodes", icon: <Network className="h-4 w-4" />, items: (graph.nodes || []).map((n: any) => n.label || n.id || n) },
  ];

  return (
    <div className="space-y-4 pt-3">
      {categories.map((cat, idx) => (
        <div key={idx}>
          <div className="flex items-center space-x-2 mb-2">
            <span className="text-muted-foreground">{cat.icon}</span>
            <h4 className="text-xs font-semibold uppercase tracking-wider text-muted-foreground">{cat.title}</h4>
          </div>
          {cat.items.length === 0 ? (
            <p className="text-xs text-muted-foreground pl-6">No items found.</p>
          ) : (
            <div className="space-y-1 pl-6">
              {cat.items.map((item: string, i: number) => (
                <div key={i} className="text-sm border rounded-md px-3 py-2 bg-secondary/30 truncate" title={item}>
                  {item}
                </div>
              ))}
            </div>
          )}
        </div>
      ))}
    </div>
  );
}
