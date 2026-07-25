"""
INDUS AI — Conflict Detector

Applies rule-based heuristics across documents, SOPs, factory memories, CBR,
compliance rules, and maintenance logs to detect contradictions and severities.
"""

import logging
from datetime import datetime, timezone, timedelta
from typing import List, Optional
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Model imports for contextual queries
from app.models.operations import InspectionReport
from app.idie.evidence_collector import EvidenceBundle
from app.conflict_engine.conflict_models import ConflictItem

logger = logging.getLogger(__name__)


class ConflictDetector:
    """Core detection engine applying programmatic business logic rules for anomalies."""

    @classmethod
    async def detect(
        cls,
        db: AsyncSession,
        bundle: EvidenceBundle,
        current_recommendation: str,
        machine_id: Optional[UUID] = None,
    ) -> List[ConflictItem]:
        """
        Runs all conflict detection rules.
        Isolates execution steps so an error in one query doesn't break others.
        """
        conflicts: List[ConflictItem] = []

        # 1. DOCUMENT_CONFLICT
        try:
            doc_conf = cls._detect_document_conflicts(bundle, current_recommendation)
            if doc_conf:
                conflicts.append(doc_conf)
        except Exception as e:
            logger.error("Error in document conflict rule: %s", str(e))

        # 2. SOP_CONFLICT
        try:
            sop_conf = cls._detect_sop_conflicts(bundle)
            if sop_conf:
                conflicts.append(sop_conf)
        except Exception as e:
            logger.error("Error in SOP conflict rule: %s", str(e))

        # 3. ENGINEER_CONFLICT
        try:
            eng_conf = cls._detect_engineer_conflicts(bundle)
            if eng_conf:
                conflicts.append(eng_conf)
        except Exception as e:
            logger.error("Error in engineer conflict rule: %s", str(e))

        # 4. REASONING_CONFLICT
        try:
            reason_conf = cls._detect_reasoning_conflicts(bundle, current_recommendation)
            if reason_conf:
                conflicts.append(reason_conf)
        except Exception as e:
            logger.error("Error in reasoning conflict rule: %s", str(e))

        # 5. COMPLIANCE_CONFLICT
        try:
            comp_conf = await cls._detect_compliance_conflicts(db, bundle, machine_id)
            if comp_conf:
                conflicts.append(comp_conf)
        except Exception as e:
            logger.error("Error in compliance conflict rule: %s", str(e))

        # 6. MISSING_EVIDENCE
        try:
            miss_conf = cls._detect_missing_evidence(bundle)
            if miss_conf:
                conflicts.append(miss_conf)
        except Exception as e:
            logger.error("Error in missing evidence rule: %s", str(e))

        logger.info(
            "Conflict detection complete for case %s: %d conflicts identified",
            bundle.decision_case_id[:8], len(conflicts)
        )
        return conflicts

    # ── Rule 1: Document Conflict ─────────────────────────────────────────

    @staticmethod
    def _detect_document_conflicts(bundle: EvidenceBundle, recommendation: str) -> Optional[ConflictItem]:
        """Detects contradictions between RAG answers/manuals and engineer memory records."""
        if not bundle.factory_memories:
            return None

        # Compare recommendation/manual keywords against memories
        rec_lower = recommendation.lower()
        has_replace = "replace" in rec_lower or "install new" in rec_lower
        
        recal_solutions = []
        sources = []
        for mem in bundle.factory_memories:
            sol_lower = mem.solution.lower()
            if "recalibrate" in sol_lower or "adjust" in sol_lower or "lubricat" in sol_lower:
                recal_solutions.append(mem.solution)
                sources.append(str(mem.id))

        if has_replace and recal_solutions:
            return ConflictItem(
                type="DOCUMENT_CONFLICT",
                severity="HIGH",
                description=(
                    f"Official document/manual suggests parts replacement. However, "
                    f"{len(recal_solutions)} engineer memories solved this via calibration/maintenance."
                ),
                sources=sources
            )
        return None

    # ── Rule 2: SOP Conflict ──────────────────────────────────────────────

    @staticmethod
    def _detect_sop_conflicts(bundle: EvidenceBundle) -> Optional[ConflictItem]:
        """Detects contradictions between machine SOP titles and engineer memory solutions."""
        if not bundle.factory_memories:
            return None

        # Filter SOP nodes from graph context
        sop_entities = [g for g in bundle.graph_context if g.entity_type == "SOP"]
        if not sop_entities:
            return None

        mismatches = []
        sources = []
        for ent in sop_entities:
            sop_title = ent.properties.get("title", "").lower() if ent.properties else ""
            if not sop_title:
                continue

            for mem in bundle.factory_memories:
                sol_lower = mem.solution.lower()
                # If SOP recommends replacement but solution is recalibration
                if "replace" in sop_title and ("recalibrate" in sol_lower or "cleaning" in sol_lower):
                    mismatches.append(f"SOP title: '{ent.properties.get('title')}' vs Memory: '{mem.solution[:50]}...'")
                    sources.extend([ent.entity_id, str(mem.id)])

        if mismatches:
            return ConflictItem(
                type="SOP_CONFLICT",
                severity="MEDIUM",
                description="Contradiction between machine SOP requirements and past field solutions.",
                sources=list(set(sources))
            )
        return None

    # ── Rule 3: Engineer Conflict ─────────────────────────────────────────

    @staticmethod
    def _detect_engineer_conflicts(bundle: EvidenceBundle) -> Optional[ConflictItem]:
        """Detects contradictions between multiple engineer memory records."""
        if len(bundle.factory_memories) < 2:
            return None

        solutions = [m.solution.lower() for m in bundle.factory_memories]
        
        has_replace = any("replace" in s or "swap" in s for s in solutions)
        has_adjust = any("recalibrate" in s or "adjust" in s or "clean" in s for s in solutions)

        if has_replace and has_adjust:
            sources = [str(m.id) for m in bundle.factory_memories]
            return ConflictItem(
                type="ENGINEER_CONFLICT",
                severity="HIGH",
                description="Plant engineers reported contradictory solutions (parts replacement vs adjustment) for this issue.",
                sources=sources
            )
        return None

    # ── Rule 4: Reasoning Conflict ────────────────────────────────────────

    @staticmethod
    def _detect_reasoning_conflicts(bundle: EvidenceBundle, recommendation: str) -> Optional[ConflictItem]:
        """Detects if a similar past case failed, but the current recommendation is identical."""
        if not bundle.reasoning_cases:
            return None

        rec_lower = recommendation.lower()
        failed_cases = [c for c in bundle.reasoning_cases if c.outcome_status in ["FAILED", "PARTIALLY_SUCCESSFUL"]]

        matches = []
        sources = []
        for case in failed_cases:
            past_rec = case.final_recommendation.lower()
            # Check key action overlap (e.g. check if both contain bearing/spindle/seal and replace/clean/calibrate keywords)
            keywords = ["replace", "recalibrate", "spindle", "bearing", "seal", "sensor", "lubricat"]
            match_count = sum(1 for kw in keywords if kw in rec_lower and kw in past_rec)
            
            if match_count >= 3:
                matches.append(case.case_title)
                sources.append(str(case.decision_case_id))

        if matches:
            return ConflictItem(
                type="REASONING_CONFLICT",
                severity="CRITICAL",
                description=(
                    f"The current recommendation matches the action taken in historical case failures: "
                    f"'{', '.join(matches[:2])}'."
                ),
                sources=sources
            )
        return None

    # ── Rule 5: Compliance Conflict ───────────────────────────────────────

    @classmethod
    async def _detect_compliance_conflicts(
        cls,
        db: AsyncSession,
        bundle: EvidenceBundle,
        machine_id: Optional[UUID],
    ) -> Optional[ConflictItem]:
        """Checks if machine inspection/maintenance schedule violates compliance rules."""
        if not machine_id:
            return None

        # Check if query or context touches safety/compliance rules
        has_compliance = any(
            g.entity_type == "COMPLIANCE_RULE" for g in bundle.graph_context
        ) or any(
            k in bundle.query.lower() for k in ["safe", "safety", "comply", "compliance", "inspection", "audit"]
        )

        if not has_compliance:
            return None

        # Fetch last inspection report for this machine
        stmt = (
            select(InspectionReport)
            .where(InspectionReport.machine_id == machine_id)
            .order_by(InspectionReport.created_at.desc())
            .limit(1)
        )
        res = await db.execute(stmt)
        last_inspection = res.scalar_one_or_none()

        violation = False
        description = ""
        sources = []

        now = datetime.now(timezone.utc)
        if last_inspection:
            # Inspection date check (e.g., check if last inspection is older than 30 days)
            age = now - last_inspection.created_at
            if age > timedelta(days=30):
                violation = True
                description = f"Last safety inspection was performed {age.days} days ago, exceeding the 30-day compliance rule."
                sources.append(str(last_inspection.id))
        else:
            # Missing inspection record entirely
            violation = True
            description = "No safety inspection records found in database for this machine asset."

        if violation:
            # Find rule reference from graph if available
            rules = [g.entity_id for g in bundle.graph_context if g.entity_type == "COMPLIANCE_RULE"]
            sources.extend(rules)

            return ConflictItem(
                type="COMPLIANCE_CONFLICT",
                severity="HIGH",
                description=description,
                sources=list(set(sources))
            )
        return None

    # ── Rule 6: Missing Evidence ──────────────────────────────────────────

    @staticmethod
    def _detect_missing_evidence(bundle: EvidenceBundle) -> Optional[ConflictItem]:
        """Flag missing evidence for high-severity safety or incident queries."""
        has_critical_intent = any(
            k in bundle.query.lower() for k in ["safety", "hazard", "spill", "accident", "emergency", "comply"]
        )

        if has_critical_intent and len(bundle.documents) == 0 and len(bundle.factory_memories) == 0:
            return ConflictItem(
                type="MISSING_EVIDENCE",
                severity="HIGH",
                description="Zero manuals or validated engineer solutions retrieved for this safety-critical query.",
                sources=[]
            )
        return None
