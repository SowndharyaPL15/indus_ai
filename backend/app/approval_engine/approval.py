from uuid import UUID
from typing import List
from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.models.users import User
from app.api.auth import get_current_user
from app.approval_engine.approval_models import (
    ApprovalRequestCreate, 
    ApprovalResponse, 
    ApprovalActionRequest, 
    RejectActionRequest, 
    EscalateActionRequest
)
from app.approval_engine.approval_service import ApprovalService

router = APIRouter()

# Mock function for getting a default user if auth is not fully configured,
# but we will use the actual get_current_user to remain enterprise-grade.

@router.post("/request", response_model=ApprovalResponse)
async def create_approval_request(
    payload: ApprovalRequestCreate,
    db: AsyncSession = Depends(get_db)
):
    service = ApprovalService(db)
    return await service.create_request(payload)

@router.get("/pending", response_model=List[ApprovalResponse])
async def get_pending_approvals(
    db: AsyncSession = Depends(get_db)
):
    service = ApprovalService(db)
    return await service.get_pending()

@router.get("/{approval_id}", response_model=ApprovalResponse)
async def get_approval(
    approval_id: UUID,
    db: AsyncSession = Depends(get_db)
):
    service = ApprovalService(db)
    return await service.get_by_id(approval_id)

@router.post("/{approval_id}/approve", response_model=ApprovalResponse)
async def approve_request(
    approval_id: UUID,
    payload: ApprovalActionRequest,
    db: AsyncSession = Depends(get_db),
    # Assuming standard get_current_user implementation
    current_user: User = Depends(get_current_user) 
):
    service = ApprovalService(db)
    return await service.approve(approval_id, payload, current_user)

@router.post("/{approval_id}/reject", response_model=ApprovalResponse)
async def reject_request(
    approval_id: UUID,
    payload: RejectActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ApprovalService(db)
    return await service.reject(approval_id, payload, current_user)

@router.post("/{approval_id}/escalate", response_model=ApprovalResponse)
async def escalate_request(
    approval_id: UUID,
    payload: EscalateActionRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    service = ApprovalService(db)
    return await service.escalate(approval_id, payload, current_user)
