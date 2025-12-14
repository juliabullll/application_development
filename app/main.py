import asyncio
import threading
import uvicorn
from litestar import Litestar, get
from litestar.openapi import OpenAPIConfig
import os
import sys
from pathlib import Path
from datetime import datetime

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.controllers.order_controller import OrderController
from app.controllers.product_controller import ProductController
from app.controllers.test_controller import TestController

from app.controllers.cache_controller import (
    UserCacheController, 
    ProductCacheController, 
    CacheManagementController
)

try:
    from app.rabbitmq.consumer import app as faststream_app
    RABBITMQ_AVAILABLE = True
except ImportError as e:
    print(f"RabbitMQ consumer not available: {e}")
    RABBITMQ_AVAILABLE = False
    faststream_app = None

# Импорт Redis клиента
try:
    from app.redis.client import get_redis
    REDIS_AVAILABLE = True
except ImportError as e:
    print(f"Redis not available: {e}")
    REDIS_AVAILABLE = False

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))


async def start_rabbitmq_consumer():
    if not RABBITMQ_AVAILABLE or faststream_app is None:
        print("RabbitMQ consumer not available")
        return
    
    try:
        print("Starting RabbitMQ consumer...")
        await faststream_app.run()
    except Exception as e:
        print(f"Error starting RabbitMQ consumer: {e}")


@get("/")
async def root() -> dict:
    return {
        "message": "Order Processing System API",
        "version": "1.0.0",
        "endpoints": {
            "orders": "/api/v1/orders",
            "products": "/api/v1/products",
            "health": "/health",
            "test": "/test",
            "cache": "/cache",
            "redis_strings": "/redis/strings",
            "redis_lists": "/redis/lists",
            "redis_sets": "/redis/sets",
            "redis_hashes": "/redis/hashes",
            "redis_sorted_sets": "/redis/sorted-sets",
            "docs": "/schema"
        }
    }


@get("/health")
async def health_check() -> dict:
    redis_status = "unknown"
    redis_details = {}
    
    if REDIS_AVAILABLE:
        try:
            redis_client = get_redis()
            if redis_client:
                try:
                    redis_ping = redis_client.ping()
                    redis_status = "connected" if redis_ping else "error"
                    
                    # Тестируем запись/чтение
                    test_key = f"health_test_{datetime.now().strftime('%H%M%S')}"
                    redis_client.set(test_key, "test_value", ex=10)
                    retrieved = redis_client.get(test_key)
                    
                    redis_details = {
                        "ping": redis_ping,
                        "test_write_read": retrieved == "test_value",
                        "test_key": test_key,
                        "type": "real" if hasattr(redis_client, '_data') else "mock"
                    }
                except AttributeError:
                    # Mock Redis может не иметь всех методов
                    redis_status = "mock"
                    redis_details = {"type": "mock"}
            else:
                redis_status = "client_not_initialized"
        except Exception as e:
            redis_status = f"error: {str(e)}"
    else:
        redis_status = "not_configured"
    
    return {
        "status": "ok",
        "timestamp": datetime.now().isoformat(),
        "service": "Order Processing System",
        "services": {
            "rabbitmq": "connected" if RABBITMQ_AVAILABLE else "disconnected",
            "redis": redis_status,
            "redis_details": redis_details
        }
    }


@get("/test")
async def test_endpoint() -> dict:
    return {"message": "API is working!"}


@get("/cache")
async def cache_example(key: str, value: str = None) -> dict:
    """Пример работы с Redis кэшем"""
    if not REDIS_AVAILABLE:
        return {"error": "Redis недоступен"}
    
    try:
        redis_client = get_redis()
        if not redis_client:
            return {"error": "Redis client не инициализирован"}
        
        if value:
            # Сохраняем значение
            if hasattr(redis_client, 'set'):
                redis_client.set(key, value, ex=3600)
                return {
                    "status": "saved", 
                    "key": key, 
                    "value": value,
                    "ttl_seconds": 3600,
                    "type": "mock" if hasattr(redis_client, '_data') else "real"
                }
            else:
                return {"error": "Redis client не поддерживает set"}
        else:
            # Получаем значение
            if hasattr(redis_client, 'get'):
                cached_value = redis_client.get(key)
                ttl = redis_client.ttl(key) if hasattr(redis_client, 'ttl') else None
                return {
                    "key": key, 
                    "value": cached_value,
                    "ttl_seconds": ttl if ttl and ttl > 0 else None,
                    "type": "mock" if hasattr(redis_client, '_data') else "real"
                }
            else:
                return {"error": "Redis client не поддерживает get"}
    except Exception as e:
        return {"error": f"Redis error: {str(e)}"}


@get("/redis/strings")
async def redis_strings(key: str = "test_key", value: str = "test_value") -> dict:
    """Работа со строками Redis"""
    client = get_redis()
    if not client:
        return {"error": "Redis недоступен"}
    
    client.set(key, value)
    retrieved = client.get(key)
    ttl = client.ttl(key)
    
    client.set("counter", 0)
    client.incr("counter")
    
    return {
        "operation": "strings",
        "set_key": key,
        "get_value": retrieved,
        "ttl": ttl,
        "counter": client.get("counter")
    }


@get("/redis/lists")
async def redis_lists() -> dict:
    """Работа со списками Redis"""
    client = get_redis()
    if not client:
        return {"error": "Redis недоступен"}
    
    client.delete("test_tasks")
    client.lpush("test_tasks", "task1", "task2")
    client.rpush("test_tasks", "task3", "task4")
    all_tasks = client.lrange("test_tasks", 0, -1)
    length = client.llen("test_tasks")
    
    return {
        "operation": "lists",
        "all_tasks": all_tasks,
        "length": length
    }


@get("/redis/sets")
async def redis_sets() -> dict:
    """Работа с множествами Redis"""
    client = get_redis()
    if not client:
        return {"error": "Redis недоступен"}
    
    client.sadd("test_tags", "python", "redis", "database")
    client.sadd("test_langs", "python", "java")
    intersection = client.sinter("test_tags", "test_langs")
    
    return {
        "operation": "sets",
        "tags": list(client.smembers("test_tags")),
        "intersection": list(intersection)
    }


@get("/redis/hashes")
async def redis_hashes() -> dict:
    """Работа с хэшами Redis"""
    client = get_redis()
    if not client:
        return {"error": "Redis недоступен"}
    
    client.hset("test_user:1", mapping={
        "name": "Иван",
        "age": "25",
        "city": "Москва"
    })
    all_data = client.hgetall("test_user:1")
    
    return {
        "operation": "hashes",
        "user_data": all_data
    }


@get("/redis/sorted-sets")
async def redis_sorted_sets() -> dict:
    """Работа с упорядоченными множествами Redis"""
    client = get_redis()
    if not client:
        return {"error": "Redis недоступен"}
    
    client.zadd("test_leaderboard", {
        "player1": 100,
        "player2": 200,
        "player3": 150
    })
    top_players = client.zrange("test_leaderboard", 0, 2, withscores=True)
    
    return {
        "operation": "sorted_sets",
        "top_players": [(player.decode() if isinstance(player, bytes) else player, score) 
                       for player, score in top_players]
    }


app = Litestar(
    route_handlers=[
        root,
        health_check,
        test_endpoint,
        cache_example,
        redis_strings,
        redis_lists,
        redis_sets,
        redis_hashes,
        redis_sorted_sets,
        OrderController,
        ProductController,
        TestController,
        UserCacheController,      
        ProductCacheController,  
        CacheManagementController 
    ],
    debug=True,
    cors_config={"allow_origins": ["*"]},
    openapi_config=OpenAPIConfig(
        title="Order Processing System API",
        version="1.0.0",
        description="API для обработки заказов и продукции через RabbitMQ и Redis"
    )
)


async def startup():
    print("Starting application...")
    
    # Инициализация Redis
    if REDIS_AVAILABLE:
        try:
            redis_client = get_redis()
            if redis_client:
                print(f"[Redis] Initialized: {type(redis_client)}")
                if hasattr(redis_client, '_data'):
                    print("[Redis] Using MOCK Redis (in-memory storage)")
                else:
                    print("[Redis] Using REAL Redis server")
                # Тестируем подключение
                try:
                    print(f"[Redis] Ping: {redis_client.ping()}")
                except:
                    print("[Redis] Ping method not available")
        except Exception as e:
            print(f"[Redis] Error initializing: {e}")
    
    # Запуск RabbitMQ consumer
    if RABBITMQ_AVAILABLE:
        import asyncio as async_lib
        task = async_lib.create_task(start_rabbitmq_consumer())
        print("RabbitMQ consumer starting in background task...")


app.on_startup.append(startup)


if __name__ == "__main__":
    print(f"Starting server on {HOST}:{PORT}")
    print(f"RabbitMQ available: {RABBITMQ_AVAILABLE}")
    print(f"Redis available: {REDIS_AVAILABLE}")
    
    uvicorn.run(
        "app.main:app",
        host=HOST,
        port=PORT,
        reload=True
    )   