"""
INDUS AI — Confidence Service

Orchestrates confidence scoring, explanation generation, database persistence
(both standard confidence scores and history logs), and lookups.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Component imports
from app.idie.evidence_collector import EvidenceCollector, EvidenceBundle
from app.confidence_engine.confidence_calculator import ConfidenceCalculator
from app.confidence_engine.confidence_explainer import ConfidenceExplainer
from app.confidence_engine.confidence_repository import ConfidenceRepository
from app.confidence_engine.confidence_models import (
    ConfidenceResponse,
    ComponentScores,
)

# Models and standard DB records
from app.models.decision_intelligence import DecisionCase, AIResponse, ConfidenceScore

logger = logging.getLogger(__name__)

# Configured calculator instance
_calculator = ConfidenceCalculator()


class ConfidenceService:
    """Service facade centralizing all Confidence Engine logic."""

    @classmethod
    async def calculate_and_persist(
        cls,
        db: AsyncSession,
        decision_case: DecisionCase,
        bundle: EvidenceBundle,
        intent_confidence: float,
    ) -> ConfidenceResponse:
        """
        Calculates confidence components, maps explanations, updates standard
        DB tables, appends to the history log, and returns the response schema.
        """
        case_id = decision_case.id

        # 1. Programmatic calculations
        score, components = _calculator.calculate_overall(bundle, intent_confidence)
        level = ConfidenceExplainer.get_level(score)
        explanation = ConfidenceExplainer.explain(score, components, bundle)

        # 2. Update Standard AIResponse / ConfidenceScore records
        resp_stmt = select(AIResponse).where(AIResponse.decision_case_id == case_id)
        resp_res = await db.execute(resp_stmt)
        ai_resp = resp_res.scalar_one_or_none()

        if ai_resp:
            score_stmt = select(ConfidenceScore).where(ConfidenceScore.ai_response_id == ai_resp.id)
            score_res = await db.execute(score_stmt)
            conf_record = score_res.scalar_one_or_none()

            if conf_record:
                conf_record.score = score
                conf_record.factors = {
                    "fused_level": level,
                    "explanation": explanation,
                    "component_scores": components.model_dump()
                }
            else:
                conf_record = ConfidenceScore(
                    ai_response_id=ai_resp.id,
                    score=score,
                    factors={
                        "fused_level": level,
                        "explanation": explanation,
                        "component_scores": components.model_dump()
                    }
                )
                db.add(conf_record)

        # 3. Create recalculation history log
        await ConfidenceRepository.create_history_record(
            db, case_id, score, level, explanation, components
        )

        logger.info(
            "Confidence recalculated and persisted for case %s: score=%.2f (%s)",
            str(case_id)[:8], score, level
        )

        return ConfidenceResponse(
            score=score,
            level=level,
            explanation=explanation,
            component_scores=components
        )

    @classmethod
    async def get_confidence(
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> ConfidenceResponse:
        """
        Retrieves the latest confidence record.
        If no history exists but the decision case exists, calculates on-the-fly.
        """
        # Attempt retrieval
        latest = await ConfidenceRepository.get_latest(db, decision_case_id)
        if latest:
            comp_dict = latest.component_scores
            return ConfidenceResponse(
                score=latest.score,
                level=latest.level,
                explanation=latest.explanation,
                component_scores=ComponentScores(
                    documents=comp_dict.get("documents", 0.0),
                    factory_memory=comp_dict.get("factory_memory", 0.0),
                    reasoning=comp_dict.get("reasoning", 0.0),
                    graph=comp_dict.get("graph", 0.0),
                    intent=comp_dict.get("intent", 0.0)
                )
            )

        # On-the-fly calculation fallback
        stmt = select(DecisionCase).where(DecisionCase.id == decision_case_id)
        res = await db.execute(stmt)
        case = res.scalar_one_or_none()

        if not case:
            raise ValueError(f"Decision case not found: {decision_case_id}")

        # Gather evidence to run calculation
        bundle = await EvidenceCollector.collect_all(db, case.query, str(case.id))
        
        # Find RAG / Intent details from factors if present
        intent_conf = 0.70
        resp_stmt = select(AIResponse).where(AIResponse.decision_case_id == case.id)
        resp_res = await db.execute(resp_stmt)
        ai_resp = resp_res.scalar_one_or_none()
        if ai_resp:
            score_stmt = select(ConfidenceScore).where(ConfidenceScore.ai_response_id == ai_resp.id)
            score_res = await db.execute(score_stmt)
            conf_record = score_res.scalar_one_or_none()
            if conf_record and conf_record.factors:
                intent_conf = conf_record.factors.get("rag_confidence", 0.70)

        # Calculate and persist
        response = await ConfidenceService.calculate_and_persist(db, case, bundle, intent_conf)
        await db.commit()
        return response
