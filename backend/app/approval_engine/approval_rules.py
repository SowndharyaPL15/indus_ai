from app.models.users import RoleEnum
from app.models.decision_intelligence import ApprovalRequest
from fastapi import HTTPException, status

def check_can_approve(user_role: RoleEnum, request: ApprovalRequest):
    """
    Validates if a user's role allows them to approve the request based on rules.
    """
    # 1. Auditor can view but cannot approve operational actions
    if user_role == RoleEnum.AUDITOR:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Auditors are read-only and cannot approve actions."
        )

    # 2. Maintenance Engineer cannot approve critical safety decisions
    if request.approver_role == RoleEnum.SAFETY_OFFICER.value and user_role == RoleEnum.MAINTENANCE_ENGINEER:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Maintenance Engineer cannot approve safety decisions."
        )

    # 3. Plant Manager/Admin can approve anything high-risk
    if user_role in (RoleEnum.PLANT_MANAGER, RoleEnum.ADMIN):
        return True

    # 4. Safety Officer can approve safety-related actions
    if user_role == RoleEnum.SAFETY_OFFICER and request.approver_role == RoleEnum.SAFETY_OFFICER.value:
        return True

    # 5. Default mapping matching exact role requested
    if user_role.value != request.approver_role:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"User role {user_role.value} cannot approve. Requires {request.approver_role}."
        )
    return True

def evaluate_approval_rules(has_critical_conflict: bool, confidence: float, compliance_risk: str, safety_risk: str) -> tuple[bool, str, str]:
    """
    Evaluates if a decision case requires human approval based on configurable thresholds.
    Returns: (requires_human_approval, approver_role, risk_level)
    """
    if has_critical_conflict:
        return True, "PLANT_MANAGER", "critical"
        
    if safety_risk.upper() == "HIGH":
        return True, "SAFETY_OFFICER", "critical"
        
    if compliance_risk.upper() == "HIGH":
        return True, "PLANT_MANAGER", "high"
        
    if confidence < 0.70:
        return True, "PLANT_MANAGER", "high"
        
    return False, "ADMIN", "low"

