from datetime import datetime
from uuid import UUID
from pydantic import BaseModel
from app.models.documents import DocumentStatusEnum

class DocumentResponse(BaseModel):
    id: UUID
    title: str
    original_filename: str
    file_type: str
    file_size: int
    status: DocumentStatusEnum
    progress: float
    processing_time: float | None = None
    error_message: str | None = None
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}

class DocumentStatusResponse(BaseModel):
    id: UUID
    status: DocumentStatusEnum
    progress: float
    error_message: str | None = None
    processing_time: float | None = None

    model_config = {"from_attributes": True}
