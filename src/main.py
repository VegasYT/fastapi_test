# ruff: noqa: E402
import sys
import uvicorn
import logging
from pathlib import Path
from unittest import mock
from fastapi import FastAPI
from contextlib import asynccontextmanager
mock.patch("fastapi_cache.decorator.cache", lambda *args, **kwargs: lambda f: f).start()
from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend

sys.path.append(str(Path(__file__).parent.parent))
from src.init import redis_manager
from src.api.hotels import router as router_hotels
from src.api.rooms import router as router_rooms
from src.api.auth import router as router_auth
from src.api.bookings import router as router_bookings
from src.api.facilities import router as router_facilities
from src.api.images import router as router_images
from src.database import *  # noqa


logging.basicConfig(level=logging.INFO)


@asynccontextmanager
async def lifespan(app: FastAPI):
    # При старте приложения
    await redis_manager.connect()
    FastAPICache.init(RedisBackend(redis_manager.redis), prefix="fastapi-cache")
    logging.info("FastAPI cache initialized")
    yield
    await redis_manager.close()
    # При выключении/перезагрузке приложения


app = FastAPI(lifespan=lifespan)

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)
app.include_router(router_facilities)
app.include_router(router_images)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True, host="0.0.0.0", port=8000)
