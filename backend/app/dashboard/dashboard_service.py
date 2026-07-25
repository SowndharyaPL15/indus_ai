from sqlalchemy.ext.asyncio import AsyncSession
from app.dashboard.dashboard_repository import DashboardRepository
from app.dashboard.dashboard_models import (
    ExecutiveSummaryResponse,
    KnowledgeGrowthResponse,
    KnowledgeGrowthMonth,
    MachineIntelligenceResponse,
    AIPerformanceResponse,
    ComplianceDashboardResponse,
    LiveActivityFeedResponse
)

class DashboardService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = DashboardRepository(db)

    async def get_executive_summary(self) -> ExecutiveSummaryResponse:
        total_docs = await self.repo.count_documents()
        total_cases = await self.repo.count_decision_cases()
        status_counts = await self.repo.count_decision_cases_by_status()
        
        open_cases = sum(v for k, v in status_counts.items() if k not in ("RESOLVED", "CLOSED", "KNOWLEDGE_CAPTURED"))
        closed_cases = sum(v for k, v in status_counts.items() if k in ("RESOLVED", "CLOSED", "KNOWLEDGE_CAPTURED"))
        
        # Mocking critical cases
        critical_cases = 5
        
        approval_counts = await self.repo.count_approvals_by_status()
        pending_approvals = approval_counts.get("PENDING", 0)
        
        factory_mems = await self.repo.count_factory_memories()
        reasoning_cases = await self.repo.count_reasoning_cases()
        knowledge_items = factory_mems + reasoning_cases + total_docs
        
        avg_confidence = await self.repo.get_average_confidence()
        
        return ExecutiveSummaryResponse(
            total_documents=total_docs,
            total_decision_cases=total_cases,
            open_cases=open_cases,
            closed_cases=closed_cases,
            critical_cases=critical_cases,
            pending_approvals=pending_approvals,
            knowledge_items=knowledge_items,
            reasoning_cases=reasoning_cases,
            compliance_score=92.5,
            average_confidence=avg_confidence
        )

    async def get_knowledge_growth(self) -> KnowledgeGrowthResponse:
        # Returning mocked monthly chart data
        data = [
            KnowledgeGrowthMonth(month="Jan", documents=10, factory_memory=2, reasoning_memory=1, knowledge_graph_nodes=50, decision_cases=5),
            KnowledgeGrowthMonth(month="Feb", documents=25, factory_memory=5, reasoning_memory=3, knowledge_graph_nodes=120, decision_cases=12),
            KnowledgeGrowthMonth(month="Mar", documents=45, factory_memory=12, reasoning_memory=8, knowledge_graph_nodes=210, decision_cases=22),
            KnowledgeGrowthMonth(month="Apr", documents=80, factory_memory=20, reasoning_memory=15, knowledge_graph_nodes=350, decision_cases=35),
            KnowledgeGrowthMonth(month="May", documents=120, factory_memory=35, reasoning_memory=25, knowledge_graph_nodes=500, decision_cases=50),
            KnowledgeGrowthMonth(month="Jun", documents=150, factory_memory=42, reasoning_memory=32, knowledge_graph_nodes=620, decision_cases=65)
        ]
        return KnowledgeGrowthResponse(monthly_data=data)

    async def get_machine_intelligence(self) -> MachineIntelligenceResponse:
        # Mocking data as we don't have dedicated machine tables
        top_machines = [{"name": "CNC-04", "score": 98}, {"name": "Pump System 2", "score": 95}, {"name": "Robotic Arm B", "score": 88}]
        most_failures = [{"name": "Pump System 2", "failures": 14}, {"name": "Conveyor Belt A", "failures": 9}]
        most_incidents = [{"name": "Forklift 3", "incidents": 3}]
        most_maintenance = [{"name": "CNC-04", "hours": 120}, {"name": "Boiler 1", "hours": 85}]
        highest_risk = [{"name": "Boiler 1", "risk_score": 9.2}, {"name": "High Voltage Panel C", "risk_score": 8.8}]
        
        return MachineIntelligenceResponse(
            top_10_machines=top_machines,
            most_failures=most_failures,
            most_incidents=most_incidents,
            most_maintenance=most_maintenance,
            highest_risk=highest_risk
        )

    async def get_ai_performance(self) -> AIPerformanceResponse:
        avg_conf = await self.repo.get_average_confidence()
        cases = await self.repo.count_decision_cases()
        
        return AIPerformanceResponse(
            average_processing_time="1.2s",
            average_confidence=avg_conf,
            cases_solved=cases,
            approval_rate=0.85,
            conflict_rate=0.05
        )

    async def get_compliance(self) -> ComplianceDashboardResponse:
        return ComplianceDashboardResponse(
            compliance_percentage=92.5,
            violations=3,
            pending_audits=2,
            high_risk_assets=4
        )

    async def get_activity(self) -> LiveActivityFeedResponse:
        # Mocking latest activity feed data
        return LiveActivityFeedResponse(
            latest_documents_uploaded=[{"title": "OSHA Safety Guidelines 2026", "time": "10 mins ago"}],
            decision_cases=[{"title": "Bearing failure in CNC-04", "time": "1 hour ago"}],
            approvals=[{"title": "Safety override for Boiler 1", "time": "2 hours ago"}],
            reports_generated=[{"title": "Monthly Compliance Report", "time": "3 hours ago"}],
            knowledge_added=[{"title": "Factory Memory: Recalibrated sensor on Arm B", "time": "5 hours ago"}]
        )
