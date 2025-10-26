from sqlalchemy import select, func, case
from sqlalchemy.orm import sessionmaker
from app.models import User, Address, Product, Order
from app.data import engine

session_factory = sessionmaker(engine)

def run_sql_queries():
    
    with session_factory() as session:
    
        # ЗАПРОС 1: Самые дорогие продукты
        stmt1 = select(
            Product.name,
            Product.price,
            Product.description
        ).order_by(
            Product.price.desc()
        ).limit(3)
        
        expensive_products = session.execute(stmt1).all()
        for name, price, description in expensive_products:
            print(f"{name}")
            print(f"{price:,}")
            print(f"{description}")
        
        # ЗАПРОС 2: пользователи без адресов
        stmt2 = select(User).outerjoin(Address).where(Address.id == None)
        users_without_addresses = session.scalars(stmt2).all()
        
        if users_without_addresses:
            for user in users_without_addresses:
                print(f"{user.username} ({user.email})")
                print(f" {user.description}")
        else:
            print("У всех пользователей есть адреса")
        
        # ЗАПРОС 3: Заказы по городам доставки
        stmt3 = select(
            Address.city,
            func.count(Order.id).label('order_count'),
        ).join(
            Order, Address.id == Order.address_id
        ).group_by(
            Address.city
        ).order_by(
            func.count(Order.id).desc()
        )
        
        city_orders = session.execute(stmt3).all()
        for city, order_count in city_orders:
            print(f"{city}")
            print(f"Заказов: {order_count}")
     
if __name__ == "__main__":
    run_sql_queries()