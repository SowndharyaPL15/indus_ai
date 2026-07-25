"""
INDUS AI — Conflict Repository

Data access layer to manage conflict history log records and resolve detected contradictions.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.conflict_engine.conflict_models import ConflictHistory, ConflictItem
from app.models.decision_intelligence import ConflictLog

logger = logging.getLogger(__name__)


class ConflictRepository:
    """CRUD operations for conflict history log files and standard logs."""

    @staticmethod
    async def create_history_record(
        db: AsyncSession,
        decision_case_id: UUID,
        has_conflicts: bool,
        overall_severity: str,
        conflicts: List[ConflictItem],
    ) -> ConflictHistory:
        """Create a new history record in conflict_history."""
        record = ConflictHistory(
            decision_case_id=decision_case_id,
            has_conflicts=has_conflicts,
            overall_severity=overall_severity,
            conflicts=[c.model_dump() for c in conflicts]
        )
        db.add(record)
        await db.flush()
        logger.info(
            "Conflict history recorded: case=%s, has_conflicts=%s, severity=%s",
            str(decision_case_id)[:8], has_conflicts, overall_severity
        )
        return record

    @staticmethod
    async def get_latest(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> Optional[ConflictHistory]:
        """Fetch the most recent conflict evaluation log."""
        stmt = (
            select(ConflictHistory)
            .where(ConflictHistory.decision_case_id == decision_case_id)
            .order_by(ConflictHistory.created_at.desc())
            .limit(1)
        )
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_history(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> List[ConflictHistory]:
        """Fetch the full list of evaluation logs for a decision case."""
        stmt = (
            select(ConflictHistory)
            .where(ConflictHistory.decision_case_id == decision_case_id)
            .order_by(ConflictHistory.created_at.desc())
        )
        result = await db.execute(stmt)
        return list(result.scalars().all())

    @staticmethod
    async def resolve_conflicts(
        db: AsyncSession,
        decision_case_id: UUID,
        resolved_by_user_id: UUID,
    ) -> bool:
        """
        Resolves conflicts for a decision case.
        Updates both standard ConflictLog table rows and the latest ConflictHistory entry.
        """
        now = datetime.now(timezone.utc)
        resolved_any = False

        # 1. Update standard ConflictLogs
        stmt_logs = select(ConflictLog).where(ConflictLog.decision_case_id == decision_case_id)
        res_logs = await db.execute(stmt_logs)
        logs = res_logs.scalars().all()
        for log in logs:
            if not log.resolved:
                log.resolved = True
                resolved_any = True

        # 2. Update latest ConflictHistory record
        latest = await ConflictRepository.get_latest(db, decision_case_id)
        if latest and not latest.resolved:
            latest.resolved = True
            latest.resolved_by = resolved_by_user_id
            latest.resolved_at = now
            resolved_any = True

        if resolved_any:
            logger.info(
                "Conflicts resolved for case %s by user %s",
                str(decision_case_id)[:8], str(resolved_by_user_id)[:8]
            )
        return resolved_any
