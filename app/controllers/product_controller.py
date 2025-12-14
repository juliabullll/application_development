# app/controllers/product_controller.py
from typing import Optional, List
from litestar import Controller, get, post, put, delete
from litestar.params import Parameter
from litestar.exceptions import NotFoundException
from uuid import UUID

from app.services.product_processor import ProductProcessor


class ProductController(Controller):
    path = "/api/v1/products"
    
    @get("/{product_id:str}")
    async def get_product(
        self,
        product_id: str
    ) -> dict:
        """Получить продукт по ID"""
        try:
            product_uuid = UUID(product_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid product ID format: {product_id}")
        
        product_processor = ProductProcessor()
        await product_processor.initialize()
        
        product = await product_processor.get_product(product_uuid)
        if not product:
            raise NotFoundException(detail=f"Product {product_id} not found")
        
        return {"success": True, "data": product}
    
    @get("/")
    async def get_products(
        self,
        category: Optional[str] = Parameter(query="category", default=None),
        available_only: bool = Parameter(query="available_only", default=False),
        limit: int = Parameter(query="limit", default=50, ge=1, le=100),
        offset: int = Parameter(query="offset", default=0, ge=0)
    ) -> dict:
        """Получить список продуктов"""
        product_processor = ProductProcessor()
        await product_processor.initialize()
        
        products = await product_processor.get_products(
            category=category,
            available_only=available_only,
            limit=limit,
            offset=offset
        )
        
        return {
            "success": True,
            "data": products,
            "total": len(products),
            "filters": {
                "category": category,
                "available_only": available_only
            }
        }
    
    @post("/")
    async def create_product(self, data: dict) -> dict:
        """Создать новый продукт"""
        from app.services.product_processor import ProductProcessor
        from app.models.message_models import ProductMessage
        
        try:
            product_data = ProductMessage(
                name=data["name"],
                description=data["description"],
                price=data["price"],
                quantity=data["quantity"],
                category=data.get("category"),
                sku=data.get("sku")
            )
            
            product_processor = ProductProcessor()
            await product_processor.initialize()
            result = await product_processor.create_product(product_data)
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to create product"
            }
    
    @put("/{product_id:str}/stock")
    async def update_stock(
        self,
        product_id: str,
        quantity_change: int,
        reason: str = "adjustment"
    ) -> dict:
        """Обновить количество на складе"""
        try:
            product_uuid = UUID(product_id)
        except ValueError:
            raise NotFoundException(detail=f"Invalid product ID format: {product_id}")
        
        from app.services.inventory_service import InventoryService
        
        try:
            inventory_service = InventoryService()
            await inventory_service.initialize()
            
            result = await inventory_service.update_quantity(
                product_id=product_uuid,
                quantity_change=quantity_change,
                reason=reason
            )
            
            return result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "message": "Failed to update stock"
            }