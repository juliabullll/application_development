import sys
import os
from pathlib import Path

project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine, text

# Подключение к БД
CONNECT_URL = "sqlite:///./test.db"
engine = create_engine(CONNECT_URL, echo=True)

def clear_tables():
    """Очистить таблицы перед созданием новых данных"""
    tables = ["daily_order_reports", "orders", "addresses", "users", "products"]
    
    with engine.connect() as conn:
        for table in tables:
            try:
                conn.execute(text(f"DELETE FROM {table}"))
                print(f"Таблица {table} очищена")
            except Exception as e:
                print(f"Таблица {table} не существует или ошибка: {e}")
        
        conn.commit()
        print("\nВсе таблицы очищены")

if __name__ == "__main__":
    clear_tables()