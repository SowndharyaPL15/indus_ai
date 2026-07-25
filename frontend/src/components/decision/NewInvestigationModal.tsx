import { useState } from 'react';
import { X, Loader2 } from 'lucide-react';
import { Button } from '@/components/ui/Button';

interface ModalProps {
  isOpen: boolean;
  onClose: () => void;
  onSubmit: (payload: { query: string; machine_id?: string; execution_context?: string }) => void;
  isLoading: boolean;
}

export function NewInvestigationModal({ isOpen, onClose, onSubmit, isLoading }: ModalProps) {
  const [query, setQuery] = useState('');
  const [machine, setMachine] = useState('');
  const [context, setContext] = useState('');

  if (!isOpen) return null;

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!query.trim()) return;
    onSubmit({ query, machine_id: machine, execution_context: context });
  };

  return (
    <div className="fixed inset-0 z-50 flex items-center justify-center bg-background/80 backdrop-blur-sm">
      <div className="w-full max-w-lg rounded-lg border bg-card p-6 shadow-lg relative">
        <button onClick={onClose} className="absolute top-4 right-4 text-muted-foreground hover:text-foreground">
          <X className="h-5 w-5" />
        </button>
        <h2 className="text-xl font-semibold mb-4">New Investigation</h2>
        <form onSubmit={handleSubmit} className="space-y-4">
          <div>
            <label className="block text-sm font-medium mb-1">Query (Required)</label>
            <textarea
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary min-h-[100px]"
              placeholder="Describe the issue or objective..."
              value={query}
              onChange={(e) => setQuery(e.target.value)}
              required
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Machine ID (Optional)</label>
            <input
              type="text"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="e.g. CNC-Milling-04"
              value={machine}
              onChange={(e) => setMachine(e.target.value)}
            />
          </div>
          <div>
            <label className="block text-sm font-medium mb-1">Context (Optional)</label>
            <input
              type="text"
              className="w-full rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
              placeholder="Additional operational context"
              value={context}
              onChange={(e) => setContext(e.target.value)}
            />
          </div>
          <div className="flex justify-end space-x-2 pt-4">
            <Button type="button" variant="outline" onClick={onClose} disabled={isLoading}>
              Cancel
            </Button>
            <Button type="submit" disabled={isLoading || !query.trim()}>
              {isLoading ? <Loader2 className="mr-2 h-4 w-4 animate-spin" /> : null}
              Start Investigation
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
}
