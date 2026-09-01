import logging
from sqlalchemy import text
from app.db.database import engine
from app.db.base import Base
import app.models  # noqa: F401 Ensure all models are registered on metadata
from app.core.config import APP_ENV

logger = logging.getLogger(__name__)


async def check_database_connection() -> bool:
    """Verifies that the database is reachable."""
    try:
        async with engine.begin() as conn:
            await conn.execute(text("SELECT 1"))
        return True
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return False


async def create_tables() -> None:
    """Creates all tables if they do not exist."""
    logger.info("Validating database schema and tables...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Database tables validated successfully.")


async def drop_tables_dev_only() -> None:
    """Drops all tables. NEVER use in production."""
    if APP_ENV != "development":
        raise Exception("drop_tables_dev_only() can ONLY be run in development!")

    logger.warning("Dropping all tables (development mode)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    logger.info("All tables dropped.")


async def initialize_database() -> None:
    """Main startup initialization hook."""
    is_connected = await check_database_connection()
    if not is_connected:
        raise Exception("Could not connect to the database on startup.")
    
    await create_tables()

