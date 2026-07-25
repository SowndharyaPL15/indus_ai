"""
INDUS AI — Reasoning Service

High-level service facade for the Reasoning Memory Engine.
Consumed by the API router and exposed for future IDIE integration.

Key methods:
  - store_reasoning()     — Validate, analyze, persist, audit
  - get_similar_cases()   — IDIE integration point (Case-Based Reasoning)
"""

import logging

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.decision_intelligence import DecisionCase, ReasoningMemory
from app.models.system import AuditLog
from app.models.users import User
from app.reasoning_engine.reasoning_models import (
    ReasoningStoreRequest,
    ReasoningStoreResponse,
    SimilarCaseResult,
    SimilarCasesResponse,
)
from app.reasoning_engine.reasoning_repository import ReasoningRepository
from app.reasoning_engine.reasoning_analyzer import ReasoningAnalyzer
from app.reasoning_engine.case_matcher import CaseMatcher

logger = logging.getLogger(__name__)

# Module-level matcher instance (default strategy)
_case_matcher = CaseMatcher()


class ReasoningService:
    """Facade for all Reasoning Memory operations."""

    # ── Store Reasoning Record ────────────────────────────────────────────

    @staticmethod
    async def store_reasoning(
        db: AsyncSession,
        user: User,
        payload: ReasoningStoreRequest,
    ) -> ReasoningStoreResponse:
        """
        Full pipeline: validate case → analyze → persist → audit → respond.

        Raises:
            ValueError: If the decision case does not exist.
        """

        # ── 1. Validate the Decision Case exists ─────────────────────────
        stmt = select(DecisionCase).where(DecisionCase.id == payload.decision_case_id)
        result = await db.execute(stmt)
        decision_case = result.scalar_one_or_none()

        if decision_case is None:
            raise ValueError(f"Decision case not found: {payload.decision_case_id}")

        # ── 2. Run Reasoning Analyzer ────────────────────────────────────
        analysis = ReasoningAnalyzer.analyze(
            problem_summary=payload.problem_summary,
            final_recommendation=payload.final_recommendation,
            outcome_status=payload.outcome_status,
            confidence_score=payload.confidence_score,
            reasoning_steps=payload.reasoning_steps,
            success_score=payload.success_score,
            reusable_lesson=payload.reusable_lesson,
        )

        # Use the analyzer's key_lesson if caller didn't provide one
        enriched_lesson = payload.reusable_lesson or analysis.key_lesson

        # ── 3. Persist ReasoningMemory record ────────────────────────────
        record = ReasoningMemory(
            decision_case_id=payload.decision_case_id,
            case_title=payload.case_title,
            problem_summary=payload.problem_summary,
            reasoning_steps=payload.reasoning_steps,
            evidence_used=payload.evidence_used,
            agents_involved=payload.agents_involved,
            final_recommendation=payload.final_recommendation,
            confidence_score=payload.confidence_score,
            outcome_status=payload.outcome_status,
            success_score=payload.success_score,
            reusable_lesson=enriched_lesson,
        )
        record = await ReasoningRepository.create(db, record)

        # ── 4. Write Audit Log ───────────────────────────────────────────
        audit = AuditLog(
            user_id=user.id,
            decision_case_id=payload.decision_case_id,
            action="REASONING_RECORD_CREATED",
            details={
                "reasoning_id": str(record.id),
                "case_title": payload.case_title,
                "outcome_status": payload.outcome_status.value,
                "confidence_score": payload.confidence_score,
                "has_reasoning_steps": payload.reasoning_steps is not None,
                "has_evidence": payload.evidence_used is not None,
                "lesson_auto_generated": payload.reusable_lesson is None,
            },
        )
        db.add(audit)

        # ── 5. Commit & Return ───────────────────────────────────────────
        await db.commit()
        await db.refresh(record)

        logger.info(
            "Reasoning record stored: %s (case=%s, outcome=%s)",
            record.id,
            payload.decision_case_id,
            payload.outcome_status.value,
        )

        return ReasoningStoreResponse(
            reasoning_id=record.id,
            decision_case_id=payload.decision_case_id,
            case_title=payload.case_title,
            message="Reasoning record created and stored.",
        )

    # ── Get Similar Cases (IDIE Integration Point) ────────────────────────

    @staticmethod
    async def get_similar_cases(
        db: AsyncSession,
        query: str,
        limit: int = 5,
    ) -> SimilarCasesResponse:
        """
        Find similar previously-solved cases for a given problem query.

        This is the IDIE integration point — IDIE will consume this method
        to add case-based reasoning evidence alongside RAG and Factory Memory.
        IDIE is NOT modified; it will call this when ready.
        """
        scored_cases = await _case_matcher.find_similar(db, query, limit=limit)

        results = []
        for sc in scored_cases:
            r = sc.record
            results.append(SimilarCaseResult(
                id=r.id,
                decision_case_id=r.decision_case_id,
                case_title=r.case_title,
                problem_summary=r.problem_summary,
                final_recommendation=r.final_recommendation,
                reasoning_steps=r.reasoning_steps,
                evidence_used=r.evidence_used,
                agents_involved=r.agents_involved,
                confidence_score=r.confidence_score,
                outcome_status=r.outcome_status,
                success_score=r.success_score,
                reusable_lesson=r.reusable_lesson,
                similarity_score=round(sc.similarity_score, 4),
                created_at=r.created_at,
            ))

        return SimilarCasesResponse(
            query=query,
            results=results,
            total=len(results),
        )
