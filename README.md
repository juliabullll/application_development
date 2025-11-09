# Database Project

Проект для работы с базой данных используя SQLAlchemy и Alembic.

## Установка
1. `uv add sqlalchemy alembic psycopg2-binary asyncpg`
2. Создайте `alembic.ini` с настройками базы данных
3. `alembic upgrade head`
4. `python -m app.data`