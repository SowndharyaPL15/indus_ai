"""
INDUS AI — Living Factory Memory API

POST /api/memory/feedback   — Submit engineer feedback for a resolved decision case.
GET  /api/memory/search     — Search factory memories by text query.
"""

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.memory_engine.memory_models import (
    FeedbackSubmission,
    FeedbackResponse,
    MemorySearchResponse,
)
from app.memory_engine.memory_service import MemoryService

router = APIRouter()


@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(
    payload: FeedbackSubmission,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Submit engineer feedback for a resolved Decision Case.

    The feedback is validated (rejects empty, short, duplicate, or spam),
    stored as a FactoryMemoryRecord, and the Decision Case status is
    updated to KNOWLEDGE_CAPTURED. An audit log entry is also created.
    """
    try:
        response = await MemoryService.submit_feedback(db, current_user, payload)
        return response
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.get("/search", response_model=MemorySearchResponse)
async def search_memories(
    q: str = Query(..., min_length=1, description="Search query string"),
    limit: int = Query(20, ge=1, le=100, description="Max results to return"),
    offset: int = Query(0, ge=0, description="Offset for pagination"),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Search factory memories by text query.

    Searches across problem, solution, lesson, and feedback fields.
    Results are ordered by rating (desc), recency (desc), usage count (desc).
    """
    return await MemoryService.search_memories(db, q, limit, offset)
