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

# ── Environment ───────────────────────────────────────────────────────────────
APP_ENV: str = os.getenv("APP_ENV", "development")

# ── LLM Configuration ─────────────────────────────────────────────────────────
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "groq")
GROQ_API_KEY: str | None = os.getenv("GROQ_API_KEY")

# ── Database ──────────────────────────────────────────────────────────────────
DB_HOST: str = os.getenv("DB_HOST", "localhost")
DB_PORT: str = os.getenv("DB_PORT", "5432")
DB_NAME: str = os.getenv("DB_NAME", "indus_ai")
DB_USER: str = os.getenv("DB_USER", "postgres")
DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")

import urllib.parse

# Construct DB URL if not provided directly
encoded_password = urllib.parse.quote_plus(DB_PASSWORD)
_DEFAULT_URL = f"postgresql+asyncpg://{DB_USER}:{encoded_password}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
DATABASE_URL: str = os.getenv("DATABASE_URL", _DEFAULT_URL)
