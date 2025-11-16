from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import Product, ProductCreate, ProductUpdate
from sqlalchemy import func

class ProductRepository:
    """Репозиторий для работы с продуктами"""
    
    async def get_by_id(self, session: AsyncSession, product_id: UUID) -> Optional[Product]:
        """Получить продукт по ID"""
        query = select(Product).where(Product.id == product_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filter(
        self, 
        session: AsyncSession, 
        count: int, 
        page: int, 
        **kwargs
    ) -> List[Product]:
        """Получить список продуктов с фильтрацией и пагинацией"""
        offset = (page - 1) * count
        
        query = select(Product)
        if 'name' in kwargs:
            query = query.where(Product.name == kwargs['name'])
        if 'description' in kwargs:
            query = query.where(Product.description == kwargs['description'])
        
        query = query.offset(offset).limit(count)
        
        result = await session.execute(query)
        products = result.scalars().all()
        return list(products)

    async def create(self, session: AsyncSession, product_data: ProductCreate) -> Product:
        """Создать новый продукт"""
        # Используем model_dump для Pydantic v2
        product_dict = product_data.model_dump()
        db_product = Product(**product_dict)
        
        session.add(db_product)
        await session.commit()
        await session.refresh(db_product)
        
        return db_product

    async def update(
        self, 
        session: AsyncSession, 
        product_id: UUID, 
        product_data: ProductUpdate
    ) -> Optional[Product]:
        """Обновить данные продукта"""
        existing_product = await self.get_by_id(session, product_id)
        if not existing_product:
            return None
        
        update_data = product_data.model_dump(exclude_unset=True)
        
        if not update_data:
            return existing_product
        
        query = (
            update(Product)
            .where(Product.id == product_id)
            .values(**update_data)
        )
        
        await session.execute(query)
        await session.commit()
        return await self.get_by_id(session, product_id)

    async def delete(self, session: AsyncSession, product_id: UUID) -> bool:
        """Удалить продукт"""
        existing_product = await self.get_by_id(session, product_id)
        if not existing_product:
            return False
        
        query = delete(Product).where(Product.id == product_id)
        
        await session.execute(query)
        await session.commit()
        
        return True

    async def get_total_count(self, session: AsyncSession, **kwargs) -> int:
        """Получить общее количество продуктов"""
        query = select(func.count(Product.id))
        
        if 'name' in kwargs:
            query = query.where(Product.name == kwargs['name'])
        if 'description' in kwargs:
            query = query.where(Product.description == kwargs['description'])
        
        result = await session.execute(query)
        return result.scalar_one()