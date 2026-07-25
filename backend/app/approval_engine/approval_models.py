from typing import Optional
from uuid import UUID
from pydantic import BaseModel
from app.models.decision_intelligence import ApprovalStatusEnum

class ApprovalRequestCreate(BaseModel):
    decision_case_id: UUID
    requested_by: Optional[UUID] = None
    approver_role: str
    reason: str
    risk_level: str
    recommendation_summary: str

class ApprovalActionRequest(BaseModel):
    approved_by: Optional[UUID] = None
    comments: Optional[str] = None

class RejectActionRequest(BaseModel):
    rejected_by: Optional[UUID] = None
    reason: str

class EscalateActionRequest(BaseModel):
    escalated_by: Optional[UUID] = None
    reason: str

class ApprovalResponse(BaseModel):
    id: UUID
    decision_case_id: UUID
    requested_by: Optional[UUID]
    approver_role: str
    reason: str
    risk_level: str
    recommendation_summary: str
    status: ApprovalStatusEnum
    approved_by: Optional[UUID]
    rejected_by: Optional[UUID]
    comments: Optional[str]
    reject_reason: Optional[str]

    class Config:
        from_attributes = True
