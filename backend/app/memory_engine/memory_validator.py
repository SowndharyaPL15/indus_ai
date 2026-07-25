"""
INDUS AI — Memory Validator

Quality gate that ensures only meaningful engineer feedback
becomes part of the Living Factory Memory.

Rejects:
  - Empty or whitespace-only feedback
  - Very short feedback (< 20 characters)
  - Duplicate feedback (same case + same engineer)
  - Spam patterns (repeated chars, all-caps gibberish)
"""

import re
import logging
from dataclasses import dataclass
from uuid import UUID

from sqlalchemy import select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.factory_memory_record import FactoryMemoryRecord

logger = logging.getLogger(__name__)

MIN_FEEDBACK_LENGTH = 20


@dataclass
class ValidationResult:
    """Outcome of the validation check."""
    is_valid: bool
    rejection_reason: str | None = None
    cleaned_feedback: str | None = None
    cleaned_solution: str | None = None
    cleaned_lesson: str | None = None


class MemoryValidator:
    """Validates engineer feedback before it is stored as factory memory."""

    # ── Public API ────────────────────────────────────────────────────────

    @classmethod
    async def validate(
        cls,
        db: AsyncSession,
        decision_case_id: UUID,
        engineer_id: UUID,
        engineer_feedback: str,
        actual_solution: str,
        lesson_learned: str,
    ) -> ValidationResult:
        """
        Run all validation checks in order. Returns a ValidationResult
        indicating whether the feedback is acceptable.
        """
        # 1. Empty check
        result = cls._check_empty(engineer_feedback, actual_solution, lesson_learned)
        if result is not None:
            return result

        # 2. Strip and clean
        feedback_clean = engineer_feedback.strip()
        solution_clean = actual_solution.strip()
        lesson_clean = lesson_learned.strip()

        # 3. Length check
        result = cls._check_length(feedback_clean, solution_clean)
        if result is not None:
            return result

        # 4. Spam check
        result = cls._check_spam(feedback_clean, solution_clean, lesson_clean)
        if result is not None:
            return result

        # 5. Duplicate check (requires DB)
        result = await cls._check_duplicate(db, decision_case_id, engineer_id)
        if result is not None:
            return result

        return ValidationResult(
            is_valid=True,
            cleaned_feedback=feedback_clean,
            cleaned_solution=solution_clean,
            cleaned_lesson=lesson_clean,
        )

    # ── Private Checks ────────────────────────────────────────────────────

    @staticmethod
    def _check_empty(
        feedback: str, solution: str, lesson: str
    ) -> ValidationResult | None:
        """Reject blank / whitespace-only fields."""
        if not feedback or not feedback.strip():
            return ValidationResult(
                is_valid=False,
                rejection_reason="Engineer feedback cannot be empty.",
            )
        if not solution or not solution.strip():
            return ValidationResult(
                is_valid=False,
                rejection_reason="Actual solution cannot be empty.",
            )
        if not lesson or not lesson.strip():
            return ValidationResult(
                is_valid=False,
                rejection_reason="Lesson learned cannot be empty.",
            )
        return None

    @staticmethod
    def _check_length(feedback: str, solution: str) -> ValidationResult | None:
        """Reject feedback or solution shorter than the minimum length."""
        if len(feedback) < MIN_FEEDBACK_LENGTH:
            return ValidationResult(
                is_valid=False,
                rejection_reason=(
                    f"Engineer feedback is too short "
                    f"(minimum {MIN_FEEDBACK_LENGTH} characters, got {len(feedback)})."
                ),
            )
        if len(solution) < MIN_FEEDBACK_LENGTH:
            return ValidationResult(
                is_valid=False,
                rejection_reason=(
                    f"Actual solution is too short "
                    f"(minimum {MIN_FEEDBACK_LENGTH} characters, got {len(solution)})."
                ),
            )
        return None

    @staticmethod
    def _check_spam(
        feedback: str, solution: str, lesson: str
    ) -> ValidationResult | None:
        """
        Detect obvious spam patterns:
        - Repeated single character (e.g., 'aaaaaaa')
        - Excessive repeated words (e.g., 'test test test test')
        """
        texts = [feedback, solution, lesson]
        for text in texts:
            # Repeated characters: 5+ of the same char in a row
            if re.search(r"(.)\1{4,}", text):
                return ValidationResult(
                    is_valid=False,
                    rejection_reason="Feedback appears to contain spam (repeated characters).",
                )

            # Repeated words: same word 4+ times consecutively
            if re.search(r"\b(\w+)(?:\s+\1){3,}\b", text, re.IGNORECASE):
                return ValidationResult(
                    is_valid=False,
                    rejection_reason="Feedback appears to contain spam (repeated words).",
                )

        return None

    @staticmethod
    async def _check_duplicate(
        db: AsyncSession, decision_case_id: UUID, engineer_id: UUID
    ) -> ValidationResult | None:
        """Reject if this engineer already submitted feedback for this case."""
        stmt = select(FactoryMemoryRecord.id).where(
            and_(
                FactoryMemoryRecord.decision_case_id == decision_case_id,
                FactoryMemoryRecord.engineer_id == engineer_id,
                FactoryMemoryRecord.validated == True,  # noqa: E712
            )
        )
        result = await db.execute(stmt)
        existing = result.scalar_one_or_none()

        if existing is not None:
            return ValidationResult(
                is_valid=False,
                rejection_reason=(
                    "Duplicate feedback: you have already submitted validated "
                    "feedback for this decision case."
                ),
            )
        return None
