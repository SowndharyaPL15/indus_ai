from typing import List, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from app.models.documents import Document

async def build_citations(db: AsyncSession, retrieved_chunks: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Build structured citations including document titles by querying the DB.
    """
    citations = []
    seen = set()
    
    for chunk in retrieved_chunks:
        doc_id_str = chunk["metadata"].get("document_id")
        chunk_num = chunk["metadata"].get("chunk_number", -1)
        score = chunk["score"]
        
        sig = f"{doc_id_str}_{chunk_num}"
        if sig in seen:
            continue
        seen.add(sig)
        
        doc_title = "Unknown Document"
        if doc_id_str:
            try:
                res = await db.execute(select(Document.title).where(Document.id == UUID(doc_id_str)))
                title = res.scalar_one_or_none()
                if title:
                    doc_title = title
            except Exception:
                pass
                
        citations.append({
            "document": doc_title,
            "chunk": chunk_num,
            "score": round(score, 4),
            "document_id": doc_id_str or "unknown"
        })
        
    return citations
