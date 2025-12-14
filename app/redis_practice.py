"""Практика работы с Redis - все типы данных"""

import sys
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from app.redis.client import get_redis

def practice_redis_operations():
    """Практическое выполнение всех операций из задания"""
    print("Практика работы с Redis")
    print("=" * 50)
    
    # Получаем клиент Redis
    client = get_redis()
    if not client:
        print("Ошибка: Не удалось подключиться к Redis")
        return
    
    try:
        # Очистка старых данных
        client.delete("user:name", "session:123", "counter", "tasks", 
                     "tags", "languages", "user:1000", "leaderboard")
        
        # 1. Строки (Strings)
        # Установка и получение значения
        client.set("user:name", "Иван")
        name = client.get("user:name")
        print(f"client.set('user:name', 'Иван')")
        print(f"client.get('user:name') = {name}")
        
        # Установка с TTL (время жизни)
        client.setex("session:123", 3600, "active")  # 1 час
        ttl = client.ttl("session:123")
        print(f"\nclient.setex('session:123', 3600, 'active')")
        print(f"TTL сессии: {ttl} секунд")
        
        # Работа с числами
        client.set("counter", 0)
        client.incr("counter")        # Увеличить на 1
        client.incrby("counter", 5)   # Увеличить на 5
        client.decr("counter")        # Уменьшить на 1
        
        counter_value = client.get("counter")
        print(f"\nclient.set('counter', 0)")
        print(f"client.incr('counter')")
        print(f"client.incrby('counter', 5)")
        print(f"client.decr('counter')")
        print(f"Итоговое значение: {counter_value}")
        
        # 2. Списки (Lists)
        # Добавление элементов
        client.lpush("tasks", "task1", "task2")  # В начало
        client.rpush("tasks", "task3", "task4")  # В конец
        
        # Получение всех элементов
        tasks = client.lrange("tasks", 0, -1)
        print(f"client.lpush('tasks', 'task1', 'task2')")
        print(f"client.rpush('tasks', 'task3', 'task4')")
        print(f"client.lrange('tasks', 0, -1) = {tasks}")
        
        # Получение и удаление элементов
        first_task = client.lpop("tasks")  # Удалить и вернуть первый
        last_task = client.rpop("tasks")   # Удалить и вернуть последний
        print(f"\nclient.lpop('tasks') = {first_task}")
        print(f"client.rpop('tasks') = {last_task}")
        
        # Получение длины списка
        length = client.llen("tasks")
        print(f"client.llen('tasks') = {length}")
        
        # 3. Множества (Sets)
        # Добавление элементов
        client.sadd("tags", "python", "redis", "database")
        client.sadd("languages", "python", "java", "javascript")
        
        print(f"client.sadd('tags', 'python', 'redis', 'database')")
        print(f"client.sadd('languages', 'python', 'java', 'javascript')")
        
        # Проверка принадлежности
        is_member = client.sismember("tags", "python")
        print(f"\nclient.sismember('tags', 'python') = {is_member}")
        
        # Получение всех элементов
        all_tags = client.smembers("tags")
        print(f"client.smembers('tags') = {all_tags}")
        
        # Операции с множествами
        intersection = client.sinter("tags", "languages")  # Пересечение
        union = client.sunion("tags", "languages")         # Объединение
        difference = client.sdiff("tags", "languages")     # Разность
        
        print(f"\nclient.sinter('tags', 'languages') = {intersection}")
        print(f"client.sunion('tags', 'languages') = {union}")
        print(f"client.sdiff('tags', 'languages') = {difference}")
        
        # 4. Хэши (Hashes)   
        # Установка полей
        client.hset("user:1000", mapping={
            "name": "Иван",
            "age": "30",
            "city": "Москва"
        })
        
        print("client.hset('user:1000', mapping={'name': 'Иван', 'age': '30', 'city': 'Москва'})")
        
        # Получение значений
        name = client.hget("user:1000", "name")
        all_data = client.hgetall("user:1000")
        print(f"\nclient.hget('user:1000', 'name') = {name}")
        print(f"client.hgetall('user:1000') = {all_data}")
        
        # Проверка существования поля
        exists = client.hexists("user:1000", "age")
        print(f"\nclient.hexists('user:1000', 'age') = {exists}")
        
        # Получение всех ключей или значений
        keys = client.hkeys("user:1000")
        values = client.hvals("user:1000")
        print(f"\nclient.hkeys('user:1000') = {keys}")
        print(f"client.hvals('user:1000') = {values}")
        
        # 5. Упорядоченные множества (Sorted Sets)
        # Добавление элементов с оценкой
        client.zadd("leaderboard", {
            "player1": 100,
            "player2": 200,
            "player3": 150
        })
        
        print("client.zadd('leaderboard', {'player1': 100, 'player2': 200, 'player3': 150})")
        
        # Получение элементов по рангу
        top_players = client.zrange("leaderboard", 0, 2, withscores=True)
        print(f"\nclient.zrange('leaderboard', 0, 2, withscores=True) = {top_players}")
        
        # Получение элементов по оценке
        players_by_score = client.zrangebyscore("leaderboard", 100, 200)
        print(f"\nclient.zrangebyscore('leaderboard', 100, 200) = {players_by_score}")
        
        # Получение ранга элемента
        rank = client.zrank("leaderboard", "player1")
        print(f"\nclient.zrank('leaderboard', 'player1') = {rank}")
    except Exception as e:
        print(f"\nОшибка: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    practice_redis_operations()