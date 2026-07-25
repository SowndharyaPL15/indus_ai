import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Badge } from '@/components/ui/Badge';
import { Skeleton } from '@/components/ui/Skeleton';

interface HealthProps {
  data: any;
  isLoading: boolean;
}

export function SystemHealthSection({ data, isLoading }: HealthProps) {
  if (isLoading) {
    return <Skeleton className="h-[100px] w-full" />;
  }

  const components = [
    { name: "Database", status: data?.database?.status || "Unknown" },
    { name: "FAISS", status: data?.faiss?.status || "Unknown" },
    { name: "RAG", status: data?.rag?.status || "Unknown" },
    { name: "Knowledge Graph", status: data?.knowledge_graph?.status || "Unknown" },
    { name: "IDIE", status: data?.idie?.status || "Unknown" },
    { name: "Memory Engine", status: data?.memory_engine?.status || "Unknown" },
  ];

  const getVariant = (status: string) => {
    switch (status) {
      case "Healthy": return "success";
      case "Warning": return "warning";
      case "Offline": return "destructive";
      default: return "secondary";
    }
  };

  return (
    <Card>
      <CardHeader>
        <CardTitle className="text-sm text-muted-foreground">System Health</CardTitle>
      </CardHeader>
      <CardContent>
        <div className="flex flex-wrap gap-4">
          {components.map((comp, idx) => (
            <div key={idx} className="flex items-center space-x-2 border rounded-md px-3 py-2 bg-secondary/50">
              <span className="text-sm font-medium">{comp.name}</span>
              <Badge variant={getVariant(comp.status) as any}>{comp.status}</Badge>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
