import pytest
import asyncio
import sys
import os
from pathlib import Path

# Добавляем корень проекта в Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from litestar.testing import TestClient
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from app.main import app
from app.models import Base
from app.repositories.user_repository import UserRepository

TEST_DATABASE_URL = "sqlite+aiosqlite:///./test.db"

@pytest.fixture(scope="session")
def event_loop():
    """Создаем event loop для асинхронных тестов"""
    loop = asyncio.get_event_loop_policy().new_event_loop()
    yield loop
    loop.close()

@pytest.fixture(scope="session")
def engine():
    return create_async_engine(TEST_DATABASE_URL, echo=True)

@pytest.fixture(scope="session")
def setup_database(engine):
    """Синхронная фикстура для создания таблиц"""
    import asyncio
    
    async def async_setup():
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
            await conn.run_sync(Base.metadata.create_all)
        yield
        async with engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        gen = async_setup()
        loop.run_until_complete(gen.__anext__())
        yield
    except StopAsyncIteration:
        pass
    finally:
        try:
            loop.run_until_complete(gen.__anext__())
        except StopAsyncIteration:
            pass
        finally:
            loop.close()

@pytest.fixture
def session(engine, setup_database):
    """Синхронная фикстура для сессии"""
    import asyncio
    
    async def get_session():
        async_session = sessionmaker(
            engine, class_=AsyncSession, expire_on_commit=False
        )
        async with async_session() as session:
            return session
    
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    try:
        session_obj = loop.run_until_complete(get_session())
        yield session_obj
    finally:
        loop.run_until_complete(session_obj.close())
        loop.close()

@pytest.fixture
def user_repository(session):
    repo = UserRepository()
    repo.session = session
    return repo

@pytest.fixture
def client(setup_database):
    return TestClient(app=app)

@pytest.fixture
def product_repository(session):
    from app.repositories.product_repository import ProductRepository
    repo = ProductRepository()
    repo.session = session
    return repo

@pytest.fixture
def order_repository(session):
    from app.repositories.order_repository import OrderRepository
    repo = OrderRepository()
    repo.session = session
    return repo

