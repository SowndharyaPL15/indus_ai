import React, { Suspense } from 'react';
import { useDashboardData } from '@/hooks/useDashboardData';
import { ErrorState } from '@/components/ui/ErrorState';
import { Button } from '@/components/ui/Button';
import { FileUp, Plus, FileText } from 'lucide-react';
import { useNavigate } from 'react-router-dom';
import { KPISection } from '@/components/dashboard/KPISection';
import { KnowledgeAnalyticsSection } from '@/components/dashboard/KnowledgeAnalyticsSection';
import { ComplianceConflictsSection } from '@/components/dashboard/ComplianceConflictsSection';
import { SystemHealthSection } from '@/components/dashboard/SystemHealthSection';

// Lazy load the heavy chart components
const DecisionIntelligenceSection = React.lazy(() => 
  import('@/components/dashboard/DecisionIntelligenceSection').then(m => ({ default: m.DecisionIntelligenceSection }))
);

export default function Dashboard() {
  const navigate = useNavigate();
  const { summary, intelligence, knowledge, compliance, conflicts, health, isLoading, isError, refetchAll } = useDashboardData();

  if (isError) {
    return <ErrorState message="Unable to fetch dashboard metrics. Please ensure the backend is running." onRetry={refetchAll} />;
  }

  return (
    <div className="space-y-6 pb-10">
      <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold tracking-tight">Executive Dashboard</h1>
          <p className="text-muted-foreground">Overview of system operations and intelligence metrics.</p>
        </div>
        
        <div className="flex items-center gap-2">
          <Button variant="outline" size="sm" className="hidden sm:flex" onClick={() => navigate('/documents/upload')}>
            <FileUp className="mr-2 h-4 w-4" />
            Upload Document
          </Button>
          <Button variant="outline" size="sm" className="hidden sm:flex" onClick={() => navigate('/cases')}>
            <Plus className="mr-2 h-4 w-4" />
            Create Investigation
          </Button>
          <Button size="sm" onClick={() => navigate('/reports')}>
            <FileText className="mr-2 h-4 w-4" />
            Generate Report
          </Button>
        </div>
      </div>
      
      <div className="space-y-6">
        {/* Row 1: 8 KPIs */}
        <KPISection data={summary} isLoading={isLoading} />
        
        {/* Row 2: Decision Intelligence (Recharts) */}
        <Suspense fallback={<div className="h-[350px] bg-muted animate-pulse rounded-lg" />}>
          <DecisionIntelligenceSection data={intelligence} isLoading={isLoading} />
        </Suspense>

        {/* Row 3: Knowledge Analytics */}
        <KnowledgeAnalyticsSection data={knowledge} isLoading={isLoading} />
        
        {/* Row 4: Compliance & Conflicts */}
        <ComplianceConflictsSection complianceData={compliance} conflictsData={conflicts} isLoading={isLoading} />
        
        {/* Row 5: System Health */}
        <SystemHealthSection data={health} isLoading={isLoading} />
      </div>
    </div>
  );
}
