import { Card, CardContent } from '@/components/ui/Card';
import { Lightbulb, Database, Settings, Search } from 'lucide-react';

interface Props {
  onSelect: (query: string) => void;
}

const SUGGESTIONS = [
  {
    title: "Maintenance",
    query: "What is the maintenance procedure for Pump P101?",
    icon: Settings
  },
  {
    title: "Historical Analysis",
    query: "Show previous overheating incidents.",
    icon: Database
  },
  {
    title: "Compliance & Safety",
    query: "What SOP applies before restarting equipment?",
    icon: Search
  },
  {
    title: "Document Insights",
    query: "Summarize inspection findings from uploaded reports.",
    icon: Lightbulb
  }
];

export function CopilotEmptyState({ onSelect }: Props) {
  return (
    <div className="flex flex-col items-center justify-center h-full max-w-3xl mx-auto text-center px-4 py-12">
      <div className="bg-primary/10 p-4 rounded-full mb-6">
        <Lightbulb className="h-8 w-8 text-primary" />
      </div>
      <h2 className="text-2xl font-bold tracking-tight mb-2">Knowledge Copilot</h2>
      <p className="text-muted-foreground mb-10 max-w-lg">
        Ask complex questions about your industrial documentation, maintenance history, and standard operating procedures.
      </p>
      
      <div className="grid grid-cols-1 md:grid-cols-2 gap-4 w-full text-left">
        {SUGGESTIONS.map((s, idx) => (
          <Card 
            key={idx} 
            className="cursor-pointer hover:bg-secondary/50 transition-colors border-dashed"
            onClick={() => onSelect(s.query)}
          >
            <CardContent className="p-4 flex items-start space-x-3">
              <s.icon className="h-5 w-5 text-muted-foreground mt-0.5" />
              <div>
                <p className="font-medium text-sm text-foreground">{s.title}</p>
                <p className="text-sm text-muted-foreground mt-1">{s.query}</p>
              </div>
            </CardContent>
          </Card>
        ))}
      </div>
    </div>
  );
}
