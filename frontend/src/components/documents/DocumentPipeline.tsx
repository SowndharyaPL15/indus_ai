import { CheckCircle2, Circle, Loader2, XCircle } from 'lucide-react';
import { cn } from '@/lib/utils';

interface PipelineProps {
  currentStatus: string;
}

const STAGES = [
  { id: 'UPLOADED', label: 'Uploaded' },
  { id: 'EXTRACTING', label: 'Extracting' },
  { id: 'CHUNKING', label: 'Chunking' },
  { id: 'EMBEDDING', label: 'Embedding' },
  { id: 'INDEXING', label: 'Indexing' },
  { id: 'READY', label: 'Ready' },
];

export function DocumentPipeline({ currentStatus }: PipelineProps) {
  // Normalize status mapping (since backend might return ERROR or FAILED)
  const isFailed = currentStatus === 'FAILED' || currentStatus === 'ERROR';
  
  // Find current stage index (if not found or failed, we handle gracefully)
  const currentIndex = STAGES.findIndex(s => s.id === currentStatus);

  return (
    <div className="flex flex-col space-y-6">
      {STAGES.map((stage, index) => {
        const isCompleted = currentIndex > index || currentStatus === 'READY';
        const isCurrent = currentStatus === stage.id && !isFailed;
        
        return (
          <div key={stage.id} className="relative flex items-center">
            {/* Connecting Line */}
            {index !== STAGES.length - 1 && (
              <div 
                className={cn(
                  "absolute left-3 top-8 h-10 w-0.5 -ml-px",
                  isCompleted ? "bg-primary" : "bg-border"
                )} 
              />
            )}
            
            {/* Icon */}
            <div className="relative z-10 flex h-6 w-6 items-center justify-center bg-background">
               {isCompleted ? (
                 <CheckCircle2 className="h-5 w-5 text-primary" />
               ) : isCurrent ? (
                 <Loader2 className="h-5 w-5 text-primary animate-spin" />
               ) : isFailed && index >= Math.max(0, currentIndex) ? (
                 <XCircle className="h-5 w-5 text-destructive" />
               ) : (
                 <Circle className="h-4 w-4 text-muted-foreground" />
               )}
            </div>

            {/* Label */}
            <div className="ml-4">
              <span className={cn(
                "text-sm font-medium",
                isCurrent ? "text-primary" : isCompleted ? "text-foreground" : "text-muted-foreground"
              )}>
                {stage.label}
              </span>
              {isCurrent && (
                <p className="text-xs text-muted-foreground mt-0.5 animate-pulse">Processing...</p>
              )}
            </div>
          </div>
        );
      })}
    </div>
  );
}
