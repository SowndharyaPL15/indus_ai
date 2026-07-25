import { useState, useRef, useEffect } from 'react';
import type { CopilotResponse } from '@/hooks/useCopilot';
import { useCopilot } from '@/hooks/useCopilot';
import { CopilotEmptyState } from '@/components/copilot/CopilotEmptyState';
import { CopilotResponsePanel } from '@/components/copilot/CopilotResponsePanel';
import { CopilotInput } from '@/components/copilot/CopilotInput';
import { ErrorState } from '@/components/ui/ErrorState';
import { Loader2 } from 'lucide-react';

interface ConversationTurn {
  id: string;
  query: string;
  response?: CopilotResponse;
  isError?: boolean;
}

export default function KnowledgeCopilot() {
  const { askCopilot } = useCopilot();
  const [history, setHistory] = useState<ConversationTurn[]>([]);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Auto-scroll to bottom when history changes
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTo({
        top: scrollRef.current.scrollHeight,
        behavior: 'smooth'
      });
    }
  }, [history, askCopilot.isPending]);

  const handleQuerySubmit = (query: string) => {
    const turnId = Date.now().toString();
    
    // Optimistically add to history
    setHistory(prev => [...prev, { id: turnId, query }]);

    askCopilot.mutate(query, {
      onSuccess: (data) => {
        setHistory(prev => prev.map(turn => 
          turn.id === turnId ? { ...turn, response: data } : turn
        ));
      },
      onError: () => {
        setHistory(prev => prev.map(turn => 
          turn.id === turnId ? { ...turn, isError: true } : turn
        ));
      }
    });
  };

  const handleClear = () => {
    if (confirm("Are you sure you want to clear the conversation history?")) {
      setHistory([]);
    }
  };

  const hasHistory = history.length > 0;

  return (
    <div className="flex flex-col h-[calc(100vh-4rem)] bg-background">
      {/* Scrollable Conversation Area */}
      <div 
        ref={scrollRef}
        className="flex-1 overflow-y-auto"
      >
        {!hasHistory ? (
          <CopilotEmptyState onSelect={handleQuerySubmit} />
        ) : (
          <div className="max-w-4xl mx-auto px-4 py-8 space-y-12">
            {history.map((turn) => (
              <div key={turn.id}>
                {turn.response ? (
                  <CopilotResponsePanel query={turn.query} response={turn.response} />
                ) : turn.isError ? (
                   <div className="space-y-4">
                     <h3 className="text-xl font-bold tracking-tight border-b pb-4">{turn.query}</h3>
                     <ErrorState 
                       message="The Copilot engine encountered an error generating the response." 
                       onRetry={() => handleQuerySubmit(turn.query)}
                     />
                   </div>
                ) : (
                   <div className="space-y-6">
                     <h3 className="text-xl font-bold tracking-tight border-b pb-4">{turn.query}</h3>
                     <div className="flex items-center space-x-3 text-muted-foreground">
                        <Loader2 className="h-5 w-5 animate-spin text-primary" />
                        <span className="text-sm font-medium">Scanning knowledge graph and documents...</span>
                     </div>
                   </div>
                )}
              </div>
            ))}
          </div>
        )}
      </div>

      {/* Input Area */}
      <CopilotInput 
        onSubmit={handleQuerySubmit} 
        onClear={handleClear}
        isLoading={askCopilot.isPending}
        hasHistory={hasHistory}
      />
    </div>
  );
}
