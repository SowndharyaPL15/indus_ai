import { useState } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { useDecisionDetails } from '@/hooks/useDecisionDetails';
import { ErrorState } from '@/components/ui/ErrorState';
import { Skeleton } from '@/components/ui/Skeleton';
import { Button } from '@/components/ui/Button';
import { ArrowLeft, Brain } from 'lucide-react';

import { DetailsOverviewCard } from '@/components/decision/DetailsOverviewCard';
import { ConfidenceCard } from '@/components/decision/ConfidenceCard';
import { ConflictsCard } from '@/components/decision/ConflictsCard';
import { EvidenceGraphCard } from '@/components/decision/EvidenceGraphCard';
import { ReportActionsCard } from '@/components/decision/ReportActionsCard';
import { ExplainabilityPanel } from '@/components/xai/ExplainabilityPanel';

export default function DecisionDetails() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const { caseDetails, confidence, conflicts, graph, isLoading, isError, generateReport, downloadReport } = useDecisionDetails(id || '');
  const [isXAIOpen, setIsXAIOpen] = useState(false);

  if (isError) {
    return <ErrorState message="Failed to load decision details. The analysis engine may be offline." />;
  }

  return (
    <div className="space-y-6 pb-10">
      <div className="flex items-center justify-between mb-4">
        <Button variant="ghost" size="sm" onClick={() => navigate('/cases')} className="p-0 hover:bg-transparent">
          <ArrowLeft className="h-5 w-5 mr-1" /> Back to Cases
        </Button>
        {!isLoading && (
          <Button variant="outline" onClick={() => setIsXAIOpen(true)}>
            <Brain className="mr-2 h-4 w-4" />
            Explain AI Decision
          </Button>
        )}
      </div>
      
      <div>
        <h1 className="text-2xl font-bold tracking-tight">Case: {id?.split('-')[0].toUpperCase()}</h1>
        <p className="text-muted-foreground">Comprehensive overview of AI analysis, conflicts, and evidence.</p>
      </div>

      {isLoading ? (
        <div className="grid gap-6 md:grid-cols-2">
           <Skeleton className="h-[250px] w-full" />
           <Skeleton className="h-[250px] w-full" />
           <Skeleton className="col-span-full h-[400px] w-full" />
        </div>
      ) : (
        <div className="grid gap-6 md:grid-cols-2">
          {/* Top Row */}
          <DetailsOverviewCard caseDetails={caseDetails} />
          <ConfidenceCard confidence={confidence} />
          
          {/* Middle Row */}
          <ConflictsCard conflicts={conflicts} />
          <ReportActionsCard caseId={id || ''} generateReport={generateReport} downloadReport={downloadReport} />
          
          {/* Bottom Row (Full Width) */}
          <EvidenceGraphCard graph={graph} />
        </div>
      )}

      {/* XAI Panel — passes already-fetched data, no extra API calls */}
      <ExplainabilityPanel
        isOpen={isXAIOpen}
        onClose={() => setIsXAIOpen(false)}
        caseDetails={caseDetails}
        confidence={confidence}
        conflicts={conflicts}
        graph={graph}
      />
    </div>
  );
}
