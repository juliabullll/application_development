from datetime import datetime
"""Контроллеры для работы с кэшем"""

from litestar import Controller, get, post, delete
from litestar.params import Parameter
from litestar.status_codes import HTTP_200_OK, HTTP_201_CREATED, HTTP_404_NOT_FOUND
from typing import Dict, Any, Optional

from app.services.cache_service import cache_service


class UserCacheController(Controller):
    """Контроллер для кэширования данных пользователей"""
    path = "/api/v1/cache/users"
    
    @get("/{user_id:str}", status_code=HTTP_200_OK)
    async def get_cached_user(self, user_id: str) -> Dict[str, Any]:
        """
        Получение закэшированных данных пользователя
        
        Args:
            user_id: ID пользователя
        """
        cached_data = cache_service.get_cached_user(user_id)
        
        if cached_data:
            return {
                "status": "success",
                "source": "cache",
                "data": cached_data,
                "message": "Данные получены из кэша"
            }
        else:
            user_data = {
                "id": user_id,
                "name": f"Пользователь {user_id}",
                "email": f"user{user_id}@example.com",
                "created_at": "2024-01-01T00:00:00"
            }
            
            # Кэшируем данные
            cache_service.cache_user_data(user_id, user_data)
            
            return {
                "status": "success",
                "source": "database",
                "data": user_data,
                "message": "Данные получены из БД и закэшированы"
            }
    
    @post("/{user_id:str}", status_code=HTTP_201_CREATED)
    async def cache_user(self, user_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Кэширование данных пользователя
        
        Args:
            user_id: ID пользователя
            data: Данные пользователя
        """
        success = cache_service.cache_user_data(user_id, data)
        
        if success:
            return {
                "status": "success",
                "message": f"Данные пользователя {user_id} закэшированы на 1 час",
                "user_id": user_id,
                "ttl_seconds": 3600
            }
        else:
            return {
                "status": "error",
                "message": "Ошибка кэширования данных"
            }
    
    @delete("/{user_id:str}", status_code=HTTP_200_OK)
    async def invalidate_user_cache(self, user_id: str) -> Dict[str, Any]:
        """
        Инвалидация кэша пользователя
        
        Args:
            user_id: ID пользователя
        """
        success = cache_service.invalidate_user_cache(user_id)
        
        if success:
            return {
                "status": "success",
                "message": f"Кэш пользователя {user_id} очищен"
            }
        else:
            return {
                "status": "error",
                "message": f"Ошибка очистки кэша пользователя {user_id}"
            }


class ProductCacheController(Controller):
    """Контроллер для кэширования данных продукции"""
    path = "/api/v1/cache/products"
    
    @get("/{product_id:str}", status_code=HTTP_200_OK)
    async def get_cached_product(self, product_id: str) -> Dict[str, Any]:
        """
        Получение закэшированных данных продукции
        
        Args:
            product_id: ID продукции
        """
        cached_data = cache_service.get_cached_product(product_id)
        
        if cached_data:
            return {
                "status": "success",
                "source": "cache",
                "data": cached_data,
                "message": "Данные получены из кэша",
                "ttl_seconds": 600  # Фиксированное значение для MockRedis
            }
        else:
            # Здесь можно получить данные из БД
            # Для примера возвращаем заглушку
            product_data = {
                "id": product_id,
                "name": f"Продукт {product_id}",
                "price": 100.0,
                "quantity": 50,
                "category": "electronics",
                "created_at": "2024-01-01T00:00:00"
            }
            
            # Кэшируем данные
            cache_service.cache_product_data(product_id, product_data)
            
            return {
                "status": "success",
                "source": "database",
                "data": product_data,
                "message": "Данные получены из БД и закэшированы на 10 минут",
                "ttl_seconds": 600
            }
    
    @post("/{product_id:str}", status_code=HTTP_201_CREATED)
    async def cache_product(self, product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Кэширование данных продукции
        
        Args:
            product_id: ID продукции
            data: Данные продукции
        """
        success = cache_service.cache_product_data(product_id, data)
        
        if success:
            return {
                "status": "success",
                "message": f"Данные продукции {product_id} закэшированы на 10 минут",
                "product_id": product_id,
                "ttl_seconds": 600
            }
        else:
            return {
                "status": "error",
                "message": "Ошибка кэширования данных"
            }
    
    @post("/{product_id:str}/update", status_code=HTTP_200_OK)
    async def update_product_cache(self, product_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Обновление кэша продукции
        
        Args:
            product_id: ID продукции
            data: Обновленные данные продукции
        """
        success = cache_service.update_product_cache(product_id, data)
        
        if success:
            return {
                "status": "success",
                "message": f"Кэш продукции {product_id} обновлен",
                "product_id": product_id,
                "ttl_seconds": 600
            }
        else:
            return {
                "status": "error",
                "message": f"Ошибка обновления кэша продукции {product_id}"
            }


class CacheManagementController(Controller):
    """Контроллер для управления кэшем"""
    path = "/api/v1/cache"
    
    @get("/stats", status_code=HTTP_200_OK)
    async def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получение статистики кэша
        """
        stats = cache_service.get_cache_stats()
        
        return {
            "status": "success",
            "stats": stats,
            "timestamp": datetime.now().isoformat()
        }
    
    @delete("/clear", status_code=HTTP_200_OK)
    async def clear_all_cache(self) -> Dict[str, Any]:
        """
        Очистка всего кэша
        """
        success = cache_service.clear_all_cache()
        
        if success:
            return {
                "status": "success",
                "message": "Весь кэш очищен"
            }
        else:
            return {
                "status": "error",
                "message": "Ошибка очистки кэша"
            }
    
    @get("/keys", status_code=HTTP_200_OK)
    async def list_cache_keys(
        self,
        pattern: str = Parameter(default="*", description="Шаблон для поиска ключей")
    ) -> Dict[str, Any]:
        """
        Список ключей в кэше
        
        Args:
            pattern: Шаблон для поиска (например: "user:*", "product:*", "*")
        """
        try:
            keys = cache_service.redis.keys(pattern)
            
            # Преобразуем bytes в строки если нужно
            keys_list = []
            for key in keys:
                if isinstance(key, bytes):
                    keys_list.append(key.decode('utf-8'))
                else:
                    keys_list.append(key)
            
            return {
                "status": "success",
                "pattern": pattern,
                "count": len(keys_list),
                "keys": keys_list
            }
        except Exception as e:
            return {
                "status": "error",
                "message": f"Ошибка получения ключей: {str(e)}"
            }