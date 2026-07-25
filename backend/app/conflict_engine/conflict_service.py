"""
INDUS AI — Conflict Service

Orchestrates conflict detection logic, updates case status to WAITING_APPROVAL
on critical errors, manages approval request generation, maps explanations,
creates standard ConflictLogs, and handles resolution procedures.
"""

import logging
from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

# Component imports
from app.idie.evidence_collector import EvidenceBundle
from app.conflict_engine.conflict_detector import ConflictDetector
from app.conflict_engine.conflict_repository import ConflictRepository
from app.conflict_engine.conflict_models import ConflictResponse, ConflictItem

# Models and standard DB records
from app.models.users import User, RoleEnum
from app.models.system import AuditLog
from app.models.decision_intelligence import (
    DecisionCase,
    ConflictLog,
    ApprovalRequest,
    CaseStatusEnum,
    ApprovalStatusEnum,
)

logger = logging.getLogger(__name__)


class ConflictService:
    """Service facade centralizing conflict audits, checks, and resolutions."""

    @classmethod
    async def detect_conflicts(
        cls,
        db: AsyncSession,
        decision_case: DecisionCase,
        bundle: EvidenceBundle,
        current_recommendation: str,
    ) -> ConflictResponse:
        """
        Runs programmatic detection rules, logs standard tables, creates history logs,
        escalates to human approval on CRITICAL, and returns the response schema.
        """
        case_id = decision_case.id

        # 1. Run detection rules
        conflicts = await ConflictDetector.detect(
            db, bundle, current_recommendation, decision_case.machine_id
        )

        has_conflicts = len(conflicts) > 0
        overall_severity = "LOW"
        if has_conflicts:
            # Map highest severity
            severities = [c.severity for c in conflicts]
            if "CRITICAL" in severities:
                overall_severity = "CRITICAL"
            elif "HIGH" in severities:
                overall_severity = "HIGH"
            elif "MEDIUM" in severities:
                overall_severity = "MEDIUM"

        # 2. Write standard ConflictLogs
        for conf in conflicts:
            standard_log = ConflictLog(
                decision_case_id=case_id,
                description=f"[{conf.type}] {conf.description}",
                resolved=False
            )
            db.add(standard_log)

        # 3. Create conflict history record
        history_record = await ConflictRepository.create_history_record(
            db, case_id, has_conflicts, overall_severity, conflicts
        )

        # 4. Handle CRITICAL escalations (mandatory human approval workflow)
        if overall_severity == "CRITICAL":
            # Set case status to WAITING_APPROVAL
            decision_case.status = CaseStatusEnum.WAITING_APPROVAL
            logger.warning(
                "Decision Case %s status set to WAITING_APPROVAL due to CRITICAL conflict",
                str(case_id)[:8]
            )

            # Find a default approver (Plant Manager, Admin, or first user in DB)
            approver_id = decision_case.user_id  # Fallback to the case owner
            try:
                user_stmt = select(User).where(User.role.in_([RoleEnum.PLANT_MANAGER, RoleEnum.ADMIN])).limit(1)
                user_res = await db.execute(user_stmt)
                user_record = user_res.scalar_one_or_none()
                if user_record:
                    approver_id = user_record.id
            except Exception as e:
                logger.error("Error looking up default approver: %s", str(e))

            # Create standard ApprovalRequest record
            approval_request = ApprovalRequest(
                decision_case_id=case_id,
                approver_id=approver_id,
                status=ApprovalStatusEnum.PENDING,
                comments=f"Auto-escalated by IDIE Fusion Engine. Detected conflicts: {len(conflicts)}"
            )
            db.add(approval_request)

        # 5. Create Audit Log record
        audit = AuditLog(
            decision_case_id=case_id,
            action="CONFLICT_DETECTION_EXECUTED",
            details={
                "has_conflicts": has_conflicts,
                "overall_severity": overall_severity,
                "conflicts_count": len(conflicts),
                "types": [c.type for c in conflicts]
            }
        )
        db.add(audit)

        return ConflictResponse(
            has_conflicts=has_conflicts,
            overall_severity=overall_severity,
            conflicts=conflicts
        )

    @classmethod
    async def get_conflicts(
        cls,
        db: AsyncSession,
        decision_case_id: UUID,
    ) -> ConflictResponse:
        """Fetch the most recent conflict response evaluation for a case."""
        latest = await ConflictRepository.get_latest(db, decision_case_id)
        if not latest:
            # Return empty response if no checks were run yet
            return ConflictResponse(
                has_conflicts=False,
                overall_severity="LOW",
                conflicts=[]
            )

        conflicts = [
            ConflictItem(
                type=c.get("type", "UNKNOWN"),
                severity=c.get("severity", "LOW"),
                description=c.get("description", ""),
                sources=c.get("sources", [])
            )
            for c in latest.conflicts
        ]

        return ConflictResponse(
            has_conflicts=latest.has_conflicts,
            overall_severity=latest.overall_severity,
            conflicts=conflicts
        )

    @classmethod
    async def resolve(
        cls,
        db: AsyncSession,
        decision_case_id: UUID,
        user: User,
    ) -> bool:
        """
        Manually resolves all conflicts for a decision case.
        Updates Case status back to IN_PROGRESS, approves requests, and logs audit.
        """
        # 1. Update status fields via Repository
        resolved = await ConflictRepository.resolve_conflicts(db, decision_case_id, user.id)

        if not resolved:
            return False

        # 2. Update standard DecisionCase status
        stmt_case = select(DecisionCase).where(DecisionCase.id == decision_case_id)
        res_case = await db.execute(stmt_case)
        case = res_case.scalar_one_or_none()
        
        if case and case.status == CaseStatusEnum.WAITING_APPROVAL:
            case.status = CaseStatusEnum.IN_PROGRESS

        # 3. Approve standard ApprovalRequests
        stmt_appr = select(ApprovalRequest).where(
            and_(
                ApprovalRequest.decision_case_id == decision_case_id,
                ApprovalRequest.status == ApprovalStatusEnum.PENDING
            )
        )
        res_appr = await db.execute(stmt_appr)
        requests = res_appr.scalars().all()
        for req in requests:
            req.status = ApprovalStatusEnum.APPROVED
            req.comments = f"Resolved manually by {user.name} ({user.role.value})"

        # 4. Write Audit Log
        audit = AuditLog(
            user_id=user.id,
            decision_case_id=decision_case_id,
            action="CONFLICTS_RESOLVED",
            details={
                "resolved_by": user.name,
                "resolved_by_role": user.role.value
            }
        )
        db.add(audit)
        await db.commit()

        logger.info(
            "Conflict resolution fully persisted for case %s by user %s",
            str(decision_case_id)[:8], user.name
        )
        return True
