
from typing import Optional, List
from litestar import Controller, get, post, put, delete
from litestar.params import Parameter
from litestar.exceptions import NotFoundException
from uuid import UUID

try:
    from app.services.order_processor import OrderProcessor
except ImportError:
    OrderProcessor = None


class OrderController(Controller):
    path = "/api/v1/orders"
    
    @get("/")
    async def get_orders(
        self,
        limit: int = Parameter(query="limit", default=10, ge=1, le=100),
        offset: int = Parameter(query="offset", default=0, ge=0)
    ) -> dict:
        """Получить список заказов"""
        # Создаем экземпляр OrderProcessor
        order_processor = OrderProcessor()
        await order_processor.initialize()
        
        # Получаем все заказы из памяти (временное решение)
        orders = []
        if hasattr(order_processor, 'orders'):
            for order_id, order in order_processor.orders.items():
                orders.append({
                    "order_id": str(order_id),
                    "user_id": str(order.get("user_id")),
                    "status": order.get("status"),
                    "total_amount": order.get("total_amount"),
                    "created_at": order.get("created_at").isoformat() if order.get("created_at") else None
                })
        
        # Пагинация
        start = offset
        end = offset + limit
        paginated_orders = orders[start:end]
        
        return {
            "success": True,
            "orders": paginated_orders,
            "total": len(orders),
            "limit": limit,
            "offset": offset
        }
    
    @get("/{order_id:str}")
    async def get_order(
        self,
        order_id: str,
    ) -> dict:
        """Получить заказ по ID"""
        try:
            order_uuid = UUID(order_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid order ID format: {order_id}")
        
        # Создаем экземпляр OrderProcessor
        order_processor = OrderProcessor()
        await order_processor.initialize()
        
        order = await order_processor.get_order(order_uuid)
        if not order:
            raise NotFoundException(detail=f"Order {order_id} not found")
        
        return {"success": True, "data": order}
    
    @post("/")
    async def create_order(self, data: dict) -> dict:
        """Создать новый заказ через RabbitMQ"""
        from app.services.order_processor import OrderProcessor
        from app.models.message_models import OrderMessage, OrderItem
        from uuid import UUID
        
        try:
            # Конвертируем данные
            items = []
            for item in data.get("items", []):
                items.append(
                    OrderItem(
                        product_id=UUID(item["product_id"]),
                        quantity=item["quantity"],
                        price=item["price"]
                    )
                )
            
            order_data = OrderMessage(
                user_id=UUID(data["user_id"]),
                items=items,
                shipping_address=data["shipping_address"],
                notes=data.get("notes")
            )
            
            order_processor = OrderProcessor()
            await order_processor.initialize()
            result = await order_processor.create_order(order_data)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create order"
            }
    
    @put("/{order_id:str}/status")
    async def update_order_status(
        self,
        order_id: str,
        status: str,
        tracking_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> dict:
        """Обновить статус заказа"""
        try:
            order_uuid = UUID(order_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid order ID format: {order_id}")
        
        from app.services.order_processor import OrderProcessor
        from app.models.message_models import OrderStatus
        
        try:
            order_processor = OrderProcessor()
            await order_processor.initialize()
            
            result = await order_processor.update_order_status(
                order_id=order_uuid,
                new_status=OrderStatus(status),
                tracking_number=tracking_number,
                notes=notes
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update order status"
            }