from sqlalchemy.ext.asyncio import AsyncSession
from app.models.users import User
from app.idie.models import FusionDecisionResponse
from app.idie.fusion_engine import FusionEngine

async def run_investigation(db: AsyncSession, user: User, query: str) -> FusionDecisionResponse:
    """Runs the IDIE v2 Intelligence Fusion Engine pipeline."""
    return await FusionEngine.run_fusion_investigation(db, user, query)
