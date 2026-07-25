"""
INDUS AI — Confidence API Router

GET /api/confidence/{decision_case_id} — Retrieve the programmatic confidence analysis.
"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.confidence_engine.confidence_models import ConfidenceResponse
from app.confidence_engine.confidence_service import ConfidenceService

router = APIRouter()


@router.get("/{decision_case_id}", response_model=ConfidenceResponse)
async def get_case_confidence(
    decision_case_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Retrieve confidence score analysis for a Decision Case.

    Calculates scores programmatically across manual documents, living memories,
    CBR historical outcomes, intent confidence, and Knowledge Graph context density.
    Returns scores, explanations, and level bounds.
    """
    try:
        response = await ConfidenceService.get_confidence(db, decision_case_id)
        return response
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Recalculation error: {str(e)}")
