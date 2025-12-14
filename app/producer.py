import asyncio
import json
import aio_pika
from uuid import uuid4
import aiohttp


async def send_test_data():
    try:
        connection = await aio_pika.connect_robust("amqp://guest:guest@localhost:5672/")
        channel = await connection.channel()
        
        print("ПРОДЮСЕР ДАННЫХ")
        print("=" * 40)
        print("Отправка тестовых данных в RabbitMQ")
        print("=" * 40)
        
        products = [
            {"name": "Ноутбук Lenovo ThinkPad X1", "description": "Бизнес-ноутбук 14 дюймов", "price": 1499.99, "quantity": 25, "category": "electronics", "sku": "LEN-TPX1-001"},
            {"name": "Смартфон Samsung Galaxy S24", "description": "Флагманский смартфон", "price": 1199.99, "quantity": 40, "category": "electronics", "sku": "SAM-GS24-001"},
            {"name": "Планшет Apple iPad Pro 12.9", "description": "Планшет с дисплеем Retina", "price": 1299.99, "quantity": 18, "category": "electronics", "sku": "APP-IPPR-001"},
            {"name": "Игровая консоль PlayStation 5", "description": "Игровая консоль", "price": 499.99, "quantity": 15, "category": "gaming", "sku": "SON-PS5-001"},
            {"name": "Умные часы Apple Watch Series 9", "description": "Смарт-часы с ECG", "price": 399.99, "quantity": 30, "category": "wearables", "sku": "APP-AWS9-001"}
        ]
        
        for i, product in enumerate(products, 1):
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(product).encode()),
                routing_key="product_queue"
            )
            print(f"{i}. Продукт: {product['name']}")
        
        await asyncio.sleep(2)
        
        orders = [
            {
                "user_id": str(uuid4()),
                "items": [
                    {"product_id": "223e4567-e89b-12d3-a456-426614174001", "quantity": 1, "price": 1299.99},
                    {"product_id": "223e4567-e89b-12d3-a456-426614174002", "quantity": 2, "price": 999.99}
                ],
                "shipping_address": "ул. Пушкина, д. 10, Москва",
                "notes": "Срочный заказ",
                "status": "pending"
            },
            {
                "user_id": str(uuid4()),
                "items": [
                    {"product_id": "223e4567-e89b-12d3-a456-426614174003", "quantity": 3, "price": 349.99}
                ],
                "shipping_address": "пр. Мира, д. 45, СПб",
                "notes": "Подарок",
                "status": "pending"
            },
            {
                "user_id": str(uuid4()),
                "items": [
                    {"product_id": "223e4567-e89b-12d3-a456-426614174001", "quantity": 1, "price": 1299.99},
                    {"product_id": "223e4567-e89b-12d3-a456-426614174002", "quantity": 1, "price": 999.99},
                    {"product_id": "223e4567-e89b-12d3-a456-426614174003", "quantity": 1, "price": 349.99}
                ],
                "shipping_address": "ул. Ленина, д. 30, Екатеринбург",
                "notes": "Корпоративный заказ",
                "status": "pending"
            }
        ]
        
        for i, order in enumerate(orders, 1):
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(order).encode()),
                routing_key="order_queue"
            )
            total = sum(item['price'] * item['quantity'] for item in order['items'])
            print(f"{i}. Заказ на сумму: ${total:.2f}")
        
        inventory_updates = [
            {"product_id": "223e4567-e89b-12d3-a456-426614174001", "quantity_change": 20, "reason": "restock"},
            {"product_id": "223e4567-e89b-12d3-a456-426614174002", "quantity_change": 15, "reason": "restock"},
            {"product_id": "223e4567-e89b-12d3-a456-426614174003", "quantity_change": -5, "reason": "sale"}
        ]
        
        for i, update in enumerate(inventory_updates, 1):
            await channel.default_exchange.publish(
                aio_pika.Message(body=json.dumps(update).encode()),
                routing_key="inventory_queue"
            )
            print(f"{i}. Инвентарь: {update['reason']} для {update['product_id']}")
        
        print("=" * 40)
        print("Все тестовые данные отправлены")
        
        await connection.close()
        
    except Exception as e:
        print(f"Ошибка: {e}")


async def check_system_status():
    print("Ожидание обработки...")
    await asyncio.sleep(3)
    
    print("Проверка статуса системы...")
    
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:8000/health") as response:
                if response.status == 200:
                    health_data = await response.json()
                    print(f"Health: {health_data['status']}")
            
            async with session.get("http://localhost:8000/api/v1/products") as response:
                if response.status == 200:
                    products_data = await response.json()
                    print(f"Продуктов: {products_data.get('total', 0)}")
            
            async with session.get("http://localhost:8000/api/v1/orders") as response:
                if response.status == 200:
                    orders_data = await response.json()
                    print(f"Заказов: {orders_data.get('total', 0)}")
    
    except Exception as e:
        print(f"Не удалось проверить статус: {e}")


async def main():
    await send_test_data()
    await check_system_status()
    print("=" * 40)
    print("Завершено")


if __name__ == "__main__":
    asyncio.run(main())