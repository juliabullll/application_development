# app/controllers/test_controller.py
from litestar import Controller, get, post
from litestar.response import Response
import json
import aio_pika
import asyncio
from uuid import uuid4, UUID
from datetime import datetime


class TestController(Controller):
    path = "/api/v1/test"
    
    @get("/")
    async def test_info(self) -> dict:
        """Информация о системе"""
        return {
            "status": "running",
            "service": "Order Processing System",
            "timestamp": datetime.now().isoformat(),
            "features": [
                "RabbitMQ message processing",
                "Order management",
                "Product management",
                "Inventory control"
            ],
            "queues": [
                "order_queue",
                "product_queue", 
                "inventory_queue",
                "order_status_queue"
            ]
        }
    
    @get("/rabbitmq")
    async def test_rabbitmq(self) -> dict:
        """Тест RabbitMQ соединения"""
        try:
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
            await connection.close()
            return {"status": "success", "message": "RabbitMQ connection OK"}
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @post("/create-test-product")
    async def create_test_product(self) -> dict:
        """Создать тестовый продукт через RabbitMQ"""
        try:
            test_product = {
                "name": "Тестовый продукт API",
                "description": "Продукт созданный через API",
                "price": 199.99,
                "quantity": 50,
                "category": "electronics",
                "sku": "API-TEST-001"
            }
            
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
            channel = await connection.channel()
            
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(test_product).encode(),
                    content_type="application/json"
                ),
                routing_key="product_queue"
            )
            
            await connection.close()
            
            return {
                "status": "success",
                "message": "Test product sent to RabbitMQ",
                "product": test_product,
                "queue": "product_queue"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @post("/create-test-order")
    async def create_test_order(self, data: dict = None) -> dict:
        """Создать тестовый заказ через RabbitMQ"""
        try:
            # Используем один из существующих product_id из инвентаря
            test_order = {
                "user_id": str(uuid4()),
                "items": [
                    {
                        "product_id": "223e4567-e89b-12d3-a456-426614174001",  # Существующий в инвентаре
                        "quantity": 1,  # Только 1 чтобы не превысить запас
                        "price": 1299.99
                    }
                ],
                "shipping_address": "ул. Тестовая, д. 123, кв. 45",
                "notes": "Тестовый заказ созданный через API",
                "status": "pending"
            }
            
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
            channel = await connection.channel()
            
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(test_order).encode(),
                    content_type="application/json"
                ),
                routing_key="order_queue"
            )
            
            await connection.close()
            
            return {
                "status": "success",
                "message": "Test order sent to RabbitMQ",
                "order": test_order,
                "queue": "order_queue"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @post("/update-inventory")
    async def update_test_inventory(self) -> dict:
        """Обновить инвентарь через RabbitMQ"""
        try:
            inventory_update = {
                "product_id": "223e4567-e89b-12d3-a456-426614174001",  # Существующий продукт
                "quantity_change": 10,  # Добавить 10 единиц
                "reason": "restock"
            }
            
            connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
            channel = await connection.channel()
            
            await channel.default_exchange.publish(
                aio_pika.Message(
                    body=json.dumps(inventory_update).encode(),
                    content_type="application/json"
                ),
                routing_key="inventory_queue"
            )
            
            await connection.close()
            
            return {
                "status": "success",
                "message": "Inventory update sent to RabbitMQ",
                "update": inventory_update,
                "queue": "inventory_queue"
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @get("/inventory-status")
    async def get_inventory_status(self) -> dict:
        """Получить статус инвентаря"""
        try:
            from app.services.inventory_service import InventoryService
            
            inventory_service = InventoryService()
            await inventory_service.initialize()
            
            # Получить статус для тестовых продуктов
            statuses = {}
            for product_id in [
                "223e4567-e89b-12d3-a456-426614174001",
                "223e4567-e89b-12d3-a456-426614174002", 
                "223e4567-e89b-12d3-a456-426614174003"
            ]:
                status = await inventory_service.get_inventory_status(UUID(product_id))
                statuses[product_id] = status
            
            return {
                "status": "success",
                "inventory": statuses,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {"status": "error", "message": str(e)}
    
    @get("/system-status")
    async def system_status(self) -> dict:
        """Полный статус системы"""
        from app.services.order_processor import OrderProcessor
        from app.services.product_processor import ProductProcessor
        from app.services.inventory_service import InventoryService
        
        try:
            # Инициализируем сервисы
            order_processor = OrderProcessor()
            await order_processor.initialize()
            
            product_processor = ProductProcessor()
            await product_processor.initialize()
            
            inventory_service = InventoryService()
            await inventory_service.initialize()
            
            # Получаем статистику
            orders_count = len(order_processor.orders) if hasattr(order_processor, 'orders') else 0
            products_count = len(product_processor.products) if hasattr(product_processor, 'products') else 0
            inventory_count = len(inventory_service.inventory) if hasattr(inventory_service, 'inventory') else 0
            
            return {
                "status": "operational",
                "timestamp": datetime.now().isoformat(),
                "services": {
                    "order_processor": "running" if order_processor else "stopped",
                    "product_processor": "running" if product_processor else "stopped",
                    "inventory_service": "running" if inventory_service else "stopped",
                    "rabbitmq_consumer": "running"
                },
                "statistics": {
                    "orders": orders_count,
                    "products": products_count,
                    "inventory_items": inventory_count
                },
                "rabbitmq": {
                    "host": "localhost",
                    "port": 5672,
                    "status": "connected"
                }
            }
            
        except Exception as e:
            return {
                "status": "partial",
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }