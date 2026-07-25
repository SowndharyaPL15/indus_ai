from uuid import UUID
from typing import List, Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.decision_intelligence import ApprovalRequest, ApprovalStatusEnum

class ApprovalRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create_request(self, request: ApprovalRequest) -> ApprovalRequest:
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request

    async def get_by_id(self, approval_id: UUID) -> Optional[ApprovalRequest]:
        result = await self.db.execute(select(ApprovalRequest).where(ApprovalRequest.id == approval_id))
        return result.scalar_one_or_none()

    async def get_pending(self) -> List[ApprovalRequest]:
        result = await self.db.execute(
            select(ApprovalRequest).where(ApprovalRequest.status == ApprovalStatusEnum.PENDING)
        )
        return list(result.scalars().all())

    async def update_request(self, request: ApprovalRequest) -> ApprovalRequest:
        self.db.add(request)
        await self.db.commit()
        await self.db.refresh(request)
        return request
