import time
from sqlalchemy.ext.asyncio import AsyncSession
from langchain_core.prompts import ChatPromptTemplate
from app.rag.retrieval.retriever import retrieve_chunks
from app.rag.retrieval.context_builder import build_context
from app.rag.retrieval.citation_builder import build_citations
from app.rag.llm_service import get_llm
from app.schemas.copilot import QueryResponse, Citation

async def process_query(db: AsyncSession, query: str) -> QueryResponse:
    start_time = time.time()
    
    # 1. Retrieve
    chunks = retrieve_chunks(query, top_k=5, similarity_threshold=0.1)
    
    # 2. Build Context
    context = build_context(chunks)
    
    # 3. Build Citations
    raw_citations = await build_citations(db, chunks)
    citations = [Citation(**c) for c in raw_citations]
    
    # Extract unique document names for the response
    documents_used = list(set([c.document for c in citations]))
    
    # Calculate an aggregate confidence (heuristic)
    confidence = sum(c.score for c in citations) / len(citations) if citations else 0.0
    
    # 4. Invoke LLM
    if context.strip():
        llm = get_llm()
        prompt = ChatPromptTemplate.from_messages([
            ("system", "You are an AI assistant for INDUS AI. Answer the user's question based strictly on the following context. If the answer is not in the context, say 'I cannot answer this based on the provided documents.'\n\nContext:\n{context}"),
            ("human", "{query}")
        ])
        
        chain = prompt | llm
        try:
            response = chain.invoke({"context": context, "query": query})
            answer = response.content
        except Exception as e:
            answer = f"Error generating response from LLM: {str(e)}"
    else:
        answer = "I could not find any relevant information in the factory knowledge base to answer your query."
        confidence = 0.0

    processing_time = f"{time.time() - start_time:.2f}s"
    
    return QueryResponse(
        answer=answer,
        confidence=round(confidence, 2),
        citations=citations,
        documents_used=documents_used,
        processing_time=processing_time
    )
