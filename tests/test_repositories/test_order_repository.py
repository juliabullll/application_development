import pytest
import asyncio
from uuid import uuid4
from app.repositories.order_repository import OrderRepository
from app.models import OrderCreate, OrderUpdate

class TestOrderRepository:
    """Тесты для OrderRepository"""
    
    def test_create_order(self, order_repository: OrderRepository, session):
        """Тест создания заказа"""
        order_data = {
            "user_id": uuid4(),
            "address_id": uuid4(), 
            "product_id": uuid4(),
            "quantity": 2,
            "status": "pending"
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            order = loop.run_until_complete(order_repository.create(session, order_data))
            
            assert order.id is not None
            assert order.quantity == 2
            assert order.status == "pending"
            
            print("Create order - SUCCESS")
        finally:
            loop.close()

    def test_get_order_by_id(self, order_repository: OrderRepository, session):
        """Тест получения заказа по ID"""
        order_data = {
            "user_id": uuid4(),
            "address_id": uuid4(),
            "product_id": uuid4(),
            "quantity": 1,
            "status": "completed"
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            order = loop.run_until_complete(order_repository.create(session, order_data))
            
            found_order = loop.run_until_complete(order_repository.get_by_id(session, order.id))
            
            assert found_order is not None
            assert found_order.id == order.id
            assert found_order.status == "completed"
            
            print("Get order by ID - SUCCESS")
        finally:
            loop.close()

    def test_update_order(self, order_repository: OrderRepository, session):
        """Тест обновления заказа"""
        order_data = {
            "user_id": uuid4(),
            "address_id": uuid4(),
            "product_id": uuid4(),
            "quantity": 3,
            "status": "pending"
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            order = loop.run_until_complete(order_repository.create(session, order_data))
            
            update_data = OrderUpdate(
                quantity=5,
                status="shipped"
            )
            updated_order = loop.run_until_complete(order_repository.update(session, order.id, update_data))
            
            assert updated_order.quantity == 5
            assert updated_order.status == "shipped"
            
            print("Update order - SUCCESS")
        finally:
            loop.close()

    def test_delete_order(self, order_repository: OrderRepository, session):
        """Тест удаления заказа"""
        order_data = {
            "user_id": uuid4(),
            "address_id": uuid4(),
            "product_id": uuid4(),
            "quantity": 1,
            "status": "pending"
        }

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            order = loop.run_until_complete(order_repository.create(session, order_data))
            
            result = loop.run_until_complete(order_repository.delete(session, order.id))
            
            assert result is True
            
            found_order = loop.run_until_complete(order_repository.get_by_id(session, order.id))
            assert found_order is None
            
            print("Delete order - SUCCESS")
        finally:
            loop.close()

    def test_get_orders_by_user(self, order_repository: OrderRepository, session):
        """Тест получения заказов по user_id"""
        user_id = uuid4()
        
        orders_data = [
            {"user_id": user_id, "address_id": uuid4(), "product_id": uuid4(), "quantity": 1, "status": "pending"},
            {"user_id": user_id, "address_id": uuid4(), "product_id": uuid4(), "quantity": 2, "status": "completed"},
            {"user_id": uuid4(), "address_id": uuid4(), "product_id": uuid4(), "quantity": 1, "status": "pending"}  # Другой пользователь
        ]

        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        try:
            for order_data in orders_data:
                loop.run_until_complete(order_repository.create(session, order_data))
            
            user_orders = loop.run_until_complete(order_repository.get_by_filter(session, count=100, page=1, user_id=user_id))
            
            assert len(user_orders) == 2  
            
            print("Get orders by user - SUCCESS")
        finally:
            loop.close()