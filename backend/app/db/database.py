from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import DATABASE_URL, APP_ENV

# Adjust echo based on environment
echo_sql = APP_ENV == "development"

# Connection pooling settings for production readiness
engine = create_async_engine(
    DATABASE_URL,
    echo=echo_sql,
    pool_size=10,
    max_overflow=20,
    pool_timeout=30,
    pool_recycle=1800,
)

AsyncSessionLocal = sessionmaker(
    bind=engine, class_=AsyncSession, expire_on_commit=False
)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
