from sqlalchemy import select
from sqlalchemy.orm import selectinload, sessionmaker
from app.models import User, Address
from app.data import engine  
session_factory = sessionmaker(engine)

def query_users_with_addresses():
    
    with session_factory() as session:
        
        stmt = select(User).options(selectinload(User.addresses))
        users = session.scalars(stmt).all()
        
        for user in users:
            print(f"Пользователи: {user.username} ({user.email})")
            for address in user.addresses:
                print(f"Адреса: {address.street}, {address.city}")

if __name__ == "__main__":
    query_users_with_addresses()