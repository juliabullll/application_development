from litestar import Controller, get, post, put, delete
from litestar.params import Parameter
from litestar.exceptions import NotFoundException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from uuid import UUID
from datetime import datetime

from app.models.database_models import User, UserCreate, UserUpdate, UserResponse, user_to_response

class UserController(Controller):
    path = "/api/users"
    
    @get("/")
    async def get_users(
        self,
        session: AsyncSession,
        page: int = Parameter(query="page", default=1, ge=1),
        per_page: int = Parameter(query="per_page", default=10, ge=1, le=100),
        search: str = Parameter(query="search", default="")
    ) -> dict:
        offset = (page - 1) * per_page
        
        query = select(User)
        if search:
            query = query.where(User.username.ilike(f"%{search}%"))
        
        result = await session.execute(query.offset(offset).limit(per_page))
        users = result.scalars().all()
        
        total_query = select(User)
        if search:
            total_query = total_query.where(User.username.ilike(f"%{search}%"))
        
        total_result = await session.execute(select(User.id))
        total_count = len(total_result.scalars().all())
        
        return {
            "users": [user_to_response(user) for user in users],
            "total_count": total_count,
            "page": page,
            "per_page": per_page,
            "total_pages": (total_count + per_page - 1) // per_page
        }
    
    @get("/{user_id:uuid}")
    async def get_user(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> dict:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        
        return {"user": user_to_response(user)}
    
    @post("/")
    async def create_user(
        self,
        session: AsyncSession,
        data: UserCreate
    ) -> dict:
        user = User(
            username=data.username,
            email=data.email,
            description=data.description
        )
        
        session.add(user)
        await session.commit()
        await session.refresh(user)
        
        return {
            "message": "User created successfully",
            "user": user_to_response(user)
        }
    
    @put("/{user_id:uuid}")
    async def update_user(
        self,
        session: AsyncSession,
        user_id: UUID,
        data: UserUpdate
    ) -> dict:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        
        if data.username is not None:
            user.username = data.username
        if data.email is not None:
            user.email = data.email
        if data.description is not None:
            user.description = data.description
        
        await session.commit()
        await session.refresh(user)
        
        return {
            "message": "User updated successfully",
            "user": user_to_response(user)
        }
    
    @delete("/{user_id:uuid}")
    async def delete_user(
        self,
        session: AsyncSession,
        user_id: UUID
    ) -> dict:
        result = await session.execute(select(User).where(User.id == user_id))
        user = result.scalar_one_or_none()
        
        if not user:
            raise NotFoundException(detail=f"User with ID {user_id} not found")
        
        await session.delete(user)
        await session.commit()
        
        return {"message": f"User with ID {user_id} deleted successfully"}
