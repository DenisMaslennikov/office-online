import asyncio
from typing import Generator, AsyncGenerator

import alembic
import pytest
import pytest_asyncio
from alembic import command
from faker import Faker
from sqlalchemy.ext.asyncio import create_async_engine, AsyncEngine, AsyncSession
from httpx import AsyncClient, ASGITransport

from app import main_app
from app.api.v1.auth.jwt import create_refresh_token, create_access_token
from app.db.models import User
from tests.constants import TEST_MIGRATIONS_HOST, TEST_APP_HOST
from tests.functions import wait_for_port

from app.db.db_helper import db_helper
from app.config import settings


@pytest_asyncio.fixture
async def client(session_override) -> AsyncGenerator[AsyncClient, None]:
    """Фикстура клиента для тестов АПИ."""
    async with AsyncClient(app=main_app, base_url="http://localhost:8000") as ac:
        yield ac


@pytest.fixture
def migration_database_url() -> str:
    """Урл для подключения к базе данных для теста миграций."""

    return (
        f"postgresql+asyncpg://"
        f"{settings.db.postgres_user}:"
        f"{settings.db.postgres_password}@"
        f"{TEST_MIGRATIONS_HOST}:"
        f"{settings.db.postgres_port}/"
        f"{settings.db.postgres_db}"
    )


@pytest.fixture(scope="session")
def app_database_url() -> str:
    """Урл для подключения к базе данных для теста приложения."""

    return (
        f"postgresql+asyncpg://"
        f"{settings.db.postgres_user}:"
        f"{settings.db.postgres_password}@"
        f"{TEST_APP_HOST}:"
        f"{settings.db.postgres_port}/"
        f"{settings.db.postgres_db}"
    )


@pytest_asyncio.fixture
async def alembic_engine(migrations_test_container, migration_database_url) -> AsyncEngine:
    """Используется pytest-alembic."""

    return create_async_engine(migration_database_url)


@pytest.fixture
def alembic_config(migration_database_url):
    """Используется pytest-alembic, для настройки конфигурации алембика."""

    alembic_config = alembic.config.Config()
    alembic_config.set_main_option("sqlalchemy.url", migration_database_url)
    return alembic_config


@pytest.fixture(scope="session")
def migrations_test_container():
    """Для тестирования миграций alembic."""

    wait_for_port(TEST_MIGRATIONS_HOST, settings.db.postgres_port)


@pytest.fixture(scope="session")
def database_test_container():
    """Для тестирования."""

    if not wait_for_port(TEST_APP_HOST, settings.db.postgres_port):
        pytest.exit(f"Exiting: Failed to connect to {TEST_APP_HOST} container.")


@pytest.fixture(scope="session", autouse=True)
def migrations(app_database_url, database_test_container):
    """Запуск миграций Alembic."""

    # Запуск миграций Alembic
    alembic_cfg = alembic.config.Config("alembic.ini")
    alembic_cfg.set_main_option("sqlalchemy.url", app_database_url)
    # Применяем миграции
    try:
        command.upgrade(alembic_cfg, "head")  # Выполнение миграций
    except Exception as e:
        print(f"Error during Alembic migration: {e}")
        raise e


@pytest_asyncio.fixture(scope="session")
async def engine(app_database_url, migrations) -> AsyncEngine:
    """Создает engine SQLAlchemy для взаимодействия с базой."""

    engine = create_async_engine(app_database_url)
    yield engine
    await engine.dispose()


@pytest_asyncio.fixture
async def db_session(engine) -> AsyncGenerator[AsyncSession, None]:
    """Создает и возвращает сессию базы данных для тестирования."""

    async with engine.connect() as connection:
        transaction = await connection.begin()
        session = AsyncSession(bind=connection, join_transaction_mode="create_savepoint", expire_on_commit=False)
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()
            await transaction.rollback()
            await connection.close()


@pytest.fixture
def session_override(db_session):
    """Подменяет зависимость сессии на тестовую."""

    async def get_session_override() -> AsyncGenerator[AsyncSession, None]:
        """Функция для подмены зависимости сессии."""

        yield db_session

    # monkeypatch.setattr("app.api.v1.users.views.db_helper.get_session", get_session_override)
    main_app.dependency_overrides[db_helper.get_session] = get_session_override


@pytest.fixture
def faker() -> Faker:
    """Фикстура фейкера для генерации тестовых данных."""

    return Faker("ru_RU")


@pytest.fixture
def user_one_password(faker) -> str:
    """Пароль первого пользователя."""

    return faker.password()


@pytest.fixture
def user_two_password(faker) -> str:
    """Пароль для пользователя 2."""

    return faker.password()


@pytest_asyncio.fixture
async def user_one(db_session, faker, user_one_password) -> User:
    """Фикстура пользователя для тестов."""

    user = User(
        email=faker.unique.email(),
        first_name=faker.first_name(),
        second_name=faker.last_name(),
        middle_name=faker.middle_name(),
        username=faker.unique.user_name(),
    )
    user.password = user_one_password
    db_session.add(user)
    await db_session.commit()
    return user


@pytest_asyncio.fixture
async def user_two(db_session, faker, user_two_password) -> User:
    """Фистура другого пользователя для тестов."""

    user = User(
        email=faker.unique.email(),
        first_name=faker.first_name(),
        second_name=faker.last_name(),
        middle_name=faker.middle_name(),
        username=faker.unique.user_name(),
    )
    user.password = user_two_password
    db_session.add(user)
    await db_session.commit()
    return user


@pytest.fixture
def refresh_token_user_one(user_one) -> str:
    """Получение refresh токена для первого пользователя."""
    return create_refresh_token(user_one.id)


@pytest.fixture
def access_token_user_one(user_one) -> str:
    """Получение access токена для первого пользователя."""
    return create_access_token(user_one.id)


# @pytest.fixture(scope="session")  # (loop_scope="function", scope="function")
# def event_loop():
#     loop = asyncio.get_event_loop_policy().new_event_loop()
#     yield loop
#     loop.close()


# @pytest.fixture
# def anyio_backend():
#     return "asyncio"
#
#
# @pytest.fixture(scope="session")
# def event_loop():
#     # loop = asyncio.get_event_loop_policy().new_event_loop()
#     # yield loop
#     # loop.close()
#     return asyncio.get_event_loop()
