#!/usr/bin/env python3
"""Тестирование системы кэширования"""

import requests
import json
import time
from datetime import datetime

BASE_URL = "http://localhost:8000"

def print_step(step: str):
    print(f"\n{'='*60}")
    print(f"ШАГ: {step}")
    print(f"{'='*60}")

def test_user_caching():
    """Тестирование кэширования пользователей"""
    print_step("1. Тестирование кэширования пользователей")
    
    user_id = "user_123"
    user_data = {
        "name": "Иван Иванов",
        "email": "ivan@example.com",
        "age": 30,
        "city": "Москва"
    }
    
    # 1. Кэшируем пользователя
    print("1.1 Кэширование пользователя...")
    response = requests.post(
        f"{BASE_URL}/api/v1/cache/users/{user_id}",
        json=user_data
    )
    print(f"   Ответ: {response.json()}")
    
    # 2. Получаем из кэша
    print("\n1.2 Получение из кэша...")
    response = requests.get(f"{BASE_URL}/api/v1/cache/users/{user_id}")
    result = response.json()
    print(f"   Источник: {result['source']}")
    print(f"   Данные: {json.dumps(result['data'], indent=2, ensure_ascii=False)}")
    
    # 3. Инвалидация кэша
    print("\n1.3 Инвалидация кэша...")
    response = requests.delete(f"{BASE_URL}/api/v1/cache/users/{user_id}")
    print(f"   Ответ: {response.json()}")
    
    # 4. Проверяем что кэш очищен
    print("\n1.4 Проверка очистки кэша...")
    response = requests.get(f"{BASE_URL}/api/v1/cache/users/{user_id}")
    result = response.json()
    print(f"   Источник: {result['source']} (должно быть 'database')")

def test_product_caching():
    """Тестирование кэширования продукции"""
    print_step("2. Тестирование кэширования продукции")
    
    product_id = "prod_456"
    product_data = {
        "name": "Ноутбук Dell XPS 15",
        "price": 1499.99,
        "quantity": 25,
        "category": "Ноутбуки",
        "specifications": {
            "processor": "Intel i7",
            "ram": "16GB",
            "storage": "512GB SSD"
        }
    }
    
    # 1. Кэшируем продукт
    print("2.1 Кэширование продукта...")
    response = requests.post(
        f"{BASE_URL}/api/v1/cache/products/{product_id}",
        json=product_data
    )
    print(f"   Ответ: {response.json()}")
    
    # 2. Получаем из кэша
    print("\n2.2 Получение из кэша...")
    response = requests.get(f"{BASE_URL}/api/v1/cache/products/{product_id}")
    result = response.json()
    print(f"   Источник: {result['source']}")
    print(f"   TTL: {result.get('ttl_seconds', 'N/A')} секунд")
    
    # 3. Обновляем кэш
    print("\n2.3 Обновление кэша...")
    updated_data = product_data.copy()
    updated_data["price"] = 1399.99
    updated_data["quantity"] = 20
    
    response = requests.post(
        f"{BASE_URL}/api/v1/cache/products/{product_id}/update",
        json=updated_data
    )
    print(f"   Ответ: {response.json()}")
    
    # 4. Проверяем обновление
    print("\n2.4 Проверка обновленного кэша...")
    response = requests.get(f"{BASE_URL}/api/v1/cache/products/{product_id}")
    result = response.json()
    print(f"   Новая цена: {result['data']['price']}")
    print(f"   Новое количество: {result['data']['quantity']}")

def test_cache_management():
    """Тестирование управления кэшем"""
    print_step("3. Тестирование управления кэшем")
    
    # 1. Получаем статистику
    print("3.1 Статистика кэша...")
    response = requests.get(f"{BASE_URL}/api/v1/cache/stats")
    stats = response.json()["stats"]
    print(f"   Всего ключей: {stats.get('total_keys', 0)}")
    print(f"   Пользователей в кэше: {stats.get('user_cache_count', 0)}")
    print(f"   Продукции в кэше: {stats.get('product_cache_count', 0)}")
    print(f"   Использование памяти: {stats.get('memory_usage', 'N/A')}")
    
    # 2. Список ключей
    print("\n3.2 Список ключей...")
    for pattern in ["user:*", "product:*"]:
        response = requests.get(
            f"{BASE_URL}/api/v1/cache/keys",
            params={"pattern": pattern}
        )
        result = response.json()
        print(f"   {pattern}: {result['count']} ключей")
        if result['keys']:
            for key in result['keys'][:3]:  # Показываем первые 3 ключа
                print(f"     - {key}")
            if len(result['keys']) > 3:
                print(f"     ... и еще {len(result['keys']) - 3} ключей")
    
    # 3. Очистка всего кэша
    print("\n3.3 Очистка всего кэша...")
    response = requests.delete(f"{BASE_URL}/api/v1/cache/clear")
    print(f"   Ответ: {response.json()}")
    
    # 4. Проверяем очистку
    print("\n3.4 Проверка очистки...")
    response = requests.get(f"{BASE_URL}/api/v1/cache/stats")
    stats = response.json()["stats"]
    print(f"   Всего ключей после очистки: {stats.get('total_keys', 0)}")

def test_ttl_functionality():
    """Тестирование TTL (время жизни кэша)"""
    print_step("4. Тестирование TTL (время жизни)")
    
    # Создаем тестовые данные
    test_user = {"id": "temp_user", "name": "Временный пользователь"}
    test_product = {"id": "temp_prod", "name": "Временный продукт"}
    
    # Кэшируем с разным TTL
    requests.post(f"{BASE_URL}/api/v1/cache/users/temp_123", json=test_user)
    requests.post(f"{BASE_URL}/api/v1/cache/products/temp_456", json=test_product)
    
    print("Данные закэшированы с разным TTL:")
    print("  - Пользователь: 1 час (3600 секунд)")
    print("  - Продукт: 10 минут (600 секунд)")
    
    # Проверяем TTL
    response = requests.get(f"{BASE_URL}/api/v1/cache/users/temp_123")
    print(f"\nTTL пользователя: {response.json().get('ttl_seconds', 'N/A')}")
    
    response = requests.get(f"{BASE_URL}/api/v1/cache/products/temp_456")
    print(f"TTL продукта: {response.json().get('ttl_seconds', 'N/A')}")

def main():
    """Основная функция тестирования"""
    print("="*60)
    print("ТЕСТИРОВАНИЕ СИСТЕМЫ КЭШИРОВАНИЯ")
    print("="*60)
    
    try:
        # Проверяем доступность сервера
        response = requests.get(f"{BASE_URL}/health", timeout=5)
        if response.status_code != 200:
            print("Ошибка: Сервер не доступен")
            return
        
        # Запускаем тесты
        test_user_caching()
        test_product_caching()
        test_cache_management()
        test_ttl_functionality()
        
        print("\n" + "="*60)
        print("ВСЕ ТЕСТЫ ВЫПОЛНЕНЫ УСПЕШНО!")
        print("="*60)
        
    except requests.exceptions.ConnectionError:
        print("Ошибка: Не удалось подключиться к серверу")
        print(f"Убедитесь что сервер запущен на {BASE_URL}")
    except Exception as e:
        print(f"Ошибка при тестировании: {e}")

if __name__ == "__main__":
    main()