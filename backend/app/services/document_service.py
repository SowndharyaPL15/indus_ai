import os
import time
import uuid
import logging
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.models.documents import Document, DocumentChunk, DocumentStatusEnum
from app.rag.ingestion.loader_factory import extract_text_from_file
from app.rag.chunking.chunker import chunk_text
from app.rag.vectorstore.faiss_service import add_documents_to_faiss
from app.models.system import AuditLog

logger = logging.getLogger(__name__)

async def process_document_task(db: AsyncSession, doc_id: uuid.UUID):
    """Background task to process a document (extract, chunk, embed)."""
    start_time = time.time()
    
    # Retrieve doc
    result = await db.execute(select(Document).where(Document.id == doc_id))
    doc = result.scalar_one_or_none()
    if not doc:
        logger.error(f"Document {doc_id} not found for processing.")
        return

    doc.status = DocumentStatusEnum.PROCESSING
    await db.commit()
    
    try:
        # 1. Extraction
        doc.progress = 20.0
        await db.commit()
        
        STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage", "documents"))
        file_path = os.path.join(STORAGE_DIR, doc.stored_filename)
        extracted_text = extract_text_from_file(file_path, doc.file_type)
        
        if not extracted_text:
            raise ValueError("Extracted text is empty")
            
        # 2. Chunking
        doc.progress = 50.0
        await db.commit()
        
        chunks = chunk_text(extracted_text)
        
        # 3. Saving chunks to DB
        doc.progress = 60.0
        db_chunks = []
        for i, content in enumerate(chunks):
            chunk = DocumentChunk(document_id=doc.id, content=content, chunk_number=i)
            db.add(chunk)
            db_chunks.append(chunk)
            
        await db.commit()
        
        # 4. Embed and Index to FAISS
        doc.progress = 80.0
        await db.commit()
        
        metadatas = [{"document_id": str(doc.id), "chunk_number": i} for i in range(len(chunks))]
        add_documents_to_faiss(chunks, metadatas)
        
        # 5. Finish
        doc.progress = 100.0
        doc.status = DocumentStatusEnum.READY
        doc.processing_time = time.time() - start_time
        
        # Audit Log
        audit = AuditLog(
            user_id=doc.uploaded_by,
            action="DOCUMENT_PROCESSED",
            details={"document_id": str(doc.id), "title": doc.title, "chunks": len(chunks)}
        )
        db.add(audit)
        await db.commit()

    except Exception as e:
        logger.error(f"Error processing document {doc_id}: {str(e)}")
        doc.status = DocumentStatusEnum.FAILED
        doc.error_message = str(e)
        doc.progress = 0.0
        doc.processing_time = time.time() - start_time
        await db.commit()
