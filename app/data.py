import os

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.models import Address, User

# Используем переменную окружения или значение по умолчанию
CONNECT_URL = (
    os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./test.db")
    .replace("+aiosqlite", "")
    .replace("+asyncpg", "")
)


def add_users_and_addresses():
    engine = create_engine(CONNECT_URL, echo=True)
    session_factory = sessionmaker(engine)

    with session_factory() as session:
        # Создаем пользователей
        user1 = User(username="john_doe", email="john@example.com")
        user2 = User(username="alice_smith", email="alice123@example.com")
        user3 = User(username="bob_johnson", email="bobjoh@example.com")
        user4 = User(username="emma_wilson", email="emmochka@example.com")
        user5 = User(username="mike_brown", email="mike456@example.com")

        # Сначала сохраняем пользователей чтобы получить их ID
        session.add_all([user1, user2, user3, user4, user5])
        session.flush()  # Получаем ID пользователей

        # Теперь создаем адреса с правильными user_id
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

        # Добавляем адреса
        session.add_all([address1, address2, address3, address4, address5])
        session.commit()
        print("Test users and addresses added successfully!")


if __name__ == "__main__":
    add_users_and_addresses()
