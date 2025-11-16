import pytest
from unittest.mock import Mock, AsyncMock
from app.services.order_service import OrderService

class TestOrderServiceWithMocks:
    """Тесты для OrderService с использованием моков"""
    
    @pytest.mark.asyncio
    async def test_create_order_success(self):
        """Тест успешного создания заказа с моками"""
        # Мокаем репозитории
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()
        
        # Настраиваем моки - используем реальные значения, а не Mock объекты
        mock_user = Mock()
        mock_user.id = 1
        
        mock_product = Mock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.price = 100.0  
        mock_product.quantity = 10 
        
        mock_order = Mock()
        mock_order.id = 1
        mock_order.user_id = 1
        mock_order.total_amount = 200.0  
        mock_order.status = "pending"
        
        # Настраиваем возвращаемые значения
        mock_user_repo.get_by_id.return_value = mock_user
        mock_product_repo.get_by_id.return_value = mock_product
        mock_order_repo.create.return_value = mock_order
        
        # Создаем сервис с мок-репозиториями
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )
        
        # Тестовые данные
        order_data = {
            "user_id": 1,
            "product_id": 1,
            "quantity": 2  # Заказываем 2, а есть 10 - достаточно
        }
        
        # Вызываем метод сервиса
        result = await order_service.create_order(None, order_data)
        
        # Проверяем результаты
        assert result is not None
        assert result.total_amount == 200.0  # 100 * 2 = 200
        assert result.status == "pending"
        
        # Проверяем что методы репозиториев были вызваны
        mock_user_repo.get_by_id.assert_called_once_with(None, 1)
        mock_product_repo.get_by_id.assert_called_once_with(None, 1)
        mock_order_repo.create.assert_called_once()
        
        print("Mock test: create order success - PASSED")

    @pytest.mark.asyncio
    async def test_create_order_insufficient_stock(self):
        """Тест создания заказа с недостаточным количеством товара"""
        # Мокаем репозитории
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()
        
        # Настраиваем моки
        mock_user = Mock()
        mock_user.id = 1
        
        mock_product = Mock()
        mock_product.id = 1
        mock_product.name = "Test Product"
        mock_product.price = 100.0
        mock_product.quantity = 1  # Всего 1 товар на складе
        
        # Настраиваем возвращаемые значения
        mock_user_repo.get_by_id.return_value = mock_user
        mock_product_repo.get_by_id.return_value = mock_product
        
        # Создаем сервис с мок-репозиториями
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )
        
        # Тестовые данные - заказываем больше чем есть
        order_data = {
            "user_id": 1,
            "product_id": 1, 
            "quantity": 5  # Заказываем 5, но есть только 1
        }
        
        # Проверяем что возникает исключение
        with pytest.raises(ValueError, match="Insufficient stock"):
            await order_service.create_order(None, order_data)
        
        # Проверяем, что методы проверки были вызваны, но создание заказа - нет
        mock_user_repo.get_by_id.assert_called_once()
        mock_product_repo.get_by_id.assert_called_once()
        mock_order_repo.create.assert_not_called()  # Заказ не должен создаваться
        
        print("Mock test: insufficient stock - PASSED")

    @pytest.mark.asyncio
    async def test_create_order_user_not_found(self):
        """Тест создания заказа с несуществующим пользователем"""
        # Мокаем репозитории
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()
        
        # Настраиваем моки - пользователь не найден
        mock_user_repo.get_by_id.return_value = None
        
        # Создаем сервис с мок-репозиториями
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )
        
        # Тестовые данные
        order_data = {
            "user_id": 999,  # Несуществующий пользователь
            "product_id": 1,
            "quantity": 2
        }
        
        # Проверяем что возникает исключение
        with pytest.raises(ValueError, match="User not found"):
            await order_service.create_order(None, order_data)
        
        print("Mock test: user not found - PASSED")

    @pytest.mark.asyncio
    async def test_create_order_product_not_found(self):
        """Тест создания заказа с несуществующим продуктом"""
        # Мокаем репозитории
        mock_order_repo = AsyncMock()
        mock_product_repo = AsyncMock()
        mock_user_repo = AsyncMock()
        
        # Настраиваем моки
        mock_user = Mock()
        mock_user.id = 1
        
        # Продукт не найден
        mock_user_repo.get_by_id.return_value = mock_user
        mock_product_repo.get_by_id.return_value = None
        
        # Создаем сервис с мок-репозиториями
        order_service = OrderService(
            order_repository=mock_order_repo,
            product_repository=mock_product_repo,
            user_repository=mock_user_repo
        )
        
        # Тестовые данные
        order_data = {
            "user_id": 1,
            "product_id": 999, 
            "quantity": 2
        }
        
        # Проверяем что возникает исключение
        with pytest.raises(ValueError, match="Product not found"):
            await order_service.create_order(None, order_data)
        
        print("Mock test: product not found - PASSED")