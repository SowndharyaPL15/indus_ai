import uuid
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Integer, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import BaseModel

class DocumentStatusEnum(str, enum.Enum):
    UPLOADING = "UPLOADING"
    PROCESSING = "PROCESSING"
    READY = "READY"
    FAILED = "FAILED"

class Document(BaseModel):
    __tablename__ = "documents"
    title: Mapped[str] = mapped_column(String, index=True)
    original_filename: Mapped[str] = mapped_column(String)
    stored_filename: Mapped[str] = mapped_column(String, unique=True)
    file_type: Mapped[str] = mapped_column(String)
    file_size: Mapped[int] = mapped_column(Integer)
    uploaded_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    status: Mapped[DocumentStatusEnum] = mapped_column(Enum(DocumentStatusEnum), default=DocumentStatusEnum.UPLOADING)
    progress: Mapped[float] = mapped_column(Float, default=0.0)
    processing_time: Mapped[float | None] = mapped_column(Float, nullable=True)
    error_message: Mapped[str | None] = mapped_column(Text, nullable=True)
    source_url: Mapped[str | None] = mapped_column(String, nullable=True)
    metadata_json: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    chunks = relationship("DocumentChunk", back_populates="document", cascade="all, delete-orphan")
    uploader = relationship("User", foreign_keys=[uploaded_by])

class DocumentChunk(BaseModel):
    __tablename__ = "document_chunks"
    document_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), index=True)
    content: Mapped[str] = mapped_column(Text)
    chunk_number: Mapped[int] = mapped_column(Integer)
    
    document = relationship("Document", back_populates="chunks")
