from sqlalchemy import select
from app.data import session_factory
from app.models import Product, Order, User, Address

def add_products_and_orders():
    
    with session_factory() as session:
        
        products = [
            Product(
                name="Ноутбук",
                description="Игровой ноутбук Asus",
                price=999.99
            ),
            Product(
                name="Смартфон",
                description="Samsung", 
                price=599.99
            ),
            Product(
                name="Наушники",
                description="Беспроводные наушники Apple",
                price=199.99
            ),
            Product(
                name="Планшет",
                description="Графический планшет XP-Pen",
                price=399.99
            ),
            Product(
                name="Часы",
                description="Умные часы Huawei",
                price=99.99
            )
        ]
        
        session.add_all(products)
        session.flush() 
        
        users = session.scalars(select(User)).all()
        addresses = session.scalars(select(Address)).all()
        
        orders = [
            Order(
                user_id=users[0].id,
                address_id=addresses[0].id,
                product_id=products[0].id,
                quantity=1,
                status="completed"
            ),
            Order(
                user_id=users[1].id,
                address_id=addresses[1].id,
                product_id=products[1].id,
                quantity=2,
                status="pending"
            ),
            Order(
                user_id=users[2].id,
                address_id=addresses[2].id,
                product_id=products[2].id,
                quantity=1,
                status="completed"
            ),
            Order(
                user_id=users[3].id,
                address_id=addresses[3].id,
                product_id=products[3].id,
                quantity=3,
                status="shipped"
            ),
            Order(
                user_id=users[4].id,
                address_id=addresses[4].id,
                product_id=products[4].id,
                quantity=1,
                status="completed"
            )
        ]
        
        session.add_all(orders)
        session.commit()

if __name__ == "__main__":
    add_products_and_orders()