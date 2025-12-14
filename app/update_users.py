from sqlalchemy import select

from app.data import session_factory
from app.models import User


def add_descriptions():

    with session_factory() as session:
        users = session.scalars(select(User)).all()

        descriptions = [
            "Постоянный клиент с 2022 года",
            "Новый покупатель",
            "Бизнес клиент",
            "VIP клиент с привилегиями",
            "Оптовый покупатель",
        ]

        for i, user in enumerate(users):
            user.description = descriptions[i]

        session.commit()


if __name__ == "__main__":
    add_descriptions()
