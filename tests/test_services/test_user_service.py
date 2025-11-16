import pytest
import asyncio
from app.services.user_service import UserService
from app.repositories.user_repository import UserRepository
from app.models import UserCreate, UserUpdate

class TestUserService:
    """Тесты для UserService (синхронные)"""
    
    def test_create_and_get_user_service(self, user_repository: UserRepository, session):
        """Комбинированный тест: создание и получение через сервис"""
        user_service = UserService(user_repository)
        
        user_data = UserCreate(
            username="service_user_lab4",
            email="service_lab4@example.com",
            description="Service test user for lab 4"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(user_service.create(session, user_data))
            
            assert user is not None
            assert user.username == "service_user_lab4"
            assert user.email == "service_lab4@example.com"
            
            # Получаем пользователя по ID
            found_user = loop.run_until_complete(user_service.get_by_id(session, user.id))
            
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.username == "service_user_lab4"
            
        finally:
            loop.close()