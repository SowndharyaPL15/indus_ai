from typing import List, Dict, Any

def build_context(retrieved_chunks: List[Dict[str, Any]], max_chars: int = 15000) -> str:
    """
    Merges retrieved chunks, prevents duplicates, respects a token/char limit, 
    and sorts by relevance (which is assumed based on input order).
    """
    seen_contents = set()
    context_parts = []
    current_length = 0
    
    for chunk in retrieved_chunks:
        content = chunk["content"]
        
        if content in seen_contents:
            continue
            
        if current_length + len(content) > max_chars:
            break
            
        seen_contents.add(content)
        context_parts.append(f"[Document ID: {chunk['metadata'].get('document_id', 'Unknown')} | Chunk: {chunk['metadata'].get('chunk_number', 'Unknown')}]\n{content}")
        current_length += len(content)
        
    return "\n\n---\n\n".join(context_parts)
