"""
INDUS AI — Factory Memory Record Model

Stores validated engineer feedback from resolved Decision Cases as
organizational knowledge (Living Factory Memory).
"""

import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import Text, Integer, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import BaseModel


class FactoryMemoryRecord(BaseModel):
    """
    Each record captures what an engineer actually did to solve a problem,
    whether the AI recommendation helped, and the practical lesson learned.
    These records serve as additional evidence for future IDIE investigations.
    """
    __tablename__ = "factory_memory_records"

    # ── Foreign Keys ──────────────────────────────────────────────────────
    decision_case_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("decision_cases.id"), index=True
    )
    machine_id: Mapped[uuid.UUID | None] = mapped_column(
        UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True, index=True
    )
    engineer_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True), ForeignKey("users.id"), index=True
    )

    # ── Knowledge Fields ──────────────────────────────────────────────────
    problem: Mapped[str] = mapped_column(Text)
    solution: Mapped[str] = mapped_column(Text)
    lesson: Mapped[str] = mapped_column(Text)
    engineer_feedback: Mapped[str] = mapped_column(Text)

    # ── Quality & Tracking ────────────────────────────────────────────────
    rating: Mapped[int] = mapped_column(Integer, default=0)
    useful: Mapped[bool] = mapped_column(Boolean, default=False)
    validated: Mapped[bool] = mapped_column(Boolean, default=True)
    times_reused: Mapped[int] = mapped_column(Integer, default=0)

    # ── Relationships ─────────────────────────────────────────────────────
    decision_case = relationship("DecisionCase", back_populates="factory_memory_records")
    engineer = relationship("User")
    machine = relationship("Machine")
