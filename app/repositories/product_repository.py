from typing import Optional, List
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, and_
from app.models.database_models import Product


class ProductRepository:
    async def create(self, session: AsyncSession, product_data: dict):
        """Создание нового продукта"""
        product = Product(**product_data)
        session.add(product)
        await session.flush()
        return product
    
    async def get_by_id(self, session: AsyncSession, product_id: UUID) -> Optional[Product]:
        """Получение продукта по ID"""
        result = await session.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()
    
    async def update(self, session: AsyncSession, product_id: UUID, update_data: dict) -> Optional[Product]:
        """Обновление продукта"""
        await session.execute(
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        await session.flush()
        return await self.get_by_id(session, product_id)
    
    async def get_all(
        self, 
        session: AsyncSession,
        category: Optional[str] = None,
        available_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Product]:
        """Получение всех продуктов с фильтрами"""
        query = select(Product)
        
        if category:
            query = query.where(Product.category == category)
        
        if available_only:
            query = query.where(and_(Product.is_available == True, Product.quantity > 0))
        
        query = query.limit(limit).offset(offset)
        
        result = await session.execute(query)
        return result.scalars().all()
    
    async def get_low_stock(
        self, 
        session: AsyncSession,
        threshold: int = 10
    ) -> List[Product]:
        """Получение продуктов с низким запасом"""
        result = await session.execute(
            select(Product)
            .where(Product.quantity <= threshold)
            .where(Product.is_available == True)
            .order_by(Product.quantity.asc())
        )
        return result.scalars().all()
