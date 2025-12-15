import sqlite3
import os
from datetime import date
from pathlib import Path

def check_sqlite_reports():
    db_path = Path("test.db")
    
    if not db_path.exists():
        print("Файл БД не найден: test.db")
        return False
    
    print(f"Проверяем БД: {db_path}")
    
    try:
        conn = sqlite3.connect(str(db_path))
        cursor = conn.cursor()
        
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='daily_order_reports'")
        table_exists = cursor.fetchone()
        
        if not table_exists:
            print("Таблица 'daily_order_reports' не найдена")
            return False
        
        print("Таблица 'daily_order_reports' существует")
        
        cursor.execute("PRAGMA table_info(daily_order_reports)")
        columns = cursor.fetchall()
        
        print("Структура таблицы:")
        print("id | name | type | notnull | default | pk")
        for col in columns:
            print(f"{col[0]} | {col[1]} | {col[2]} | {col[3]} | {col[4]} | {col[5]}")
        
        cursor.execute("SELECT COUNT(*) FROM daily_order_reports")
        count = cursor.fetchone()[0]
        print(f"Записей в таблице: {count}")
        
        if count > 0:
            cursor.execute("SELECT id, report_at, order_id, count_product FROM daily_order_reports ORDER BY created_at DESC LIMIT 3")
            print("Последние записи:")
            for row in cursor.fetchall():
                print(f"  ID: {row[0][:8]}...")
                print(f"  Дата отчета: {row[1]}")
                print(f"  ID заказа: {row[2][:8]}...")
                print(f"  Количество: {row[3]}")
        
        cursor.execute("SELECT id, quantity FROM orders LIMIT 1")
        order = cursor.fetchone()
        
        if order:
            order_id, quantity = order
            today = date.today().isoformat()
            
            cursor.execute("INSERT INTO daily_order_reports (report_at, order_id, count_product, created_at) VALUES (?, ?, ?, datetime('now'))", (today, order_id, quantity or 1))
            
            conn.commit()
            print(f"Тестовая запись добавлена:")
            print(f"   Дата: {today}")
            print(f"   Заказ: {order_id[:8]}...")
            print(f"   Количество: {quantity or 1}")
        
        cursor.execute("SELECT COUNT(*) FROM daily_order_reports")
        final_count = cursor.fetchone()[0]
        
        print(f"ИТОГО записей в daily_order_reports: {final_count}")
        
        conn.close()
        return True
        
    except sqlite3.Error as e:
        print(f"Ошибка SQLite: {e}")
        return False
    except Exception as e:
        print(f"Ошибка: {e}")
        return False

def check_alembic_migration():
    print("ПРОВЕРКА MИГРАЦИЙ ALEMBIC")
    
    migrations_dir = Path("alembic/versions")
    latest_migration = None
    
    if migrations_dir.exists():
        migration_files = sorted(migrations_dir.glob("*.py"), reverse=True)
        if migration_files:
            latest_migration = migration_files[0]
            print(f"Последняя миграция: {latest_migration.name}")
    
    return latest_migration

def main():
    print("ПРОВЕРКА ТАБЛИЦЫ ОТЧЕТОВ (SQLite + Alembic)")
    
    migration = check_alembic_migration()
    
    if not migration:
        print("Файлы миграций не найдены")
        return
    
    success = check_sqlite_reports()
    
    if success:
        print("Таблица 'daily_order_reports' создана и работает")
    else:
        print("Есть проблемы с созданием таблицы")
    
    print("Для просмотра всех отчетов выполните:")
    print("   sqlite3 test.db \"SELECT * FROM daily_order_reports;\"")

if __name__ == "__main__":
    main()