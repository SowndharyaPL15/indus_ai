"""
INDUS AI — Auth Pydantic Schemas

Request / response models for registration, login, and user info.
"""

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, EmailStr, Field

from app.models.users import RoleEnum


# ── Request Schemas ───────────────────────────────────────────────────────────
class RegisterRequest(BaseModel):
    name: str = Field(..., min_length=1, max_length=120, examples=["Ravi Kumar"])
    email: EmailStr = Field(..., examples=["ravi@indus.ai"])
    password: str = Field(..., min_length=8, max_length=128)
    role: RoleEnum = Field(default=RoleEnum.FIELD_TECHNICIAN)
    department: str | None = Field(default=None, max_length=120, examples=["Maintenance"])


class LoginRequest(BaseModel):
    email: EmailStr = Field(..., examples=["ravi@indus.ai"])
    password: str = Field(...)


# ── Response Schemas ──────────────────────────────────────────────────────────
class UserResponse(BaseModel):
    id: UUID
    name: str
    email: str
    role: RoleEnum
    department: str | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: UserResponse
