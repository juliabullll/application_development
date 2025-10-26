from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from app.models import User, Address

connect_url = "sqlite:///test.db"

engine = create_engine(
    connect_url, 
    echo=True  
)

session_factory = sessionmaker(engine)

def add_users_and_addresses():
    
    with session_factory() as session:
        
        user1 = User(username="john_doe", email="john@example.com")
        address1 = Address(
            user=user1.id,
            street="3-5-1 Marunouchi",
            city="Tokyo", 
            province="Tokyo",
            zip_code="100-0005",
            country="Japan",
            is_primary=True
        )
        user1.addresses.append(address1)

        user2 = User(username="alice_smith", email="alice123@example.com")
        address2 = Address(
            street="45 Oxford Street",
            city="London",
            province="England",
            zip_code="W1D 2EB",
            country="United Kingdom", 
            is_primary=True
        )
        user2.addresses.append(address2)
        
        user3 = User(username="bob_johnson", email="bobjoh@example.com")
        address3 = Address(
            street="Friedrichstraße 15",
            city="Berlin",
            province="Berlin",
            zip_code="10117",
            country="Germany",
            is_primary=True
        )
        user3.addresses.append(address3)
        
        user4 = User(username="emma_wilson", email="emmochka@example.com")
        address4 = Address(
            street="72 Rue de Rivoli", 
            city="Paris",
            province="Île-de-France",
            zip_code="75004",
            country="France",
            is_primary=True
        )
        user4.addresses.append(address4)
       
        user5 = User(username="mike_brown", email="mike456@example.com")
        address5 = Address(
            street="123 Main Street",
            city="New York",
            province="NY", 
            zip_code="10001",
            country="USA",
            is_primary=True
        )
        user5.addresses.append(address5)
        
        session.add_all([user1, address1, user2, address2, user3, address3, 
                        user4, address4, user5, address5])
        session.commit()
    

if __name__ == "__main__":
    add_users_and_addresses()