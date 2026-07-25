from app.idie.models import DecisionCaseResponse
from app.schemas.copilot import QueryResponse
from app.idie.models import IntentResult

def format_response(
    case_id: str,
    query: str,
    intent_result: IntentResult,
    rag_response: QueryResponse,
    total_time: str
) -> DecisionCaseResponse:
    title = f"{intent_result.intent.capitalize()} Investigation"
    
    return DecisionCaseResponse(
        case_id=case_id,
        title=title,
        intent=intent_result.intent,
        summary=rag_response.answer, # Reusing RAG answer as summary for now
        recommendation=rag_response.answer, # Reusing RAG answer as recommendation for now
        confidence=rag_response.confidence,
        documents_used=rag_response.documents_used,
        citations=rag_response.citations,
        processing_time=total_time
    )
