from faststream import FastStream, Logger
from faststream.rabbit import RabbitBroker
import asyncio
import os
import json
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

from app.models.message_models import (
    OrderMessage, 
    ProductMessage, 
    InventoryUpdateMessage,
    OrderStatusUpdateMessage,
    OrderStatus
)
from app.services.order_processor import OrderProcessor
from app.services.product_processor import ProductProcessor
from app.services.inventory_service import InventoryService

RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "localhost")
RABBITMQ_PORT = os.getenv("RABBITMQ_PORT", "5673")
RABBITMQ_USER = os.getenv("RABBITMQ_USER", "guest")
RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "guest")

rabbitmq_url = f"amqp://{RABBITMQ_USER}:{RABBITMQ_PASS}@{RABBITMQ_HOST}:{RABBITMQ_PORT}/"
broker = RabbitBroker(rabbitmq_url)
app = FastStream(broker)

_order_processor = None
_product_processor = None
_inventory_service = None


async def get_order_processor():
    global _order_processor
    if _order_processor is None:
        _order_processor = OrderProcessor()
        await _order_processor.initialize()
    return _order_processor


async def get_product_processor():
    global _product_processor
    if _product_processor is None:
        _product_processor = ProductProcessor()
        await _product_processor.initialize()
    return _product_processor


async def get_inventory_service():
    global _inventory_service
    if _inventory_service is None:
        _inventory_service = InventoryService()
        await _inventory_service.initialize()
    return _inventory_service


@broker.subscriber("order_queue")
async def handle_order_queue(
    message: dict,
    logger: Logger
):
    logger.info(f"Received order message: {json.dumps(message, default=str)}")
    
    try:
        order_data = OrderMessage(**message)
        order_processor = await get_order_processor()
        inventory_service = await get_inventory_service()
        
        unavailable_items = []
        for item in order_data.items:
            is_available = await inventory_service.check_availability(
                product_id=item.product_id,
                requested_quantity=item.quantity
            )
            if not is_available:
                unavailable_items.append(str(item.product_id))
        
        if unavailable_items:
            error_msg = f"Products out of stock: {', '.join(unavailable_items)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "order_id": str(order_data.order_id) if order_data.order_id else None
            }
        
        if order_data.order_id:
            result = await order_processor.update_order(order_data)
        else:
            result = await order_processor.create_order(order_data)
            
            if result["success"]:
                for item in order_data.items:
                    await inventory_service.reserve_product(
                        product_id=item.product_id,
                        quantity=item.quantity,
                        order_id=result["order_id"]
                    )
        
        logger.info(f"Order processed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Order processing error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "order_id": str(message.get('order_id')) if message.get('order_id') else None
        }


@broker.subscriber("product_queue")
async def handle_product_queue(
    message: dict,
    logger: Logger
):
    logger.info(f"Received product message: {json.dumps(message, default=str)}")
    
    try:
        product_data = ProductMessage(**message)
        product_processor = await get_product_processor()
        
        if product_data.product_id:
            result = await product_processor.update_product(product_data)
        else:
            result = await product_processor.create_product(product_data)
        
        logger.info(f"Product processed: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Product processing error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "product_id": str(message.get('product_id')) if message.get('product_id') else None
        }


@broker.subscriber("inventory_queue")
async def handle_inventory_queue(
    message: dict,
    logger: Logger
):
    logger.info(f"Received inventory message: {json.dumps(message, default=str)}")
    
    try:
        inventory_data = InventoryUpdateMessage(**message)
        inventory_service = await get_inventory_service()
        
        result = await inventory_service.update_quantity(
            product_id=inventory_data.product_id,
            quantity_change=inventory_data.quantity_change,
            reason=inventory_data.reason
        )
        
        logger.info(f"Inventory updated: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Inventory processing error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "product_id": str(message.get('product_id')) if message.get('product_id') else None
        }


@broker.subscriber("order_status_queue")
async def handle_order_status_queue(
    message: dict,
    logger: Logger
):
    logger.info(f"Received order status message: {json.dumps(message, default=str)}")
    
    try:
        status_data = OrderStatusUpdateMessage(**message)
        order_processor = await get_order_processor()
        inventory_service = await get_inventory_service()
        
        result = await order_processor.update_order_status(
            order_id=status_data.order_id,
            new_status=status_data.new_status,
            tracking_number=status_data.tracking_number,
            notes=status_data.notes
        )
        
        if status_data.new_status == OrderStatus.CANCELLED and result["success"]:
            order_details = await order_processor.get_order(status_data.order_id)
            if order_details and order_details.get("items"):
                for item in order_details["items"]:
                    await inventory_service.update_quantity(
                        product_id=item["product_id"],
                        quantity_change=item["quantity"],
                        reason="order_cancellation"
                    )
        
        logger.info(f"Order status updated: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Order status processing error: {str(e)}")
        return {
            "success": False,
            "error": str(e),
            "order_id": str(message.get('order_id')) if message.get('order_id') else None
        }


@app.after_startup
async def test_publish():
    from uuid import uuid4
    
    test_product = {
        "name": "Test Product",
        "description": "Test Description",
        "price": 99.99,
        "quantity": 100,
        "category": "electronics",
        "sku": "TEST-001"
    }
    
    test_order = {
        "user_id": str(uuid4()),
        "items": [
            {
                "product_id": str(uuid4()),
                "quantity": 2,
                "price": 99.99
            }
        ],
        "shipping_address": "Test Address 123"
    }
    
    await broker.publish(test_product, queue="product_queue")
    print("Test product published to product_queue")
    
    await broker.publish(test_order, queue="order_queue")
    print("Test order published to order_queue")


if __name__ == "__main__":
    asyncio.run(app.run())