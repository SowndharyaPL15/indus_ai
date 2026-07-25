"""
INDUS AI — Confidence Engine Models

Pydantic schemas for the Confidence Engine API, and the
ConfidenceHistory SQLAlchemy model to store recalculation logs.
"""

import uuid
from typing import List
from pydantic import BaseModel, Field

from sqlalchemy import String, Float
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import BaseModel as DBBaseModel


# ── Pydantic Schemas ──────────────────────────────────────────────────────────

class ComponentScores(BaseModel):
    """Programmatic component scores breakdown."""
    documents: float = Field(..., ge=0.0, le=1.0)
    factory_memory: float = Field(..., ge=0.0, le=1.0)
    reasoning: float = Field(..., ge=0.0, le=1.0)
    graph: float = Field(..., ge=0.0, le=1.0)
    intent: float = Field(..., ge=0.0, le=1.0)


class ConfidenceResponse(BaseModel):
    """Confidence Engine analysis response."""
    score: float = Field(..., ge=0.0, le=1.0)
    level: str
    explanation: List[str]
    component_scores: ComponentScores

    model_config = {"from_attributes": True}


# ── SQLAlchemy Model ──────────────────────────────────────────────────────────

class ConfidenceHistory(DBBaseModel):
    """
    Stores recalculation history of decision intelligence confidence scores.
    Each time the engine is queried or updated, a historical log is appended.
    """
    __tablename__ = "confidence_history"

    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), index=True)
    score: Mapped[float] = mapped_column(Float, nullable=False)
    level: Mapped[str] = mapped_column(String, nullable=False)
    
    # Store List[str] explanation as JSONB
    explanation: Mapped[list] = mapped_column(JSONB, nullable=False)
    
    # Store component scores breakdown as JSONB
    component_scores: Mapped[dict] = mapped_column(JSONB, nullable=False)
