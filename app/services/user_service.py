from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.user_repository import UserRepository
from app.models import User


class UserService:
    """
    Сервисный слой для работы с пользователями.
    Отвечает за бизнес-логику приложения.
    """
    
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository

    async def get_by_id(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
        """
        Получить пользователя по ID
        """
        return await self.user_repository.get_by_id(session, user_id)

    async def get_by_filter(
        self, 
        session: AsyncSession, 
        count: int, 
        page: int, 
        **kwargs
    ) -> List[User]:
        """
        Получить список пользователей с фильтрацией и пагинацией
        """
        if count <= 0:
            count = 10
        if count > 100:
            count = 100
        if page <= 0:
            page = 1
            
        return await self.user_repository.get_by_filter(
            session, count, page, **kwargs
        )

    async def create(self, session: AsyncSession, user_data: dict) -> User:
        """
        Создать нового пользователя
        """
        # Базовая валидация
        if not user_data.get('username') or not user_data.get('email'):
            raise ValueError("Username and email are required")
            
        if '@' not in user_data.get('email', ''):
            raise ValueError("Invalid email format")
        
        return await self.user_repository.create(session, user_data)

    async def update(
        self, 
        session: AsyncSession, 
        user_id: UUID, 
        user_data: dict
    ) -> Optional[User]:
        """
        Обновить данные пользователя
        """
        existing_user = await self.get_by_id(session, user_id)
        if not existing_user:
            return None
            
        if 'email' in user_data and user_data['email']:
            if '@' not in user_data['email']:
                raise ValueError("Invalid email format")
                
        return await self.user_repository.update(session, user_id, user_data)

    async def delete(self, session: AsyncSession, user_id: UUID) -> bool:
        """
        Удалить пользователя
        """
        existing_user = await self.get_by_id(session, user_id)
        if not existing_user:
            return False
            
        return await self.user_repository.delete(session, user_id)

    async def get_total_count(self, session: AsyncSession, **kwargs) -> int:
        """
        Получить общее количество пользователей
        """
        return await self.user_repository.get_total_count(session, **kwargs)