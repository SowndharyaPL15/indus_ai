import { CheckCircle2 } from 'lucide-react';

const REASONING_STAGES = [
  { id: 'query', label: 'User Query', description: 'Original question submitted by the operator.' },
  { id: 'intent', label: 'Intent Detection', description: 'Classified query intent (Maintenance, Safety, Compliance).' },
  { id: 'doc_retrieval', label: 'Document Retrieval', description: 'RAG engine queried FAISS for relevant document chunks.' },
  { id: 'kg_lookup', label: 'Knowledge Graph Lookup', description: 'Traversed knowledge graph for relational context.' },
  { id: 'factory_mem', label: 'Factory Memory Search', description: 'Searched living factory memory for institutional lessons.' },
  { id: 'reasoning_mem', label: 'Reasoning Memory Search', description: 'Matched similar historical decision cases.' },
  { id: 'fusion', label: 'Evidence Fusion', description: 'IDIE v2 fused all evidence sources into a unified analysis.' },
  { id: 'confidence', label: 'Confidence Calculation', description: 'Weighted multi-factor confidence score computed.' },
  { id: 'conflict', label: 'Conflict Detection', description: 'Cross-referenced sources for contradictions and risks.' },
  { id: 'recommendation', label: 'Recommendation Generated', description: 'Final actionable recommendation produced.' },
];

export function ReasoningFlow() {
  return (
    <div className="space-y-0 pt-3">
      {REASONING_STAGES.map((stage, index) => {
        const isLast = index === REASONING_STAGES.length - 1;
        return (
          <div key={stage.id} className="relative flex items-start group">
            {/* Vertical connector */}
            {!isLast && (
              <div className="absolute left-[11px] top-7 h-full w-0.5 bg-primary/30" />
            )}
            
            {/* Node */}
            <div className="relative z-10 flex h-6 w-6 flex-shrink-0 items-center justify-center mt-0.5">
              <CheckCircle2 className="h-5 w-5 text-primary" />
            </div>

            {/* Content */}
            <div className="ml-4 pb-6">
              <p className="text-sm font-semibold text-foreground">{stage.label}</p>
              <p className="text-xs text-muted-foreground mt-0.5">{stage.description}</p>
            </div>
          </div>
        );
      })}
    </div>
  );
}
