"""Сервис для кэширования данных с инвалидацией"""

from app.redis.client import get_redis
from datetime import datetime
import json
from typing import Any, Optional, Dict, List

class CacheService:
    """Сервис для работы с кэшем Redis"""
    
    def __init__(self):
        self.redis = get_redis()
    
    def _generate_key(self, prefix: str, identifier: str) -> str:
        """Генерация ключа для кэша"""
        return f"{prefix}:{identifier}"
    
    def cache_user_data(self, user_id: str, user_data: Dict[str, Any]) -> bool:
        """
        Кэширование данных пользователя на 1 час
        
        Args:
            user_id: ID пользователя
            user_data: Данные пользователя
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            key = self._generate_key("user", user_id)
            # Сериализуем данные в JSON
            serialized_data = json.dumps(user_data, ensure_ascii=False)
            # Сохраняем на 1 час (3600 секунд)
            result = self.redis.setex(key, 3600, serialized_data)
            
            # Также сохраняем метаданные для инвалидации
            meta_key = f"{key}:meta"
            meta_data = {
                "cached_at": datetime.now().isoformat(),
                "ttl": 3600,
                "type": "user"
            }
            self.redis.setex(meta_key, 3600, json.dumps(meta_data))
            
            return result
        except Exception as e:
            print(f"Error caching user data: {e}")
            return False
    
    def get_cached_user(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение закэшированных данных пользователя
        
        Args:
            user_id: ID пользователя
        
        Returns:
            dict or None: Данные пользователя или None если не найдено
        """
        try:
            key = self._generate_key("user", user_id)
            cached_data = self.redis.get(key)
            
            if cached_data:
                # Десериализуем из JSON
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Error getting cached user: {e}")
            return None
    
    def invalidate_user_cache(self, user_id: str) -> bool:
        """
        Инвалидация кэша пользователя при обновлении данных
        
        Args:
            user_id: ID пользователя
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            key = self._generate_key("user", user_id)
            meta_key = f"{key}:meta"
            
            # Удаляем основной кэш и метаданные
            self.redis.delete(key)
            self.redis.delete(meta_key)
            
            # Также удаляем связанные данные
            pattern = f"user:{user_id}:*"
            keys = self.redis.keys(pattern)
            if keys:
                self.redis.delete(*keys)
            
            return True
        except Exception as e:
            print(f"Error invalidating user cache: {e}")
            return False
    
    def cache_product_data(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        """
        Кэширование данных продукции на 10 минут
        
        Args:
            product_id: ID продукции
            product_data: Данные продукции
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            key = self._generate_key("product", product_id)
            # Сериализуем данные в JSON
            serialized_data = json.dumps(product_data, ensure_ascii=False)
            # Сохраняем на 10 минут (600 секунд)
            result = self.redis.setex(key, 600, serialized_data)
            
            # Также сохраняем метаданные
            meta_key = f"{key}:meta"
            meta_data = {
                "cached_at": datetime.now().isoformat(),
                "ttl": 600,
                "type": "product"
            }
            self.redis.setex(meta_key, 600, json.dumps(meta_data))
            
            return result
        except Exception as e:
            print(f"Error caching product data: {e}")
            return False
    
    def get_cached_product(self, product_id: str) -> Optional[Dict[str, Any]]:
        """
        Получение закэшированных данных продукции
        
        Args:
            product_id: ID продукции
        
        Returns:
            dict or None: Данные продукции или None если не найдено
        """
        try:
            key = self._generate_key("product", product_id)
            cached_data = self.redis.get(key)
            
            if cached_data:
                # Десериализуем из JSON
                return json.loads(cached_data)
            return None
        except Exception as e:
            print(f"Error getting cached product: {e}")
            return None
    
    def update_product_cache(self, product_id: str, product_data: Dict[str, Any]) -> bool:
        """
        Обновление кэша продукции при изменении данных
        
        Args:
            product_id: ID продукции
            product_data: Новые данные продукции
        
        Returns:
            bool: True если успешно, False если ошибка
        """
        try:
            # Обновляем кэш с тем же TTL (10 минут)
            return self.cache_product_data(product_id, product_data)
        except Exception as e:
            print(f"Error updating product cache: {e}")
            return False
    
    def get_cache_stats(self) -> Dict[str, Any]:
        """
        Получение статистики по кэшу
        
        Returns:
            dict: Статистика кэша
        """
        try:
            stats = {
                "user_cache_count": len(self.redis.keys("user:*")),
                "product_cache_count": len(self.redis.keys("product:*")),
                "total_keys": len(self.redis.keys("*")),
                "memory_usage": self.redis.info().get("used_memory_human", "N/A")
            }
            
            # Получаем TTL для некоторых ключей
            sample_users = self.redis.keys("user:*")[:3]
            sample_products = self.redis.keys("product:*")[:3]
            
            ttl_info = {}
            for key in sample_users + sample_products:
                if not key.endswith(":meta"):
                    ttl = self.redis.ttl(key)
                    ttl_info[key.decode() if isinstance(key, bytes) else key] = ttl
            
            stats["sample_ttl"] = ttl_info
            return stats
        except Exception as e:
            print(f"Error getting cache stats: {e}")
            return {"error": str(e)}
    
    def clear_all_cache(self) -> bool:
        """
        Очистка всего кэша
        
        Returns:
            bool: True если успешно
        """
        try:
            self.redis.flushdb()
            return True
        except Exception as e:
            print(f"Error clearing cache: {e}")
            return False

# Глобальный экземпляр сервиса
cache_service = CacheService()