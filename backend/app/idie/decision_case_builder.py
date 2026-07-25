from sqlalchemy.ext.asyncio import AsyncSession
from app.models.decision_intelligence import DecisionCase, AIResponse, ConfidenceScore, CaseStatusEnum
from app.schemas.copilot import QueryResponse
from app.idie.models import IntentResult
from app.models.users import User

async def build_and_persist_decision_case(
    db: AsyncSession, 
    user: User,
    query: str, 
    intent_result: IntentResult, 
    rag_response: QueryResponse
) -> str:
    # Generate custom title based on query
    title = f"{intent_result.intent.capitalize()} Investigation: {query[:30]}..."
    
    # 1. Create DecisionCase record
    db_case = DecisionCase(
        user_id=user.id,
        query=query,
        status=CaseStatusEnum.OPEN
    )
    db.add(db_case)
    await db.commit()
    await db.refresh(db_case)
    
    # 2. Create AIResponse record
    # We serialize the summary and recommendation into the response text, or just store the raw answer
    db_response = AIResponse(
        decision_case_id=db_case.id,
        response_text=rag_response.answer
    )
    db.add(db_response)
    await db.commit()
    await db.refresh(db_response)
    
    # 3. Create ConfidenceScore record
    db_score = ConfidenceScore(
        ai_response_id=db_response.id,
        score=rag_response.confidence,
        factors={"intent": intent_result.intent, "rag_confidence": rag_response.confidence}
    )
    db.add(db_score)
    await db.commit()
    
    # Return formatted case ID (DC-YYYY-UUID_PREFIX)
    import datetime
    year = datetime.datetime.now().year
    uuid_prefix = str(db_case.id).split("-")[0].upper()
    return f"DC-{year}-{uuid_prefix}"
