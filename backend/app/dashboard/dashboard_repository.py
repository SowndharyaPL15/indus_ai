from typing import Dict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from app.models.decision_intelligence import DecisionCase, ReasoningMemory, ApprovalRequest, ConfidenceScore
from app.models.documents import Document
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.system import GeneratedReport

class DashboardRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def count_documents(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Document))
        return result.scalar() or 0

    async def count_decision_cases(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(DecisionCase))
        return result.scalar() or 0

    async def count_decision_cases_by_status(self) -> Dict[str, int]:
        result = await self.db.execute(
            select(DecisionCase.status, func.count(DecisionCase.id))
            .group_by(DecisionCase.status)
        )
        return {status.value if hasattr(status, 'value') else str(status): count for status, count in result.all()}

    async def count_factory_memories(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(FactoryMemoryRecord))
        return result.scalar() or 0

    async def count_reasoning_cases(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(ReasoningMemory))
        return result.scalar() or 0

    async def count_generated_reports(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(GeneratedReport))
        return result.scalar() or 0
        
    async def get_average_confidence(self) -> float:
        result = await self.db.execute(select(func.avg(ConfidenceScore.score)).select_from(ConfidenceScore))
        val = result.scalar()
        return float(val) if val is not None else 0.0

    async def count_approvals_by_status(self) -> Dict[str, int]:
        result = await self.db.execute(
            select(ApprovalRequest.status, func.count(ApprovalRequest.id))
            .group_by(ApprovalRequest.status)
        )
        return {status.value if hasattr(status, 'value') else str(status): count for status, count in result.all()}

    # Graph nodes are currently a mock since we don't have a concrete relational table for all nodes natively in standard db
    # We will return 0 or a mocked value from the service.

    async def check_db_health(self) -> bool:
        try:
            await self.db.execute(select(1))
            return True
        except Exception:
            return False
