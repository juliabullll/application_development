from typing import List, Optional
from uuid import UUID
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from app.models import User
from app.models import UserCreate, UserUpdate, UserResponse, user_to_response
from sqlalchemy import select, func

class UserRepository:
    
    async def get_by_id(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
        query = select(User).where(User.id == user_id)
        result = await session.execute(query)
        return result.scalar_one_or_none()

    async def get_by_filter(
        self, 
        session: AsyncSession, 
        count: int, 
        page: int, 
        **kwargs
    ) -> List[User]:
        offset = (page - 1) * count
        
        query = select(User)
        if 'username' in kwargs:
            query = query.where(User.username == kwargs['username'])
        if 'email' in kwargs:
            query = query.where(User.email == kwargs['email'])
        if 'description' in kwargs:
            query = query.where(User.description == kwargs['description'])
        
        query = query.offset(offset).limit(count)
        
        result = await session.execute(query)
        return result.scalars().all()

    async def create(self, session: AsyncSession, user_data: UserCreate) -> User:
        
        db_user = User(
            username=user_data.username,
            email=user_data.email,
            description=user_data.description
        )
        
        session.add(db_user)
        await session.commit()
        await session.refresh(db_user)
        
        return db_user

    async def update(
        self, 
        session: AsyncSession, 
        user_id: UUID, 
        user_data: UserUpdate
    ) -> Optional[User]:
        existing_user = await self.get_by_id(session, user_id)
        if not existing_user:
            return None
        
        update_data = user_data.dict(exclude_unset=True)
        
        if not update_data:
            return existing_user
        
        query = (
            update(User)
            .where(User.id == user_id)
            .values(**update_data)
        )
        
        await session.execute(query)
        await session.commit()
        return await self.get_by_id(session, user_id)

    async def delete(self, session: AsyncSession, user_id: UUID) -> bool:
    
        existing_user = await self.get_by_id(session, user_id)
        if not existing_user:
            return False
        
        query = delete(User).where(User.id == user_id)
        
        await session.execute(query)
        await session.commit()
        
        return True

        from sqlalchemy import select, func  # Добавляем func для подсчета

    
    async def get_total_count(self, session: AsyncSession, **kwargs) -> int:
        """
        Получить общее количество пользователей (для пагинации)
        
        Args:
            session: Асинхронная сессия SQLAlchemy
            **kwargs: Параметры фильтрации
            
        Returns:
            int: Общее количество пользователей
        """
        query = select(func.count(User.id))
        

        if 'username' in kwargs:
            query = query.where(User.username == kwargs['username'])
        if 'email' in kwargs:
            query = query.where(User.email == kwargs['email'])
        if 'description' in kwargs:
            query = query.where(User.description == kwargs['description'])
        
        result = await session.execute(query)
        return result.scalar_one()