import asyncio
import os
from sqlalchemy.ext.asyncio import create_async_engine
from app.models import Base

async def init_database():
    database_url = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    engine = create_async_engine(database_url, echo=True)
    
    # Создаем таблицы
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    
    print("Database tables created successfully!")
    
    # Добавляем тестовые данные
    from app.data import add_users_and_addresses
    add_users_and_addresses()
    
    print("Test data added successfully!")
    await engine.dispose()

if __name__ == "__main__":
    asyncio.run(init_database())