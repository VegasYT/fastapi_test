import json
from pathlib import Path
import pytest
from httpx import ASGITransport, AsyncClient

from src.schemas.hotels import HotelAdd
from src.schemas.rooms import RoomAdd
from src.repos.hotels import HotelsRepository
from src.repos.rooms import RoomsRepository
from src.config import settings
from src.database import Base, engine_null_pool
from src.main import app
from src.models import *


@pytest.fixture(scope="session", autouse=True)
def check_test_mode():
    assert settings.MODE == "TEST"


@pytest.fixture(scope="session", autouse=True)
async def create_test_db(check_test_mode):
    async with engine_null_pool.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)


@pytest.fixture(scope="session", autouse=True)
async def load_mock_data(register_user):
    async with engine_null_pool.begin() as session:
        # Загрузка данных отелей
        hotels_file = Path(__file__).parent / "mock_hotels.json"
        with open(hotels_file, "r", encoding="utf-8") as f:
            hotels_data = json.load(f)
        
        for hotel_data in hotels_data:
            hotel_add = HotelAdd(**hotel_data)
            await HotelsRepository(session).add(hotel_add)
        
        # Загрузка данных комнат
        rooms_file = Path(__file__).parent / "mock_rooms.json"
        with open(rooms_file, "r", encoding="utf-8") as f:
            rooms_data = json.load(f)
        
        for room_data in rooms_data:
            room_add = RoomAdd(**room_data)
            await RoomsRepository(session).add(room_add)
        
        await session.commit()


@pytest.fixture(scope="session", autouse=True)
async def register_user(create_test_db):
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
        await ac.post(
            "/auth/register",
            json={
                "email": "user@mail.ru",
                "password": "1234"
            }
        )