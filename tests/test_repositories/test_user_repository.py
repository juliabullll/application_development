import pytest
import asyncio
from uuid import uuid4
from app.repositories.user_repository import UserRepository
from app.models import UserCreate, UserUpdate

class TestUserRepository:
    """Тесты для UserRepository (синхронные)"""
    
    def test_create_and_get_user(self, user_repository: UserRepository, session):
        """Комбинированный тест: создание и получение пользователя"""
        # Создаем пользователя
        user_data = UserCreate(
            username="test_user_lab4",
            email="test_lab4@example.com",
            description="Test user for lab 4"
        )
        
        # Запускаем асинхронную функцию с новым event loop
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(user_repository.create(session, user_data))
            
            assert user is not None
            assert user.username == "test_user_lab4"
            assert user.email == "test_lab4@example.com"
            assert user.id is not None
            
            # Получаем пользователя по ID
            found_user = loop.run_until_complete(user_repository.get_by_id(session, user.id))
            
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.username == "test_user_lab4"
            
        finally:
            loop.close()
    
    def test_get_by_filter(self, user_repository: UserRepository, session):
        """Тест фильтрации пользователей"""
        # Создаем тестовых пользователей
        user1_data = UserCreate(username="filter_user_1", email="filter1@example.com")
        user2_data = UserCreate(username="filter_user_2", email="filter2@example.com")
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(user_repository.create(session, user1_data))
            loop.run_until_complete(user_repository.create(session, user2_data))
            
            users = loop.run_until_complete(user_repository.get_by_filter(session, count=10, page=1, username="filter_user_1"))
            
            assert len(users) >= 1
            assert users[0].username == "filter_user_1"
            
        finally:
            loop.close()


    def test_create_user(self, user_repository: UserRepository, session):
        """Тест создания пользователя в репозитории"""
        user_data = UserCreate(
            email="test@example.com",
            username="john_doe",
            description="Test user description"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(user_repository.create(session, user_data))

            assert user.id is not None, "User ID должен быть сгенерирован"
            assert user.email == "test@example.com", "Email должен совпадать"
            assert user.username == "john_doe", "Username должен совпадать"
            assert user.description == "Test user description", "Description должен совпадать"
            
            print("User creation in repository - SUCCESS")
            print(f"Created user: {user.username} ({user.email}) with ID: {user.id}")
            
        finally:
            loop.close()






   