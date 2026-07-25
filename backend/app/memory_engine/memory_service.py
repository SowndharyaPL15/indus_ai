"""
INDUS AI — Memory Service

High-level service layer consumed by the API router.
Delegates to FeedbackProcessor and MemoryRetriever.
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.users import User
from app.models.factory_memory_record import FactoryMemoryRecord
from app.memory_engine.memory_models import (
    FeedbackSubmission,
    FeedbackResponse,
    MemorySearchResult,
    MemorySearchResponse,
)
from app.memory_engine.feedback_processor import FeedbackProcessor
from app.memory_engine.memory_retriever import MemoryRetriever

logger = logging.getLogger(__name__)


class MemoryService:
    """Facade for all Living Factory Memory operations."""

    # ── Feedback Submission ───────────────────────────────────────────────

    @staticmethod
    async def submit_feedback(
        db: AsyncSession,
        user: User,
        payload: FeedbackSubmission,
    ) -> FeedbackResponse:
        """
        Validate and store engineer feedback as factory memory.

        Raises:
            ValueError: Propagated from FeedbackProcessor on validation or lookup failure.
        """
        record = await FeedbackProcessor.process(db, user, payload)

        return FeedbackResponse(
            memory_id=record.id,
            decision_case_id=record.decision_case_id,
            status="KNOWLEDGE_CAPTURED",
            message="Feedback validated and stored as factory memory.",
        )

    # ── Search ────────────────────────────────────────────────────────────

    @staticmethod
    async def search_memories(
        db: AsyncSession,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> MemorySearchResponse:
        """
        Search factory memories by text query across problem, solution, and lesson.
        """
        records, total = await MemoryRetriever.search(db, query, limit, offset)

        return MemorySearchResponse(
            results=[
                MemorySearchResult.model_validate(r) for r in records
            ],
            total=total,
            query=query,
            limit=limit,
            offset=offset,
        )

    # ── Single Record Lookup ──────────────────────────────────────────────

    @staticmethod
    async def get_memory_by_id(
        db: AsyncSession,
        memory_id: UUID,
    ) -> Optional[FactoryMemoryRecord]:
        """Retrieve a single factory memory record by ID."""
        return await MemoryRetriever.get_by_id(db, memory_id)

    # ── Memories for a Decision Case ──────────────────────────────────────

    @staticmethod
    async def get_memories_for_case(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> List[FactoryMemoryRecord]:
        """Retrieve all memory records tied to a specific decision case."""
        return await MemoryRetriever.get_for_case(db, decision_case_id)
