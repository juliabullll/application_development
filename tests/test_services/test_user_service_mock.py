import pytest
from unittest.mock import Mock, AsyncMock
from app.services.user_service import UserService
from app.models import UserCreate, UserUpdate

class TestUserServiceWithMocks:
    """Тесты для UserService с использованием моков"""
    
    @pytest.mark.asyncio
    async def test_create_user_success(self):
        """Тест успешного создания пользователя с моками"""
        # Мокаем репозиторий
        mock_user_repo = AsyncMock()
        
        # Настраиваем мок - создаем фиктивного пользователя
        mock_user = Mock()
        mock_user.id = "123e4567-e89b-12d3-a456-426614174000"
        mock_user.username = "testuser"
        mock_user.email = "test@example.com"
        mock_user.description = "Test user"
        
        # Настраиваем возвращаемое значение
        mock_user_repo.create.return_value = mock_user
        
        # Создаем сервис с мок-репозиторием
        user_service = UserService(user_repository=mock_user_repo)
        
        # Тестовые данные
        user_data = UserCreate(
            username="testuser",
            email="test@example.com",
            description="Test user"
        )
        
        # Вызываем метод сервиса
        result = await user_service.create(None, user_data)  # session не нужен с моками
        
        # Проверяем результаты
        assert result is not None
        assert result.username == "testuser"
        assert result.email == "test@example.com"
        assert result.id == "123e4567-e89b-12d3-a456-426614174000"
        
        # Проверяем что метод репозитория был вызван
        mock_user_repo.create.assert_called_once()
        
        print("Mock test: create user success - PASSED")

    @pytest.mark.asyncio
    async def test_get_user_by_id_success(self):
        """Тест успешного получения пользователя по ID с моками"""
        # Мокаем репозиторий
        mock_user_repo = AsyncMock()
        
        # Настраиваем мок - фиктивный пользователь
        mock_user = Mock()
        mock_user.id = "123e4567-e89b-12d3-a456-426614174000"
        mock_user.username = "john_doe"
        mock_user.email = "john@example.com"
        
        # Настраиваем возвращаемое значение
        mock_user_repo.get_by_id.return_value = mock_user
        
        # Создаем сервис с мок-репозиторием
        user_service = UserService(user_repository=mock_user_repo)
        
        # Вызываем метод сервиса
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        result = await user_service.get_by_id(None, user_id)  # session не нужен с моками
        
        # Проверяем результаты
        assert result is not None
        assert result.id == user_id
        assert result.username == "john_doe"
        
        # Проверяем, что метод репозитория был вызван с правильным ID
        mock_user_repo.get_by_id.assert_called_once_with(None, user_id)
        
        print("Mock test: get user by ID - PASSED")

    @pytest.mark.asyncio
    async def test_get_user_by_id_not_found(self):
        """Тест случая когда пользователь не найден"""
        # Мокаем репозиторий
        mock_user_repo = AsyncMock()
        
        # Настраиваем мок - возвращаем None (пользователь не найден)
        mock_user_repo.get_by_id.return_value = None
        
        # Создаем сервис с мок-репозиторием
        user_service = UserService(user_repository=mock_user_repo)
        
        # Вызываем метод сервиса
        user_id = "99999999-9999-9999-9999-999999999999"
        result = await user_service.get_by_id(None, user_id)
        
        # Проверяем, что вернулся None
        assert result is None
        
        # Проверяем, что метод репозитория был вызван
        mock_user_repo.get_by_id.assert_called_once_with(None, user_id)
        
        print("Mock test: user not found - PASSED")

    @pytest.mark.asyncio
    async def test_update_user_success(self):
        """Тест успешного обновления пользователя"""
        # Мокаем репозиторий
        mock_user_repo = AsyncMock()
        
        # Настраиваем мок - обновленный пользователь
        mock_updated_user = Mock()
        mock_updated_user.id = "123e4567-e89b-12d3-a456-426614174000"
        mock_updated_user.username = "updated_user"
        mock_updated_user.email = "updated@example.com"
        mock_updated_user.description = "Updated description"
        
        # Настраиваем возвращаемое значение
        mock_user_repo.update.return_value = mock_updated_user
        
        # Создаем сервис с мок-репозиторием
        user_service = UserService(user_repository=mock_user_repo)
        
        # Тестовые данные для обновления
        update_data = UserUpdate(
            username="updated_user",
            description="Updated description"
        )
        
        # Вызываем метод сервиса
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        result = await user_service.update(None, user_id, update_data)
        
        # Проверяем результаты
        assert result is not None
        assert result.username == "updated_user"
        assert result.description == "Updated description"
        
        # Проверяем, что метод репозитория был вызван
        mock_user_repo.update.assert_called_once()
        
        print("Mock test: update user - PASSED")

    @pytest.mark.asyncio
    async def test_delete_user_success(self):
        """Тест успешного удаления пользователя"""
        # Мокаем репозиторий
        mock_user_repo = AsyncMock()
        
        # Настраиваем мок - удаление успешно
        mock_user_repo.delete.return_value = True
        
        # Создаем сервис с мок-репозиторием
        user_service = UserService(user_repository=mock_user_repo)
        
        # Вызываем метод сервиса
        user_id = "123e4567-e89b-12d3-a456-426614174000"
        result = await user_service.delete(None, user_id)
        
        # Проверяем, что удаление прошло успешно
        assert result is True
        
        # Проверяем, что метод репозитория был вызван
        mock_user_repo.delete.assert_called_once_with(None, user_id)
        
        print("Mock test: delete user - PASSED")