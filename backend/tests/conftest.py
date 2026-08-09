import os
import secrets
import uuid

# Test database URL
path = os.path.dirname(os.path.realpath(__file__))

TEST_DB_PATH = f"{path}/test.db"
TEST_DB_URL = f"sqlite+aiosqlite:///{TEST_DB_PATH}"

# Set environment variables for tests before importing the app
os.environ["APP__DB__FILE_PATH"] = TEST_DB_PATH
os.environ["APP__AUTH__SECRET_KEY"] = secrets.token_urlsafe(32)
os.environ["APP__BOT__TOKEN"] = "123456789:ABCdefGHIjklMNOpqrsTUVwxyz"
os.environ["APP__BOT__WEBHOOK_SECRET"] = secrets.token_hex(32)
os.environ["APP__MODE"] = "dev"


import asyncio
from collections.abc import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.db_helper import db_helper
from core.models.base import Base
from main import app

# Create test engine and session factory
test_engine = create_async_engine(TEST_DB_URL, echo=False)
test_session_factory = async_sessionmaker(
    bind=test_engine,
    autoflush=False,
    autocommit=False,
    expire_on_commit=False,
)


async def override_get_async_session() -> AsyncGenerator[AsyncSession]:
    async with test_session_factory() as session:
        yield session
        await session.close()


@pytest.fixture(scope="session", autouse=True)
def event_loop():
    loop = asyncio.new_event_loop()
    yield loop
    loop.close()


@pytest.fixture(scope="session", autouse=True)
async def setup_db():
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
    await test_engine.dispose()
    try:
        from core.scheduler import shutdown_scheduler

        shutdown_scheduler()
    except Exception:
        pass
    if os.path.exists(TEST_DB_PATH):
        try:
            os.remove(TEST_DB_PATH)
        except OSError:
            pass


@pytest.fixture
async def session() -> AsyncGenerator[AsyncSession]:
    async with test_session_factory() as session:
        yield session
        await session.rollback()
        await session.close()


@pytest.fixture
def user_password() -> str:
    return "testpassword123"


@pytest.fixture
async def test_user(client: AsyncClient, user_password: str) -> dict:
    unique_username = f"user_{uuid.uuid4().hex[:8]}"
    response = await client.post(
        "/api/users",
        json={
            "username": unique_username,
            "name": "Test User",
            "password": user_password,
        },
    )
    return response.json()


@pytest.fixture
async def user_token(client: AsyncClient, test_user: dict, user_password: str) -> str:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as login_client:
        response = await login_client.post(
            "/api/auth/login",
            data={
                "username": test_user["username"],
                "password": user_password,
            },
        )
        return response.json()["access_token"]


@pytest.fixture
async def auth_client(
    client: AsyncClient, user_token: str
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
        headers={"Authorization": f"Bearer {user_token}"},
    ) as ac:
        yield ac


@pytest.fixture
async def cookie_auth_client(
    client: AsyncClient,
    test_user: dict,
    user_password: str,
) -> AsyncGenerator[AsyncClient]:
    async with AsyncClient(
        transport=ASGITransport(app=app),
        base_url="http://test",
    ) as ac:
        await ac.post(
            "/api/auth/login",
            data={
                "username": test_user["username"],
                "password": user_password,
            },
        )
        yield ac


@pytest.fixture
async def test_car(auth_client: AsyncClient, test_user: dict) -> dict:
    response = await auth_client.post(
        "/api/cars",
        json={
            "brand": "Sample",
            "model": "Car",
            "year": 2020,
            "initial_odometer_km": 1000,
        },
    )
    return response.json()


@pytest.fixture
async def test_service_item(auth_client: AsyncClient, test_car: dict) -> dict:
    car_id = test_car["id"]
    response = await auth_client.post(
        "/api/service-items",
        json={
            "car_id": car_id,
            "name": "Oil Change",
            "last_service_at": "2026-01-01T00:00:00Z",
            "last_service_odometer_km": 1000,
        },
    )
    return response.json()


@pytest.fixture
async def client() -> AsyncGenerator[AsyncClient]:
    app.dependency_overrides[db_helper.session_dependency] = override_get_async_session
    async with AsyncClient(
        transport=ASGITransport(app=app), base_url="http://test"
    ) as ac:
        yield ac
    app.dependency_overrides.clear()
