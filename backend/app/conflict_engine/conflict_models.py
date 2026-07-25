"""
INDUS AI — Conflict Detection Engine Models

Pydantic schemas for conflict details, and the ConflictHistory
SQLAlchemy model to persist execution logs and resolution states.
"""

import uuid
from typing import List
from datetime import datetime
from pydantic import BaseModel, Field

from sqlalchemy import String, Boolean, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import BaseModel as DBBaseModel


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class ConflictItem(BaseModel):
    """Details of a single detected conflict."""
    type: str = Field(..., description="Conflict type (e.g., ENGINEER_CONFLICT)")
    severity: str = Field(..., description="Severity level (e.g., HIGH, CRITICAL)")
    description: str = Field(..., description="Human-readable explanation of the mismatch")
    sources: List[str] = Field(default_factory=list, description="IDs or references of contributing entities")


class ConflictResponse(BaseModel):
    """Summary of all conflicts discovered for a Decision Case."""
    has_conflicts: bool
    overall_severity: str
    conflicts: List[ConflictItem]

    model_config = {"from_attributes": True}


# ── SQLAlchemy Model ──────────────────────────────────────────────────────────

class ConflictHistory(DBBaseModel):
    """
    Stores full conflict evaluation history logs.
    Includes resolution states when plant staff manually approve/reconcile cases.
    """
    __tablename__ = "conflict_history"

    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    has_conflicts: Mapped[bool] = mapped_column(Boolean, default=False)
    overall_severity: Mapped[str] = mapped_column(String, default="LOW")
    
    # Store List[ConflictItem] as JSONB
    conflicts: Mapped[list] = mapped_column(JSONB, nullable=False)
    
    # Resolution Status
    resolved: Mapped[bool] = mapped_column(Boolean, default=False)
    resolved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), nullable=True)
    resolved_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
