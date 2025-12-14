import json
import os
from typing import Any, Dict
from datetime import datetime
from app.rabbitmq.producer import RabbitMQProducer


class RabbitMQService:
    """Сервис для работы с RabbitMQ через FastStream"""
    
    def __init__(self):
        self.producer = RabbitMQProducer()
        self.is_connected = False
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        try:
            await self.producer.start()
            self.is_connected = True
            print("RabbitMQ connected via FastStream")
            return True
        except Exception as e:
            print(f"RabbitMQ connection error: {e}")
            return False
    
    async def disconnect(self):
        """Отключение от RabbitMQ"""
        if self.is_connected:
            await self.producer.stop()
            self.is_connected = False
    
    async def publish_order_created(self, order_data: Dict[str, Any]):
        """Публикация события создания заказа"""
        if not self.is_connected:
            await self.connect()
        
        event_data = {
            "event_type": "order.created",
            **order_data,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.producer.publish_order(event_data)
            print(f"Order created event published: {order_data.get('order_id')}")
            return True
        except Exception as e:
            print(f"Failed to publish order event: {e}")
            return False
    
    async def publish_user_event(self, event_type: str, user_data: Dict[str, Any]):
        """Публикация события пользователя"""
        if not self.is_connected:
            await self.connect()
        
        event_data = {
            "event_type": event_type,
            **user_data,
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            await self.producer.publish_user_event(event_data)
            print(f"User event published: {event_type}")
            return True
        except Exception as e:
            print(f"Failed to publish user event: {e}")
            return False