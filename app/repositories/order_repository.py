from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from app.models.database_models import Order, OrderItem


class OrderRepository:
    async def create(self, session: AsyncSession, order_data: dict):
        """Создание нового заказа"""
        order = Order(**order_data)
        session.add(order)
        await session.flush()
        return order
    
    async def get_by_id(self, session: AsyncSession, order_id: UUID) -> Optional[Order]:
        """Получение заказа по ID"""
        result = await session.execute(
            select(Order).where(Order.id == order_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, session: AsyncSession, order_id: UUID, update_data: dict) -> Optional[Order]:
        """Обновление заказа"""
        await session.execute(
            update(Order)
            .where(Order.id == order_id)
            .values(**update_data)
        )
        await session.flush()
        return await self.get_by_id(session, order_id)
    
    async def get_order_items(self, session: AsyncSession, order_id: UUID) -> List[OrderItem]:
        """Получение позиций заказа"""
        result = await session.execute(
            select(OrderItem).where(OrderItem.order_id == order_id)
        )
        return result.scalars().all()
    
    async def create_items(self, session: AsyncSession, items_data: List[dict]):
        """Создание позиций заказа"""
        for item_data in items_data:
            item = OrderItem(**item_data)
            session.add(item)
        await session.flush()