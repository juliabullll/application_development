from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.models.message_models import OrderMessage, OrderStatus


class OrderProcessor:
    def __init__(self):
        self.orders = {}
        self.order_items = {}
    
    async def initialize(self):
        print("OrderProcessor initialized")
        return self
    
    async def create_order(self, order_data: OrderMessage) -> Dict[str, Any]:
        try:
            total_amount = sum(item.price * item.quantity for item in order_data.items)
            
            order_id = uuid4()
            
            order = {
                "id": order_id,
                "user_id": order_data.user_id,
                "status": order_data.status.value if order_data.status else "pending",
                "total_amount": total_amount,
                "shipping_address": order_data.shipping_address,
                "notes": order_data.notes,
                "created_at": datetime.utcnow(),
                "items": order_data.items
            }
            
            self.orders[order_id] = order
            
            self.order_items[order_id] = [
                {
                    "product_id": item.product_id,
                    "quantity": item.quantity,
                    "price": item.price
                }
                for item in order_data.items
            ]
            
            return {
                "success": True,
                "order_id": str(order_id),
                "status": order["status"],
                "total_amount": total_amount,
                "message": "Order created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create order"
            }
    
    async def update_order(self, order_data: OrderMessage) -> Dict[str, Any]:
        if not order_data.order_id:
            return {
                "success": False,
                "error": "Order ID is required for update"
            }
        
        try:
            if order_data.order_id not in self.orders:
                return {
                    "success": False,
                    "error": f"Order {order_data.order_id} not found"
                }
            
            order = self.orders[order_data.order_id]
            
            if order_data.shipping_address:
                order["shipping_address"] = order_data.shipping_address
            if order_data.notes:
                order["notes"] = order_data.notes
            if order_data.status:
                order["status"] = order_data.status.value
            
            order["updated_at"] = datetime.utcnow()
            
            return {
                "success": True,
                "order_id": str(order_data.order_id),
                "message": "Order updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "order_id": str(order_data.order_id) if order_data.order_id else None
            }
    
    async def update_order_status(
        self, 
        order_id: UUID, 
        new_status: OrderStatus,
        tracking_number: Optional[str] = None,
        notes: Optional[str] = None
    ) -> Dict[str, Any]:
        try:
            if order_id not in self.orders:
                return {
                    "success": False,
                    "error": f"Order {order_id} not found"
                }
            
            order = self.orders[order_id]
            order["status"] = new_status.value
            
            if tracking_number:
                order["tracking_number"] = tracking_number
            if notes:
                order["notes"] = notes
            
            order["updated_at"] = datetime.utcnow()
            
            return {
                "success": True,
                "order_id": str(order_id),
                "new_status": new_status.value,
                "message": "Order status updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "order_id": str(order_id)
            }
    
    async def get_order(self, order_id: UUID) -> Optional[Dict[str, Any]]:
        if order_id not in self.orders:
            return None
        
        order = self.orders[order_id]
        
        return {
            "order_id": str(order["id"]),
            "user_id": str(order["user_id"]),
            "status": order["status"],
            "total_amount": order["total_amount"],
            "shipping_address": order["shipping_address"],
            "tracking_number": order.get("tracking_number"),
            "notes": order.get("notes"),
            "created_at": order["created_at"].isoformat(),
            "updated_at": order.get("updated_at").isoformat() if order.get("updated_at") else None,
            "items": self.order_items.get(order_id, [])
        }