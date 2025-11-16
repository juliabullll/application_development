import pytest
from litestar.testing import TestClient

class TestUserController:
    """Tests for UserController"""
    
    def test_create_user(self, client: TestClient):
        """Test creating a user via the controller"""
        user_data = {
            "username": "test_user_1",
            "email": "test1@example.com",
            "description": "Test user"
        }
        response = client.post("/users", json=user_data)
        assert response.status_code in [200, 201]
        response_data = response.json()
        assert "id" in response_data
        assert response_data["username"] == user_data["username"]
        assert response_data["email"] == user_data["email"]

import pytest
import asyncio
from uuid import uuid4
from app.repositories.user_repository import UserRepository
from app.models import UserCreate

class TestUserRepository:
    """Тесты для UserRepository"""
    
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

            assert user.id is not None
            assert user.email == "test@example.com"
            assert user.username == "john_doe"
            assert user.description == "Test user description"
            print("User creation in repository - SUCCESS")
        finally:
            loop.close()

    def test_create_and_get_user(self, user_repository: UserRepository, session):
        """Тест создания и получения пользователя"""
        user_data = UserCreate(
            username="test_user_repo",
            email="test_repo@example.com",
            description="Repository test user"
        )
        
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            user = loop.run_until_complete(user_repository.create(session, user_data))
            
            assert user is not None
            assert user.username == "test_user_repo"
            assert user.email == "test_repo@example.com"
            assert user.id is not None

            found_user = loop.run_until_complete(user_repository.get_by_id(session, user.id))
            
            assert found_user is not None
            assert found_user.id == user.id
            assert found_user.username == "test_user_repo"
            
            print("Create and get user - SUCCESS")
        finally:
            loop.close()

    def test_get_by_filter(self, user_repository: UserRepository, session):
        """Тест фильтрации пользователей"""
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
            
            print("User filtering - SUCCESS")
        finally:
            loop.close()