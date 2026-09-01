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
raw_db_url = os.getenv("DATABASE_URL", _DEFAULT_URL)

def clean_database_url_for_asyncpg(url: str) -> str:
    # 1. Adapt scheme
    if url.startswith("postgres://"):
        url = url.replace("postgres://", "postgresql+asyncpg://", 1)
    elif url.startswith("postgresql://") and not url.startswith("postgresql+asyncpg://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    # 2. Parse query parameters to remove/fix asyncpg incompatible params
    parsed = urllib.parse.urlparse(url)
    if parsed.query:
        query_params = urllib.parse.parse_qs(parsed.query)
        # asyncpg uses 'ssl' instead of 'sslmode'
        if "sslmode" in query_params:
            ssl_val = query_params.pop("sslmode")[0]
            if ssl_val in ("require", "verify-ca", "verify-full", "prefer", "allow"):
                query_params["ssl"] = ["require"]

        # Remove libpq specific options that asyncpg doesn't accept
        query_params.pop("channel_binding", None)
        query_params.pop("gssencmode", None)
        query_params.pop("target_session_attrs", None)

        new_query = urllib.parse.urlencode(query_params, doseq=True)
        url = urllib.parse.urlunparse((
            parsed.scheme,
            parsed.netloc,
            parsed.path,
            parsed.params,
            new_query,
            parsed.fragment
        ))
    return url

DATABASE_URL: str = clean_database_url_for_asyncpg(raw_db_url)


