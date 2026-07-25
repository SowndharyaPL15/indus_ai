"""
INDUS AI — Feedback Processor

Orchestrates the full feedback-to-memory pipeline:
1. Validate via MemoryValidator
2. Look up the DecisionCase for context (machine_id, original query)
3. Create FactoryMemoryRecord
4. Update DecisionCase status → KNOWLEDGE_CAPTURED
5. Write AuditLog entry
6. Return the created record
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_intelligence import DecisionCase, CaseStatusEnum
from app.models.factory_memory_record import FactoryMemoryRecord
from app.models.system import AuditLog
from app.models.users import User
from app.memory_engine.memory_validator import MemoryValidator, ValidationResult
from app.memory_engine.memory_models import FeedbackSubmission

logger = logging.getLogger(__name__)


class FeedbackProcessor:
    """Processes raw engineer feedback into validated factory memory."""

    @staticmethod
    async def process(
        db: AsyncSession,
        user: User,
        payload: FeedbackSubmission,
    ) -> FactoryMemoryRecord:
        """
        Full pipeline: validate → lookup case → store memory → update status → audit.

        Raises:
            ValueError: If validation fails or the decision case is not found.
        """

        # ── 1. Validate ──────────────────────────────────────────────────
        validation: ValidationResult = await MemoryValidator.validate(
            db=db,
            decision_case_id=payload.decision_case_id,
            engineer_id=user.id,
            engineer_feedback=payload.engineer_feedback,
            actual_solution=payload.actual_solution,
            lesson_learned=payload.lesson_learned,
        )

        if not validation.is_valid:
            raise ValueError(validation.rejection_reason)

        # ── 2. Lookup Decision Case ──────────────────────────────────────
        stmt = select(DecisionCase).where(DecisionCase.id == payload.decision_case_id)
        result = await db.execute(stmt)
        decision_case = result.scalar_one_or_none()

        if decision_case is None:
            raise ValueError(
                f"Decision case not found: {payload.decision_case_id}"
            )

        # ── 3. Create Factory Memory Record ──────────────────────────────
        memory_record = FactoryMemoryRecord(
            decision_case_id=decision_case.id,
            machine_id=decision_case.machine_id,
            engineer_id=user.id,
            problem=decision_case.query,
            solution=validation.cleaned_solution,
            lesson=validation.cleaned_lesson,
            engineer_feedback=validation.cleaned_feedback,
            rating=payload.rating,
            useful=payload.useful,
            validated=True,
            times_reused=0,
        )
        db.add(memory_record)

        # ── 4. Update Decision Case Status ───────────────────────────────
        decision_case.status = CaseStatusEnum.KNOWLEDGE_CAPTURED
        logger.info(
            "Decision case %s status → KNOWLEDGE_CAPTURED", decision_case.id
        )

        # ── 5. Write Audit Log ───────────────────────────────────────────
        audit = AuditLog(
            user_id=user.id,
            decision_case_id=decision_case.id,
            action="MEMORY_FEEDBACK_SUBMITTED",
            details={
                "rating": payload.rating,
                "useful": payload.useful,
                "solution_length": len(validation.cleaned_solution),
                "lesson_length": len(validation.cleaned_lesson),
            },
        )
        db.add(audit)

        # ── 6. Commit & Return ───────────────────────────────────────────
        await db.commit()
        await db.refresh(memory_record)

        logger.info(
            "Factory memory created: %s (case=%s, engineer=%s)",
            memory_record.id,
            decision_case.id,
            user.id,
        )
        return memory_record
