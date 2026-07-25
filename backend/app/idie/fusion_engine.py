"""
INDUS AI — IDIE v2 Intelligence Fusion Engine

The central coordinator that orchestrates the cognitive fusion workflow:
1. Intent Detection
2. Initial RAG pipeline retrieval
3. Create & Persist Decision Case in DB
4. Gather Evidence (RAG, Factory Memory, Reasoning, Knowledge Graph) in parallel-safe steps
5. Score and weight evidence to compute fused confidence
6. Synthesize the context into decision components (summary, risks, actions)
7. Build structured recommendation
8. Update Decision Case & AI Response in DB
9. Trigger Knowledge Graph edge construction for the new case
10. Return unified FusionDecisionResponse
"""

import time
import logging
from typing import Dict

from sqlalchemy import select, cast, String
from sqlalchemy.ext.asyncio import AsyncSession

# IDIE components
from app.idie.intent_detector import detect_intent
from app.rag.retrieval.query_pipeline import process_query
from app.idie.decision_case_builder import build_and_persist_decision_case
from app.idie.evidence_collector import EvidenceCollector, EvidenceBundle
from app.idie.decision_synthesizer import DecisionSynthesizer
from app.idie.recommendation_builder import RecommendationBuilder
from app.confidence_engine.confidence_service import ConfidenceService
from app.conflict_engine.conflict_service import ConflictService

# Models and schemas
from app.models.users import User
from app.approval_engine.approval_service import ApprovalService
from app.approval_engine.approval_models import ApprovalRequestCreate
from app.approval_engine.approval_rules import evaluate_approval_rules

from app.models.decision_intelligence import DecisionCase, AIResponse
from app.idie.models import (
    FusionDecisionResponse,
    FactoryMemoryResponseItem,
    SimilarCaseResponseItem,
    GraphContextResponseItem,
)
from app.knowledge_graph.graph_service import GraphService

logger = logging.getLogger(__name__)


class FusionEngine:
    """Orchestrates IDIE v2 Fusion workflow."""

    @classmethod
    async def run_fusion_investigation(
        cls,
        db: AsyncSession,
        user: User,
        query: str,
    ) -> FusionDecisionResponse:
        """Runs the intelligence fusion pipeline and returns the structured response."""
        start_overall = time.time()
        timings: Dict[str, float] = {}

        # ── 1. Intent Detection ───────────────────────────────────────────────
        t_start = time.time()
        intent_result = detect_intent(query)
        timings["intent_detection"] = time.time() - t_start

        # ── 2. Run Initial RAG (required by legacy builder signature) ─────────
        t_start = time.time()
        initial_rag = await process_query(db, query)
        timings["initial_rag"] = time.time() - t_start

        # ── 3. Build & Persist Decision Case ──────────────────────────────────
        t_start = time.time()
        formatted_case_id = await build_and_persist_decision_case(
            db, user, query, intent_result, initial_rag
        )
        timings["persist_case"] = time.time() - t_start

        # ── 4. Retrieve Case Object to get internal UUID ──────────────────────
        # Extract the last part of formatted case ID (DC-YYYY-UUID_PREFIX)
        uuid_prefix = formatted_case_id.split("-")[-1].lower()
        stmt = select(DecisionCase).where(cast(DecisionCase.id, String).ilike(f"{uuid_prefix}%"))
        result = await db.execute(stmt)
        decision_case = result.scalar_one_or_none()

        if not decision_case:
            raise ValueError(f"Failed to retrieve persisted case with prefix {uuid_prefix}")

        case_uuid_str = str(decision_case.id)

        # ── 5. Evidence Collection ────────────────────────────────────────────
        t_start = time.time()
        bundle: EvidenceBundle = await EvidenceCollector.collect_all(db, query, case_uuid_str)
        # Inherit the RAG timing if collector re-ran RAG, otherwise add timing
        for k, v in bundle.processing_times.items():
            timings[f"collect_{k}"] = v
        timings["evidence_collection"] = time.time() - t_start

        # ── 6. Programmatic Confidence Calculation ────────────────────────────
        t_start = time.time()
        confidence_res = await ConfidenceService.calculate_and_persist(
            db, decision_case, bundle, intent_result.confidence
        )
        fused_confidence = confidence_res.score
        timings["confidence_calculation"] = time.time() - t_start

        # ── 7. Decision Synthesis ─────────────────────────────────────────────
        t_start = time.time()
        decision = await DecisionSynthesizer.synthesize(bundle)
        timings["synthesis"] = time.time() - t_start

        # ── 8. Recommendation Building ────────────────────────────────────────
        t_start = time.time()
        rec = RecommendationBuilder.build(bundle, decision)
        timings["recommendation_building"] = time.time() - t_start

        # ── 9. Update Decision Case & AI Response in DB ───────────────────────
        t_start = time.time()
        # Find AIResponse and update response_text with immediate actions
        resp_stmt = select(AIResponse).where(AIResponse.decision_case_id == decision_case.id)
        resp_result = await db.execute(resp_stmt)
        ai_response = resp_result.scalar_one_or_none()

        if ai_response:
            ai_response.response_text = rec.immediate_actions

        # ── 9.5 Programmatic Conflict Detection ───────────────────────────────
        t_start = time.time()
        has_critical_conflict = False
        try:
            conflict_res = await ConflictService.detect_conflicts(
                db, decision_case, bundle, rec.immediate_actions
            )
            if conflict_res.overall_severity == "CRITICAL":
                has_critical_conflict = True
        except Exception as e:
            logger.error("Failed to run conflict detection for case %s: %s", case_uuid_str, str(e))
        timings["conflict_detection"] = time.time() - t_start

        # ── 10. Graph Edge Construction ───────────────────────────────────────
        # Build the graph node and automatically link relations
        try:
            await GraphService.build_for_decision_case(db, decision_case)
        except Exception as e:
            logger.error("Failed to build Knowledge Graph links for case %s: %s", case_uuid_str, str(e))

        await db.commit()
        timings["db_update_and_graph"] = time.time() - t_start

        # ── 11. Format Response ───────────────────────────────────────────────
        total_time = time.time() - start_overall
        timings["total_overall"] = total_time

        # Map to final schemas
        factory_memories = [
            FactoryMemoryResponseItem(
                id=str(m.id),
                decision_case_id=str(m.decision_case_id),
                problem=m.problem,
                solution=m.solution,
                lesson=m.lesson,
                rating=m.rating,
                useful=m.useful,
            )
            for m in bundle.factory_memories
        ]

        similar_cases = [
            SimilarCaseResponseItem(
                id=str(c.id),
                decision_case_id=str(c.decision_case_id),
                case_title=c.case_title,
                problem_summary=c.problem_summary,
                final_recommendation=c.final_recommendation,
                outcome_status=c.outcome_status.value if hasattr(c.outcome_status, 'value') else str(c.outcome_status),
                reusable_lesson=c.reusable_lesson,
                similarity_score=c.similarity_score,
            )
            for c in bundle.reasoning_cases
        ]

        graph_context = [
            GraphContextResponseItem(
                entity_id=ent.entity_id,
                entity_type=ent.entity_type.value,
                relationship_type=ent.relationship_type.value,
                direction=ent.direction,
                depth=ent.depth,
                properties=ent.properties,
            )
            for ent in bundle.graph_context
        ]

        # Log orchestration details
        logger.info(
            "IDIE v2 Fusion Investigation successfully completed. "
            "Case ID: %s, Fused Confidence: %.2f, Total Time: %.2fs",
            formatted_case_id, fused_confidence, total_time
        )

        # ── Approval Workflow Hook ──────────────────────────────────────────
        intent_str = intent_result.intent.lower()
        compliance_risk = "HIGH" if intent_str == "compliance" else "LOW"
        safety_risk = "HIGH" if intent_str == "safety" else "LOW"

        requires_human_approval, approver_role, risk_level = evaluate_approval_rules(
            has_critical_conflict=has_critical_conflict,
            confidence=fused_confidence,
            compliance_risk=compliance_risk,
            safety_risk=safety_risk
        )
            
        if requires_human_approval:
            approval_svc = ApprovalService(db)
            await approval_svc.create_request(ApprovalRequestCreate(
                decision_case_id=decision_case.id,
                requested_by=user.id,
                approver_role=approver_role,
                reason=f"Auto-generated approval for intent {intent_result.intent} with confidence {fused_confidence:.2f}",
                risk_level=risk_level,
                recommendation_summary=rec.immediate_actions
            ))
        # ──────────────────────────────────────────────────────────────────


        return FusionDecisionResponse(
            case_id=case_uuid_str,
            intent=intent_result.intent,
            decision_summary=decision.decision_summary,
            recommended_action=rec.immediate_actions,
            root_cause=rec.root_cause,
            supporting_documents=rec.supporting_evidence,
            factory_memory=factory_memories,
            similar_cases=similar_cases,
            graph_context=graph_context,
            processing_time=f"{total_time:.2f}s",
            fused_confidence=fused_confidence,
            module_timings={k: f"{v:.3f}s" for k, v in timings.items()},
            requires_human_approval=requires_human_approval,
            approval_status="PENDING" if requires_human_approval else None,
            recommended_reviewer=approver_role if requires_human_approval else None,
        )
