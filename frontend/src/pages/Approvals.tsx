import { useState } from 'react';
import { useApprovals } from '@/hooks/useApprovals';
import { EmptyState } from '@/components/ui/EmptyState';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import { Badge } from '@/components/ui/Badge';
import { Button } from '@/components/ui/Button';
import { Table, TableHeader, TableRow, TableHead, TableBody, TableCell } from '@/components/ui/Table';
import { ConfirmationModal } from '@/components/ui/ConfirmationModal';
import { CheckCircle2, XCircle, ArrowUpCircle, RefreshCw } from 'lucide-react';

type ModalAction = 'approve' | 'reject' | 'escalate' | null;

export default function Approvals() {
  const { approvals, isLoading, isError, refetch, approve, reject, escalate } = useApprovals();
  const [modalAction, setModalAction] = useState<ModalAction>(null);
  const [selectedId, setSelectedId] = useState<string>('');

  const openModal = (action: ModalAction, id: string) => {
    setModalAction(action);
    setSelectedId(id);
  };

  const handleConfirm = (value: string) => {
    if (modalAction === 'approve') approve.mutate({ id: selectedId, comments: value }, { onSuccess: () => setModalAction(null) });
    if (modalAction === 'reject') reject.mutate({ id: selectedId, reason: value }, { onSuccess: () => setModalAction(null) });
    if (modalAction === 'escalate') escalate.mutate({ id: selectedId, reason: value }, { onSuccess: () => setModalAction(null) });
  };

  if (isError) return <ErrorState message="Unable to load approval queue." onRetry={refetch} />;

  const modalConfig = {
    approve: { title: 'Approve Request', description: 'This action will approve the AI recommendation for execution.', inputLabel: 'Comments', inputPlaceholder: 'Add approval comments...', confirmText: 'Approve', variant: 'default' as const },
    reject: { title: 'Reject Request', description: 'This action will reject the AI recommendation.', inputLabel: 'Rejection Reason', inputPlaceholder: 'Explain why this was rejected...', confirmText: 'Reject', variant: 'destructive' as const },
    escalate: { title: 'Escalate Request', description: 'This action will escalate the request to a senior authority.', inputLabel: 'Escalation Reason', inputPlaceholder: 'Explain the escalation reason...', confirmText: 'Escalate', variant: 'default' as const },
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Human Approval Center</h1>
          <p className="text-muted-foreground">Review and action AI-generated recommendations requiring human oversight.</p>
        </div>
        <Button variant="outline" onClick={() => refetch()}>
          <RefreshCw className="mr-2 h-4 w-4" /> Refresh
        </Button>
      </div>

      <div className="bg-card border rounded-lg overflow-hidden shadow-sm">
        {isLoading ? (
          <div className="p-6 space-y-4">
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
            <Skeleton className="h-10 w-full" />
          </div>
        ) : approvals.length === 0 ? (
          <div className="p-12">
            <EmptyState title="No approval requests pending" description="All industrial decision recommendations have been reviewed. Check back later." />
          </div>
        ) : (
          <Table>
            <TableHeader>
              <TableRow>
                <TableHead>Case ID</TableHead>
                <TableHead>Reason</TableHead>
                <TableHead>Risk Level</TableHead>
                <TableHead>Role</TableHead>
                <TableHead>Status</TableHead>
                <TableHead className="text-right">Actions</TableHead>
              </TableRow>
            </TableHeader>
            <TableBody>
              {approvals.map((a: any) => (
                <TableRow key={a.id}>
                  <TableCell className="font-medium font-mono text-xs">{a.decision_case_id?.split('-')[0] || 'N/A'}</TableCell>
                  <TableCell className="max-w-[200px] truncate text-sm" title={a.reason}>{a.reason || 'Pending Review'}</TableCell>
                  <TableCell>
                    <Badge variant={a.risk_level?.toUpperCase() === 'CRITICAL' ? 'destructive' : a.risk_level?.toUpperCase() === 'HIGH' ? 'warning' : 'secondary'}>
                      {a.risk_level || 'MEDIUM'}
                    </Badge>
                  </TableCell>
                  <TableCell className="text-sm">{a.approver_role || 'Supervisor'}</TableCell>
                  <TableCell><Badge variant="warning">{a.status || 'PENDING'}</Badge></TableCell>
                  <TableCell className="text-right space-x-1">
                    <Button variant="ghost" size="sm" className="text-green-600 hover:text-green-700" onClick={() => openModal('approve', a.id)}>
                      <CheckCircle2 className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="text-destructive hover:text-destructive" onClick={() => openModal('reject', a.id)}>
                      <XCircle className="h-4 w-4" />
                    </Button>
                    <Button variant="ghost" size="sm" className="text-yellow-600 hover:text-yellow-700" onClick={() => openModal('escalate', a.id)}>
                      <ArrowUpCircle className="h-4 w-4" />
                    </Button>
                  </TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        )}
      </div>

      {modalAction && (
        <ConfirmationModal
          isOpen={true}
          onClose={() => setModalAction(null)}
          onConfirm={handleConfirm}
          isLoading={approve.isPending || reject.isPending || escalate.isPending}
          {...modalConfig[modalAction]}
        />
      )}
    </div>
  );
}
