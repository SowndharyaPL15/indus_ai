"""
INDUS AI — Core Configuration

Centralizes all environment-driven settings using Pydantic.
"""

import os
from dotenv import load_dotenv

load_dotenv()

# ── JWT Settings ──────────────────────────────────────────────────────────────
SECRET_KEY: str = os.getenv("SECRET_KEY", "indus-ai-dev-secret-change-in-production")
ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# ── Database ──────────────────────────────────────────────────────────────────
DATABASE_URL: str = os.getenv(
    "DATABASE_URL",
    "postgresql+asyncpg://postgres:postgres@localhost:5432/indus_ai",
)
