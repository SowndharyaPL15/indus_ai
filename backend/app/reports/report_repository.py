from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.system import GeneratedReport, AuditLog
from app.models.decision_intelligence import DecisionCase, AIResponse, ApprovalRequest

class ReportRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def save_report_metadata(self, title: str, file_path: str, report_type: str, generated_by: UUID, decision_case_id: UUID) -> GeneratedReport:
        report = GeneratedReport(
            title=title,
            file_path=file_path,
            report_type=report_type,
            generated_by=generated_by,
            decision_case_id=decision_case_id
        )
        self.db.add(report)
        await self.db.commit()
        await self.db.refresh(report)
        return report

    async def get_report_by_id(self, report_id: UUID) -> Optional[GeneratedReport]:
        result = await self.db.execute(select(GeneratedReport).where(GeneratedReport.id == report_id))
        return result.scalar_one_or_none()

    async def get_decision_case(self, case_id: UUID) -> Optional[DecisionCase]:
        # Simple fetch, in reality might need options(joinedload(...))
        result = await self.db.execute(select(DecisionCase).where(DecisionCase.id == case_id))
        return result.scalar_one_or_none()
        
    async def get_ai_responses(self, case_id: UUID) -> List[AIResponse]:
        result = await self.db.execute(select(AIResponse).where(AIResponse.decision_case_id == case_id))
        return list(result.scalars().all())

    async def get_audit_logs(self, case_id: UUID) -> List[AuditLog]:
        result = await self.db.execute(select(AuditLog).where(AuditLog.decision_case_id == case_id))
        return list(result.scalars().all())
        
    async def get_approvals(self, case_id: UUID) -> List[ApprovalRequest]:
        result = await self.db.execute(select(ApprovalRequest).where(ApprovalRequest.decision_case_id == case_id))
        return list(result.scalars().all())

    async def log_audit(self, action: str, details: dict, user_id: UUID, decision_case_id: UUID):
        log = AuditLog(
            action=action,
            details=details,
            user_id=user_id,
            decision_case_id=decision_case_id
        )
        self.db.add(log)
        await self.db.commit()
