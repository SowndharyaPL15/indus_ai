"""
INDUS AI — Confidence Repository

Data access layer to retrieve and create recalculation history records in
the `confidence_history` table.
"""

import logging
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.confidence_engine.confidence_models import ConfidenceHistory, ComponentScores

logger = logging.getLogger(__name__)


class ConfidenceRepository:
    """CRUD operations for confidence_history logs."""

    @staticmethod
    async def create_history_record(
        db: AsyncSession,
        decision_case_id: UUID,
        score: float,
        level: str,
        explanation: List[str],
        component_scores: ComponentScores,
    ) -> ConfidenceHistory:
        """Create a new recalculation log in confidence_history."""
        record = ConfidenceHistory(
            decision_case_id=decision_case_id,
            score=score,
            level=level,
            explanation=explanation,
            component_scores=component_scores.model_dump()
        )
        db.add(record)
        await db.flush()
        logger.info(
            "Confidence history recorded: case=%s, score=%.2f, level=%s",
            str(decision_case_id)[:8], score, level
        )
        return record

    @staticmethod
    async def get_latest(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> Optional[ConfidenceHistory]:
        """Fetch the most recent confidence calculation log."""
        stmt = (
            select(ConfidenceHistory)
            .where(ConfidenceHistory.decision_case_id == decision_case_id)
            .order_by(ConfidenceHistory.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_history(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> List[ConfidenceHistory]:
        """Fetch the full list of recalculation records for a decision case."""
        stmt = (
            select(ConfidenceHistory)
            .where(ConfidenceHistory.decision_case_id == decision_case_id)
            .order_by(ConfidenceHistory.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())
