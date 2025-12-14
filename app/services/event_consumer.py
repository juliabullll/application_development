import asyncio
from app.services.rabbitmq_service import RabbitMQService
from app.services.event_handlers import EventHandlers


async def start_event_consumers():
    rabbitmq = RabbitMQService()
    
    if await rabbitmq.connect():
        print("Starting RabbitMQ event consumers...")
        
        tasks = [
            rabbitmq.consume_events(
                queue_name="user_created_queue",
                routing_key="user.created",
                callback=EventHandlers.handle_user_created
            ),
            rabbitmq.consume_events(
                queue_name="order_created_queue", 
                routing_key="order.created",
                callback=EventHandlers.handle_order_created
            ),
            rabbitmq.consume_events(
                queue_name="product_updated_queue",
                routing_key="product.updated",
                callback=EventHandlers.handle_product_updated
            )
        ]
        
        await asyncio.gather(*tasks)
    else:
        print("Failed to start event consumers: RabbitMQ not available")


if __name__ == "__main__":
    asyncio.run(start_event_consumers())