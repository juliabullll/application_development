import aio_pika
import json
import os
from typing import Any


class RabbitMQProducer:
    def __init__(self):
        self.connection = None
        self.channel = None
        self.rabbitmq_url = os.getenv(
            "RABBITMQ_URL", 
            "amqp://guest:guest@localhost:5672/"
        )
    
    async def connect(self):
        """Подключение к RabbitMQ"""
        if not self.connection:
            self.connection = await aio_pika.connect_robust(self.rabbitmq_url)
            self.channel = await self.connection.channel()
    
    async def publish(self, queue_name: str, message: Any):
        """Публикация сообщения в очередь"""
        if not self.connection:
            await self.connect()
        
        await self.channel.default_exchange.publish(
            aio_pika.Message(
                body=json.dumps(message).encode()
            ),
            routing_key=queue_name
        )
    
    async def close(self):
        """Закрытие соединения"""
        if self.connection:
            await self.connection.close()

producer = RabbitMQProducer()


async def publish_to_queue(queue_name: str, message: Any):
    """Функция для публикации сообщений"""
    await producer.publish(queue_name, message)