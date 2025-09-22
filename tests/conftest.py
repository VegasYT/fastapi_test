import json
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.database import async_session_maker_null_pool
from src.config import settings
from src.database import Base, engine_null_pool
from src.main import app
from src.models import *
from src.utils.db_manager import DBManager
from src.api.dependencies import get_db


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


async def get_db_null_pool():
    async with DBManager(session_factory=async_session_maker_null_pool) as db:
        yield db


@pytest.fixture(scope="function")
async def db() -> DBManager: # type: ignore
    async for db in get_db_null_pool():
        yield db


app.dependency_overrides[get_db] = get_db_null_pool


@pytest.fixture(scope="session", autouse=True)
async def create_test_db(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def load_mock_data(create_test_db):
    async with engine_null_pool.begin() as session:
        with open("tests/mock_hotels.json", encoding="utf-8") as file_hotels:
            hotels = json.load(file_hotels)
        with open("tests/mock_rooms.json", encoding="utf-8") as file_rooms:
            rooms = json.load(file_rooms)

        hotels = [HotelAdd.model_validate(hotel) for hotel in hotels]
        rooms = [RoomAdd.model_validate(room) for room in rooms]

        async with DBManager(session_factory=async_session_maker_null_pool) as db_:
            await db_.hotels.add_bulk(hotels)
            await db_.rooms.add_bulk(rooms)
            await db_.commit()


@pytest.fixture(scope="session")
async def ac() -> AsyncClient: # type: ignore
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        yield ac


@pytest.fixture(scope="session", autouse=True)
async def register_user(ac, load_mock_data):
    await ac.post(
        "/auth/register",
        json={
            "email": "user@mail.ru",
            "password": "1234",
            "first_name": "Тоха",
            "last_name": "Сиплый"
        }
    )


@pytest.fixture(scope="session")
async def auth_ac(ac, register_user):
    await ac.post(
        "/auth/login",
        json={
            "email": "user@mail.ru",
            "password": "1234"
        }
    )
    assert ac.cookies["access_token"]
    yield ac
