from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from app.models.database_models import InventoryLog


class InventoryLogRepository:
    async def create(self, session: AsyncSession, log_data: dict):
        """Создание лога инвентаря"""
        log = InventoryLog(**log_data)
        session.add(log)
        await session.flush()
        return log
    
    async def get_all(
        self, 
        session: AsyncSession,
        product_id: Optional[UUID] = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[InventoryLog]:
        """Получение всех логов с фильтрами"""
        query = select(InventoryLog)
        
        if product_id:
            query = query.where(InventoryLog.product_id == product_id)
        
        query = query.limit(limit).offset(offset).order_by(InventoryLog.created_at.desc())
        
        result = await session.execute(query)
        return result.scalars().all()