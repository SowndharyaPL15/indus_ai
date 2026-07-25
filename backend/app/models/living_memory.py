import uuid
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Text, ForeignKey
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import BaseModel

class EngineerInsight(BaseModel):
    __tablename__ = "engineer_insights"
    engineer_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    machine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True, index=True)
    insight_text: Mapped[str] = mapped_column(Text)

class FactoryMemory(BaseModel):
    __tablename__ = "factory_memory"
    event_type: Mapped[str] = mapped_column(String, index=True)
    context_data: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    description: Mapped[str] = mapped_column(Text)
