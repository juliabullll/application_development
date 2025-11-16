from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Order, OrderCreate, OrderUpdate
from sqlalchemy import func

class OrderRepository:
    """Репозиторий для работы с заказами"""
    
    async def get_by_id(self, session: AsyncSession, order_id: UUID) -> Optional[Order]:
        """Получить заказ по ID"""
        query = select(Order).where(Order.id == order_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filter(
        self, 
        session: AsyncSession, 
        count: int, 
        page: int, 
        **kwargs
    ) -> List[Order]:
        """Получить список заказов с фильтрацией и пагинацией"""
        offset = (page - 1) * count
        
        query = select(Order)
        if 'user_id' in kwargs:
            query = query.where(Order.user_id == kwargs['user_id'])
        if 'status' in kwargs:
            query = query.where(Order.status == kwargs['status'])
        
        query = query.offset(offset).limit(count)
        
        result = await session.execute(query)
        orders = result.scalars().all()
        return list(orders)

    async def create(self, session: AsyncSession, order_data: dict) -> Order:
        """Создать новый заказ"""
        db_order = Order(**order_data)
        
        session.add(db_order)
        await session.commit()
        await session.refresh(db_order)
        
        return db_order

    async def update(
        self, 
        session: AsyncSession, 
        order_id: UUID, 
        order_data: OrderUpdate
    ) -> Optional[Order]:
        """Обновить данные заказа"""
        existing_order = await self.get_by_id(session, order_id)
        if not existing_order:
            return None
        
        update_data = order_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing_order
        
        query = (
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
        )
        
        await session.execute(query)
        await session.commit()
        return await self.get_by_id(session, order_id)

    async def delete(self, session: AsyncSession, order_id: UUID) -> bool:
        """Удалить заказ"""
        existing_order = await self.get_by_id(session, order_id)
        if not existing_order:
            return False
        
        query = delete(Order).where(Order.id == order_id)
        
        await session.execute(query)
        await session.commit()
        
        return True

    async def get_total_count(self, session: AsyncSession, **kwargs) -> int:
        """Получить общее количество заказов"""
        query = select(func.count(Order.id))
        
        if 'user_id' in kwargs:
            query = query.where(Order.user_id == kwargs['user_id'])
        if 'status' in kwargs:
            query = query.where(Order.status == kwargs['status'])
        
        result = await session.execute(query)
        return result.scalar_one()