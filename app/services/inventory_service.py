from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime


class InventoryService:
    def __init__(self):
        self.inventory = {}
        self.inventory_logs = []
        
        self.products = {
            UUID("223e4567-e89b-12d3-a456-426614174001"): {"name": "Ноутбук Dell XPS 13", "quantity": 35, "is_available": True},
            UUID("223e4567-e89b-12d3-a456-426614174002"): {"name": "Смартфон iPhone 15 Pro", "quantity": 40, "is_available": True},
            UUID("223e4567-e89b-12d3-a456-426614174003"): {"name": "Наушники Sony WH-1000XM5", "quantity": 50, "is_available": True},
        }
        
        self.inventory = self.products.copy()
    
    async def initialize(self):
        return self
    
    async def check_availability(self, product_id: UUID, requested_quantity: int) -> bool:
        if product_id not in self.inventory:
            return False
        product = self.inventory[product_id]
        return product["is_available"] and product["quantity"] >= requested_quantity
    
    async def update_quantity(self, product_id: UUID, quantity_change: int, reason: str) -> Dict[str, Any]:
        try:
            if product_id not in self.inventory:
                self.inventory[product_id] = {"name": f"Product {product_id}", "quantity": 0, "is_available": True}
            
            product = self.inventory[product_id]
            current_quantity = product["quantity"]
            new_quantity = current_quantity + quantity_change
            
            if new_quantity < 0:
                return {"success": False, "error": f"Insufficient stock. Current: {current_quantity}, Change: {quantity_change}"}
            
            product["quantity"] = new_quantity
            product["is_available"] = new_quantity > 0
            
            self.inventory_logs.append({
                "product_id": product_id,
                "old_quantity": current_quantity,
                "new_quantity": new_quantity,
                "quantity_change": quantity_change,
                "reason": reason,
                "timestamp": datetime.utcnow().isoformat()
            })
            
            return {
                "success": True,
                "product_id": str(product_id),
                "old_quantity": current_quantity,
                "new_quantity": new_quantity,
                "change": quantity_change,
                "reason": reason,
                "message": "Inventory updated"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e), "product_id": str(product_id)}
    
    async def reserve_product(self, product_id: UUID, quantity: int, order_id: UUID) -> Dict[str, Any]:
        return await self.update_quantity(product_id=product_id, quantity_change=-quantity, reason=f"reservation_for_order_{order_id}")