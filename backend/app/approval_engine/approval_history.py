"""
INDUS AI - Approval History Models

Defines history logging model for approval tracking.
"""
from datetime import datetime, timezone
import uuid
from sqlalchemy import String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import BaseModel as DBBaseModel

class ApprovalHistoryRecord(DBBaseModel):
    """
    Stores full approval history logs.
    Includes reviewer, decision, comment, timestamp, and status tracking.
    """
    __tablename__ = "approval_history"

    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    reviewer_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    decision: Mapped[str] = mapped_column(String, nullable=False)
    comment: Mapped[str | None] = mapped_column(String, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    previous_status: Mapped[str] = mapped_column(String, nullable=False)
    new_status: Mapped[str] = mapped_column(String, nullable=False)
