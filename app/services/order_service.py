from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.models import Order, OrderCreate
from app.services.rabbitmq_service import RabbitMQService


class OrderService:
    def __init__(
        self,
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository
        self.rabbitmq = RabbitMQService()
    
    async def create_order(self, session: AsyncSession, order_data: dict) -> Order:
        user = await self.user_repository.get_by_id(session, order_data["user_id"])
        if not user:
            raise ValueError("User not found")
        
        product = await self.product_repository.get_by_id(session, order_data["product_id"])
        if not product:
            raise ValueError("Product not found")
        
        if hasattr(product, 'quantity') and product.quantity is not None:
            if order_data["quantity"] > product.quantity:
                raise ValueError("Insufficient stock")
        
        total_amount = product.price * order_data["quantity"]
        order_data_with_total = {**order_data, "total_amount": total_amount}
        
        order = await self.order_repository.create(session, order_data_with_total)
        
        order_event = {
            "order_id": str(order.id),
            "user_id": str(order.user_id),
            "product_id": str(order.product_id),
            "quantity": order.quantity,
            "total_amount": float(order.total_amount) if hasattr(order, 'total_amount') else float(total_amount),
            "status": order.status
        }
        
        try:
            await self.rabbitmq.publish_order_created(order_event)
        except Exception as e:
            print(f"Failed to send RabbitMQ event: {e}")
        
        return order
    
    async def get_order_by_id(self, session: AsyncSession, order_id: UUID) -> Optional[Order]:
        return await self.order_repository.get_by_id(session, order_id)
    
    async def get_orders_by_user(self, session: AsyncSession, user_id: UUID) -> List[Order]:
        return await self.order_repository.get_by_filter(session, count=100, page=1, user_id=user_id)
    async def get_orders_by_user(
        self, session: AsyncSession, user_id: UUID
    ) -> List[Order]:
        """
        Получить заказы пользователя
        """
        return await self.order_repository.get_by_filter(
            session, count=100, page=1, user_id=user_id
        )
