from pydantic import BaseModel, Field
from typing import List, Optional
from uuid import UUID
from datetime import datetime
from enum import Enum


class OrderStatus(str, Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    CANCELLED = "cancelled"


class OrderItem(BaseModel):
    product_id: UUID
    quantity: int
    price: float


class OrderMessage(BaseModel):
    """Модель сообщения для создания/обновления заказа"""
    order_id: Optional[UUID] = None
    user_id: UUID
    items: List[OrderItem]
    shipping_address: str
    status: Optional[OrderStatus] = OrderStatus.PENDING
    total_amount: Optional[float] = None
    notes: Optional[str] = None


class ProductMessage(BaseModel):
    """Модель сообщения для работы с продукцией"""
    product_id: Optional[UUID] = None
    name: str
    description: str
    price: float
    quantity: int
    category: Optional[str] = None
    sku: Optional[str] = None
    is_available: Optional[bool] = True


class InventoryUpdateMessage(BaseModel):
    """Модель для обновления инвентаря"""
    product_id: UUID
    quantity_change: int
    reason: str = Field(..., description="restock, sale, damage, adjustment, order_cancellation")


class OrderStatusUpdateMessage(BaseModel):
    """Модель для обновления статуса заказа"""
    order_id: UUID
    new_status: OrderStatus
    tracking_number: Optional[str] = None
    notes: Optional[str] = None