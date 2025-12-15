import os
import sys
from pathlib import Path

project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import datetime

from app.models.database_models import Address, User

CONNECT_URL = (
    os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    .replace("+aiosqlite", "")
    .replace("+asyncpg", "")
)

engine = create_engine(CONNECT_URL, echo=True)
session_factory = sessionmaker(engine)

def add_users_and_addresses():
    with session_factory() as session:
        # Используем уникальные email с timestamp
        timestamp = datetime.now().strftime("%H%M%S")
        
        user1 = User(username=f"john_doe_{timestamp}", email=f"john_{timestamp}@example.com")
        user2 = User(username=f"alice_smith_{timestamp}", email=f"alice_{timestamp}@example.com")
        user3 = User(username=f"bob_johnson_{timestamp}", email=f"bob_{timestamp}@example.com")
        user4 = User(username=f"emma_wilson_{timestamp}", email=f"emma_{timestamp}@example.com")
        user5 = User(username=f"mike_brown_{timestamp}", email=f"mike_{timestamp}@example.com")

        session.add_all([user1, user2, user3, user4, user5])
        session.flush()

        address1 = Address(
            user_id=user1.id,
            street="3-5-1 Marunouchi",
            city="Tokyo",
            province="Tokyo",
            zip_code="100-0005",
            country="Japan",
            is_primary=True,
        )

        address2 = Address(
            user_id=user2.id,
            street="45 Oxford Street",
            city="London",
            province="England",
            zip_code="W1D 2EB",
            country="United Kingdom",
            is_primary=True,
        )

        address3 = Address(
            user_id=user3.id,
            street="Friedrichstraße 15",
            city="Berlin",
            province="Berlin",
            zip_code="10117",
            country="Germany",
            is_primary=True,
        )

        address4 = Address(
            user_id=user4.id,
            street="72 Rue de Rivoli",
            city="Paris",
            province="Île-de-France",
            zip_code="75004",
            country="France",
            is_primary=True,
        )

        address5 = Address(
            user_id=user5.id,
            street="123 Main Street",
            city="New York",
            province="NY",
            zip_code="10001",
            country="USA",
            is_primary=True,
        )

        session.add_all([address1, address2, address3, address4, address5])
        session.commit()
        print("Test users and addresses added successfully!")

if __name__ == "__main__":
    add_users_and_addresses()