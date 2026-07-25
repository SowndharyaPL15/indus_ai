import uuid
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.reports.report_models import ReportResponse
from app.reports.report_repository import ReportRepository
from app.reports.report_generator import ReportGenerator

class ReportService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ReportRepository(db)

    async def _generate_common(self, case_id: uuid.UUID, report_type: str, user_id: uuid.UUID) -> ReportResponse:
        case = await self.repo.get_decision_case(case_id)
        if not case:
            raise HTTPException(status_code=404, detail="Decision case not found")
            
        ai_responses = await self.repo.get_ai_responses(case_id)
        audit_logs = await self.repo.get_audit_logs(case_id)
        approvals = await self.repo.get_approvals(case_id)
        
        report_id_str = str(uuid.uuid4())
        
        if report_type == "Decision Case Report":
            filepath = ReportGenerator.generate_decision_case_report(
                report_id_str, case, ai_responses, approvals, audit_logs
            )
        elif report_type == "Audit Report":
            filepath = ReportGenerator.generate_audit_report(
                report_id_str, case, audit_logs
            )
        else:
            raise ValueError(f"Unknown common report type: {report_type}")
            
        # Save to DB
        report = await self.repo.save_report_metadata(
            title=f"{report_type} - {case.id}",
            file_path=filepath,
            report_type=report_type,
            generated_by=user_id,
            decision_case_id=case.id
        )
        
        # Log Audit
        await self.repo.log_audit(
            action="REPORT_GENERATED",
            details={"report_id": str(report.id), "report_type": report_type},
            user_id=user_id,
            decision_case_id=case.id
        )
        
        return report

    async def generate_decision_case_report(self, case_id: uuid.UUID, user_id: uuid.UUID) -> ReportResponse:
        return await self._generate_common(case_id, "Decision Case Report", user_id)

    async def generate_compliance_report(self, user_id: uuid.UUID) -> ReportResponse:
        report_id_str = str(uuid.uuid4())
        filepath = ReportGenerator.generate_compliance_report(report_id_str)
        
        report = await self.repo.save_report_metadata(
            title="System Compliance Report",
            file_path=filepath,
            report_type="Compliance Report",
            generated_by=user_id,
            decision_case_id=None
        )
        
        await self.repo.log_audit(
            action="REPORT_GENERATED",
            details={"report_id": str(report.id), "report_type": "Compliance Report"},
            user_id=user_id,
            decision_case_id=None
        )
        
        return report

    async def generate_maintenance_report(self, machine_id: str, user_id: uuid.UUID) -> ReportResponse:
        # Mocking getting recent cases for machine since no machine_id on cases directly in this simple example
        # Normally would query cases by machine_id
        report_id_str = str(uuid.uuid4())
        filepath = ReportGenerator.generate_maintenance_report(report_id_str, machine_id, [], [])
        
        report = await self.repo.save_report_metadata(
            title=f"Maintenance Report - {machine_id}",
            file_path=filepath,
            report_type="Maintenance Report",
            generated_by=user_id,
            decision_case_id=None
        )
        
        await self.repo.log_audit(
            action="REPORT_GENERATED",
            details={"report_id": str(report.id), "report_type": "Maintenance Report", "machine_id": machine_id},
            user_id=user_id,
            decision_case_id=None
        )
        return report

    async def generate_executive_summary(self, user_id: uuid.UUID) -> ReportResponse:
        report_id_str = str(uuid.uuid4())
        
        # Mocking stats
        filepath = ReportGenerator.generate_executive_summary_report(
            report_id_str, 
            total_cases=142, 
            avg_confidence=0.88, 
            critical_cases=5, 
            pending_approvals=2
        )
        
        report = await self.repo.save_report_metadata(
            title="Executive Summary",
            file_path=filepath,
            report_type="Executive Summary Report",
            generated_by=user_id,
            decision_case_id=None
        )
        
        await self.repo.log_audit(
            action="REPORT_GENERATED",
            details={"report_id": str(report.id), "report_type": "Executive Summary Report"},
            user_id=user_id,
            decision_case_id=None
        )
        return report

    async def generate_audit_report(self, case_id: uuid.UUID, user_id: uuid.UUID) -> ReportResponse:
        return await self._generate_common(case_id, "Audit Report", user_id)

    async def get_report_download_path(self, report_id: uuid.UUID) -> str:
        report = await self.repo.get_report_by_id(report_id)
        if not report:
            raise HTTPException(status_code=404, detail="Report not found")
        return report.file_path
