from typing import Dict, Any, Optional, List
from uuid import UUID, uuid4
from datetime import datetime

from app.models.message_models import ProductMessage


class ProductProcessor:
    def __init__(self):
        self.products = {}
    
    async def initialize(self):
        print("ProductProcessor initialized")
        
        test_products = [
            {
                "id": uuid4(),
                "name": "Ноутбук Dell XPS 13",
                "description": "13-дюймовый ноутбук с процессором Intel i7",
                "price": 1299.99,
                "quantity": 15,
                "category": "electronics",
                "sku": "DLXPS13-001",
                "is_available": True
            },
            {
                "id": uuid4(),
                "name": "Смартфон iPhone 15 Pro",
                "description": "Флагманский смартфон Apple",
                "price": 999.99,
                "quantity": 25,
                "category": "electronics",
                "sku": "IP15P-001",
                "is_available": True
            },
            {
                "id": uuid4(),
                "name": "Наушники Sony WH-1000XM5",
                "description": "Беспроводные наушники с шумоподавлением",
                "price": 349.99,
                "quantity": 30,
                "category": "electronics",
                "sku": "SONYXM5-001",
                "is_available": True
            }
        ]
        
        for product in test_products:
            self.products[product["id"]] = product
        
        return self
    
    async def create_product(self, product_data: ProductMessage) -> Dict[str, Any]:
        try:
            product_id = uuid4()
            
            product = {
                "id": product_id,
                "name": product_data.name,
                "description": product_data.description,
                "price": product_data.price,
                "quantity": product_data.quantity,
                "category": product_data.category,
                "sku": product_data.sku,
                "is_available": product_data.quantity > 0,
                "created_at": datetime.utcnow()
            }
            
            self.products[product_id] = product
            
            return {
                "success": True,
                "product_id": str(product_id),
                "name": product["name"],
                "price": product["price"],
                "quantity": product["quantity"],
                "is_available": product["is_available"],
                "message": "Product created successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create product"
            }
    
    async def update_product(self, product_data: ProductMessage) -> Dict[str, Any]:
        if not product_data.product_id:
            return {
                "success": False,
                "error": "Product ID is required for update"
            }
        
        try:
            if product_data.product_id not in self.products:
                return {
                    "success": False,
                    "error": f"Product {product_data.product_id} not found"
                }
            
            product = self.products[product_data.product_id]
            
            product["name"] = product_data.name
            product["description"] = product_data.description
            product["price"] = product_data.price
            product["quantity"] = product_data.quantity
            product["category"] = product_data.category
            product["sku"] = product_data.sku
            product["is_available"] = product_data.quantity > 0
            product["updated_at"] = datetime.utcnow()
            
            return {
                "success": True,
                "product_id": str(product_data.product_id),
                "name": product["name"],
                "quantity": product["quantity"],
                "is_available": product["is_available"],
                "message": "Product updated successfully"
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "product_id": str(product_data.product_id) if product_data.product_id else None
            }
    
    async def get_product(self, product_id: UUID) -> Optional[Dict[str, Any]]:
        if product_id not in self.products:
            return None
        
        product = self.products[product_id]
        
        return {
            "product_id": str(product["id"]),
            "name": product["name"],
            "description": product["description"],
            "price": product["price"],
            "quantity": product["quantity"],
            "category": product["category"],
            "sku": product["sku"],
            "is_available": product["is_available"],
            "created_at": product["created_at"].isoformat(),
            "updated_at": product.get("updated_at").isoformat() if product.get("updated_at") else None
        }
    
    async def get_products(
        self, 
        category: Optional[str] = None,
        available_only: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict[str, Any]]:
        result = []
        
        for product_id, product in self.products.items():
            if category and product["category"] != category:
                continue
            
            if available_only and not product["is_available"]:
                continue
            
            result.append({
                "product_id": str(product_id),
                "name": product["name"],
                "description": product["description"],
                "price": product["price"],
                "quantity": product["quantity"],
                "category": product["category"],
                "is_available": product["is_available"]
            })
        
        start = offset
        end = offset + limit
        return result[start:end]