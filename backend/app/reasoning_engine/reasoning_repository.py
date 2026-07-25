"""
INDUS AI — Reasoning Repository

Data access layer for the existing `reasoning_memory` table.
All database operations for ReasoningMemory records are centralized here.
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, or_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_intelligence import ReasoningMemory, OutcomeStatusEnum

logger = logging.getLogger(__name__)


class ReasoningRepository:
    """CRUD and query operations for the reasoning_memory table."""

    # ── Create ────────────────────────────────────────────────────────────

    @staticmethod
    async def create(
        db: AsyncSession,
        record: ReasoningMemory,
    ) -> ReasoningMemory:
        """Insert a new ReasoningMemory row and return the refreshed record."""
        db.add(record)
        await db.flush()
        await db.refresh(record)
        logger.info("Reasoning record created: %s (case=%s)", record.id, record.decision_case_id)
        return record

    # ── Read by ID ────────────────────────────────────────────────────────

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        reasoning_id: UUID,
    ) -> Optional[ReasoningMemory]:
        """Fetch a single reasoning record by its primary key."""
        stmt = select(ReasoningMemory).where(ReasoningMemory.id == reasoning_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    # ── Read by Decision Case ─────────────────────────────────────────────

    @staticmethod
    async def get_by_case(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> List[ReasoningMemory]:
        """Fetch all reasoning records for a specific decision case."""
        stmt = (
            select(ReasoningMemory)
            .where(ReasoningMemory.decision_case_id == decision_case_id)
            .order_by(ReasoningMemory.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── Successful Cases ──────────────────────────────────────────────────

    @staticmethod
    async def get_successful_cases(
        db: AsyncSession,
        limit: int = 50,
    ) -> List[ReasoningMemory]:
        """
        Fetch all reasoning records with SUCCESSFUL outcome,
        ordered by confidence → recency.
        """
        stmt = (
            select(ReasoningMemory)
            .where(ReasoningMemory.outcome_status == OutcomeStatusEnum.SUCCESSFUL)
            .order_by(
                ReasoningMemory.confidence_score.desc(),
                ReasoningMemory.created_at.desc(),
            )
            .limit(limit)
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    # ── Text Search ───────────────────────────────────────────────────────

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        limit: int = 20,
    ) -> List[ReasoningMemory]:
        """
        ILIKE search across problem_summary, final_recommendation,
        and reusable_lesson fields.

        Returns records ordered by confidence → recency.
        """
        search_pattern = f"%{query}%"

        stmt = (
            select(ReasoningMemory)
            .where(
                or_(
                    ReasoningMemory.problem_summary.ilike(search_pattern),
                    ReasoningMemory.final_recommendation.ilike(search_pattern),
                    ReasoningMemory.reusable_lesson.ilike(search_pattern),
                    ReasoningMemory.case_title.ilike(search_pattern),
                )
            )
            .order_by(
                ReasoningMemory.confidence_score.desc(),
                ReasoningMemory.created_at.desc(),
            )
            .limit(limit)
        )
        result = await db.execute(stmt)
        records = list(result.scalars().all())

        logger.info(
            "Reasoning search for '%s': %d results found", query, len(records)
        )
        return records

    # ── Count ─────────────────────────────────────────────────────────────

    @staticmethod
    async def count_all(db: AsyncSession) -> int:
        """Total number of reasoning records."""
        stmt = select(func.count()).select_from(ReasoningMemory)
        return (await db.execute(stmt)).scalar() or 0
