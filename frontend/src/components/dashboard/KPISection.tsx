import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/Card';
import { Skeleton } from '@/components/ui/Skeleton';
import { FileText, ClipboardCheck, Clock, CheckCircle2, Brain, Network, Share2, FileBarChart } from 'lucide-react';

interface KPIProps {
  data: any;
  isLoading: boolean;
}

export function KPISection({ data, isLoading }: KPIProps) {
  if (isLoading) {
    return (
      <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 animate-in fade-in duration-500">
        {Array.from({ length: 8 }).map((_, i) => (
          <Card key={i} className="shadow-sm border-border">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <Skeleton className="h-4 w-[100px]" />
              <Skeleton className="h-4 w-4 rounded-full" />
            </CardHeader>
            <CardContent>
              <Skeleton className="h-8 w-[60px] mb-2" />
              <Skeleton className="h-3 w-[140px]" />
            </CardContent>
          </Card>
        ))}
      </div>
    );
  }

  const kpis = [
    { title: "Total Documents", value: data?.total_documents || 0, desc: "Indexed industrial references", icon: FileText, color: "text-blue-500" },
    { title: "Decision Cases", value: data?.total_decision_cases || 0, desc: "Industrial investigations completed", icon: ClipboardCheck, color: "text-indigo-500" },
    { title: "Active Cases", value: data?.active_cases || 0, desc: "Investigations in progress", icon: Clock, color: "text-orange-500" },
    { title: "Closed Cases", value: data?.closed_cases || 0, desc: "Resolved and archived", icon: CheckCircle2, color: "text-green-500" },
    { title: "Factory Memories", value: data?.factory_memories || 0, desc: "Validated engineering knowledge", icon: Brain, color: "text-purple-500" },
    { title: "Reasoning Cases", value: data?.reasoning_cases || 0, desc: "Reusable solved cases", icon: Share2, color: "text-pink-500" },
    { title: "Knowledge Graph Nodes", value: data?.knowledge_graph_nodes || 0, desc: "Connected industrial entities", icon: Network, color: "text-teal-500" },
    { title: "Reports Generated", value: data?.generated_reports || 0, desc: "Automated compliance reports", icon: FileBarChart, color: "text-rose-500" },
  ];

  return (
    <div className="grid gap-4 md:grid-cols-2 lg:grid-cols-4 xl:grid-cols-4 animate-in fade-in slide-in-from-bottom-4 duration-700">
      {kpis.map((kpi, idx) => {
        const Icon = kpi.icon;
        return (
          <Card key={idx} className="shadow-sm hover:shadow-md transition-shadow duration-200 border-border bg-card">
            <CardHeader className="flex flex-row items-center justify-between space-y-0 pb-2">
              <CardTitle className="text-sm font-semibold text-muted-foreground">{kpi.title}</CardTitle>
              <Icon className={`h-4 w-4 ${kpi.color} opacity-75`} />
            </CardHeader>
            <CardContent>
              <div className="text-2xl font-bold tracking-tight text-foreground mb-1">{kpi.value.toLocaleString()}</div>
              <p className="text-xs text-muted-foreground">{kpi.desc}</p>
            </CardContent>
          </Card>
        );
      })}
    </div>
  );
}
