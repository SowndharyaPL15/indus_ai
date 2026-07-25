import uuid
from typing import List
from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.decision_intelligence import ApprovalRequest, ApprovalStatusEnum, CaseStatusEnum
from app.models.system import AuditLog
from app.models.users import User
from app.approval_engine.approval_models import ApprovalRequestCreate, ApprovalActionRequest, RejectActionRequest, EscalateActionRequest
from app.approval_engine.approval_repository import ApprovalRepository
from app.approval_engine.approval_rules import check_can_approve
from app.approval_engine.approval_history import ApprovalHistoryRecord

class ApprovalService:
    def __init__(self, db: AsyncSession):
        self.db = db
        self.repo = ApprovalRepository(db)

    async def _log_audit(self, action: str, details: dict, decision_case_id: uuid.UUID = None, user_id: uuid.UUID = None):
        log = AuditLog(
            user_id=user_id,
            decision_case_id=decision_case_id,
            action=action,
            details=details
        )
        self.db.add(log)
        # We don't commit here, we let the caller commit the transaction
        
    async def _log_history(self, decision_case_id: uuid.UUID, reviewer_id: uuid.UUID, decision: str, comment: str, prev_status: str, new_status: str):
        history = ApprovalHistoryRecord(
            decision_case_id=decision_case_id,
            reviewer_id=reviewer_id,
            decision=decision,
            comment=comment,
            previous_status=prev_status,
            new_status=new_status
        )
        self.db.add(history)

    async def create_request(self, payload: ApprovalRequestCreate) -> ApprovalRequest:
        request = ApprovalRequest(
            decision_case_id=payload.decision_case_id,
            requested_by=payload.requested_by,
            approver_role=payload.approver_role,
            reason=payload.reason,
            risk_level=payload.risk_level,
            recommendation_summary=payload.recommendation_summary,
            status=ApprovalStatusEnum.PENDING
        )
        request = await self.repo.create_request(request)
        await self._log_audit(
            action="APPROVAL_REQUESTED",
            details={"approval_id": str(request.id), "reason": request.reason},
            decision_case_id=request.decision_case_id,
            user_id=request.requested_by
        )
        await self.db.commit()
        return request

    async def get_pending(self) -> List[ApprovalRequest]:
        return await self.repo.get_pending()

    async def get_by_id(self, approval_id: uuid.UUID) -> ApprovalRequest:
        request = await self.repo.get_by_id(approval_id)
        if not request:
            raise HTTPException(status_code=404, detail="Approval request not found")
        return request

    async def approve(self, approval_id: uuid.UUID, payload: ApprovalActionRequest, user: User) -> ApprovalRequest:
        request = await self.get_by_id(approval_id)
        if request.status != ApprovalStatusEnum.PENDING:
            raise HTTPException(status_code=400, detail="Only pending requests can be approved")
            
        check_can_approve(user.role, request)
        
        request.status = ApprovalStatusEnum.APPROVED
        request.approved_by = payload.approved_by
        request.comments = payload.comments
        
        # Optionally update decision case status
        if request.decision_case:
            request.decision_case.status = CaseStatusEnum.IN_PROGRESS
            
        request = await self.repo.update_request(request)
        
        await self._log_audit(
            action="APPROVAL_GRANTED",
            details={"approval_id": str(request.id), "comments": request.comments},
            decision_case_id=request.decision_case_id,
            user_id=payload.approved_by
        )
        await self._log_history(
            decision_case_id=request.decision_case_id,
            reviewer_id=payload.approved_by,
            decision="APPROVE",
            comment=payload.comments,
            prev_status=ApprovalStatusEnum.PENDING.value,
            new_status=ApprovalStatusEnum.APPROVED.value
        )
        await self.db.commit()
        return request

    async def reject(self, approval_id: uuid.UUID, payload: RejectActionRequest, user: User) -> ApprovalRequest:
        request = await self.get_by_id(approval_id)
        if request.status != ApprovalStatusEnum.PENDING:
            raise HTTPException(status_code=400, detail="Only pending requests can be rejected")
            
        check_can_approve(user.role, request)
        
        request.status = ApprovalStatusEnum.REJECTED
        request.rejected_by = payload.rejected_by
        request.reject_reason = payload.reason
        
        if request.decision_case:
            request.decision_case.status = CaseStatusEnum.RESOLVED
            
        request = await self.repo.update_request(request)
        
        await self._log_audit(
            action="APPROVAL_REJECTED",
            details={"approval_id": str(request.id), "reason": payload.reason},
            decision_case_id=request.decision_case_id,
            user_id=payload.rejected_by
        )
        await self._log_history(
            decision_case_id=request.decision_case_id,
            reviewer_id=payload.rejected_by,
            decision="REJECT",
            comment=payload.reason,
            prev_status=ApprovalStatusEnum.PENDING.value,
            new_status=ApprovalStatusEnum.REJECTED.value
        )
        await self.db.commit()
        return request

    async def escalate(self, approval_id: uuid.UUID, payload: EscalateActionRequest, user: User) -> ApprovalRequest:
        request = await self.get_by_id(approval_id)
        if request.status != ApprovalStatusEnum.PENDING:
            raise HTTPException(status_code=400, detail="Only pending requests can be escalated")
            
        # Anyone can potentially escalate if they can see it, but we can restrict
        request.status = ApprovalStatusEnum.ESCALATED
        request.comments = f"Escalated by {user.name}: {payload.reason}"
        
        request = await self.repo.update_request(request)
        
        await self._log_audit(
            action="APPROVAL_ESCALATED",
            details={"approval_id": str(request.id), "reason": payload.reason},
            decision_case_id=request.decision_case_id,
            user_id=payload.escalated_by
        )
        await self._log_history(
            decision_case_id=request.decision_case_id,
            reviewer_id=payload.escalated_by,
            decision="ESCALATE",
            comment=payload.reason,
            prev_status=ApprovalStatusEnum.PENDING.value,
            new_status=ApprovalStatusEnum.ESCALATED.value
        )
        await self.db.commit()
        return request
