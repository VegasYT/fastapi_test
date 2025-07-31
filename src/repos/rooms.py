from datetime import date
from sqlalchemy import func, select
from sqlalchemy.orm import joinedload

from src.repos.utils import rooms_ids_for_booking
from src.models.bookings import BookingsOrm
from src.models.rooms import RoomsOrm
from src.models.hotels import HotelsOrm
from src.repos.base import BaseRepository
from src.schemas.rooms import Room
from src.database import engine


class RoomsRepository(BaseRepository):
    model = RoomsOrm
    schema = Room

    async def get_filtered_by_time(
        self, 
        hotel_id: int | None = None,
        date_from: date | None = None,
        date_to: date | None = None,
    ):
        rooms_ids_to_get = rooms_ids_for_booking(date_from, date_to, hotel_id)

        return await self.get_filtered(RoomsOrm.id.in_(rooms_ids_to_get))


    async def get_room_price(
        self, 
        room_id
    ) -> int:
        query = select(RoomsOrm.price).where(RoomsOrm.id == room_id)

        result = await self.session.execute(query)

        return result.scalar_one()
