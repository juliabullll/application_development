from typing import List, Optional
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.repositories.order_repository import OrderRepository
from app.repositories.product_repository import ProductRepository
from app.repositories.user_repository import UserRepository
from app.models import Order, OrderCreate


class OrderService:
    """
    Сервисный слой для работы с заказами.
    Отвечает за бизнес-логику заказов.
    """
    
    def __init__(
        self, 
        order_repository: OrderRepository,
        product_repository: ProductRepository,
        user_repository: UserRepository
    ):
        self.order_repository = order_repository
        self.product_repository = product_repository
        self.user_repository = user_repository

    async def create_order(self, session: AsyncSession, order_data: dict) -> Order:
        """
        Создать новый заказ с проверкой бизнес-логики
        """
        # Проверяем что пользователь существует
        user = await self.user_repository.get_by_id(session, order_data["user_id"])
        if not user:
            raise ValueError("User not found")
        
        # Проверяем что продукт существует
        product = await self.product_repository.get_by_id(session, order_data["product_id"])
        if not product:
            raise ValueError("Product not found")
        
        # Проверяем есть ли у продукта поле quantity (количество на складе)
        if hasattr(product, 'quantity') and product.quantity is not None:
            if order_data["quantity"] > product.quantity:
                raise ValueError("Insufficient stock")
        
        # Рассчитываем общую сумму
        total_amount = product.price * order_data["quantity"]
        
        # Создаем заказ
        order_data_with_total = {**order_data, "total_amount": total_amount}
        return await self.order_repository.create(session, order_data_with_total)

    async def get_order_by_id(self, session: AsyncSession, order_id: UUID) -> Optional[Order]:
        """
        Получить заказ по ID
        """
        return await self.order_repository.get_by_id(session, order_id)

    async def get_orders_by_user(self, session: AsyncSession, user_id: UUID) -> List[Order]:
        """
        Получить заказы пользователя
        """
        return await self.order_repository.get_by_filter(session, count=100, page=1, user_id=user_id)