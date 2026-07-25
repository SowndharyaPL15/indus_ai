from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.system import AuditLog
from app.idie.models import InvestigateRequest, FusionDecisionResponse
from app.idie.workflow import run_investigation

router = APIRouter()


@router.post("/investigate", response_model=FusionDecisionResponse)
async def investigate_issue(
    payload: InvestigateRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run IDIE v2 Intelligence Fusion Engine pipeline.
    Combines RAG Documents, Factory Memory, Reasoning CBR, and Knowledge Graph.
    """
    response = await run_investigation(db, current_user, payload.query)

    # Log the IDIE v2 Fusion orchestration
    audit = AuditLog(
        user_id=current_user.id,
        action="IDIE_FUSION_INVESTIGATION",
        details={
            "query": payload.query,
            "intent": response.intent,
            "fused_confidence": response.fused_confidence,
            "supporting_documents_count": len(response.supporting_documents),
            "factory_memory_count": len(response.factory_memory),
            "similar_cases_count": len(response.similar_cases),
            "graph_context_count": len(response.graph_context),
            "processing_time": response.processing_time,
            "module_timings": response.module_timings
        }
    )
    db.add(audit)
    await db.commit()

    return response
