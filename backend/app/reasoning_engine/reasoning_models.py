"""
INDUS AI — Reasoning Memory Pydantic Schemas

Request and response models for the Reasoning Memory API endpoints.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import UUID

from app.models.decision_intelligence import OutcomeStatusEnum


# ── Request Schemas ───────────────────────────────────────────────────────────

class ReasoningStoreRequest(BaseModel):
    """Input schema for POST /api/reasoning/store."""
    decision_case_id: UUID
    case_title: str = Field(..., min_length=3, description="Short title for the case")
    problem_summary: str = Field(..., min_length=10, description="Summary of the problem")
    reasoning_steps: Optional[Dict[str, Any]] = Field(
        None, description="Structured reasoning steps taken to solve the case"
    )
    evidence_used: Optional[Dict[str, Any]] = Field(
        None, description="Documents, data points, and evidence consulted"
    )
    agents_involved: Optional[Dict[str, Any]] = Field(
        None, description="AI agents or modules that contributed"
    )
    final_recommendation: str = Field(
        ..., min_length=10, description="The recommendation that was given"
    )
    confidence_score: float = Field(
        ..., ge=0.0, le=1.0, description="Confidence in the recommendation (0-1)"
    )
    outcome_status: OutcomeStatusEnum = Field(
        ..., description="How the recommendation turned out"
    )
    success_score: Optional[float] = Field(
        None, ge=0.0, le=1.0, description="Measured success score (0-1)"
    )
    reusable_lesson: Optional[str] = Field(
        None, description="Key lesson learned (auto-generated if omitted)"
    )


# ── Response Schemas ──────────────────────────────────────────────────────────

class ReasoningStoreResponse(BaseModel):
    """Response after successful reasoning record creation."""
    reasoning_id: UUID
    decision_case_id: UUID
    case_title: str
    message: str = "Reasoning record created and stored."


class SimilarCaseResult(BaseModel):
    """A single similar case returned from the case matcher."""
    id: UUID
    decision_case_id: UUID
    case_title: str
    problem_summary: str
    final_recommendation: str
    reasoning_steps: Optional[Dict[str, Any]] = None
    evidence_used: Optional[Dict[str, Any]] = None
    agents_involved: Optional[Dict[str, Any]] = None
    confidence_score: float
    outcome_status: OutcomeStatusEnum
    success_score: Optional[float] = None
    reusable_lesson: Optional[str] = None
    similarity_score: float = Field(
        ..., description="Computed similarity to the query (0-1)"
    )
    created_at: datetime

    model_config = {"from_attributes": True}


class SimilarCasesResponse(BaseModel):
    """List of top-N similar cases with query echo."""
    query: str
    results: List[SimilarCaseResult]
    total: int
