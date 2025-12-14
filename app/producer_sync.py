import pika
import json
from uuid import uuid4


def send_test_data_sync():
    try:
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(
                host='localhost',
                port=5672
            )
        )
        
        channel = connection.channel()
        
        print("Отправка тестовых данных...")
        
        products = [
            {
                "name": "Ноутбук HP Spectre x360",
                "description": "Ноутбук-трансформер",
                "price": 1599.99,
                "quantity": 20,
                "category": "electronics",
                "sku": "HP-SPX360-001"
            },
            {
                "name": "Смартфон Google Pixel 8 Pro",
                "description": "Смартфон с камерой",
                "price": 899.99,
                "quantity": 35,
                "category": "electronics",
                "sku": "GOO-PX8P-001"
            },
            {
                "name": "Наушники Bose QuietComfort 45",
                "description": "Наушники с шумоподавлением",
                "price": 329.99,
                "quantity": 50,
                "category": "audio",
                "sku": "BOS-QC45-001"
            },
            {
                "name": "Фотоаппарат Canon EOS R6",
                "description": "Зеркальная камера",
                "price": 2499.99,
                "quantity": 8,
                "category": "photo",
                "sku": "CAN-R6-001"
            },
            {
                "name": "Книга Amazon Kindle Paperwhite",
                "description": "Читалка с подсветкой",
                "price": 139.99,
                "quantity": 60,
                "category": "reading",
                "sku": "AMA-KPW-001"
            }
        ]
        
        for product in products:
            channel.basic_publish(
                exchange='',
                routing_key='product_queue',
                body=json.dumps(product),
                properties=pika.BasicProperties(
                    content_type='application/json'
                )
            )
            print(f"Продукт: {product['name']}")
        
        orders = [
            {
                "user_id": str(uuid4()),
                "items": [
                    {
                        "product_id": "223e4567-e89b-12d3-a456-426614174001",
                        "quantity": 1,
                        "price": 1299.99
                    }
                ],
                "shipping_address": "ул. Гагарина, д. 12, Казань",
                "notes": "Заказ для офиса",
                "status": "pending"
            },
            {
                "user_id": str(uuid4()),
                "items": [
                    {
                        "product_id": "223e4567-e89b-12d3-a456-426614174002",
                        "quantity": 1,
                        "price": 999.99
                    },
                    {
                        "product_id": "223e4567-e89b-12d3-a456-426614174003",
                        "quantity": 2,
                        "price": 349.99
                    }
                ],
                "shipping_address": "пр. Победы, д. 88, Новосибирск",
                "notes": "Личный заказ",
                "status": "pending"
            },
            {
                "user_id": str(uuid4()),
                "items": [
                    {
                        "product_id": "223e4567-e89b-12d3-a456-426614174001",
                        "quantity": 2,
                        "price": 1299.99
                    }
                ],
                "shipping_address": "ул. Советская, д. 5, Сочи",
                "notes": "Для отдела разработки",
                "status": "pending"
            }
        ]
        
        for order in orders:
            channel.basic_publish(
                exchange='',
                routing_key='order_queue',
                body=json.dumps(order),
                properties=pika.BasicProperties(
                    content_type='application/json'
                )
            )
            total = sum(item['price'] * item['quantity'] for item in order['items'])
            print(f"Заказ: ${total:.2f}")
        
        connection.close()
        
        print("=" * 40)
        print("Все данные отправлены")
        
    except Exception as e:
        print(f"Ошибка: {e}")


if __name__ == "__main__":
    send_test_data_sync()