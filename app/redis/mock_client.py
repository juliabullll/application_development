import os
from typing import Optional, Any

class MockRedis:
    def __init__(self):
        self._data = {}
        print("[MockRedis] Initialized")
    
    def ping(self) -> bool:
        return True
    
    def set(self, key: str, value: Any, ex: Optional[int] = None) -> bool:
        self._data[key] = value
        return True
    
    def get(self, key: str) -> Optional[str]:
        return self._data.get(key)
    
    def ttl(self, key: str) -> int:
        return -1  # no expiration
    
    def keys(self, pattern: str = "*") -> list:
        return list(self._data.keys())
    
    def delete(self, *keys) -> int:
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count

# Глобальный инстанс
_mock_redis = None

def get_mock_redis():
    global _mock_redis
    if _mock_redis is None:
        _mock_redis = MockRedis()
    return _mock_redis