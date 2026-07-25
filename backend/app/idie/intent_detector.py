from app.idie.models import IntentResult

def detect_intent(query: str) -> IntentResult:
    query_lower = query.lower()
    
    # Rule-based heuristics
    if any(k in query_lower for k in ["maintain", "maintenance", "vibration", "fix", "repair", "broken", "temperature high"]):
        return IntentResult(intent="MAINTENANCE", confidence=0.85)
    elif any(k in query_lower for k in ["safe", "safety", "hazard", "risk", "injury", "ppe"]):
        return IntentResult(intent="SAFETY", confidence=0.88)
    elif any(k in query_lower for k in ["comply", "compliance", "regulation", "iso", "standard", "audit"]):
        return IntentResult(intent="COMPLIANCE", confidence=0.90)
    elif any(k in query_lower for k in ["incident", "accident", "spill", "fire", "emergency"]):
        return IntentResult(intent="INCIDENT", confidence=0.92)
    elif any(k in query_lower for k in ["report", "summary", "stats", "statistics", "metric"]):
        return IntentResult(intent="REPORT", confidence=0.80)
    elif any(k in query_lower for k in ["search", "find", "document", "manual", "guide", "sop"]):
        return IntentResult(intent="DOCUMENT_SEARCH", confidence=0.75)
    else:
        return IntentResult(intent="GENERAL", confidence=0.50)
