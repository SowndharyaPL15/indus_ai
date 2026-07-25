import uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Boolean, ForeignKey
from sqlalchemy.dialects.postgresql import UUID
from app.db.base import BaseModel

class Machine(BaseModel):
    __tablename__ = "machines"
    name: Mapped[str] = mapped_column(String, index=True)
    location: Mapped[str | None] = mapped_column(String, nullable=True)
    status: Mapped[str] = mapped_column(String, default="OPERATIONAL") # e.g., OPERATIONAL, MAINTENANCE, OFFLINE
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)

    sops = relationship("SOP", back_populates="machine")
    decision_cases = relationship("DecisionCase", back_populates="machine")

class SOP(BaseModel):
    __tablename__ = "sops"
    title: Mapped[str] = mapped_column(String)
    machine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True, index=True)
    document_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("documents.id"), nullable=True, index=True)

    machine = relationship("Machine", back_populates="sops")

class ComplianceRule(BaseModel):
    __tablename__ = "compliance_rules"
    rule_code: Mapped[str] = mapped_column(String, index=True)
    description: Mapped[str] = mapped_column(String)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True)
