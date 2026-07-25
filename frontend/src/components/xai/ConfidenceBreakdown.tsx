import { cn } from '@/lib/utils';

interface Props {
  confidence: any;
}

interface BarProps {
  label: string;
  value: number; // 0-1
  color?: string;
}

function ProgressBar({ label, value, color = "bg-primary" }: BarProps) {
  const percentage = Math.round(value * 100);
  return (
    <div className="space-y-1">
      <div className="flex justify-between text-xs">
        <span className="font-medium text-muted-foreground">{label}</span>
        <span className={cn(
          "font-semibold",
          percentage >= 70 ? "text-green-600" : percentage >= 40 ? "text-yellow-600" : "text-destructive"
        )}>{percentage}%</span>
      </div>
      <div className="h-2 rounded-full bg-secondary overflow-hidden">
        <div
          className={cn("h-full rounded-full transition-all duration-700 ease-out", color)}
          style={{ width: `${percentage}%` }}
        />
      </div>
    </div>
  );
}

export function ConfidenceBreakdown({ confidence }: Props) {
  if (!confidence) {
    return <p className="text-sm text-muted-foreground pt-3">No confidence data available.</p>;
  }

  // Map confidence factors into progress bars
  const factors = confidence.factors || [];
  
  // Build a map of factor names to weights
  const factorMap: Record<string, number> = {};
  factors.forEach((f: any) => {
    factorMap[f.name] = f.weight || 0;
  });

  const bars = [
    { label: "Documents", value: factorMap["document_relevance"] || factorMap["Documents"] || 0 },
    { label: "Factory Memory", value: factorMap["factory_memory"] || factorMap["Factory Memory"] || 0 },
    { label: "Reasoning Memory", value: factorMap["reasoning_memory"] || factorMap["Reasoning Memory"] || 0 },
    { label: "Knowledge Graph", value: factorMap["knowledge_graph"] || factorMap["Knowledge Graph"] || 0 },
    { label: "Intent", value: factorMap["intent_confidence"] || factorMap["Intent"] || 0 },
  ];

  return (
    <div className="space-y-4 pt-3">
      {bars.map((bar, idx) => (
        <ProgressBar key={idx} label={bar.label} value={bar.value} />
      ))}
      
      {/* Overall Score — highlighted */}
      <div className="pt-3 border-t">
        <ProgressBar 
          label="Overall Confidence" 
          value={confidence.score || 0} 
          color="bg-primary"
        />
      </div>
    </div>
  );
}
