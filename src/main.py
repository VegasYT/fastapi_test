from fastapi import FastAPI
import uvicorn

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from src.api.hotels import router as router_hotels
from src.api.rooms import router as router_rooms
from src.api.auth import router as router_auth
from src.api.bookings import router as router_bookings
from src.config import settings
from src.database import *
# print(settings.DB_URL)


app = FastAPI()

app.include_router(router_auth)
app.include_router(router_hotels)
app.include_router(router_rooms)
app.include_router(router_bookings)


if __name__ == "__main__":
    uvicorn.run("main:app", reload=True)
