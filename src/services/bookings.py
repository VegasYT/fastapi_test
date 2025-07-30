from fastapi import Depends

from src.repos.bookings import BookingsRepository
from src.repos.rooms import RoomsRepository
from src.schemas.bookings import BookingAddInternal, BookingAddRequest
from src.repos.base import BaseRepository


class BookingService:
    def __init__(self, db):
        self.db = db

    async def create_booking(
        self,
        booking_data: BookingAddRequest,
        user_id: int,
    ):
        room_price = await self.db.rooms.get_room_price(room_id=booking_data.room_id)

        internal_data = BookingAddInternal(
            **booking_data.model_dump(),
            user_id=user_id,
            price=room_price,
        )

        res = await self.db.bookings.add(internal_data)
        await self.db.commit()

        return res