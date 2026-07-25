"""
INDUS AI — Memory Retriever

Searches and retrieves factory memory records for the Living Factory Memory API.

Results are ordered by:
  1. Rating (descending)
  2. Recency (created_at descending)
  3. Usage count (times_reused descending)

Also exposes `get_relevant_memories()` for future IDIE integration
(memory as additional evidence, NOT direct answers).
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select, func, or_, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.factory_memory_record import FactoryMemoryRecord

logger = logging.getLogger(__name__)


class MemoryRetriever:
    """Retrieves validated factory memory records."""

    @staticmethod
    async def search(
        db: AsyncSession,
        query: str,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[List[FactoryMemoryRecord], int]:
        """
        Full-text search across problem, solution, and lesson fields.

        Returns:
            Tuple of (list of records, total matching count).
        """
        search_pattern = f"%{query}%"

        # Base filter: validated records matching the query
        search_filter = and_validated(
            or_(
                FactoryMemoryRecord.problem.ilike(search_pattern),
                FactoryMemoryRecord.solution.ilike(search_pattern),
                FactoryMemoryRecord.lesson.ilike(search_pattern),
                FactoryMemoryRecord.engineer_feedback.ilike(search_pattern),
            )
        )

        # Count total matches
        count_stmt = select(func.count()).select_from(
            FactoryMemoryRecord
        ).where(search_filter)
        total = (await db.execute(count_stmt)).scalar() or 0

        # Fetch paginated results ordered by rating → recency → usage
        results_stmt = (
            select(FactoryMemoryRecord)
            .where(search_filter)
            .order_by(
                FactoryMemoryRecord.rating.desc(),
                FactoryMemoryRecord.created_at.desc(),
                FactoryMemoryRecord.times_reused.desc(),
            )
            .limit(limit)
            .offset(offset)
        )
        result = await db.execute(results_stmt)
        records = list(result.scalars().all())

        logger.info(
            "Memory search for '%s': %d results (total=%d)", query, len(records), total
        )
        return records, total

    @staticmethod
    async def get_by_id(
        db: AsyncSession,
        memory_id: UUID,
    ) -> Optional[FactoryMemoryRecord]:
        """Fetch a single memory record by its ID."""
        stmt = select(FactoryMemoryRecord).where(
            FactoryMemoryRecord.id == memory_id
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_for_case(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> List[FactoryMemoryRecord]:
        """Fetch all memory records for a specific decision case."""
        stmt = (
            select(FactoryMemoryRecord)
            .where(
                FactoryMemoryRecord.decision_case_id == decision_case_id,
                FactoryMemoryRecord.validated == True,  # noqa: E712
            )
            .order_by(FactoryMemoryRecord.rating.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def get_relevant_memories(
        db: AsyncSession,
        query: str,
        limit: int = 5,
    ) -> List[FactoryMemoryRecord]:
        """
        Retrieve the most relevant validated memories for a given query.

        This is the integration point for IDIE — memory serves as
        ADDITIONAL evidence alongside RAG, never as a direct answer.

        Returns the top-N records by relevance (ILIKE match),
        ordered by rating → recency → usage.
        """
        search_pattern = f"%{query}%"

        stmt = (
            select(FactoryMemoryRecord)
            .where(
                FactoryMemoryRecord.validated == True,  # noqa: E712
                or_(
                    FactoryMemoryRecord.problem.ilike(search_pattern),
                    FactoryMemoryRecord.solution.ilike(search_pattern),
                    FactoryMemoryRecord.lesson.ilike(search_pattern),
                ),
            )
            .order_by(
                FactoryMemoryRecord.rating.desc(),
                FactoryMemoryRecord.created_at.desc(),
                FactoryMemoryRecord.times_reused.desc(),
            )
            .limit(limit)
        )
        result = await db.execute(stmt)
        records = list(result.scalars().all())

        logger.info(
            "Relevant memories for IDIE query '%s': %d found", query, len(records)
        )
        return records


# ── Helper ────────────────────────────────────────────────────────────────────

def and_validated(*conditions):
    """Combine conditions with a mandatory validated=True filter."""
    return and_(
        FactoryMemoryRecord.validated == True,  # noqa: E712
        *conditions,
    )
