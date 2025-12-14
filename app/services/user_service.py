from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.user_repository import UserRepository
from app.models import User, UserCreate, UserUpdate
from app.services.rabbitmq_service import RabbitMQService
from datetime import datetime


class UserService:
    def __init__(self, user_repository: UserRepository):
        self.user_repository = user_repository
        self.rabbitmq = RabbitMQService()
    
    async def get_by_id(self, session: AsyncSession, user_id: UUID) -> Optional[User]:
        return await self.user_repository.get_by_id(session, user_id)
    
    async def get_by_filter(self, session: AsyncSession, count: int, page: int, **kwargs) -> List[User]:
        count = min(count, 100)
        if page <= 0:
            page = 1
        return await self.user_repository.get_by_filter(session, count, page, **kwargs)
    
    async def create(self, session: AsyncSession, user_data: UserCreate) -> User:
        if not user_data.username or not user_data.email:
            raise ValueError("Username and email are required")
        if '@' not in user_data.email:
            raise ValueError("Invalid email format")
        
        user = await self.user_repository.create(session, user_data)
        
        event_data = {
            "event_type": "user.created",
            "user_id": str(user.id),
            "username": user.username,
            "email": user.email,
            "timestamp": user.created_at.isoformat()
        }
        
        try:
            await self.rabbitmq.publish_event("user.created", event_data)
            print(f"User created event sent to RabbitMQ: {user.username}")
        except Exception as e:
            print(f"Failed to send RabbitMQ event: {e}")
        
        return user
    
    async def update(self, session: AsyncSession, user_id: UUID, user_data: UserUpdate) -> Optional[User]:
        existing_user = await self.get_by_id(session, user_id)
        if not existing_user:
            return None
        if user_data.email and '@' not in user_data.email:
            raise ValueError("Invalid email format")
                
        updated_user = await self.user_repository.update(session, user_id, user_data)
        
        if updated_user:
            event_data = {
                "event_type": "user.updated",
                "user_id": str(updated_user.id),
                "updated_fields": user_data.model_dump(exclude_unset=True),
                "timestamp": updated_user.updated_at.isoformat() if hasattr(updated_user, 'updated_at') else None
            }
            try:
                await self.rabbitmq.publish_event("user.updated", event_data)
            except Exception as e:
                print(f"Failed to send RabbitMQ event: {e}")
        
        return updated_user
    
    async def delete(self, session: AsyncSession, user_id: UUID) -> bool:
        existing_user = await self.get_by_id(session, user_id)
        if not existing_user:
            return False
            
        result = await self.user_repository.delete(session, user_id)
        
        if result:
            event_data = {
                "event_type": "user.deleted",
                "user_id": str(user_id),
                "timestamp": datetime.now().isoformat()
            }
            try:
                await self.rabbitmq.publish_event("user.deleted", event_data)
            except Exception as e:
                print(f"Failed to send RabbitMQ event: {e}")
        
        return result
    
    async def get_total_count(self, session: AsyncSession, **kwargs) -> int:
        return await self.user_repository.get_total_count(session, **kwargs)