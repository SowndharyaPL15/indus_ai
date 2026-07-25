import { motion, AnimatePresence } from 'framer-motion';
import { X, Brain, BarChart3, FileSearch, AlertTriangle, Workflow, Activity, Lightbulb, FileText, Database, Network } from 'lucide-react';
import { CollapsibleSection } from '@/components/ui/CollapsibleSection';
import { Badge } from '@/components/ui/Badge';
import { ConfidenceBreakdown } from './ConfidenceBreakdown';
import { EvidenceTimeline } from './EvidenceTimeline';
import { ReasoningFlow } from './ReasoningFlow';

interface Props {
  isOpen: boolean;
  onClose: () => void;
  caseDetails: any;
  confidence: any;
  conflicts: any;
  graph: any;
}

export function ExplainabilityPanel({ isOpen, onClose, caseDetails, confidence, conflicts, graph }: Props) {
  if (!isOpen) return null;

  // Transparency metrics
  const docCount = graph?.edges?.filter((e: any) => e.relationship === "REFERENCES")?.length || 0;
  const nodeCount = graph?.nodes?.length || 0;
  const edgeCount = graph?.edges?.length || 0;
  const conflictCount = Array.isArray(conflicts) ? conflicts.length : 0;

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            className="fixed inset-0 z-40 bg-background/60 md:bg-transparent"
            onClick={onClose}
          />

          {/* Panel — right drawer on desktop, full screen on mobile */}
          <motion.div
            initial={{ x: "100%" }}
            animate={{ x: 0 }}
            exit={{ x: "100%" }}
            transition={{ type: "spring", damping: 30, stiffness: 300 }}
            className="fixed inset-y-0 right-0 z-50 w-full md:w-[480px] bg-background border-l shadow-2xl flex flex-col overflow-hidden"
          >
            {/* Header */}
            <div className="flex items-center justify-between p-4 border-b bg-card flex-shrink-0">
              <div className="flex items-center space-x-3">
                <div className="h-8 w-8 rounded-full bg-primary/10 flex items-center justify-center">
                  <Brain className="h-5 w-5 text-primary" />
                </div>
                <div>
                  <h2 className="text-lg font-bold tracking-tight">Explainable AI</h2>
                  <p className="text-xs text-muted-foreground">Transparency Report</p>
                </div>
              </div>
              <button onClick={onClose} className="p-2 rounded-md hover:bg-secondary text-muted-foreground">
                <X className="h-5 w-5" />
              </button>
            </div>

            {/* Scrollable Content */}
            <div className="flex-1 overflow-y-auto p-4 space-y-4">
              {/* Section 1: Decision Summary */}
              <CollapsibleSection title="Decision Summary" icon={<Lightbulb className="h-4 w-4" />}>
                <div className="grid grid-cols-2 gap-3 pt-3">
                  <div>
                    <p className="text-xs text-muted-foreground">Recommendation</p>
                    <p className="text-sm font-medium mt-0.5">Auto-shutdown and schedule Maintenance</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Intent</p>
                    <p className="text-sm font-medium mt-0.5">{caseDetails?.intent || 'INVESTIGATION'}</p>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Priority</p>
                    <Badge variant="warning">{caseDetails?.priority || 'HIGH'}</Badge>
                  </div>
                  <div>
                    <p className="text-xs text-muted-foreground">Status</p>
                    <Badge variant="secondary">{caseDetails?.status || 'OPEN'}</Badge>
                  </div>
                </div>
              </CollapsibleSection>

              {/* Section 2: Evidence Used */}
              <CollapsibleSection title="Evidence Used" icon={<FileSearch className="h-4 w-4" />}>
                <EvidenceTimeline graph={graph} />
              </CollapsibleSection>

              {/* Section 3: Confidence Breakdown */}
              <CollapsibleSection title="Confidence Breakdown" icon={<BarChart3 className="h-4 w-4" />}>
                <ConfidenceBreakdown confidence={confidence} />
              </CollapsibleSection>

              {/* Section 4: Conflict Analysis */}
              <CollapsibleSection title="Conflict Analysis" icon={<AlertTriangle className="h-4 w-4" />}>
                <div className="pt-3">
                  {conflictCount === 0 ? (
                    <div className="flex items-center space-x-2 border rounded-md p-3 bg-green-50 dark:bg-green-950 border-green-200 dark:border-green-800">
                      <div className="h-2 w-2 rounded-full bg-green-500" />
                      <p className="text-sm font-medium text-green-700 dark:text-green-300">No conflicts detected.</p>
                    </div>
                  ) : (
                    <div className="space-y-3">
                      {conflicts.map((c: any, idx: number) => (
                        <div key={idx} className="border rounded-md p-3 border-destructive/30 bg-destructive/5">
                          <div className="flex justify-between items-center mb-1">
                            <span className="text-sm font-semibold">{c.conflict_type}</span>
                            <Badge variant="destructive">{c.severity}</Badge>
                          </div>
                          <p className="text-xs text-muted-foreground">{c.description}</p>
                        </div>
                      ))}
                    </div>
                  )}
                </div>
              </CollapsibleSection>

              {/* Section 5: AI Reasoning Flow */}
              <CollapsibleSection title="AI Reasoning Flow" icon={<Workflow className="h-4 w-4" />} defaultOpen={false}>
                <ReasoningFlow />
              </CollapsibleSection>

              {/* Section 6: Transparency Metrics */}
              <CollapsibleSection title="Transparency Metrics" icon={<Activity className="h-4 w-4" />}>
                <div className="grid grid-cols-2 gap-3 pt-3">
                  {[
                    { label: "Documents Used", value: docCount, icon: <FileText className="h-4 w-4" /> },
                    { label: "Memories Used", value: edgeCount - docCount, icon: <Database className="h-4 w-4" /> },
                    { label: "Graph Nodes Traversed", value: nodeCount, icon: <Network className="h-4 w-4" /> },
                    { label: "Confidence Level", value: confidence?.score ? `${(confidence.score * 100).toFixed(0)}%` : 'N/A', icon: <BarChart3 className="h-4 w-4" /> },
                  ].map((metric, idx) => (
                    <div key={idx} className="flex items-center space-x-3 border rounded-md p-3 bg-secondary/30">
                      <span className="text-muted-foreground">{metric.icon}</span>
                      <div>
                        <p className="text-xs text-muted-foreground">{metric.label}</p>
                        <p className="text-sm font-bold">{metric.value}</p>
                      </div>
                    </div>
                  ))}
                </div>
              </CollapsibleSection>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}
