# app/models/__init__.py
from .database_models import (
    Base, 
    User, 
    Address, 
    Order, 
    Product,
    UserCreate,
    UserUpdate,
    UserResponse,
    UsersListResponse,
    ProductCreate,
    ProductUpdate,
    ProductResponse,
    OrderCreate,
    OrderUpdate,
    OrderResponse,
    user_to_response
)

from .message_models import (
    OrderMessage, 
    ProductMessage, 
    InventoryUpdateMessage,
    OrderStatusUpdateMessage,
    OrderStatus
)

from pydantic import BaseModel
from uuid import UUID

class OrderItem(BaseModel):
    """Модель для позиции заказа в сообщениях RabbitMQ"""
    product_id: UUID
    quantity: int
    price: float

__all__ = [
    'Base', 
    'User', 
    'Address', 
    'Order', 
    'Product',
    'UserCreate',
    'UserUpdate',
    'UserResponse', 
    'UsersListResponse',
    'ProductCreate',
    'ProductUpdate',
    'ProductResponse',
    'OrderCreate',
    'OrderUpdate',
    'OrderResponse',
    'user_to_response',
    'OrderItem',  
    'OrderMessage',
    'ProductMessage', 
    'InventoryUpdateMessage',
    'OrderStatusUpdateMessage',
    'OrderStatus'
]