from pydantic import BaseModel
from typing import List, Optional, Dict, Any
from app.schemas.copilot import Citation

class InvestigateRequest(BaseModel):
    query: str

class IntentResult(BaseModel):
    intent: str
    confidence: float

class DecisionCaseResponse(BaseModel):
    case_id: str
    title: str
    intent: str
    summary: str
    recommendation: str
    confidence: float
    documents_used: List[str]
    citations: List[Citation]
    processing_time: str

# ── IDIE v2 Enriched Models ───────────────────────────────────────────────────

class FactoryMemoryResponseItem(BaseModel):
    id: str
    decision_case_id: str
    problem: str
    solution: str
    lesson: str
    rating: int
    useful: bool

class SimilarCaseResponseItem(BaseModel):
    id: str
    decision_case_id: str
    case_title: str
    problem_summary: str
    final_recommendation: str
    outcome_status: str
    reusable_lesson: Optional[str] = None
    similarity_score: float

class GraphContextResponseItem(BaseModel):
    entity_id: str
    entity_type: str
    relationship_type: str
    direction: str
    depth: int
    properties: Optional[Dict[str, Any]] = None

class FusionDecisionResponse(BaseModel):
    case_id: str
    intent: str
    decision_summary: str
    recommended_action: str
    root_cause: str
    supporting_documents: List[str]
    factory_memory: List[FactoryMemoryResponseItem]
    similar_cases: List[SimilarCaseResponseItem]
    graph_context: List[GraphContextResponseItem]
    processing_time: str
    fused_confidence: float
    module_timings: Dict[str, str]
    requires_human_approval: bool = False
    approval_status: Optional[str] = None
    recommended_reviewer: Optional[str] = None
