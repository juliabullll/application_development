from typing import List
from litestar import Controller, get, post, put, delete
from litestar.params import Parameter, Body  # Import Body from here
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession

from app.services.user_service import UserService
from app.models import UserCreate, UserUpdate, UserResponse, UsersListResponse, user_to_response


class UserController(Controller):
    """Контроллер для управления пользователями через HTTP API"""
    
    path = "/users"

    @get("/{user_id:str}")
    async def get_user_by_id(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        user_id: str,
    ) -> UserResponse:
        """Получить пользователя по ID"""
        from uuid import UUID
        
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid user ID format: {user_id}")
        
        user = await user_service.get_by_id(db_session, user_uuid)
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        
        return user_to_response(user)

    @get()
    async def get_all_users(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        count: int = Parameter(gt=0, le=100, default=10),
        page: int = Parameter(gt=0, default=1),
    ) -> UsersListResponse:
        """Получить список пользователей с пагинацией и общим количеством"""
        users = await user_service.get_by_filter(db_session, count, page)
        
        total_count = await user_service.get_total_count(db_session)
        total_pages = (total_count + count - 1) // count if total_count > 0 else 0
        
        return UsersListResponse(
            users=[user_to_response(user) for user in users],
            total_count=total_count,
            page=page,
            per_page=count,
            total_pages=total_pages
        )

    @post()
    async def create_user(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        data: UserCreate = Body(),  
    ) -> UserResponse:
        """Создать нового пользователя"""
        user = await user_service.create(db_session, data)
        return user_to_response(user)

    @delete("/{user_id:str}")
    async def delete_user(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        user_id: str,
    ) -> None:
        """Удалить пользователя"""
        from uuid import UUID
        
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid user ID format: {user_id}")
        
        success = await user_service.delete(db_session, user_uuid)
        if not success:
            raise NotFoundException(detail=f"User with ID {user_id} not found")

    @put("/{user_id:str}")
    async def update_user(
        self,
        user_service: UserService,
        db_session: AsyncSession,
        user_id: str,
        data: UserUpdate = Body(),  
    ) -> UserResponse:
        """Обновить данные пользователя"""
        from uuid import UUID
        
        try:
            user_uuid = UUID(user_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid user ID format: {user_id}")
        
        user = await user_service.update(db_session, user_uuid, data)
        
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        
        return user_to_response(user)