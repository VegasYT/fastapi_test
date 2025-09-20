from datetime import date

from fastapi import HTTPException
from sqlalchemy import select

from src.repos.utils import rooms_ids_for_booking
from src.repos.mappers.mappers import BookingDataMapper
from src.schemas.bookings import Booking, BookingGetAllResponse, BookingAddInternal
from src.models.bookings import BookingsOrm
from src.repos.base import BaseRepository


class BookingsRepository(BaseRepository):
    model = BookingsOrm
    mapper = BookingDataMapper

    async def get_all(
            self, 
            limit,
            offset,
            user_id: int = None
    ) -> list[Booking]:
        query = select(BookingsOrm)

        if user_id:
            query = query.where(BookingsOrm.user_id == user_id)

        query = (
            query
            .limit(limit)
            .offset(offset)
        )

        result = await self.session.execute(query)

        return [BookingGetAllResponse.model_validate(booking, from_attributes=True) for booking in result.scalars().all()]

    async def get_bookings_with_today_checkin(self):
        query = (
            select(BookingsOrm)
            .filter(BookingsOrm.date_from == date.today())
        )
        res = await self.session.execute(query)
        return [self.mapper.map_to_domain_entity(booking) for booking in res.scalars().all()]
    
    async def add_booking(
        self,
        booking_data: BookingAddInternal,
        hotel_id: int
    ):
        rooms_ids_to_get = rooms_ids_for_booking(booking_data.date_from, booking_data.date_to, hotel_id)

        rooms_for_bookings_res = await self.session.execute(rooms_ids_to_get)
        rooms_for_bookings = rooms_for_bookings_res.unique().scalars().all()

        if booking_data.room_id not in rooms_for_bookings:
            raise HTTPException(
                status_code=409,
                detail="Выбранная комната недоступна в указанные даты"
            )

        booking = await self.add(booking_data)
        return booking