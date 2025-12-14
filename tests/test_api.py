import pytest
import asyncio
from uuid import uuid4, UUID
from litestar.status_codes import (
    HTTP_200_OK, 
    HTTP_201_CREATED, 
    HTTP_204_NO_CONTENT, 
    HTTP_404_NOT_FOUND,
    HTTP_422_UNPROCESSABLE_ENTITY,
    HTTP_400_BAD_REQUEST
)
from litestar.testing import TestClient
from app.models import UserCreate, UserUpdate


class TestUserControllerAPI:
    """API тесты для UserController"""

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self, client: TestClient, user_repository, session):
        """Тест успешного получения пользователя по ID"""
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            description="Test user"
        )
        user = await user_repository.create(session, user_data)
        
        response = client.get(f"/users/{user.id}")
        
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["username"] == user_data.username
        assert data["email"] == user_data.email
        assert data["description"] == user_data.description
        assert UUID(data["id"]) == user.id

    def test_get_user_by_id_not_found(self, client: TestClient):
        """Тест получения несуществующего пользователя"""
        response = client.get(f"/users/{uuid4()}")

        assert response.status_code == HTTP_404_NOT_FOUND
        assert "not found" in response.json()["detail"].lower()

    def test_get_user_by_id_invalid_uuid(self, client: TestClient):
        """Тест получения пользователя с невалидным UUID"""
        response = client.get("/users/invalid-uuid")
        
        assert response.status_code == HTTP_404_NOT_FOUND
        assert "invalid" in response.json()["detail"].lower()

    def test_create_user_success(self, client: TestClient):
        """Тест успешного создания пользователя"""

        user_data = {
            "username": "newuser",
            "email": "new@example.com",
            "description": "New user description"
        }
        
        response = client.post("/users", json=user_data)
        
        assert response.status_code == HTTP_201_CREATED
        data = response.json()
        assert data["username"] == user_data["username"]
        assert data["email"] == user_data["email"]
        assert data["description"] == user_data["description"]
        assert "id" in data
        assert "created_at" in data

    def test_create_user_invalid_email(self, client: TestClient):
        """Тест создания пользователя с невалидным email"""
        user_data = {
            "username": "baduser",
            "email": "invalid-email",
            "description": "Bad user"
        }
        
        response = client.post("/users", json=user_data)
        
        assert response.status_code == HTTP_400_BAD_REQUEST

    def test_create_user_missing_required_fields(self, client: TestClient):
        """Тест создания пользователя без обязательных полей"""
        user_data = {
            "description": "Only description"
        }
        
        response = client.post("/users", json=user_data)
        

        assert response.status_code == HTTP_400_BAD_REQUEST

    @pytest.mark.asyncio
    async def test_get_all_users_success(self, client: TestClient, user_repository, session):
        """Тест успешного получения списка пользователей"""
        users_data = [
            UserCreate(username=f"user{i}", email=f"user{i}@example.com")
            for i in range(3)
        ]
        
        for user_data in users_data:
            await user_repository.create(session, user_data)

        response = client.get("/users?count=10&page=1")
        
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert "users" in data
        assert "total_count" in data
        assert "page" in data
        assert "per_page" in data
        assert "total_pages" in data
        assert len(data["users"]) >= 1

    @pytest.mark.asyncio 
    async def test_get_all_users_pagination(self, client: TestClient, user_repository, session):
        """Тест пагинации списка пользователей"""
        users_data = [
            UserCreate(username=f"paguser{i}", email=f"paguser{i}@example.com")
            for i in range(5)
        ]
        
        for user_data in users_data:
            await user_repository.create(session, user_data)

        response = client.get("/users?count=2&page=1")
        

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["page"] == 1
        assert data["per_page"] == 2

    @pytest.mark.asyncio
    async def test_update_user_success(self, client: TestClient, user_repository, session):
        """Тест успешного обновления пользователя"""
        user_data = UserCreate(
            username="originaluser",
            email="original@example.com",
            description="Original description"
        )
        user = await user_repository.create(session, user_data)
        
        update_data = {
            "username": "updateduser",
            "email": "updated@example.com", 
            "description": "Updated description"
        }
        
        response = client.put(f"/users/{user.id}", json=update_data)

        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == update_data["email"]
        assert data["description"] == update_data["description"]

    @pytest.mark.asyncio
    async def test_update_user_partial(self, client: TestClient, user_repository, session):
        """Тест частичного обновления пользователя"""
        user_data = UserCreate(
            username="partialuser",
            email="partial@example.com",
            description="Original description"
        )
        user = await user_repository.create(session, user_data)
        
        update_data = {
            "username": "partiallyupdated"
        }
        

        response = client.put(f"/users/{user.id}", json=update_data)
        
        assert response.status_code == HTTP_200_OK
        data = response.json()
        assert data["username"] == update_data["username"]
        assert data["email"] == user_data.email 
        assert data["description"] == user_data.description  

    def test_update_user_not_found(self, client: TestClient):
        """Тест обновления несуществующего пользователя"""
        update_data = {
            "username": "updateduser"
        }
        
        response = client.put(f"/users/{uuid4()}", json=update_data)
        
        assert response.status_code == HTTP_404_NOT_FOUND

    @pytest.mark.asyncio
    async def test_delete_user_success(self, client: TestClient, user_repository, session):
        """Тест успешного удаления пользователя"""
        user_data = UserCreate(
            username="tobedeleted",
            email="delete@example.com"
        )
        user = await user_repository.create(session, user_data)
        
        response = client.delete(f"/users/{user.id}")
        
        assert response.status_code == HTTP_204_NO_CONTENT
        assert response.content == b""  
        get_response = client.get(f"/users/{user.id}")
        assert get_response.status_code == HTTP_404_NOT_FOUND

    def test_delete_user_not_found(self, client: TestClient):
        """Тест удаления несуществующего пользователя"""
        response = client.delete(f"/users/{uuid4()}")
        
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_delete_user_invalid_uuid(self, client: TestClient):
        """Тест удаления с невалидным UUID"""
      
        response = client.delete("/users/invalid-uuid")
        assert response.status_code == HTTP_404_NOT_FOUND

    def test_create_user_invalid_email(self, client: TestClient):
        """Тест создания пользователя с невалидным email"""
        user_data = {
            "username": "baduser", 
            "email": "invalid-email",
            "description": "Bad user"
        }

        response = client.post("/users", json=user_data)
        assert response.status_code == 500 
        assert response.status_code >= 500

        