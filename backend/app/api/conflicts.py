"""
INDUS AI — Conflict API Router

GET  /api/conflicts/{decision_case_id}         — Retrieve case conflict evaluation.
POST /api/conflicts/{decision_case_id}/resolve — Manually resolve conflicts for a case.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.conflict_engine.conflict_models import ConflictResponse
from app.conflict_engine.conflict_service import ConflictService

router = APIRouter()


@router.get("/{decision_case_id}", response_model=ConflictResponse)
async def get_case_conflicts(
    decision_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve detected conflicts for a Decision Case.

    Evaluates contradictions between RAG documentation, machine SOPs,
    engineer feedback records, past CBR reasoning failures, safety protocols,
    and compliance rule inspection records.
    """
    try:
        response = await ConflictService.get_conflicts(db, decision_case_id)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to load conflicts: {str(e)}")


@router.post("/{decision_case_id}/resolve")
async def resolve_case_conflicts(
    decision_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Manually resolve conflicts for a Decision Case.

    Updates standard database columns, marks ApprovalRequest records as approved,
    sets case status back to IN_PROGRESS, and logs a full audit entry.
    """
    try:
        resolved = await ConflictService.resolve(db, decision_case_id, current_user)
        if not resolved:
            raise HTTPException(status_code=400, detail="No unresolved conflicts found for this case ID.")
        return {"status": "SUCCESS", "message": "Case conflicts successfully resolved."}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Resolution error: {str(e)}")
