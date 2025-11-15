import os
from typing import AsyncGenerator
from litestar import Litestar
from litestar.di import Provide
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
import uvicorn

from app.controllers.user_controller import UserController
from app.repositories.user_repository import UserRepository
from app.services.user_service import UserService

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")

engine = create_async_engine(DATABASE_URL, echo=True)
async_session_factory = async_sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

async def provide_db_session() -> AsyncGenerator[AsyncSession, None]:
    """Провайдер сессии базы данных"""
    async with async_session_factory() as session:
        try:
            yield session
        finally:
            await session.close()

def provide_user_repository() -> UserRepository:
    return UserRepository()

def provide_user_service(user_repository: UserRepository) -> UserService:
    return UserService(user_repository)

app = Litestar(
    route_handlers=[UserController],
    dependencies={
        "db_session": Provide(provide_db_session, sync_to_thread=False),
        "user_repository": Provide(provide_user_repository, sync_to_thread=False),
        "user_service": Provide(provide_user_service, sync_to_thread=False),
    },
)

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)