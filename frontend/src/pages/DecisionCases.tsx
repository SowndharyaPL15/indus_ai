import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import { useDecisionCases } from '@/hooks/useDecisionCases';
import { EmptyState } from '@/components/ui/EmptyState';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { Search, Plus } from 'lucide-react';
import { NewInvestigationModal } from '@/components/decision/NewInvestigationModal';
import { InvestigationOrchestrator } from '@/components/decision/InvestigationOrchestrator';
import { Skeleton } from '@/components/ui/Skeleton';

export default function DecisionCases() {
  const navigate = useNavigate();
  const { cases, isLoading, createInvestigation } = useDecisionCases();
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [orchestratorActive, setOrchestratorActive] = useState(false);
  const [orchestratorQuery, setOrchestratorQuery] = useState('');
  const [backendComplete, setBackendComplete] = useState(false);
  const [pendingCaseId, setPendingCaseId] = useState<string | null>(null);

  const handleNewInvestigation = (payload: any) => {
    setIsModalOpen(false);
    setOrchestratorQuery(payload.query);
    setOrchestratorActive(true);
    setBackendComplete(false);
    setPendingCaseId(null);

    createInvestigation.mutate(payload, {
      onSuccess: (data) => {
        // Signal backend is done — orchestrator will rush remaining stages
        setBackendComplete(true);
        if (data.case_id) {
          setPendingCaseId(data.case_id);
        }
      },
      onError: () => {
        // On error, still let animation finish then close
        setBackendComplete(true);
      }
    });
  };

  // Called when orchestrator animation finishes (all 9 stages done)
  // We use a useEffect inside the orchestrator, but the simplest approach
  // is to check periodically. Instead, let's use a timeout after backendComplete.
  // Actually, we navigate when the user sees "Investigation Complete" for a beat.
  // The orchestrator runs ~4s total. We navigate after that.
  // Let's use a simple approach: when backendComplete + orchestrator has had enough time.

  // Watch for completion
  if (backendComplete && pendingCaseId && orchestratorActive) {
    // The orchestrator will rush through remaining stages since backendComplete=true
    // After ~2s from backend completing, navigate away
    setTimeout(() => {
      setOrchestratorActive(false);
      navigate(`/cases/${pendingCaseId}`);
    }, 3000);
  }

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Decision Intelligence Center</h1>
          <p className="text-muted-foreground">Manage and track AI-driven investigations.</p>
        </div>
        <Button onClick={() => setIsModalOpen(true)}>
          <Plus className="mr-2 h-4 w-4" />
          New Investigation
        </Button>
      </div>
      
      {/* Search & Filters */}
      <div className="flex flex-col md:flex-row gap-4 items-center bg-card p-4 rounded-lg border shadow-sm">
        <div className="relative flex-1 w-full">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 h-4 w-4 text-muted-foreground" />
          <input 
            type="text" 
            placeholder="Search cases..." 
            className="w-full rounded-md border bg-background pl-9 pr-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary"
          />
        </div>
        <div className="flex gap-2 w-full md:w-auto overflow-x-auto">
          <select className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
            <option>All Intents</option>
            <option>Safety</option>
            <option>Maintenance</option>
          </select>
          <select className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
            <option>All Statuses</option>
            <option>Open</option>
            <option>Closed</option>
          </select>
          <select className="rounded-md border bg-background px-3 py-2 text-sm focus:outline-none focus:ring-2 focus:ring-primary">
            <option>All Priorities</option>
            <option>High</option>
            <option>Medium</option>
          </select>
        </div>
      </div>

      {/* Data Table */}
      <div className="bg-card border rounded-lg overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : cases.length === 0 ? (
          <div className="p-12">
            <EmptyState 
              title="No historical maintenance cases found" 
              description="Start a new investigation to log a decision case." 
            />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Case ID</TableHead>
                <TableHead>Title</TableHead>
                <TableHead>Intent</TableHead>
                <TableHead>Priority</TableHead>
                <TableHead>Confidence</TableHead>
                <TableHead>Status</TableHead>
                <TableHead>Created At</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {cases.map((c: any) => (
                <TableRow key={c.id}>
                  {/* Map properties here when API is ready */}
                  <TableCell colSpan={8}>Placeholder Data</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      <NewInvestigationModal 
        isOpen={isModalOpen} 
        onClose={() => setIsModalOpen(false)} 
        onSubmit={handleNewInvestigation}
        isLoading={createInvestigation.isPending}
      />

      {/* Orchestration Animation Overlay */}
      <InvestigationOrchestrator
        isActive={orchestratorActive}
        isBackendComplete={backendComplete}
        query={orchestratorQuery}
      />
    </div>
  )
}
