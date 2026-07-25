import { useState, useRef, useEffect } from 'react';
import { Send, Trash2, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface Props {
  onSubmit: (query: string) => void;
  onClear: () => void;
  isLoading: boolean;
  hasHistory: boolean;
}

export function CopilotInput({ onSubmit, onClear, isLoading, hasHistory }: Props) {
  const [query, setQuery] = useState('');
  const textareaRef = useRef<HTMLTextAreaElement>(null);

  const handleSubmit = () => {
    if (!query.trim() || isLoading) return;
    onSubmit(query.trim());
    setQuery('');
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSubmit();
    }
  };

  const handleInput = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setQuery(e.target.value);
    // Auto-resize
    if (textareaRef.current) {
      textareaRef.current.style.height = 'auto';
      textareaRef.current.style.height = `${Math.min(textareaRef.current.scrollHeight, 150)}px`;
    }
  };

  // Focus input on mount
  useEffect(() => {
    if (textareaRef.current) {
      textareaRef.current.focus();
    }
  }, []);

  return (
    <div className="bg-background border-t p-4 pb-8 sm:pb-4 shadow-[0_-4px_10px_-10px_rgba(0,0,0,0.1)]">
      <div className="max-w-4xl mx-auto flex items-end space-x-2">
        {hasHistory && (
          <Button 
            variant="ghost" 
            size="icon" 
            onClick={onClear} 
            title="Clear Conversation"
            className="mb-1 flex-shrink-0 text-muted-foreground hover:text-destructive"
          >
            <Trash2 className="h-5 w-5" />
          </Button>
        )}
        
        <div className="relative flex-1 bg-card border rounded-lg shadow-sm focus-within:ring-2 focus-within:ring-primary focus-within:border-transparent transition-all">
          <textarea
            ref={textareaRef}
            value={query}
            onChange={handleInput}
            onKeyDown={handleKeyDown}
            placeholder="Ask a question about maintenance, standard operating procedures, or historical incidents..."
            className="w-full bg-transparent border-0 resize-none py-3 pl-4 pr-12 focus:ring-0 text-sm max-h-[150px] min-h-[48px]"
            rows={1}
            disabled={isLoading}
          />
          <button
            onClick={handleSubmit}
            disabled={!query.trim() || isLoading}
            className="absolute right-2 bottom-2 p-1.5 rounded-md bg-primary text-primary-foreground disabled:opacity-50 disabled:cursor-not-allowed hover:bg-primary/90 transition-colors"
          >
            {isLoading ? <Loader2 className="h-4 w-4 animate-spin" /> : <Send className="h-4 w-4" />}
          </button>
        </div>
      </div>
      <div className="max-w-4xl mx-auto text-center mt-2">
        <p className="text-xs text-muted-foreground">
          INDUS AI Knowledge Copilot uses RAG to fetch contextual documents. It can make mistakes. Verify critical actions in the Decision Intelligence Center.
        </p>
      </div>
    </div>
  );
}
