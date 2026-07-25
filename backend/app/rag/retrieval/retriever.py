import re
import logging
from typing import List, Dict, Any
from app.rag.vectorstore.faiss_service import get_faiss_index

logger = logging.getLogger(__name__)

ALL_ASSETS = {"P101", "M101", "CP01", "CT01", "B201", "C301", "HX01", "HX02"}

def extract_asset_tag(query: str) -> str | None:
    match = re.search(r'\b(P-?101|M-?101|CP-?01|CT-?01|B-?201|C-?301|HX-?0[12])\b', query, re.IGNORECASE)
    if match:
        return match.group(1).upper().replace('-', '')
    return None

def is_maintenance_issue_query(query: str) -> bool:
    keywords = ["vibration", "maintenance", "issue", "failure", "broken", "leak", "damage", "fault"]
    query_lower = query.lower()
    return any(k in query_lower for k in keywords)

def get_document_type(filename: str) -> str:
    filename_upper = filename.upper()
    if "MLOG" in filename_upper: return "Maintenance Log"
    if "SOP" in filename_upper: return "SOP"
    if "MAN" in filename_upper: return "Manual"
    if "IR-" in filename_upper: return "Incident Report"
    return "Other"

def retrieve_chunks(query: str, top_k: int = 5, similarity_threshold: float = 0.5) -> List[Dict[str, Any]]:
    """
    Search the FAISS vectorstore for relevant chunks.
    Applies entity-aware retrieval ranking.
    """
    vectorstore = get_faiss_index()
    if not vectorstore:
        return []
        
    # We fetch a larger pool to re-rank
    fetch_k = max(top_k * 3, 15)
    results = vectorstore.similarity_search_with_score(query, k=fetch_k)
    
    extracted_asset = extract_asset_tag(query)
    is_maint_query = is_maintenance_issue_query(query)
    
    logger.info(f"RAG Entity Retrieval - extracted_asset: {extracted_asset}")
    
    retrieved_chunks = []
    ranking_breakdown = []
    
    for doc, distance in results:
        # semantic similarity base
        semantic_score = 1.0 / (1.0 + distance)
        
        filename = str(doc.metadata.get("source", ""))
        title = str(doc.metadata.get("title", ""))
        content = doc.page_content
        doc_text = f"{filename} {title} {content}".upper()
        
        asset_match_boost = 0.0
        document_type_boost = 0.0
        unrelated_asset_penalty = 0.0
        
        if extracted_asset:
            # Check for asset match boost
            if extracted_asset in doc_text:
                asset_match_boost = 0.30
                
            # Check for unrelated asset penalty
            for asset in ALL_ASSETS:
                if asset != extracted_asset and asset in doc_text:
                    # Penalize unless the doc strongly mentions the target asset as well
                    if extracted_asset not in filename.upper() and extracted_asset not in title.upper():
                        unrelated_asset_penalty = 0.40
                        break
        
        if is_maint_query:
            doc_type = get_document_type(filename)
            if doc_type in ["Maintenance Log", "SOP", "Manual", "Incident Report"]:
                document_type_boost = 0.15
                
        final_score = semantic_score + asset_match_boost + document_type_boost - unrelated_asset_penalty
        
        # Clamp score between 0.0 and 1.0
        final_score = max(0.0, min(1.0, final_score))
        
        ranking_breakdown.append({
            "filename": filename,
            "semantic": semantic_score,
            "asset_boost": asset_match_boost,
            "doc_boost": document_type_boost,
            "penalty": unrelated_asset_penalty,
            "final": final_score
        })
        
        if final_score >= similarity_threshold:
            retrieved_chunks.append({
                "content": content,
                "metadata": doc.metadata,
                "score": final_score,
                "debug": ranking_breakdown[-1]
            })
            
    # Re-sort chunks
    retrieved_chunks.sort(key=lambda x: x["score"], reverse=True)
    
    # Take top_k
    final_top_chunks = retrieved_chunks[:top_k]
    
    final_top_documents = [c["metadata"].get("source", "") for c in final_top_chunks]
    logger.info(f"RAG Entity Retrieval - ranking_breakdown: {ranking_breakdown}")
    logger.info(f"RAG Entity Retrieval - final_top_documents: {final_top_documents}")
    
    return final_top_chunks
