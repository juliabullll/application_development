import redis
import os

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6379))
REDIS_DB = int(os.getenv("REDIS_DB", 0))

_redis_client = None

def get_redis():
    global _redis_client
    if _redis_client is None:
        try:
            _redis_client = redis.Redis(
                host=REDIS_HOST,
                port=REDIS_PORT,
                db=REDIS_DB,
                decode_responses=True
            )
            _redis_client.ping()
            print(f"[Redis] Connected to {REDIS_HOST}:{REDIS_PORT}")
        except Exception as e:
            print(f"[Redis] Connection error: {e}")
            # Fallback to mock
            _redis_client = MockRedis()
    return _redis_client

class MockRedis:
    def __init__(self):
        self._data = {}
        print("[Redis] Using mock Redis")
    
    def set(self, key, value, ex=None):
        self._data[key] = value
        return True
    
    def get(self, key):
        return self._data.get(key)
    
    def delete(self, *keys):
        count = 0
        for key in keys:
            if key in self._data:
                del self._data[key]
                count += 1
        return count
    
    def ping(self):
        return True
    
    def keys(self, pattern="*"):
        import fnmatch
        return [k for k in self._data.keys() if fnmatch.fnmatch(k, pattern)]
    
    def exists(self, *keys):
        return sum(1 for key in keys if key in self._data)
    
    def setex(self, key, time, value):
        self._data[key] = value
        return True
    
    def incr(self, key):
        current = int(self._data.get(key, 0))
        self._data[key] = current + 1
        return current + 1