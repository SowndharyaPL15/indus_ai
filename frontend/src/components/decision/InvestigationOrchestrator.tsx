import { useState, useEffect } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { CheckCircle2, Loader2 } from 'lucide-react';

const PIPELINE_STAGES = [
  { id: 'retrieve',    icon: '🔍', label: 'Retrieving Documents',       description: 'Scanning FAISS vector store for relevant SOPs, manuals, and reports...' },
  { id: 'memory',      icon: '🧠', label: 'Searching Factory Memory',   description: 'Querying living factory memory for validated operational knowledge...' },
  { id: 'reasoning',   icon: '📚', label: 'Searching Reasoning Memory', description: 'Matching against historical decision cases for similar patterns...' },
  { id: 'graph',       icon: '🕸️', label: 'Building Knowledge Graph',   description: 'Constructing entity relationships across machines, SOPs, and incidents...' },
  { id: 'confidence',  icon: '📊', label: 'Calculating Confidence',     description: 'Aggregating evidence quality scores from all intelligence sources...' },
  { id: 'conflicts',   icon: '⚠️', label: 'Detecting Conflicts',        description: 'Cross-referencing recommendations against compliance and safety rules...' },
  { id: 'synthesize',  icon: '🤖', label: 'Synthesizing Decision',      description: 'Fusing multi-source evidence into a unified industrial recommendation...' },
  { id: 'create',      icon: '📄', label: 'Creating Decision Case',     description: 'Persisting the decision case with full audit trail and evidence chain...' },
  { id: 'complete',    icon: '✓',  label: 'Investigation Complete',     description: 'All engines have reported. Decision case is ready for review.' },
];

interface Props {
  isActive: boolean;
  isBackendComplete: boolean;
  query: string;
}

export function InvestigationOrchestrator({ isActive, isBackendComplete, query }: Props) {
  const [currentStage, setCurrentStage] = useState(0);
  const [completedStages, setCompletedStages] = useState<number[]>([]);

  // Advance stages on a timer (300-600ms each)
  useEffect(() => {
    if (!isActive) {
      setCurrentStage(0);
      setCompletedStages([]);
      return;
    }

    const totalStages = PIPELINE_STAGES.length;

    if (currentStage >= totalStages) return;

    // If backend is done, rush remaining stages at 200ms
    // If backend is still working, pace at 400-600ms
    const delay = isBackendComplete
      ? 200
      : 400 + Math.random() * 200;

    const timer = setTimeout(() => {
      setCompletedStages(prev => [...prev, currentStage]);
      setCurrentStage(prev => prev + 1);
    }, delay);

    return () => clearTimeout(timer);
  }, [isActive, currentStage, isBackendComplete]);

  if (!isActive) return null;

  const allDone = completedStages.length >= PIPELINE_STAGES.length;

  return (
    <div className="fixed inset-0 z-[60] flex items-center justify-center bg-background/95">
      <div className="w-full max-w-2xl mx-auto px-6">
        {/* Header */}
        <div className="text-center mb-10">
          <motion.h2
            initial={{ opacity: 0, y: -10 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-2xl font-bold tracking-tight"
          >
            IDIE Orchestration Engine
          </motion.h2>
          <motion.p
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            transition={{ delay: 0.2 }}
            className="text-sm text-muted-foreground mt-2 font-mono"
          >
            Investigating: "{query}"
          </motion.p>
        </div>

        {/* Pipeline stages */}
        <div className="space-y-1">
          {PIPELINE_STAGES.map((stage, idx) => {
            const isCompleted = completedStages.includes(idx);
            const isCurrent = currentStage === idx && !isCompleted;
            const isPending = idx > currentStage;

            return (
              <motion.div
                key={stage.id}
                initial={{ opacity: 0, x: -20 }}
                animate={{ opacity: isPending ? 0.35 : 1, x: 0 }}
                transition={{ delay: idx * 0.05, duration: 0.3 }}
                className={`
                  flex items-center gap-4 px-4 py-3 rounded-lg border transition-colors duration-300
                  ${isCurrent ? 'bg-primary/5 border-primary/30' : ''}
                  ${isCompleted ? 'bg-card border-border' : ''}
                  ${isPending ? 'bg-transparent border-transparent' : ''}
                `}
              >
                {/* Status indicator */}
                <div className="flex-shrink-0 w-8 h-8 flex items-center justify-center">
                  <AnimatePresence mode="wait">
                    {isCompleted ? (
                      <motion.div
                        key="done"
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        transition={{ type: 'spring', stiffness: 400, damping: 15 }}
                      >
                        <CheckCircle2 className="h-5 w-5 text-green-600" />
                      </motion.div>
                    ) : isCurrent ? (
                      <motion.div
                        key="active"
                        initial={{ scale: 0.8 }}
                        animate={{ scale: 1 }}
                      >
                        <Loader2 className="h-5 w-5 animate-spin text-primary" />
                      </motion.div>
                    ) : (
                      <span className="text-lg opacity-40">{stage.icon}</span>
                    )}
                  </AnimatePresence>
                </div>

                {/* Label + description */}
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span className={`text-sm font-medium ${isCompleted ? 'text-foreground' : isCurrent ? 'text-primary' : 'text-muted-foreground'}`}>
                      {stage.label}
                    </span>
                    {isCompleted && (
                      <motion.span
                        initial={{ opacity: 0, width: 0 }}
                        animate={{ opacity: 1, width: 'auto' }}
                        className="text-[10px] font-mono text-green-600 uppercase tracking-wider"
                      >
                        DONE
                      </motion.span>
                    )}
                  </div>
                  {isCurrent && (
                    <motion.p
                      initial={{ opacity: 0, height: 0 }}
                      animate={{ opacity: 1, height: 'auto' }}
                      className="text-xs text-muted-foreground mt-0.5"
                    >
                      {stage.description}
                    </motion.p>
                  )}
                </div>

                {/* Timing indicator */}
                <div className="flex-shrink-0 w-12 text-right">
                  {isCompleted && (
                    <motion.span
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="text-[10px] font-mono text-muted-foreground"
                    >
                      {(300 + Math.floor(Math.random() * 300))}ms
                    </motion.span>
                  )}
                </div>
              </motion.div>
            );
          })}
        </div>

        {/* Bottom status bar */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.5 }}
          className="mt-8 flex items-center justify-between px-4"
        >
          <div className="flex items-center gap-2">
            <div className={`h-2 w-2 rounded-full ${allDone ? 'bg-green-500' : 'bg-primary animate-pulse'}`} />
            <span className="text-xs font-mono text-muted-foreground">
              {allDone ? 'ALL ENGINES REPORTED' : `ENGINE ${Math.min(currentStage + 1, PIPELINE_STAGES.length)}/${PIPELINE_STAGES.length}`}
            </span>
          </div>
          <div className="h-1.5 flex-1 mx-6 bg-secondary rounded-full overflow-hidden">
            <motion.div
              className="h-full bg-primary rounded-full"
              initial={{ width: '0%' }}
              animate={{ width: `${(completedStages.length / PIPELINE_STAGES.length) * 100}%` }}
              transition={{ duration: 0.3 }}
            />
          </div>
          <span className="text-xs font-mono text-muted-foreground">
            {Math.round((completedStages.length / PIPELINE_STAGES.length) * 100)}%
          </span>
        </motion.div>
      </div>
    </div>
  );
}
