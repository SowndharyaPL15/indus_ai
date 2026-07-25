import uuid
import enum
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy import String, Text, ForeignKey, Enum, Float
from sqlalchemy.dialects.postgresql import UUID, JSONB
from app.db.base import BaseModel

class CaseStatusEnum(str, enum.Enum):
    OPEN = "OPEN"
    IN_PROGRESS = "IN_PROGRESS"
    WAITING_APPROVAL = "WAITING_APPROVAL"
    RESOLVED = "RESOLVED"
    CLOSED = "CLOSED"
    KNOWLEDGE_CAPTURED = "KNOWLEDGE_CAPTURED"

class ApprovalStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    APPROVED = "APPROVED"
    REJECTED = "REJECTED"
    ESCALATED = "ESCALATED"
    CANCELLED = "CANCELLED"


class OutcomeStatusEnum(str, enum.Enum):
    PENDING = "PENDING"
    SUCCESSFUL = "SUCCESSFUL"
    FAILED = "FAILED"
    PARTIALLY_SUCCESSFUL = "PARTIALLY_SUCCESSFUL"
    UNKNOWN = "UNKNOWN"

class DecisionCase(BaseModel):
    __tablename__ = "decision_cases"
    user_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), index=True)
    machine_id: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("machines.id"), nullable=True, index=True)
    query: Mapped[str] = mapped_column(Text)
    status: Mapped[CaseStatusEnum] = mapped_column(Enum(CaseStatusEnum), default=CaseStatusEnum.OPEN)
    
    user = relationship("User", back_populates="decision_cases")
    machine = relationship("Machine", back_populates="decision_cases")
    ai_responses = relationship("AIResponse", back_populates="decision_case")
    conflict_logs = relationship("ConflictLog", back_populates="decision_case")
    approval_requests = relationship("ApprovalRequest", back_populates="decision_case")
    audit_logs = relationship("AuditLog", back_populates="decision_case")
    reasoning_memories = relationship("ReasoningMemory", back_populates="decision_case")
    factory_memory_records = relationship("FactoryMemoryRecord", back_populates="decision_case")

class AIResponse(BaseModel):
    __tablename__ = "ai_responses"
    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("decision_cases.id"), index=True)
    response_text: Mapped[str] = mapped_column(Text)
    
    decision_case = relationship("DecisionCase", back_populates="ai_responses")
    confidence_score = relationship("ConfidenceScore", back_populates="ai_response", uselist=False)

class ConfidenceScore(BaseModel):
    __tablename__ = "confidence_scores"
    ai_response_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("ai_responses.id"), index=True)
    score: Mapped[float] = mapped_column(Float)
    factors: Mapped[dict | None] = mapped_column(JSONB, nullable=True) # Explains why the score is what it is

    ai_response = relationship("AIResponse", back_populates="confidence_score")

class ConflictLog(BaseModel):
    __tablename__ = "conflict_logs"
    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("decision_cases.id"), index=True)
    description: Mapped[str] = mapped_column(Text)
    resolved: Mapped[bool] = mapped_column(default=False)

    decision_case = relationship("DecisionCase", back_populates="conflict_logs")

class ApprovalRequest(BaseModel):
    __tablename__ = "approval_requests"
    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("decision_cases.id"), index=True)
    requested_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    approver_role: Mapped[str] = mapped_column(String)
    reason: Mapped[str] = mapped_column(Text)
    risk_level: Mapped[str] = mapped_column(String)
    recommendation_summary: Mapped[str] = mapped_column(Text)
    
    status: Mapped[ApprovalStatusEnum] = mapped_column(Enum(ApprovalStatusEnum), default=ApprovalStatusEnum.PENDING)
    
    approved_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    rejected_by: Mapped[uuid.UUID | None] = mapped_column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True, index=True)
    comments: Mapped[str | None] = mapped_column(Text, nullable=True)
    reject_reason: Mapped[str | None] = mapped_column(Text, nullable=True)

    decision_case = relationship("DecisionCase", back_populates="approval_requests")


class ReasoningMemory(BaseModel):
    """Stores how previous decision cases were solved, enabling case-based reasoning."""
    __tablename__ = "reasoning_memory"
    decision_case_id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), ForeignKey("decision_cases.id"), index=True)
    case_title: Mapped[str] = mapped_column(String, index=True)
    problem_summary: Mapped[str] = mapped_column(Text)
    reasoning_steps: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    evidence_used: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    agents_involved: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    final_recommendation: Mapped[str] = mapped_column(Text)
    confidence_score: Mapped[float] = mapped_column(Float)
    outcome_status: Mapped[OutcomeStatusEnum] = mapped_column(
        Enum(OutcomeStatusEnum), default=OutcomeStatusEnum.PENDING
    )
    success_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    reusable_lesson: Mapped[str | None] = mapped_column(Text, nullable=True)

    decision_case = relationship("DecisionCase", back_populates="reasoning_memories")
