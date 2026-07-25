"""
INDUS AI — Memory Module Pydantic Schemas

Request and response models for the Living Factory Memory API endpoints.
"""

from pydantic import BaseModel, Field, field_validator
from typing import List, Optional
from datetime import datetime
from uuid import UUID


# ── Request Schemas ───────────────────────────────────────────────────────────

class FeedbackSubmission(BaseModel):
    """Input schema for POST /api/memory/feedback."""
    decision_case_id: UUID
    engineer_feedback: str = Field(..., description="What actually solved the issue and general feedback")
    actual_solution: str = Field(..., description="The concrete solution applied")
    useful: bool = Field(..., description="Was the AI recommendation useful?")
    rating: int = Field(..., ge=1, le=5, description="Quality rating 1-5")
    lesson_learned: str = Field(..., description="Practical lesson for future reference")

    @field_validator("engineer_feedback", "actual_solution", "lesson_learned", mode="before")
    @classmethod
    def strip_whitespace(cls, v: str) -> str:
        if isinstance(v, str):
            return v.strip()
        return v


# ── Response Schemas ──────────────────────────────────────────────────────────

class FeedbackResponse(BaseModel):
    """Response after successful feedback submission."""
    memory_id: UUID
    decision_case_id: UUID
    status: str = "KNOWLEDGE_CAPTURED"
    message: str = "Feedback validated and stored as factory memory."


class MemorySearchResult(BaseModel):
    """A single factory memory record returned from search."""
    id: UUID
    decision_case_id: UUID
    machine_id: Optional[UUID] = None
    engineer_id: UUID
    problem: str
    solution: str
    lesson: str
    engineer_feedback: str
    rating: int
    useful: bool
    validated: bool
    times_reused: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MemorySearchResponse(BaseModel):
    """Paginated list of search results."""
    results: List[MemorySearchResult]
    total: int
    query: str
    limit: int
    offset: int
