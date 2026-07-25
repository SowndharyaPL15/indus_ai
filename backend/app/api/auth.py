"""
INDUS AI — Auth API Router

Endpoints:
    POST /api/auth/register  — Create a new user account
    POST /api/auth/login     — Authenticate and receive a JWT
    GET  /api/auth/me        — Return the current authenticated user
"""

from typing import Annotated

from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import create_access_token, get_current_user
from app.db.database import get_db
from app.models.users import User
from app.schemas.auth import (
    RegisterRequest,
    LoginRequest,
    TokenResponse,
    UserResponse,
)
from app.services.auth_service import register_user, authenticate_user

router = APIRouter()


# ── POST /register ────────────────────────────────────────────────────────────
@router.post("/register", response_model=UserResponse, status_code=201)
async def register(payload: RegisterRequest, db: AsyncSession = Depends(get_db)):
    """Register a new INDUS AI user."""
    user = await register_user(db, payload)
    return user


# ── POST /login ───────────────────────────────────────────────────────────────
@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: AsyncSession = Depends(get_db)):
    """Authenticate and return an access token."""
    user = await authenticate_user(db, payload.email, payload.password)
    token = create_access_token(data={"sub": str(user.id)})
    return TokenResponse(
        access_token=token,
        token_type="bearer",
        user=UserResponse.model_validate(user),
    )


# ── GET /me ───────────────────────────────────────────────────────────────────
@router.get("/me", response_model=UserResponse)
async def me(current_user: Annotated[User, Depends(get_current_user)]):
    """Return the profile of the currently authenticated user."""
    return current_user
