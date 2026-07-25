import uuid
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Enum
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import BaseModel

class NotificationStatus(str, enum.Enum):
    UNREAD = "UNREAD"
    READ = "READ"

class Notification(BaseModel):
    __tablename__ = "notifications"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    message: Mapped[str] = mapped_column(Text)
    status: Mapped[NotificationStatus] = mapped_column(Enum(NotificationStatus), default=NotificationStatus.UNREAD)

class GeneratedReport(BaseModel):
    __tablename__ = "generated_reports"
    title: Mapped[str] = mapped_column(String)
    file_path: Mapped[str] = mapped_column(String)
    report_type: Mapped[str] = mapped_column(String, default="Decision Case Report")
    generated_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    decision_case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("decision_cases.id"), nullable=True, index=True)


class AuditLog(BaseModel):
    __tablename__ = "audit_logs"
    user_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    decision_case_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("decision_cases.id"), nullable=True, index=True)
    action: Mapped[str] = mapped_column(String, index=True)
    details: Mapped[dict | None] = mapped_column(JSONB, nullable=True)

    decision_case = relationship("DecisionCase", back_populates="audit_logs")
