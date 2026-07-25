from pydantic import BaseModel
from typing import List, Dict, Any

class ExecutiveSummaryResponse(BaseModel):
    total_documents: int
    total_decision_cases: int
    open_cases: int
    closed_cases: int
    critical_cases: int
    pending_approvals: int
    knowledge_items: int
    reasoning_cases: int
    compliance_score: float
    average_confidence: float

class KnowledgeGrowthMonth(BaseModel):
    month: str
    documents: int
    factory_memory: int
    reasoning_memory: int
    knowledge_graph_nodes: int
    decision_cases: int

class KnowledgeGrowthResponse(BaseModel):
    monthly_data: List[KnowledgeGrowthMonth]

class MachineIntelligenceResponse(BaseModel):
    top_10_machines: List[Dict[str, Any]]
    most_failures: List[Dict[str, Any]]
    most_incidents: List[Dict[str, Any]]
    most_maintenance: List[Dict[str, Any]]
    highest_risk: List[Dict[str, Any]]

class AIPerformanceResponse(BaseModel):
    average_processing_time: str
    average_confidence: float
    cases_solved: int
    approval_rate: float
    conflict_rate: float

class ComplianceDashboardResponse(BaseModel):
    compliance_percentage: float
    violations: int
    pending_audits: int
    high_risk_assets: int

class LiveActivityFeedResponse(BaseModel):
    latest_documents_uploaded: List[Dict[str, Any]]
    decision_cases: List[Dict[str, Any]]
    approvals: List[Dict[str, Any]]
    reports_generated: List[Dict[str, Any]]
    knowledge_added: List[Dict[str, Any]]
