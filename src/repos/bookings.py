from datetime import date

from sqlalchemy import select

from src.repos.mappers.mappers import BookingDataMapper
from src.schemas.bookings import Booking, BookingGetAllResponse
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