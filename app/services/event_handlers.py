import asyncio
from typing import Dict, Any
from datetime import datetime


class EventHandlers:
    @staticmethod
    async def handle_user_created(event: Dict[str, Any]):
        print(f"User created event: {event}")
        
        user_id = event.get("user_id")
        username = event.get("username")
        email = event.get("email")
        
        print(f"Processing new user: {username} ({email})")
        await asyncio.sleep(1)
        print(f"User {username} processing completed at {datetime.now()}")
    
    @staticmethod
    async def handle_order_created(event: Dict[str, Any]):
        print(f"Order created event: {event}")
        
        order_id = event.get("order_id")
        user_id = event.get("user_id")
        total_amount = event.get("total_amount")
        
        print(f"Processing order {order_id} for user {user_id}")
        await asyncio.sleep(2)
        print(f"Order {order_id} processing completed")
    
    @staticmethod
    async def handle_product_updated(event: Dict[str, Any]):
        print(f"Product updated event: {event}")
        
        product_id = event.get("product_id")
        product_name = event.get("name")
        new_price = event.get("price")
        
        print(f"Product {product_name} updated, new price: {new_price}")
        await asyncio.sleep(0.5)
        print(f"Product {product_id} update processed")