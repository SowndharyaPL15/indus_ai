from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.system import AuditLog
from app.schemas.copilot import QueryRequest, QueryResponse
from app.rag.retrieval.query_pipeline import process_query

router = APIRouter()

@router.post("/query", response_model=QueryResponse)
async def query_copilot(
    payload: QueryRequest,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    response = await process_query(db, payload.query)
    
    # Audit Logging
    audit = AuditLog(
        user_id=current_user.id,
        action="COPILOT_QUERY",
        details={
            "query": payload.query,
            "response_time": response.processing_time,
            "documents_used": response.documents_used,
            "confidence": response.confidence
        }
    )
    db.add(audit)
    await db.commit()
    
    return response
