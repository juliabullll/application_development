
Лабораторные работы по разработке приложений.

## Лабораторные работы

- **Лабораторная работа №2** - тег `lab_2`
- **Лабораторная работа №3** - тег `lab_3` - CRUD API с трехуровневой архитектурой
- **Лабораторная работа №4** - тег `lab_4` - Комплексное тестирование приложения
- **Лабораторная работа №5** - тег `lab_5` - Инструменты качества кода и Docker-контейнеризация
- **Лабораторная работа №6** - тег `lab_6` - RabbitMQ обработка заказов и продукции
- **Лабораторная работа №7** - тег `lab_7` - Redis кэширование данных пользователей и продукции

## Быстрый запуск приложения 

### Предварительные требования
- Python 3.8+
- Git

### Клонирование и настройка
```bash
# Клонировать репозиторий
git clone https://github.com/juliabullll/application_development.git
cd application_development

# Перейти на тег лабораторной работы 
git checkout lab_3
git checkout lab_4
git checkout lab_5
# Установить зависимости
pip install -r requirements.txt
pip install litestar sqlalchemy pydantic uvicorn aiosqlite alembic

#Запуск всех тестов
pytest tests/ -v
#Запуск отдельных тестов
pytest tests/test_repositories/ -v -s          # Интеграционные тесты
pytest tests/test_services/ -v -s              # Mock тесты
pytest tests/test_api.py -v -s --asyncio-mode=auto  # API тесты

# Запуск приложения в Docker
docker-compose up --build
# Приложение доступно по: http://localhost:8000

#unit-тесты
tests/test_rabbitmq.py
tests/test_services.py
