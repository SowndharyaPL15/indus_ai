"""
INDUS AI — Database Initialization

Handles connection checking, auto-creation of tables (dev only), and basic initialization logic.
"""

import logging
from sqlalchemy import text
from app.db.database import engine
from app.db.base import Base
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
    """Creates all tables. Should ONLY be used in development.
    In production, use Alembic migrations.
    """
    if APP_ENV != "development":
        logger.warning("create_tables() called outside development mode. Skipping.")
        return

    logger.info("Creating tables (development mode)...")
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("Tables created successfully.")


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
    
    if APP_ENV == "development":
        # In dev mode, we can optionally auto-create tables if they don't exist
        # However, relying on alembic is better practice. For now, we will create them
        # if the user specifically runs reset_database, but we can also ensure they exist.
        await create_tables()
