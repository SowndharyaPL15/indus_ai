import os
import uuid
import shutil
from typing import List

from fastapi import APIRouter, Depends, UploadFile, File, HTTPException, BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.db.database import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.documents import Document, DocumentStatusEnum
from app.models.system import AuditLog
from app.schemas.document import DocumentResponse, DocumentStatusResponse
from app.services.document_service import process_document_task

router = APIRouter()

STORAGE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "storage", "documents"))

ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50 MB

@router.post("/upload", response_model=List[DocumentResponse])
async def upload_documents(
    background_tasks: BackgroundTasks,
    files: List[UploadFile] = File(...),
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    os.makedirs(STORAGE_DIR, exist_ok=True)
    uploaded_docs = []

    for file in files:
        # Validate extension
        ext = os.path.splitext(file.filename)[1].lower()
        if ext not in ALLOWED_EXTENSIONS:
            raise HTTPException(status_code=400, detail=f"Unsupported file type: {ext}")
            
        # Validate size (simple check by reading content length)
        content = await file.read()
        if len(content) > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail=f"File {file.filename} exceeds 50MB limit")
        await file.seek(0)
        
        # Check duplicate filename for this user
        res = await db.execute(select(Document).where(Document.original_filename == file.filename, Document.uploaded_by == current_user.id))
        if res.scalar_one_or_none():
            raise HTTPException(status_code=400, detail=f"File {file.filename} already exists")

        # Save file
        stored_filename = f"{uuid.uuid4()}{ext}"
        file_path = os.path.join(STORAGE_DIR, stored_filename)
        
        with open(file_path, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
            
        # Create DB record
        doc = Document(
            title=file.filename,
            original_filename=file.filename,
            stored_filename=stored_filename,
            file_type=file.content_type,
            file_size=len(content),
            uploaded_by=current_user.id,
            status=DocumentStatusEnum.UPLOADING
        )
        db.add(doc)
        
        # Audit Log
        audit = AuditLog(
            user_id=current_user.id,
            action="DOCUMENT_UPLOADED",
            details={"original_filename": file.filename}
        )
        db.add(audit)
        
        await db.commit()
        await db.refresh(doc)
        uploaded_docs.append(doc)
        
        # Queue processing
        background_tasks.add_task(process_document_task, db, doc.id)
        
    return uploaded_docs

@router.get("/", response_model=List[DocumentResponse])
async def list_documents(db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Document))
    return res.scalars().all()

@router.get("/{id}", response_model=DocumentResponse)
async def get_document(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Document).where(Document.id == id))
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.get("/status/{id}", response_model=DocumentStatusResponse)
async def get_document_status(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Document).where(Document.id == id))
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
    return doc

@router.delete("/{id}")
async def delete_document(id: uuid.UUID, db: AsyncSession = Depends(get_db), current_user: User = Depends(get_current_user)):
    res = await db.execute(select(Document).where(Document.id == id))
    doc = res.scalar_one_or_none()
    if not doc:
        raise HTTPException(status_code=404, detail="Document not found")
        
    file_path = os.path.join(STORAGE_DIR, doc.stored_filename)
    if os.path.exists(file_path):
        os.remove(file_path)
        
    await db.delete(doc)
    
    audit = AuditLog(
        user_id=current_user.id,
        action="DOCUMENT_DELETED",
        details={"document_id": str(id), "original_filename": doc.original_filename}
    )
    db.add(audit)
    
    await db.commit()
    return {"message": "Document deleted"}
